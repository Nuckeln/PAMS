from sqlalchemy import create_engine
import pandas as pd
from sqlalchemy import types 
import datetime

class SQL:
    
    def read_table(table_name, columns=None, day1=None, day2=None, date_column=None):
        """
        Liest Daten aus einer SQL-Tabelle. Optional kann ein Datumsbereich angegeben werden, um die Daten zu filtern.

        :param table_name: Name der Tabelle, aus der die Daten gelesen werden sollen.
        :param columns: Liste der Spalten, die gelesen werden sollen. Wenn None, werden alle Spalten gelesen.
        :param day1: Startdatum für die Filterung der Daten. Wenn None, wird kein Datumsfilter angewendet.
        :param day2: Enddatum für die Filterung der Daten. Wenn None, wird kein Datumsfilter angewendet.
        :param date_column: Name der Spalte, die das Datum enthält. Muss angegeben werden, wenn day1 und day2 gesetzt sind.
        :return: DataFrame mit den gelesenen Daten.
        """
        server = "batsql-pp-ne-cmes-prod-10.database.windows.net"
        database = "batsdb-pp-ne-prod-reporting_SuperDepot"
        username = "batedp-cmes-prod-reportinguser"
        password = "b2.5v^H!IKjetuXMVNvW"

        # Datenbankverbindung erstellen
        engine = create_engine(f'mssql+pyodbc://{username}:{password}@{server}/{database}?driver=ODBC+Driver+17+for+SQL+Server')

        # Wenn keine Spalten angegeben sind, wähle alle Spalten aus
        if columns is None:
            columns = '*'
        else:
            columns = ', '.join(columns)

        # SQL-Abfrage erstellen
        sql_query = f'SELECT {columns} FROM [{table_name}]'
        if day1 and day2 and date_column:
            sql_query += f" WHERE {date_column} BETWEEN '{day1}' AND '{day2}'"

        # Daten auslesen
        df = pd.read_sql(sql_query, engine)

        # Verbindung schließen
        engine.dispose()
        return df

    def load_table_by_Col_Content(table_name: str, col_name: str, content: list[str]) -> pd.DataFrame:
        """
        Lädt Daten aus einer SQL-Tabelle basierend auf den Werten in einer bestimmten Spalte.

        :param table_name: Name der Tabelle, aus der die Daten gelesen werden sollen.
        :param col_name: Name der Spalte, die gefiltert werden soll.
        :param content: Liste der Werte, die in der Spalte enthalten sein sollen.
        :return: DataFrame mit den gelesenen Daten.
        """
        if not content:
            raise ValueError("Die Liste 'content' darf nicht leer sein.")
        
        server = "batsql-pp-ne-cmes-prod-10.database.windows.net"
        database = "batsdb-pp-ne-prod-reporting_SuperDepot"
        username = "batedp-cmes-prod-reportinguser"
        password = "b2.5v^H!IKjetuXMVNvW"
        
        # Datenbankverbindung erstellen
        engine = create_engine(f'mssql+pyodbc://{username}:{password}@{server}/{database}?driver=ODBC+Driver+17+for+SQL+Server')
        
        max_size = 50  # Maximale Anzahl von Werten pro Batch
        order_number_batches = [content[i:i+max_size] for i in range(0, len(content), max_size)]
        
        dfs = []
        for batch in order_number_batches:
            # SQL-Abfrage erstellen, um die Tabelle nach den Werten in der Spalte zu filtern
            sap_order_numbers = "', '".join(batch)
            query = f"SELECT * FROM [{table_name}] WHERE {col_name} IN ('{sap_order_numbers}')"
            df_batch = pd.read_sql(query, engine)
            if not df_batch.empty:
                dfs.append(df_batch)
        
        if not dfs:
            raise ValueError("Keine Daten gefunden, die den angegebenen Kriterien entsprechen.")
        
        # Alle DataFrames zusammenführen
        df = pd.concat(dfs, ignore_index=True)
        
        # Verbindung schließen
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
