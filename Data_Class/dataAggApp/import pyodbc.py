import pyodbc
import pandas as pd

# Connection string for MS SQL Server
conn = pyodbc.connect(
    'DRIVER={ODBC Driver 18 for SQL Server};'
    'SERVER=batsql-pp-ne-cmes-prod-10.database.windows.net;'
    'DATABASE=batsdb-pp-ne-prod-reporting_SuperDepot;'
    'UID=batedp-cmes-prod-reportinguser;'
    'PWD=b2.5v^H!IKjetuXMVNvW'
)

# Read sample data
df = pd.read_parquet('Data/appData/df.parquet.gzip')

# Write data to MS SQL Server
#df.to_sql('MeineTabelle', conn, if_exists='replace', index=False, chunksize=1000)
# Insert data into database
cursor = conn.cursor()
for index, row in df.iterrows():
    cursor.execute("INSERT INTO <table_name> VALUES (?, ?, ...)", row['col1'], row['col2'], ...)
conn.commit()

# Close database connection
conn.close()

# Close the connection
conn.close()
