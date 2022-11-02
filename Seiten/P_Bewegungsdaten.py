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

class Page_Bewegungsdaten:
        
        def LadeBewegungsdatenTag(self, dflt):
            # ------ Änderungen am Dataframe
            # Rundung auf 5 min takt
            dflt['Pick Zeit'] = pd.to_datetime(dflt['Pick Zeit'])            
            dflt['Pick Datum']= pd.to_datetime(dflt['Pick Datum']).dt.date
            # -------- Sidebar Config
            
            startdatum = st.sidebar.date_input("Datum",value=dflt['Pick Datum'].max() ,max_value=dflt['Pick Datum'].max(), min_value=dflt['Pick Datum'].min())
            mask = (dflt['Pick Datum'] == startdatum)
            dflt = dflt.loc[mask]

            # Columns Kennzahlen
            #--1--#
            aktivenutzer = dflt['Name'].nunique()
            anzahllieferscheine = dflt['V'].nunique()
            #--2---#
            pickscs= int(dflt["Picks CS"].sum())
            picksout= int(dflt["Picks OUT"].sum())
            pickspal= int(dflt["PICKS PAL"].sum())
            # Columns Darstellung
            left_column, middle_column, right_column = st.columns(3)
            with left_column:
                st.write(f"Aktive Kommissionier: {aktivenutzer}")
                st.write("Stundeneinsatz")
                st.write("Durchschnittliche Picks/h")
                timefeq = st.selectbox("Zeitfrequenzen anpassen",["5min","15min","30min","60min"],index=3)
            with middle_column:
                st.write(f"Stangen: {picksout:,}")
                st.write(f"Kartons Gesamt: {pickscs:,}")
                st.write(f"Paletten Gesamt: {pickspal:,}")
            with right_column:
                st.write(f"GesamtPicks: {pickscs + picksout + pickspal:,}")
                st.write(f"Picks/h: {((pickscs + picksout + pickspal) * aktivenutzer)/ 7.5:,}")
                #st.select_slider('Datum wählen',options=dflt['Pick Datum'].unique())
                
            # -------- Charts------------------------#
            def FigTimeLine():
                # ------ Timeline
                #dfTime = dflt['Pick Zeit']
                #dfTime['Zeit'] = dfTime['Pick Zeit'].dt.strftime('%H:%M:%S')
                #dflt['Pick Zeit'] = dflt['Pick Zeit'].dt.round(timefeq)
                dfTime = dflt.groupby(['Pick Zeit'])['PICKS'].sum().reset_index()
                time = dfTime['Pick Zeit']
                picks = dfTime['PICKS']
                st.dataframe(dflt)
                #fig = px.histogram(dfTime, x=time y=picks, title='Picks Timeline')#,animation_frame="Zeit", animation_group="PICKS", range_x=[0, 24], range_y=[0, 200])
                #st.plotly_chart(fig,use_container_width=True)
            FigTimeLine()
            # ------ Picks in Mitarbeiter          
            def FigPicksMitarbeiter():
                fig = px.bar(dflt, x="Pick Zeit", y=['PICKS'], color='Name', title="Wide-Form Input",)#hover_data=['V', 'PICKS'])
                st.plotly_chart(fig,use_container_width=True)
            FigPicksMitarbeiter()
            # ------ Heatmap SKU's
            def FigHeatmapSKU():
                dflt['B'] = dflt['B'].astype(str)
                anzZugrSKU15min = dflt.groupby(['Pick Zeit','B']).size().reset_index(name='Anzahl Zugriffe SKU')
                # delete all rows with Anzahl Zugriffe =>1
                anzZugrSKU15min = anzZugrSKU15min[anzZugrSKU15min['Anzahl Zugriffe SKU'] > 1]
                np.random.seed(1)
                bins = anzZugrSKU15min['B']
                dates = anzZugrSKU15min['Pick Zeit']
                z = np.random.poisson(size=(len(bins), len(dates)))
                fig3 = go.Figure(data=go.Heatmap(
                        z=z,
                        x=dates,
                        y=bins,
                        colorscale='Viridis'))
                fig3.update_layout(
                    title='SKU Heatmap',
                    xaxis_nticks=48)            
                st.plotly_chart(fig3)               
            def FigHeatmapBINS():
                anzZugrBIN15min = dflt.groupby(['Pick Zeit','F']).size().reset_index(name='Anzahl Zugriffe Bins')
                # delete all rows with Anzahl Zugriffe =>1
                anzZugrBIN15min = anzZugrBIN15min[anzZugrBIN15min['Anzahl Zugriffe Bins'] > 1]
                np.random.seed(1)
                bins = anzZugrBIN15min['F']
                dates = anzZugrBIN15min['Pick Zeit']
                z = np.random.poisson(size=(len(bins), len(dates)))
                fig3 = go.Figure(data=go.Heatmap(
                        z=z,
                        x=dates,
                        y=bins,
                        colorscale='Viridis'))
                fig3.update_layout(
                    title='BIN Heatmap',
                    xaxis_nticks=48)            
                st.plotly_chart(fig3)           
            left_heat,right_heat = st.columns(2)
            with left_heat:
                FigHeatmapSKU()
            with right_heat:
                FigHeatmapBINS()
        def LadeBewegungsdatenZeitraum(self,dflt):
            st.header("Bewegungsdaten")
       

