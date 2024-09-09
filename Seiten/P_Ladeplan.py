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
import hydralit_components as hc

from annotated_text import annotated_text, annotation
from Data_Class.AzureStorage_dev import get_blob_list_dev, get_file_dev
from Data_Class.MMSQL_connection import read_Table
import json

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

def save_update_time():
    # Aktuelles Datum und Uhrzeit speichern
    jetzt = datetime.datetime.now()

    # Datum und Uhrzeit als String speichern
    datum_zeit_string = jetzt.strftime("%Y-%m-%d %H:%M:%S")

    # Daten in eine Datei schreiben
    with open('Data/appData/update_time_Ladeplan.json', 'w') as file:
        json.dump(datum_zeit_string, file)

@st.cache_data(show_spinner=False)
def load_data_CW():
    save_update_time()
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
    
    # except:
    #     df_outbound = pd.read_csv('Data/con_backups/Quelle_PA_BLOBB/Outbound_Monitor.csv')
    #     df_inbound = pd.read_csv('Data/con_backups/Quelle_PA_BLOBB/Inbound_Monitor.csv')
    #     st.warning('Fehler beim Laden der 2024_Ladeplan_SDDS_FG_GER_Domestic.xlsm Datei. Bitte kontaktieren Sie den Administrator.')
    #     st.error('Die Angezeigten Daten sind Veraltet')
    #     return df_outbound, df_inbound, None

@st.cache_data(show_spinner=False)
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
    data = get_file_dev("Anwesenheit.xlsx")
        # #save as csv to Data/con_backups/Quelle_PA_BLOBB
    @st.cache_data
    def loadData(data):
        df = pd.read_excel(BytesIO(data),sheet_name='LPC')
        return df
    df = loadData(data)    


    df = df[2:]
    df = df.T
    df_transposed = df.iloc[1:5].T
    #drop zeile 2 bis 4
    df = df.drop(df.index[1:5])
    
    df.columns = df.iloc[0]
    df_transposed.columns = df_transposed.iloc[0]
    df = df[1:]
    df_transposed = df_transposed[1:]
    
    st.dataframe(df_transposed)
    st.dataframe(df)

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


