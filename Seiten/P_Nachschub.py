import streamlit as st
import pandas as pd
import datetime
#from Data_Class.SQL import sql_datenLadenLabel,sql_datenLadenOderItems,sql_datenLadenStammdaten,sql_datenLadenOder
#from Data_Class.DB_Daten_Agg import orderDatenAgg
import st_aggrid as ag
import plotly_express as px
from streamlit_option_menu import option_menu
from Data_Class.MMSQL_connection import read_Table , save_Table
import Data_Class.AzureStorage
from io import BytesIO



heute = datetime.date.today()
morgen = heute + datetime.timedelta(days=4)
heute_minus_10_tage =  datetime.timedelta(days=30)
def untersagte_sku_TN():
    df = read_Table('data_materialmaster-MaterialMasterUnitOfMeasures')
    dfText = read_Table('MaterialMasterMaterialDescriptions')

    # filtere nur nicht leer in InternationalArticleNumber
    df = df[df['InternationalArticleNumber'].notna()]

    # Kombiniere MaterialNumber und InternationalArticleNumber zu einem neuen Feld Check
    df['Check'] = df['MaterialNumber'].astype(str) + df['InternationalArticleNumber'].astype(str)

    # Filter nur Zeilen in denen es Duplikate in InternationalArticleNumber gibt
    df = df[df.duplicated(['Check'], keep=False)]
    save_Table(df, 'data_materialmaster_Duplicate_InternationalArticleNumber')
@st.cache_data
def loadDF():
    df = read_Table('OrderDatenLines')
    masterdata = read_Table('data_materialmaster_Duplicate_InternationalArticleNumber')
    return df, masterdata
    
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
        untersagte_sku_TN()        
    
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
    dfOrders,masterdata = loadDF()
    #st.data_editor(dfOrders)
    datenUpload()

    #----- Lade Stellplatzdaten -----
    dfBIN, filenameOrg = datenLadenBIN()
    st.write('Stellplatzdaten: ',filenameOrg)
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
    def berechnungen(dfBedarfSKU):
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

    #----- Filter nach Stellplatz -----                              

    with st.expander('Nicht Gepflegte SKUs',expanded=False):
        df_nichtGepflegt_SN = dfBedarfSKU[dfBedarfSKU['LGPLA_SN'] == 'Kein Stellplatz in SN1']
        # drop duplicates in MaterialNumber
        df_nichtGepflegt_SN = df_nichtGepflegt_SN.drop_duplicates(subset=['MaterialNumber'])
        df_nichtGepflegt_TN = dfBedarfSKU[dfBedarfSKU['LGPLA_TN'] == 'Kein Stellplatz in TN1']
        # drop duplicates in MaterialNumber
        df_nichtGepflegt_TN = df_nichtGepflegt_TN.drop_duplicates(subset=['MaterialNumber'])
        st.warning('Nicht gepflegte SKUs in SN1')
        st.dataframe(df_nichtGepflegt_SN)
        st.warning('Nicht gepflegte SKUs in TN1')
        st.dataframe(df_nichtGepflegt_TN)

    with st.expander('Alle Bestellpositionen',expanded=False):
        st.data_editor(dfBedarfSKU, key='my_editorALL')

    with st.expander('Kartonbedarf SN1',expanded=False):
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
        
    with st.expander('Stangenbedarf TN1',expanded=False):
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

    with st.expander('Rohdaten',expanded=False):
        st.data_editor(dfOrg, key='my_editorRohdaten')

    with st.expander('Verbotene SKUs',expanded=False):
        masterdata['MaterialNumber'] = masterdata['MaterialNumber'].str.replace('0000000000', '')
        #Filter masterdata['UnitOfMeasure'] == 'OUT'
        df_verbot = pd.merge(dfBIN_TN, masterdata, how='inner', left_on='MATNR', right_on='MaterialNumber')
        st.data_editor(df_verbot, key='my_editorStellplatzdaten')
        st.dataframe(dfBIN_TN)


def seite():

    pageStellplatzverwaltung()
    if st.button('Daten vom Server neu laden'):
        st.cache_data.clear()
        #rerun page
        st.experimental_rerun()

        

