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
import altair as alt
import plotly.express as px

class Forecast:
        
        def LadeForecast(self):
            
            st.header("Forecast")
            st.write("Hier kannst du sehen wie sich die Daten entwickeln")
            st.write("Datenzeitraum ab 01.04.2022")
            df = pd.read_csv('Data/valid.csv', sep=';')
            #rename columns
            df = df.rename(columns={'Unnamed: 0': 'Date'})
            df = df[-15:]
            #df Picks Gesamt to int
            df['Picks Gesamt'] = df['Picks Gesamt'].astype(int)
            df['Predictions'] = df['Predictions'].astype(int)


            # create pltoly figure of df by Date bar1 is Picks Gesamt Bar2 is Predictions
            fig = go.Figure()
            fig.add_trace(go.Bar(x=df['Date'], y=df['Picks Gesamt'], name='Picks Gesamt'))
            fig.add_trace(go.Bar(x=df['Date'], y=df['Predictions'], name='Predictions'))
            fig.update_layout(barmode='group')
            st.plotly_chart(fig)
            df['Abweichung'] = (1 - (df ['Predictions'] / df ['Picks Gesamt'])) * 100
            #df['Abweichung'] in %
            df['Abweichung'] = df['Abweichung'].round(2)
            # create pltoly figure of df by Date bar1 is Picks Gesamt Bar2 is Predictions and line is Abweichung on top
            fig = go.Figure()
            fig.add_trace(go.Bar(x=df['Date'], y=df['Picks Gesamt'], name='Picks Gesamt'))
            fig.add_trace(go.Bar(x=df['Date'], y=df['Predictions'], name='Predictions'))
            fig.add_trace(go.Scatter
            (x=df['Date'], y=df['Abweichung'], name='Abweichung', line=dict(color='firebrick', width=4)))
            fig.update_layout(barmode='group')
            st.plotly_chart(fig)
            # create pltoly figure of df by Date line is Abweichung
            fig = go.Figure()
            fig.add_trace(go.Scatter
            (x=df['Date'], y=df['Abweichung'], name='Abweichung', line=dict(color='firebrick', width=4, dash='dot')))
            st.plotly_chart(fig)

            # create pltoly figure of df by Date line is Abweichung

            
            st.dataframe(df)