def show_domestic(df_CW_out, df_CW_inb, df_CW_dds,sel_date):

    try:
        df_dds = df_CW_dds
        df_dds['Date'] = pd.to_datetime(df_dds['Date'], errors='coerce').dt.date

        # Setze das aktuelle Date auf das neueste Date im DataFrame, wenn es innerhalb der letzten 5 Tage liegt
        # Stellen Sie sicher, dass 'Date' als datetime interpretiert wird
        df_dds['Date'] = pd.to_datetime(df_dds['Date'])
        # Filtere df_dds basierend auf dem aktuellen Datum
        # sel_date to datetime
        sel_date = pd.to_datetime(sel_date)
        df_dds = df_dds[df_dds['Date'] == sel_date]
        df_dds['Total'] = df_dds['Blocklager Paletten ist'] + df_dds['Regalager Paletten ist']
        total_stock = df_dds['Total'].sum()
    except:
        total_stock = 0

    def outbound(df_CW_out):
      
        sum_of_loadings = df_CW_out['Destination City'].count()
        # zähle Verladen + PGI' in 'Status Verladung '
        sum_loaded = df_CW_out[df_CW_out['Status Verladung'] == 'Verladen + PGI']['Status Verladung'].count()
        def time_to_timedelta(t):
            return pd.Timedelta(hours=t.hour, minutes=t.minute, seconds=t.second)
        try:
            # filter ist null 0 or NaN or empty df_CW_out['Wartezeit bis Verladebeginn']
            df_CW_out = df_CW_out[df_CW_out['On time innerhalb 2,5 Std. (Automatisch berechnet) '].notnull()]
            df_CW_out = df_CW_out[df_CW_out['On time innerhalb 2,5 Std. (Automatisch berechnet) '] != '0']
            df_CW_out = df_CW_out[df_CW_out['On time innerhalb 2,5 Std. (Automatisch berechnet) '] != '']
            # to datetime
            df_CW_out['On time innerhalb 2,5 Std. (Automatisch berechnet) '] = pd.to_datetime(df_CW_out['On time innerhalb 2,5 Std. (Automatisch berechnet) '], errors='coerce').dt.time
            df_CW_out['On time innerhalb 2,5 Std. (Automatisch berechnet) '] = df_CW_out['On time innerhalb 2,5 Std. (Automatisch berechnet) '].apply(time_to_timedelta)
            out_time = df_CW_out['On time innerhalb 2,5 Std. (Automatisch berechnet) '].mean().seconds / 60
            out_time = round(out_time)
        except:
            out_time = 0
        col1, col2, col3  = st.columns([2,2,1],gap='small')
        
        with col1:
            outbound = Image.open('Data/img/Outbound.png', mode='r')
            st.image(outbound, use_column_width=True)    
        with col2:
            img_truck = truck_progress_png(sum_loaded, sum_of_loadings)
            st.image(img_truck, use_column_width=True)

        with col3:
            st.metric("ø Verladezeit", value = f"{out_time} min",)
        sum_wartend = df_CW_out['Ankunft Office'].count()
        sum_wartend = sum_wartend - sum_loaded
        #sum wartent to anteil in %
        sum_wartend2 = (sum_wartend / sum_of_loadings) * 100
        sum_wartend = str(sum_wartend)
        override_theme_1 = {'bgcolor': '#EFF8F7','progress_color': '#ef7d00'}
        sum_wartend = sum_wartend + ' CW'

        hc.progress_bar(sum_wartend2,f'Wartende LKW {sum_wartend} 🚛',override_theme=override_theme_1)
                
    def logo_and_Zahlen_inbound(df_inb):
        def time_to_timedelta(t):
            return pd.Timedelta(hours=t.hour, minutes=t.minute, seconds=t.second)
        
        try:
            # Konvertiere 'Wartezeit bis Entladebeginn' in timedelta-Objekte
            # to datetime
            df_inb['Wartezeit bis Entladebeginn'] = pd.to_datetime(df_inb['Wartezeit bis Entladebeginn'])
            df_CW_inb['Entladungszeit'] = pd.to_datetime(df_CW_inb['Entladungszeit'])
            df_inb['Wartezeit bis Entladebeginn'] = df_inb['Wartezeit bis Entladebeginn'].apply(time_to_timedelta)
            #Entladungszeit
            df_inb['Entladungszeit'] = df_inb['Entladungszeit'].apply(time_to_timedelta)
            # Berechne die Gesamtzeit in neue Spalte Entladegesamtzeit
            df_inb['Entladegesamtzeit'] = df_inb['Wartezeit bis Entladebeginn'] + df_inb['Entladungszeit']
            # Berechne den Durchschnitt der Entladegesamtzeit
            inb_time = df_inb['Entladegesamtzeit'].mean().seconds / 60
            # runde auf minuten
            inb_time = round(inb_time)
        except:
            inb_time = 0
            
        sum_of_loadings = df_inb['Soure Location'].count()
        
        # zähle Verladen + PGI' in 'Status Verladung '
        sum_GR = df_inb[df_inb['Status'] == 'Eingelagert']['Status'].count()

        col1, col2, col3 = st.columns([2,2,1],gap='small')
        
        with col1:
            outbound = Image.open('Data/img/Inbound.png', mode='r')
            st.image(outbound, use_column_width=True)    
        with col2:
            img_truck = truck_progress_png(sum_GR, sum_of_loadings)
            st.image(img_truck, use_column_width=True)
        with col3:  
            st.metric("ø Entladezeit", value = f"{inb_time} min",)# delta=" 95,6 % Servicelevel")

    def plotly_warehouse_stocks(df_CW_dds):
        # Entferne Zeilen mit NaN-Werten
        #df_CW_dds = df_CW_dds.dropna(subset=['Blocklager Paletten ist', 'Regalager Paletten ist'])

        df_CW_dds['Date'] = pd.to_datetime(df_CW_dds['Date'], errors='coerce').dt.date

        # Setze das aktuelle Datum auf das neueste Datum im DataFrame, wenn es innerhalb der letzten 5 Tage liegt
        current_date = min(datetime.date.today(), df_CW_dds['Date'].max())

        # Filtere df_CW_dds.Date zwischen heute und - 5 Werktage
        df_CW_dds = df_CW_dds[df_CW_dds['Date'] <= current_date]
        df_CW_dds = df_CW_dds[df_CW_dds['Date'] >= (current_date - datetime.timedelta(days=5))]

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

    ##### Show the Data #####
    #########################

    col1,col2,col3 = st.columns([4,2,1])
    img = Image.open('Data/img/Domestic_LOGO.png', mode='r')  
    with col1:
        st.image(img, width=250)
    with col2:
        max_stock = 2800
        free_space = max_stock - total_stock
        st.metric("Bestand", value = f"{total_stock} PAL", delta=f"{free_space} PAL Platz")
    with col3:
        on_table = st.toggle('Tabellen', False, key='tables_CW')
        
        
    col1,col2,col3,col4 = st.columns([3,1,1,1])
    with col1:
        st.write('')
    outbound(df_CW_out)
    logo_and_Zahlen_inbound(df_CW_inb)
    with st.expander('Lagerbestand', expanded=False):
        plotly_warehouse_stocks(df_CW_dds)
    if on_table:
        st.write('Outbound CW')
        st.dataframe(df_CW_out)
        st.write('Inbound CW')
        st.data_editor(df_CW_inb)
        st.write('DDS CW')
        st.data_editor(df_CW_dds)
  
