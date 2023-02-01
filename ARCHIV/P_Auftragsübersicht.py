
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
    def Auftragsübersicht_Page(self,dfLS):

        # Datenfilter Funktionen
        def FilterNachDatum(day1, day2,df):
            mask = (df['Pick Datum'] >= day1) & (df['Pick Datum'] <= day2)         
            df = df.loc[mask]
            return df
        def FilterNachWochen(wochen):
            mask = (df['Kalender Woche'] == wochen)
            df = df.loc[mask]
            return df
        def FilterNachMonate(monate):
            mask = (df['Monat'] == monate)
            df = df.loc[mask]
        def DatenKundeaufbereiten(dfa):
            dfa['Pick Datum'] = pd.to_datetime(dfa['B']).dt.date
            dfa.rename(columns={'L': 'Kunde'}, inplace=True)
            dfa.rename(columns={'A': 'Lieferschein'}, inplace=True)
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
            dfT['Pick Datum'] = pd.to_datetime(dfT['B']).dt.date
            dfT.rename(columns={'L': 'Kunde'}, inplace=True)
            dfT.rename(columns={'A': 'Lieferschein'}, inplace=True)
            dfaPicksTag = dfT.groupby(['Pick Datum'])['Picks Gesamt'].sum().reset_index()
            dfaCStag = dfT.groupby(['Pick Datum'])['Picks CS'].sum().reset_index()   
            dfaPALtag = dfT.groupby(['Pick Datum'])['Picks PAL'].sum().reset_index()      
            dfaOUTtag = dfT.groupby(['Pick Datum'])['Picks OUT'].sum().reset_index()
            dfaZugriffe = pd.merge(dfaPicksTag, dfaCStag[['Pick Datum','Picks CS']],left_on='Pick Datum', right_on='Pick Datum',how='left')         
            dfaZugriffe = pd.merge(dfaZugriffe, dfaOUTtag[['Pick Datum','Picks OUT']],left_on='Pick Datum', right_on='Pick Datum',how='left')
            dfaZugriffe = pd.merge(dfaZugriffe, dfaPALtag[['Pick Datum','Picks PAL']],left_on='Pick Datum', right_on='Pick Datum',how='left')
            
            return dfaZugriffe
        # Daten Bearbeiten
            #----- Datenfiltern -----
        dfKunden = DatenKundeaufbereiten(dfLS)
        dfPicks = DatenPickTagaufbereiten(dfLS)         
        start_date = dfLS['B'].min()
        # größtes Pick Datum
        end_date = dfLS['B'].max()# + relativedelta(days=1)    
        btnTages = st.sidebar.button('Tagesanalyse')      
        day1 = st.sidebar.date_input('Startdatum', end_date, min_value=start_date, max_value=end_date)
        day2 = st.sidebar.date_input('Enddatum', end_date, max_value=end_date, min_value=start_date)
        wochen = st.sidebar.selectbox('Wochen', dfLS['Kalender Woche'].unique())      
        dfKunden = FilterNachDatum(day1,day2,dfKunden)
        dfPicks = FilterNachDatum(day1,day2,dfPicks)

