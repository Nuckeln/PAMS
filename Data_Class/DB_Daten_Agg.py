from datetime import datetime
from pytz import timezone
import datetime
from lark import logger
import pandas as pd
import numpy as np
from Data_Class.SQL import SQL_TabellenLadenBearbeiten as SQL
import streamlit as st # Streamlit Web App Framework
import requests
import os
import pyarrow.parquet as pq
import pytz





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
        #safe dfSammdaten to excel
        #dfStammdaten.to_excel('/Users/martinwolf/Python/Superdepot Reporting/dfStammdaten.xlsx')

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
        #df.to_parquet('dfLines.parquet.gzip', compression='gzip')

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
            try:
                df['Fertiggestellt'] = pd.to_datetime(df['Fertiggestellt']).dt.strftime("%Y-%m-%d %H:%M:%S")
                df['Fertiggestellt'] = df['Fertiggestellt'].dt.tz_localize(None)    
            
            except:
                pass
    
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
        
        #save df to parquet
        return df

    def orderDatenGo(day1,day2):
        '''<<<start date, end date>>> gibt die Konsolidierten Daten als df zurück'''
        df = DatenAgregieren.orderDatenLines(date1=day1,date2=day2)
        df2 = df.copy()
        dfOr = DatenAgregieren.oderDaten(df2)
        return dfOr

class UpdateDaten():
    def updateAlle_Daten_():
        '''update Daten' seit Depotstart, braucht 1-2 min'''
        heute = datetime.datetime.now()
        heutePlus6 = heute + datetime.timedelta(days=6)
        df = DatenAgregieren.orderDatenGo(DatenAgregieren.startDatumDepot,heutePlus6)
        #save df to parquet
        df.to_parquet('df.parquet.gzip', compression='gzip')
        SQL.sql_test('prod_Kundenbestellungen', df)

    def updateDaten_byDate():
        df = pq.read_table('df.parquet.gzip').to_pandas()
        '''update Daten' seit Depotstart, braucht 1-2 min'''
        #df PlannetDate to datetime
        df['PlannedDate'] = pd.to_datetime(df['PlannedDate'])
        lastDay = df['PlannedDate'].max()
        # last day -5 tage

        lastDay = pd.to_datetime(lastDay) - datetime.timedelta(days=5)
        #add 10 days to lastDay
        #erase all data from day1 to day2
        df = df[df['PlannedDate'] < lastDay]
        df1 = DatenAgregieren.orderDatenGo(lastDay,DatenAgregieren.fuenfTage)
        dfneu = pd.concat([df,df1])
        #save
        #SQL.sql_test('prod_Kundenbestellungen', dfneu)
        # save to parquet
        #dfneu.to_parquet('df.parquet.gzip', compression='gzip')
        dftime = pd.DataFrame({'time':[datetime.datetime.now()]})
        dftime['time'] = dftime['time'] + datetime.timedelta(hours=1)
        SQL.sql_updateTabelle('prod_KundenbestellungenUpdateTime',dftime)
        df = SQL.sql_datenTabelleLaden('prod_Kundenbestellungen')
    def updateTable_Kundenbestellungen_14Days():
        df = SQL.sql_datenTabelleLaden('prod_Kundenbestellungen_14days')
        df['PlannedDate'] = df['PlannedDate'].astype(str)
        df['PlannedDate'] = pd.to_datetime(df['PlannedDate'].str[:10])
        # max date
        lastDay = df['PlannedDate'].max()
        # Calculate the date 5 days before the last day
        cutoff_date = lastDay - pd.Timedelta(days=14)
        # Keep only rows with PlannedDate greater than cutoff_date
        df = df[df['PlannedDate'] > cutoff_date]
        # last day plus 5 tage
        lastDayplus5 = pd.to_datetime(lastDay) + datetime.timedelta(days=15)
        df1 = pd.DataFrame()
        df1 = DatenAgregieren.orderDatenGo(cutoff_date,lastDayplus5)
        SQL.sql_test('prod_Kundenbestellungen_14days', df1)
        dftime = pd.DataFrame({'time':[datetime.datetime.now()]})
        dftime['time'] = dftime['time'] + datetime.timedelta(hours=1)
        SQL.sql_updateTabelle('prod_KundenbestellungenUpdateTime',dftime)

    def neuUpdate():
        if st.button('Update Daten'):
            UpdateDaten.updateAlle_Daten_()
            st.write('Update erfolgreich')
        df = SQL.sql_datenTabelleLaden('prod_Kundenbestellungen')
        dfOrginal = df.copy()
        st.dataframe(df)
        df['PlannedDate'] = df['PlannedDate'].astype(str)
        df['PlannedDate'] = pd.to_datetime(df['PlannedDate'].str[:10])
        # max date
        lastDay = df['PlannedDate'].max()
        # Calculate the date 5 days before the last day
        cutoff_date = lastDay - pd.Timedelta(days=14)

        # Keep only rows with PlannedDate greater than cutoff_date
        df = df[df['PlannedDate'] > cutoff_date]
        st.write('df nach cutoff')
        st.dataframe(df)
        # last day plus 5 tage
        lastDayplus5 = pd.to_datetime(lastDay) + datetime.timedelta(days=15)
        st.write('lastDay plus 5')
        st.write(lastDayplus5)
        df1 = pd.DataFrame()
        if st.button('Führe Daten AGG Aus und Update Tabelle prod_KundenbestellungenUpdateTime'):
                df1 = DatenAgregieren.orderDatenGo(cutoff_date,lastDayplus5)
                st.write('Daten AGG Ausgeführt', key = 'df1')
                #SQL.sql_createTable('prod_Kundenbestellungen_14days',df1)
                SQL.sql_test('prod_Kundenbestellungen_14days', df1)
                dftime = pd.DataFrame({'time':[datetime.datetime.now()]})
                dftime['time'] = dftime['time'] + datetime.timedelta(hours=1)
                SQL.sql_updateTabelle('prod_KundenbestellungenUpdateTime',dftime)
                st.dataframe(df1)               
        if st.button('Concat Dataframes and Update Table' , key = 'concat'):
                #merge df and df1
                dfneu = pd.concat([dfOrginal,df1])
                st.write('DF nach Concat')
                st.dataframe(dfneu)
                SQL.sql_test('prod_Kundenbestellungen', dfneu)
                st.write('Tabelle prod_Kundenbestellungen wurde aktualisiert')
                df = SQL.sql_datenTabelleLaden('prod_Kundenbestellungen')
                st.write('Tabelle prod_Kundenbestellungen aktualisiert')
                st.dataframe(df)