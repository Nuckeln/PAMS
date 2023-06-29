from dataclasses import dataclass
from typing import Dict, Any, Iterable, List
import pandas as pd
import urllib
from sqlalchemy import create_engine, inspect
import time
from sqlalchemy import text
import os


@dataclass(frozen=True)
class ConnectionSettings:
    server: str
    database: str
    username: str
    password: str
    driver: str = '{ODBC Driver 18 for SQL Server}'
    timeout: int = 30

class AzureDbConnection:
    def __init__(self, conn_settings: ConnectionSettings, echo: bool = False) -> None:
        conn_params = urllib.parse.quote_plus(
            'Driver=%s;' % conn_settings.driver +
            'Server=tcp:%s.database.windows.net,1433;' % conn_settings.server +
            'Database=%s;' % conn_settings.database +
            'Uid=%s;' % conn_settings.username +
            'Pwd=%s;' % conn_settings.password +
            'Encrypt=yes;' +
            'TrustServerCertificate=no;' +
            'Connection Timeout=%s;' % conn_settings.timeout
        )
        conn_string = f'mssql+pyodbc:///?odbc_connect={conn_params}'
        self.engine = create_engine(conn_string, echo=echo)

    def __enter__(self):
        self.conn = self.engine.connect()
        return self.conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()
        self.engine.dispose()

    def get_tables(self) -> Iterable[str]:
        inspector = inspect(self.engine)
        return [t for t in inspector.get_table_names()]

def verbinder() -> AzureDbConnection:
    conn_settings = ConnectionSettings(    
        server = 'batsql-pp-ne-cmes-prod-10',
        database= 'batsdb-pp-ne-prod-reporting_SuperDepot',
        username='batedp-cmes-prod-reportinguser',
        password='b2.5v^H!IKjetuXMVNvW')
    return AzureDbConnection(conn_settings)

def create_table(conn, table_name: str, df: pd.DataFrame) -> None:
    df.to_sql(table_name, conn, if_exists='replace', index=False)

def update_table(conn, table_name: str, df: pd.DataFrame) -> None:
    with conn.begin():
        print(f"Deleting records from table: {table_name}")
        delete_statement = text(f"DELETE FROM [{table_name}]")
        print(f"Executing: {delete_statement}")
        conn.execute(delete_statement)
        print("Appending records to table")
        df.to_sql(table_name, conn, if_exists='append', index=False)
        print("Update complete")

def delete_entry(conn, table_name: str, entry: int) -> None:
    conn.execute(f"DELETE FROM [{table_name}] WHERE [Index] = {entry}")

def delete_table(conn, table_name: str) -> None:
    inspector = inspect(conn)
    if table_name in inspector.get_table_names():
        conn.execute(text(f"DROP TABLE [{table_name}]"))
    else:
        print(f"Table '{table_name}' does not exist")


def load_table(conn, table_name: str) -> pd.DataFrame:
    return pd.read_sql(f"SELECT * FROM [{table_name}]", conn)

def truncate_table(conn, table_name: str) -> None:
    with conn.begin():
        conn.execute(text(f"TRUNCATE TABLE [{table_name}]"))
    return f'Table {table_name} truncated successfully'
        

def load_table_by_date_range(conn, table_name: str, date_column: str, start_date: str, end_date: str) -> pd.DataFrame:
    query = f"SELECT * FROM [{table_name}] WHERE {date_column} BETWEEN '{start_date}' AND '{end_date}'"
    return pd.read_sql(query, conn)

def load_table_by_order_number(conn, table_name: str, order_numbers: List[str]) -> pd.DataFrame:
    max_size = 50
    order_number_batches = [order_numbers[i:i+max_size] for i in range(0, len(order_numbers), max_size)]
    dfs = []
    for batch in order_number_batches:
        sap_order_numbers = "', '".join(batch)
        query = f"SELECT * FROM [{table_name}] WHERE SapOrderNumber IN ('{sap_order_numbers}')"
        df = pd.read_sql_query(query, conn)
        dfs.append(df)
    return



def backup_all_tables(conn: AzureDbConnection, backup_directory: str = "backup") -> None:
    if not os.path.exists(backup_directory):
        os.makedirs(backup_directory)
    
    table_names = conn.get_tables()
    
    with conn as connection:
        for table_name in table_names:
            print(f"Backing up table: {table_name}")
            df = load_table(connection, table_name)
            backup_file_path = os.path.join(backup_directory, f"{table_name}_backup_{time.strftime('%Y%m%d-%H%M%S')}.parquet")
            df.to_parquet(backup_file_path, index=False)
            print(f"Backup of table {table_name} saved to: {backup_file_path}")