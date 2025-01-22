from sqlalchemy import create_engine
import pandas as pd
from sqlalchemy import types 
import datetime

class SQL:
    def read_Table(table_name):
        server = "batsql-pp-ne-cmes-prod-10.database.windows.net"
        database = "batsdb-pp-ne-prod-reporting_SuperDepot"
        username = "batedp-cmes-prod-reportinguser"
        password = "b2.5v^H!IKjetuXMVNvW"

        # Datenbankverbindung erstellen
        engine = create_engine(f'mssql+pyodbc://{username}:{password}@{server}/{database}?driver=ODBC+Driver+17+for+SQL+Server')
        # Daten auslesen
        df = pd.read_sql(f'SELECT * FROM {table_name}', engine)
        # Connection schließen
        engine.dispose()
        return df

    def update_Table(table_name: str, datenframe: pd.DataFrame, id_column: str):
        '''Updatet eine Tabelle in der Datenbank nur neue oder veränderte Zeilen'''
        server = "batsql-pp-ne-cmes-prod-10.database.windows.net"
        database = "batsdb-pp-ne-prod-reporting_SuperDepot"
        username = "batedp-cmes-prod-reportinguser"
        password = "b2.5v^H!IKjetuXMVNvW"
        
        # Datenbankverbindung erstellen
        engine = create_engine(f'mssql+pyodbc://{username}:{password}@{server}/{database}?driver=ODBC+Driver+17+for+SQL+Server')
        
        # Aktuelle Tabelle aus der Datenbank lesen
        existing_df = pd.read_sql(f'SELECT * FROM {table_name}', engine)

        # Ermitteln, welche neuen oder geänderten Daten hinzugefügt werden müssen
        # Hier wird angenommen, dass die Tabelle eine Primärschlüsselspalte 'id' enthält
        if id_column not in datenframe.columns:
            raise ValueError("Die Spalte 'id' ist erforderlich, um Unterschiede zu erkennen.")
        
        # Verbinde die Datenrahmen, um Änderungen zu identifizieren
        merged_df = datenframe.merge(existing_df, on=id_column, how='left', indicator=True)
        to_update_or_insert = merged_df[merged_df['_merge'] != 'both']

        # Trenne neue und aktualisierte Zeilen
        new_rows = to_update_or_insert[to_update_or_insert['_merge'] == 'left_only']
        updated_rows = to_update_or_insert[to_update_or_insert['_merge'] == 'right_only']

        # Füge neue Zeilen ein
        if not new_rows.empty:
            new_rows = new_rows.drop(columns=['_merge'])  # Entferne die Hilfsspalte
            new_rows.to_sql(table_name, engine, if_exists='append', index=False)
        
        # Aktualisiere bestehende Zeilen
        if not updated_rows.empty:
            with engine.connect() as conn:
                for _, row in updated_rows.iterrows():
                    update_query = f"""
                    UPDATE {table_name}
                    SET {', '.join([f"{col} = '{row[col]}'" for col in row.index if col != id_column])}
                    WHERE id = '{row[id_column]}'
                    """
                    conn.execute(update_query)
        
        # Verbindung schließen
        engine.dispose()
        
    def save_Table(table_name: str, datenframe: pd.DataFrame):
        '''Speichert den gesamten DataFrame in eine Tabelle und überschreibt vorhandene Daten.'''
        server = "batsql-pp-ne-cmes-prod-10.database.windows.net"
        database = "batsdb-pp-ne-prod-reporting_SuperDepot"
        username = "batedp-cmes-prod-reportinguser"
        password = "b2.5v^H!IKjetuXMVNvW"
        
        # Datenbankverbindung erstellen
        engine = create_engine(f'mssql+pyodbc://{username}:{password}@{server}/{database}?driver=ODBC+Driver+17+for+SQL+Server')
        
        # Speichern der Daten in der Tabelle
        datenframe.to_sql(table_name, engine, if_exists='replace', index=False)
        
        # Verbindung schließen
        engine.dispose()
        print(f"Tabelle {table_name} erfolgreich gespeichert.")
