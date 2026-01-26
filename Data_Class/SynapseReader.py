import os
from deltalake import DeltaTable
from deltalake.exceptions import TableNotFoundError
import pandas as pd
import pyarrow as pa
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
import pyarrow.fs
import fsspec

class SynapseReader:
    """
    A class to read data from Azure Synapse Delta tables and CSVs without Spark.
    """
    STORAGE_ACCOUNT_KEY = os.environ.get("AZURE_STORAGE_KEY", "Nhl9qv4ZP/oFN8mmU+MUn9F+MPcJA0oP/WjpaVBUyf4w7X/2jmAoeSSsK8Wu89QOYOpPaVZAQssV+AStuyZYAg==")
    CONTAINER_NAME = "synapsefs"
    STORAGE_ACCOUNT_NAME = "storpdnedatalakedev01"
    
    _fs = None

    @classmethod
    def _ensure_fs(cls):
        if cls._fs is None:
            abfs = fsspec.filesystem("abfs", 
                                     account_name=cls.STORAGE_ACCOUNT_NAME, 
                                     account_key=cls.STORAGE_ACCOUNT_KEY)
            cls._fs = pa.fs.PyFileSystem(pa.fs.FSSpecHandler(abfs))

    @classmethod
    def load_delta(cls, folder_path: str, as_pandas: bool = False, filters=None):
        """
        Lädt eine Delta-Tabelle.
        Optional mit Filter (PyArrow Compute Expression), z.B. pc.field("Date") >= ...
        Rückgabe: PyArrow Table (default) oder Pandas DataFrame (as_pandas=True).
        """
        delta_uri = f"abfs://{cls.CONTAINER_NAME}@{cls.STORAGE_ACCOUNT_NAME}.dfs.core.windows.net/{folder_path}"
        storage_options = {
            "account_name": cls.STORAGE_ACCOUNT_NAME,
            "account_key": cls.STORAGE_ACCOUNT_KEY
        }

        try:
            dt = DeltaTable(delta_uri, storage_options=storage_options)
            dataset = dt.to_pyarrow_dataset()
            
            # Use filter if provided
            scanner = dataset.scanner(use_threads=True, filter=filters) if filters is not None else dataset.scanner(use_threads=True)
            table = scanner.to_table()
            
            return table.to_pandas(split_blocks=True, self_destruct=True) if as_pandas else table
        except TableNotFoundError:
            print(f"Warning: Delta table not found at {delta_uri}")
            return pd.DataFrame() if as_pandas else pa.Table.from_pydict({})
        except Exception as e:
            print(f"An unexpected error occurred while loading delta table {delta_uri}: {e}")
            raise e

    @classmethod
    def get_latest_csv_blob(cls, folder_path: str) -> pd.DataFrame:
        """
        Sucht die neueste CSV-Datei in einem Ordner (Datum im Namen oder last_modified)
        und lädt sie als DataFrame.
        """
        cls._ensure_fs()
        
        full_path = f"{cls.CONTAINER_NAME}/{folder_path}"
        
        def extract_datetime_from_name(name: str):
            patterns = [
                r'(\d{4}[-_]\d{2}[-_]\d{2}[_-]?\d{0,4})',  # 2024-05-06(_1430)
                r'(\d{8}[_-]?\d{0,4})'                      # 20240506(_1430)
            ]
            for pattern in patterns:
                m = re.search(pattern, os.path.basename(name))
                if m:
                    raw = m.group(1).replace("_", "").replace("-", "")
                    try:
                        return datetime.strptime(raw[:12], '%Y%m%d%H%M') if len(raw) >= 12 \
                               else datetime.strptime(raw[:8], '%Y%m%d')
                    except Exception:
                        continue
            return None

        try:
            selector = pa.fs.FileSelector(full_path, recursive=True)
            files = cls._fs.get_file_info(selector)
        except Exception as e:
            print(f"Error listing files in {full_path}: {e}")
            return pd.DataFrame()
        
        csv_files = [f for f in files if f.path.endswith('.csv') and f.type == pa.fs.FileType.File]

        if not csv_files:
            return pd.DataFrame()

        dated = []
        undated = []
        for f in csv_files:
            dt = extract_datetime_from_name(f.path)
            if dt:
                dated.append((dt, f.path, f))
            else:
                undated.append((f.mtime, f.path, f))

        if not dated and not undated:
            return pd.DataFrame()

        latest_file_info = max(dated, key=lambda x: x[0]) if dated else max(undated, key=lambda x: x[0])
        latest_path = latest_file_info[1]
        
        print(f"📦 Neueste Datei: {os.path.basename(latest_path)} (Datum: {latest_file_info[0]})")
        
        return cls.read_csv_from_blob(latest_path, sep=",")

    @classmethod
    def read_csv_from_blob(cls, file_path: str, sep: str = ',') -> pd.DataFrame:
        """Reads a CSV file from a given blob path into a pandas DataFrame."""
        cls._ensure_fs()
        try:
            with cls._fs.open_input_stream(file_path) as stream:
                # The stream from pyarrow is a raw buffer. pandas can read it directly.
                # We need to handle potential encoding issues. Let's assume UTF-8 for now.
                try:
                    return pd.read_csv(stream, sep=sep, encoding='utf-8')
                except UnicodeDecodeError:
                    # Rewind stream and try with a different encoding, e.g., 'latin1' or 'cp1252'
                    stream.seek(0)
                    return pd.read_csv(stream, sep=sep, encoding='latin1')
        except Exception as e:
            print(f"Error reading CSV blob {file_path}: {e}")
            return pd.DataFrame()