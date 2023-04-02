from dataclasses import dataclass
from typing import Dict, Any, Iterable
from pandas import DataFrame
from sqlalchemy import create_engine, inspect
import urllib
import pandas as pd
import time

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

    def verbinder():

        conn_settings = ConnectionSettings(    
        server = 'batsql-pp-ne-cmes-prod-10',
        database= 'batsdb-pp-ne-prod-reporting_SuperDepot',
        username='batedp-cmes-prod-reportinguser',
        password='b2.5v^H!IKjetuXMVNvW')
        db_conn = AzureDbConnection(conn_settings)
        return db_conn
    
    def readAlltablesNames():
        db_conn = verbinder()
        db_conn.connect()
        tables = db_conn.get_tables()
        db_conn.dispose()
        return tables

    ### Tabellen erstellen
    def sql_createTable(tabellenName, df):
        '''erwartet den Tabellennamen als String und ein DataFrame'''
        db_conn = verbinder()
        db_conn.connect()
        df.to_sql(tabellenName, db_conn.conn, if_exists='replace')
        db_conn.dispose()
        return print(f'Tabelle {tabellenName} wurde erstellt')
    
    ## Tabellen bearbeiten
    def addtoTable(tabellenName, df):
        db_conn = verbinder()
        db_conn.connect()
        dfOrg = pd.read_sql(f"SELECT * FROM [{tabellenName}]", db_conn.conn)
        #readlastIndex of dfOrg
        lastindex = dfOrg.index[-1]
        #add new rows to database table
        df.to_sql(tabellenName, db_conn.conn, if_exists='append', index=False, chunksize=300)
        #read new table
        dfNew = pd.read_sql(f"SELECT * FROM [{tabellenName}]", db_conn.conn)
        #read new last index
        lastindexNew = dfNew.index[-1]
        #compare new last index with old last index
        if lastindexNew == lastindex:
            print('Keine neuen Daten eingefügt')
        else:
            print('Neue Daten eingefügt')
        db_conn.dispose()


    def trunk_Update(tabellenName, df):
        # truncate
        start_time = time.time()
        db_conn = SQL_TabellenLadenBearbeiten.verbinder()
        db_conn.connect() 
        with AzureDbConnection.db.begin() as connection:
            connection.execute(f"TRUNCATE TABLE [{tabellenName}]")
            insert_start_time = time.time()
            df.to_sql(tabellenName, connection, if_exists='replace', index=False, chunksize=5,method='multi')
            insert_end_time = time.time()
        end_time = time.time()
        print(f'Tabelle {tabellenName} wurde geleert und neu befüllt')
        print(f"Time taken to truncate table: {insert_start_time - start_time:.2f} seconds")
        print(f"Time taken to insert data: {insert_end_time - insert_start_time:.2f} seconds")
        print(f"Total time taken: {end_time - start_time:.2f} seconds")
        return print(f'Tabelle {tabellenName} wurde geleert und neu befüllt')
    

    def sql_updateTabelle(tabellenName, df):
        '''erwartet den Tabellennamen als String und ein DataFrame'''
        db_conn = verbinder()
        db_conn.connect()
        df.to_sql(tabellenName, db_conn.conn, if_exists='replace', index=False)
        db_conn.dispose()
        return 'Tabelle wurde erfolgreich aktualisiert'
    

    def sql_deleteEintrag(tabellenName, eintrag):
        '''erwartet den Tabellennamen als String und ein DataFrame'''
        db_conn = verbinder()
        db_conn.connect()
        db_conn.conn.execute(f"DELETE FROM [{tabellenName}] WHERE [Index] = {eintrag}")
        db_conn.dispose()
        return 'Eintrag wurde erfolgreich gelöscht'
    
    ### TABELLEN LADEN
    
    def load_table_by_order_number(table_name: str, order_numbers: list[str]) -> pd.DataFrame:
        db_conn = verbinder()
        db_conn.connect()
        
        # Split order_numbers into batches of max_size
        max_size = 50  # or any other number that works for your case
        order_number_batches = [order_numbers[i:i+max_size] for i in range(0, len(order_numbers), max_size)]
        
        dfs = []
        for batch in order_number_batches:
            # Build SQL query to filter table by SAP Order Numbers
            sap_order_numbers = "', '".join(batch)
            query = f"SELECT * FROM [{table_name}] WHERE SapOrderNumber IN ('{sap_order_numbers}')"

            # Execute SQL query and append result to dfs
            df = pd.read_sql_query(query, db_conn.conn)
            dfs.append(df)
        
        db_conn.dispose()
        return pd.concat(dfs, ignore_index=True)


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
        
        sqlQuery = f"SELECT * FROM [{tabellenName}] WHERE {datumsSpalte} BETWEEN '{day1}' AND '{day2}'"
        db_conn = verbinder()
        db_conn.connect()
        df = pd.read_sql(sqlQuery, db_conn.conn)
        db_conn.dispose()
        return df


    def sql_datenTabelleLaden(tabellenName):
        '''erwartet den Tabellennamen als String'''
        db_conn = verbinder()
        db_conn.connect()
        df = pd.read_sql(f"SELECT * FROM [{tabellenName}]", db_conn.conn)
        db_conn.dispose()
        return df


    def sql_Stammdaten():
        db_conn = verbinder()
        db_conn.connect()
        df = pd.read_sql('SELECT [UnitOfMeasure],[MaterialNumber], [NumeratorToBaseUnitOfMeasure], [DenominatorToBaseUnitOfMeasure] FROM [data_materialmaster-MaterialMasterUnitOfMeasures] WHERE [UnitOfMeasure] IN (\'CS\', \'OUT\', \'D97\')', db_conn.conn)
        db_conn.dispose()
        return df


    ##Löschen einer Tabelle
    def sql_deleteTabelle(tabellenName):
        '''erwartet den Tabellennamen als String'''
        db_conn = verbinder()
        db_conn.connect()
        db_conn.conn.execute(f"DROP TABLE [{tabellenName}]")
        db_conn.dispose()
        return 'Tabelle wurde erfolgreich gelöscht'

def verbinder():

    conn_settings = ConnectionSettings(    
    server = 'batsql-pp-ne-cmes-prod-10',
    database= 'batsdb-pp-ne-prod-reporting_SuperDepot',
    username='batedp-cmes-prod-reportinguser',
    password='b2.5v^H!IKjetuXMVNvW')
    db_conn = AzureDbConnection(conn_settings)
    return db_conn




















    db_conn = verbinder()
    db_conn.connect()
    df = pd.read_sql('SELECT * FROM [dds]', db_conn.conn)
    db_conn.dispose()
    return df  