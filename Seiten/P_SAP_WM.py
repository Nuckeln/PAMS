import streamlit as st
import pandas as pd
import numpy as np
import datetime
#from Data_Class.SQL import sql_datenLadenLabel,sql_datenLadenOderItems,sql_datenLadenStammdaten,sql_datenLadenOder
#from Data_Class.DB_Daten_Agg import orderDatenAgg
import st_aggrid as ag
import plotly_express as px
import plotly.graph_objects as go
from streamlit_option_menu import option_menu
from Data_Class.DB_Daten_Agg import DatenAgregieren as DA
from Data_Class.SQL import createnewTable, sql_datenLadenMLGT

class figSAPWM:       

    def fig_SN1(df):

        # TODO Wenn SKU gewählt dann Hervorheben mit Rot 

        df = df[df.LGTYP != 'TN1']
        anzZugrBIN15min = df.groupby(['LGPLA','MaterialNumber']).size().reset_index(name='Anzahl Zugriffe SKU/BIN')
        # create a heatmap with the numbers of LGPLA x = quantity of LGPLA
        # sort the values
        anzZugrBIN15min = anzZugrBIN15min.sort_values(by=['Anzahl Zugriffe SKU/BIN'], ascending=False)
        fig = px.bar(anzZugrBIN15min, x='LGPLA', y='Anzahl Zugriffe SKU/BIN', color='Anzahl Zugriffe SKU/BIN',hover_data=['MaterialNumber'])
        fig.update(layout_coloraxis_showscale=False)
        #fig.update_layout(yaxis=dict(visible=False))
        return fig

    def fig_TN1(df):
        # TODO Wenn SKU gewählt dann Hervorheben mit Rot 

        df = df[df.LGTYP != 'SN1']
        anzZugrBIN15min = df.groupby(['LGPLA','MaterialNumber']).size().reset_index(name='Anzahl Zugriffe SKU/BIN')
        # create a heatmap with the numbers of LGPLA x = quantity of LGPLA
        # sort the values
        anzZugrBIN15min = anzZugrBIN15min.sort_values(by=['Anzahl Zugriffe SKU/BIN'], ascending=False)
        fig = px.bar(anzZugrBIN15min, x='LGPLA', y='Anzahl Zugriffe SKU/BIN', color='Anzahl Zugriffe SKU/BIN',hover_data=['MaterialNumber'])
        #remove colur bar
        fig.update(layout_coloraxis_showscale=False)
        #fig.update_layout(yaxis=dict(visible=False))
        
        return fig

