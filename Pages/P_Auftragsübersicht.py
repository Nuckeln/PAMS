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
            start_date = df['B'].min()
            end_date = df['B'].max()# + relativedelta(days=1)
            #slider 
            df['B'] = pd.to_datetime(df['B']).dt.date
            day1 = st.date_input('Startdatum', start_date)
            day2 = st.date_input('Enddatum', end_date)
            st.write('Du hast folgende Daten ausgewählt:', day1, 'bis', day2)
            mask = (df['B'] >= day1) & (df['B'] <= day2)
            df = df.loc[mask]
            

            def Tagesanalyse():
                Kunden = df.groupby(['L'])['Picks Gesamt'].sum().reset_index()#.sort_values(by='Picks Gesamt', ascending=False)
                #sort kunden by picks
                Kunden = Kunden.sort_values(by='Picks Gesamt', ascending=False)
                




            Tagesanalyse()

            
           

 


