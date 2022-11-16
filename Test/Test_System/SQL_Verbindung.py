from dataclasses import dataclass
from typing import Dict, Any, Iterable
from pandas import DataFrame
from sqlalchemy import create_engine, inspect
import urllib
import pandas as pd

import pyodbc



@dataclass(frozen=True)
class ConnectionSettings:
    """Connection Settings."""
    server: str
    database: str
    username: str
    password: str
    #driver: str = '{ODBC Driver 18 for SQL Server}'
    #driver: str = '{ODBC Driver 13 for SQL Server}'
    driver: str = '{ODBC Driver 18 for SQL Server}'
    timeout: int = 30
class AzureDbConnection:
    """
    Azure SQL database connection.
    """
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
        self.db = create_engine(conn_string, echo=echo)
    def connect(self) -> None:
        """Estimate connection."""
        self.conn = self.db.connect()
    def get_tables(self) -> Iterable[str]:
        """Get list of tables."""
        inspector = inspect(self.db)
        return [t for t in inspector.get_table_names()]
    def dispose(self) -> None:
        """Dispose opened connections."""
        self.conn.close()
        self.db.dispose()
    def execute(self, query: str) -> None:
        """Execute query."""
        self.conn.execute(query)

def datenLadenLabel():
    conn_settings = ConnectionSettings(
    #server='batsql-pd-ne-cmes-dev-10.database.windows.net',
    server='batsql-pd-ne-cmes-dev-10',
    database='batsdb-pd-ne-dev-reporting_SuperDepot',
    username='batedp-cmes-dev-reportinguser',
    password='b2.5v^H!IKjetuXMVNvW')

    db_conn = AzureDbConnection(conn_settings)
    db_conn.connect()
    dfLabel = pd.read_sql('SELECT * FROM [business_depotDEBYKN-LabelPrintOrders]', db_conn.conn)
    return dfLabel

def datenLadenStammdaten():
    conn_settings = ConnectionSettings(
    #server='batsql-pd-ne-cmes-dev-10.database.windows.net',
    server='batsql-pd-ne-cmes-dev-10',
    database='batsdb-pd-ne-dev-reporting_SuperDepot',
    username='batedp-cmes-dev-reportinguser',
    password='b2.5v^H!IKjetuXMVNvW')

    db_conn = AzureDbConnection(conn_settings)
    db_conn.connect()
    dfStammdaten = pd.read_sql('SELECT * FROM [data_materialmaster-MaterialMasterUnitOfMeasures]', db_conn.conn)
    return dfStammdaten

def datenLadenAufträge():
    conn_settings = ConnectionSettings(
    #server='batsql-pd-ne-cmes-dev-10.database.windows.net',
    server='batsql-pd-ne-cmes-dev-10',
    database='batsdb-pd-ne-dev-reporting_SuperDepot',
    username='batedp-cmes-dev-reportinguser',
    password='b2.5v^H!IKjetuXMVNvW')

    db_conn = AzureDbConnection(conn_settings)
    db_conn.connect()
    dfAufträge = pd.read_sql('SELECT * FROM [business_depotDEBYKN-DepotDEBYKNOrders]', db_conn.conn)
    return dfAufträge

