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
    '''Ermöglicht die Auswahl von Spalten aus bestimmten Tabellen
    sowie Datumsbereich
    und gibt diese als DataFrame zurück'''
    
    tabelle_DepotDEBYKNOrders = 'business_depotDEBYKN-DepotDEBYKNOrders'
    datumSpalteLSüber = 'CreatedTimeStamp'
    '''Wann wurde der Lieferschein von HH übergeben'''
    datumplannedDate = 'PlannedDate'
    '''Wann sollte der Lieferschein verladen werden zum Depot werden'''
    tabelle_DepotDEBYKNOrderItems = 'business_depotDEBYKN-DepotDEBYKNOrderItems'
    tabelleSSCCLabel = 'business_depotDEBYKN-DepotOrderDEBYKN_SSCCs'
    ## Tabelle mit den SSCC Labeln
    tabelleUser = 'user' # Tabelle mit den Usern Passwörtern etc.
    tabellemitarbeiter = 'Mitarbeiter' # Tabelle mit den Mitarbeitern
    tabelleSAP_lt22 = 'upload_SAP_lt22' # Tabelle mit den SAP lt22

    def verbinder():

        conn_settings = ConnectionSettings(    
        server = 'batsql-pp-ne-cmes-prod-10',
        database= 'batsdb-pp-ne-prod-reporting_SuperDepot',
        username='batedp-cmes-prod-reportinguser',
        password='b2.5v^H!IKjetuXMVNvW')
        db_conn = AzureDbConnection(conn_settings)
        return db_conn
    
    ### Tabellen erstellen
    def sql_createTable(tabellenName, df):
        '''erwartet den Tabellennamen als String und ein DataFrame'''
        db_conn = SQL_TabellenLadenBearbeiten.verbinder()
        db_conn.connect()
        df.to_sql(tabellenName, db_conn.conn, if_exists='replace', index=True, index_label='id', chunksize=1000)
        db_conn.dispose()
        return print(f'Tabelle {tabellenName} wurde erstellt')
    
    ### TABELLEN LADEN
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
        db_conn = SQL_TabellenLadenBearbeiten.verbinder()
        db_conn.connect()
        df = pd.read_sql(sqlQuery, db_conn.conn)
        db_conn.dispose()
        return df

    def sql_datenTabelleLaden(tabellenName):
        '''erwartet den Tabellennamen als String'''
        db_conn = SQL_TabellenLadenBearbeiten.verbinder()
        db_conn.connect()
        df = pd.read_sql(f"SELECT * FROM [{tabellenName}]", db_conn.conn)
        db_conn.dispose()
        return df

    def sql_Stammdaten():
        db_conn = SQL_TabellenLadenBearbeiten.verbinder()
        db_conn.connect()
        df = pd.read_sql('SELECT [UnitOfMeasure],[MaterialNumber], [NumeratorToBaseUnitOfMeasure], [DenominatorToBaseUnitOfMeasure] FROM [data_materialmaster-MaterialMasterUnitOfMeasures] WHERE [UnitOfMeasure] IN (\'CS\', \'OUT\', \'D97\')', db_conn.conn)
        db_conn.dispose()
        return df

    def sql_datenLadenItems(orders):
        # order is a list of numbers from dataframe now we need to get the items from the SapOrderNumber
        
        db_conn = SQL_TabellenLadenBearbeiten.verbinder()
        db_conn.connect()
        df = pd.read_sql(f"SELECT * FROM [business_depotDEBYKN-DepotDEBYKNOrderItems] WHERE [SapOrderNumber] IN {(orders)}", db_conn.conn)
        db_conn.dispose()
        return df
    ### Update von Tabellen

    def sql_trunkTable(tabellenName):
        '''erwartet den Tabellennamen als String'''
        db_conn = SQL_TabellenLadenBearbeiten.verbinder()
        db_conn.connect()
        db_conn.conn.execute(f"TRUNCATE TABLE [{tabellenName}]")
        db_conn.dispose()
        return print(f'Tabelle {tabellenName} wurde geleert')
    
    def sql_test(tabellenName, df):
        # truncate
        # Einfügen der Werte
        db_conn = SQL_TabellenLadenBearbeiten.verbinder()
        db_conn.connect() 
        with AzureDbConnection.db.begin() as connection:
            connection.execute(f"TRUNCATE TABLE [{tabellenName}]")
            df.to_sql(tabellenName, connection, if_exists='replace', index=False, chunksize=10000)
        return print(f'Tabelle {tabellenName} wurde geleert und neu befüllt')

    def sql_updateTabelle(tabellenName, df):
        '''expects table name as a string and a DataFrame'''

        db_conn = SQL_TabellenLadenBearbeiten.verbinder()
        db_conn.connect()
        df.to_sql(tabellenName, db_conn.conn, if_exists='replace', index=False, chunksize=1000)
        db_conn.dispose()
        return 'Table was successfully updated'
        
    ##löschen von einträgen in Tabelle
    def sql_deleteEintrag(tabellenName, eintrag):
        '''erwartet den Tabellennamen als String und ein DataFrame'''
        db_conn = SQL_TabellenLadenBearbeiten.verbinder()
        db_conn.connect()
        db_conn.conn.execute(f"DELETE FROM [{tabellenName}] WHERE [Index] = {eintrag}")
        db_conn.dispose()
        return 'Eintrag wurde erfolgreich gelöscht'
    
    ##Löschen einer Tabelle
    def sql_deleteTabelle(tabellenName):
        '''erwartet den Tabellennamen als String'''
        db_conn = SQL_TabellenLadenBearbeiten.verbinder()
        db_conn.connect()
        db_conn.conn.execute(f"DROP TABLE [{tabellenName}]")
        db_conn.dispose()
        return 'Tabelle wurde erfolgreich gelöscht'
