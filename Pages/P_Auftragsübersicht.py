from distutils.log import info
from email.header import Header
from enum import unique
from itertools import count
import datetime
from folium import Tooltip
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from requests import head
import streamlit as st
from PIL import Image
from dateutil.relativedelta import relativedelta # to add days or years

class Page_Auftragsübersicht:
        
        def LadeAuftragsübersicht(self, df):
            # ----- Datenfiltern -----
            # kleinstes Pick Datum
            start_date = df['B'].min()
            # größtes Pick Datum
            end_date = df['B'].max()# + relativedelta(days=1)          
            #Pick Datum zu Datetime 
            df['Pick Datum'] = pd.to_datetime(df['B']).dt.date
            
            day1 = st.sidebar.date_input('Startdatum', start_date)
            btnTages = st.sidebar.button('Tagesanalyse')

            day2 = st.sidebar.date_input('Enddatum', end_date)
            wochen = st.sidebar.selectbox('Wochen', df['Kalender Woche'].unique())
            monate = st.sidebar.selectbox('Monate', ['Tag', 'Woche', 'Monat', 'Jahr'])

            def FilterNachDatum(day1, day2):
                mask = (df['Pick Datum'] >= day1) & (df['Pick Datum'] <= day2)         
                df = df.loc[mask]
            def FilterNachWochen(wochen):
                mask = (df['Kalender Woche'] == wochen)
                df = df.loc[mask]
            def FilterNachMonate(monate):
                mask = (df['Monat'] == monate)
                df = df.loc[mask]


            def Tagesanalyse():
                Kunden = df.groupby(['L','Pick Datum'])['Picks Gesamt'].sum().reset_index()
                Kunden = Kunden.sort_values(by='Picks Gesamt', ascending=False)
                st.bar_chart(Kunden,x='Pick Datum', y='Picks Gesamt', width=0, height=0, use_container_width=True)
                st.dataframe(Kunden)



            if btnTages:
                day2 = day1
                Tagesanalyse()


            

            



            

                




            

            
           

 


