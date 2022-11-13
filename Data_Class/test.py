import pandas as pd

dfUser = pd.read_excel('Data/user.xlsx', 0, header=0)


dfUser.to_feather('Data/user.feather')
