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
from streamlit_option_menu import option_menu

#' Murmade'


class Seite1:
        
        def Ladeseite(self, dfDaten):
            
            dfDaten['Pick Datum']= pd.to_datetime(dfDaten['Pick Datum']).dt.date
            userauswahl = pd.Series(dfDaten['Name'].unique())
            def MenueLaden(self):
                selected2 = option_menu(None, ["Tag Auswerten", "Zeitraum Auswerten"], 
                icons=['house', 'cloud-upload', "list-task"], 
                menu_icon="cast", default_index=0, orientation="horizontal")
                return selected2
            
            def Tagauswahl():
                col1 ,col2, col3 = st.columns(3)
                with col1:
                    userselection = st.selectbox("Mitarbeiter:", list(userauswahl))
                with col2:
                    start_date = st.date_input('Datum :',dfDaten['Pick Datum'].max(),min_value=dfDaten['Pick Datum'].min(),max_value=dfDaten['Pick Datum'].max())
                with col3:
                    timefeq = st.selectbox("Zeitfrequenzen anpassen:",["5min","15min","30min","60min"],index=3)
                    
                
                # ----- Datenfiltern -----
                dfAll = dfDaten
                mask = (dfDaten['Pick Datum'] == start_date)
                mask2 = (dfAll['Pick Datum'] == start_date)
                dfAll['Pick Zeit'] = dfAll['Pick Zeit'].dt.round(timefeq)
                df = dfDaten.loc[mask]
                dfAll = dfAll.loc[mask2]
                df = df[df['Name'] == userselection]
                #----- Daten Tag Gesatm--------#
                pickscsGes= int(dfAll["Picks CS"].sum())
                picksoutGes= int(dfAll["Picks OUT"].sum())
                pickspalGes= int(dfAll["PICKS PAL"].sum())
                #----- Daten Mitarbeiter--------#
                pickscs= int(df["Picks CS"].sum())
                picksout= int(df["Picks OUT"].sum())
                pickspal= int(df["PICKS PAL"].sum())
                #labelerstellt= int(df["Label"].sum())
                lieferscheine = df['V'].nunique()
                ## ----- Kennzahlen Mitarbeiter-----##
                
                left_column, middle_column, right_column = st.columns(3)
                with left_column:
                    st.write(f"Stangen: {picksoutGes:,}")
                    st.write(f"Kartons Gesamt: {pickscsGes:,}")
                    st.write(f"Paletten Gesamt: {pickspalGes:,}")
                    st.write(f"GesamtPicks: {pickscsGes + picksoutGes + pickspalGes:,}")
                with middle_column:
                    st.write(f"Stangen: {picksout:,}")
                    st.write(f"Kartons Gesamt: {pickscs:,}")
                    st.write(f"Paletten Gesamt: {pickspal:,}")
                    st.write(f"GesamtPicks: {pickscs + picksout + pickspal:,}")
                with right_column:
                    st.write(f"Bearbeitete Lieferscheine: {lieferscheine:,}")
                    #st.write(f"Label erstellt: {labelerstellt:,}")
                    st.write(f"Erstellte Label: {pickscs + picksout + pickspal:,}")
                    st.write(f"Erstellte Paletten Label: {pickscs + picksout + pickspal:,}")
                    st.write(f"Picks/h: {(pickscs + picksout + pickspal) / 7.5:,}")
                
                # ------ DIAGRAMM ------ #
                def FigMitarbeiter():
                    fig = px.bar(df, x="Pick Zeit", y=['Picks CS','Picks OUT','PICKS PAL'], color='V')
                    fig.update_layout(barmode='stack' ,showlegend=False)
                    st.plotly_chart(fig,use_container_width=True)
                FigMitarbeiter()

                #st.bar_chart(data=df,x='Pick Zeit',y=['Picks CS','Picks OUT','PICKS PAL'])
                def FigPicksMitarbeiter():
                    fig = px.bar(dfAll, x="Pick Zeit", y=['PICKS'], color='Name')
                    st.plotly_chart(fig,use_container_width=True)
                FigPicksMitarbeiter()
            def Zeitauswahl(dfDaten):
                col1 ,col2, col22, col3 = st.columns(4)
                with col1:
                    userselection = st.selectbox("Mitarbeiter:", list(userauswahl))
                with col2:
                    start_date = st.date_input('Datum von :',dfDaten['Pick Datum'].max(),min_value=dfDaten['Pick Datum'].min(),max_value=dfDaten['Pick Datum'].max())
                with col22:
                    end_date = st.date_input('Datum bis :',dfDaten['Pick Datum'].max(),min_value=dfDaten['Pick Datum'].min(),max_value=dfDaten['Pick Datum'].max())
                with col3:
                    timefeq = st.selectbox("Zeitfrequenzen anpassen:",["5min","15min","30min","60min"],index=3)           
                # ----- Datenfiltern -----

                dfAll = dfDaten
                mask = (dfDaten['Pick Datum'] >= start_date) & (dfDaten['Pick Datum'] <= end_date)
                mask2 = (dfAll['Pick Datum'] >= start_date) & (dfAll['Pick Datum'] <= end_date)
                dfAll['Pick Zeit'] = dfAll['Pick Zeit'].dt.round(timefeq)
                df = dfDaten.loc[mask]
                dfAll = dfAll.loc[mask2]
                df = df[df['Name'] == userselection]

                #----- Daten Tag Gesatm--------#
                pickscsGes= int(dfAll["Picks CS"].sum())
                picksoutGes= int(dfAll["Picks OUT"].sum())
                pickspalGes= int(dfAll["PICKS PAL"].sum())
                #----- Daten Mitarbeiter--------#
                pickscs= int(df["Picks CS"].sum())
                picksout= int(df["Picks OUT"].sum())
                pickspal= int(df["PICKS PAL"].sum())
                #labelerstellt= int(df["Label"].sum())
                lieferscheine = df['V'].nunique()
                l = 10
                l = 29
                ## ----- Kennzahlen Mitarbeiter-----##
                
                left_column, middle_column, right_column = st.columns(3)
                with left_column:
                    st.write(f"Stangen: {picksoutGes:,}")
                    st.write(f"Kartons Gesamt: {pickscsGes:,}")
                    st.write(f"Paletten Gesamt: {pickspalGes:,}")
                    st.write(f"GesamtPicks: {pickscsGes + picksoutGes + pickspalGes:,}")
                with middle_column:
                    st.write(f"Stangen: {picksout:,}")
                    st.write(f"Kartons Gesamt: {pickscs:,}")
                    st.write(f"Paletten Gesamt: {pickspal:,}")
                    st.write(f"GesamtPicks: {pickscs + picksout + pickspal:,}")
                with right_column:
                    st.write(f"Bearbeitete Lieferscheine: {lieferscheine:,}")
                    st.write(f"Erstellte Label: {l:,}")
                    st.write(f"Erstellte Paletten Label: {l:,}")
                    st.write(f"Picks/h: {(pickscs + picksout + pickspal) / 7.5:,}")
                
                def FigMitarbeiter():
                    

                    dfapicks = df.groupby(['Name','Pick Datum'],dropna =False)['PICKS'].sum().reset_index()
                    a = df['PICKS'].sum()
                    fig = px.bar(df, x="Pick Datum", y=['Picks CS','Picks OUT','PICKS PAL'], color='Pick Art',hover_data=['V','Pick Zeit'])
                    fig.update_layout(barmode='stack' ,showlegend=False)
                    st.plotly_chart(fig,use_container_width=True)
                FigMitarbeiter()
                def FigPicksMitarbeiter():
                    fig2 = px.bar(dfAll, x="Pick Datum", y=['PICKS'], color='Name',hover_data=['V','Picks OUT','Picks CS','PICKS PAL'],color_continuous_scale=px.colors.sequential.RdBu)
                    fig2.update_layout(barmode='stack' ,showlegend=False)
                    st.plotly_chart(fig2,use_container_width=True)
                FigPicksMitarbeiter()
                def FigPicksMitarbeiterLine():
                    dfapicks = dfAll.groupby(['Name','Pick Datum'],dropna =False)['PICKS'].sum().reset_index()

                    c =np.array(dfapicks['Name'].unique())        
                    mitarbeiter = st.multiselect('Mitarbeiter auswählen', c)
                    dfapicks = dfapicks[dfapicks['Name'].isin(mitarbeiter)]
                    fig2 = px.line(dfapicks, x="Pick Datum", y=['PICKS'],color='Name') #color='Name',hover_data=['V','Picks OUT','Picks CS','PICKS PAL'],color_continuous_scale=px.colors.sequential.RdBu)
                    fig2.update_layout(barmode='stack')
                    st.plotly_chart(fig2,use_container_width=True)
                FigPicksMitarbeiterLine()
                
            selected2 = MenueLaden(self)
            if selected2 == "Tag Auswerten":
                Tagauswahl()
            if selected2 == "Zeitraum Auswerten":
                Zeitauswahl(dfDaten)
                
            
            