import streamlit as st
import pandas as pd
import numpy as np
import datetime
import streamlit_autorefresh as sar
from PIL import Image
import plotly_express as px
import plotly.graph_objects as go
from annotated_text import annotated_text, annotation

from Data_Class.wetter.api import getWetterBayreuth
from Data_Class.SQL import read_table
from Data_Class.AzureStorage_dev import get_blob_list_dev, get_file_dev
import matplotlib.pyplot as plt
from io import BytesIO
import matplotlib.pyplot as plt
from PIL import Image
import numpy as np


@st.cache_data
def load_data_CW():
    data = get_file_dev("CW_DDS.xlsm")
    df_outbound = pd.read_excel(BytesIO(data),sheet_name='Outbound_Monitor')
    df_inbound = pd.read_excel(BytesIO(data), sheet_name='Inbound_Monitor')
    # setze die erste Zeile als Spaltennamen
    df_outbound.columns = df_outbound.iloc[0]
    # entferne die ersten 2 Zeilenx
    df_outbound = df_outbound[2:]
    #df_inbound.columns = df_inbound.iloc[0]
    #df_inbound = df_inbound[2:]
    return df_outbound, df_inbound

#@st.cache_data
def load_data_SFG():
    data = get_file_dev("SFG_DDS.xlsx")
    df = pd.read_excel(BytesIO(data))
    df = df[2:]
    return df
    
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
    ax.barh([''], [percentage], color='#50af47')
    ax.barh([''], [100-percentage], left=[percentage], color='#ef7d00')

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
def show_raw_data(df_CW_out, df_CW_inb, df_SFG):

    st.write('Outbound CW')
    st.dataframe(df_CW_out)
    st.write('Inbound CW')
    st.data_editor(df_CW_inb)
    st.write('SFG')
    st.data_editor(df_SFG)


def filter_data(df, date, useCol):
    df[useCol] = pd.to_datetime(df[useCol], errors='coerce').dt.date
    df = df[df[useCol] == date]
    return df

def show_DIET(df):
    #load logo
    img = Image.open('Data/img/DIET_LOGO.png', mode='r')
    st.image(img, width=300)
    sum_of_loadings = df['Destination City'].count()
    
    # zähle Verladen + PGI' in 'Status Verladung '
    sum_loaded = df[df['Status Verladung '] == 'Verladen']['Status Verladung '].count()
    # zähle Vorgestellt in 'Status Verladung '
    sum_prepared = df[df['Status Verladung '] == 'Vorgestellt']['Status Verladung '].count()
    # zähle in in Vorbereitung 'Status Verladung '
    sum_on_preparation = df[df['Status Verladung '] == 'in Vorbereitung']['Status Verladung '].count()
    # Zähle Gestrichen in 'Status Verladung '
    sum_canceled = df[df['Status Verladung '] == 'Gestrichen']['Status Verladung '].count()
    
    
    img_truck = truck_progress_png(sum_of_loadings, 40)
    st.image(img_truck, width=250)
    
    annotated_text(annotation(f'Verladene Trucks: {sum_loaded}', '', "#50af47", font_family="Montserrat"))
    annotated_text(annotation(f'Vorgestellte Trucks: {sum_prepared}', '', "#afca0b", font_family="Montserrat"))
    annotated_text(annotation(f'Trucks in Vorbereitung: {sum_on_preparation}', '', "#ef7d00", font_family="Montserrat"))
    annotated_text(annotation(f'Gestrichene Trucks: {sum_canceled}', '', "#e72582", font_family="Montserrat"))
    

def show_domestic(df):
    #load logo
    img = Image.open('Data/img/Domestic_LOGO.png', mode='r')
    st.image(img, width=320)
    sum_of_loadings = df['Destination City'].count()
    
    # zähle Verladen + PGI' in 'Status Verladung '
    sum_loaded = df[df['Status Verladung '] == 'Verladen']['Status Verladung '].count()
    # zähle Vorgestellt in 'Status Verladung '
    sum_prepared = df[df['Status Verladung '] == 'Vorgestellt']['Status Verladung '].count()
    # zähle in in Vorbereitung 'Status Verladung '
    sum_on_preparation = df[df['Status Verladung '] == 'in Vorbereitung']['Status Verladung '].count()
    # Zähle Gestrichen in 'Status Verladung '
    sum_canceled = df[df['Status Verladung '] == 'Gestrichen']['Status Verladung '].count()
    
    
    img_truck = truck_progress_png(sum_of_loadings, 40)
    st.image(img_truck, width=250)
    
    annotated_text(annotation(f'Verladene Trucks: {sum_loaded}', '', "#50af47", font_family="Montserrat"))
    annotated_text(annotation(f'Vorgestellte Trucks: {sum_prepared}', '', "#afca0b", font_family="Montserrat"))
    annotated_text(annotation(f'Trucks in Vorbereitung: {sum_on_preparation}', '', "#ef7d00", font_family="Montserrat"))
    annotated_text(annotation(f'Gestrichene Trucks: {sum_canceled}', '', "#e72582", font_family="Montserrat"))
    


def main():
    st.title('Ladeplan')

    sel_date = st.date_input('Datum', datetime.date.today())
    df_CW_out, df_CW_inb  = load_data_CW()
    df_CW_out = filter_data(df_CW_out,sel_date,'Ist Datum')
    df_SFG = load_data_SFG()

    st.markdown(
        """
        <style>
            div[data-testid="column"]:nth-of-type(1)
            {
                
            } 

            div[data-testid="column"]:nth-of-type(2)
            {
                border:2px solid blue;
                text-align: right;
            } 
        </style>
        """,unsafe_allow_html=True
    )
   
    
    col1, col2 = st.columns(2)
    with col1:
        show_domestic(df_CW_out)
    with col2:
        show_DIET(df_CW_out)
    
    show_raw_data(df_CW_out, df_CW_inb, df_SFG)
    
    #anwesenheit()
    
    #df_SFG = filter_data(df_SFG,sel_date,'Ist Datum (Tatsächliche Anlieferung)')
    
    #st.data_editor  (df_CW)
    