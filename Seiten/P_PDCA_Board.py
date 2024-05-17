import pygwalker as pyg
import streamlit.components.v1 as components
from pygwalker.api.streamlit import StreamlitRenderer, init_streamlit_comm
from PIL import Image

import streamlit as st
import pandas as pd
from datetime import datetime
import pygwalker as pyg
import pandas as pd
import streamlit.components.v1 as components
import plotly.express as px
import hydralit_components as hc

from annotated_text import annotated_text, annotation
from Data_Class.MMSQL_connection import read_Table
import plotly.graph_objs as go
from Data_Class.AzureStorage_dev import get_blob_list_dev, get_file_dev
from io import BytesIO

def rename_duplicate_columns(df):
    cols = pd.Series(df.columns)
    for dup in cols[cols.duplicated()].unique(): 
        cols[cols[cols == dup].index.values.tolist()] = [dup + str(i) if i != 0 else dup for i in range(sum(cols == dup))]
    df.columns = cols
    return df

def rename_duplicate_values_in_first_row(df):
    first_row = df.iloc[0]
    for dup in first_row[first_row.duplicated()].unique(): 
        first_row[first_row[first_row == dup].index.values.tolist()] = [dup + '_' + str(i) if i != 0 else dup for i in range(sum(first_row == dup))]
    df.iloc[0] = first_row
    return df

# init_streamlit_comm()

''' BAT Colurs
#0e2b63 darkBlue
#004f9f MidBlue
#00b1eb LightBlue
#ef7d00 Orange
#ffbb00 Yellow
#ffaf47 Green
#afca0b lightGreen
#5a328a Purple
#e72582 Pink
'''
##### LOAD AND FILTER DATA #####
BATColurs = ['#0e2b63','#004f9f','#00b1eb','#ef7d00','#ffbb00','#ffaf47','#afca0b','#5a328a','#e72582']
@st.cache_data(show_spinner=False)
def load_data_Depot():

    df_depot = read_Table('prod_Kundenbestellungen')
    dfIssues_depot = read_Table('PAMS_SD_Issues')
        # Behandle df_Depot
    df_depot.PlannedDate = pd.to_datetime(df_depot.PlannedDate)
    df_depot['Packtag'] = df_depot.PlannedDate.dt.strftime('%d.%m.%Y')
    df_depot['Packtag'] = df_depot['Packtag'].astype(str)
    df_depot['Jahr'] = df_depot.PlannedDate.dt.strftime('%Y')
    df_depot['Wochentag'] = df_depot['PlannedDate'].dt.strftime('%A')
    df_depot['Woche'] = df_depot['PlannedDate'].dt.strftime('%V.%Y')
    df_depot['Monat'] = df_depot['PlannedDate'].dt.strftime('%m.%Y')
    df_depot.PlannedDate = df_depot.PlannedDate.dt.strftime('%d.%m.%Y')

    #Behandele dfIssues
    dfIssues_depot['Monat'] = dfIssues_depot['Datum gemeldet'].dt.strftime('%m.%Y')
    dfIssues_depot['Jahr'] = dfIssues_depot['Datum gemeldet'].dt.strftime('%Y')
    return df_depot, dfIssues_depot
@st.cache_data(show_spinner=False)
def load_data_CW():
    data = get_file_dev("CW_SDDS.xlsm")
    df_outbound = read_Table('PAMS_CW_SDDS_Outbound_Monitor')
    df_inbound = read_Table('PAMS_CW_SDDS_Inbound_Monitor')
    df_dds = get_file_dev('CW_DDS.xlsm')
    df_dds = pd.read_excel(BytesIO(df_dds), sheet_name='Logistik DE DDS')
    df_dds = df_dds.T
    df_dds = df_dds.iloc[:, :93]
    df_dds = rename_duplicate_values_in_first_row(df_dds)  # Aktualisiere die Werte in der ersten Zeile von df_dds
    #set the first row as the header
    df_dds.columns = df_dds.iloc[0]
    # rename column 1 to 'Date'
    df_dds.rename(columns={df_dds.columns[0]: 'Date',df_dds.columns[1]: 'Weekday'}, inplace=True)
    df_dds.reset_index(drop=True, inplace=True)
    df_dds = df_dds[6:]

    return df_outbound, df_inbound, df_dds
    
@st.cache_data(show_spinner=False)
def load_data_LC():
    try:
        data = get_file_dev("LC_SDDS.xlsm")
        df_outbound = read_Table('PAMS_LC_SDDS_Outbound_Monitor')
        df_inbound = read_Table('PAMS_LC_SDDS_Inbound_Monitor')
        
        df_dds = get_file_dev('LC_DDS.xlsm')
        #df_dds = None
        df_dds = pd.read_excel(BytesIO(df_dds), sheet_name='Logistik Bayreuth DDS')
        df_dds = df_dds.T

        df_dds.iloc[0, 0] = 'Date'
        df_dds.iloc[0] = df_dds.iloc[0].fillna('Leer')
        df_dds = rename_duplicate_values_in_first_row(df_dds)  # Aktualisiere die Werte in der ersten Zeile von df_dds

        df_dds.columns = df_dds.iloc[0]
        
        
        # # rename column 1 to 'Date'
        df_dds.rename(columns={df_dds.columns[0]: 'Date',df_dds.columns[1]: 'Weekday'}, inplace=True)
        # df_dds.reset_index(drop=True, inplace=True)
        df_dds = df_dds[5:]
        #save as csv to Data/con_backups/Quelle_PA_BLOBB
        df_dds.to_csv('Data/con_backups/Quelle_PA_BLOBB/LC_DDS.csv', index=False)
        return df_outbound, df_inbound, df_dds
    except:
        df_outbound = pd.read_csv('Data/con_backups/Quelle_PA_BLOBB/Outbound_Monitor.csv')
        df_inbound = pd.read_csv('Data/con_backups/Quelle_PA_BLOBB/Inbound_Monitor.csv')
        st.warning('Fehler beim Laden der 2024_Ladeplan_SDDS_FG_GER_Domestic.xlsm Datei. Bitte kontaktieren Sie den Administrator.')
        st.error('Die Angezeigten Daten sind Veraltet')
        return df_outbound, df_inbound, None    
