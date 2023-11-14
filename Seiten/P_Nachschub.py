import streamlit as st
import pandas as pd
import datetime
#from Data_Class.SQL import sql_datenLadenLabel,sql_datenLadenOderItems,sql_datenLadenStammdaten,sql_datenLadenOder
#from Data_Class.DB_Daten_Agg import orderDatenAgg
import st_aggrid as ag
import plotly_express as px
from streamlit_option_menu import option_menu
from Data_Class.MMSQL_connection import read_Table
import Data_Class.AzureStorage
from io import BytesIO




class figSAPWM:       

    def fig_SN1(df):
        df = df[df.LGTYP != 'TN1']
        anzZugrBIN15min = df.groupby(['LGPLA','MaterialNumber']).size().reset_index(name='Anzahl Zugriffe SKU/BIN')
        # create a heatmap with the numbers of LGPLA x = quantity of LGPLA
        # sort the values
        anzZugrBIN15min = anzZugrBIN15min.sort_values(by=['Anzahl Zugriffe SKU/BIN'], ascending=False)
        fig = px.bar(anzZugrBIN15min, x='LGPLA', y='Anzahl Zugriffe SKU/BIN', color='Anzahl Zugriffe SKU/BIN',hover_data=['MaterialNumber'])
        fig.update(layout_coloraxis_showscale=False)
        fig.update_layout(yaxis=dict(visible=False))
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
    heute_minus_10_tage =  datetime.timedelta(days=30)

    @st.cache_data
    def loadDF():
        df = read_Table('OrderDatenLines')
        return df  
      
    def menueLaden():
        selected2 = option_menu(None, ["Stellplatzverwaltung", "Zugriffe SN/TN "],
        icons=['house', 'cloud-upload', "list-task"], 
        menu_icon="cast", default_index=0, orientation="horizontal")
        return selected2   
    
    def FilterNachDatum(day1, day2, df):
        day1 = pd.to_datetime(day1).date()
        day2 = pd.to_datetime(day2).date()
        # filter date
        df['PlannedDate'] = pd.to_datetime(df['PlannedDate']).dt.date
        df = df[(df['PlannedDate'] >= day1) & (df['PlannedDate'] <= day2)]
        df = df.astype(str)
        return df
    

    def datenUpload():
        with st.expander('Stellplatzdaten Updaten', expanded=False):
            Data_Class.AzureStorage.st_Azure_uploadBtn('Nachschub')
            
        
    def datenLadenBIN():
        file = read_Table('AzureStorage')
        #serch last entry Nachschub[anwendung] == Nachschub and get filename
        filename = file[file['anwendung'] == 'Nachschub']
        filename = filename.sort_values(by=['dateTime'], ascending=False)
        file_name = filename.iloc[0]['filename']
        filenameOrg = filename.iloc[0]['filenameorg']
        # add filename to a string
        file_name = file_name.lower()

        file = Data_Class.AzureStorage.get_blob_file(file_name)
        df = pd.read_excel(BytesIO(file), engine='openpyxl', header=3)

        return df, filenameOrg
         
    def pageStellplatzverwaltung():
        dfOrders = SAPWM.loadDF()
        #st.data_editor(dfOrders)
        SAPWM.datenUpload()

        #----- Lade Stellplatzdaten -----
        dfBIN, filenameOrg = SAPWM.datenLadenBIN()
        st.write('Stellplatzdaten: ',filenameOrg)
        dfBIN['MATNR'] = dfBIN['MATNR'].astype(str)
        dfBIN['MATNR'] = dfBIN['MATNR'].str[:8]

        #----- Filter nach Datum -----
        col1, col2 = st.columns(2)
        with col1:
            seldate = st.date_input('Datum')
        with col2:
            sel_range = st.slider('Wähle einen Bedarfszeitraum', min_value=1, max_value=14, value=5, step=1)
            sel_range = SAPWM.heute - datetime.timedelta(days=sel_range)
            
        #-- Bedarf letzte 7 Tage ermitteln und Df für Figur erstellen
        dfBedarfSKU = SAPWM.FilterNachDatum(sel_range,SAPWM.heute,dfOrders)
        #drop all columns except MaterialNumber PlannedDate, CorrospondingOuters. CorrospondingMasterCases, SaporderNumber
        dfBedarfSKU['MaterialNumber'] = dfBedarfSKU['MaterialNumber'].astype(str)
        dfBedarfSKU['CorrespondingOuters'] = dfBedarfSKU['CorrespondingOuters'].astype(float)
        dfBedarfSKU['CorrespondingMastercases'] = dfBedarfSKU['CorrespondingMastercases'].astype(float)

        #Filter dfBIN dfBIN['LGTYP'] == 'SN1'
        dfBIN_SN = dfBIN[dfBIN['LGTYP'] == 'SN1']
        dfBIN_SN = dfBIN_SN.rename(columns={'LGPLA': 'LGPLA_SN','LGTYP': 'LGTYP_SN'})
        dfBIN_TN = dfBIN[dfBIN['LGTYP'] == 'TN1']
        dfBIN_TN = dfBIN_TN.rename(columns={'LGPLA': 'LGPLA_TN','LGTYP': 'LGTYP_TN'})

        dfBedarfSKU = dfBedarfSKU.merge(dfBIN_SN, how='left', left_on='MaterialNumber', right_on='MATNR')
        dfBedarfSKU = dfBedarfSKU.merge(dfBIN_TN, how='left', left_on='MaterialNumber', right_on='MATNR')

        dfBedarfSKU['LGPLA_SN'] = dfBedarfSKU['LGPLA_SN'].fillna('Kein Stellplatz in SN1')
        # fill none in LGTYP with 'Kein Stellplatz'

        dfBedarfSKU['LGPLA_TN'] = dfBedarfSKU['LGPLA_TN'].fillna('Kein Stellplatz in TN1')
        # Fill None in LGPLA with 'Kein Stellplatz'
        dfBedarfSKU = dfBedarfSKU[['MaterialNumber','PlannedDate','CorrespondingOuters','CorrespondingMastercases','SapOrderNumber','LGPLA_SN','LGTYP_SN','LGTYP_TN','LGPLA_TN']]
        st.dataframe(dfBedarfSKU)
        
        with st.expander('Nicht Gepflegte SKUs',expanded=True):
            df_nichtGepflegt_SN = dfBedarfSKU[dfBedarfSKU['LGPLA_SN'] == 'Kein Stellplatz in SN1']
            # drop duplicates in MaterialNumber
            df_nichtGepflegt_SN = df_nichtGepflegt_SN.drop_duplicates(subset=['MaterialNumber'])
            df_nichtGepflegt_TN = dfBedarfSKU[dfBedarfSKU['LGPLA_TN'] == 'Kein Stellplatz in TN1']
            # drop duplicates in MaterialNumber
            df_nichtGepflegt_TN = df_nichtGepflegt_TN.drop_duplicates(subset=['MaterialNumber'])
            st.dataframe(df_nichtGepflegt_SN)
            st.dataframe(df_nichtGepflegt_TN)

        with st.expander('Kartonbedarf SN1',expanded=True):
            # filter CorrospondingMastercases > 0
            dfBedarfSKU_SN = dfBedarfSKU[dfBedarfSKU['CorrespondingMastercases'] > 0]
            # drop PlannedDate and SapOrderNumber
            dfBedarfSKU_SN = dfBedarfSKU_SN[['MaterialNumber','CorrespondingMastercases','LGPLA_SN']]
            # group by MaterialNumber and sum CorrespondingMastercases
            dfBedarfSKU_SN = dfBedarfSKU_SN.groupby(['MaterialNumber','LGPLA_SN']).sum().reset_index()
            # sort by CorrespondingMastercases
            dfBedarfSKU_SN = dfBedarfSKU_SN.sort_values(by=['CorrespondingMastercases'], ascending=False)
            st.data_editor(dfBedarfSKU_SN, key='my_editorSNBedarf')
            fig = px.bar(dfBedarfSKU_SN, x='LGPLA_SN', y='CorrespondingMastercases', color='CorrespondingMastercases',hover_data=['MaterialNumber'])
            fig.update(layout_coloraxis_showscale=False)
            fig.update_layout(yaxis=dict(visible=False))
            st.plotly_chart(fig, use_container_width=True)
            
        with st.expander('Stangenbedarf TN1',expanded=True):
            # filter CorrospondingMastercases > 0
            dfBedarfSKU_TN = dfBedarfSKU[dfBedarfSKU['CorrespondingOuters'] > 0]
            # drop PlannedDate and SapOrderNumber
            dfBedarfSKU_TN = dfBedarfSKU_TN[['MaterialNumber','CorrespondingOuters','LGPLA_TN']]
            # group by MaterialNumber and sum CorrespondingMastercases
            dfBedarfSKU_TN = dfBedarfSKU_TN.groupby(['MaterialNumber','LGPLA_TN']).sum().reset_index()
            # sort by CorrespondingMastercases
            dfBedarfSKU_TN = dfBedarfSKU_TN.sort_values(by=['CorrespondingOuters'], ascending=False)
            st.data_editor(dfBedarfSKU_TN, key='my_editorTNBedarf')
            fig = px.bar(dfBedarfSKU_TN, x='LGPLA_TN', y='CorrespondingOuters', color='CorrespondingOuters',hover_data=['MaterialNumber'])
            fig.update(layout_coloraxis_showscale=False)
            fig.update_layout(yaxis=dict(visible=False))
            st.plotly_chart(fig, use_container_width=True)

