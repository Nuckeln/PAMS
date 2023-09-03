from dataclasses import dataclass
from typing import Dict, Any, Iterable
from pandas import DataFrame
from sqlalchemy import create_engine, inspect
import urllib
import pandas as pd
import time
import json

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

def read_Table(table_name):
    json_path = 'Data/appData/credentials.json'
    conn_settings = load_connection_settings(json_path)
    db_conn = AzureDbConnection(conn_settings)
    # Verbindung herstellen
    db_conn.connect()
    # Hier kannst du die Verbindung verwenden, z.B. Abfragen ausführen oder Tabellen abrufen
    df = pd.read_sql(f"SELECT * FROM [{table_name}]", db_conn.db)
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
    # Split order_numbers into batches of max_size
    max_size = 50  # or any other number that works for your case
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


# if __name__ == "__main__":
#     main()

#     def readAlltablesNames():
#         db_conn = verbinder()
#         db_conn.connect()
#         tables = db_conn.get_tables()
#         db_conn.dispose()
#         return tables

#     ### Tabellen erstellen
#     def sql_createTable(tabellenName, df):
#         '''erwartet den Tabellennamen als String und ein DataFrame'''
#         db_conn = verbinder()
#         db_conn.connect()
#         df.to_sql(tabellenName, db_conn.conn, if_exists='replace')
#         db_conn.dispose()
#         return print(f'Tabelle {tabellenName} wurde erstellt')
    
#     ## Tabellen bearbeiten
#     def addtoTable(tabellenName, df):
#         db_conn = verbinder()
#         db_conn.connect()
#         dfOrg = pd.read_sql(f"SELECT * FROM [{tabellenName}]", db_conn.conn)
#         #readlastIndex of dfOrg
#         lastindex = dfOrg.index[-1]
#         #add new rows to database table
#         df.to_sql(tabellenName, db_conn.conn, if_exists='append', index=False, chunksize=300)
#         #read new table
#         dfNew = pd.read_sql(f"SELECT * FROM [{tabellenName}]", db_conn.conn)
#         #read new last index
#         lastindexNew = dfNew.index[-1]
#         #compare new last index with old last index
#         if lastindexNew == lastindex:
#             print('Keine neuen Daten eingefügt')
#         else:
#             print('Neue Daten eingefügt')
#         db_conn.dispose()


#     def trunk_Update(tabellenName, df):
#         # truncate
#         start_time = time.time()
#         db_conn = SQL_TabellenLadenBearbeiten.verbinder()
#         db_conn.connect() 
#         with AzureDbConnection.db.begin() as connection:
#             connection.execute(f"TRUNCATE TABLE [{tabellenName}]")
#             insert_start_time = time.time()
#             df.to_sql(tabellenName, connection, if_exists='replace', index=False, chunksize=5,method='multi')
#             insert_end_time = time.time()
#         end_time = time.time()
#         print(f'Tabelle {tabellenName} wurde geleert und neu befüllt')
#         print(f"Time taken to truncate table: {insert_start_time - start_time:.2f} seconds")
#         print(f"Time taken to insert data: {insert_end_time - insert_start_time:.2f} seconds")
#         print(f"Total time taken: {end_time - start_time:.2f} seconds")
#         return print(f'Tabelle {tabellenName} wurde geleert und neu befüllt')
    

#     def sql_updateTabelle(tabellenName, df):
#         '''erwartet den Tabellennamen als String und ein DataFrame'''
#         db_conn = verbinder()
#         db_conn.connect()
#         df.to_sql(tabellenName, db_conn.conn, if_exists='replace', index=False)
#         db_conn.dispose()
#         return 'Tabelle wurde erfolgreich aktualisiert'
    

#     def sql_deleteEintrag(tabellenName, eintrag):
#         '''erwartet den Tabellennamen als String und ein DataFrame'''
#         db_conn = verbinder()
#         db_conn.connect()
#         db_conn.conn.execute(f"DELETE FROM [{tabellenName}] WHERE [Index] = {eintrag}")
#         db_conn.dispose()
#         return 'Eintrag wurde erfolgreich gelöscht'
    
#     ### TABELLEN LADEN
    
#     def load_table_by_order_number(table_name: str, order_numbers: list[str]) -> pd.DataFrame:
#         db_conn = verbinder()
#         db_conn.connect()
        
