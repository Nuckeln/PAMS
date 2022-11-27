from distutils.log import info
import datetime
import pandas as pd
import numpy as np
from data_Class.SQL import sql_datenLadenLabel,sql_datenLadenOderItems,sql_datenLadenStammdaten,sql_datenLadenOder,createnewTable




def stammdatenBearbeiten():
    dfStammdaten = sql_datenLadenStammdaten()
    dfStammdaten = dfStammdaten[dfStammdaten['UnitOfMeasure'].isin(['CS','D97','OUT'])]   
    def f_CS(row):
        try:
            if row.UnitOfMeasure == 'CS':          
                return row.NumeratorToBaseUnitOfMeasure / row.DenominatorToBaseUnitOfMeasure
        except:
            return np.nan
    def f_PAL(row):
        try:
            if row.UnitOfMeasure == 'D97':
                return row.NumeratorToBaseUnitOfMeasure / row.DenominatorToBaseUnitOfMeasure
        except:
            return np.nan
    def f_OUT(row):
        try:
            if row.UnitOfMeasure == 'OUT':
                return row.NumeratorToBaseUnitOfMeasure / row.DenominatorToBaseUnitOfMeasure
        except:
            return np.nan
    dfStammdaten['OUT'] = dfStammdaten.apply(f_OUT,axis=1)
    dfStammdaten['CS'] = dfStammdaten.apply(f_CS,axis=1)
    dfStammdaten['PAL'] = dfStammdaten.apply(f_PAL,axis=1)

    return dfStammdaten

def orderDatenAgg():
    dfStammdaten = stammdatenBearbeiten()
    dfOrder = sql_datenLadenOder()
    dfOrderItems = sql_datenLadenOderItems()

    dfOrderItems['MaterialNumber'] = dfOrderItems['MaterialNumber'].astype(str)
    dfOrderItems['MaterialNumber'] = dfOrderItems['MaterialNumber'].str.replace('0000000000', '')
    dfOrderItems = pd.merge(dfOrderItems, dfStammdaten[dfStammdaten['UnitOfMeasure'] == 'CS'][['MaterialNumber','CS']],left_on='MaterialNumber', right_on='MaterialNumber',how='left')
    dfOrderItems = pd.merge(dfOrderItems, dfStammdaten[dfStammdaten['UnitOfMeasure'] == 'D97'][['MaterialNumber','PAL']],left_on='MaterialNumber', right_on='MaterialNumber',how='left')
    dfOrderItems = pd.merge(dfOrderItems, dfStammdaten[dfStammdaten['UnitOfMeasure'] == 'OUT'][['MaterialNumber','OUT']],left_on='MaterialNumber', right_on='MaterialNumber',how='left')

    dfOrderItems['O'] = dfOrderItems['Outers'] * dfOrderItems['OUT']
    dfOrderItems['Picks PAL'] = dfOrderItems.O / dfOrderItems.PAL
    dfOrderItems['Picks CS'] = dfOrderItems.O / dfOrderItems.CS
    dfOrderItems['Picks OUT'] = dfOrderItems.O/ dfOrderItems.OUT
    #Bereinige Berechnungen der Picks 
    for i in range(0,len(dfOrderItems.index)):
        #----PAL bereinigen
            if (dfOrderItems.loc[i,'Picks PAL'] <1):
                dfOrderItems.loc[i,'Picks PAL'] = 0
        #----cs bereinigen
            if (dfOrderItems.loc[i,'Picks CS'] <1):
                dfOrderItems.loc[i,'Picks CS'] = 0 
        #mögliche PAL picks abziehen
            if (dfOrderItems.loc[i,'Picks PAL'] >=1):
                dfOrderItems.loc[i,'Picks CS'] = (dfOrderItems.loc[i,'O'] - (dfOrderItems.loc[i,'Picks PAL'] * dfOrderItems.loc[i,'PAL'])) * dfOrderItems.loc[i,'CS']
        #---OUT bereinigen
            if (dfOrderItems.loc[i,'Picks OUT'] <1):
                dfOrderItems.loc[i,'Picks OUT'] = 0
        #mögliche PAL picks abziehen
            if (dfOrderItems.loc[i,'Picks PAL'] >=1):
                dfOrderItems.loc[i,'Picks OUT'] = (dfOrderItems.loc[i,'O'] - (dfOrderItems.loc[i,'Picks PAL'] * dfOrderItems.loc[i,'PAL'])) * dfOrderItems.loc[i,'OUT']
        #mögliche CS picks abziehen
            if (dfOrderItems.loc[i,'Picks CS'] >=1):
                dfOrderItems.loc[i,'Picks OUT'] = 0#(dfOrderItems.loc[i,'O'] - (dfOrderItems.loc[i,'Picks CS'] * dfOrderItems.loc[i,'CS'])) * dfOrderItems.loc[i,'OUT']
    # Picks Gesamt
    dfOrderItems['Picks Gesamt'] = dfOrderItems['Picks PAL'] + dfOrderItems['Picks CS'] + dfOrderItems['Picks OUT']
    df = pd.merge(dfOrder, dfOrderItems, left_on='SapOrderNumber', right_on='SapOrderNumber', how='left')

    return df





# class DB_DatenAggregation:


#     def labelAgg():
#         #TODO: Label aus DB laden übernehmen
#         # gibt nur Label aus die von angelegten Mitarbeitern bearbeitet wurden
#         dfUser = pd.read_feather('/Users/martinwolf/Python/Superdepot Reporting/data/user.feather')
#         dfLabel = datenLadenLabel()
        
        
#         # #dfLabel = pd.read_csv('data/Label.csv')
#         # dfLabel.columns = ['A', 'B','C','D','E','F','G','H','I','J','K','L','M','N']
        
#         #dfLabel['CreatedTimestamp'] = pd.to_datetime(dfLabel['CreatedTimestamp'])
#         # dfLabel['DATUM'] = dfLabel['CreatedTimestamp'].dt.strftime('%m/%d/%y')
#         # dfLabel['TIME'] = dfLabel['CreatedTimestamp'].dt.strftime('%H:%M:%S')
#         # dfLabel['TIME'] = dfLabel['TIME'] + pd.Timedelta(hours=1)
#         # dfLabel['TIME'] = dfLabel['CreatedTimestamp'].dt.strftime('%H:%M:%S')
#         dfLabel = pd.merge(dfLabel, dfUser, left_on='CreatedBy', right_on='Name')
#         return dfLabel
    
