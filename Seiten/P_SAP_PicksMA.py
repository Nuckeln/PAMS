

import datetime

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
import streamlit as st
from streamlit_option_menu import option_menu
from Data_Class.DB_Daten_SAP import DatenAgregieren as DA 

#' Murmade'
class HeadMenue:
        def menueLaden():
            selected2 = option_menu(None, ["Tag Auswerten", "Zeitraum Auswerten"], 
            icons=['house', 'cloud-upload', "list-task"], 
            menu_icon="cast", default_index=0, orientation="horizontal")
            return selected2

class PicksMA:
        def menueLaden():
            selected2 = option_menu(None, ["Tag Auswerten", "Zeitraum Auswerten"], 
            icons=['house', 'cloud-upload', "list-task"], 
            menu_icon="cast", default_index=0, orientation="horizontal")
            return selected2
        #@st.cache(allow_output_mutation=True)
        def load_data():
            df = pd.read_parquet('Data/upload/lt22.parquet')
            return df

        def TagAuswerten(df):

            df['Pick Datum']= pd.to_datetime(df['Pick Datum']).dt.date

            def hardfactsGesamt(df):

                aktivenutzer = df['MitarbeiterCreateTO'].nunique()
                #anzahllieferscheine = df['V'].nunique()
                #--2---#
                pickscs= int(df["Picks CS"].sum())
                picksout= int(df["Picks OUT"].sum())
                pickspal= int(df["PICKS PAL"].sum())
                
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

            def mitarbeiterHardfacts(df):
                df = df.groupby(['Name']).agg({'Picks CS': 'sum', 'Picks OUT': 'sum', 'PICKS PAL': 'sum','DestBin': 'nunique'})
                df = df.rename(columns={'DestBin': 'Lieferscheine'})
                df = df.reset_index()
                df['GesamtPicks'] = df['Picks CS'] + df['Picks OUT'] + df['PICKS PAL']
                df = df.sort_values(by='GesamtPicks', ascending=False)

            def figPicksMitarbeiter(df):
                df = df.groupby(['Name']).agg({'Picks CS': 'sum', 'Picks OUT': 'sum', 'PICKS PAL': 'sum','DestBin': 'nunique'})
                df = df.rename(columns={'DestBin': 'Lieferscheine'})
                df = df.reset_index()
                df['GesamtPicks'] = df['Picks CS'] + df['Picks OUT'] + df['PICKS PAL']
                df = df.sort_values(by='GesamtPicks', ascending=False)

                fig = go.Figure()

                # Balken hinzufügen und Labels hinzufügen
                fig.add_trace(go.Bar(x=df['Name'], y=df['Picks CS'], name='Picks CS', text=df['Picks CS'], textposition='inside'))
                fig.add_trace(go.Bar(x=df['Name'], y=df['Picks OUT'], name='Picks OUT', text=df['Picks OUT'], textposition='inside'))
                fig.add_trace(go.Bar(x=df['Name'], y=df['PICKS PAL'], name='PICKS PAL', text=df['PICKS PAL'], textposition='inside'))
                
                # Layout aktualisieren, um die Balken zu stapeln
                fig.update_layout(barmode='stack')
                # Linie hinzufügen
                fig.add_trace(go.Scatter(x=df['Name'], y=df['Lieferscheine'], name='Lieferscheine', mode='lines+markers', line=dict(color='black', width=2)))
                # add a line with value from Lieferscheine
                fig.add_hline(y=df['Lieferscheine'].mean(), line_dash="dash", line_width=2, line_color="gray")
                # add a line with value from Lieferscheine
                st.plotly_chart(fig, use_container_width=True)

            def figPicksMitarbeiterLine(dfAll):
                dfapicks = dfAll.groupby(['Name','Pick Datum'],dropna =False)['PICKS'].sum().reset_index()

                c =np.array(dfapicks['Name'].unique())        
                fig2 = px.line(dfapicks, x="Pick Datum", y=['PICKS'],color='Name') #color='Name',hover_data=['V','Picks OUT','Picks CS','PICKS PAL'],color_continuous_scale=px.colors.sequential.RdBu)
                fig2.update_layout(barmode='stack')
                st.plotly_chart(fig2,use_container_width=True)
                
            def figVerfügbareTo(dfNurDate):
                dfNurDate = dfNurDate.groupby(['PickDatum']).agg({'Picks CS': 'sum', 'Picks OUT': 'sum', 'PICKS PAL': 'sum','DestBin': 'nunique'})

            def page(df):
                col1, col2, col3 = st.columns(3)
                with col1:
                    #letzer Tag im Datenframe
                    first_date = df['Pick Datum'].min()
                    last_date = df['Pick Datum'].max()
                    sel_date = st.date_input("Datum auswählen", last_date)
                    df = df[df['Pick Datum'] == sel_date]     
                with col2:
                #first and last date from df 
                    st.write(f"Vorhandender Datenzeitraum vom:")
                    st.write(f' {first_date} bis: {last_date}')
                with col3:
                    sel_fachbereich = st.radio("Fachbereich",["Superdepot","CW","C&F"],index=0)
                    if sel_fachbereich == "Superdepot":
                        df = df[df['SuperDepot'] == 1]
                    # elif sel_fachbereich == "CW":
                    #     df = df[df['Fachbereich'] == "CW"]
                    # elif sel_fachbereich == "C&F":
                    #     df = df[df['Fachbereich'] == "C&F"]
                st.write(" ")
                dfNurDate = df          
                hardfactsGesamt(df)
                sel_mitarbeiter = st.multiselect("Mitarbeiter auswählen",df['Name'].unique(),default=df['Name'].unique())
                df = df[df['Name'].isin(sel_mitarbeiter)]

                sel_timefeq = st.selectbox("Zeitfrequenzen anpassen",["5min","15min","30min","60min"],index=3)
                df['Pick Zeit'] = df['Pick Zeit'].dt.round(sel_timefeq)
                mitarbeiterHardfacts(df)
                figPicksMitarbeiter(df)
                #figPicksMitarbeiterLine(df)
                st.dataframe(df)

               
            page(df)

class PicksMaZeitraum:
    
    def datefFilter():
        #create a date slider from to
        st.slider("Zeitraum auswählen", value=(datetime.date(2021, 1, 1), datetime.date(2021, 1, 31)), min_value=datetime.date(2021, 1, 1), max_value=datetime.date(2021, 1, 31), format="DD.MM.YYYY")


    def page():
        st.write(" ")
        pass
        


class LoadPageSapPicksMA:    

    def mitarbeiterPage():
        selected2 = HeadMenue.menueLaden()
        if selected2 == "Tag Auswerten":
            df = PicksMA.load_data()    
            PicksMA.TagAuswerten(df)
        elif selected2 == "Zeitraum Auswerten":
            PicksMaZeitraum.page()

                
            
            