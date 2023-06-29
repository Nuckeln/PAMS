import pandas as pd
from Data_Class import SQL as sql


#load db 

# df = sql.SQL_TabellenLadenBearbeiten.sql_datenTabelleLaden('Issues')
# #save as excel
# df.to_excel('Issues.xlsx', index=False)

df = pd.read_excel('/Users/martinwolf/Python/IPYNB/SQL_Test/test.xlsx')
print(df)
#sql.SQL_TabellenLadenBearbeiten.sql_deleteTabelle('Issues')
sql.SQL_TabellenLadenBearbeiten.sql_createTable('Issues', df)