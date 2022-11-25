import streamlit as st
import pandas as pd
import numpy as np
import datetime
from data_Class.SQL import sql_datenLadenLabel,sql_datenLadenOderItems,sql_datenLadenStammdaten,sql_datenLadenOder
from data_Class.DB_Daten_Agg import test
from data_Class.wether.api import getWetterBayreuth

def sessionstate():
    if 'key' not in st.session_state:
        st.session_state['key'] = 'value'
    if 'key' not in st.session_state:
        st.session_state.key = +1
def filterNachDatum(day1, day2,df):
    # df['PlannedDate'] to date
    df['PlannedDate'] = pd.to_datetime(df['PlannedDate'])
    mask = (df['PlannedDate'] >= day1) & (df['PlannedDate'] <= day2)         
    df = df.loc[mask]
    return df

def liveStatusPage(df):
###TODO: Wetter integrieren
       
    day1 = st.date_input('Start Date', value=pd.to_datetime('today'))
    day2 = st.date_input('End Date', value=pd.to_datetime('today'))
    df["Verladetag"] = pd.to_datetime(df["PlannedDate"]).dt.date
    mask = (df['Verladetag'] >= day1) & (df['Verladetag'] <= day2)
    df = df.loc[mask]
    #dfapicksinPAL = dfa.groupby(['Lieferschein','Pick Datum'])['Picks PAL'].sum().reset_index()
    a = df.groupby(['Verladetag'])['Picks Gesamt'].sum().reset_index()
    st.write(a)
    #df = fil   terNachDatum(day1, day2,df)
    st.write(df)
    