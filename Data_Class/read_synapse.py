from azure.storage.blob import BlobServiceClient
from deltalake import DeltaTable
import pandas as pd
import numpy as np
from io import BytesIO
from datetime import datetime
import re 

class Synapse_Daten:

    # Azure Storage Account Informationen
    STORAGE_ACCOUNT_URL = "https://storpdnedatalakedev01.blob.core.windows.net/"
    STORAGE_ACCOUNT_KEY = "Nhl9qv4ZP/oFN8mmU+MUn9F+MPcJA0oP/WjpaVBUyf4w7X/2jmAoeSSsK8Wu89QOYOpPaVZAQssV+AStuyZYAg=="  # Replace with your storage account key
    CONTAINER_NAME = "synapsefs"

    # BlobServiceClient initialisieren
    blob_service_client = BlobServiceClient(
        account_url=STORAGE_ACCOUNT_URL,
        credential=STORAGE_ACCOUNT_KEY
    )
    container_client = blob_service_client.get_container_client(CONTAINER_NAME)

    @classmethod
    def read_csv_from_blob(cls, blob_path, **kwargs):
        """Liest eine CSV-Datei aus Azure Blob Storage"""
        blob_client = cls.blob_service_client.get_blob_client(container=cls.CONTAINER_NAME, blob=blob_path)
        stream_downloader = blob_client.download_blob()
        file_stream = BytesIO()
        stream_downloader.readinto(file_stream)
        file_stream.seek(0)
        df = pd.read_csv(file_stream, **kwargs)
        return df

    @classmethod
    def read_parquet_from_blob(cls, blob_path, **kwargs):
        """Liest eine Parquet-Datei aus Azure Blob Storage"""
        blob_client = cls.blob_service_client.get_blob_client(container=cls.CONTAINER_NAME, blob=blob_path)
        stream_downloader = blob_client.download_blob()
        file_stream = BytesIO()
        stream_downloader.readinto(file_stream)
        file_stream.seek(0)
        df = pd.read_parquet(file_stream, **kwargs)
        return df

    @classmethod
    def list_blobs_in_folder(cls, folder_path):
        """Listet alle .csv-Dateien in einem virtuellen Blob-Ordner"""
        blob_list = cls.container_client.list_blobs(name_starts_with=folder_path)
        return [blob.name for blob in blob_list if blob.name.endswith('.csv')]

    @classmethod
    def load_mass_csv_files_from_blob(cls, path=None):
        """Lädt und kombiniert alle CSVs aus einem Ordner"""
        if path is None:
            return pd.DataFrame()
        files = cls.list_blobs_in_folder(path)
        files = [f for f in files if f.endswith('.csv')]

        df = pd.DataFrame()
        for file in files:
            try:
                print(f"📦 Lade Datei: {file}")
                df = pd.concat([df, cls.read_csv_from_blob(blob_path=file, sep=',')], ignore_index=True)
            except Exception as e:
                print(f"❌ Fehler beim Laden von {file}: {e}")
        return df

    @classmethod
    def load_delta_table_from_blob(cls, folder_path: str, date_column: str = None, von: str = None, bis: str = None) -> pd.DataFrame:
        """
        Lädt eine Delta-Tabelle aus einem Azure Data Lake Ordner (z. B. Synapse).
        Optional: Filterung nach Datumsbereich über eine definierte Spalte.
        """
        delta_uri = f"abfs://{cls.CONTAINER_NAME}@storpdnedatalakedev01.dfs.core.windows.net/{folder_path}"

        try:
            dt = DeltaTable(delta_uri, storage_options={
                "account_name": "storpdnedatalakedev01",
                "account_key": cls.STORAGE_ACCOUNT_KEY
            })
            df = dt.to_pandas()

            # Optionaler Datumsfilter
            if date_column and (von or bis):
                df[date_column] = pd.to_datetime(df[date_column], errors='coerce')
                if von:
                    df = df[df[date_column] >= pd.to_datetime(von)]
                if bis:
                    df = df[df[date_column] <= pd.to_datetime(bis)]

            return df

        except Exception as e:
            print(f"❌ Fehler beim Laden der Delta-Tabelle: {e}")
            return pd.DataFrame()
        
    @classmethod
    def read_excel_from_blob(cls, blob_path, **kwargs):
        """
        Liest eine Excel-Datei (.xlsx) aus Azure Blob Storage in ein Pandas DataFrame.
        :param blob_path: Pfad zur Datei im Blob-Container
        :param kwargs: Weitere Parameter für pd.read_excel (z. B. sheet_name)
        :return: Pandas DataFrame
        """
        try:
            blob_client = cls.blob_service_client.get_blob_client(container=cls.CONTAINER_NAME, blob=blob_path)
            stream_downloader = blob_client.download_blob()
            file_stream = BytesIO()
            stream_downloader.readinto(file_stream)
            file_stream.seek(0)
            df = pd.read_excel(file_stream, **kwargs)
            return df
        except Exception as e:
            print(f"❌ Fehler beim Laden der Excel-Datei {blob_path}: {e}")
            return pd.DataFrame()
        
        import re


    @classmethod
    def get_latest_csv_blob(cls, folder_path: str) -> str:
        """
        Sucht die neueste CSV-Datei in einem Blob-Ordner basierend auf dem Datum im Dateinamen oder dem Änderungsdatum.
        Gibt den vollständigen Blob-Pfad zurück.
        """
        def extract_datetime_from_name(name):
            # Suche nach Datums-/Zeitmustern im Dateinamen, z. B. 2024-05-06, 20240506, 2024_05_06_1430
            patterns = [
                r'(\d{4}[-_]\d{2}[-_]\d{2}[_-]?\d{0,4})',     # 2024-05-06, 2024_05_06, 2024-05-06_1430
                r'(\d{8}[_-]?\d{0,4})'                        # 20240506, 20240506_1430
            ]
            for pattern in patterns:
                match = re.search(pattern, name)
                if match:
                    try:
                        raw = match.group(1).replace("_", "").replace("-", "")
                        dt = datetime.strptime(raw[:12], '%Y%m%d%H%M') if len(raw) >= 12 else \
                            datetime.strptime(raw[:8], '%Y%m%d')
                        return dt
                    except:
                        continue
            return None

        blobs = list(cls.container_client.list_blobs(name_starts_with=folder_path))
        csv_blobs = [b for b in blobs if b.name.endswith('.csv')]

        # Versuche, Datum aus Dateinamen zu extrahieren
        dated = []
        undated = []

        for blob in csv_blobs:
            dt = extract_datetime_from_name(blob.name)
            if dt:
                dated.append((dt, blob.name))
            else:
                undated.append((blob.last_modified, blob.name))

        if dated:
            latest = max(dated, key=lambda x: x[0])
        elif undated:
            latest = max(undated, key=lambda x: x[0])
        else:
            return None
        
        print(f"📦 Neueste Datei: {latest[1]} mit Datum: {latest[0]}")
        # als Dataframe zurückgeben
        return cls.read_csv_from_blob(blob_path=latest[1], sep=',')