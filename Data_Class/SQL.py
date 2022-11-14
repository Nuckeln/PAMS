# import mysql.connector

# mydb = mysql.connector.connect(
#   host="batsql-pd-ne-cmes-dev-10.database.windows.net",
#   user="batedp-cmes-dev-reportinguser",
#   password="b2.5v^H!IKjetuXMVNvW",
#   #database="batsdb-pd-ne-dev-reporting_SuperDepot"
# )

# mycursor = mydb.cursor()

# print(mydb)


# Modul für die Kommunikation mit einer MySQL Datenbank
import mysql.connector
#Aufbau einer Verbindung
db = mysql.connector.connect(
  host="batsql-pd-ne-cmes-dev-10.database.windows.net", # Servername
  user="batedp-cmes-dev-reportinguser", # Benutzername
  password="b2.5v^H!IKjetuXMVNvW" # Passwort
)
# Ausgabe des Hashwertes des initialisierten Objektes
print(db)