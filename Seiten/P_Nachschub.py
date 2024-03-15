import streamlit as st
import pandas as pd
import datetime
import time
#from Data_Class.SQL import sql_datenLadenLabel,sql_datenLadenOderItems,sql_datenLadenStammdaten,sql_datenLadenOder
#from Data_Class.DB_Daten_Agg import orderDatenAgg
import st_aggrid as ag
import plotly_express as px
from streamlit_option_menu import option_menu
from Data_Class.MMSQL_connection import read_Table , save_Table
import Data_Class.AzureStorage
from io import BytesIO
from PIL import Image
import json


import seaborn as sns
import matplotlib.pyplot as plt




heute = datetime.date.today()
morgen = heute + datetime.timedelta(days=4)
heute_minus_10_tage =  datetime.timedelta(days=30)

def untersagte_sku_TN(masterdata,dfBIN):
    df = read_Table('data_materialmaster-MaterialMasterUnitOfMeasures')
    dfText = read_Table('MaterialMasterMaterialDescriptions')
    masterdata = read_Table('data_materialmaster_Duplicate_InternationalArticleNumber')

    # filtere nur nicht leer in InternationalArticleNumber
    df = df[df['InternationalArticleNumber'].notna()]

    # Kombiniere MaterialNumber und InternationalArticleNumber zu einem neuen Feld Check
    df['Check'] = df['MaterialNumber'].astype(str) + df['InternationalArticleNumber'].astype(str)

    # Filter nur Zeilen in denen es Duplikate in InternationalArticleNumber gibt
    df = df[df.duplicated(['Check'], keep=False)]


    save_Table(df, 'data_materialmaster_Duplicate_InternationalArticleNumber')
    
    #check if InternationalArticleNumber is in dfText
    masterdata['MaterialNumber'] = masterdata['MaterialNumber'].str.replace('0000000000', '')
    # filter dfBin by LPGTY == 'TN1'
    dfBIN = dfBIN[dfBIN['LGTYP'] == 'TN1']
    #Filter masterdata['UnitOfMeasure'] == 'OUT'
    masterdata = masterdata[masterdata['UnitOfMeasure'] == 'OUT']
    #MaterialNumber to float
    masterdata['MaterialNumber'] = masterdata['MaterialNumber'].astype(float)
    df_verbot = pd.merge(dfBIN, masterdata, how='inner', left_on='MATNR', right_on='MaterialNumber')
    # filter is LGPLA_TN not None
    df_verbot = df_verbot[df_verbot['LGPLA'].notna()]
    # drop duplicates in MATNR
    df_verbot = df_verbot.drop_duplicates(subset=['MATNR'])
    # drop columns bis auf MATNR and LGPLA 
    df_verbot = df_verbot[['MATNR','LGPLA']] 
    #save dfVerbot
    df_verbot.to_csv('Data/df_verbot.csv', index=False)
    return df

@st.cache_data
def loadDF():
    df = read_Table('OrderDatenLines')

    masterdata = read_Table('data_materialmaster_Duplicate_InternationalArticleNumber')

    df = df[(df['IsDeleted'] == 0) & (df['IsReturnDelivery'] == 0)]
        
    dfBIN = pd.read_excel("Data/appData/MLGT.xlsx",header=3)
    
    dfBIN = dfBIN[dfBIN['MATNR'].notna()]   
    def read_single_value_from_file(file_path):
        with open(file_path, 'r') as f:
            data = f.read().strip()
        return data

    # Verwenden Sie die Funktion, um den Wert aus der Datei zu lesen
    lastUpload = read_single_value_from_file('Data/appData/lastUpload.json')
    filenameOrg = f"MLGT vom:{lastUpload}"
    df_alleVerbotenenSKU = untersagte_sku_TN(masterdata,dfBIN)       
    return df, masterdata,dfBIN, filenameOrg,df_alleVerbotenenSKU
    
def menueLaden():
    selected2 = option_menu(None, ["Stellplatzverwaltung", "Zugriffe SN/TN "],
    icons=['house', 'cloud-upload', "list-task"], 
    menu_icon="cast", default_index=0, orientation="horizontal")
    return selected2   

def FilterNachDatum(day1, day2, df):
    day1 = pd.to_datetime(day1).date()
    day2 = pd.to_datetime(day2).date()

    #st.data_editor(df)  
    # filter date
    df['PlannedDate'] = pd.to_datetime(df['PlannedDate'], format="%d.%m.%Y").dt.date 
    df = df[(df['PlannedDate'] >= day1) & (df['PlannedDate'] <= day2)]
    df = df.astype(str)
    # filter date   
    return df

