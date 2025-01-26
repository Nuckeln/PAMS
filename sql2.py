def read_table_combined(table_name, columns=None, day1=None, day2=None, date_column=None):
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