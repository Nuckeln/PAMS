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
        
        def LadeBewegungsdaten(self, dflt):
            # ------ Änderungen am Dataframe
            # Rundung auf 5 min takt
            dflt['Pick Zeit'] = pd.to_datetime(dflt['Pick Zeit'])            
            dflt['Pick Datum']= pd.to_datetime(dflt['Pick Datum']).dt.date
            # -------- Sidebar Config
            
            startdatum = st.sidebar.date_input("Datum")
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
            with middle_column:
                st.write(f"Stangen: {picksout:,}")
                st.write(f"Kartons Gesamt: {pickscs:,}")
                st.write(f"Paletten Gesamt: {pickspal:,}")
            with right_column:
                st.write(f"GesamtPicks: {pickscs + picksout + pickspal:,}")
                st.write(f"Picks/h: {((pickscs + picksout + pickspal) * aktivenutzer)/ 7.5:,}")
            # -------- Charts------------------------#
            # ------ Picks zu Zeit            
            def FigPicksZeit():
                dflt['Pick Zeit'] = dflt['Pick Zeit'].dt.round('15min')
                plotdf = dflt.groupby(['Pick Zeit'])['PICKS'].sum().reset_index()
                st.bar_chart(data=plotdf, y='PICKS', x='Pick Zeit') 
            FigPicksZeit()
            def FigPicksZeit2():
                unique_items = dflt['Pick Zeit'].unique()
                anzZu = dflt.groupby('Pick Zeit').size().reset_index(name='Anzahl Zugriffe')
                # delete all rows with Anzahl Zugriffe =>1
                anzZu = anzZu[anzZu['Anzahl Zugriffe'] > 1]
                st.line_chart(data=anzZu,x='Pick Zeit',y='Anzahl Zugriffe')
            FigPicksZeit2()
            # ------ Picks in Mitarbeiter
            def FigPicksMitarbeiter():
                fig = px.bar(dflt, x="Pick Zeit", y=['PICKS'], color='Name', title="Wide-Form Input")
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
            def FigTimeLine():
                df = dflt.groupby(['Pick Zeit'])['PICKS'].sum().reset_index()
                df['Zeit'] = df['Pick Zeit'].dt.strftime('%H:%M:%S')
                df.drop(['Pick Zeit'], axis=1, inplace=True)
                time = df['Zeit']
                picks = df['PICKS']
                #fig = px.histogram(df, x="total_bill")
                fig = px.histogram(df, x=time, y=picks, title='Picks Timeline'
                ,animation_frame="Zeit", animation_group="PICKS", range_x=[time.min(), time.max()], range_y=[picks.min(), picks.max()])
                st.plotly_chart(fig)
                st.dataframe(df)
                st.write(picks)
                st.write(time)
            left_heat,right_heat = st.columns(2)
            FigTimeLine()
            with left_heat:
                FigHeatmapSKU()
            with right_heat:
                FigHeatmapBINS()


