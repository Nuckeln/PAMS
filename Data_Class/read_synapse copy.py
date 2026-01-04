from azure.storage.blob import BlobServiceClient
from deltalake import DeltaTable
import pandas as pd
import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.parquet as pq
import pyarrow.dataset as ds
from io import BytesIO
from datetime import datetime
import re
import platform
# --------------------------------------------------------
from pyspark.sql import SparkSession
from delta import configure_spark_with_delta_pip
import platform

from azure.storage.blob import BlobServiceClient
from deltalake import DeltaTable
import pandas as pd
import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.parquet as pq
import pyarrow.dataset as ds
from pyarrow.fs import AzureFileSystem   # ✅ <--- das ist der fehlende Import
from io import BytesIO
from datetime import datetime
import re

class Synapse_Daten:
    # ==== Konfiguration ====
    STORAGE_ACCOUNT_URL = "https://storpdnedatalakedev01.blob.core.windows.net/"
    STORAGE_ACCOUNT_KEY = "Nhl9qv4ZP/oFN8mmU+MUn9F+MPcJA0oP/WjpaVBUyf4w7X/2jmAoeSSsK8Wu89QOYOpPaVZAQssV+AStuyZYAg=="
    CONTAINER_NAME = "synapsefs"

    # werden lazy gesetzt
    blob_service_client = None
    container_client = None

    # ==== Hilfsfunktionen ====
    @classmethod
    def _ensure_clients(cls):
        if cls.blob_service_client is None:
            cls.blob_service_client = BlobServiceClient(
                account_url=cls.STORAGE_ACCOUNT_URL,
                credential=cls.STORAGE_ACCOUNT_KEY
            )
        if cls.container_client is None:
            cls.container_client = cls.blob_service_client.get_container_client(cls.CONTAINER_NAME)

    @staticmethod
    def _is_dir_path(p: str) -> bool:
        return p.endswith("/")

    # ==== Delta lesen (vollständig) ====
    @classmethod
    def load_delta_all(cls, folder_path: str, as_pandas: bool = False):
        """
        Lädt eine Delta-Tabelle vollständig (ohne Filter).
        Rückgabe: PyArrow Table (default) oder Pandas DataFrame (as_pandas=True).
        """
        delta_uri = f"abfs://{cls.CONTAINER_NAME}@storpdnedatalakedev01.dfs.core.windows.net/{folder_path}"
        dt = DeltaTable(
            delta_uri,
            storage_options={"account_name": "storpdnedatalakedev01", "account_key": cls.STORAGE_ACCOUNT_KEY},
        )
        dataset = dt.to_pyarrow_dataset()
        table = dataset.scanner(use_threads=True).to_table()
        return table.to_pandas(split_blocks=True, self_destruct=True) if as_pandas else table

    # ==== Parquet-Dataset (Ordner) lesen ====
    @classmethod
    def load_parquet_dataset_all(cls, folder_path: str, as_pandas: bool = False):
        """
        Lädt ein Parquet-Dataset (Ordner) vollständig, ohne Filter/Prüfungen.
        """
        uri = f"abfs://{cls.CONTAINER_NAME}@storpdnedatalakedev01.dfs.core.windows.net/{folder_path}"
        # pyarrow erkennt das abfs://-FS automatisch
        dataset = ds.dataset(uri, format="parquet")
        table = dataset.scanner(use_threads=True).to_table()
        return table.to_pandas(split_blocks=True, self_destruct=True) if as_pandas else table

    # ==== CSV/Parquet/Excel über Blob SDK lesen ====
    @classmethod
    def read_csv_from_blob(cls, blob_path, **kwargs):
        """Liest eine CSV-Datei aus Azure Blob Storage"""
        cls._ensure_clients()
        blob_client = cls.blob_service_client.get_blob_client(container=cls.CONTAINER_NAME, blob=blob_path)
        stream = blob_client.download_blob().readall()
        return pd.read_csv(BytesIO(stream), **kwargs)

    @classmethod
    def read_parquet_from_blob(cls, blob_path, **kwargs):
        """
        Liest Parquet aus Blob Storage.
        - Wenn ein Ordner übergeben wird, werden alle 'part-*' Dateien zusammengeführt.
        - Wenn eine Datei übergeben wird, wird nur diese gelesen.
        """
        cls._ensure_clients()

        if cls._is_dir_path(blob_path):
            prefix = blob_path
        else:
            # Prüfe, ob 'blob_path' eher ein Ordner ist (kommt z.B. ohne Slash)
            # Dann suchen wir darunter 'part-*'
            prefix = blob_path.rstrip("/") + "/"

        parts = [
            b.name for b in cls.container_client.list_blobs(name_starts_with=prefix)
            if b.name.split("/")[-1].startswith("part-") and (getattr(b, "size", 1) or 0) > 0
        ]

        if parts:
            dfs = []
            for name in parts:
                stream = cls.blob_service_client.get_blob_client(cls.CONTAINER_NAME, name).download_blob().readall()
                dfs.append(pd.read_parquet(BytesIO(stream), engine="pyarrow", **kwargs))
            return pd.concat(dfs, ignore_index=True)
        else:
            # Einzeldatei
            blob_client = cls.blob_service_client.get_blob_client(container=cls.CONTAINER_NAME, blob=blob_path)
            props = blob_client.get_blob_properties()
            if props.size == 0:
                raise ValueError(f"Blob hat 0 Bytes: {blob_path}")
            stream = blob_client.download_blob().readall()
            return pd.read_parquet(BytesIO(stream), engine="pyarrow", **kwargs)

    @classmethod
    def read_excel_from_blob(cls, blob_path, **kwargs):
        """Liest eine .xlsx-Datei aus Blob Storage in ein DataFrame."""
        cls._ensure_clients()
        try:
            blob_client = cls.blob_service_client.get_blob_client(container=cls.CONTAINER_NAME, blob=blob_path)
            stream = blob_client.download_blob().readall()
            return pd.read_excel(BytesIO(stream), **kwargs)
        except Exception as e:
            print(f"❌ Fehler beim Laden der Excel-Datei {blob_path}: {e}")
            return pd.DataFrame()

    # ==== Delta lesen (robust, mit optionaler Datumsfilterung) ====
    @classmethod
    def load_delta_table_from_blob(cls, folder_path: str, date_column: str = None, von: str = None, bis: str = None) -> pd.DataFrame:
        """
        Lädt eine Delta-Tabelle robust und vollständig.
        - Timestamps werden vor Konvertierung zu Pandas in Arrow zu String gecastet (vermeidet Casting-Errors).
        - Optional: Filter auf `date_column` innerhalb [von, bis].
        """
        cls._ensure_clients()
        delta_uri = f"abfs://{cls.CONTAINER_NAME}@storpdnedatalakedev01.dfs.core.windows.net/{folder_path}"

        try:
            dt = DeltaTable(delta_uri, storage_options={"account_name": "storpdnedatalakedev01", "account_key": cls.STORAGE_ACCOUNT_KEY})

            # Versuche direkt als Arrow Table
            try:
                table = dt.to_pyarrow_table()
                # Timestamps -> String
                cols = {}
                for i, field in enumerate(table.schema):
                    col = table.column(i)
                    if pa.types.is_timestamp(field.type):
                        col = pc.cast(col, pa.string())
                    cols[field.name] = col
                table = pa.table(cols)

            except Exception as e_table:
                print(f"❌ Fehler beim Laden als Arrow-Table: {e_table}")
                print("➡️ Datei-weise Fallback (alle Parquet-Parts lesen).")
                prefix = folder_path.rstrip('/') + '/'
                blobs = [
                    b.name for b in cls.container_client.list_blobs(name_starts_with=prefix)
                    if ('/_delta_log/' not in ('/' + b.name)) and b.name.endswith('.parquet')
                ]
                if not blobs:
                    print("⚠️ Keine Parquet-Dateien gefunden.")
                    return pd.DataFrame()

                dfs = []
                for name in blobs:
                    try:
                        stream = cls.blob_service_client.get_blob_client(cls.CONTAINER_NAME, name).download_blob().readall()
                        t = pq.read_table(BytesIO(stream))
                        # Timestamps in diesem Chunk -> String
                        cols = {}
                        for i, field in enumerate(t.schema):
                            col = t.column(i)
                            if pa.types.is_timestamp(field.type):
                                col = pc.cast(col, pa.string())
                            cols[field.name] = col
                        t = pa.table(cols)
                        dfs.append(t.to_pandas())
                    except Exception as e_part:
                        print(f"⚠️ Fehler beim Lesen von {name}: {e_part}")
                if not dfs:
                    return pd.DataFrame()
                df = pd.concat(dfs, ignore_index=True)
            else:
                df = table.to_pandas()

            # Optional: Datumsfilter
            if date_column and date_column in df.columns and (von or bis):
                ser = df[date_column]
                try:
                    if pd.api.types.is_integer_dtype(ser) or (pd.api.types.is_string_dtype(ser) and ser.astype(str).str.len().dropna().median() == 8 and ser.astype(str).str.isnumeric().all()):
                        parsed = pd.to_datetime(ser.astype(str), format='%Y%m%d', errors='coerce')
                    else:
                        parsed = pd.to_datetime(ser, errors='coerce', utc=False)
                except Exception:
                    parsed = pd.to_datetime(ser.astype(str), errors='coerce', utc=False)

                if von:
                    parsed_from = pd.to_datetime(von, errors='coerce')
                    if pd.notna(parsed_from):
                        df = df[parsed >= parsed_from]
                if bis:
                    parsed_to = pd.to_datetime(bis, errors='coerce')
                    if pd.notna(parsed_to):
                        df = df[parsed <= parsed_to]

            return df

        except Exception as e:
            print(f"❌ Fehler beim Laden der Delta-Tabelle: {e}")
            return pd.DataFrame()

    # ==== Helfer: neueste CSV in Ordner finden und laden ====
    @classmethod
    def get_latest_csv_blob(cls, folder_path: str) -> pd.DataFrame:
        """
        Sucht die neueste CSV-Datei in einem Ordner (Datum im Namen oder last_modified)
        und lädt sie als DataFrame.
        """
        cls._ensure_clients()

        def extract_datetime_from_name(name: str):
            patterns = [
                r'(\d{4}[-_]\d{2}[-_]\d{2}[_-]?\d{0,4})',  # 2024-05-06(_1430)
                r'(\d{8}[_-]?\d{0,4})'                      # 20240506(_1430)
            ]
            for pattern in patterns:
                m = re.search(pattern, name)
                if m:
                    raw = m.group(1).replace("_", "").replace("-", "")
                    try:
                        return datetime.strptime(raw[:12], '%Y%m%d%H%M') if len(raw) >= 12 \
                               else datetime.strptime(raw[:8], '%Y%m%d')
                    except Exception:
                        continue
            return None

        blobs = list(cls.container_client.list_blobs(name_starts_with=folder_path))
        csv_blobs = [b for b in blobs if b.name.endswith('.csv')]

        dated = []
        undated = []
        for b in csv_blobs:
            dt = extract_datetime_from_name(b.name)
            if dt:
                dated.append((dt, b.name))
            else:
                undated.append((b.last_modified, b.name))

        if not dated and not undated:
            return pd.DataFrame()

        latest = max(dated, key=lambda x: x[0]) if dated else max(undated, key=lambda x: x[0])
        print(f"📦 Neueste Datei: {latest[1]} (Datum: {latest[0]})")
        return cls.read_csv_from_blob(latest[1], sep=",")
    
    @classmethod
    def load_parquet_dataset_all_safe(cls, folder_path: str, as_pandas: bool = False):
        """
        Lädt nur Parquet-Dateien (ignoriert _delta_log und Manifest-Dateien).
        """
        cls._ensure_clients()
        prefix = folder_path.rstrip("/") + "/"

        blobs = [
            b.name for b in cls.container_client.list_blobs(name_starts_with=prefix)
            if b.name.endswith(".parquet") and "_delta_log" not in b.name
        ]

        if not blobs:
            print("⚠️ Keine Parquet-Dateien gefunden.")
            return pd.DataFrame()

        dfs = []
        for name in blobs:
            stream = cls.blob_service_client.get_blob_client(cls.CONTAINER_NAME, name).download_blob().readall()
            dfs.append(pd.read_parquet(BytesIO(stream), engine="pyarrow"))

        df = pd.concat(dfs, ignore_index=True)
        print(f"✅ Geladen: {len(dfs)} Parquet-Dateien ({len(df):,} Zeilen)")
        return df
    


    @classmethod
    def load_delta_pyspark(cls, path: str, as_pandas: bool = True, show_rows: int = 5):
        """
        Liest eine Delta-Tabelle über PySpark (lokal, mit Delta-Unterstützung)
        und gibt wahlweise einen Spark- oder Pandas-DataFrame zurück.
        """

        print(f"🔹 Lade Delta-Tabelle über PySpark: {path}")

        # Prüfe, ob auf macOS (lokal) ausgeführt
        is_local = platform.system() == "Darwin"
        if not is_local:
            print("⚠️ Achtung: Diese Funktion ist für lokale Mac-Ausführung optimiert.")

        # Hole Storage Key (aus Klassenkonstante oder ENV)
        storage_key = getattr(cls, "STORAGE_ACCOUNT_KEY", None)
        if not storage_key:
            raise ValueError("❌ Kein STORAGE_ACCOUNT_KEY in Synapse_Daten definiert!")

        # Baue SparkSession
        builder = (
            SparkSession.builder
            .appName("Local Delta Reader")
            .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
            .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")
            # Azure ADLS Zugriff
            .config("fs.azure.account.auth.type.storpdnedatalakedev01.dfs.core.windows.net", "SharedKey")
            .config("fs.azure.account.key.storpdnedatalakedev01.dfs.core.windows.net", storage_key)
            # Delta Optionen
            .config("spark.databricks.delta.schema.autoMerge.enabled", "true")
            .config("spark.sql.parquet.mergeSchema", "false")
        )

        spark = configure_spark_with_delta_pip(builder).getOrCreate()

        # Pfad vollständig machen (falls kein abfss:// enthalten)
        if not path.startswith("abfss://"):
            path = f"abfss://{cls.CONTAINER_NAME}@storpdnedatalakedev01.dfs.core.windows.net/{path.lstrip('/')}"

        # Lade Delta-Tabelle
        df = spark.read.format("delta").load(path)

        print(f"✅ Delta-Tabelle erfolgreich geladen: {df.count()} Zeilen, {len(df.columns)} Spalten")

        if show_rows:
            df.show(show_rows)

        if as_pandas:
            print("📥 Konvertiere zu Pandas-DataFrame...")
            return df.toPandas()

        return df