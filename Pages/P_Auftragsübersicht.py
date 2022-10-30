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
            # rename df['L'] to 'Kunde'
            df.rename(columns={'L': 'Kunde'}, inplace=True)
            df.rename(columns={'A': 'Lieferschein'}, inplace=True)

            
            day1 = st.sidebar.date_input('Startdatum', start_date)
            btnTages = st.sidebar.button('Tagesanalyse')

            day2 = st.sidebar.date_input('Enddatum', end_date)
            wochen = st.sidebar.selectbox('Wochen', df['Kalender Woche'].unique())
            monate = st.sidebar.selectbox('Monate', ['Tag', 'Woche', 'Monat', 'Jahr'])

            def FilterNachDatum(day1, day2,df):
                mask = (df['Pick Datum'] >= day1) & (df['Pick Datum'] <= day2)         
                df = df.loc[mask]
                return df
            def FilterNachWochen(wochen):
                mask = (df['Kalender Woche'] == wochen)
                df = df.loc[mask]
            def FilterNachMonate(monate):
                mask = (df['Monat'] == monate)
                df = df.loc[mask]

            def Tagesanalyse(df):
                st.header('Auftragsübersicht Tagesanalyse')
                # ----- Datenfiltern -----
                picks = df.groupby(['Lieferschein','Pick Datum'])['Picks Gesamt'].sum().reset_index()
                picksinCS = df.groupby(['Lieferschein','Pick Datum'])['Picks CS'].sum().reset_index()
                picksinPAL = df.groupby(['Lieferschein','Pick Datum'])['Picks PAL'].sum().reset_index()
                picksinOUT = df.groupby(['Lieferschein','Pick Datum'])['Picks OUT'].sum().reset_index()
                kunden = pd.merge(picks, picksinCS[['Lieferschein','Picks CS']],left_on='Lieferschein', right_on='Lieferschein',how='left')
                kunden = pd.merge(kunden, picksinPAL[['Lieferschein','Picks PAL']],left_on='Lieferschein', right_on='Lieferschein',how='left')
                kunden = pd.merge(kunden, picksinOUT[['Lieferschein','Picks OUT']],left_on='Lieferschein', right_on='Lieferschein',how='left')
                
                ## ----- Hardfacts Auftragsübersicht -----
                picksGesamt = int(df["Picks Gesamt"].sum())
                picksOUT = int(df["Picks OUT"].sum())
                picksCS = int(df["Picks CS"].sum())
                picksPAL = int(df["Picks PAL"].sum())
            ## ----- Kennzahlen Liefertag-----##
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"Datum: {day1}")
                    st.write(f"Anzahl Lieferschiene: {picksGesamt}")
                    st.write(f"Gesamt Picks: {picksGesamt}")
                with col2:
                    st.write(f"Anzahl Stangen: {picksOUT}")
                    st.write(f"Anzahl Karton: {picksCS}")
                    st.write(f"Anzahl Paletten: {picksPAL}")
            ### ----- Chart  Auftragsübersicht -----
                fig = go.Figure()
                fig.add_trace(go.Bar(x=kunden['Pick Datum'], y=kunden['Picks Gesamt'], name='Picks Gesamt'))

                fig.update_layout(barmode='stack', title_text='Auftragsübersicht Tagesanalyse')
                st.plotly_chart(fig)
                st.write(kunden)
                



            def Zeitraumanalyse(df):
                Kunden = df.groupby(['Kunde','Pick Datum'])['Picks Gesamt'].sum().reset_index()
                Kunden = Kunden.sort_values(by='Picks Gesamt', ascending=False)
                st.bar_chart(Kunden,x='Kunde', y='Picks Gesamt', width=0, height=0, use_container_width=True)
                st.dataframe(Kunden)



            if btnTages:
                df = FilterNachDatum(day1, day1,df)
                Tagesanalyse(df)



            

            



            

                




            

            
           

 


