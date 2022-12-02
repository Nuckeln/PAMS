import streamlit as st
import pandas as pd
import numpy as np
import datetime
from Data_Class.SQL import sql_datenLadenLabel,sql_datenLadenOderItems,sql_datenLadenStammdaten,sql_datenLadenOder
from Data_Class.DB_Daten_Agg import orderDatenAgg
from Data_Class.wetter.api import getWetterBayreuth

class LIVE:
    day1 = datetime.date.today()
    day2 = day1 - datetime.timedelta(days=30)

    def __init__(self,df):
        self.df = df




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
        st.title("Superdepot Live Status")
    with col2:
        wetter()
    ls = df['SapOrderNumber'].unique()

    def FilterNachDatum(day1, day2,df):
        df['Pick Datum'] = df['PlannedDate'].dt.strftime('%m/%d/%y')
        df['Pick Datum'] = df['Pick Datum'].astype('datetime64[ns]').dt.date
        mask = (df['Pick Datum'] >= day1) & (df['Pick Datum'] <= day2)         
        df = df.loc[mask]
        return df
    seldate = st.date_input('Datum', LIVE.day1)
    if seldate:
        df = FilterNachDatum(seldate,seldate,df)
    st.dataframe(df)    

    def columnsKennzahlen(df):
        dfapicksDepot = df.groupby(['Pick Datum','DeliveryDepot'],dropna =False)['Picks Gesamt'].sum().reset_index()
        # dfapicksOffen = df.groupby(['Pick Datum','DeliveryDepot'],dropna =False)['Picks Offen'].sum().reset_index()
        # dfapicksGeliefert = df.groupby(['Pick Datum','DeliveryDepot'],dropna =False)['Picks Geliefert'].sum().reset_index()



        col1, col2, col3 = st.columns(3)
        with col1:
            st.subheader("Gesamt Picks Tag")
            dfapicksDepot = df.groupby(['DeliveryDepot'],dropna =False)['Picks Gesamt'].sum().reset_index()
            pickges = dfapicksDepot['Picks Gesamt'].sum()
            st.write(f"Gesamtvolumen:  {pickges}")
            #---##---#
            dfapicksDepotKNSTR = dfapicksDepot.loc[dfapicksDepot['DeliveryDepot']=='KNSTR']
            picksStr = dfapicksDepotKNSTR['Picks Gesamt'].sum()
            st.write(f"Stuttgart:  {picksStr}")
            #---##---#
            dfapicksDepotKNLEJ = dfapicksDepot.loc[dfapicksDepot['DeliveryDepot']=='KNLEJ']
            picksLej = dfapicksDepotKNLEJ['Picks Gesamt'].sum()
            st.write(f"Leipzig:  {picksLej}")
        with col2:
            st.subheader("Noch zu Picken")
            
        with col3:
            st.subheader("Fertig")

    columnsKennzahlen(df)
    st.dataframe(df)

    #df = df[df['SapOrderNumber'].isin(selLs)]

