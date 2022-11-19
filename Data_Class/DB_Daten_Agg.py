from distutils.log import info
import datetime
import pandas as pd
from SQL import datenLadenStammdaten , datenLadenLabel


class DB_DatenAggregation:

    def stammdatenAgg():
        # gibt die fertigen Stammdaten aus
        # Stammdaten laden und Denummerator/Numerator berechnen 
        dfStammdaten = datenLadenStammdaten()
        
        dfStammdaten['MaterialNumber'] = dfStammdaten['MaterialNumber'].str.replace('0000000000', '')
        for each in dfStammdaten.index:
            if dfStammdaten.loc[each, 'UnitOfMeasure'] == 'CS':
                dfStammdaten.loc[each, 'CS'] = dfStammdaten.loc[each, 'NumeratorToBaseUnitOfMeasure'] / dfStammdaten.loc[each, 'DenominatorToBaseUnitOfMeasure']
            else:
                dfStammdaten.loc[each, 'CS'] = 0        
            if dfStammdaten.loc[each, 'UnitOfMeasure'] == 'OUT':
                dfStammdaten.loc[each, 'OUT'] = dfStammdaten.loc[each, 'NumeratorToBaseUnitOfMeasure'] / dfStammdaten.loc[each, 'DenominatorToBaseUnitOfMeasure']
            else:
                dfStammdaten.loc[each, 'OUT'] = 0
            if dfStammdaten.loc[each, 'UnitOfMeasure'] == 'D97':
                dfStammdaten.loc[each, 'PAL'] = dfStammdaten.loc[each, 'NumeratorToBaseUnitOfMeasure'] / dfStammdaten.loc[each, 'DenominatorToBaseUnitOfMeasure']
            else:
                dfStammdaten.loc[each, 'PAL'] = 0       
        return dfStammdaten
    def labelAgg():
        #TODO: Label aus DB laden übernehmen
        # gibt nur Label aus die von angelegten Mitarbeitern bearbeitet wurden
        dfUser = pd.read_feather('/Users/martinwolf/Python/Superdepot Reporting/data/user.feather')
        dfLabel = datenLadenLabel()
        
        
        # #dfLabel = pd.read_csv('data/Label.csv')
        # dfLabel.columns = ['A', 'B','C','D','E','F','G','H','I','J','K','L','M','N']
        
        #dfLabel['CreatedTimestamp'] = pd.to_datetime(dfLabel['CreatedTimestamp'])
        # dfLabel['DATUM'] = dfLabel['CreatedTimestamp'].dt.strftime('%m/%d/%y')
        # dfLabel['TIME'] = dfLabel['CreatedTimestamp'].dt.strftime('%H:%M:%S')
        # dfLabel['TIME'] = dfLabel['TIME'] + pd.Timedelta(hours=1)
        # dfLabel['TIME'] = dfLabel['CreatedTimestamp'].dt.strftime('%H:%M:%S')
        dfLabel = pd.merge(dfLabel, dfUser, left_on='CreatedBy', right_on='Name')
        return dfLabel
    
    def bestellungenAgg(dfStammdaten, dflabel):
        #gibt die fertigen Bestellungen aus
        #berechnet die Picks pro Bestellung
        #ordent die Bestellungen zu den Labeln zu
        
        df['SKU'] = df['SKU'].astype(str)
        df = pd.merge(df, dfStammdaten[dfStammdaten['A'] == 'CS'][['SKU','CS']],left_on='SKU', right_on='SKU',how='left')
        df = pd.merge(df, dfStammdaten[dfStammdaten['A'] == 'D97'][['SKU','PAL']],left_on='SKU', right_on='SKU',how='left')
        df = pd.merge(df, dfStammdaten[dfStammdaten['A'] == 'OUT'][['SKU','OUT']],left_on='SKU', right_on='SKU',how='left')
        #Berechne Picks
        df['Picks PAL'] = df.O / df.PAL
        df['Picks CS'] = df.O / df.CS
        df['Picks OUT'] = df.O/ df.OUT
        #Bereinige Berechnungen der Picks 
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
        # Picks Gesamt
        df['Picks Gesamt'] = df['Picks PAL'] + df['Picks CS'] + df['Picks OUT']
        df['Kalender Woche'] = df['B'].dt.strftime('%U')
        df['Monat'] = df['B'].dt.month
        return df
    #print(dfstammdat
dfLabel = DB_DatenAggregation.labelAgg()
print(dfLabel)
