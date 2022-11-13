import pandas as pd

class Reperatur:
    def go(self):
        dfUser = pd.read_excel('Data/user.xlsx', 0, header=0)
        dflt22 = pd.read_excel('Data/lt22.XLSX', 0, header=0)
        dflt22.to_feather('Data/LT22.feather')
        dfUser.to_feather('Data/user.feather')
