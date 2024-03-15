import plotly.graph_objects as go
import streamlit as st
import pandas as pd
import numpy as np
import datetime
import streamlit_autorefresh as sar
from PIL import Image
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from io import BytesIO
import time

from annotated_text import annotated_text, annotation
from Data_Class.AzureStorage_dev import get_blob_list_dev, get_file_dev
from Data_Class.MMSQL_connection import read_Table
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

@st.cache_data
def load_data_CW():
    try:
        data = get_file_dev("CW_SDDS.xlsm")
        # #save as csv to Data/con_backups/Quelle_PA_BLOBB
        
        
        # df_outbound = pd.read_excel(BytesIO(data),sheet_name='Outbound_Monitor')
        # df_outbound.columns = df_outbound.iloc[0]
        # df_outbound = df_outbound[2:]
        df_outbound = read_Table('PAMS_CW_SDDS_Outbound_Monitor')
        
        
        
        # df_inbound = pd.read_excel(BytesIO(data), sheet_name='Inbound_Monitor')       
        # df_inbound.columns = df_inbound.iloc[0]
        # df_inbound = df_inbound[2:]
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
    
    except:
        df_outbound = pd.read_csv('Data/con_backups/Quelle_PA_BLOBB/Outbound_Monitor.csv')
        df_inbound = pd.read_csv('Data/con_backups/Quelle_PA_BLOBB/Inbound_Monitor.csv')
        st.warning('Fehler beim Laden der 2024_Ladeplan_SDDS_FG_GER_Domestic.xlsm Datei. Bitte kontaktieren Sie den Administrator.')
        st.error('Die Angezeigten Daten sind Veraltet')
        return df_outbound, df_inbound, None

@st.cache_data
def load_data_LC():
    try:
        data = get_file_dev("LC_SDDS.xlsm")
        # df_outbound = pd.read_excel(BytesIO(data),sheet_name='Outbound_Monitor')
        # df_outbound = rename_duplicate_values_in_first_row(df_outbound)  # Aktualisiere die Werte in der ersten Zeile von df_dds
        # df_outbound.columns = df_outbound.iloc[0]
        # df_outbound = df_outbound[1:]
        # #df_inbound = None
        # df_inbound = pd.read_excel(BytesIO(data), sheet_name='Inbound_Monitor')       
        # # df_inbound.columns = df_inbound.iloc[0]
        # df_inbound = df_inbound[2:]
        
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

@st.cache_data
def load_data_SFG():
    try:
        data = get_file_dev("SFG_SDDS.xlsx")

        # df_outbound = pd.read_excel(BytesIO(data),sheet_name='Outbound_Monitor')#,engine='openpyxl', sheet_name='Outbound_Monitor')

        # df_outbound = rename_duplicate_values_in_first_row(df_outbound)  # Aktualisiere die Werte in der ersten Zeile von df_dds
        # df_outbound.columns = df_outbound.iloc[0]
        # df_outbound = df_outbound[2:]    
        # # #df_inbound = None
        # df_inbound = pd.read_excel(BytesIO(data), sheet_name='Inbound_Monitor',engine='openpyxl')       
        # # # df_inbound.columns = df_inbound.iloc[0]
        # df_inbound = df_inbound[2:]
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
 
def anwesenheit():
     img = Image.open('Data/img/Mitarbeiter/micha.png', mode='r')
     st.image(img, width=200)

