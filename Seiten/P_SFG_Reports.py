import pandas as pd
import numpy as np
import streamlit as st
from Data_Class.MMSQL_connection import read_Table
import plotly.express as px
import plotly.graph_objs as go
from PIL import Image



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

# "Loading Date Plan DHL" TERMIN
# Pick-up date update Tatsächliche abholung

def read_data():
    df = read_Table('PAMS_SFG_SDDS_Outbound_Monitor')

    df["Abholdatum Update"] = pd.to_datetime(df["Abholdatum Update"], errors='coerce')
    df = df.rename(columns={"Abholdatum Update": "Pick-up date update"})
    df["Loading Date Plan DHL"] = pd.to_datetime(df["Loading Date Plan DHL"], errors='coerce')
    df["Difference in days"] = df["Pick-up date update"] - df["Loading Date Plan DHL"]
    df["Loading Plan KW"] = df["Loading Date Plan DHL"].dt.strftime('%U')
    df["Loading Plan Month"] = df["Loading Date Plan DHL"].dt.strftime('%Y-%m') 
    return df 


    # df = df.dropna(subset=["Loading Date Plan DHL"])
    # df = df.dropna(subset=["Abholdatum Update"])
    # df = df.dropna(subset=["SCI"])
    # df = df[df["SCI"].str.isnumeric()]

def date_filter(df, sel_day_ref, sel_von_bis, sel_from, sel_to):
    df = df.copy()
    df = df[df[sel_day_ref] >= sel_from]
    df = df[df[sel_day_ref] <= sel_to]
    


def user_selection(df):
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        df = df.rename(columns={"Material Group:\nDiet\nCAF\nStaub\nPresize\nRohware": "TYPE"})
        sel_fachbereich = st.selectbox('Fachbereich', df['TYPE'].unique())
        df = df[df["TYPE"] == sel_fachbereich]
    with col2:
        with st.container(border=True):
            sel_day_ref = st.radio('Referenz Tag', ['Pick-up date update'],horizontal=True)
    with col3:
        with st.container(border=True):
            sel_von_bis = st.radio('Zeitraum', ['Tag', 'Woche', 'Monat'],horizontal=True)
            
    col1, col2 = st.columns([1, 1])
    with st.container(border=True):
        with col1:
            sel_from = col1.date_input('Von', pd.Timestamp.now() - pd.Timedelta(days=20))
        with col2:
            sel_to = col2.date_input('Bis', pd.Timestamp.now())
    
        return df
    
def plot_data(df):
    import matplotlib.pyplot as plt
    data = df.copy()
    # Prepare data
    data['Loading Date Plan DHL'] = pd.to_datetime(data['Loading Date Plan DHL'], errors='coerce')
    data['Pick-up date update'] = pd.to_datetime(data['Pick-up date update'], errors='coerce')

    # Count planned and actual transports
    planned_transports = data['Loading Date Plan DHL'].value_counts().sort_index()
    actual_transports = data['Pick-up date update'].value_counts().sort_index()

    # Create a DataFrame for plotting
    transport_counts = pd.DataFrame({
        'Planned Transports': planned_transports,
        'Actual Transports': actual_transports
    })

    # Fill NaN values with 0 as they represent days with no transports
    transport_counts.fillna(0, inplace=True)

    # Plot
    plt.figure(figsize=(14, 6))
    transport_counts.plot(kind='bar', color=['skyblue', 'green'])
    plt.title('Planned vs Actual Transports by Date')
    plt.xlabel('Date')
    plt.ylabel('Number of Transports')
    plt.xticks(rotation=45)
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.legend()
    plt.tight_layout()
    st.pyplot(plt)
    
def main():
    df = read_data()
    pd.set_option("display.precision", 2)
    df = user_selection(df)
    img_strip = Image.open('Data/img/strip.png')   
    img_strip = img_strip.resize((1000, 15))  
    st.image(img_strip, use_column_width=True)
    st.data_editor(df)
    df = df[df["Pick-up date update"] >= pd.Timestamp.now() - pd.Timedelta(days=20)]
    plot_data(df)
    # Filter für die letzten 20 Tage
    # df = df[df["Pick-up date update"] >= pd.Timestamp.now() - pd.Timedelta(days=20)]

    