class SAPWM:

    heute = datetime.date.today()
    morgen = heute + datetime.timedelta(days=4)
    weekdays = [0, 1, 2, 3, 4]  # Montag ist 0, Dienstag ist 1, usw.
    today = datetime.date.today()
    workdays = []
    for i in range(5):
        if today.weekday() in weekdays:
            workdays.append(today)
        today -= datetime.timedelta(days=1)
    heute_minus_10_tage = workdays[0] - datetime.timedelta(days=30)

    
    @st.experimental_memo
    def loadDF():
        heute = datetime.date.today()
        heute_minus_10_tage = heute - datetime.timedelta(days=30)
        df = DA.orderDatenLines(
            heute_minus_10_tage, heute)
        return df


    def reload():
        if st.button("Reload"):
            SAPWM.loadDF.clear()
        

    def menueLaden():
        selected2 = option_menu(None, ["Stellplatzverwaltung", "Zugriffe SN/TN "],
        icons=['house', 'cloud-upload', "list-task"], 
        menu_icon="cast", default_index=0, orientation="horizontal")
        return selected2   

    def FilterNachDatum(day1, day2,df):
        df['PlannedDate'] = df['PlannedDate'].astype('datetime64[ns]').dt.date
        #filter nach Datum
        df = df[(df['PlannedDate'] >= day1) & (df['PlannedDate'] <= day2)]
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
        df = sql_datenLadenMLGT()
        return df
         
    def pageStellplatzverwaltung():
        dfOrders = SAPWM.loadDF()
        col1, col2 = st.columns(2)
        #----- Zeige StellplatzUptaden -----
        with col1:
            SAPWM.datenUpload()
        with col2:
            st.button("Reload", on_click=SAPWM.reload)
        #----- Lade Stellplatzdaten -----
        dfBIN = SAPWM.datenLadenBIN()
        dfBIN['MATNR'] = dfBIN['MATNR'].astype(str)
        dfBIN['MATNR'] = dfBIN['MATNR'].str[:8]

        #----- Filter nach Datum -----
        col1, col2 = st.columns(2)
        with col1:
            seldate = st.date_input('Datum')
        with col2:
            sel_range = st.slider('Wähle einen Bedarfszeitraum', min_value=1, max_value=30, value=5, step=1)
            sel_range = SAPWM.heute - datetime.timedelta(days=sel_range)
        #-- Bedarf letzte 7 Tage ermitteln und Df für Figur erstellen
        dfBedarfSKU = SAPWM.FilterNachDatum(sel_range,SAPWM.heute,dfOrders)
        dfFig = dfBedarfSKU.groupby(['MaterialNumber','PlannedDate','Picks OUT']).size().reset_index(name='Picks CS')
        dfFig = dfFig.merge(dfBIN, how='left', left_on='MaterialNumber', right_on='MATNR')
        dfBedarfSKU = dfBedarfSKU.groupby(['MaterialNumber']).sum().reset_index()

        #-- Filter nach Datum
        if seldate:
            dfOrders = SAPWM.FilterNachDatum(seldate,SAPWM.morgen,dfOrders)

        def bedarfCS(dfBedarfSKU,dfOrders):
                #--- Stellplatzdaten mit Bedarf zusammenführen-----
            dfBedarfSKU['Bedarf über Zeitraum'] = dfBedarfSKU['Picks CS']
            dfBedarfSKU = dfBedarfSKU[['MaterialNumber','Bedarf über Zeitraum']]
            dfOrders = dfOrders.merge(dfBedarfSKU, how='left', left_on='MaterialNumber', right_on='MaterialNumber')
            dfOrders = dfOrders.merge(dfBIN, how='left', left_on='MaterialNumber', right_on='MATNR')
            dfOrders = dfOrders.fillna('Kein Stellplatz')
            dfOrders['Bedarf über Zeitraum'] = dfOrders['Bedarf über Zeitraum']#.astype(int)
            #------drop unnötige Spalten -----
            dfOrders = dfOrders[['MaterialNumber','SapOrderNumber','Bedarf über Zeitraum','PlannedDate' ,'Picks CS','LGPLA', 'LPMIN' ,'LPMAX' ,'LGTYP', 'LGNUM']]
            dfOrders['LGPLA'] = dfOrders['LGPLA'].astype(str)
            dfOrders = dfOrders.rename(columns={'Picks CS': 'Bedarf gewählter Tag'})
            dfOrders = dfOrders.groupby(['MaterialNumber','SapOrderNumber','Bedarf über Zeitraum','PlannedDate' ,'LGPLA', 'LPMIN' ,'LPMAX' ,'LGTYP', 'LGNUM'])['Bedarf gewählter Tag'].sum().reset_index()
            dfOrders = dfOrders[['MaterialNumber','SapOrderNumber','Bedarf über Zeitraum','Bedarf gewählter Tag','PlannedDate' ,'LGPLA', 'LPMIN' ,'LPMAX' ,'LGTYP', 'LGNUM']]
        # Tn1 rausfiltern 
            dfOrders = dfOrders[dfOrders.LGTYP != 'TN1']
            return dfOrders
        def bedarfOut(dfBedarfSKU,dfOrders):
                #--- Stellplatzdaten mit Bedarf zusammenführen-----
            dfBedarfSKU['Bedarf über Zeitraum'] = dfBedarfSKU['Picks OUT']
            dfBedarfSKU = dfBedarfSKU[['MaterialNumber','Bedarf über Zeitraum']]
            dfOrders = dfOrders.merge(dfBedarfSKU, how='left', left_on='MaterialNumber', right_on='MaterialNumber')
            dfOrders = dfOrders.merge(dfBIN, how='left', left_on='MaterialNumber', right_on='MATNR')
            dfOrders = dfOrders.fillna('Kein Stellplatz')
            dfOrders['Bedarf über Zeitraum'] = dfOrders['Bedarf über Zeitraum']#.astype(int)
            #------drop unnötige Spalten -----
            dfOrders = dfOrders[['MaterialNumber','SapOrderNumber','Bedarf über Zeitraum','PlannedDate' ,'Picks OUT','LGPLA', 'LPMIN' ,'LPMAX' ,'LGTYP', 'LGNUM']]
            dfOrders['LGPLA'] = dfOrders['LGPLA'].astype(str)
            dfOrders = dfOrders.rename(columns={'Picks OUT': 'Bedarf gewählter Tag'})
            dfOrders = dfOrders.groupby(['MaterialNumber','SapOrderNumber','Bedarf über Zeitraum','PlannedDate' ,'LGPLA', 'LPMIN' ,'LPMAX' ,'LGTYP', 'LGNUM'])['Bedarf gewählter Tag'].sum().reset_index()
            dfOrders = dfOrders[['MaterialNumber','SapOrderNumber','Bedarf über Zeitraum','Bedarf gewählter Tag','PlannedDate' ,'LGPLA', 'LPMIN' ,'LPMAX' ,'LGTYP', 'LGNUM']]
        # Tn1 rausfiltern 
            dfOrders = dfOrders[dfOrders.LGTYP != 'SN1']
            # groupby 

            return dfOrders

        dfBedarfSKU = dfBedarfSKU.groupby(['MaterialNumber']).sum().reset_index()
        with st.expander('Kartonbedarf SN1', expanded=False):
            dfKarton = bedarfCS(dfBedarfSKU,dfOrders)
            ag.AgGrid(dfKarton,height=400)
            fig = figSAPWM.fig_SN1(dfFig)
            st.plotly_chart(fig, use_container_width=True)
        with st.expander('Stangenbedarf TN1', expanded=False):
            dfKarton = bedarfOut(dfBedarfSKU,dfOrders)
            ag.AgGrid(dfKarton,height=400)
            fig2 = figSAPWM.fig_TN1(dfFig)
            st.plotly_chart(fig2, use_container_width=True)


    def sap_wm_page():

        selected2 = SAPWM.menueLaden()
        if selected2 == "Stellplatzverwaltung":
            SAPWM.pageStellplatzverwaltung()
        elif selected2 == "Zugriffe SN/TN":
            SAPWM.pageLaden()
            