def show_LC(df_LC_out, df_LC_inb, df_LC_dds, sel_date):

    try:
        df_dds = df_LC_dds
        df_dds['Date'] = pd.to_datetime(df_dds['Date'], errors='coerce').dt.date

        # Setze das aktuelle Date auf das neueste Date im DataFrame, wenn es innerhalb der letzten 5 Tage liegt
        # Stellen Sie sicher, dass 'Date' als datetime interpretiert wird
        df_dds['Date'] = pd.to_datetime(df_dds['Date'])
        # Filtere df_dds basierend auf dem aktuellen Datum
        # sel_date to datetime
        sel_date = pd.to_datetime(sel_date)
        df_dds = df_dds[df_dds['Date'] == sel_date]


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
        total_stock = df_dds['Total'].sum()
    except:
        
        total_stock = 0
    

    def outbound(df_LC_out):
      
        sum_of_loadings = df_LC_out['SCI'].count()
        
        # zähle Verladen + PGI' in 'Status Verladung '
        sum_loaded = df_LC_out[df_LC_out['Loaded at Bayreuth (Documents finished)'] != None]['Loaded at Bayreuth (Documents finished)'].count()
        # zähle Vorgestellt in 'Status Verladung '
        def time_to_timedelta(t):
            return pd.Timedelta(hours=t.hour, minutes=t.minute, seconds=t.second)
        try:
            df_LC_out = df_LC_out[df_LC_out['Verladungszeit Log-In'].notnull()]
            df_LC_out = df_LC_out[df_LC_out['Verladungszeit Log-In'] != '0']
            df_LC_out = df_LC_out[df_LC_out['Verladungszeit Log-In'] != '']
            # to datetime
            df_LC_out['Verladungszeit Log-In'] = pd.to_datetime(df_LC_out['Verladungszeit Log-In'])
            df_LC_out['Verladungszeit Log-In'] = df_LC_out['Verladungszeit Log-In'].apply(time_to_timedelta)
            out_time = df_LC_out['Verladungszeit Log-In'].mean().seconds / 60
            out_time = round(out_time)
        except:
            out_time = 0

        col1, col2, col3  = st.columns([2,2,1],gap='small')
        
        with col1:
            outbound = Image.open('Data/img/Outbound.png', mode='r')
            st.image(outbound, use_column_width=True)    
        with col2:
            img_truck = truck_progress_png(sum_loaded, sum_of_loadings)
            st.image(img_truck, use_column_width=True)
        with col3:
            st.metric("ø Verladezeit", value = f"{out_time} min",)
        sum_wartend = df_LC_out['Ankunft Office'].count()
        sum_wartend = sum_wartend - sum_loaded
        #sum wartent to anteil in %
        sum_wartend3 = (sum_wartend / sum_of_loadings) * 100
        sum_wartend = str(sum_wartend)
        sum_wartend = sum_wartend + ' LC'

        override_theme_1 = {'bgcolor': '#EFF8F7','progress_color': '#ef7d00'}
        hc.progress_bar(sum_wartend3,f'Wartende LKW {sum_wartend} 🚛',override_theme=override_theme_1)
                        
            
            
            
    def logo_and_Zahlen_inbound(df_inb):
        def time_to_timedelta(t):
            return pd.Timedelta(hours=t.hour, minutes=t.minute, seconds=t.second)
        
        try:
            # Konvertiere 'Wartezeit bis Entladebeginn' in timedelta-Objekte
            # to datetime
            df_inb['Automatisch berechnet.2'] = pd.to_datetime(df_inb['Automatisch berechnet.2'])
            df_inb['Automatisch berechnet.2'] = df_inb['Automatisch berechnet.2'].apply(time_to_timedelta)
            #Entladungszeit
            inb_time = df_inb['Automatisch berechnet.2'].mean().seconds / 60
            # runde auf minuten
            inb_time = round(inb_time)
        except:
            inb_time = 0
            
        sum_of_loadings = df_inb['Datum'].count()
        
        sum_GR = df_inb['Echtzeit Büro.1'].count()
        # zähle FG in 
        sum_unloadedFG = df_inb['Anzahl Paletten'].count()
        # zähle in in Vorbereitung 'Status Verladung '
        sum_unloadedWMS = df_inb['Anzahl Paletten.1'].count()

        col1, col2, col3 = st.columns([2,2,1],gap='small')
        
        with col1:
            outbound = Image.open('Data/img/Inbound.png', mode='r')
            st.image(outbound, use_column_width=True)    
        with col2:
            img_truck = truck_progress_png(sum_GR, sum_of_loadings)
            st.image(img_truck, use_column_width=True)
        with col3:  
            st.metric("ø Entladezeit", value = f"{inb_time} min",)# delta=" 95,6 % Servicelevel")

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
        df_dds = df_dds[df_dds['Date'] >= (current_date - datetime.timedelta(days=5))]

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
    
    
    col1,col2,col3 = st.columns([4,2,1])
    img = Image.open('Data/img/LC_LOGO.png', mode='r')  
    with col1:
        st.image(img, width=250)
    with col2:
        max_stock = 6959
        free_space = max_stock - total_stock
        st.metric("Bestand", value = f"{total_stock} PAL", delta=f"{free_space} PAL Platz")
    with col3:
        on_table = st.toggle('Tabellen', False, key='tables_LC')
    col1,col2,col3,col4 = st.columns([3,1,1,1])
    with col1:
        st.write('')
    outbound(df_LC_out)
    logo_and_Zahlen_inbound(df_LC_inb)
    with st.expander('Lagerbestand', expanded=False):
        plotly_warehouse_stocks(df_LC_dds)
    if on_table:
        #
        st.write('Outbound LC')
        st.dataframe(df_LC_out)
        st.write('Inbound LC')
        st.data_editor(df_LC_inb)
        st.write('DDS LC')
        st.data_editor(df_LC_dds)

