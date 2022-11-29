import streamlit as st
import pandas as pd
import numpy as np
import datetime
from data_Class.SQL import sql_datenLadenLabel,sql_datenLadenOderItems,sql_datenLadenStammdaten,sql_datenLadenOder
from data_Class.DB_Daten_Agg import orderDatenAgg
from data_Class.wetter.api import getWetterBayreuth

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

    st.write("Wetter")
    st.write("Temperatur: ",temp)
    if clouds > 0:
        st.write("Wolken: ",clouds)
# def filterNachDatum(day1, day2,df):
#     # df['PlannedDate'] to date
        
    
#     df['PlannedDate'] = pd.to_datetime(df['PlannedDate'])
#     df['Pick Datum'] = df['PlannedDate'].dt.strftime('%m/%d/%y')
#     mask = (df['PlannedDate'] >= day1) & (df['PlannedDate'] <= day2)         
#     df = df.loc[mask]
#     return df


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


    seldate = st.date_input('Datum', datetime.date(df['PlannedDate'].min().year,df['PlannedDate'].min().month,df['PlannedDate'].min().day))
    seldate2 = st.date_input('Datum', datetime.date(df['PlannedDate'].max().year,df['PlannedDate'].max().month,df['PlannedDate'].max().day))


    #
    df = FilterNachDatum(seldate, seldate2,df)

    #df = df[df['SapOrderNumber'].isin(selLs)]

    st.dataframe(df)