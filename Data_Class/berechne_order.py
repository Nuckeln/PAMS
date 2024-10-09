
import streamlit as st
import numpy as np

import pandas as pd
import hydralit_components as hc
from Data_Class.MMSQL_connection import read_Table,save_Table_append

def berechne_order_daten():
    
    #     dfOrder = read_Table_by_Date(start_date,end_date,'business_depotDEBYKN-DepotDEBYKNOrders','PlannedDate')
    dfOrder = read_Table('business_depotDEBYKN-DepotDEBYKNOrders')
    dfOrder['Gepackte Paletten'] = dfOrder.ActualNumberOfPallets
    dfOrder['Fertige Paletten'] = dfOrder.ActualNumberOfPallets
    dfOrder['Geschätzte Paletten'] = dfOrder.EstimatedNumberOfPallets
    
    dfKunden = read_Table('Kunden_mit_Packinfos')
    dfKunden.PartnerNo = dfKunden.PartnerNo.astype(str)
    dfOrder = pd.merge(dfOrder, dfKunden[['PartnerNo', 'PartnerName']], on='PartnerNo', how='left')
    dfOrder = dfOrder.rename(columns={'CorrespondingPallets': 'Picks Paletten', 'CorrespondingMastercases': 'Picks Karton', 'CorrespondingOuters': 'Picks Stangen', 'KVP': 'KVP'})
    dfOrder['Picks Gesamt'] = dfOrder['Picks Paletten'] + dfOrder['Picks Karton'] + dfOrder['Picks Stangen']   
    dfOrder['Lieferschein erhalten'] = dfOrder['CreatedTimestamp']





    def f_Fertig(row):
        try:
            if row.AllSSCCLabelsPrinted == 1:
                return row.PicksGesamt
        except:
            return np.nan
        
    dfOrder['PicksFertig'] = dfOrder.apply(f_Fertig,axis=1)

    def f_Offen(row):
        try:
            if row.AllSSCCLabelsPrinted == 0:
                return row.PicksGesamt
        except:
            return np.nan
        
    dfOrder['PicksOffen'] = dfOrder.apply(f_Offen,axis=1)
        
    # dfOrderOpen = dfOrder[dfOrder['AllSSCCLabelsPrinted'] == 0]
    # dfOrderOpen['Picks Karton offen'] = dfOrderOpen['Picks Karton'].fillna(0)
    # dfOrderOpen['Picks Paletten offen'] = dfOrderOpen['Picks Paletten'].fillna(0)
    # dfOrderOpen['Picks Stangen offen'] = dfOrderOpen['Picks Stangen'].fillna(0)

    # dfOrderDone = dfOrder[dfOrder['AllSSCCLabelsPrinted'] == 1]
    # dfOrderDone['Picks Karton fertig'] = dfOrderDone['Picks Karton'].fillna(0)
    # dfOrderDone['Picks Paletten fertig'] = dfOrderDone['Picks Paletten'].fillna(0)
    # dfOrderDone['Picks Stangen fertig'] = dfOrderDone['Picks Stangen'].fillna(0)



    # dfOrder = pd.concat([dfOrderOpen, dfOrderDone])
    # dfOrder = dfOrder[dfOrder['IsReturnDelivery'] == 0]

    # dfOrder.loc[dfOrder['AllSSCCLabelsPrinted'] == 1, 'Fertiggestellt'] = dfOrder.loc[dfOrder['AllSSCCLabelsPrinted'] == 1, 'QuantityCheckTimestamp']

    # #all Datetime to String
    # dfOrder['CreatedTimestamp'] = dfOrder['CreatedTimestamp'].astype(str)
    # dfOrder['PlannedDate'] = dfOrder['PlannedDate'].astype(str)
    # dfOrder['QuantityCheckTimestamp'] = dfOrder['QuantityCheckTimestamp'].astype(str)
    # dfOrder['Fertiggestellt'] = dfOrder['Fertiggestellt'].astype(str)
    # dfOrder['Lieferschein erhalten'] = dfOrder['Lieferschein erhalten'].astype(str)
    # dfOrder['NiceLabelTransmissionState_TimeStamp'] = dfOrder['NiceLabelTransmissionState_TimeStamp'].astype(str)
    # #UpdatedTimestamp
    # dfOrder['UpdatedTimestamp'] = dfOrder['UpdatedTimestamp'].astype(str)
    
    # dfOrderLabels = read_Table('business_depotDEBYKN-LabelPrintOrders')
    # #Suche nach SapOrderNumber in dfOrderLabels und finde dann den kleinsten wert in CreatedTimestamp
    # dfOrder['Fertiggestellt'] = dfOrder['SapOrderNumber'].apply(lambda x: dfOrderLabels[dfOrderLabels['SapOrderNumber'] == x]['CreatedTimestamp'].max() if len(dfOrderLabels[dfOrderLabels['SapOrderNumber'] == x]['CreatedTimestamp']) > 0 else np.nan)
    # dfOrder['First_Picking'] = dfOrder['SapOrderNumber'].apply(lambda x: dfOrderLabels[dfOrderLabels['SapOrderNumber'] == x]['CreatedTimestamp'].min() if len(dfOrderLabels[dfOrderLabels['SapOrderNumber'] == x]['CreatedTimestamp']) > 0 else np.nan)

    return dfOrder