def show_DIET(df_SFG_out, df_SFG_inb, df_SFG_dds, sel_date):
    try:
        df_dds = df_SFG_dds
        df_dds['Date'] = pd.to_datetime(df_dds['Date'], errors='coerce').dt.date
        df_dds['Date'] = pd.to_datetime(df_dds['Date'])

        sel_date = pd.to_datetime(sel_date)
        df_dds = df_dds[df_dds['Date'] == sel_date]
        df_dds['Total'] = df_dds['PMD ']
        total_stock = df_dds['PMD '].sum()

        if total_stock == 0:
            # so lange sel_date - Tag bis total_stock > 0
            
            while total_stock == 0:
                sel_date = sel_date - datetime.timedelta(days=1)
                df_dds = df_SFG_dds
                df_dds['Date'] = pd.to_datetime(df_dds['Date'], errors='coerce').dt.date
                df_dds['Date'] = pd.to_datetime(df_dds['Date'])
                df_dds = df_dds[df_dds['Date'] == sel_date]
                df_dds['Total'] = df_dds['PMD ']
                total_stock = df_dds['PMD '].sum()
        
    except:
        total_stock = 0


    def outbound(df_out):
      
        df_out = df_out.rename(columns={"Material Group:\nDiet\nCAF\nStaub\nPresize\nRohware": "TYPE"})
        # flter df_out["TYPE"] == 'Diet' oder DIET
        df_out = df_out[df_out['TYPE'].str.contains('Diet', case=False, na=False)]
        # zähle Vorgestellt in 'Status Verladung '
        sum_loadings = df_out["TYPE"].count()
        sum_finished = df_out[df_out['Ladeende'] != None]['Ladeende'].count()
        
        
        def time_to_timedelta(t):
            return pd.Timedelta(hours=t.hour, minutes=t.minute, seconds=t.second)
        try:
            # filter ist null 0 or NaN or empty df_CW_out['Wartezeit bis Verladebeginn']
            df_out = df_out[df_out['Dauer von Ankuft  bis Ladeende'].notnull()]
            df_out = df_out[df_out['Dauer von Ankuft  bis Ladeende'] != '0']
            df_out = df_out[df_out['Dauer von Ankuft  bis Ladeende'] != '']
            # to datetime
            df_out['Dauer von Ankuft  bis Ladeende'] = pd.to_datetime(df_out['Dauer von Ankuft  bis Ladeende'], errors='coerce').dt.time
            df_out['Dauer von Ankuft  bis Ladeende'] = df_out['Dauer von Ankuft  bis Ladeende'].apply(time_to_timedelta)
            out_time = df_out['Dauer von Ankuft  bis Ladeende'].mean().seconds / 60
            out_time = round(out_time)
        except:
            out_time = 0
        col1, col2, col3  = st.columns([2,2,1],gap='small')
        
        with col1:
            outbound = Image.open('Data/img/Outbound.png', mode='r')
            st.image(outbound, use_column_width=True)  
        with col2:
            img_truck = truck_progress_png(sum_finished, sum_loadings)
            st.image(img_truck, use_column_width=True)
        with col3:
            st.metric("ø Verladezeit", value = f"{out_time} min",)
        sum_wartend = df_out['Ankunft \nOffice\nDatum'].count()
        sum_wartend = sum_wartend - sum_finished
        #sum wartent to anteil in %
        sum_wartend2 = (sum_wartend / sum_loadings) * 100
        sum_wartend = str(sum_wartend)
        # add DIET to sum_wartend
        sum_wartend = sum_wartend + ' DIET'
        override_theme_1 = {'bgcolor': '#EFF8F7','progress_color': '#ef7d00'}
        hc.progress_bar(sum_wartend2,f'Wartende LKW {sum_wartend} 🚛',override_theme=override_theme_1)
            

    def plotly_warehouse_stocks(df_dds):

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
        fig.add_trace(go.Bar(x=df_dds['Date'], y=df_dds['PMD '], name='PMD ', marker_color='#0e2b63', text=df_dds['PMD '], textposition='auto'))
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
        
    col1,col2,col3 = st.columns([4,2,1])
    img = Image.open('Data/img/DIET_LOGO.png', mode='r')  
    with col1:
        st.image(img, width=250)
    with col2:
        max_stock = 6959
        free_space = max_stock - total_stock
        st.metric("Bestand", value = f"{total_stock} CS", delta=f"{free_space} CS Platz")
    with col3:
        on_table = st.toggle('Tabellen', False, key='tables_DIET')
        
    col1,col2,col3,col4 = st.columns([3,1,1,1])
    with col1:
        st.write('')
    outbound(df_SFG_out)
    with st.expander('Lagerbestand', expanded=False):
        plotly_warehouse_stocks(df_SFG_dds)
    if on_table:
        st.write('Outbound SFG')
        st.dataframe(df_SFG_out)
        
        st.write('Inbound SFG')
        st.data_editor(df_SFG_inb)
        
        st.write('DDS SFG')
        st.data_editor(df_SFG_dds)

