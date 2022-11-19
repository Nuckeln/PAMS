from distutils.log import info
import datetime
import pandas as pd
from SQL import datenLadenStammdaten

##TODO: SAFE BACKUP LT22 BEFORE ANYTHING
class SapDatenAggregation:

    def lt22(self):
        print('Start')

        dfStammdaten = datenLadenStammdaten()
        dfUser = pd.read_excel('Data/user.xlsx', 0, header=0, index_col=0)
        # Weil ich nunmal ein Excel Idiot bin
        dflt22 = pd.read_feather('Data/LT22.feather')

        dflt22.columns = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z','AA','AB','AC']
        dflt22['Ziel'] = dflt22['U'].str[:2]
        dflt22['Quelle'] = dflt22['E'].str[:2]
        dflt22['Pick Datum'] = dflt22['L'].dt.strftime('%m/%d/%y')
        dflt22['K'] = dflt22['K'].astype(str)
        dflt22['K'] = pd.to_datetime(dflt22['K'], format='%H:%M:%S')
        dflt22['Pick Zeit'] = dflt22['K']
            
        dflt22['L'] = pd.to_datetime(dflt22['L'])
        dflt22['Pick Datum'] = dflt22['L'].dt.strftime('%m/%d/%y')

        print('Daten geladen')
        
        dfStammdaten.columns = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q']
        #dfLabel.columns = ['A', 'B','C','D','E','F','G','H','I','J','K','L','M','N']

        dfStammdaten['B'] = dfStammdaten['B'].str.replace('0000000000', '')
        #dfLabel['B'] = pd.to_datetime(dfLabel['B'])
        #dfLabel['DATUM'] = dfLabel['B'].dt.strftime('%m/%d/%y')
        #dfLabel['TIME'] = dfLabel['B'].dt.strftime('%H:%M:%S')
        # dfLabel['Time'] plus 1 hour
        #dfLabel['TIME'] = dfLabel['TIME'] + pd.Timedelta(hours=1)
        #dfLabel['TIME'] = dfLabel['B'].dt.strftime('%H:%M:%S')

        #dfLabel = pd.merge(dfLabel, dfUser, left_on='C', right_on='Name')

        #def StammdatenErweitern(dfStammdaten):
        #Stamdaten erweitern 
        # print('Stammdaten erweitern')
        # for each in dfStammdaten.index:
        #     if dfStammdaten.loc[each, 'A'] == 'CS':
        #         dfStammdaten.loc[each, 'CS'] = dfStammdaten.loc[each, 'C'] / dfStammdaten.loc[each, 'D']
        #     else:
        #         dfStammdaten.loc[each, 'CS'] = 0        
        #     if dfStammdaten.loc[each, 'A'] == 'OUT':
        #         dfStammdaten.loc[each, 'OUT'] = dfStammdaten.loc[each, 'C'] / dfStammdaten.loc[each, 'D']
        #     else:
        #         dfStammdaten.loc[each, 'OUT'] = 0
        #     if dfStammdaten.loc[each, 'A'] == 'D97':
        #         dfStammdaten.loc[each, 'PAL'] = dfStammdaten.loc[each, 'C'] / dfStammdaten.loc[each, 'D']
        #     else:
        #         dfStammdaten.loc[each, 'PAL'] = 0

    #####------------------LT22-Bearbeiten-----------------#####
        print('stammdaten merge')
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
        print('pickschleife')
        #Schleife erst Picks Berechnen -> Dann Umlagerungen ermitteln
        for each in dflt22.index:
            if dflt22.loc[each, 'E'] == 'TN1' and dflt22.loc[each, 'U'] == '916':
                dflt22.loc[each, 'PICKS'] = dflt22.loc[each, 'H'] 
                dflt22.loc[each, 'Picks OUT'] = dflt22.loc[each, 'H'] 
                dflt22.loc[each, 'Pick Art'] = 'Stange'
            if dflt22.loc[each, 'E'] == 'SN1' and dflt22.loc[each, 'U'] == '916' or dflt22.loc[each, 'E'] == 'SN2' and dflt22.loc[each, 'U'] == '916' or dflt22.loc[each, 'E'] == 'SN3' and dflt22.loc[each, 'U'] == '916' or dflt22.loc[each, 'E'] == 'SN4' and dflt22.loc[each, 'U'] == '916':
                dflt22.loc[each, 'PICKS'] = (dflt22.loc[each, 'H'] * dflt22.loc[each, 'OUT']) / dflt22.loc[each, 'CS']
                dflt22.loc[each, 'Picks CS'] = (dflt22.loc[each, 'H'] * dflt22.loc[each, 'OUT']) / dflt22.loc[each, 'CS']
                dflt22.loc[each, 'Pick Art'] = 'Karton'
            if dflt22.loc[each, 'E'] == 'BS3' and dflt22.loc[each, 'U'] == '916':
                dflt22.loc[each, 'PICKS'] = (dflt22.loc[each, 'H'] * dflt22.loc[each, 'OUT']) / dflt22.loc[each, 'PAL']
                dflt22.loc[each, 'PICKS PAL'] = (dflt22.loc[each, 'H'] * dflt22.loc[each, 'OUT']) / dflt22.loc[each, 'PAL']
                dflt22.loc[each, 'Pick Art'] = 'Palette'
            #Umlagerungen Ermitteln 
            if dflt22.loc[each, 'E'] == 'BS3' and dflt22.loc[each, 'Ziel'] == 'SN':
                dflt22.loc[each, 'Umlagerung'] = 1
                dflt22.loc[each, 'Art'] = 'Karton'
            if dflt22.loc[each, 'Quelle'] == 'RS' and dflt22.loc[each, 'Ziel'] == 'SN':
                dflt22.loc[each, 'Umlagerung'] = 1
                dflt22.loc[each, 'Art'] = 'Karton'
            if dflt22.loc[each, 'Quelle'] == 'SN' and dflt22.loc[each, 'Ziel'] == 'TN':
                dflt22.loc[each, 'Umlagerung'] = 1
                dflt22.loc[each, 'Art'] = 'Gebinde'

        #Mitarbeiter Hinzufügen
        adduser = pd.merge(dflt22, dfUser, left_on='O', right_on='One ID')
        dflt22.set_index('A', inplace=True)
        adduser.set_index('A', inplace=True)
        dflt22 = pd.concat([dflt22[~dflt22.index.isin(adduser.index)], adduser],)
        dflt22.reset_index(inplace=True)

        print('ausgabe Excel')
        # --- Ausgabe in Excel
        dflt22.to_feather('Data/Bewegungsdaten.feather')
        print('ausgabe Excel fertig')
    
    