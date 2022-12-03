import streamlit as st
import pandas as pd
import numpy as np
import datetime
from Data_Class.SQL import sql_datenLadenLabel,sql_datenLadenOderItems,sql_datenLadenStammdaten,sql_datenLadenOder
from Data_Class.DB_Daten_Agg import orderDatenAgg
from Data_Class.wetter.api import getWetterBayreuth

class LIVE:
    heute  = datetime.date.today()
    morgen =heute + datetime.timedelta(days=1)

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

def liveStatusPage(df,dfL):

    def headerAndWetter():
        col1, col2 = st.columns(2)
        with col1:
            st.title("Superdepot Live Status")
        with col2:
            wetter()

    def FilterNachDatum(day1, day2,df):
        df['PlannedDate'] = df['PlannedDate'].dt.strftime('%m/%d/%y')
        df['PlannedDate'] = df['PlannedDate'].astype('datetime64[ns]').dt.date
        #filter nach Datum
        df = df[(df['PlannedDate'] >= day1) & (df['PlannedDate'] <= day2)]
        #mask = (df['PlannedDate'] >= day1) & (df['PlannedDate'] <= day2)         
        #df = df.loc[mask]
        return df

    def FilterNachDatumLabel(day1, day2,df):
        # df['DATUM'] = df['DATUM'].dt.strftime('%m/%d/%y')
        # df['DATUM'] = df['DATUM'].astype('datetime64[ns]').dt.date
        #filter nach Datum
        df = df[(df['DATUM'] >= day1) & (df['DATUM'] <= day2)]


        return df

    def columnsKennzahlen(df,dfL):
        dfapicksDepot = df.groupby(['PlannedDate','DeliveryDepot'],dropna =False)['Picks Gesamt'].sum().reset_index()
        dfapicksOffen = df.groupby(['PlannedDate','AllSSCCLabelsPrinted'],dropna =False)['Picks Gesamt'].sum().reset_index()
        # dfapicksGeliefert = df.groupby(['PlannedDate','DeliveryDepot'],dropna =False)['Picks Geliefert'].sum().reset_index()
        


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
        st.dataframe(dfapicksOffen)
    
    
       
    
    # if seldate:
    #     df = FilterNachDatum(seldate,seldate,df)
    #     dfL = FilterNachDatumLabel(seldate,seldate,dfL)
    headerAndWetter()
    columnsKennzahlen(df,dfL)
    st.dataframe(df)

    st.dataframe(dfL)

    #df = df[df['SapOrderNumber'].isin(selLs)]