@st.cache_data(show_spinner=False)
def load_data_SFG():
    try:
        data = get_file_dev("SFG_SDDS.xlsx")
        df_outbound = read_Table('PAMS_SFG_SDDS_Outbound_Monitor')
        df_inbound = read_Table('PAMS_SFG_SDDS_Inbound_Monitor')
        df_dds = pd.read_excel(BytesIO(data), sheet_name='SFG_DDS 24',engine='openpyxl')  

        df_dds = df_dds.T

        df_dds.iloc[0, 0] = 'Date'
        df_dds.iloc[0] = df_dds.iloc[0].fillna('Leer')
        df_dds = rename_duplicate_values_in_first_row(df_dds)  # Aktualisiere die Werte in der ersten Zeile von df_dds

        df_dds.columns = df_dds.iloc[0]
        
        
        # # # rename column 1 to 'Date'
        df_dds.rename(columns={df_dds.columns[0]: 'Date',df_dds.columns[1]: 'Weekday'}, inplace=True)
        df_dds.reset_index(drop=True, inplace=True)
        df_dds = df_dds[5:]
        #df_outbound = None

        return df_outbound, df_inbound, df_dds
    except:
        df_outbound = pd.read_csv('Data/con_backups/Quelle_PA_BLOBB/Outbound_Monitor.csv')
        df_inbound = pd.read_csv('Data/con_backups/Quelle_PA_BLOBB/Inbound_Monitor.csv')
        st.warning('Fehler beim Laden der 2024_Ladeplan_SDDS_FG_GER_Domestic.xlsm Datei. Bitte kontaktieren Sie den Administrator.')
        st.error('Die Angezeigten Daten sind Veraltet')
        return df_outbound, df_inbound, None    
@st.cache_data(show_spinner=False)
def load_img_logos():
    cw_img = Image.open('Data/img/Domestic_LOGO.png', mode='r')  
    lc_img = Image.open('Data/img/LC_LOGO.png', mode='r')  
    diet_img = Image.open('Data/img/DIET_LOGO.png', mode='r')  
    caf_img = Image.open('Data/img/C&F_LOGO.png', mode='r')  
    leaf_img = Image.open('Data/img/LEAF_LOGO.png', mode='r')  
    outbound_img = Image.open('Data/img/Outbound.png', mode='r')
    inbound_img = Image.open('Data/img/Inbound.png', mode='r')
    return cw_img, lc_img, diet_img, caf_img, leaf_img, outbound_img, inbound_img

    
def filter_data(df, sel_weekRange, useCol, ref_col):
    
    if ref_col != 'PlannedDate' or ref_col != 'Datum gemeldet':
    
        df[ref_col] = pd.to_datetime(df[ref_col],format='mixed', errors='coerce')   
        df['Wochentag'] = df[ref_col].dt.strftime('%A')
        df['Woche'] = df[ref_col].dt.strftime('%V.%Y')
        df['Monat'] = df[ref_col].dt.strftime('%m.%Y')
        df['Jahr'] = df[ref_col].dt.strftime('%Y')
        
    
    df = df[df[useCol] == sel_weekRange]
    return df  

def showTabels(df_depot: pd, dfIssues_depot: pd, ):
    ''' Zeige Tabellen als Dataframe an'''
    st.write('DF Depot')
    st.dataframe(df_depot)
    st.write('DF Issues')
    st.dataframe(dfIssues_depot)

