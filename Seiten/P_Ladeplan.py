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

@st.cache_data
def load_data_SFG():
    data = get_file_dev("SFG_DDS.xlsx")
    df = pd.read_excel(BytesIO(data))
    df = df[2:]
    return df
    
def anwesenheit():
     img = Image.open('Data/img/Mitarbeiter/micha.png', mode='r')
     st.image(img, width=200)

#filter the data by Date
def show_raw_data(df_CW_out, df_CW_inb, df_SFG):

    st.write('Outbound CW')
    st.dataframe(df_CW_out)
    st.write('Inbound CW')
    st.data_editor(df_CW_inb)
    st.write('SFG')
    st.data_editor(df_SFG)


def filter_data(df, date,useCol):
    df[useCol] = df[useCol].astype('datetime64[ns]').dt.date
    df = df[df[useCol] == date]
    return df

def show_DIET(df):
    #load logo
    img = Image.open('Data/img/DIET_LOGO.png', mode='r')
    st.image(img, width=200)

def show_domestic(df):
    #load logo
    img = Image.open('Data/img/Domestic_LOGO.png', mode='r')
    st.image(img, width=200)
    


def main():
    st.title('Ladeplan')

    sel_date = st.date_input('Datum', datetime.date.today())
    
    df_CW_out, df_CW_inb  = load_data_CW()
    df_SFG = load_data_SFG()
    show_raw_data(df_CW_out, df_CW_inb, df_SFG)
    
    col1, col2 = st.columns(2)
    with col1:
        show_domestic(df_CW_out)
    with col2:
        show_DIET(df_CW_out)
    
    
    #anwesenheit()
    
    #df_SFG = filter_data(df_SFG,sel_date,'Ist Datum (Tatsächliche Anlieferung)')
    
    #st.data_editor  (df_CW)
    