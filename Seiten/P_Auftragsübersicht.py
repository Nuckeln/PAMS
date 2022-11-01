
import datetime
from folium import Tooltip
from matplotlib.pyplot import legend
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from requests import head
import streamlit as st
from PIL import Image

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

            
            day1 = st.sidebar.date_input('Startdatum', end_date, min_value=start_date, max_value=end_date)
            btnTages = st.sidebar.button('Tagesanalyse')

            day2 = st.sidebar.date_input('Enddatum', end_date, max_value=end_date, min_value=start_date)
            wochen = st.sidebar.selectbox('Wochen', df['Kalender Woche'].unique())
            #monate = st.sidebar.selectbox('Monate', ['Tag', 'Woche', 'Monat', 'Jahr'])

            def FilterNachDatum(day1, day2,df):
                mask = (df['Pick Datum'] >= day1) & (df['Pick Datum'] <= day2)         
                df = df.loc[mask]
                return df
            def FilterNachWochen(wochen):
                mask = (df['Kalender Woche'] == wochen)
                df = df.loc[mask]
            #def FilterNachMonate(monate):
                mask = (df['Monat'] == monate)
                df = df.loc[mask]
            def DatenKundeaufbereiten(dfa):
                # DataFrame Picks zu Kunden
                dfapicks = dfa.groupby(['Lieferschein','Pick Datum','Kunde'],dropna =False)['Picks Gesamt'].sum().reset_index()
                dfapicksinCS = dfa.groupby(['Lieferschein','Pick Datum'])['Picks CS'].sum().reset_index()
                dfapicksinPAL = dfa.groupby(['Lieferschein','Pick Datum'])['Picks PAL'].sum().reset_index()
                dfapicksinOUT = dfa.groupby(['Lieferschein','Pick Datum'])['Picks OUT'].sum().reset_index()
                dfakunden = pd.merge(dfapicks, dfapicksinCS[['Lieferschein','Picks CS']],left_on='Lieferschein', right_on='Lieferschein',how='left')
                dfakunden = pd.merge(dfakunden, dfapicksinOUT[['Lieferschein','Picks OUT']],left_on='Lieferschein', right_on='Lieferschein',how='left')
                dfakunden = pd.merge(dfakunden, dfapicksinPAL[['Lieferschein','Picks PAL']],left_on='Lieferschein', right_on='Lieferschein',how='left')
                # DataFrame Picks zu Tag
                return dfakunden
            def DatenPickTagaufbereiten(dfT):
                dfaPicksTag = dfT.groupby(['Pick Datum'])['Picks Gesamt'].sum().reset_index()
                dfaCStag = dfT.groupby(['Pick Datum'])['Picks CS'].sum().reset_index()   
                dfaPALtag = dfT.groupby(['Pick Datum'])['Picks PAL'].sum().reset_index()      
                dfaOUTtag = dfT.groupby(['Pick Datum'])['Picks OUT'].sum().reset_index()
                dfaZugriffe = pd.merge(dfaPicksTag, dfaCStag[['Pick Datum','Picks CS']],left_on='Pick Datum', right_on='Pick Datum',how='left')         
                dfaZugriffe = pd.merge(dfaZugriffe, dfaOUTtag[['Pick Datum','Picks OUT']],left_on='Pick Datum', right_on='Pick Datum',how='left')
                dfaZugriffe = pd.merge(dfaZugriffe, dfaPALtag[['Pick Datum','Picks PAL']],left_on='Pick Datum', right_on='Pick Datum',how='left')
                return dfaZugriffe

                # ----- Hardfacts Auftragsübersicht -----
            def Tagesanalyse(df, dfakunden):
                st.header('Auftragsübersicht Tagesanalyse')
                # ----- Datenfiltern -----            
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
                fig = px.bar(dfakunden, x="Kunde", y="Picks Gesamt", barmode="group", title="Auftragsübersicht")
                st.plotly_chart(fig)

            def Zeitraumanalyse(df,dfakunden,dfaPicks):
                # Header
                
                st.header('Auftragsübersicht Zeitraumanalyse')
                # GesamtDaten über Zeitraum Filtern 

                # ----- Hardfacts Auftragsübersicht -----
                picksGesamt = int(df["Picks Gesamt"].sum())
                picksOUT = int(df["Picks OUT"].sum())
                picksCS = int(df["Picks CS"].sum())
                picksPAL = int(df["Picks PAL"].sum())
                lieferscheine = int(df["Lieferschein"].nunique())
            ## ----- Kennzahlen Liefertag-----##
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"Datum: {day1}")
                    st.write(f"Anzahl Lieferschiene: {lieferscheine}")
                    st.write(f"Gesamt Picks: {picksGesamt}")
                with col2:
                    st.write(f"Anzahl Stangen: {picksOUT}")
                    st.write(f"Anzahl Karton: {picksCS}")
                    st.write(f"Anzahl Paletten: {picksPAL}")
                #figpick = px.bar(dfTag, x="Pick Datum", y="Picks Gesamt",color='' title="Auftragsübersicht")
                #st.plotly_chart(figpick)
                fig = px.bar(dfakunden, x="Pick Datum", y="Picks Gesamt", title="Zeitraum Picks Kunde",hover_data=['Lieferschein', 'Picks Gesamt'], color='Kunde',)
                
                fig.update_layout(showlegend=False,
                )
                

                st.plotly_chart(fig)
            

            
            df = FilterNachDatum(day1, day1,df)
            dfaPicks = DatenPickTagaufbereiten(df)
            dfakunden = DatenKundeaufbereiten(df)
            Tagesanalyse(dfaPicks,dfakunden)




            

            



            

                




            

            
           

 


