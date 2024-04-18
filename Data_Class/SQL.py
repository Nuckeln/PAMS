from sqlalchemy import create_engine
import pandas as pd
from sqlalchemy import text
import os

#credentials = os.environ['SQLAZURECONNSTR_DbConnection']

def return_table_names():
    server = "batsql-pp-ne-cmes-prod-10.database.windows.net"
    database = "batsdb-pp-ne-prod-reporting_SuperDepot"
    username = "batedp-cmes-prod-reportinguser"
    password = "b2.5v^H!IKjetuXMVNvW"

    # Datenbankverbindung erstellen
    engine = create_engine(f'mssql+pyodbc://{username}:{password}@{server}/{database}?driver=ODBC+Driver+17+for+SQL+Server')

    # Tabellennamen abrufen
    with engine.connect() as conn:
        query = text("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE='BASE TABLE'")
        result = conn.execute(query)
        table_names = [row[0] for row in result]

    return table_names

def save_table_to_SQL(df: pd.DataFrame, table_name: str, batch_size: int = 10):
    server = "batsql-pp-ne-cmes-prod-10.database.windows.net"
    database = "batsdb-pp-ne-prod-reporting_SuperDepot"
    username = "batedp-cmes-prod-reportinguser"
    password = "b2.5v^H!IKjetuXMVNvW"

    # Datenbankverbindung erstellen
    engine = create_engine(f'mssql+pyodbc://{username}:{password}@{server}/{database}?driver=ODBC+Driver+17+for+SQL+Server')

    # DataFrame in Chargen schreiben
    start = 0
    end = batch_size
    while start < len(df):
        batch_df = df.iloc[start:end]
        batch_df.to_sql(table_name, engine, if_exists='append', index=False)
        start = end
        end += batch_size

    return 'Success'

def truncateTableAndSave(df: pd.DataFrame, table_name: str, batch_size: int = 1000):
    server = "batsql-pp-ne-cmes-prod-10.database.windows.net"
    database = "batsdb-pp-ne-prod-reporting_SuperDepot"
    username = "batedp-cmes-prod-reportinguser"
    password = "b2.5v^H!IKjetuXMVNvW"
    
    engine = create_engine(f'mssql+pyodbc://{username}:{password}@{server}/{database}?driver=ODBC+Driver+17+for+SQL+Server')
    engine.connect()
    engine.execute(f"TRUNCATE TABLE [{table_name}]")
    engine.dispose()

    return print('Table truncated and loaded successfully')

def loescheTable(table_name):
    server = "batsql-pp-ne-cmes-prod-10.database.windows.net"
    database = "batsdb-pp-ne-prod-reporting_SuperDepot"
    username = "batedp-cmes-prod-reportinguser"
    password = "b2.5v^H!IKjetuXMVNvW"
    # Datenbankverbindung erstellen
    engine = create_engine(f'mssql+pyodbc://{username}:{password}@{server}/{database}?driver=ODBC+Driver+17+for+SQL+Server')

    engine.connect()
    engine.execute(f"DROP TABLE [{table_name}]")
    engine.dispose()

    return print(f'Table {table_name} deleted successfully')

def read_table(table_name: str):
    server = "batsql-pp-ne-cmes-prod-10.database.windows.net"
    database = "batsdb-pp-ne-prod-reporting_SuperDepot"
    username = "batedp-cmes-prod-reportinguser"
    password = "b2.5v^H!IKjetuXMVNvW"
    connection_string = f'mssql+pyodbc://{username}:{password}@{server}/{database}?driver=ODBC+Driver+17+for+SQL+Server'
    engine = create_engine(connection_string)
    query = f"SELECT * FROM {table_name}"
    df = pd.read_sql(query, engine)
    return df

def updateTable(df: pd.DataFrame, table_name: str):
    server = "batsql-pp-ne-cmes-prod-10.database.windows.net"
    database = "batsdb-pp-ne-prod-reporting_SuperDepot"
    username = "batedp-cmes-prod-reportinguser"
    password = "b2.5v^H!IKjetuXMVNvW"
    # Datenbankverbindung erstellen
    engine = create_engine(f'mssql+pyodbc://{username}:{password}@{server}/{database}?driver=ODBC+Driver+17+for+SQL+Server')
    # SQL-Befehl laden der Tabelle
    df.to_sql(table_name, engine, if_exists='replace', index=False)

def read_MasterData():
    server = "batsql-pp-ne-cmes-prod-10.database.windows.net"
    database = "batsdb-pp-ne-prod-reporting_SuperDepot"
    username = "batedp-cmes-prod-reportinguser"
    password = "b2.5v^H!IKjetuXMVNvW"
    # Datenbankverbindung erstellen
    engine = create_engine(f'mssql+pyodbc://{username}:{password}@{server}/{database}?driver=ODBC+Driver+17+for+SQL+Server')
    # SQL-Befehl laden der Tabelle
    df = pd.read_sql('SELECT [UnitOfMeasure],[MaterialNumber],[Height],[Length],[Width], [NumeratorToBaseUnitOfMeasure], [DenominatorToBaseUnitOfMeasure] FROM [data_materialmaster-MaterialMasterUnitOfMeasures] WHERE [UnitOfMeasure] IN (\'CS\', \'OUT\', \'D97\')', engine)
    # Datenframe aus der Datenbank laden

    return df

