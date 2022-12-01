import streamlit as st
import pandas as pd
import numpy as np
import datetime
from Data_Class.SQL import sql_datenLadenLabel,sql_datenLadenOderItems,sql_datenLadenStammdaten,sql_datenLadenOder
from Data_Class.DB_Daten_Agg import orderDatenAgg
from Data_Class.wetter.api import getWetterBayreuth

def sessionstate():
    if 'key' not in st.session_state:
        st.session_state['key'] = 'value'
    if 'key' not in st.session_state:
        st.session_state.key = +1
def wetter():
    df = getWetterBayreuth()
    temp = df.loc[0,'Temp']
    temp_max = df.loc[0,'Temp Max']
    temp_min = df.loc[0,'Temp Min']
    humidity = df.loc[0,'Humidity']
    wind_speed = df.loc[0,'Wind Speed']
    wind_degree = df.loc[0,'Wind Degree']
    clouds = df.loc[0,'Clouds']
    weather = df.loc[0,'Weather']
    #temp to int
    temp = int(temp)
    st.write(f"Temperatur: {temp}" + "°C")
    if weather == "Clouds":
        st.write("Wolkig")
    elif weather == "Rain":
        st.write("Regen")
    elif weather == "Clear":
        st.write("Klar")
    elif weather == "Snow":
        st.write("Schnee")
    else:
        st.write("Sonstiges")

def liveStatusPage(df):
###TODO: Wetter integrieren
    


    col1, col2 = st.columns(2)
    with col1:
        st.header("Superdepot Live Status")
    with col2:
        wetter()
    ls = df['SapOrderNumber'].unique()

    def FilterNachDatum(day1, day2,df):
        df['Pick Datum'] = df['PlannedDate'].dt.strftime('%m/%d/%y')
        df['Pick Datum'] = df['Pick Datum'].astype('datetime64[ns]').dt.date

        mask = (df['Pick Datum'] >= day1) & (df['Pick Datum'] <= day2)         
        df = df.loc[mask]
        return df
    seldate = st.date_input('Datum', datetime.date(2022, 11, 1))
    df = FilterNachDatum(seldate, seldate,df)
    df.groupby('Pick Datum')['SapOrderNumber'].count()



    #df = df[df['SapOrderNumber'].isin(selLs)]

    st.dataframe(df)