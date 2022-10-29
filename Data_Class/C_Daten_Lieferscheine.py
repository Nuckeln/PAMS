from distutils.log import info
import datetime
import pandas as pd


class DatenAuswerten:
#     pass

    def go():
        df = pd.read_excel('/Users/martinwolf/Desktop/SuperDepot Python/Data/vl06o items.XLSX') 
        df.columns = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R']
        dfStammdaten = pd.read_excel('/Users/martinwolf/Desktop/SuperDepot Python/Data/Stammdaten.xlsx', 0, header=0)
        dfStammdaten.columns = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q']

        dfStammdaten['B'] = dfStammdaten['B'].str.replace('0000000000', '')
        for each in dfStammdaten.index:
            if dfStammdaten.loc[each, 'A'] == 'CS':
                dfStammdaten.loc[each, 'CS'] = dfStammdaten.loc[each, 'C'] / dfStammdaten.loc[each, 'D']
            else:
                dfStammdaten.loc[each, 'CS'] = 0
        for each in dfStammdaten.index:
            if dfStammdaten.loc[each, 'A'] == 'OUT':
                dfStammdaten.loc[each, 'OUT'] = dfStammdaten.loc[each, 'C'] / dfStammdaten.loc[each, 'D']
            else:
                dfStammdaten.loc[each, 'OUT'] = 0
        for each in dfStammdaten.index:
            if dfStammdaten.loc[each, 'A'] == 'D97':
                dfStammdaten.loc[each, 'PAL'] = dfStammdaten.loc[each, 'C'] / dfStammdaten.loc[each, 'D']
            else:
                dfStammdaten.loc[each, 'PAL'] = 0
            



       

        print('Bewegungsdaten wurden erstellt')

    go()