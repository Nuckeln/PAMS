from dataclasses import dataclass
from typing import Dict, Any, Iterable
from pandas import DataFrame
from sqlalchemy import create_engine, inspect
import urllib
import pandas as pd
import time
import json
from sqlalchemy import Table, Column, Integer, MetaData
import streamlit as st
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
    driver: str = '{ODBC Driver 17 for SQL Server}'
    timeout: int = 30

class AzureDbConnection:
    db = None
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
        #self.db = create_engine(conn_string, echo=echo)
        AzureDbConnection.db = create_engine(conn_string, echo=echo)
        
    def connect(self) -> None:
        """Establish connection."""
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

def load_connection_settings(json_path):
    with open(json_path, 'r') as json_file:
        data = json.load(json_file)
        return ConnectionSettings(
            server=data['server'],
            database=data['database'],
            username=data['username'],
            password=data['password']
        )
def create_table(df, table_name):
    json_path = 'Data/appData/credentials.json'
    conn_settings = load_connection_settings(json_path)
    db_conn = AzureDbConnection(conn_settings)
    # Verbindung herstellen
    db_conn.connect()
    # Hier kannst du die Verbindung verwenden, z.B. Abfragen ausführen oder Tabellen abrufen
    df.to_sql(table_name, db_conn.db, if_exists='replace', index=False)
    # Verbindung schließen
    db_conn.dispose()

def save_Table(df, table_name):
    json_path = 'Data/appData/credentials.json'
    conn_settings = load_connection_settings(json_path)
    db_conn = AzureDbConnection(conn_settings)
    # Verbindung herstellen
    db_conn.connect()
    # Hier kannst du die Verbindung verwenden, z.B. Abfragen ausführen oder Tabellen abrufen
    df.to_sql(table_name, db_conn.db, if_exists='replace', index=False)
    # Verbindung schließen
    db_conn.dispose()
def save_Table_append(df, table_name):
    json_path = 'Data/appData/credentials.json'
    conn_settings = load_connection_settings(json_path)
    db_conn = AzureDbConnection(conn_settings)
    # Verbindung herstellen
    db_conn.connect()
    # Hier kannst du die Verbindung verwenden, z.B. Abfragen ausführen oder Tabellen abrufen
    df.to_sql(table_name, db_conn.db, if_exists='append', index=False)
    # Verbindung schließen
    db_conn.dispose()

def read_Table(table_name):
    json_path = 'Data/appData/credentials.json'
    conn_settings = load_connection_settings(json_path)
    db_conn = AzureDbConnection(conn_settings)
    # Verbindung herstellen
    db_conn.connect()
    try:
        # Hier kannst du die Verbindung verwenden, z.B. Abfragen ausführen oder Tabellen abrufen
        df = pd.read_sql(f"SELECT * FROM [{table_name}]", db_conn.db)
    except:
        st.warning(f"Table {table_name} not found")
    # Verbindung schließen
    db_conn.dispose()
    
    return df

def read_Table_by_Date(day1: str, day2:str, tabellenName,datumsSpalte):
    '''erwartet zwei Datumsangaben im Format 'YYYY-MM-DD' 
    und den Tabellennamen als String  
    day 1 Startwert z.B 2020-01-01   
    day 2 Endwert z.B 2020-01-31'''

    json_path = 'Data/appData/credentials.json'
    conn_settings = load_connection_settings(json_path)
    db_conn = AzureDbConnection(conn_settings)
    # Verbindung herstellen
    sqlQuery = f"SELECT * FROM [{tabellenName}] WHERE {datumsSpalte} BETWEEN '{day1}' AND '{day2}'"
    db_conn.connect()
    df = pd.read_sql(sqlQuery, db_conn.conn)
    db_conn.dispose()
    return df

def truncate_Table(table_name):
    json_path = 'Data/appData/credentials.json'
    conn_settings = load_connection_settings(json_path)
    db_conn = AzureDbConnection(conn_settings)
    # Verbindung herstellen
    db_conn.connect()
    # Hier kannst du die Verbindung verwenden, z.B. Abfragen ausführen oder Tabellen abrufen
    db_conn.db.execute(f"TRUNCATE TABLE [{table_name}]")
    # Verbindung schließen
    db_conn.dispose()
    
def load_table_by_Col_Content(table_name: str, col_name: str,content: list[str]) -> pd.DataFrame:
    json_path = 'Data/appData/credentials.json'
    conn_settings = load_connection_settings(json_path)
    db_conn = AzureDbConnection(conn_settings)

    max_size = 50  # 
    order_number_batches = [content[i:i+max_size] for i in range(0, len(content), max_size)]
    
    dfs = []
    for batch in order_number_batches:
        # Build SQL query to filter table by SAP Order Numbers
        sap_order_numbers = "', '".join(batch)
        query = f"SELECT * FROM [{table_name}] WHERE {col_name} IN ('{sap_order_numbers}')"

        # Execute SQL query and append result to dfs
        df = pd.read_sql_query(query, db_conn.conn)
        dfs.append(df)
    
    db_conn.dispose()
    return pd.concat(dfs, ignore_index=True)

