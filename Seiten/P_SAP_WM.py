import streamlit as st
import pandas as pd
import numpy as np
import datetime
#from Data_Class.SQL import sql_datenLadenLabel,sql_datenLadenOderItems,sql_datenLadenStammdaten,sql_datenLadenOder
from Data_Class.DB_Daten_Agg import orderDatenAgg
import plotly_express as px
from streamlit_option_menu import option_menu
from Data_Class.DB_Daten_Agg import orderDatenAgg
from Data_Class.SQL import createnewTable, sql_datenLadenMLGT

class SAPWM:
    
    heute  = datetime.date.today()
    morgen =heute + datetime.timedelta(days=1)
    def __init__(self):
        self.df = df

    def sessionstate():
        if 'key' not in st.session_state:
            st.session_state['key'] = 'value'
        if 'key' not in st.session_state:
            st.session_state.key = +1
    @st.experimental_memo
    def labeOrderDaten():
        df = orderDatenAgg()
        return df
    

    def menueLaden():
        selected2 = option_menu(None, ["Stellplatzverwaltung", "Zugriffe SN/TN "],
        icons=['house', 'cloud-upload', "list-task"], 
        menu_icon="cast", default_index=0, orientation="horizontal")
        return selected2   

    def FilterNachDatum(day1, day2,df):
        #df['PlannedDate'] = df['PlannedDate'].dt.strftime('%m/%d/%y')
        df['PlannedDate'] = df['PlannedDate'].astype('datetime64[ns]').dt.date
        #filter nach Datum
        df = df[(df['PlannedDate'] >= day1) & (df['PlannedDate'] <= day2)]
        #mask = (df['PlannedDate'] >= day1) & (df['PlannedDate'] <= day2)         
        #df = df.loc[mask]
        return df
    
    def datenUpload():
        with st.expander('Stellplatzdaten Updaten', expanded=False):
            uploaded_file = st.file_uploader("Bitte die Stellplatzdaten hochladen", type="xlsx")
            if uploaded_file is not None:
                df = pd.read_excel(uploaded_file,header=3)
                createnewTable(df,'MLGT_Stellplatz')
                st.success("File uploaded successfully")
                st.balloons()
                st.experimental_rerun()

    def datenLadenBIN():
        #df = pd.read_excel("Data/MLGT.xlsx",header=3) 
        df = sql_datenLadenMLGT()
        return df
         
    def pageStellplatzverwaltung(dfOrders):
        SAPWM.datenUpload()
        #----- Lade Stellplatzdaten -----
        dfBIN = SAPWM.datenLadenBIN()
        dfBIN['MATNR'] = dfBIN['MATNR'].astype(str)
        dfBIN['MATNR'] = dfBIN['MATNR'].str[:8]
        
        #-- Bedarf letzte 7 Tage ermitteln
        heuteMinus7Tage = SAPWM.heute - datetime.timedelta(days=7)
        dfBedarfSKU = SAPWM.FilterNachDatum(heuteMinus7Tage,SAPWM.heute,dfOrders)
        dfBedarfSKU = dfBedarfSKU.groupby(['MaterialNumber']).sum().reset_index()
        dfBedarfSKU['GesamtBedarfSKU'] = dfBedarfSKU['Picks CS']
        dfBedarfSKU = dfBedarfSKU[['MaterialNumber','GesamtBedarfSKU']]
        #--- Stellplatzdaten mit Bedarf zusammenführen-----
        dfOrders = dfOrders.merge(dfBedarfSKU, how='left', left_on='MaterialNumber', right_on='MaterialNumber')
        dfOrders = dfOrders.merge(dfBIN, how='left', left_on='MaterialNumber', right_on='MATNR')
        dfOrders = dfOrders.fillna(0)
        dfOrders['GesamtBedarfSKU'] = dfOrders['GesamtBedarfSKU'].astype(int)
        #------drop unnötige Spalten -----
        dfOrders = dfOrders[['MaterialNumber','SapOrderNumber','GesamtBedarfSKU','PlannedDate' ,'Picks CS','LGPLA', 'LPMIN' ,'LPMAX' ,'LGTYP', 'LGNUM']]
        dfOrders['LGPLA'] = dfOrders['LGPLA'].astype(str)
        dfOrders = dfOrders.rename(columns={'Picks CS': 'BedarfCsTag'})
        dfOrders = dfOrders.groupby(['MaterialNumber','SapOrderNumber','GesamtBedarfSKU','PlannedDate' ,'LGPLA', 'LPMIN' ,'LPMAX' ,'LGTYP', 'LGNUM'])['BedarfCsTag'].sum().reset_index()
        dfOrders = dfOrders[['MaterialNumber','SapOrderNumber','GesamtBedarfSKU','BedarfCsTag','PlannedDate' ,'LGPLA', 'LPMIN' ,'LPMAX' ,'LGTYP', 'LGNUM']]
        dfOrders = dfOrders[dfOrders.LGTYP != 'TN1']
        
        
        seldate = st.date_input('Datum')
        if seldate:
            dfOrders = SAPWM.FilterNachDatum(seldate,seldate,dfOrders)
            #dfCS = dfCS.groupby(['MaterialNumber','LGPLA'],dropna =False)['Picks CS'].sum().reset_index()

        st.dataframe(dfOrders)      

    def sap_wm_page():
        dfOrders = SAPWM.labeOrderDaten()
        selected2 = SAPWM.menueLaden()
        if selected2 == "Stellplatzverwaltung":
            SAPWM.pageStellplatzverwaltung(dfOrders)
        elif selected2 == "Zugriffe SN/TN":
            SAPWM.pageLaden()
            