def datenUpload(masterdata,dfBIN):
    with st.expander('Stellplatzdaten Updaten', expanded=False):
        org_file = 'Data/appData/MLGTP_org.xlsx'
        date = datetime.date.today().strftime("%Y-%m-%d")
        selFile = st.file_uploader('Stellplatzdaten Updaten', type=['xlsx'])
        col1 , col2 = st.columns(2)
        with col1:
            if st.button('Upload'):
                if selFile is not None:
                    st.write('Uploading...')
                    # Speichern Sie die hochgeladene Datei unter einem neuen Namen und Pfad
                    with open(f'Data/appData/MLGT.xlsx', 'wb') as f:
                        f.write(selFile.getvalue())
                        #save date in a locl json file
                        with open('Data/appData/lastUpload.json', 'w') as f:
                            f.write(date)
                    st.success('Upload erfolgreich')
                    with st.spinner('Reload in 3 seconds...'):
                        time.sleep(3)
                        st.cache_data.clear()
                        st.rerun()
            else:
                pass
        with col2:            
            if st.button('Restore Original'):
                st.write('Restoring...')
                # erstelle eine Kopie von Data/appData/MLGTP_org.xlsx und speichere Sie als Data/appData/MLGTP.xlsx
                with open(f'Data/appData/MLGT.xlsx', 'wb') as f:
                    f.write(open(org_file, 'rb').read())
                    #save date in a locl json file
                    with open('Data/appData/lastUpload.json', 'w') as f:
                        f.write(date)
                with st.spinner('Reload in 3 seconds...'):
                    time.sleep(3)
                    st.cache_data.clear()
                    st.rerun()
        