def cw_loadingperformance(df_CW_out, df_in_CW):
    
    sum_of_loadings = df_CW_out['Destination City'].count()
    # zähle Verladen + PGI' in 'Status Verladung '
    sum_loaded = df_CW_out[df_CW_out['Status Verladung'] == 'Verladen + PGI']['Status Verladung'].count()
    def time_to_timedelta(t):
        return pd.Timedelta(hours=t.hour, minutes=t.minute, seconds=t.second)
    
    # filter ist null 0 or NaN or empty df_CW_out['Wartezeit bis Verladebeginn']
    df_CW_out = df_CW_out[df_CW_out['On time innerhalb 2,5 Std. (Automatisch berechnet) '].notnull()]
    df_CW_out = df_CW_out[df_CW_out['On time innerhalb 2,5 Std. (Automatisch berechnet) '] != '0']
    df_CW_out = df_CW_out[df_CW_out['On time innerhalb 2,5 Std. (Automatisch berechnet) '] != '']
    # to datetime
    df_CW_out['On time innerhalb 2,5 Std. (Automatisch berechnet) '] = pd.to_datetime(df_CW_out['On time innerhalb 2,5 Std. (Automatisch berechnet) '], errors='coerce').dt.time
    df_CW_out['On time innerhalb 2,5 Std. (Automatisch berechnet) '] = df_CW_out['On time innerhalb 2,5 Std. (Automatisch berechnet) '].apply(time_to_timedelta)
    out_time = df_CW_out['On time innerhalb 2,5 Std. (Automatisch berechnet) '].mean().seconds / 60
    lp_cw = round(out_time) 
    
    # ermittle ob innerhalb von 150 Minuten verladen wurde und setze True oder False
    df_CW_out['In time'] = df_CW_out['On time innerhalb 2,5 Std. (Automatisch berechnet) '] <= pd.Timedelta(minutes=150)   
    
    outbound_time = df_CW_out['In time'].sum() / sum_of_loadings * 100
    in_time_loded_total = df_CW_out['In time'].sum()
    outbound_time = round(outbound_time,1)
    
    def plotly_loadingTime_CW(df_CW_out):
        # Entferne Zeilen mit NaN-Werten
        df_CW_out = df_CW_out.dropna(subset=['In time'])

        # df_CW_out group by Date and the mean of 'On time innerhalb 2,5 Std. (Automatisch berechnet) '
        df_CW_out = df_CW_out.groupby('Ist Datum').agg({'On time innerhalb 2,5 Std. (Automatisch berechnet) ': 'mean'}).reset_index()
        # Erstelle ein gestapeltes Flächendiagramm
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df_CW_out['Ist Datum'], y=df_CW_out['On time innerhalb 2,5 Std. (Automatisch berechnet) '], name='Blocklager Paletten ist', mode='lines', fill='tozeroy', line=dict(width=0.5, color='#0e2b63')))
        #fig.add_trace(go.Scatter(x=df_CW_dds['Date'], y=df_CW_dds['Kumulatives Regalager'], name='Regalager Paletten ist', mode='lines', fill='tonexty', line=dict(width=0.5, color='#ef7d00')))

        # # Füge Beschriftungen nur alle drei Tage hinzu
        # df_CW_dds['Beschriftung'] = pd.to_datetime(df_CW_dds['Date']).dt.day % 3 == 0
        # df_label = df_CW_dds[df_CW_dds['Beschriftung']]

        # fig.add_trace(go.Scatter(
        #     x=df_label['Date'],
        #     y=df_label['Kumulatives Regalager'],
        #     mode='text',
        #     text=df_label['Kumulatives Regalager'],
        #     textposition="top center",
        #     textfont=dict(
        #         color="#000000"
        #     ),
        #     showlegend=False
        # ))

        # # Ändere das Layout
        # fig.update_layout(
        #     xaxis_title=None,
        #     yaxis_title='Anzahl Paletten',
        #     title='CW (Geb7) Lagerbestand in Paletten',
        #     font=dict(
        #         family="Montserrat",
        #         size=12,
        #         color="#7f7f7f"
        #     ),
        #     legend=dict(
        #         title='',
        #         orientation="h",
        #         yanchor="bottom",
        #         y=1.02,
        #         xanchor="right",
        #         x=1
        #     )
        # )
        return fig
    
    
    
    
    try:
        # Konvertiere 'Wartezeit bis Entladebeginn' in timedelta-Objekte
        # to datetime
        df_in_CW['Wartezeit bis Entladebeginn'] = pd.to_datetime(df_in_CW['Wartezeit bis Entladebeginn'])
        df_in_CW['Entladungszeit'] = pd.to_datetime(df_in_CW['Entladungszeit'])
        df_in_CW['Wartezeit bis Entladebeginn'] = df_in_CW['Wartezeit bis Entladebeginn'].apply(time_to_timedelta)
        #Entladungszeit
        df_in_CW['Entladungszeit'] = df_in_CW['Entladungszeit'].apply(time_to_timedelta)
        # Berechne die Gesamtzeit in neue Spalte Entladegesamtzeit
        df_in_CW['Entladegesamtzeit'] = df_in_CW['Wartezeit bis Entladebeginn'] + df_in_CW['Entladungszeit']
        # Berechne den Durchschnitt der Entladegesamtzeit
        inb_time = df_in_CW['Entladegesamtzeit'].mean().seconds / 60
        # runde auf minuten
        inb_time = round(inb_time)
    except:
        inb_time = 0
        
        
    
    fig = plotly_loadingTime_CW(df_CW_out)
    
    return lp_cw,in_time_loded_total ,fig, inb_time, sum_of_loadings
    #group by 'Ist Datum', Destination City, count 'On time innerhalb 2,5 Std. (Automatisch berechnet) '

