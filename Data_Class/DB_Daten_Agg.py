from distutils.log import info
import datetime
import pandas as pd
import numpy as np
from Data_Class.SQL import sql_datenLadenLabel,sql_datenLadenOderItems,sql_datenLadenStammdaten,sql_datenLadenOder,createnewTable




def stammdatenBearbeiten():
    dfStammdaten = sql_datenLadenStammdaten()
    dfStammdaten['MaterialNumber'] = dfStammdaten['MaterialNumber'].str.replace('0000000000', '')
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
    dfOrderItems['PicksPAL'] = dfOrderItems.O / dfOrderItems.PAL
    dfOrderItems['PicksCS'] = dfOrderItems.CorrespondingCartons 
    dfOrderItems['Picks OUT'] = dfOrderItems.CorrespondingOuters
    #Bereinige Berechnungen der Picks 
    dfOrderItems['PicksPAL'] = dfOrderItems['PicksPAL'].fillna(0) 
    dfOrderItems['O'] = dfOrderItems.O.fillna(0) 
    dfOrderItems['Picks OUT'] = dfOrderItems['Picks OUT'].fillna(0) 

    # Pal kleiner als 1 bereinigen
    def f_PAL(row):
            if row.PicksPAL < 1:
                return 0
            else:
                return row.PicksPAL

    dfOrderItems['Picks PAL'] = dfOrderItems.apply(f_PAL,axis=1)

    def f_OUT(row):
            if row.PicksPAL >= 1:
                return row.CorrespondingCartons  - ((row.PicksPAL * row.PAL) / row.CS)
            else:
                return row.CorrespondingCartons

    dfOrderItems['Picks CS'] = dfOrderItems.apply(f_OUT,axis=1)

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
    