## ABFRAGE DATUM
        def Tagesanalyse(dfKunden,dfPicks):
            st.header('Auftragsübersicht Tagesanalyse')
            dfKunden = FilterNachDatum(day1,day2,dfKunden)
            dfPicks = FilterNachDatum(day1,day2,dfPicks)
            
            picksGesamt = int(dfKunden["Picks Gesamt"].sum())
            picksOUT = int(dfKunden["Picks OUT"].sum())
            picksCS = int(dfKunden["Picks CS"].sum())
            picksPAL = int(dfKunden["Picks PAL"].sum())
            # count lieferschein in dfKunden
            countLS = dfKunden['Lieferschein'].nunique()
        ## ----- Kennzahlen Liefertag-----##
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"Datum: {day1}")
                st.write(f"Anzahl Lieferschiene: {countLS}")
                st.write(f"Gesamt Picks: {picksGesamt}")
            with col2:
                st.write(f"Anzahl Stangen: {picksOUT}")
                st.write(f"Anzahl Karton: {picksCS}")
                st.write(f"Anzahl Paletten: {picksPAL}")
            #---- Anzeige der Picks pro Kunde ----#
            def figPiePickaufteilung():
                random_x = [picksCS,picksOUT,picksPAL]
                names = ['CS', 'OUT', 'PAL'] 
                figPiePickaufteilung = px.pie(values=random_x, names=names)
                figPiePickaufteilung.update_layout(margin=dict(t=15, b=15, l=15, r=15)) 
                figPiePickaufteilung.update_layout(title_text='Picks aufgeteilt nach Stangen, Karton und Paletten')
                figPiePickaufteilung.update_traces(textposition='inside', textinfo='percent+label')
                #center = {'x': 0.5, 'y': 0.5}
                figPiePickaufteilung.update_layout(legend=dict(orientation="h",yanchor="bottom",y=1.02,xanchor="right",x=1))
                st.plotly_chart(figPiePickaufteilung, use_container_width=True)
            st.write('  ')
            figPiePickaufteilung()
            def figPicksKunde():
                figTagKunden = px.bar(dfKunden, x="Kunde", y="Picks Gesamt",  title="Kundenverteilung",hover_data=['Picks Gesamt','Lieferschein','Picks OUT','Picks CS','Picks PAL'],color='Picks Gesamt',color_continuous_scale=px.colors.sequential.Jet)
                st.plotly_chart(figTagKunden,use_container_width=True)         
            figPicksKunde()

            st.dataframe(dfKunden)


        def Zeitraumanalyse(dfKunden,dfPicks):
            st.header('Auftragsübersicht Zeitraumanalyse')
            dfKunden = FilterNachDatum(day1,day2,dfKunden)
            dfPicks = FilterNachDatum(day1,day2,dfPicks)
            # add Weekday to dfKunden
            dfKunden['Wochentag'] = pd.to_datetime(dfKunden['Pick Datum']).dt.day_name()
            # Average of 'Gesamt Picks' by 'Pick Datum'
            a = dfKunden[["Picks Gesamt"]].mean()
            picksGesSchnitt = a
            #
            picksOUT = int(dfKunden["Picks OUT"].sum())
            picksCS = int(dfKunden["Picks CS"].sum())
            picksPAL = int(dfKunden["Picks PAL"].sum())
            # count lieferschein in dfKunden
            countLS = dfKunden['Lieferschein'].nunique()
        ## ----- Kennzahlen Liefertag-----##
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"Datum: {day1}")
                st.write(f"Anzahl Lieferschiene: {countLS}")
                st.write(f"Gesamt Picks: {picksGesSchnitt}")
            with col2:
                st.write(f"Anzahl Stangen: {picksOUT}")
                st.write(f"Anzahl Karton: {picksCS}")
                st.write(f"Anzahl Paletten: {picksPAL}")
            #---- Anzeige der Picks pro Kunde ----#
            def figPicksGesamt():
                figTagKunden = px.bar(dfPicks, x="Pick Datum", y="Picks Gesamt",  title="Picks",hover_data=['Pick Datum','Picks OUT','Picks CS','Picks PAL'],color='Picks Gesamt',color_continuous_scale=px.colors.sequential.RdBu)
                st.plotly_chart(figTagKunden,use_container_width=True)      
            figPicksGesamt()
            def figPicksKunde():
                figTagKunden = px.bar(dfKunden, x="Kunde", y="Picks Gesamt",  title="Kundenverteilung",hover_data=['Picks Gesamt','Lieferschein','Picks OUT','Picks CS','Picks PAL'],color='Picks Gesamt',color_continuous_scale=px.colors.sequential.RdBu)
                st.plotly_chart(figTagKunden,use_container_width=True)         
            figPicksKunde()
            st.markdown('###Was noch folgt:  '
                        '1. Anzeige der Picks pro Kunde pro Tag  '
                        '2. Anzeige der Picks pro Kunde pro Woche  ')
            st.dataframe(dfKunden)
            st.dataframe(dfPicks)
            



        # Seiteninhalt anhand von Date! 
        if day1 == day2 or btnTages:
            day1 = day2
            Tagesanalyse(dfKunden,dfPicks)
        else:
            Zeitraumanalyse(dfKunden,dfPicks)
        
    