#         # Split order_numbers into batches of max_size
#         max_size = 50  # or any other number that works for your case
#         order_number_batches = [order_numbers[i:i+max_size] for i in range(0, len(order_numbers), max_size)]
        
#         dfs = []
#         for batch in order_number_batches:
#             # Build SQL query to filter table by SAP Order Numbers
#             sap_order_numbers = "', '".join(batch)
#             query = f"SELECT * FROM [{table_name}] WHERE SapOrderNumber IN ('{sap_order_numbers}')"

#             # Execute SQL query and append result to dfs
#             df = pd.read_sql_query(query, db_conn.conn)
#             dfs.append(df)
        
#         db_conn.dispose()
#         return pd.concat(dfs, ignore_index=True)


#     def sql_datenLadenDatum(day1, day2, tabellenName,datumsSpalte):
#         '''erwartet zwei Datumsangaben im Format 'YYYY-MM-DD' 
#         und den Tabellennamen als String  
#         day 1 Startwert z.B 2020-01-01   
#         day 2 Endwert z.B 2020-01-31,   
#         vorhandene Tabellen sind:,
#         'dds',
#         'business_depotDEBYKN-LabelPrintOrders',
#         'business_depotDEBYKN-DepotDEBYKNOrderItems', 
#         'business_depotDEBYKN-DepotDEBYKNOrders',
#         'data_materialmaster-MaterialMasterUnitOfMeasures'''
        
#         sqlQuery = f"SELECT * FROM [{tabellenName}] WHERE {datumsSpalte} BETWEEN '{day1}' AND '{day2}'"
#         db_conn = verbinder()
#         db_conn.connect()
#         df = pd.read_sql(sqlQuery, db_conn.conn)
#         db_conn.dispose()
#         return df


#     def sql_datenTabelleLaden(tabellenName):
#         '''erwartet den Tabellennamen als String'''
#         db_conn = verbinder()
#         db_conn.connect()
#         df = pd.read_sql(f"SELECT * FROM [{tabellenName}]", db_conn.conn)
#         db_conn.dispose()
#         return df


#     def sql_Stammdaten():
#         db_conn = verbinder()
#         db_conn.connect()
#         df = pd.read_sql('SELECT [UnitOfMeasure],[MaterialNumber], [NumeratorToBaseUnitOfMeasure], [DenominatorToBaseUnitOfMeasure] FROM [data_materialmaster-MaterialMasterUnitOfMeasures] WHERE [UnitOfMeasure] IN (\'CS\', \'OUT\', \'D97\')', db_conn.conn)
#         db_conn.dispose()
#         return df


#     ##Löschen einer Tabelle
#     def sql_deleteTabelle(tabellenName):
#         '''erwartet den Tabellennamen als String'''
#         db_conn = verbinder()
#         db_conn.connect()
#         db_conn.conn.execute(f"DROP TABLE [{tabellenName}]")
#         db_conn.dispose()
#         return 'Tabelle wurde erfolgreich gelöscht'


























# def verbinderTestServer():

#     conn_settings = ConnectionSettings(
#     server='batsql-pd-ne-cmes-dev-10',
#     database='batsdb-pd-ne-dev-reporting_SuperDepot',
#     username='batedp-cmes-dev-reportinguser',
#     password='b2.5v^H!IKjetuXMVNvW')

#     db_conn = AzureDbConnection(conn_settings)
#     return db_conn

# def verbinder():

#     conn_settings = ConnectionSettings(    
#     server = 'batsql-pp-ne-cmes-prod-10',
#     database= 'batsdb-pp-ne-prod-reporting_SuperDepot',
#     username='batedp-cmes-prod-reportinguser',
#     password='b2.5v^H!IKjetuXMVNvW')
#     db_conn = AzureDbConnection(conn_settings)
#     return db_conn

# def createnewTable(df, tableName):
#     db_conn = verbinder()
#     db_conn.connect()
#     df.to_sql(tableName, db_conn.conn, if_exists='replace', index=False)
#     db_conn.dispose()

