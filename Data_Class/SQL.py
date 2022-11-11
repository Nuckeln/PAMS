import pyodbc 

server = 'tcp:myserver.database.windows.net' 
database = 'mydb'
username = 'myusername' 
password = 'mypassword'
driver = '{ODBC Driver 18 for SQL Server}'

try:
    cnxn = pyodbc.connect('DRIVER=' + driver + 
                      ';SERVER=' + server + 
                      ';DATABASE=' + database + 
                      ';UID=' + username + 
                      ';PWD=' + password)

    cursor = cnxn.cursor()
    print('Connection established')
except:
    print('Cannot connect to SQL server')