# def Tag(dfT):
        # Config Sidebar
    # day1 = st.sidebar.date_input('Startdatum', end_date, min_value=start_date, max_value=end_date)
    # btnTages = st.sidebar.button('Tagesanalyse')
    # day2 = st.sidebar.date_input('Enddatum', end_date, max_value=end_date, min_value=start_date)
    # wochen = st.sidebar.selectbox('Wochen', dfT['Kalender Woche'].unique())
    # start_date = dfT['B'].min()
    # # größtes Pick Datum
    # end_date = dfT['B'].max()# + relativedelta(days=1)          
    # day1 = st.sidebar.date_input('Startdatum', end_date, min_value=start_date, max_value=end_date)
    # btnTages = st.sidebar.button('Tagesanalyse')
    # day2 = st.sidebar.date_input('Enddatum', end_date, max_value=end_date, min_value=start_date)
        
        
        #wochen = st.sidebar.selectbox('Wochen', dfT['Kalender Woche'].unique())















        







        #monate = st.sidebar.selectbox('Monate', ['Tag', 'Woche', 'Monat', 'Jahr'])

         #def FilterNachMonate(monate):

            # ----- Hardfacts Auftragsübersicht -----
        # def Tagesanalyse(df, dfakunden):
        #     st.header('Auftragsübersicht Tagesanalyse')
        #     # ----- Datenfiltern -----            
        #     ## ----- Hardfacts Auftragsübersicht -----
        #     picksGesamt = int(df["Picks Gesamt"].sum())
        #     picksOUT = int(df["Picks OUT"].sum())
        #     picksCS = int(df["Picks CS"].sum())
        #     picksPAL = int(df["Picks PAL"].sum())
        # ## ----- Kennzahlen Liefertag-----##
        #     col1, col2 = st.columns(2)
        #     with col1:
        #         st.write(f"Datum: {day1}")
        #         st.write(f"Anzahl Lieferschiene: {picksGesamt}")
        #         st.write(f"Gesamt Picks: {picksGesamt}")
        #     with col2:
        #         st.write(f"Anzahl Stangen: {picksOUT}")
        #         st.write(f"Anzahl Karton: {picksCS}")
        #         st.write(f"Anzahl Paletten: {picksPAL}")
        # ### ----- Chart  Auftragsübersicht -----
        #     fig = px.bar(dfakunden, x="Kunde", y="Picks Gesamt", barmode="group", title="Auftragsübersicht")
        #     st.plotly_chart(fig)

        # def Zeitraumanalyse(df,dfakunden,dfaPicks):
        #     # Header
            
        #     st.header('Auftragsübersicht Zeitraumanalyse')
        #     # GesamtDaten über Zeitraum Filtern 

        #     # ----- Hardfacts Auftragsübersicht -----
        #     picksGesamt = int(df["Picks Gesamt"].sum())
        #     picksOUT = int(df["Picks OUT"].sum())
        #     picksCS = int(df["Picks CS"].sum())
        #     picksPAL = int(df["Picks PAL"].sum())
        #     lieferscheine = int(df["Lieferschein"].nunique())
        # ## ----- Kennzahlen Liefertag-----##
        #     col1, col2 = st.columns(2)
        #     with col1:
        #         st.write(f"Datum: {day1}")
        #         st.write(f"Anzahl Lieferschiene: {lieferscheine}")
        #         st.write(f"Gesamt Picks: {picksGesamt}")
        #     with col2:
        #         st.write(f"Anzahl Stangen: {picksOUT}")
        #         st.write(f"Anzahl Karton: {picksCS}")
        #         st.write(f"Anzahl Paletten: {picksPAL}")
        #     #figpick = px.bar(dfTag, x="Pick Datum", y="Picks Gesamt",color='' title="Auftragsübersicht")
        #     #st.plotly_chart(figpick)
        #     fig = px.bar(dfakunden, x="Pick Datum", y="Picks Gesamt", title="Zeitraum Picks Kunde",hover_data=['Lieferschein', 'Picks Gesamt'], color='Kunde',)
            
        #     fig.update_layout(showlegend=False,
        #     )
            

        #     st.plotly_chart(fig)