#            st.plotly_chart(fig, use_container_width=True)

    #     with st.expander('Stangenbedarf TN1', expanded=True):
    #         dfKarton = bedarfOut(dfBedarfSKU,dfOrders)
    #         ag.AgGrid(dfKarton,height=400)
    #         fig2 = figSAPWM.fig_TN1(dfFig)
    #         st.plotly_chart(fig2, use_container_width=True)


    #     dfFig = dfBedarfSKU.groupby(['MaterialNumber','PlannedDate','Picks OUT']).size().reset_index(name='Picks CS')

    #     #-- Stellplatzdaten mit Bedarf zusammenführen-----
    #     #MaterialNumber to int
    #     dfBedarfSKU = dfBedarfSKU.groupby(['MaterialNumber']).sum().reset_index()

    #     #-- Filter nach Datum
    #     if seldate:
    #         dfOrders = SAPWM.FilterNachDatum(seldate,seldate,dfOrders)

    #     def bedarfCS(dfBedarfSKU,dfOrders):
    #             #--- Stellplatzdaten mit Bedarf zusammenführen-----
    #         dfBedarfSKU['Bedarf über Zeitraum'] = dfBedarfSKU['Picks CS']
    #         dfBedarfSKU = dfBedarfSKU[['MaterialNumber','Bedarf über Zeitraum']]
    #         dfOrders = dfOrders.merge(dfBedarfSKU, how='left', left_on='MaterialNumber', right_on='MaterialNumber')
    #         dfOrders['MaterialNumber'] = dfOrders['MaterialNumber'].astype(str)

    #         dfOrders = dfOrders.merge(dfBIN, how='left', left_on='MaterialNumber', right_on='MATNR')
    #         dfOrders = dfOrders.fillna('Kein Stellplatz')
    #         dfOrders['Bedarf über Zeitraum'] = dfOrders['Bedarf über Zeitraum']#.astype(int)
    #         #------drop unnötige Spalten -----
    #         dfOrders = dfOrders[['MaterialNumber','SapOrderNumber','Bedarf über Zeitraum','PlannedDate' ,'Picks CS','LGPLA', 'LPMIN' ,'LPMAX' ,'LGTYP', 'LGNUM']]
    #         dfOrders['LGPLA'] = dfOrders['LGPLA'].astype(str)
    #         dfOrders = dfOrders.rename(columns={'Picks CS': 'Bedarf gewählter Tag'})
    #         dfOrders = dfOrders.groupby(['MaterialNumber','SapOrderNumber','Bedarf über Zeitraum','PlannedDate' ,'LGPLA', 'LPMIN' ,'LPMAX' ,'LGTYP', 'LGNUM'])['Bedarf gewählter Tag'].sum().reset_index()
    #         dfOrders = dfOrders[['MaterialNumber','SapOrderNumber','Bedarf über Zeitraum','Bedarf gewählter Tag','PlannedDate' ,'LGPLA', 'LPMIN' ,'LPMAX' ,'LGTYP', 'LGNUM']]
    #     # SN1 rausfiltern 
    #         dfOrders = dfOrders[dfOrders.LGTYP != 'TN1']
    #         dfOrders = dfOrders[dfOrders['Bedarf gewählter Tag'] != 0]

    #         return dfOrders
        
    #     def bedarfOut(dfBedarfSKU,dfOrders):
    #             #--- Stellplatzdaten mit Bedarf zusammenführen-----
    #         dfBedarfSKU['Bedarf über Zeitraum'] = dfBedarfSKU['Picks OUT']
    #         dfBedarfSKU = dfBedarfSKU[['MaterialNumber','Bedarf über Zeitraum']]
    #         dfOrders = dfOrders.merge(dfBedarfSKU, how='left', left_on='MaterialNumber', right_on='MaterialNumber')
    #         dfOrders = dfOrders.merge(dfBIN, how='left', left_on='MaterialNumber', right_on='MATNR')
    #         dfOrders = dfOrders.fillna('Kein Stellplatz')
    #         dfOrders['Bedarf über Zeitraum'] = dfOrders['Bedarf über Zeitraum']#.astype(int)
    #         #------drop unnötige Spalten -----
    #         dfOrders = dfOrders[['MaterialNumber','SapOrderNumber','Bedarf über Zeitraum','PlannedDate' ,'Picks OUT','LGPLA', 'LPMIN' ,'LPMAX' ,'LGTYP', 'LGNUM']]
    #         dfOrders['LGPLA'] = dfOrders['LGPLA'].astype(str)
    #         dfOrders = dfOrders.rename(columns={'Picks OUT': 'Bedarf gewählter Tag'})
    #         dfOrders = dfOrders.groupby(['MaterialNumber','SapOrderNumber','Bedarf über Zeitraum','PlannedDate' ,'LGPLA', 'LPMIN' ,'LPMAX' ,'LGTYP', 'LGNUM'])['Bedarf gewählter Tag'].sum().reset_index()
    #         dfOrders = dfOrders[['MaterialNumber','SapOrderNumber','Bedarf über Zeitraum','Bedarf gewählter Tag','PlannedDate' ,'LGPLA', 'LPMIN' ,'LPMAX' ,'LGTYP', 'LGNUM']]
    #     # Tn1 rausfiltern 
    #         dfOrders = dfOrders[dfOrders.LGTYP != 'SN1']
    #         dfOrders = dfOrders[dfOrders['Bedarf gewählter Tag'] != 0]
    #         return dfOrders

    #     dfBedarfSKU = dfBedarfSKU.groupby(['MaterialNumber']).sum().reset_index()


    def seite():

        SAPWM.pageStellplatzverwaltung()

            