def LC_loadingperformance(df_out_LC, df_in_LC):
    
    sum_of_loadings = df_out_LC['SCI'].count()
    
    # zähle Verladen + PGI' in 'Status Verladung '
    sum_loaded = df_out_LC[df_out_LC['Loaded at Bayreuth (Documents finished)'] != None]['Loaded at Bayreuth (Documents finished)'].count()
    # zähle Vorgestellt in 'Status Verladung '
    def time_to_timedelta(t):
        return pd.Timedelta(hours=t.hour, minutes=t.minute, seconds=t.second)
    try:
        df_out_LC = df_out_LC[df_out_LC['Verladungszeit Log-In'].notnull()]
        df_out_LC = df_out_LC[df_out_LC['Verladungszeit Log-In'] != '0']
        df_out_LC = df_out_LC[df_out_LC['Verladungszeit Log-In'] != '']
        # to datetime
        df_out_LC['Verladungszeit Log-In'] = pd.to_datetime(df_out_LC['Verladungszeit Log-In'])
        df_out_LC['Verladungszeit Log-In'] = df_out_LC['Verladungszeit Log-In'].apply(time_to_timedelta)
        out_time = df_out_LC['Verladungszeit Log-In'].mean().seconds / 60
        out_time = round(out_time)
    except:
        out_time = 0
    
    # ermittle ob innerhalb von 150 Minuten verladen wurde und setze True oder False
    df_out_LC['In time'] = df_out_LC['Verladungszeit Log-In'] <= pd.Timedelta(minutes=150)   
    
    outbound_time = df_out_LC['In time'].sum() / sum_of_loadings * 100
    in_time_loded_total = df_out_LC['In time'].sum()
    lp_lc = round(outbound_time,1)
    fig = px.bar(df_out_LC, x='Destination City', y='Verladungszeit Log-In', color='In time', title='Verladezeit in Minuten', labels={'Destination City': 'Stadt', 'Verladungszeit Log-In': 'Verladezeit in Minuten', 'In time': 'Innerhalb von 150 Minuten verladen'})

    try:
        # Konvertiere 'Wartezeit bis Entladebeginn' in timedelta-Objekte
        # to datetime
        df_in_LC['Automatisch berechnet.2'] = pd.to_datetime(df_in_LC['Automatisch berechnet.2'])
        df_in_LC['Automatisch berechnet.2'] = df_in_LC['Automatisch berechnet.2'].apply(time_to_timedelta)
        #Entladungszeit
        inb_time = df_in_LC['Automatisch berechnet.2'].mean().seconds / 60
        # runde auf minuten
        inb_time = round(inb_time)
    except:
        inb_time = 0
        
    sum_of_loadings = df_in_LC['Datum'].count()
    
    sum_GR = df_in_LC['Echtzeit Büro.1'].count()
    # zähle FG in 
    sum_unloadedFG = df_in_LC['Anzahl Paletten'].count()
    # zähle in in Vorbereitung 'Status Verladung '
    sum_unloadedWMS = df_in_LC['Anzahl Paletten.1'].count()
    
    
    return lp_lc,in_time_loded_total ,fig, inb_time, sum_of_loadings
    #group by 'Ist Datum', Destination City, count 'On time innerhalb 2,5 Std. (Automatisch berechnet) '

def SFG_loadingperformance(df_CW_out, df_in_CW):
    
    sum_of_loadings = df_CW_out['Destination City'].count()
    # zähle Verladen + PGI' in 'Status Verladung '
    sum_loaded = df_CW_out[df_CW_out['Status Verladung'] == 'Verladen + PGI']['Status Verladung'].count()
    def time_to_timedelta(t):
        return pd.Timedelta(hours=t.hour, minutes=t.minute, seconds=t.second)
    
    # filter ist null 0 or NaN or empty df_CW_out['Wartezeit bis Verladebeginn']
    df_CW_out = df_CW_out[df_CW_out['Dauer von Ankuft  bis Ladeende'].notnull()]
    df_CW_out = df_CW_out[df_CW_out['Dauer von Ankuft  bis Ladeende'] != '0']
    df_CW_out = df_CW_out[df_CW_out['Dauer von Ankuft  bis Ladeende'] != '']
    #prüfe ob Fehlerhafte werte (nicht Zeit) in der Spalte sind
    df_CW_out = df_CW_out[df_CW_out['Dauer von Ankuft  bis Ladeende'].str.contains(':')]
    # Gebe aus wie viele Zeilen entfernt wurden
    st.write('Fehlerhafte Werte in der Spalte Dauer von Ankuft  bis Ladeende: ', sum_of_loadings - df_CW_out['Destination City'].count())
    
    # to datetime
    df_CW_out['On time innerhalb 2,5 Std. (Automatisch berechnet) '] = pd.to_datetime(df_CW_out['On time innerhalb 2,5 Std. (Automatisch berechnet) '], errors='coerce').dt.time
    df_CW_out['On time innerhalb 2,5 Std. (Automatisch berechnet) '] = df_CW_out['On time innerhalb 2,5 Std. (Automatisch berechnet) '].apply(time_to_timedelta)
    out_time = df_CW_out['On time innerhalb 2,5 Std. (Automatisch berechnet) '].mean().seconds / 60
    lp_cw = round(out_time) 
    
    # ermittle ob innerhalb von 150 Minuten verladen wurde und setze True oder False
    df_CW_out['In time'] = df_CW_out['On time innerhalb 2,5 Std. (Automatisch berechnet) '] <= pd.Timedelta(minutes=150)   
    
    outbound_time = df_CW_out['In time'].sum() / sum_of_loadings * 100
    in_time_loded_total = df_CW_out['In time'].sum()
    outbound_time = round(outbound_time,1)
    fig = px.bar(df_CW_out, x='Destination City', y='On time innerhalb 2,5 Std. (Automatisch berechnet) ', color='In time', title='Verladezeit in Minuten', labels={'Destination City': 'Stadt', 'On time innerhalb 2,5 Std. (Automatisch berechnet) ': 'Verladezeit in Minuten', 'In time': 'Innerhalb von 150 Minuten verladen'})

    try:
        # Konvertiere 'Wartezeit bis Entladebeginn' in timedelta-Objekte
        # to datetime
        df_in_CW['Wartezeit bis Entladebeginn'] = pd.to_datetime(df_in_CW['Wartezeit bis Entladebeginn'])
        df_in_CW['Entladungszeit'] = pd.to_datetime(df_in_CW['Entladungszeit'])
        df_in_CW['Wartezeit bis Entladebeginn'] = df_in_CW['Wartezeit bis Entladebeginn'].apply(time_to_timedelta)
        #Entladungszeit
        df_in_CW['Entladungszeit'] = df_in_CW['Entladungszeit'].apply(time_to_timedelta)
        # Berechne die Gesamtzeit in neue Spalte Entladegesamtzeit
        df_in_CW['Entladegesamtzeit'] = df_in_CW['Wartezeit bis Entladebeginn'] + df_in_CW['Entladungszeit']
        # Berechne den Durchschnitt der Entladegesamtzeit
        inb_time = df_in_CW['Entladegesamtzeit'].mean().seconds / 60
        # runde auf minuten
        inb_time = round(inb_time)
    except:
        inb_time = 0
    
    
    
    return lp_cw,in_time_loded_total ,fig, inb_time, sum_of_loadings
    #group by 'Ist Datum', Destination City, count 'On time innerhalb 2,5 Std. (Automatisch berechnet) '





