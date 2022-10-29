from distutils.log import info
import datetime
import pandas as pd


class LsAuswerten:
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
    
        df = df.rename(columns={'M':'SKU'})
        dfStammdaten = dfStammdaten.rename(columns={'B':'SKU'})
#df.set_index('SKU')
# change df.sku to string
        df['SKU'] = df['SKU'].astype(str)
        df = pd.merge(df, dfStammdaten[dfStammdaten['A'] == 'CS'][['SKU','CS']],left_on='SKU', right_on='SKU',how='left')
        df = pd.merge(df, dfStammdaten[dfStammdaten['A'] == 'D97'][['SKU','PAL']],left_on='SKU', right_on='SKU',how='left')
        df = pd.merge(df, dfStammdaten[dfStammdaten['A'] == 'OUT'][['SKU','OUT']],left_on='SKU', right_on='SKU',how='left')

        df['Picks PAL'] = df.O / df.PAL
        df['Picks CS'] = df.O / df.CS
        df['Picks OUT'] = df.O/ df.OUT

        for i in range(0,len(df.index)):
            #----PAL bereinigen
                if (df.loc[i,'Picks PAL'] <1):
                    df.loc[i,'Picks PAL'] = 0
            #----cs bereinigen
                if (df.loc[i,'Picks CS'] <1):
                    df.loc[i,'Picks CS'] = 0 
            #mögliche PAL picks abziehen
                if (df.loc[i,'Picks PAL'] >=1):
                    df.loc[i,'Picks CS'] = (df.loc[i,'O'] - (df.loc[i,'Picks PAL'] * df.loc[i,'PAL'])) * df.loc[i,'CS']
            #---OUT bereinigen
                if (df.loc[i,'Picks OUT'] <1):
                    df.loc[i,'Picks OUT'] = 0
            #mögliche PAL picks abziehen
                if (df.loc[i,'Picks PAL'] >=1):
                    df.loc[i,'Picks OUT'] = (df.loc[i,'O'] - (df.loc[i,'Picks PAL'] * df.loc[i,'PAL'])) * df.loc[i,'OUT']
            #mögliche CS picks abziehen
                if (df.loc[i,'Picks CS'] >=1):
                    df.loc[i,'Picks OUT'] = 0#(df.loc[i,'O'] - (df.loc[i,'Picks CS'] * df.loc[i,'CS'])) * df.loc[i,'OUT']
        print('Bewegungsdaten wurden erstellt')
        return df

    df = go()
    print(df)