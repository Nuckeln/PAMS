from distutils.log import info
import datetime
import pandas as pd


class DatenAuswerten:
#     pass

    def go():

        dflt22 = pd.read_excel('Data/lt22.XLSX', 0, header=0)
        dfStammdaten = pd.read_excel('Data/Stammdaten.xlsx', 0, header=0)
        dfLabel = pd.read_csv('Data/Label.csv', sep=",")
        dfUser = pd.read_excel('Data/user.xlsx', 0, header=0, index_col=0)
        # Weil ich nunmal ein Excel Idiot bin
        dflt22.columns = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z','AA','AB','AC']
        dfStammdaten.columns = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q']
        dfLabel.columns = ['A', 'B','C','D','E','F','G','H','I','J','K','L','M','N']

        dfStammdaten['B'] = dfStammdaten['B'].str.replace('0000000000', '')
        dfLabel['B'] = pd.to_datetime(dfLabel['B'])
        dfLabel['DATUM'] = dfLabel['B'].dt.strftime('%m/%d/%y')
        dfLabel['TIME'] = dfLabel['B'].dt.strftime('%H:%M:%S')
        # dfLabel['Time'] plus 1 hour
        dfLabel['TIME'] = dfLabel['TIME'] + pd.Timedelta(hours=1)
        dfLabel['TIME'] = dfLabel['B'].dt.strftime('%H:%M:%S')

        dfLabel = pd.merge(dfLabel, dfUser, left_on='C', right_on='Name')

        #def StammdatenErweitern(dfStammdaten):
        #Stamdaten erweitern 
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



        # LT22 Stammdaten übergeben 
        dflt22['B'] = dflt22['B'].astype(str)
        df = dfStammdaten[dfStammdaten['A'] == 'CS']
        df2 = pd.merge(dflt22, df[['B','CS']], left_on='B', right_on='B')
        dflt22 = df2
        df = dfStammdaten[dfStammdaten['A'] == 'OUT']
        df2 = pd.merge(dflt22, df[['B','OUT']], left_on='B', right_on='B')
        dflt22 = df2
        df = dfStammdaten[dfStammdaten['A'] == 'D97']
        df2 = pd.merge(dflt22, df[['B','PAL']], left_on='B', right_on='B')
        dflt22 = df2

            #Picks Berechnen
        for each in dflt22.index:
            if dflt22.loc[each, 'E'] == 'TN1' and dflt22.loc[each, 'U'] == '916':
                dflt22.loc[each, 'PICKS'] = dflt22.loc[each, 'H'] 
                dflt22.loc[each, 'Picks OUT'] = dflt22.loc[each, 'H'] 
        for each in dflt22.index:
            if dflt22.loc[each, 'E'] == 'SN1' and dflt22.loc[each, 'U'] == '916' or dflt22.loc[each, 'E'] == 'SN2' and dflt22.loc[each, 'U'] == '916' or dflt22.loc[each, 'E'] == 'SN3' and dflt22.loc[each, 'U'] == '916' or dflt22.loc[each, 'E'] == 'SN4' and dflt22.loc[each, 'U'] == '916':
                dflt22.loc[each, 'PICKS'] = (dflt22.loc[each, 'H'] * dflt22.loc[each, 'OUT']) / dflt22.loc[each, 'CS']
                dflt22.loc[each, 'Picks CS'] = (dflt22.loc[each, 'H'] * dflt22.loc[each, 'OUT']) / dflt22.loc[each, 'CS']
        for each in dflt22.index:
            if dflt22.loc[each, 'E'] == 'BS3' and dflt22.loc[each, 'U'] == '916':
                dflt22.loc[each, 'PICKS'] = (dflt22.loc[each, 'H'] * dflt22.loc[each, 'OUT']) / dflt22.loc[each, 'PAL']
                dflt22.loc[each, 'PICKS PAL'] = (dflt22.loc[each, 'H'] * dflt22.loc[each, 'OUT']) / dflt22.loc[each, 'PAL']

        dflt22['Pick Datum'] = dflt22['L'].dt.strftime('%m/%d/%y')
        dflt22['Pick Zeit'] = dflt22['K']  

        #-------Label mit anhängen ----------------
        for each in dfLabel.index:
            a= {"L": dfLabel.loc[each, 'DATUM'],"K": dfLabel.loc[each, 'TIME'], "O": dfLabel.loc[each, 'One ID'], "Label": dfLabel.loc[each, 'I']}
            dflt22 = dflt22.append(a, ignore_index=True)

        dflt22['L'] = pd.to_datetime(dflt22['L'])
        dflt22['Pick Datum'] = dflt22['L'].dt.strftime('%m/%d/%y')
        dflt22['Pick Zeit'] = dflt22['K']  
        dflt22 = pd.merge(dflt22, dfUser, left_on='O', right_on='One ID')

        # --- Ausgabe in Excel
        dflt22.to_excel('/Users/martinwolf/Desktop/SuperDepot Python/Data/Bewegungsdaten.xlsx', index=False)

    go()