def show_CF(df_SFG_out, df_SFG_inb, df_SFG_dds, sel_date):

    try:
        df_dds = df_SFG_dds
        df_dds['Date'] = pd.to_datetime(df_dds['Date'], errors='coerce').dt.date
        df_dds['Date'] = pd.to_datetime(df_dds['Date'])

        sel_date = pd.to_datetime(sel_date)
        df_dds = df_dds[df_dds['Date'] == sel_date]
        df_dds['Total'] = df_dds['C & F - Paletten']
        total_stock = df_dds['C & F - Paletten'].sum()

        if total_stock == 0:
            # so lange sel_date - Tag bis total_stock > 0
            
            while total_stock == 0:
                sel_date = sel_date - datetime.timedelta(days=1)
                df_dds = df_SFG_dds
                df_dds['Date'] = pd.to_datetime(df_dds['Date'], errors='coerce').dt.date
                df_dds['Date'] = pd.to_datetime(df_dds['Date'])
                df_dds = df_dds[df_dds['Date'] == sel_date]
                df_dds['Total'] = df_dds['C & F - Paletten']
                total_stock = df_dds['C & F - Paletten'].sum()
        
    except:
        total_stock = 0




    def outbound(df_out):
        # rename column "Material Group:\nDiet\nCAF\nStaub\nPresize\nRohware" to 'TYPE'
        df_out = df_out.rename(columns={"Material Group:\nDiet\nCAF\nStaub\nPresize\nRohware": "TYPE"})
        # flter df_out["TYPE"] == 'CAF'
        df_out = df_out[df_out["TYPE"] == 'CAF']
        # zähle Vorgestellt in 'Status Verladung '
        sum_loadings = df_out["TYPE"].count()
        sum_finished = df_out[df_out['Ladeende'] != None]['Ladeende'].count()        
        
        
        def time_to_timedelta(t):
            return pd.Timedelta(hours=t.hour, minutes=t.minute, seconds=t.second)
        try:
            # filter ist null 0 or NaN or empty df_CW_out['Wartezeit bis Verladebeginn']
            df_out = df_out[df_out['Dauer von Ankuft  bis Ladeende'].notnull()]
            df_out = df_out[df_out['Dauer von Ankuft  bis Ladeende'] != '0']
            df_out = df_out[df_out['Dauer von Ankuft  bis Ladeende'] != '']
            # to datetime
            df_out['Dauer von Ankuft  bis Ladeende'] = pd.to_datetime(df_out['Dauer von Ankuft  bis Ladeende'], errors='coerce').dt.time
            df_out['Dauer von Ankuft  bis Ladeende'] = df_out['Dauer von Ankuft  bis Ladeende'].apply(time_to_timedelta)
            out_time = df_out['Dauer von Ankuft  bis Ladeende'].mean().seconds / 60
            out_time = round(out_time)
        except:
            out_time = 0
        col1, col2, col3  = st.columns([2,2,1],gap='small')
        
        with col1:
            outbound = Image.open('Data/img/Outbound.png', mode='r')
            st.image(outbound, use_column_width=True)    
        with col2:
            img_truck = truck_progress_png(sum_finished, sum_loadings)
            st.image(img_truck, use_column_width=True)
        with col3:
            st.metric("ø Verladezeit", value = f"{out_time} min",)
        sum_wartend = df_out['Ankunft \nOffice\nDatum'].count()
        sum_wartend = sum_wartend - sum_finished
        #sum wartent to anteil in %
        sum_wartend3 = (sum_wartend / sum_loadings) * 100
        sum_wartend = str(sum_wartend)
        sum_wartend = sum_wartend + ' C&F'

        override_theme_1 = {'bgcolor': '#EFF8F7','progress_color': '#ef7d00'}
        hc.progress_bar(sum_wartend3,f'Wartende LKW {sum_wartend} 🚛',override_theme=override_theme_1)
            


    def plotly_warehouse_stocks(df_dds):

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
        
    col1,col2,col3 = st.columns([4,2,1])
    img = Image.open('Data/img/C&F_LOGO.png', mode='r')  
    with col1:
        st.image(img, width=250)
    with col2:
        max_stock = 700
        free_space = max_stock - total_stock
        st.metric("Bestand", value = f"{total_stock} PAL", delta=f"{free_space} PAL Platz")
    with col3:
        on_table = st.toggle('Tabellen', False, key='tables_CF')
        
    col1,col2,col3,col4 = st.columns([3,1,1,1])
    with col1:
        st.write('')
    outbound(df_SFG_out)
    with st.expander('Lagerbestand', expanded=False):
        plotly_warehouse_stocks(df_SFG_dds)
    if on_table:
        st.write('Outbound SFG')
        st.dataframe(df_SFG_out)
        
        st.write('Inbound SFG')
        st.data_editor(df_SFG_inb)
        
        st.write('DDS SFG')
        st.data_editor(df_SFG_dds)