# # Usereingaben/Interne Datenbanken
# def datenLadenUser():
#     db_conn = verbinder()
#     db_conn.connect()
#     df= pd.read_sql('SELECT * FROM [user]', db_conn.conn)
#     db_conn.dispose()
#     return df
# def updateUser(df):
#     db_conn = verbinder()
#     db_conn.connect()
#     df.to_sql('user', db_conn.conn, if_exists='replace', index=False)
#     db_conn.dispose()

# def sql_datenLadenMLGT():
#     db_conn = verbinder()
#     db_conn.connect()
#     df= pd.read_sql('SELECT * FROM [MLGT_Stellplatz]', db_conn.conn)
#     db_conn.dispose()
#     return df

# def datenLadenMitarbeiter():
#     db_conn = verbinderTestServer()
#     db_conn.connect()
#     dfMitarbeiter = pd.read_sql('SELECT * FROM [Mitarbeiter]', db_conn.conn)
#     db_conn.dispose()
#     return dfMitarbeiter   
# def datenSpeichernMitarbeiter(dfMitarbeiter):
#     db_conn = verbinderTestServer()
#     db_conn.connect()
#     #save dfMitarbeiter to Azure SQL
#     dfMitarbeiter.to_sql('Mitarbeiter', db_conn.conn, if_exists='replace', index=False)
#     db_conn.dispose()
# def datenLadenFehlverladungen():
#     db_conn = verbinder()
#     db_conn.connect()
#     dfMitarbeiter = pd.read_sql('SELECT * FROM [issues]', db_conn.conn)
#     db_conn.dispose()
#     return dfMitarbeiter   
# def datenSpeichernFehlverladungen(df):
#     db_conn = verbinder()
#     db_conn.connect()
#     # change index to id 
#     df.to_sql('issues', db_conn.conn, if_exists='replace', index=False)
#     db_conn.dispose()
# def datenSpeichern_CS_OUT_STammdaten(df):
#     db_conn = verbinder()
#     db_conn.connect()
#     #save dfMitarbeiter to Azure SQL
#     df.to_sql('Mitarbeiter', db_conn.conn, if_exists='replace', index=False)
#     db_conn.dispose()
# # Externe Datenbanken
# def sql_datenLadenLabel():
#     db_conn = verbinder()
#     db_conn.connect()
#     dfLabel = pd.read_sql('SELECT * FROM [business_depotDEBYKN-LabelPrintOrders]', db_conn.conn)
#     return dfLabel
# def sql_datenLadenStammdaten():
#     db_conn = verbinder()
#     db_conn.connect()
#     dfStammdaten = pd.read_sql('SELECT * FROM [data_materialmaster-MaterialMasterUnitOfMeasures]', db_conn.conn)
#     return dfStammdaten
# def sql_datenLadenMaster_CS_OUT():
#     db_conn = verbinder()
#     db_conn.connect()
#     #load  only from dbo.MaterialMasterUnitOfMeasures if is in 'UnitOfMeasureId' == CS, OUT, D97 and load only Columns [UnitOfMeasure],[MaterialNumber],[SnapshotId],[NumeratorToBaseUnitOfMeasure],[DenominatorToBaseUnitOfMeasure]
#     df = pd.read_sql('SELECT * FROM [data_materialmaster-MaterialMasterUnitOfMeasures] WHERE [UnitOfMeasure] IN (\'CS\', \'OUT\', \'D97\')', db_conn.conn)
#     return df
# def sql_datenLadenOder():
#     db_conn = verbinder()
#     db_conn.connect()
#     df = pd.read_sql('SELECT * FROM [business_depotDEBYKN-DepotDEBYKNOrders]', db_conn.conn)
#     db_conn.dispose()
#     return df  
# def sql_datenLadenOderItems():
#     db_conn = verbinder()
#     db_conn.connect()
#     df = pd.read_sql('SELECT * FROM [business_depotDEBYKN-DepotDEBYKNOrderItems]', db_conn.conn)
#     db_conn.dispose()
#     return df  

# def sql_datenLadenKunden():
#     db_conn = verbinder()
#     db_conn.connect()
#     df = pd.read_sql('SELECT * FROM [Kunden_mit_Packinfos]', db_conn.conn)
#     db_conn.dispose()
#     return df  

# def sql_datenLadenDDS():
#     db_conn = verbinder()
#     db_conn.connect()
#     df = pd.read_sql('SELECT * FROM [dds]', db_conn.conn)
#     db_conn.dispose()
#     return df  