def truck_progress_png(progress, total):
    # Lade das Bild
    img = Image.open('Data/img/truck.png')

    # Berechne den Prozentsatz des Fortschritts
    percentage = (progress / total) * 100

    # Erstelle eine Figur mit transparentem Hintergrund
    fig, ax = plt.subplots(figsize=(35, 11))
    fig.patch.set_alpha(0)

    # Erstelle die Fortschrittsleiste
    ax.barh([''], [percentage], color='#50af47')#50af47'
    ax.barh([''], [100-percentage], left=[percentage], color='#4D4D4D')

    # Setze Grenzen und Labels
    ax.set_xlim(0, 100)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_frame_on(False)

    # Füge den Fortschrittstext hinzu
    plt.text(0, 0, f'{progress} von {total} ({percentage:.0f}%)', ha='left', va='center', color='white', fontsize=205, fontdict={'family': 'Montserrat', 'weight': 'bold'})

    # Konvertiere das Diagramm in ein NumPy-Array
    fig.canvas.draw()
    progress_bar_np = np.array(fig.canvas.renderer._renderer)
    plt.close()

    # Bestimme, wo die Fortschrittsleiste auf dem Bild platziert werden soll
    img_width, img_height = img.size
    bar_height = progress_bar_np.shape[0]
    bar_width = progress_bar_np.shape[1]
    x_offset = 160  # Setze diesen Wert auf 133, um den Balken bei Pixel 133 beginnen zu lassen
    y_offset = img_height - bar_height - (img_height // 4)

    # Füge die Fortschrittsleiste zum Bild hinzu
    final_img = img.copy()
    final_img.paste(Image.fromarray(progress_bar_np), (x_offset, y_offset), Image.fromarray(progress_bar_np))

    # Speichere das finale Bild
    return final_img
#filter the data by Date
def show_raw_data(df_CW_out, df_CW_inb, df_CW_dds, df_LC_out,df_LC_inb, df_LC_dds, df_SFG):

    st.write('Outbound CW')
    st.dataframe(df_CW_out)
    st.write('Inbound CW')
    st.data_editor(df_CW_inb)
    st.write('DDS CW')
    st.data_editor(df_CW_dds)
    st.write('Outbound LC')
    st.data_editor(df_LC_out)
    st.write('Inbound LC')
    st.data_editor(df_LC_inb)
    st.write('DDS LC')
    st.data_editor(df_LC_dds)
    st.write('SFG')
    st.data_editor(df_SFG)

def filter_data(df, date, useCol):
    df[useCol] = pd.to_datetime(df[useCol], errors='coerce').dt.date
    df = df[df[useCol] == date]
    return df

def show_domestic(df_CW_out, df_CW_inb, df_CW_dds):
    #st.dataframe(df_CW_out)
    def logo_and_Zahlen(df_CW_out):
      
        sum_of_loadings = df_CW_out['Destination City'].count()
        
        # zähle Verladen + PGI' in 'Status Verladung '
        sum_loaded = df_CW_out[df_CW_out['Status Verladung'] == 'Verladen + PGI']['Status Verladung'].count()
        # zähle Vorgestellt in 'Status Verladung '
        sum_prepared = df_CW_out[df_CW_out['Status Verladung'] == 'Vorgestellt']['Status Verladung'].count()
        # zähle in in Vorbereitung 'Status Verladung '
        sum_on_preparation = df_CW_out[df_CW_out['Status Verladung'] == 'in Vorbereitung']['Status Verladung'].count()
        # Zähle Gestrichen in 'Status Verladung '
        sum_in_lodingprogress = df_CW_out[df_CW_out['Status Verladung'] == 'Verladung']['Status Verladung'].count()
        
        sum_canceled = df_CW_out[df_CW_out['Status Verladung'] == 'Gestrichen']['Status Verladung'].count()

        col1, col2, col3 = st.columns([1,1,3],gap='small')
        
        with col1:
            outbound = Image.open('Data/img/Outbound.png', mode='r')
            st.image(outbound, use_column_width=True)    
        with col2:
            img_truck = truck_progress_png(sum_loaded, sum_of_loadings)
            st.image(img_truck, use_column_width=True)
            
        with col3:  
            #st.write('Letzte Aktualisierung: ', datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S"))
            annotated_text(
                           annotation(f'Verladene Trucks: {sum_loaded}', '', "#50af47", font_family="Montserrat"),
                           '/',
                           annotation(f'Trucks in Verladung: {sum_in_lodingprogress}', '', "#afca0b", font_family="Montserrat"),
                            '/',
                           annotation(f'Vorgestellte Trucks: {sum_prepared}', '', "#ffbb00", font_family="Montserrat"),
                           '/',
                           annotation(f'Gestrichene Trucks: {sum_canceled}', '', "#e72582", font_family="Montserrat"))        
    def logo_and_Zahlen_inbound(df_inb):
      
        sum_of_loadings = df_inb['Soure Location'].count()
        
        # zähle Verladen + PGI' in 'Status Verladung '
        sum_GR = df_inb[df_inb['Status'] == 'Eingelagert']['Status'].count()
        # zähle Vorgestellt in 'Status Verladung '
        sum_unloaded = df_inb[df_inb['Status'] == 'Entladen']['Status'].count()
        # zähle in in Vorbereitung 'Status Verladung '
        sum_on_preparation = df_inb[df_inb['Status'] == 'Gebucht']['Status'].count()
        # Zähle Gestrichen in 'Status Verladung '
        sum_in_lodingprogress = df_inb[df_inb['Status'] == 'In Arbeit']['Status'].count()
        
        sum_canceled_inb = df_inb[df_inb['Status'] == 'Gestrichen']['Status'].count()

        col1, col2, col3 = st.columns([1,1,3],gap='small')
        
        with col1:
            outbound = Image.open('Data/img/Inbound.png', mode='r')
            st.image(outbound, use_column_width=True)    
        with col2:
            img_truck = truck_progress_png(sum_GR, sum_of_loadings)
            st.image(img_truck, use_column_width=True)
            
        with col3:  
            #st.write('Letzte Aktualisierung: ', datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S"))
            annotated_text(
                           annotation(f'Fertig Trucks: {sum_GR}', '', "#50af47", font_family="Montserrat"),
                           '/',
                           annotation(f'Satus Entladen: {sum_in_lodingprogress}', '', "#afca0b", font_family="Montserrat"),
                            '/',
                           annotation(f'Satus Gebucht: {sum_GR}', '', "#ffbb00", font_family="Montserrat"),
                           '/',
                           annotation(f'Gestrichene Trucks: {sum_canceled_inb}', '', "#e72582", font_family="Montserrat"))        

    def plotly_warehouse_stocks(df_CW_dds):
        # Entferne Zeilen mit NaN-Werten
        #df_CW_dds = df_CW_dds.dropna(subset=['Blocklager Paletten ist', 'Regalager Paletten ist'])

        df_CW_dds['Date'] = pd.to_datetime(df_CW_dds['Date'], errors='coerce').dt.date

        # Setze das aktuelle Datum auf das neueste Datum im DataFrame, wenn es innerhalb der letzten 5 Tage liegt
        current_date = min(datetime.date.today(), df_CW_dds['Date'].max())

        # Filtere df_CW_dds.Date zwischen heute und - 5 Werktage
        df_CW_dds = df_CW_dds[df_CW_dds['Date'] <= current_date]
        df_CW_dds = df_CW_dds[df_CW_dds['Date'] >= (current_date - datetime.timedelta(days=10))]

        # Berechne die Summe der beiden Spalten
        df_CW_dds['Total'] = df_CW_dds['Blocklager Paletten ist'] + df_CW_dds['Regalager Paletten ist']

        # Erstelle gestapelte Balken
        fig = go.Figure()
        fig.add_trace(go.Bar(x=df_CW_dds['Date'], y=df_CW_dds['Blocklager Paletten ist'], name='Blocklager Paletten ist', marker_color='#0e2b63', text=df_CW_dds['Blocklager Paletten ist'], textposition='auto'))
        fig.add_trace(go.Bar(x=df_CW_dds['Date'], y=df_CW_dds['Regalager Paletten ist'], name='Regalager Paletten ist', marker_color='#ef7d00', text=df_CW_dds['Regalager Paletten ist'], textposition='auto'))

        # Füge die Gesamtsumme als Datenbeschriftung hinzu
        fig.add_trace(go.Scatter(
            x=df_CW_dds['Date'],
            y=df_CW_dds['Total'],
            mode='text',
            text=df_CW_dds['Total'],
            textposition="top center",
            textfont=dict(
                color="#000000"
            ),
            showlegend=False
        ))

        # Ändere das Layout
        fig.update_layout(
            barmode='stack',
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
        st.plotly_chart(fig, use_container_width=True)
    col1,col2 = st.columns([4,1])
    img = Image.open('Data/img/Domestic_LOGO.png', mode='r')  
    with col1:
        st.image(img, width=250)
    with col2:
        on_table = st.toggle('Tabellen', False, key='tables_cw')
    col1,col2,col3,col4 = st.columns([3,1,1,1])
    with col1:
        st.write('')
    def cal_hard_messure(df_CW_dds,df_CW_inb,df_CW_out):
        
        df_CW_dds = df_CW_dds.dropna(subset=['Blocklager Paletten ist', 'Regalager Paletten ist'])
        #drop 0 values
        df_CW_dds = df_CW_dds[(df_CW_dds['Blocklager Paletten ist'] != 0) | (df_CW_dds['Regalager Paletten ist'] != 0)]

        # Konvertiere die 'Date'-Spalte in ein datetime-Objekt
        df_CW_dds['Date'] = pd.to_datetime(df_CW_dds['Date'])

        # Finde das neueste Datum mit Einträgen in den Beständen
        latest_date = df_CW_dds['Date'].max()

        # Filtere den DataFrame auf Zeilen mit dem neuesten Datum
        df_latest = df_CW_dds[df_CW_dds['Date'] == latest_date]

        # Summiere 'Blocklager Paletten ist' und 'Regalager Paletten ist'
        total_stock = df_latest['Blocklager Paletten ist'].sum() + df_latest['Regalager Paletten ist'].sum()
        # Funktion, die datetime.time in timedelta konvertiert
        
        
        def time_to_timedelta(t):
            return pd.Timedelta(hours=t.hour, minutes=t.minute, seconds=t.second)
        try:
            # Konvertiere 'Wartezeit bis Entladebeginn' in timedelta-Objekte
            df_CW_inb['Wartezeit bis Entladebeginn'] = df_CW_inb['Wartezeit bis Entladebeginn'].apply(time_to_timedelta)
            #Entladungszeit
            df_CW_inb['Entladungszeit'] = df_CW_inb['Entladungszeit'].apply(time_to_timedelta)
            # Berechne die Gesamtzeit in neue Spalte Entladegesamtzeit
            df_CW_inb['Entladegesamtzeit'] = df_CW_inb['Wartezeit bis Entladebeginn'] + df_CW_inb['Entladungszeit']
            # Berechne den Durchschnitt der Entladegesamtzeit
            inb_time = df_CW_inb['Entladegesamtzeit'].mean().seconds / 60
            # runde auf minuten
            inb_time = round(inb_time, 1)
        except:
            inb_time = 0
        try:
            # filter ist null 0 or NaN or empty df_CW_out['Wartezeit bis Verladebeginn']
            df_CW_out = df_CW_out[df_CW_out['Wartezeit bis Verladebeginn'].notnull()]
            df_CW_out = df_CW_out[df_CW_out['Wartezeit bis Verladebeginn'] != '0']
            df_CW_out = df_CW_out[df_CW_out['Wartezeit bis Verladebeginn'] != '']
            df_CW_out['Wartezeit bis Verladebeginn'] = df_CW_out['Wartezeit bis Verladebeginn'].apply(time_to_timedelta)
            #Entladungszeit
            df_CW_out['Verladungszeit'] = df_CW_out['Verladungszeit'].apply(time_to_timedelta)
            # Berechne die Gesamtzeit in neue Spalte Entladegesamtzeit
            df_CW_out['Ladegesamtzeit'] = df_CW_out['Wartezeit bis Verladebeginn'] + df_CW_out['Verladungszeit']
            # Berechne den Durchschnitt der Entladegesamtzeit
            out_time = df_CW_out['Ladegesamtzeit'].mean().seconds / 60
            out_time = round(out_time, 1)
        except:
            out_time = 0

        
        return total_stock, inb_time, out_time

    # Zeige den Gesamtlagerbestand an
    total_stock, inb_time,out_time  = cal_hard_messure(df_CW_dds, df_CW_inb, df_CW_out)
    col2.metric("Bestand", value = f"{total_stock} EP", delta="1.2 EP frei")
    col3.metric("ø Verladezeit", value = f"{out_time} min",)
    col4.metric("ø Entladezeit", value = f"{inb_time} min",)# delta=" 95,6 % Servicelevel")

    logo_and_Zahlen(df_CW_out)
    logo_and_Zahlen_inbound(df_CW_inb)
    with st.expander('Lagerbestand', expanded=False):
        plotly_warehouse_stocks(df_CW_dds)
    if on_table:
        st.write('Outbound LC')
        st.dataframe(df_CW_out)
        st.write('Inbound LC')
        st.data_editor(df_CW_inb)
        st.write('DDS LC')
        st.data_editor(df_CW_dds)


def show_LC(df_LC_out, df_LC_inb, df_LC_dds):
    #st.dataframe(df_LC_dds)
    def logo_and_Zahlen(df_CW_out):
      
        sum_of_loadings = df_CW_out['SCI'].count()
        
        # zähle Verladen + PGI' in 'Status Verladung '
        sum_loaded = df_CW_out[df_CW_out['Loaded at Bayreuth (Documents finished)'] != None]['Loaded at Bayreuth (Documents finished)'].count()
        # zähle Vorgestellt in 'Status Verladung '
        
        sum_canceled = df_CW_out[df_CW_out['Verschoben / Nicht gekommen (Details schreibe Bemerkung)'] == 'X']['Verschoben / Nicht gekommen (Details schreibe Bemerkung)'].count()

        col1, col2, col3 = st.columns([1,1,3],gap='small')
        
        with col1:
            outbound = Image.open('Data/img/Outbound.png', mode='r')
            st.image(outbound, use_column_width=True)    
        with col2:
            img_truck = truck_progress_png(sum_loaded, sum_of_loadings)
            st.image(img_truck, use_column_width=True)
            
        with col3:  
            #st.write('Letzte Aktualisierung: ', datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S"))
            annotated_text(
                           annotation(f'Verladene Trucks: {sum_loaded}', '', "#50af47", font_family="Montserrat"),
                            '/',
                           annotation(f'Gestrichene Trucks: {sum_canceled}', '', "#e72582", font_family="Montserrat"))        
    def logo_and_Zahlen_inbound(df_inb):
      
        sum_of_loadings = df_inb['Datum'].count()
        
        sum_GR = df_inb['Echtzeit Büro.1'].count()
        # zähle FG in 
        sum_unloadedFG = df_inb['Anzahl Paletten'].count()
        # zähle in in Vorbereitung 'Status Verladung '
        sum_unloadedWMS = df_inb['Anzahl Paletten.1'].count()
        
        
        col1, col2, col3 = st.columns([1,1,3],gap='small')
        
        with col1:
            outbound = Image.open('Data/img/Inbound.png', mode='r')
            st.image(outbound, use_column_width=True)    
        with col2:
            img_truck = truck_progress_png(sum_GR, sum_of_loadings)
            st.image(img_truck, use_column_width=True)
            
        with col3:  
            #st.write('Letzte Aktualisierung: ', datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S"))
            annotated_text(
                           annotation(f'Fertig Trucks: {sum_GR}', '', "#50af47", font_family="Montserrat"),
                           '/',
                           annotation(f'Anzahl FG Trucks: {sum_unloadedFG}', '', "#afca0b", font_family="Montserrat"),
                            '/',
                           annotation(f'Anzahl WMS Trucks: {sum_unloadedWMS}', '', "#ffbb00", font_family="Montserrat"))
                         

    def plotly_warehouse_stocks(df_dds):
        # Entferne Zeilen mit NaN-Werten
        #df_dds = df_dds.dropna(subset=['Blocklager Paletten ist', 'Regalager Paletten ist'])

        df_dds['Date'] = pd.to_datetime(df_dds['Date'], errors='coerce').dt.date

        # Setze das aktuelle Date auf das neueste Date im DataFrame, wenn es innerhalb der letzten 5 Tage liegt
        # Stellen Sie sicher, dass 'Date' als datetime interpretiert wird
        df_dds['Date'] = pd.to_datetime(df_dds['Date'])

        # Berechne das aktuelle Datum
        current_date = pd.Timestamp(datetime.date.today())

        # Filtere df_dds basierend auf 'Date'
        df_dds = df_dds[df_dds['Date'] <= current_date]
        # Filtere df_dds.Date zwischen heute und - 5 Werktage
        df_dds = df_dds[df_dds['Date'] <= current_date]
        df_dds = df_dds[df_dds['Date'] >= (current_date - datetime.timedelta(days=10))]

        # Berechne die Summe der beiden Spalten
        columns_prod_mat = [col for col in df_dds.columns if 'Produktionsmaterialien' in col]
        summeWMS_filtered = df_dds[columns_prod_mat].sum(axis=1)

        # Berechne SummeFG (Summe der Fertigwaren nach Abzug des GEW Bestand)
        columns_summeFG = ['Zigaretten (ZFG100000)', 'Zigarillos (ZFG110000)', 'OTP (ZFG130000)']
        summeFG_filtered = df_dds[columns_summeFG].sum(axis=1) - df_dds['GEW Bestand ']

        # Erstelle einen DataFrame für das Sankey-Diagramm
        sankey_data_filtered = pd.DataFrame({
            'Date': df_dds['Date'],
            'SummeWMS': summeWMS_filtered,
            'SummeFG': summeFG_filtered,
            'GEW Bestand': df_dds['GEW Bestand ']
})
        
        df_dds = sankey_data_filtered
        df_dds['Total'] = df_dds['SummeWMS'] + df_dds['SummeFG'] + df_dds['GEW Bestand']
        # Erstelle gestapelte Balken
        fig = go.Figure()
        fig.add_trace(go.Bar(x=df_dds['Date'], y=df_dds['GEW Bestand'], name='GEW Bestand', marker_color='#00b1eb', text=df_dds['GEW Bestand'], textposition='auto'))
        fig.add_trace(go.Bar(x=df_dds['Date'], y=df_dds['SummeWMS'], name='SummeWMS', marker_color='#0e2b63', text=df_dds['SummeWMS'], textposition='auto'))
        fig.add_trace(go.Bar(x=df_dds['Date'], y=df_dds['SummeFG'], name='SummeFG', marker_color='#ef7d00', text=df_dds['SummeFG'], textposition='auto'))

        # Füge die Gesamtsumme als Datenbeschriftung hinzu
        fig.add_trace(go.Scatter(
            x=df_dds['Date'],
            y=df_dds['Total'],
            mode='text',
            text=df_dds['Total'],
            textposition="top center",
            textfont=dict(
                color="#000000"
            ),
            showlegend=False
        ))

        # Ändere das Layout
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
        st.plotly_chart(fig, use_container_width=True)
    col1,col2 = st.columns([4,1])

    img = Image.open('Data/img/LC_LOGO.png', mode='r')  
    with col1:
        st.image(img, width=250)
    with col2:
        on_table = st.toggle('Tabellen', False, key='tables_LC')
    col1,col2,col3,col4 = st.columns([3,1,1,1])
    with col1:
        st.write('')

    def cal_hard_messure(df_dds,df_CW_inb,df_CW_out):
        
        # filtere 0 values aus df_latest['Gesamtlagerkapazität']
        df_dds = df_dds.dropna(subset=['Gesamtlagerkapazität'])
        # Konvertiere die 'Date'-Spalte in ein datetime-Objekt
        df_dds['Date'] = pd.to_datetime(df_dds['Date'])

        # Finde das neueste Datum mit Einträgen in den Beständen
        latest_date = df_dds['Date'].max()

        # Filtere den DataFrame auf Zeilen mit dem neuesten Datum
        df_latest = df_dds[df_dds['Date'] == latest_date]

        # Summiere 'Blocklager Paletten ist' und 'Regalager Paletten ist'
        total_stock = df_latest['Gesamtlagerkapazität'].sum()
        # Funktion, die datetime.time in timedelta konvertiert
        
        
        def time_to_timedelta(t):
            return pd.Timedelta(hours=t.hour, minutes=t.minute, seconds=t.second)
        try:
            # Konvertiere 'Wartezeit bis Entladebeginn' in timedelta-Objekte
            df_CW_inb['Wartezeit bis Entladebeginn'] = df_CW_inb['Wartezeit bis Entladebeginn'].apply(time_to_timedelta)
            #Entladungszeit
            df_CW_inb['Entladungszeit'] = df_CW_inb['Entladungszeit'].apply(time_to_timedelta)
            # Berechne die Gesamtzeit in neue Spalte Entladegesamtzeit
            df_CW_inb['Entladegesamtzeit'] = df_CW_inb['Wartezeit bis Entladebeginn'] + df_CW_inb['Entladungszeit']
            # Berechne den Durchschnitt der Entladegesamtzeit
            inb_time = df_CW_inb['Entladegesamtzeit'].mean().seconds / 60
            # runde auf minuten
            inb_time = round(inb_time, 1)
        except:
            inb_time = 0
        try:
            # filter ist null 0 or NaN or empty df_CW_out['Wartezeit bis Verladebeginn']
            df_CW_out = df_CW_out[df_CW_out['Wartezeit bis Verladebeginn'].notnull()]
            df_CW_out = df_CW_out[df_CW_out['Wartezeit bis Verladebeginn'] != '0']
            df_CW_out = df_CW_out[df_CW_out['Wartezeit bis Verladebeginn'] != '']
            df_CW_out['Wartezeit bis Verladebeginn'] = df_CW_out['Wartezeit bis Verladebeginn'].apply(time_to_timedelta)
            #Entladungszeit
            df_CW_out['Verladungszeit'] = df_CW_out['Verladungszeit'].apply(time_to_timedelta)
            # Berechne die Gesamtzeit in neue Spalte Entladegesamtzeit
            df_CW_out['Ladegesamtzeit'] = df_CW_out['Wartezeit bis Verladebeginn'] + df_CW_out['Verladungszeit']
            # Berechne den Durchschnitt der Entladegesamtzeit
            out_time = df_CW_out['Ladegesamtzeit'].mean().seconds / 60
            out_time = round(out_time, 1)
        except:
            out_time = 0

        
        return total_stock, inb_time, out_time



    # Zeige den Gesamtlagerbestand an
    total_stock, inb_time,out_time  = cal_hard_messure(df_LC_dds, df_LC_inb, df_LC_out)
    col2.metric("Bestand", value = f"{total_stock} EP", delta="1.2 EP frei")
    col3.metric("ø Verladezeit", value = f"{out_time} min",)
    col4.metric("ø Entladezeit", value = f"{inb_time} min",)# delta=" 95,6 % Servicelevel")

    logo_and_Zahlen(df_LC_out)
    logo_and_Zahlen_inbound(df_LC_inb)
    with st.expander('Lagerbestand', expanded=False):
        plotly_warehouse_stocks(df_LC_dds)
    if on_table:
        st.write('Outbound LC')
        st.dataframe(df_LC_out)
        st.write('Inbound LC')
        st.data_editor(df_LC_inb)
        st.write('DDS LC')
        st.data_editor(df_LC_dds)
  
def show_SFG(df_SFG_out, df_SFG_inb, df_SFG_dds):
    # st.write('Outbound SFG')
    # st.data_editor(df_SFG_out)
    # st.write('Inbound SFG')
    # st.data_editor(df_SFG_inb)
    # st.data_editor(df_SFG_dds)
    def logo_and_Zahlen(df_out):       
        'Filter DIET'
        df_out["Material Group:\nDiet\nCAF\nStaub\nPresize\nRohware"] == 'Diet'
        # zähle Vorgestellt in 'Status Verladung '
        sum_loadings = df_out["Material Group:\nDiet\nCAF\nStaub\nPresize\nRohware"].count()
        sum_finished = df_out[df_out['Ladeende'] != None]['Ladeende'].count()

        col1, col2, col3 = st.columns([1,1,3],gap='small')
        
        with col1:
            outbound = Image.open('Data/img/Outbound.png', mode='r')
            st.image(outbound, use_column_width=True)    
        with col2:
            img_truck = truck_progress_png(sum_loadings, sum_finished)
            st.image(img_truck, use_column_width=True)
            
        with col3:  
            #st.write('Letzte Aktualisierung: ', datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S"))
            annotated_text(
                           annotation(f'Verladene Trucks: {sum_finished}', '', "#50af47", font_family="Montserrat"),
                            '/',
                           annotation(f'Gestrichene Trucks: {sum_finished}', '', "#e72582", font_family="Montserrat"))        
    def logo_and_Zahlen_inbound(df_inb):
      
        sum_of_loadings = df_inb['Datum'].count()
        
        sum_GR = df_inb['Echtzeit Büro.1'].count()
        # zähle FG in 
        sum_unloadedFG = df_inb['Anzahl Paletten'].count()
        # zähle in in Vorbereitung 'Status Verladung '
        sum_unloadedWMS = df_inb['Anzahl Paletten.1'].count()
        
        
        col1, col2, col3 = st.columns([1,1,3],gap='small')
        
        with col1:
            outbound = Image.open('Data/img/Inbound.png', mode='r')
            st.image(outbound, use_column_width=True)    
        with col2:
            img_truck = truck_progress_png(sum_GR, sum_of_loadings)
            st.image(img_truck, use_column_width=True)
            
        with col3:  
            #st.write('Letzte Aktualisierung: ', datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S"))
            annotated_text(
                           annotation(f'Fertig Trucks: {sum_GR}', '', "#50af47", font_family="Montserrat"),
                           '/',
                           annotation(f'Anzahl FG Trucks: {sum_unloadedFG}', '', "#afca0b", font_family="Montserrat"),
                            '/',
                           annotation(f'Anzahl WMS Trucks: {sum_unloadedWMS}', '', "#ffbb00", font_family="Montserrat"))         

    def plotly_warehouse_stocks(df_dds):

        df_dds['Date'] = pd.to_datetime(df_dds['Date'], errors='coerce').dt.date

        df_dds['Date'] = pd.to_datetime(df_dds['Date'])

        # Berechne das aktuelle Datum
        current_date = pd.Timestamp(datetime.date.today())

        # Filtere df_dds basierend auf 'Date'
        df_dds = df_dds[df_dds['Date'] <= current_date]
        # Filtere df_dds.Date zwischen heute und - 5 Werktage
        df_dds = df_dds[df_dds['Date'] <= current_date]
        df_dds = df_dds[df_dds['Date'] >= (current_date - datetime.timedelta(days=10))]

        # rename PMD to DIET CS
        st.data_editor(df_dds)
        
        fig = go.Figure()
        fig.add_trace(go.Bar(x=df_dds['Date'], y=df_dds['PMD '], name='PMD ', marker_color='#00b1eb', text=df_dds['PMD '], textposition='auto'))
        # fig.add_trace(go.Bar(x=df_dds['Date'], y=df_dds['SummeWMS'], name='SummeWMS', marker_color='#0e2b63', text=df_dds['SummeWMS'], textposition='auto'))
        # fig.add_trace(go.Bar(x=df_dds['Date'], y=df_dds['SummeFG'], name='SummeFG', marker_color='#ef7d00', text=df_dds['SummeFG'], textposition='auto'))
        # Füge die Gesamtsumme als Datenbeschriftung hinzu
        # fig.add_trace(go.Scatter(
        #     x=df_dds['Date'],
        #     y=df_dds['Total'],
        #     mode='text',
        #     text=df_dds['Total'],
        #     textposition="top center",
        #     textfont=dict(
        #         color="#000000"
        #     ),
        #     showlegend=False
        # ))

        # Ändere das Layout
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
        st.plotly_chart(fig, use_container_width=True)
    col1,col2 = st.columns([4,1])

    with col1:
        img = Image.open('Data/img/DIET_LOGO.png', mode='r')  
    with col2:
        on_table = st.toggle('Tabellen', False, key='tables_SFG')
    col1,col2,col3,col4 = st.columns([3,1,1,1])
    with col1:
         
        st.image(img, width=250)
        #st.image(img2, width=180)
    st.write('')

    def cal_hard_messure(df_SFG_out, df_SFG_inb, df_dds):
        
        # filtere 0 values aus df_latest['Gesamtlagerkapazität']
        df_dds = df_dds.dropna(subset=['PMD '])
        # Konvertiere die 'Date'-Spalte in ein datetime-Objekt
        df_dds['Date'] = pd.to_datetime(df_dds['Date'])

        # Finde das neueste Datum mit Einträgen in den Beständen
        latest_date = df_dds['Date'].max()

        # Filtere den DataFrame auf Zeilen mit dem neuesten Datum
        df_latest = df_dds[df_dds['Date'] == latest_date]

        # Summiere 'Blocklager Paletten ist' und 'Regalager Paletten ist'
        total_stock = df_latest['PMD '].sum()
        # Funktion, die datetime.time in timedelta konvertiert
        
        
        def time_to_timedelta(t):
            return pd.Timedelta(hours=t.hour, minutes=t.minute, seconds=t.second)
        try:
            # Konvertiere 'Wartezeit bis Entladebeginn' in timedelta-Objekte
            df_CW_inb['Wartezeit bis Entladebeginn'] = df_CW_inb['Wartezeit bis Entladebeginn'].apply(time_to_timedelta)
            #Entladungszeit
            df_CW_inb['Entladungszeit'] = df_CW_inb['Entladungszeit'].apply(time_to_timedelta)
            # Berechne die Gesamtzeit in neue Spalte Entladegesamtzeit
            df_CW_inb['Entladegesamtzeit'] = df_CW_inb['Wartezeit bis Entladebeginn'] + df_CW_inb['Entladungszeit']
            # Berechne den Durchschnitt der Entladegesamtzeit
            inb_time = df_CW_inb['Entladegesamtzeit'].mean().seconds / 60
            # runde auf minuten
            inb_time = round(inb_time, 1)
        except:
            inb_time = 0
        try:
            # filter ist null 0 or NaN or empty df_CW_out['Wartezeit bis Verladebeginn']
            df_CW_out = df_CW_out[df_CW_out['Wartezeit bis Verladebeginn'].notnull()]
            df_CW_out = df_CW_out[df_CW_out['Wartezeit bis Verladebeginn'] != '0']
            df_CW_out = df_CW_out[df_CW_out['Wartezeit bis Verladebeginn'] != '']
            df_CW_out['Wartezeit bis Verladebeginn'] = df_CW_out['Wartezeit bis Verladebeginn'].apply(time_to_timedelta)
            #Entladungszeit
            df_CW_out['Verladungszeit'] = df_CW_out['Verladungszeit'].apply(time_to_timedelta)
            # Berechne die Gesamtzeit in neue Spalte Entladegesamtzeit
            df_CW_out['Ladegesamtzeit'] = df_CW_out['Wartezeit bis Verladebeginn'] + df_CW_out['Verladungszeit']
            # Berechne den Durchschnitt der Entladegesamtzeit
            out_time = df_CW_out['Ladegesamtzeit'].mean().seconds / 60
            out_time = round(out_time, 1)
        except:
            out_time = 0

        
        return total_stock, inb_time, out_time



    # Zeige den Gesamtlagerbestand an
    total_stock, inb_time,out_time  = cal_hard_messure(df_SFG_out, df_SFG_inb, df_SFG_dds)
    col2.metric("Bestand", value = f"{total_stock} EP", delta="1.2 EP frei")
    col3.metric("ø Verladezeit", value = f"{out_time} min",)
    col4.metric("ø Entladezeit", value = f"{inb_time} min",)# delta=" 95,6 % Servicelevel")

    logo_and_Zahlen(df_SFG_out)
    #logo_and_Zahlen_inbound(df_LC_inb)
    with st.expander('Lagerbestand', expanded=False):
        plotly_warehouse_stocks(df_SFG_dds)
    if on_table:
        st.write('Outbound LC')
        st.dataframe(df_SFG_out)
        
        st.write('Inbound LC')
        st.data_editor(df_SFG_inb)
        
        st.write('DDS LC')
        st.data_editor(df_SFG_dds)

  
def show_LEAF(df_CW_out, df_CW_inb, df_CW_dds):
   
    def logo_and_Zahlen(f_CW_out, df_CW_inb):
      
        sum_of_loadings = df_CW_out['Destination City'].count()
        
        # zähle Verladen + PGI' in 'Status Verladung '
        sum_loaded = df_CW_out[df_CW_out['Status Verladung'] == 'Verladen + PGI']['Status Verladung'].count()
        # zähle Vorgestellt in 'Status Verladung '
        sum_prepared = df_CW_out[df_CW_out['Status Verladung'] == 'Vorgestellt']['Status Verladung'].count()
        # zähle in in Vorbereitung 'Status Verladung '
        sum_on_preparation = df_CW_out[df_CW_out['Status Verladung'] == 'in Vorbereitung']['Status Verladung'].count()
        # Zähle Gestrichen in 'Status Verladung '
        sum_in_lodingprogress = df_CW_out[df_CW_out['Status Verladung'] == 'Verladung']['Status Verladung'].count()
        
        sum_canceled = df_CW_out[df_CW_out['Status Verladung'] == 'Gestrichen']['Status Verladung'].count()

        col1, col2, col3 = st.columns([1,1,3],gap='small')
        
        with col1:
            outbound = Image.open('Data/img/Outbound.png', mode='r')
            st.image(outbound, use_column_width=True)    
        with col2:
            img_truck = truck_progress_png(sum_loaded, sum_of_loadings)
            st.image(img_truck, use_column_width=True)
            
        with col3:  
            #st.write('Letzte Aktualisierung: ', datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S"))
            annotated_text(
                           annotation(f'Verladene Trucks: {sum_loaded}', '', "#50af47", font_family="Montserrat"),
                           '/',
                           annotation(f'Trucks in Verladung: {sum_in_lodingprogress}', '', "#afca0b", font_family="Montserrat"),
                            '/',
                           annotation(f'Vorgestellte Trucks: {sum_prepared}', '', "#ffbb00", font_family="Montserrat"),
                           '/',
                           annotation(f'Gestrichene Trucks: {sum_canceled}', '', "#e72582", font_family="Montserrat"))        
    def logo_and_Zahlen_inbound(f_CW_out, df_CW_inb):
      
        sum_of_loadings = df_CW_out['Destination City'].count()
        
        # zähle Verladen + PGI' in 'Status Verladung '
        sum_loaded = df_CW_out[df_CW_out['Status Verladung'] == 'Verladen + PGI']['Status Verladung'].count()
        # zähle Vorgestellt in 'Status Verladung '
        sum_prepared = df_CW_out[df_CW_out['Status Verladung'] == 'Vorgestellt']['Status Verladung'].count()
        # zähle in in Vorbereitung 'Status Verladung '
        sum_on_preparation = df_CW_out[df_CW_out['Status Verladung'] == 'in Vorbereitung']['Status Verladung'].count()
        # Zähle Gestrichen in 'Status Verladung '
        sum_in_lodingprogress = df_CW_out[df_CW_out['Status Verladung'] == 'Verladung']['Status Verladung'].count()
        
        sum_canceled = df_CW_out[df_CW_out['Status Verladung'] == 'Gestrichen']['Status Verladung'].count()

        col1, col2, col3 = st.columns([1,1,3],gap='small')
        
        with col1:
            outbound = Image.open('Data/img/Inbound.png', mode='r')
            st.image(outbound, use_column_width=True)    
        with col2:
            img_truck = truck_progress_png(sum_loaded, sum_of_loadings)
            st.image(img_truck, use_column_width=True)
            
        with col3:  
            #st.write('Letzte Aktualisierung: ', datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S"))
            annotated_text(
                           annotation(f'Verladene Trucks: {sum_loaded}', '', "#50af47", font_family="Montserrat"),
                           '/',
                           annotation(f'Trucks in Verladung: {sum_in_lodingprogress}', '', "#afca0b", font_family="Montserrat"),
                            '/',
                           annotation(f'Vorgestellte Trucks: {sum_prepared}', '', "#ffbb00", font_family="Montserrat"),
                           '/',
                           annotation(f'Gestrichene Trucks: {sum_canceled}', '', "#e72582", font_family="Montserrat"))        

    def plotly_warehouse_stocks(df_CW_dds):
        # Entferne Zeilen mit NaN-Werten
        #df_CW_dds = df_CW_dds.dropna(subset=['Blocklager Paletten ist', 'Regalager Paletten ist'])

        df_CW_dds['Date'] = pd.to_datetime(df_CW_dds['Date'], errors='coerce').dt.date

        # Setze das aktuelle Datum auf das neueste Datum im DataFrame, wenn es innerhalb der letzten 5 Tage liegt
        current_date = min(datetime.date.today(), df_CW_dds['Date'].max())

        # Filtere df_CW_dds.Date zwischen heute und - 5 Werktage
        df_CW_dds = df_CW_dds[df_CW_dds['Date'] <= current_date]
        df_CW_dds = df_CW_dds[df_CW_dds['Date'] >= (current_date - datetime.timedelta(days=10))]

        # Berechne die Summe der beiden Spalten
        df_CW_dds['Total'] = df_CW_dds['Blocklager Paletten ist'] + df_CW_dds['Regalager Paletten ist']

        # Erstelle gestapelte Balken
        fig = go.Figure()
        fig.add_trace(go.Bar(x=df_CW_dds['Date'], y=df_CW_dds['Blocklager Paletten ist'], name='Blocklager Paletten ist', marker_color='#0e2b63', text=df_CW_dds['Blocklager Paletten ist'], textposition='auto'))
        fig.add_trace(go.Bar(x=df_CW_dds['Date'], y=df_CW_dds['Regalager Paletten ist'], name='Regalager Paletten ist', marker_color='#ef7d00', text=df_CW_dds['Regalager Paletten ist'], textposition='auto'))

        # Füge die Gesamtsumme als Datenbeschriftung hinzu
        fig.add_trace(go.Scatter(
            x=df_CW_dds['Date'],
            y=df_CW_dds['Total'],
            mode='text',
            text=df_CW_dds['Total'],
            textposition="top center",
            textfont=dict(
                color="#000000"
            ),
            showlegend=False
        ))

        # Ändere das Layout
        fig.update_layout(
            barmode='stack',
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
        st.plotly_chart(fig, use_container_width=True)

    img = Image.open('Data/img/LEAF_LOGO.png', mode='r')  
    #st.image(img, width=250)
    col1,col2,col3,col4 = st.columns([3,1,1,1])
    with col1:  
        st.image(img, width=250)
    lagerbestand = df_CW_dds['Blocklager Paletten ist'].sum() + df_CW_dds['Regalager Paletten ist'].sum()
    col2.metric(f"Temperature", lagerbestand, "1.2 °F")
    col3.metric("Temperature", "70 °F", "1.2 °F")
    col4.metric("Temperature", "70 °F", "1.2 °F")

    #logo_and_Zahlen(df_CW_out, df_CW_inb)
    logo_and_Zahlen_inbound(df_CW_out, df_CW_inb)
    with st.expander('Lagerbestand', expanded=False):
        plotly_warehouse_stocks(df_CW_dds)
    
def show_CF(df_CW_out, df_CW_inb, df_CW_dds):
   
    def logo_and_Zahlen(f_CW_out, df_CW_inb):
      
        sum_of_loadings = df_CW_out['Destination City'].count()
        
        # zähle Verladen + PGI' in 'Status Verladung '
        sum_loaded = df_CW_out[df_CW_out['Status Verladung'] == 'Verladen + PGI']['Status Verladung'].count()
        # zähle Vorgestellt in 'Status Verladung '
        sum_prepared = df_CW_out[df_CW_out['Status Verladung'] == 'Vorgestellt']['Status Verladung'].count()
        # zähle in in Vorbereitung 'Status Verladung '
        sum_on_preparation = df_CW_out[df_CW_out['Status Verladung'] == 'in Vorbereitung']['Status Verladung'].count()
        # Zähle Gestrichen in 'Status Verladung '
        sum_in_lodingprogress = df_CW_out[df_CW_out['Status Verladung'] == 'Verladung']['Status Verladung'].count()
        
        sum_canceled = df_CW_out[df_CW_out['Status Verladung'] == 'Gestrichen']['Status Verladung'].count()

        col1, col2, col3 = st.columns([1,1,3],gap='small')
        
        with col1:
            outbound = Image.open('Data/img/Outbound.png', mode='r')
            st.image(outbound, use_column_width=True)    
        with col2:
            img_truck = truck_progress_png(sum_loaded, sum_of_loadings)
            st.image(img_truck, use_column_width=True)
            
        with col3:  
            #st.write('Letzte Aktualisierung: ', datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S"))
            annotated_text(
                           annotation(f'Verladene Trucks: {sum_loaded}', '', "#50af47", font_family="Montserrat"),
                           '/',
                           annotation(f'Trucks in Verladung: {sum_in_lodingprogress}', '', "#afca0b", font_family="Montserrat"),
                            '/',
                           annotation(f'Vorgestellte Trucks: {sum_prepared}', '', "#ffbb00", font_family="Montserrat"),
                           '/',
                           annotation(f'Gestrichene Trucks: {sum_canceled}', '', "#e72582", font_family="Montserrat"))        
    def logo_and_Zahlen_inbound(f_CW_out, df_CW_inb):
      
        sum_of_loadings = df_CW_out['Destination City'].count()
        
        # zähle Verladen + PGI' in 'Status Verladung '
        sum_loaded = df_CW_out[df_CW_out['Status Verladung'] == 'Verladen + PGI']['Status Verladung'].count()
        # zähle Vorgestellt in 'Status Verladung '
        sum_prepared = df_CW_out[df_CW_out['Status Verladung'] == 'Vorgestellt']['Status Verladung'].count()
        # zähle in in Vorbereitung 'Status Verladung '
        sum_on_preparation = df_CW_out[df_CW_out['Status Verladung'] == 'in Vorbereitung']['Status Verladung'].count()
        # Zähle Gestrichen in 'Status Verladung '
        sum_in_lodingprogress = df_CW_out[df_CW_out['Status Verladung'] == 'Verladung']['Status Verladung'].count()
        
        sum_canceled = df_CW_out[df_CW_out['Status Verladung'] == 'Gestrichen']['Status Verladung'].count()

        col1, col2, col3 = st.columns([1,1,3],gap='small')
        
        with col1:
            outbound = Image.open('Data/img/Inbound.png', mode='r')
            st.image(outbound, use_column_width=True)    
        with col2:
            img_truck = truck_progress_png(sum_loaded, sum_of_loadings)
            st.image(img_truck, use_column_width=True)
            
        with col3:  
            #st.write('Letzte Aktualisierung: ', datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S"))
            annotated_text(
                           annotation(f'Verladene Trucks: {sum_loaded}', '', "#50af47", font_family="Montserrat"),
                           '/',
                           annotation(f'Trucks in Verladung: {sum_in_lodingprogress}', '', "#afca0b", font_family="Montserrat"),
                            '/',
                           annotation(f'Vorgestellte Trucks: {sum_prepared}', '', "#ffbb00", font_family="Montserrat"),
                           '/',
                           annotation(f'Gestrichene Trucks: {sum_canceled}', '', "#e72582", font_family="Montserrat"))        

    def plotly_warehouse_stocks(df_CW_dds):
        # Entferne Zeilen mit NaN-Werten
        #df_CW_dds = df_CW_dds.dropna(subset=['Blocklager Paletten ist', 'Regalager Paletten ist'])

        df_CW_dds['Date'] = pd.to_datetime(df_CW_dds['Date'], errors='coerce').dt.date

        # Setze das aktuelle Datum auf das neueste Datum im DataFrame, wenn es innerhalb der letzten 5 Tage liegt
        current_date = min(datetime.date.today(), df_CW_dds['Date'].max())

        # Filtere df_CW_dds.Date zwischen heute und - 5 Werktage
        df_CW_dds = df_CW_dds[df_CW_dds['Date'] <= current_date]
        df_CW_dds = df_CW_dds[df_CW_dds['Date'] >= (current_date - datetime.timedelta(days=10))]

        # Berechne die Summe der beiden Spalten
        df_CW_dds['Total'] = df_CW_dds['Blocklager Paletten ist'] + df_CW_dds['Regalager Paletten ist']

        # Erstelle gestapelte Balken
        fig = go.Figure()
        fig.add_trace(go.Bar(x=df_CW_dds['Date'], y=df_CW_dds['Blocklager Paletten ist'], name='Blocklager Paletten ist', marker_color='#0e2b63', text=df_CW_dds['Blocklager Paletten ist'], textposition='auto'))
        fig.add_trace(go.Bar(x=df_CW_dds['Date'], y=df_CW_dds['Regalager Paletten ist'], name='Regalager Paletten ist', marker_color='#ef7d00', text=df_CW_dds['Regalager Paletten ist'], textposition='auto'))

        # Füge die Gesamtsumme als Datenbeschriftung hinzu
        fig.add_trace(go.Scatter(
            x=df_CW_dds['Date'],
            y=df_CW_dds['Total'],
            mode='text',
            text=df_CW_dds['Total'],
            textposition="top center",
            textfont=dict(
                color="#000000"
            ),
            showlegend=False
        ))

        # Ändere das Layout
        fig.update_layout(
            barmode='stack',
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
        st.plotly_chart(fig, use_container_width=True)

    img = Image.open('Data/img/C&F_LOGO.png', mode='r')  
    #st.image(img, width=250)
    col1,col2,col3,col4 = st.columns([3,1,1,1])
    with col1:  
        st.image(img, width=250)
    lagerbestand = df_CW_dds['Blocklager Paletten ist'].sum() + df_CW_dds['Regalager Paletten ist'].sum()
    col2.metric(f"Temperature", lagerbestand, "1.2 °F")
    col3.metric("Temperature", "70 °F", "1.2 °F")
    col4.metric("Temperature", "70 °F", "1.2 °F")

    logo_and_Zahlen(df_CW_out, df_CW_inb)
    #logo_and_Zahlen_inbound(df_CW_out, df_CW_inb)
    with st.expander('Lagerbestand', expanded=False):
        plotly_warehouse_stocks(df_CW_dds)
    

def main():
    col1, col2, col3 = st.columns([2,1,1])
    with col1:  
        st.markdown("""
                    <style>
                    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@700&display=swap');
                    </style>
                    <h2 style='text-align: left; color: #0F2B63; font-family: Montserrat; font-weight: bold;'>{}</h1>
                    """.format('Logistics Live Monitor'), unsafe_allow_html=True)   
    with col2:
        #st.write('Letzte Aktualisierung: ', datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S"))
        sel_date = st.date_input('Datum', datetime.date.today())
    with col3:
        if st.button('Reload'):
            with st.spinner('Reload in 3 seconds...'):
                time.sleep(3)
                st.cache_data.clear()
                st.rerun()
    img_strip = Image.open('Data/img/strip.png')   
    img_strip = img_strip.resize((1000, 15))     
    st.image(img_strip, use_column_width=True, caption='',)   



    df_CW_out, df_CW_inb, df_CW_dds  = load_data_CW()
    df_CW_out = filter_data(df_CW_out,sel_date,'Ist Datum')
    df_CW_inb = filter_data(df_CW_inb,sel_date,'Ist Datum')
    df_LC_out, df_LC_inb, df_LC_dds = load_data_LC()
    df_LC_out = filter_data(df_LC_out,sel_date,'Datum')
    df_LC_inb = filter_data(df_LC_inb,sel_date,'Datum')
    df_SFG_out, df_SFG_inb, df_SFG_dds = load_data_SFG()
    df_SFG_out = filter_data(df_SFG_out,sel_date,'Abholdatum Update')
    df_SFG_inb = filter_data(df_SFG_inb,sel_date,'Ist Datum\n(Tatsächliche Anlieferung)')

    show_LC(df_LC_out, df_LC_inb, df_LC_dds)
    show_domestic(df_CW_out, df_CW_inb, df_CW_dds)
    show_SFG(df_SFG_out, df_SFG_inb, df_SFG_dds)
    show_LEAF(df_CW_out, df_CW_inb, df_CW_dds)
    show_CF(df_CW_out, df_CW_inb, df_CW_dds)
    