def show_LEAF(df_SFG_out, df_SFG_inb, df_SFG_dds, sel_date):

    try:
        df_dds = df_SFG_dds
        df_dds['Date'] = pd.to_datetime(df_dds['Date'], errors='coerce').dt.date
        df_dds['Date'] = pd.to_datetime(df_dds['Date'])

        sel_date = pd.to_datetime(sel_date)
        df_dds = df_dds[df_dds['Date'] == sel_date]
        df_dds['Total'] = df_dds['LEAF - Kartons']
        total_stock = df_dds['LEAF - Kartons'].sum()

        if total_stock == 0:
            # so lange sel_date - Tag bis total_stock > 0
            
            while total_stock == 0:
                sel_date = sel_date - datetime.timedelta(days=1)
                df_dds = df_SFG_dds
                df_dds['Date'] = pd.to_datetime(df_dds['Date'], errors='coerce').dt.date
                df_dds['Date'] = pd.to_datetime(df_dds['Date'])
                df_dds = df_dds[df_dds['Date'] == sel_date]
                df_dds['Total'] = df_dds['LEAF - Kartons']
                total_stock = df_dds['LEAF - Kartons'].sum()
        
    except:
        total_stock = 0


    def logo_and_Zahlen_inbound(df_inb):
        def time_to_timedelta(t):
            return pd.Timedelta(hours=t.hour, minutes=t.minute, seconds=t.second)
        try:
            df_inb['Auto.6'] = df_inb['Auto.6'].apply(time_to_timedelta)
            #Entladungszeit
            inb_time = df_inb['Auto.6'].mean().seconds / 60
            # runde auf minuten
            inb_time = round(inb_time)
        except:
            inb_time = 0
            
        try:
            sum_of_loadings = df_inb['Category'].value_counts()['Leaf']
        except:
            sum_of_loadings = 0
        try:
            sum_finish_loads = (df_inb['Category'] == 'Leaf') & (df_inb['Status'] == 'Entladen')
            sum_finish_loads = sum_finish_loads.sum()
        except:
    
            sum_finish_loads = 0     
        
        
        col1, col2, col3 = st.columns([2,2,1],gap='small')
        
        with col1:
            outbound = Image.open('Data/img/Inbound.png', mode='r')
            st.image(outbound, use_column_width=True)    
        with col2:
            img_truck = truck_progress_png(sum_finish_loads, sum_of_loadings)
            st.image(img_truck, use_column_width=True)
        with col3:  
            st.metric("ø Entladezeit", value = f"{inb_time} min",)# delta=" 95,6 % Servicelevel")

    def plotly_warehouse_stocks(df_dds):

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
        fig.add_trace(go.Bar(x=df_dds['Date'], y=df_dds['LEAF - Kartons'], name='LEAF - Kartons', marker_color='#0e2b63', text=df_dds['LEAF - Kartons'], textposition='auto'))
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
        
    col1,col2,col3 = st.columns([4,2,1])
    img = Image.open('Data/img/LEAF_LOGO.png', mode='r')  
    with col1:
        st.image(img, width=250)
    with col2:
        max_stock = 6007
        free_space = max_stock - total_stock
        st.metric("Bestand", value = f"{total_stock} CS", delta=f"{free_space} CS Platz")
    with col3:
        on_table = st.toggle('Tabellen', False, key='tables_LEAF')
        
    col1,col2,col3,col4 = st.columns([3,1,1,1])
    with col1:
        st.write('')
    logo_and_Zahlen_inbound(df_SFG_inb)
    with st.expander('Lagerbestand', expanded=False):
        plotly_warehouse_stocks(df_SFG_dds)
    if on_table:
        st.write('Outbound SFG')
        st.dataframe(df_SFG_out)
        
        st.write('Inbound SFG')
        st.data_editor(df_SFG_inb)
        
        st.write('DDS SFG')
        st.data_editor(df_SFG_dds)

