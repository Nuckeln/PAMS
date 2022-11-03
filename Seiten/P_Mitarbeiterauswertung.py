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

class Seite1:
        
        def Ladeseite(self, dfDaten):
            
            st.header('Mitarbeiter im Detail')
            userauswahl = pd.Series(dfDaten['Name'].unique())
            userselection = st.sidebar.selectbox("Mitarbeiter", list(userauswahl))

            # ----- Datenfiltern -----
            #Nach User
            dfDaten['Pick Datum']= pd.to_datetime(dfDaten['Pick Datum']).dt.date
            dfAll = dfDaten
            #Nach Datum
            start_date = st.sidebar.date_input('Start Datum :',dfDaten['Pick Datum'].max(),min_value=dfDaten['Pick Datum'].min(),max_value=dfDaten['Pick Datum'].max())
            mask = (dfDaten['Pick Datum'] == start_date)
            df = dfDaten.loc[mask]
            df = df[df['Name'] == userselection]
            #----- Daten Mitarbeiter--------#
            pickscs= int(df["Picks CS"].sum())
            picksout= int(df["Picks OUT"].sum())
            pickspal= int(df["PICKS PAL"].sum())
            #labelerstellt= int(df["Label"].sum())
            lieferscheine = df['V'].nunique()
            ## ----- Kennzahlen Mitarbeiter-----##
            
            left_column, middle_column, right_column = st.columns(3)
            with left_column:
                st.write(userselection)
            with middle_column:
                st.write(f"Stangen: {picksout:,}")
                st.write(f"Kartons Gesamt: {pickscs:,}")
                st.write(f"Paletten Gesamt: {pickspal:,}")
            with right_column:
                st.write(f"Bearbeitete Lieferscheine: {lieferscheine:,}")
                #st.write(f"Label erstellt: {labelerstellt:,}")
                st.write(f"GesamtPicks: {pickscs + picksout + pickspal:,}")
                st.write(f"Picks/h: {(pickscs + picksout + pickspal) / 7.5:,}")
            
            
            # ----- Tabelle -----#   
            random_x = [pickscs, picksout, pickspal] 
            names = ['CS', 'OUT', 'PAL'] 
            fig = px.pie(values=random_x, names=names)
            fig.update_layout(margin=dict(t=20, b=20, l=20, r=20)) 
            # ------ DIAGRAMM ------ #
            st.bar_chart(data=df,x='Pick Zeit',y=['Picks CS','Picks OUT','PICKS PAL','Label'])
            st.dataframe(df)
            st.plotly_chart(fig)
