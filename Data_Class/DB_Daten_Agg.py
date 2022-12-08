from distutils.log import info
import datetime
import pandas as pd
import numpy as np
from Data_Class.SQL import  sql_datenLadenStammdaten,sql_datenLadenKunden,sql_datenLadenOderItems,sql_datenLadenLabel, sql_datenLadenMaster_CS_OUT,datenSpeichern_CS_OUT_STammdaten
from Data_Class.SQL import SQL_TabellenLadenBearbeiten as SQL

def orderDatenAgg():
    dfStammdaten = sql_datenLadenMaster_CS_OUT()

    dfStammdaten = dfStammdaten[dfStammdaten['UnitOfMeasure'].isin(['CS','D97','OUT'])]
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
    #dfStammdaten.to_sql('CS_OUT_PAL_MaterialMasterUnitOfMeasures', SQL.db_conn.conn, if_exists='replace', index=False)


    heute  = datetime.date.today()
    # heute plus 3 Tage
    morgen =heute + datetime.timedelta(days=3)
    day2 = heute - datetime.timedelta(days=10)
    dfOrder = SQL.sql_datenLadenDatum(day2,morgen,SQL.tabelle_DepotDEBYKNOrders,SQL.datumSpalteLSüber)
    #dfOrder = sql_datenLadenOder()
    #dfOrder = sql_datenLadenDatum(day2,heute,'business_depotDEBYKN-DepotDEBYKNOrders')

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
    #dfKunden PartnerNo to string
    dfKunden['PartnerNo'] = dfKunden['PartnerNo'].astype(str)
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
    df['PicksOffen'] = df.apply(f_Offen,axis=1)

    #drop row frow df if isReturnDelivery = 1
    # convert  IDocNumberDESADV to string
    df['IDocNumberDESADV'] = df['IDocNumberDESADV'].astype(str)

    df = df[df['IsReturnDelivery'] == 0]
    df = df.fillna(0)
    #df[QuantityCheckTimestamp to string
    df['QuantityCheckTimestamp'] = df['QuantityCheckTimestamp'].astype(str)
    df['Source'] = df['Source'].astype(str)
    df['UnloadingListIdentifier'] = df['UnloadingListIdentifier'].astype(str)


    return df