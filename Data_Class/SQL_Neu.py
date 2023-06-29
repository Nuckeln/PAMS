from sqlalchemy import create_engine
import pandas as pd

def save_table_to_SQL(df: pd.DataFrame, table_name: str):
    server = "batsql-pp-ne-cmes-prod-10.database.windows.net"
    database = "batsdb-pp-ne-prod-reporting_SuperDepot"
    username = "batedp-cmes-prod-reportinguser"
    password = "b2.5v^H!IKjetuXMVNvW"

    # Datenbankverbindung erstellen
    engine = create_engine(f'mssql+pyodbc://{username}:{password}@{server}/{database}?driver=ODBC+Driver+18+for+SQL+Server')

    # SQL-Befehl zum Löschen des Tabelleninhalts
    delete_query = f"DELETE FROM {table_name}"
    try:
        engine.execute(delete_query)
    except Exception as e:
        return f'Error: {str(e)}'

    # Datenframe in die Datenbank schreiben
    df.to_sql(table_name, engine, if_exists='append', index=False)

    return 'Success'

def read_table(table_name: str):
    server = "batsql-pp-ne-cmes-prod-10.database.windows.net"
    database = "batsdb-pp-ne-prod-reporting_SuperDepot"
    username = "batedp-cmes-prod-reportinguser"
    password = "b2.5v^H!IKjetuXMVNvW"
    # Datenbankverbindung erstellen
    engine = create_engine(f'mssql+pyodbc://{username}:{password}@{server}/{database}?driver=ODBC+Driver+18+for+SQL+Server')
    # SQL-Befehl laden der Tabelle
    query = f"SELECT * FROM {table_name}"
    # Datenframe aus der Datenbank laden
    df = pd.read_sql(query, engine)
    if table_name == 'SAP_lt22':
        
# Table SAP_lt22 Spaltennamen wiederherstellen 
        column_names = {
            'Transfer_Order_Number': 'Transfer Order Number',
            'Material': 'Material',
            'Stock_Category': 'Stock Category',
            'Special_Stock': 'Special Stock',
            'Source_Storage_Type': 'Source Storage Type',
            'Source_Storage_Bin': 'Source Storage Bin',
            'Source_Storage_Unit': 'Source storage unit',
            'Source_Target_Qty': 'Source target qty',
            'Alternative_Unit_of_Measure': 'Alternative Unit of Measure',
            'Material_Description': 'Material Description',
            'Confirmation_Time': 'Confirmation time',
            'Confirmation_Date': 'Confirmation date',
            'User': 'User',
            'User_1': 'User.1',
            'Plant': 'Plant',
            'Creation_Time': 'Creation time',
            'Confirmation_Time_1': 'Confirmation time.1',
            'Creation_Date': 'Creation Date',
            'Filler': 'Filler',
            'Dest_Storage_Type': 'Dest. Storage Type',
            'Dest_Storage_Bin': 'Dest.Storage Bin',
            'Dest_Target_Quantity': 'Dest.target quantity',
            'Filler_1': 'Filler.1'
        }

        # Spaltennamen in der Datenbanktabelle wiederherstellen
        df.rename(columns=column_names, inplace=True)

    return df

from sqlalchemy import text

def updateTable(df, table_name: str):
    server = "batsql-pp-ne-cmes-prod-10.database.windows.net"
    database = "batsdb-pp-ne-prod-reporting_SuperDepot"
    username = "batedp-cmes-prod-reportinguser"
    password = "b2.5v^H!IKjetuXMVNvW"
    # Datenbankverbindung erstellen
    engine = create_engine(f'mssql+pyodbc://{username}:{password}@{server}/{database}?driver=ODBC+Driver+18+for+SQL+Server')
    
    print(f"Deleting records from table: {table_name}")
    delete_statement = text(f"DELETE FROM [{table_name}]")
    print(f"Executing: {delete_statement}")
    with engine.connect() as conn:
        conn.execute(delete_statement)
        print("Appending records to table")
        df.to_sql(table_name, conn, if_exists='append', index=False)
        print("Update complete")
    return 'Success'



