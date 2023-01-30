from datetime import datetime
from pytz import timezone
import datetime
from lark import logger
import pandas as pd
import numpy as np
from SQL import SQL_TabellenLadenBearbeiten as SQL
import streamlit as st # Streamlit Web App Framework
import requests
import os

#   streamlit run "/Users/martinwolf/Python/Superdepot Reporting/Data_Class/dataAggApp/DB_Daten.py"

class TagUndZeit():

    def UpdateZeitSQLTabelle():
        date_time_obj = datetime.datetime.now()
        # Create a pandas dataframe with two columns for the date and time
        df = pd.DataFrame({'Date': [date_time_obj.date()], 'Time': [date_time_obj.time()]})
        df = pd.DataFrame({'Date': [date_time_obj.date()], 'Time': [date_time_obj.time()]})
        #to string
        df['Date'] = df['Date'].astype(str)
        df['Time'] = df['Time'].astype(str)
        SQL.sql_updateTabelle('prod_KundenbestellungenUpdateTime', df)
        return df

class DatenAgregieren():
    '''Klasse zum Agregieren von Daten aus der Datenbank
    Datum eingrenzen? 
    '''
    heute = datetime.date.today()
    morgen = heute + datetime.timedelta(days=1)
    fuenfTage = heute + datetime.timedelta(days=5)
    startDatumDepot = '2021-04-01'
    time = datetime.datetime.now()

    def orderDatenLines(date1, date2):
        '''Lädt die Daten aus der Datenbank und berechnet die Werte
        erwartet 2 Datumsangaben'''
        ##------------------ Stammdaten Laden und berechnen ------------------##
        dfStammdaten = SQL.sql_datenTabelleLaden('data_materialmaster-MaterialMasterUnitOfMeasures')
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

        ##------------------ Order Date von DB Laden ------------------##
        dfOrder = SQL.sql_datenLadenDatum(date1,date2,SQL.tabelle_DepotDEBYKNOrders,SQL.datumplannedDate)
        ##------------------ Order Items von DB Laden ------------------##
        dfOrderItems = SQL.sql_datenTabelleLaden('business_depotDEBYKN-DepotDEBYKNOrderItems')
        ##------------------ Kunden von DB Laden ------------------##
        dfKunden = SQL.sql_datenTabelleLaden('Kunden_mit_Packinfos')
        ##------------------ Merge Items und Stammdaten ------------------##
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

        # applying merge

        df = pd.merge(dfOrder, dfOrderItems, left_on='SapOrderNumber', right_on='SapOrderNumber', how='left')
        df = pd.merge(df, dfKunden[['PartnerNo', 'PartnerName']], on='PartnerNo', how='left')


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
        #NiceLabelTransmissionState_TimeStamp to string
        df['NiceLabelTransmissionState_TimeStamp'] = df['NiceLabelTransmissionState_TimeStamp'].astype(str)
        return df

    def oderDaten(df):
        #df = DatenAgregieren.orderDatenLines()
        dfLabel = SQL.sql_datenLadenDatum(DatenAgregieren.startDatumDepot, DatenAgregieren.fuenfTage ,SQL.tabelleSSCCLabel,'CreatedTimestamp')       
        df1 = df
        
            
        df = df.groupby(['PlannedDate','PartnerName','SapOrderNumber',"AllSSCCLabelsPrinted",'DeliveryDepot']).agg({'Picks Gesamt':'sum'}).reset_index()
        df['Lieferschein erhalten'] = df['SapOrderNumber'].apply(lambda x: df1.loc[df1['SapOrderNumber'] == x]['CreatedTimestamp'].iloc[0])


        def handle_invalid_date(date_value):
            try:
                return pd.to_datetime(date_value).strftime("%Y-%m-%d %H:%M:%S%z")
            except ValueError:
                # handle invalid date value
                return None

        df1["QuantityCheckTimestamp"] = df1["QuantityCheckTimestamp"].apply(handle_invalid_date)
        df1['QuantityCheckTimestamp'] = pd.to_datetime(df1['QuantityCheckTimestamp']).dt.strftime("%Y-%m-%d %H:%M:%S")
        #df1["QuantityCheckTimestamp"] = df1["QuantityCheckTimestamp"].dt.tz_localize(None)
        df['Fertiggestellt'] = df['SapOrderNumber'].apply(lambda x: df1.loc[df1['SapOrderNumber'] == x]['QuantityCheckTimestamp'].iloc[0])
        if df['Fertiggestellt'].notna().all():
            df['Fertiggestellt'] = df['Fertiggestellt'].dt.tz_localize(None)        
        df['Truck Kennzeichen'] = df['SapOrderNumber'].apply(lambda x: df1.loc[df1['SapOrderNumber'] == x]['UnloadingListIdentifier'].iloc[0])
        # sum for each in df.SapOrderNumber of df1'Picks CS'  with same SapOrderNumber
        df['Picks Karton'] = df['SapOrderNumber'].apply(lambda x: df1.loc[df1['SapOrderNumber'] == x]['Picks CS'].sum())
        df['Picks Paletten'] = df['SapOrderNumber'].apply(lambda x: df1.loc[df1['SapOrderNumber'] == x]['Picks PAL'].sum())
        df['Picks Stangen'] = df['SapOrderNumber'].apply(lambda x: df1.loc[df1['SapOrderNumber'] == x]['Picks OUT'].sum())
        # sum for each in df.SapOrderNumber of df1'offen Picks CS'  with same SapOrderNumber and AllSSCCLabelsPrinted = 0
        df['Picks Karton offen'] = df['SapOrderNumber'].apply(lambda x: df1.loc[(df1['SapOrderNumber'] == x) & (df1['AllSSCCLabelsPrinted'] == 0)]['Picks CS'].sum())
        df['Picks Paletten offen'] = df['SapOrderNumber'].apply(lambda x: df1.loc[(df1['SapOrderNumber'] == x) & (df1['AllSSCCLabelsPrinted'] == 0)]['Picks PAL'].sum())
        df['Picks Stangen offen'] = df['SapOrderNumber'].apply(lambda x: df1.loc[(df1['SapOrderNumber'] == x) & (df1['AllSSCCLabelsPrinted'] == 0)]['Picks OUT'].sum())
        df['Picks Karton fertig'] = df['SapOrderNumber'].apply(lambda x: df1.loc[(df1['SapOrderNumber'] == x) & (df1['AllSSCCLabelsPrinted'] == 1)]['Picks CS'].sum())
        df['Picks Paletten fertig'] = df['SapOrderNumber'].apply(lambda x: df1.loc[(df1['SapOrderNumber'] == x) & (df1['AllSSCCLabelsPrinted'] == 1)]['Picks PAL'].sum())
        df['Picks Stangen fertig'] = df['SapOrderNumber'].apply(lambda x: df1.loc[(df1['SapOrderNumber'] == x) & (df1['AllSSCCLabelsPrinted'] == 1)]['Picks OUT'].sum())

        #df PartnerName, SapOrderNumber, AllSSCCLabelsPrinted, Picks Gesamt to str
        df['PartnerName'] = df['PartnerName'].astype(str)
        df['SapOrderNumber'] = df['SapOrderNumber'].astype(str)
        #df['AllSSCCLabelsPrinted'] = df['AllSSCCLabelsPrinted'].astype(str)
        #df['Picks Gesamt'] to int
        df['Picks Gesamt'] = df['Picks Gesamt'].astype(int)
        # count for each in df.SapOrderNumber how many D97 entrys are in dfLabel.UnitOfMeasure with same SapOrderNumber and ParentID = null
        df['Fertige Paletten'] = df['SapOrderNumber'].apply(lambda x: dfLabel[(dfLabel['UnitOfMeasure'] == 'D97') & (dfLabel['ParentID'].isnull())].loc[dfLabel['SapOrderNumber'] == x].shape[0])
        #df['Paletten Label'] = df['SapOrderNumber'].apply(lambda x: dfLabel[dfLabel['UnitOfMeasure'] == 'D97'].loc[dfLabel['SapOrderNumber'] == x].shape[0])
        df['Lieferschein erhalten'] = df['Lieferschein erhalten'].astype(str)
        df['Fertiggestellt'] = df['Fertiggestellt'].astype(str)
        df['Fertiggestellt'] = df['Fertiggestellt'].str.replace("nan","")
        df['Fertiggestellt'] = df['Fertiggestellt'].str.replace("NaT","")
        df['PlannedDate'] = df['PlannedDate'].astype(str)
        return df

    def orderDatenGo(day1,day2):
        '''<<<start date, end date>>> gibt die Konsolidierten Daten als df zurück'''
        df = DatenAgregieren.orderDatenLines(date1=day1,date2=day2)
        df = DatenAgregieren.oderDaten(df)
        return df

