from distutils.log import info
import datetime
import pandas as pd
import numpy as np
from Data_Class.SQL import  sql_datenLadenStammdaten,sql_datenLadenKunden,sql_datenLadenOderItems,sql_datenLadenLabel
from Data_Class.SQL import SQL_TabellenLadenBearbeiten as SQL



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
    heute  = datetime.date.today()
    day2 = heute - datetime.timedelta(days=90)
    dfOrder = SQL.sql_datenLadenDatum(day2,heute,SQL.tabelle_DepotDEBYKNOrders,SQL.datumSpalteLSüber)

    #dfOrder = sql_datenLadenDatum(day2,heute,'business_depotDEBYKN-DepotDEBYKNOrders')
    dfStammdaten = stammdatenBearbeiten()
    dfOrderItems = sql_datenLadenOderItems()
    dfKunden = sql_datenLadenKunden()
    dfLabel = sql_datenLadenLabel()

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
    df = pd.merge(df, dfKunden, left_on='PartnerNo', right_on='PartnerNo', how='left')
    # count in dfLabel sum of Status "printed" by SapOrderNumber
    dfLabel = dfLabel[dfLabel['Status'] == 'printed']
    dfLabel = dfLabel.groupby(['SapOrderNumber']).size().reset_index(name='LabelCount')
    df['PicksGesamt'] = df['Picks Gesamt']

    def f_Fertig(row):
        try:
            if row.AllSSCCLabelsPrinted == 1:
                return row.PicksGesamt
        except:
            return np.nan
    df['PicksFertig'] = df.apply(f_Fertig,axis=1)
    def f_Offen(row):
        try:
            if row.AllSSCCLabelsPrinted == 0:
                return row.PicksGesamt
        except:
            return np.nan
    df['PicksOffen'] = df.apply(f_Fertig,axis=1)

    #drop row frow df if isReturnDelivery = 1
    df = df[df['IsReturnDelivery'] == 0]
    


    #df = pd.merge(df, dfLabel, left_on='SapOrderNumber', right_on='SapOrderNumber', how='left')

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
    