def pageStellplatzverwaltung():
    dfOrders,masterdata,dfBIN, filenameOrg, df_alleVerbotenenSKU= loadDF()
    datenUpload(masterdata,dfBIN)

    #----- Lade Stellplatzdaten -----
    col1, col2 = st.columns(2)
    with col1:
        st.write('Stellplatzdaten: ',filenameOrg)
    with col2:
        if  st.button('Reload', key='aktualisieren'):
            with st.spinner('Reload in 3 seconds...'):
                time.sleep(3)
                st.cache_data.clear()
                st.rerun()
        
    dfBIN['MATNR'] = dfBIN['MATNR'].astype(str)
    dfBIN['MATNR'] = dfBIN['MATNR'].str[:8]

    #----- Filter nach Datum -----
    col1, col2 = st.columns(2)
    with col1:
        seldate = st.date_input('Datum')
    with col2:
        sel_range = st.slider('Wähle einen Bedarfszeitraum', min_value=1, max_value=14, value=5, step=1)
        sel_range = heute - datetime.timedelta(days=sel_range)
        
    

    dfBedarfSKU = FilterNachDatum(sel_range,heute,dfOrders)

    

    
    st.write('Bedarfszeitraum: ' + str(sel_range) + ' bis ' + str(heute))
    #st.data_editor(dfBedarfSKU)
    
    verbot = pd.read_csv('Data/df_verbot.csv')
    # if verbot nicht leer dann values aus MATNR und  st.warning('Verbotene SKUs in TN1' + MATNR)
    if verbot.empty:
        pass
    else:
        st.error('Verbotene SKUs in TN1! Sofort Korrigieren!')
        st.dataframe(verbot)

    def berechnungen(dfBedarfSKU):
        #st.data_editor(dfBIN)
        #-- Bedarf letzte 7 Tage ermitteln und Df für Figur erstellen
        dfOrg = dfBedarfSKU.copy()
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

        return dfBedarfSKU, dfOrg, dfBIN_TN, dfBIN_SN

    dfBedarfSKU, dfOrg, dfBIN_TN, dfBIN_SN = berechnungen(dfBedarfSKU)
    

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        nichtgepflegteSKU = st.toggle('Nicht gepflegte SKUs', key='nichtgepflegteSKU')
    with col2:
        stangenbedarf = st.toggle('Stangenbedarf', key='stangenbedarf')
    with col3:
        kartonbedarf = st.toggle('Kartonbedarf', key='kartonbedarf')
    with col4:
        heatmap = st.toggle('Heatmap', key='heatmap')
    img_strip = Image.open('Data/img/strip.png')   
    img_strip = img_strip.resize((1000, 15))     
    st.image(img_strip, use_column_width=True, caption='',)     
    
       

    #----- Filter nach Stellplatz -----                              
    if nichtgepflegteSKU:
        with st.expander('Nicht Gepflegte SKUs',expanded=True):
            df_nichtGepflegt_SN = dfBedarfSKU[dfBedarfSKU['LGPLA_SN'] == 'Kein Stellplatz in SN1']
            # drop duplicates in MaterialNumber
            df_nichtGepflegt_SN = df_nichtGepflegt_SN.drop_duplicates(subset=['MaterialNumber'])
            df_nichtGepflegt_TN = dfBedarfSKU[dfBedarfSKU['LGPLA_TN'] == 'Kein Stellplatz in TN1']
            # drop duplicates in MaterialNumber
            df_nichtGepflegt_TN = df_nichtGepflegt_TN.drop_duplicates(subset=['MaterialNumber'])
            st.warning('Nicht gepflegte SKUs in SN1')
            #sort by CorrespondingMastercases
            df_nichtGepflegt_SN = df_nichtGepflegt_SN.sort_values(by=['CorrespondingMastercases'], ascending=False)
            st.dataframe(df_nichtGepflegt_SN)
            st.warning('Nicht gepflegte SKUs in TN1')
            df_nichtGepflegt_TN = pd.merge(df_nichtGepflegt_TN, df_alleVerbotenenSKU, how='left', left_on='MaterialNumber', right_on='MaterialNumber')
            #sort by CorrespondingMastercases
            df_nichtGepflegt_TN = df_nichtGepflegt_TN.sort_values(by=['CorrespondingOuters'], ascending=False)
            st.dataframe(df_nichtGepflegt_TN)
    if kartonbedarf:
        with st.expander('Kartonbedarf SN1',expanded=True):
         
            # filter CorrospondingMastercases > 0
            dfBedarfSKU_SN = dfBedarfSKU[dfBedarfSKU['CorrespondingMastercases'] > 0]
            # Lieferscheine = Zähle MaterialNumber in dfBedarfSKU_SN

            # drop PlannedDate and SapOrderNumber
            dfBedarfSKU_SN = dfBedarfSKU_SN[['MaterialNumber','CorrespondingMastercases','LGPLA_SN']]
            # group by MaterialNumber and sum CorrespondingMastercases
            dfBedarfSKU_SN = dfBedarfSKU_SN.groupby(['MaterialNumber','LGPLA_SN']).sum().reset_index()
            # sort by CorrespondingMastercases
            dfBedarfSKU_SN = dfBedarfSKU_SN.sort_values(by=['CorrespondingMastercases'], ascending=False)

            # Count Positionen 
            material_daily_count_sku = dfBedarfSKU.groupby(['MaterialNumber', 'PlannedDate']).size().unstack(fill_value=0)

            # Umwandeln der Gruppierung in einen DataFrame
            material_daily_count_sku_df = material_daily_count_sku.reset_index()

            # Zusammenführen des Ergebnisses mit dfBedarfSKU_SN
            dfBedarfSKU_SN = pd.merge(dfBedarfSKU_SN, material_daily_count_sku_df, on="MaterialNumber", how="left")


            st.data_editor(dfBedarfSKU_SN, key='my_editorSNBedarf')
            #save to excel
            dfBedarfSKU.to_excel('Data/dfBedarfSKU.xlsx', index=False)
            fig = px.bar(dfBedarfSKU_SN, x='LGPLA_SN', y='CorrespondingMastercases', color='CorrespondingMastercases',hover_data=['MaterialNumber'])
            fig.update(layout_coloraxis_showscale=False)
            fig.update_layout(yaxis=dict(visible=False))
            st.plotly_chart(fig, use_container_width=True)
    if stangenbedarf:    
        with st.expander('Stangenbedarf TN1',expanded=True):

            # filter CorrospondingMastercases > 0
            dfBedarfSKU_TN = dfBedarfSKU[dfBedarfSKU['CorrespondingOuters'] > 0]
            # drop PlannedDate and SapOrderNumber
            dfBedarfSKU_TN = dfBedarfSKU_TN[['MaterialNumber','CorrespondingOuters','LGPLA_TN']]
            # group by MaterialNumber and sum CorrespondingMastercases
            dfBedarfSKU_TN = dfBedarfSKU_TN.groupby(['MaterialNumber','LGPLA_TN']).sum().reset_index()
            # sort by CorrespondingMastercases
            dfBedarfSKU_TN = dfBedarfSKU_TN.sort_values(by=['CorrespondingOuters'], ascending=False)
            material_daily_count_sku2 = dfBedarfSKU.groupby(['MaterialNumber', 'PlannedDate']).size().unstack(fill_value=0)

            # Umwandeln der Gruppierung in einen DataFrame
            material_daily_count_sku_df2 = material_daily_count_sku2.reset_index()

            # Zusammenführen des Ergebnisses mit dfBedarfSKU_SN
            dfBedarfSKU_TN = pd.merge(dfBedarfSKU_TN, material_daily_count_sku_df2, on="MaterialNumber", how="left")
            #dfBedarfSKU_TN = pd.merge(dfBedarfSKU_TN, df_alleVerbotenenSKU, how='left', left_on='MaterialNumber', right_on='MaterialNumber')


            st.data_editor(dfBedarfSKU_TN, key='my_editorTNBedarf')
            fig = px.bar(dfBedarfSKU_TN, x='LGPLA_TN', y='CorrespondingOuters', color='CorrespondingOuters',hover_data=['MaterialNumber'])
            fig.update(layout_coloraxis_showscale=False)
            fig.update_layout(yaxis=dict(visible=False))
            st.plotly_chart(fig, use_container_width=True)

    def karton_heatmap(dfBedarf):

        LagerNeu_path = 'Data/appData/LagerNeu.xlsx'
        image_path = 'Data/appData/Lager.png'

        LagerNeu = pd.read_excel(LagerNeu_path)

        # Bereinigen Sie die LagerNeu DataFrame
        LagerNeu_clean = LagerNeu.drop(columns=[col for col in LagerNeu if col.startswith('Unnamed:')])

        # Zusammenführen der DataFrames basierend auf dem Lagerplatz
        merged_data = pd.merge(dfBedarf, LagerNeu_clean, left_on='LGPLA_SN', right_on='Stellplatz', how='left')

        # Entfernen von Zeilen ohne Koordinaten
        heatmap_data = merged_data.dropna(subset=['X', 'Y'])

        # Normalisierung der 'CorrespondingMastercases'
        max_cases = heatmap_data['CorrespondingMastercases'].max()
        heatmap_data['NormalizedCases'] = heatmap_data['CorrespondingMastercases'] / max_cases

        # Funktion zur Zuweisung von Farben basierend auf normalisierten Fällen
        def get_color(value):
            return plt.cm.hot(value)

        # Laden des Lagerbildes
        warehouse_image = Image.open(image_path)

        # Erstellen des Plots
        plt.figure(figsize=(16, 8))
        plt.imshow(warehouse_image)

        # Heatmap über das Lagerbild legen
        for index, row in heatmap_data.iterrows():
            plt.gca().add_patch(plt.Rectangle((row['X'], row['Y']), 100, 100, color=get_color(row['NormalizedCases']), alpha=0.5))
            
            # Beschriftung hinzufügen über den Blöcken
            plt.text(row['X'], row['Y'] + 1, str(row['CorrespondingMastercases']), color='white', fontfamily='Montserrat', fontsize=12)

        plt.axis('off')
        fig = plt.gcf()
        st.pyplot(fig)


    if heatmap:
        dfBedarfSKU_SN = dfBedarfSKU[dfBedarfSKU['CorrespondingMastercases'] > 0]
        # Lieferscheine = Zähle MaterialNumber in dfBedarfSKU_SN
        dfBedarfSKU_SN['Lieferscheine'] = dfBedarfSKU_SN.groupby('MaterialNumber')['MaterialNumber'].transform('count')

        #dfBedarfSKU_SN['Lieferscheine'] = dfBedarfSKU.groupby(['MaterialNumber'])['MaterialNumber'].transform('count')

        # drop PlannedDate and SapOrderNumber
        dfBedarfSKU_SN = dfBedarfSKU_SN[['MaterialNumber','CorrespondingMastercases','LGPLA_SN','Lieferscheine']]
        karton_heatmap(dfBedarfSKU_SN)
    if st.button('Aktualisieren'):
        st.cache_data.clear()
        #rerun page
        st.experimental_rerun()

def seite():

    pageStellplatzverwaltung()


        