class UpdateDaten():
    def updateAlle_Daten_():
        '''update Daten' seit Depotstart, braucht 1-2 min'''
        df = DatenAgregieren.orderDatenGo(DatenAgregieren.startDatumDepot,DatenAgregieren.fuenfTage)
        #save df to parquet
        df.to_parquet('Data/appData/df.parquet.gzip', compression='gzip')

    def updateDaten_byDate(df):
        '''update Daten' seit Depotstart, braucht 1-2 min'''
        lastDay = df['PlannedDate'].max()
        #add 10 days to lastDay
        #erase all data from day1 to day2
        df = df[df['PlannedDate'] < lastDay]
        st.warning('Daten werden aktualisiert')
        df1 = DatenAgregieren.orderDatenGo(lastDay,DatenAgregieren.fuenfTage)
        st.success('Daten wurden aktualisiert')
        df = pd.concat([df,df1])
        SQL.sql_updateTabelle(df)
        #save df to parquet

st.set_page_config(layout="wide", page_title="DBDaten", page_icon=":bar_chart:",initial_sidebar_state="collapsed")
df = SQL.sql_datenTabelleLaden('prod_Kundenbestellungen')
df['PlannedDate'] = pd.to_datetime(df['PlannedDate'].str[:10])
st.write(DatenAgregieren.time)
#Count Picks Karton Fertig
a = df['Picks Karton fertig'].sum()
st.write('Picks Karton fertig',a)

#erease timestamps from PlannedDate
#creeate df 2 columns one with actual date and one with time both from WEB API call
st.dataframe(df)
st.write('Update Daten')
if st.button('Update'):

    UpdateDaten.updateDaten_byDate(df)
    st.success('Daten wurden aktualisiert')
    df2 = SQL.sql_datenTabelleLaden('prod_Kundenbestellungen')
    #TagUndZeit.UpdateZeitSQLTabelle()
    st.dataframe(df2)
