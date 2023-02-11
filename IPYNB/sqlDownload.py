import SQL as sql
import pandas as pd
import numpy as np
import parquet as pq

dfStammdaten = sql.SQL_TabellenLadenBearbeiten.sql_datenTabelleLaden('data_materialmaster-MaterialMasterUnitOfMeasures')
#safe to parquet
dfStammdaten.to_parquet('/Users/martinwolf/Python/Superdepot Reporting/Data/appData/data_materialmaster-MaterialMasterUnitOfMeasures.parquet')
print('done')