def main():
    
    st.warning('Offline bis Q4/2024')
    
    # with open( "style.css" ) as css:
    #     st.markdown( f'<style>{css.read()}</style>' , unsafe_allow_html= True)

    # col1, col2, col3 = st.columns([2,1,1])
    # with col1:  
    #     st.markdown("""
    #                 <style>
    #                 @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@700&display=swap');
    #                 </style>
    #                 <h2 style='text-align: left; color: #0F2B63; font-family: Montserrat; font-weight: bold;'>{}</h1>
    #                 """.format('Logistics Live Monitor'), unsafe_allow_html=True)   
    # with col2:
    #     sel_date = st.date_input('Datum', datetime.date.today())
    # with col3:
    #     with open('Data/appData/update_time_Ladeplan.json', 'r') as file:
    #         lastupdate = file.read()
    #     st.write('Stand: ' + lastupdate)
    #     if st.button('Aktualisieren'):
    #         with st.spinner('Aktualisierung startet...'):
    #             time.sleep(3)
    #             save_update_time()
    #             st.cache_data.clear()
    #             st.rerun()
    # img_strip = Image.open('Data/img/strip.png')   
    # img_strip = img_strip.resize((1000, 15))     
    # st.image(img_strip, use_column_width=True, caption='',)   


    # # schreibe die Funktionszeit in Konsole
    

    # df_CW_out, df_CW_inb, df_CW_dds  = load_data_CW()
    # df_CW_out = filter_data(df_CW_out,sel_date,'Ist Datum')
    # df_CW_inb = filter_data(df_CW_inb,sel_date,'Ist Datum')
    
    # # df_LC_out, df_LC_inb, df_LC_dds = load_data_LC()
    # # df_LC_out = filter_data(df_LC_out,sel_date,'Datum')
    # # df_LC_inb = filter_data(df_LC_inb,sel_date,'Datum')
    # df_SFG_out, df_SFG_inb, df_SFG_dds = load_data_SFG()
    # df_SFG_out = filter_data(df_SFG_out,sel_date,'Abholdatum Update')
    # df_SFG_inb = filter_data(df_SFG_inb,sel_date,'Ist Datum\n(Tatsächliche Anlieferung)')


    # col1,col2 = st.columns([1,1])
    # with col1:
    #     with st.container(border=True):
    #         show_LEAF(df_SFG_out, df_SFG_inb, df_SFG_dds, sel_date)
    # #     with st.container(border=True):
    # #         show_LC(df_LC_out, df_LC_inb, df_LC_dds,sel_date)
    # with col2:
    #     with st.container(border=True):
    #         show_domestic(df_CW_out, df_CW_inb, df_CW_dds,sel_date)
    # col1,col2 = st.columns([1,1])
    # with col1:
    #     with st.container(border=True):        
    #         show_DIET(df_SFG_out, df_SFG_inb, df_SFG_dds, sel_date)
    # with col2:
    #     with st.container(border=True):
    #         show_CF(df_SFG_out, df_SFG_inb, df_SFG_dds, sel_date)
    # col1,col2 = st.columns([1,1])
    # with col1:
    #     pass


    # # show_domestic(df_CW_out, df_CW_inb, df_CW_dds)
    # # show_SFG(df_SFG_out, df_SFG_inb, df_SFG_dds)
    # # show_LEAF(df_CW_out, df_CW_inb, df_CW_dds)
    # # show_CF(df_CW_out, df_CW_inb, df_CW_dds)
    