def Lagerbestand (df_dds_cw, df_dds_lc, df_dds_sfg, sel_stock):
    img = Image.open('Data/img/Domestic_LOGO.png', mode='r')  


    def plotly_warehouse_stocks_CW(df_CW_dds):
        # Entferne Zeilen mit NaN-Werten
        df_CW_dds = df_CW_dds.dropna(subset=['Blocklager Paletten ist', 'Regalager Paletten ist'])

        # Berechne kumulative Werte für das gestapelte Diagramm
        df_CW_dds['Kumulatives Blocklager'] = df_CW_dds['Blocklager Paletten ist']
        df_CW_dds['Kumulatives Regalager'] = df_CW_dds['Blocklager Paletten ist'] + df_CW_dds['Regalager Paletten ist']

        # Erstelle ein gestapeltes Flächendiagramm
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df_CW_dds['Date'], y=df_CW_dds['Kumulatives Blocklager'], name='Blocklager Paletten ist', mode='lines', fill='tozeroy', line=dict(width=0.5, color='#0e2b63')))
        fig.add_trace(go.Scatter(x=df_CW_dds['Date'], y=df_CW_dds['Kumulatives Regalager'], name='Regalager Paletten ist', mode='lines', fill='tonexty', line=dict(width=0.5, color='#ef7d00')))

        # Füge Beschriftungen nur alle drei Tage hinzu
        df_CW_dds['Beschriftung'] = pd.to_datetime(df_CW_dds['Date']).dt.day % 3 == 0
        df_label = df_CW_dds[df_CW_dds['Beschriftung']]

        fig.add_trace(go.Scatter(
            x=df_label['Date'],
            y=df_label['Kumulatives Regalager'],
            mode='text',
            text=df_label['Kumulatives Regalager'],
            textposition="top center",
            textfont=dict(
                color="#000000"
            ),
            showlegend=False
        ))

        # Ändere das Layout
        fig.update_layout(
            xaxis_title=None,
            yaxis_title='Anzahl Paletten',
            title='CW (Geb7) Lagerbestand in Paletten',
            font=dict(
                family="Montserrat",
                size=12,
                color="#7f7f7f"
            ),
            legend=dict(
                title='',
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        return fig

    def plotly_warehouse_stocks_LC(df_dds):
        df_dds = df_dds.dropna(subset=['Zigaretten (ZFG100000)'])
        df_dds = df_dds[df_dds['Zigaretten (ZFG100000)'] != 0]

        columns_prod_mat = [col for col in df_dds.columns if 'Produktionsmaterialien' in col]
        summeWMS_filtered = df_dds[columns_prod_mat].sum(axis=1)

        # Berechne SummeFG (Summe der Fertigwaren nach Abzug des GEW Bestand)
        columns_summeFG = ['Zigaretten (ZFG100000)', 'Zigarillos (ZFG110000)', 'OTP (ZFG130000)']
        summeFG_filtered = df_dds[columns_summeFG].sum(axis=1) - df_dds['GEW Bestand ']

        # Erstelle einen DataFrame für das Diagramm
        sankey_data_filtered = pd.DataFrame({
            'Date': df_dds['Date'],
            'SummeWMS': summeWMS_filtered,
            'SummeFG': summeFG_filtered,
            'GEW Bestand': df_dds['GEW Bestand ']
        })

        df_dds = sankey_data_filtered
        df_dds['Total'] = df_dds['SummeWMS'] + df_dds['SummeFG'] + df_dds['GEW Bestand']

        # Erstelle ein gestapeltes Flächendiagramm
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df_dds['Date'], y=df_dds['GEW Bestand'], name='GEW Bestand', mode='lines', fill='tozeroy', line=dict(width=0.5, color='#00b1eb')))
        fig.add_trace(go.Scatter(x=df_dds['Date'], y=df_dds['SummeWMS'] + df_dds['GEW Bestand'], name='SummeWMS', mode='lines', fill='tonexty', line=dict(width=0.5, color='#0e2b63')))
        fig.add_trace(go.Scatter(x=df_dds['Date'], y=df_dds['Total'], name='SummeFG', mode='lines', fill='tonexty', line=dict(width=0.5, color='#ef7d00')))

        # Füge die Gesamtsumme als Datenbeschriftung hinzu und zeige sie nur alle drei Tage
        df_dds['Label'] = pd.to_datetime(df_dds['Date']).dt.day % 3 == 0
        df_label = df_dds[df_dds['Label']]

        fig.add_trace(go.Scatter(
            x=df_label['Date'],
            y=df_label['Total'],
            mode='text',
            text=df_label['Total'],
            textposition="top center",
            textfont=dict(
                color="#000000"
            ),
            showlegend=False
        ))

        # Ändere das Layout
        fig.update_layout(
            xaxis_title=None,
            yaxis_title='Anzahl Paletten',
            title='Lagerbestand der letzten 5 Werktage',
            font=dict(
                family="Montserrat",
                size=12,
                color="#7f7f7f"
            ),
            legend=dict(
                title='',
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )

        return fig
     
    def plotly_warehouse_stocks_DIET(df_dds):
        fig = go.Figure()
        df_dds = df_dds.dropna(subset=['PMD '])
        #drop if is "0"
        df_dds = df_dds[df_dds['PMD '] != 0]

        fig.add_trace(go.Scatter(x=df_dds['Date'], y=df_dds['PMD '], name='DIET Bestand', mode='lines', fill='tozeroy', line=dict(width=0.5, color='#0e2b63')))
                # Füge Beschriftungen nur alle drei Tage hinzu
        df_dds['Beschriftung'] = pd.to_datetime(df_dds['Date']).dt.day % 3 == 0
        df_label = df_dds[df_dds['Beschriftung']]

        fig.add_trace(go.Scatter(
            x=df_label['Date'],
            y=df_label['PMD '],
            text=df_label['PMD '],
            mode='text',
            textposition="top center",
            textfont=dict(
                color="#000000"
            ),
            showlegend=False
        ))

        
        fig.update_layout(
            xaxis_title=None,
            yaxis_title='Anzahl Paletten',
            title='DIET (Geb1) Lagerbestand in Paletten',
            font=dict(
                family="Montserrat",
                size=12,
                color="#7f7f7f"
            ),
            legend=dict(
                title='',
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        return fig

    def plotly_warehouse_stocks_CAF(df_dds):

        df_dds['Date'] = pd.to_datetime(df_dds['Date'], errors='coerce').dt.date

        df_dds['Date'] = pd.to_datetime(df_dds['Date'])

        # Berechne das aktuelle Datum
        current_date = pd.Timestamp(datetime.date.today())

        # Filtere df_dds basierend auf 'Date'
        df_dds = df_dds[df_dds['Date'] <= current_date]
        # Filtere df_dds.Date zwischen heute und - 5 Werktage
        df_dds = df_dds[df_dds['Date'] <= current_date]
        df_dds = df_dds[df_dds['Date'] >= (current_date - datetime.timedelta(days=5))]
        
        fig = go.Figure()
        fig.add_trace(go.Bar(x=df_dds['Date'], y=df_dds['C & F - Paletten'], name='C & F - Paletten', marker_color='#0e2b63', text=df_dds['C & F - Paletten'], textposition='auto'))

        fig.update_layout(
            barmode='relative',
            #xaxis={'categoryorder':'total descending', 'type': 'category'},
            xaxis_title=None,
            yaxis_title='Anzahl Paletten',
            title='Lagerbestand der letzten 5 Werktage',
            font=dict(
                family="Montserrat",
                size=12,
                color="#7f7f7f"
            ),
            legend=dict(
                title='',
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        return fig

    def plotly_warehouse_stocks_LEAF(df_dds):
        df_dds = df_dds.dropna(subset=['LEAF - Kartons'])
        fig = go.Figure()
        #fig.add_trace(go.Bar(x=df_dds['Date'], y=df_dds['LEAF - Kartons'], name='LEAF - Kartons', marker_color='#0e2b63', text=df_dds['LEAF - Kartons'], textposition='auto'))
        fig.add_trace(go.Scatter(x=df_dds['Date'], y=df_dds['LEAF - Kartons'], name='LEAF Bestand CS', mode='lines', fill='tonexty', line=dict(width=0.5, color='#ef7d00')))

        # Füge Beschriftungen nur alle drei Tage hinzu
        df_dds['Beschriftung'] = pd.to_datetime(df_dds['Date']).dt.day % 3 == 0
        df_label = df_dds[df_dds['Beschriftung']]

        fig.add_trace(go.Scatter(
            x=df_label['Date'],
            y=df_label['LEAF - Kartons'],
            mode='text',
            text=df_label['LEAF - Kartons'],
            textposition="top center",
            textfont=dict(
                color="#000000"
            ),
            showlegend=False
        ))
        fig.update_layout(
            xaxis_title=None,
            yaxis_title='Anzahl Karton',
            title='LEAF (Geb4) Lagerbestand in Karton',
            font=dict(
                family="Montserrat",
                size=12,
                color="#7f7f7f"
            ),
            legend=dict(
                title='',
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        return fig       

    # jeder wert in sel_stock wird geprüft und das jewilige Diagramm wird gezeichnet
    # wenn CW teil des arrays ist, wird das CW Diagramm gezeichnet
    if 'CW' in sel_stock:
        st.plotly_chart(plotly_warehouse_stocks_CW(df_dds_cw), use_container_width=True)
    if 'LC' in sel_stock:
        st.plotly_chart(plotly_warehouse_stocks_LC(df_dds_lc), use_container_width=True)
    if 'SFG LEAF' in sel_stock:
        st.plotly_chart(plotly_warehouse_stocks_LEAF(df_dds_sfg), use_container_width=True)
    if 'SFG DIET' in sel_stock:
        st.plotly_chart(plotly_warehouse_stocks_DIET(df_dds_sfg),use_container_width=True)
    if 'SFG CAF' in sel_stock:
        st.plotly_chart(plotly_warehouse_stocks_CAF(df_dds_sfg),use_container_width=True)

def main():
        
    with st.expander('Filter', expanded=False,):     
        
        df_depot, dfIssues_depot = load_data_Depot()
        df_out_CW, df_in_CW, df_dds_cw = load_data_CW()
        df_out_LC, df_in_LC , df_dds_lc= load_data_LC()
        df_out_SFG, df_in_SFG, df_dds_sfg = load_data_SFG()
        cw_img, lc_img, diet_img, caf_img, leaf_img, outbound_img, inbound_img = load_img_logos()
        col1, col2 = st.columns(2)
        with col1:
            sel_filter = st.radio(
            "Filtern nach:",
            ["Monat", 'Jahr' ],
            key="visibility",
            horizontal=True)  
            
            if sel_filter == 'Monat':
                dfMonth = df_depot.sort_values(by=['PlannedDate'], ascending=False)
                #select unique values in column Monat
                dfMonth = dfMonth['Monat'].unique()
                dfMonth_sorted = sorted(dfMonth, key=lambda x: (x.split('.')[1], x.split('.')[0]), reverse=True)
                sel_monthRange = st.selectbox('Wähle Monat', dfMonth_sorted)  
            
            if sel_filter == 'Jahr':
                dfYear = df_depot.sort_values(by=['PlannedDate'], ascending=False)
                #select unique values in column Monat
                dfYear = dfYear['Jahr'].unique()
                dfYear_sorted = sorted(dfYear, key=lambda x: (x.split('.')[1], x.split('.')[0]) if '.' in x else (x, x), reverse=True)
                sel_yearRange = st.selectbox('Wähle Jahr', dfYear_sorted)

            tabelle = st.checkbox('Tabellen einblenden')
        with col2:
            sel_Day_week = st.radio("Zeige in: ", ["Monaten","Jahren"], key="zeigeIn", horizontal=True)
            sel_stock = st.multiselect('Wähle Lagerbestand', ['CW', 'LC', 'SFG LEAF', 'SFG DIET', 'SFG CAF'], default=['CW'])
        if sel_Day_week == 'Monaten':
            sel_Day_week = 'Monat'
        if sel_Day_week == 'Jahren':
            sel_Day_week = 'Jahr'   
        

        if sel_filter == 'Monat':
            df_depot = filter_data(df_depot, sel_monthRange, 'Monat', 'PlannedDate')
            dfIssues_depot = filter_data(dfIssues_depot, sel_monthRange, 'Monat', 'Datum gemeldet')
            df_out_CW = filter_data(df_out_CW, sel_monthRange, 'Monat','Ist Datum')
            df_in_CW = filter_data(df_in_CW, sel_monthRange, 'Monat', 'Ist Datum')
            df_dds_cw = filter_data(df_dds_cw, sel_monthRange, 'Monat','Date')
            df_out_LC = filter_data(df_out_LC, sel_monthRange, 'Monat','Datum')
            df_in_LC = filter_data(df_in_LC, sel_monthRange, 'Monat','Datum')
            df_dds_lc = filter_data(df_dds_lc, sel_monthRange, 'Monat','Date')
            df_out_SFG = filter_data(df_out_SFG, sel_monthRange, 'Monat', 'Abholdatum Update')
            df_in_SFG = filter_data(df_in_SFG, sel_monthRange, 'Monat','Ist Datum\n(Tatsächliche Anlieferung)')
            df_dds_sfg = filter_data(df_dds_sfg, sel_monthRange, 'Monat','Date')
        if sel_filter == 'Jahr':
            df_depot = filter_data(df_depot, sel_yearRange, 'Jahr', 'PlannedDate')
            dfIssues_depot = filter_data(dfIssues_depot, sel_yearRange, 'Jahr', 'Datum gemeldet')
            df_out_CW = filter_data(df_out_CW, sel_yearRange, 'Jahr','Ist Datum')
            df_in_CW = filter_data(df_in_CW, sel_yearRange, 'Jahr', 'Ist Datum')
            df_out_LC = filter_data(df_out_LC, sel_yearRange, 'Jahr','Datum')
            df_in_LC = filter_data(df_in_LC, sel_yearRange, 'Jahr','Datum')
            df_dds_lc = filter_data(df_dds_lc, sel_yearRange, 'Jahr','Date')
            df_out_SFG = filter_data(df_out_SFG, sel_yearRange, 'Jahr', 'Abholdatum Update')
            df_in_SFG = filter_data(df_in_SFG, sel_yearRange, 'Jahr','Ist Datum\n(Tatsächliche Anlieferung)')
        
    
    cw_actual_total_stock = df_dds_cw['Blocklager Paletten ist'].iloc[-1] + df_dds_cw['Regalager Paletten ist'].iloc[-1]
    cw_max_stock = 2800
    cw_free_space = cw_max_stock - cw_actual_total_stock
    lc_actual_total_stock = df_dds_lc['Zigaretten (ZFG100000)'].iloc[-1] + df_dds_lc['Zigarillos (ZFG110000)'].iloc[-1]+ df_dds_lc['OTP (ZFG130000)'].iloc[-1]

    theme_bad = {'bgcolor': '#FFF0F0','title_color': 'red','content_color': 'red','icon_color': 'red', 'icon': 'fa fa-times-circle'}
    theme_neutral = {'bgcolor': '#f9f9f9','title_color': 'orange','content_color': 'orange','icon_color': 'orange', 'icon': 'fa fa-question-circle'}
    theme_good = {'bgcolor': '#EFF8F7','title_color': 'green','content_color': 'green','icon_color': 'green', 'icon': 'fa fa-check-circle'}
    lp_cw,in_time_loded_total ,fig, inb_time, sum_of_loadings = cw_loadingperformance(df_out_CW, df_in_CW)
    lp_lc,lc_in_time_loded_total ,lc_fig, lc_inb_time, lc_sum_of_loadings = LC_loadingperformance(df_out_LC, df_in_LC)
    with st.container(border=True):
        col1, col2, col3, col4, col5  = st.columns([1,1,1,1,1]) 
        
        ## CW
        with col1:
            st.image(cw_img, use_column_width=True)
            if lp_cw < 85:
                hc.info_card(title=f'{lp_cw} %', content='Loading performance',bar_value=lp_cw, theme_override=theme_bad)
            if lp_cw >= 85:
                hc.info_card(title=f'{lp_cw} %', content='Loading performance',bar_value=lp_cw, theme_override=theme_good)
        
            annotated_text(annotation(f'In Time {str(lp_cw)}','', "#50af47", font_family="Montserrat"),'  ',annotation(f'To Late {str(lp_cw)}','', "#ef7d00", font_family="Montserrat"))
            st.title("This is :red-background[red].")
            with st.popover('Loadingtimes'):
                st.plotly_chart(fig, use_container_width=True,config={'displayModeBar': False})
                st.plotly_chart(lc_fig, use_container_width=True,config={'displayModeBar': False})
            if inb_time < 85:
                hc.info_card(title=f'{inb_time} %', content='Unloading performance',bar_value=inb_time, theme_override=theme_bad)
            if inb_time >= 85:
                hc.info_card(title=f'{inb_time} %', content='Unloading performance',bar_value=inb_time, theme_override=theme_good)
            
            annotated_text(annotation(f'In Time {str(inb_time)}','', "#50af47", font_family="Montserrat"),'  ',annotation(f'To Late {str(inb_time)}','', "#ef7d00", font_family="Montserrat"))
    
        
        with col2:
            st.image(lc_img, use_column_width=True)
            if lp_lc < 85:
                hc.info_card(title=f'{lp_lc} %', content='Loading performance',bar_value=lp_lc, theme_override=theme_bad)
            if lp_lc >= 85:
                hc.info_card(title=f'{lp_lc} %', content='Loading performance',bar_value=lp_lc, theme_override=theme_good)
            
            st.metric('CW Stock: ', value = f"{cw_actual_total_stock}",delta=f"{cw_free_space} PAL Platz")
        ## CAF
    #     with col3:
    #         st.image(caf_img, use_column_width=True)
    #         if in_time < 85:
    #             hc.info_card(title=f'{in_time} %', content='Loading performance CW!',bar_value=in_time, theme_override=theme_bad)
    #         if in_time >= 85:
    #             hc.info_card(title=f'{in_time} %', content='Loading performance CW!',bar_value=in_time, theme_override=theme_good)
            
    #     ## DIET
    #     with col4:
    #         st.image(diet_img, use_column_width=True)
    #         if in_time < 85:
    #             hc.info_card(title=f'{in_time} %', content='Loading performance CW!',bar_value=in_time, theme_override=theme_bad)
    #         if in_time >= 85:
    #             hc.info_card(title=f'{in_time} %', content='Loading performance CW!',bar_value=in_time, theme_override=theme_good)
            
    #     ## LEAF
    #     with col5:
    #         st.image(leaf_img, use_column_width=True)
    #         if in_time < 85:
    #             hc.info_card(title=f'{in_time} %', content='Loading performance CW!',bar_value=in_time, theme_override=theme_bad)
    #         if in_time >= 85:
    #             hc.info_card(title=f'{in_time} %', content='Loading performance CW!',bar_value=in_time, theme_override=theme_good)
            

        
    # Lagerbestand(df_dds_cw, df_dds_lc, df_dds_sfg, sel_stock)  
    # if tabelle:
    #     showTabels(df_depot, dfIssues_depot)
    #     showTabels(df_out_CW, df_in_CW)
    #     showTabels(df_out_LC, df_in_LC)
    #     showTabels(df_out_SFG, df_in_SFG)
        
    