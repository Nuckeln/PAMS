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

class SQL_TabellenLadenBearbeiten:
    '''Ermöglicht die Auswahl von Spalten aus bestimmten Tabellen
    sowie Datumsbereich
    und gibt diese als DataFrame zurück'''
    
    tabelle_DepotDEBYKNOrders = 'business_depotDEBYKN-DepotDEBYKNOrders'
    datumSpalteLSüber = 'CreatedTimeStamp'
    tabelle_DepotDEBYKNOrderItems = 'business_depotDEBYKN-DepotDEBYKNOrderItems'


    def verbinder():

        conn_settings = ConnectionSettings(    
        server = 'batsql-pp-ne-cmes-prod-10',
        database= 'batsdb-pp-ne-prod-reporting_SuperDepot',
        username='batedp-cmes-prod-reportinguser',
        password='b2.5v^H!IKjetuXMVNvW')
        db_conn = AzureDbConnection(conn_settings)
        return db_conn
    
    def sql_datenLadenDatum(day1, day2, tabellenName,datumsSpalte):
        '''erwartet zwei Datumsangaben im Format 'YYYY-MM-DD' 
        und den Tabellennamen als String  
        day 1 Startwert z.B 2020-01-01   
        day 2 Endwert z.B 2020-01-31,   
        vorhandene Tabellen sind:,
        'dds',
        'business_depotDEBYKN-LabelPrintOrders',
        'business_depotDEBYKN-DepotDEBYKNOrderItems', 
        'business_depotDEBYKN-DepotDEBYKNOrders',
        'data_materialmaster-MaterialMasterUnitOfMeasures'''
        
        sqlQuery = f"SELECT * FROM [{tabellenName}] WHERE [{datumsSpalte}] BETWEEN '{day1}' AND '{day2}'"
        db_conn = verbinder()
        db_conn.connect()
        df = pd.read_sql(sqlQuery, db_conn.conn)
        db_conn.dispose()
        return df

    

def verbinderTestServer():

    conn_settings = ConnectionSettings(
    server='batsql-pd-ne-cmes-dev-10',
    database='batsdb-pd-ne-dev-reporting_SuperDepot',
    username='batedp-cmes-dev-reportinguser',
    password='b2.5v^H!IKjetuXMVNvW')

    db_conn = AzureDbConnection(conn_settings)
    return db_conn

def verbinder():

    conn_settings = ConnectionSettings(    
    server = 'batsql-pp-ne-cmes-prod-10',
    database= 'batsdb-pp-ne-prod-reporting_SuperDepot',
    username='batedp-cmes-prod-reportinguser',
    password='b2.5v^H!IKjetuXMVNvW')
    db_conn = AzureDbConnection(conn_settings)
    return db_conn

def createnewTable(df, tableName):
    db_conn = verbinder()
    db_conn.connect()
    df.to_sql(tableName, db_conn.conn, if_exists='replace', index=False)
    db_conn.dispose()

# Usereingaben/Interne Datenbanken
def datenLadenUser():
    db_conn = verbinder()
    db_conn.connect()
    df= pd.read_sql('SELECT * FROM [user]', db_conn.conn)
    db_conn.dispose()
    return df
def updateUser(df):
    db_conn = verbinder()
    db_conn.connect()
    df.to_sql('user', db_conn.conn, if_exists='replace', index=False)
    db_conn.dispose()

def sql_datenLadenMLGT():
    db_conn = verbinder()
    db_conn.connect()
    df= pd.read_sql('SELECT * FROM [MLGT_Stellplatz]', db_conn.conn)
    db_conn.dispose()
    return df

def datenLadenMitarbeiter():
    db_conn = verbinderTestServer()
    db_conn.connect()
    dfMitarbeiter = pd.read_sql('SELECT * FROM [Mitarbeiter]', db_conn.conn)
    db_conn.dispose()
    return dfMitarbeiter   
def datenSpeichernMitarbeiter(dfMitarbeiter):
    db_conn = verbinderTestServer()
    db_conn.connect()
    #save dfMitarbeiter to Azure SQL
    dfMitarbeiter.to_sql('Mitarbeiter', db_conn.conn, if_exists='replace', index=False)
    db_conn.dispose()
def datenLadenFehlverladungen():
    db_conn = verbinder()
    db_conn.connect()
    dfMitarbeiter = pd.read_sql('SELECT * FROM [issues]', db_conn.conn)
    db_conn.dispose()
    return dfMitarbeiter   
def datenSpeichernFehlverladungen(df):
    db_conn = verbinder()
    db_conn.connect()
    # change index to id 
    df.to_sql('issues', db_conn.conn, if_exists='replace', index=False)
    db_conn.dispose()
def datenSpeichern_CS_OUT_STammdaten(df):
    db_conn = verbinder()
    db_conn.connect()
    #save dfMitarbeiter to Azure SQL
    df.to_sql('Mitarbeiter', db_conn.conn, if_exists='replace', index=False)
    db_conn.dispose()
# Externe Datenbanken
def sql_datenLadenLabel():
    db_conn = verbinder()
    db_conn.connect()
    dfLabel = pd.read_sql('SELECT * FROM [business_depotDEBYKN-LabelPrintOrders]', db_conn.conn)
    return dfLabel
def sql_datenLadenStammdaten():
    db_conn = verbinder()
    db_conn.connect()
    dfStammdaten = pd.read_sql('SELECT * FROM [data_materialmaster-MaterialMasterUnitOfMeasures]', db_conn.conn)
    return dfStammdaten
def sql_datenLadenMaster_CS_OUT():
    db_conn = verbinder()
    db_conn.connect()
    #load  only from dbo.MaterialMasterUnitOfMeasures if is in 'UnitOfMeasureId' == CS, OUT, D97
    df = pd.read_sql('SELECT * FROM [data_materialmaster-MaterialMasterUnitOfMeasures] WHERE [UnitOfMeasure] IN (\'CS\', \'OUT\', \'D97\')', db_conn.conn)
    return df
def sql_datenLadenOder():
    db_conn = verbinder()
    db_conn.connect()
    df = pd.read_sql('SELECT * FROM [business_depotDEBYKN-DepotDEBYKNOrders]', db_conn.conn)
    db_conn.dispose()
    return df  
def sql_datenLadenOderItems():
    db_conn = verbinder()
    db_conn.connect()
    df = pd.read_sql('SELECT * FROM [business_depotDEBYKN-DepotDEBYKNOrderItems]', db_conn.conn)
    db_conn.dispose()
    return df  

def sql_datenLadenKunden():
    db_conn = verbinder()
    db_conn.connect()
    df = pd.read_sql('SELECT * FROM [Kunden_mit_Packinfos]', db_conn.conn)
    db_conn.dispose()
    return df  

def sql_datenLadenDDS():
    db_conn = verbinder()
    db_conn.connect()
    df = pd.read_sql('SELECT * FROM [dds]', db_conn.conn)
    db_conn.dispose()
    return df  