
import pytz
import streamlit as st
import pandas as pd
import numpy as np
from streamlit_option_menu import option_menu
import datetime
import plotly.express as px
import pyarrow.parquet as pq
from Data_Class.SQL import SQL_TabellenLadenBearbeiten as sql
from Data_Class.DB_Daten_SAP import DatenAgregieren as da

#Berichtsdaten laden und berechnen und Filtern ##############
def dateFilter(df):
    df['PlannedDate'] = df['PlannedDate'].astype(str)
    df['PlannedDate'] = pd.to_datetime(df['PlannedDate'].str[:10])
    df['Tag'] = df['PlannedDate'].dt.strftime('%d.%m.%Y')
   # df tag to datetime.date
    df['Tag'] = pd.to_datetime(df['Tag'])
    df['Wochentag'] = df['PlannedDate'].dt.strftime('%A')

    # df['Woche'] = Wochennummer und Jahr
    df['Woche'] = df['PlannedDate'].dt.strftime('%V.%Y')
    
    df['Monat'] = df['PlannedDate'].dt.strftime('%m.%Y')

    col1, col2, col3 = st.columns(3)
    # Nach Zeitraum Devinieren
    with col1:
        sel_datePicker = st.selectbox('Zeitraum:', ['Woche','Tag','Tage letzte 30', 'Tage letzte 90'])
    # Nach Tage filtern
    with col2:
        if sel_datePicker == 'Tag':
            sel_date = st.date_input('Wähle Tag', datetime.date.today())
            df = df[(df['Tag'] == np.datetime64(sel_date))]
        if sel_datePicker == 'Tage letzte 30':
            end_date = datetime.date.today()
            start_date = end_date - datetime.timedelta(days=30)
            format = "DD.MM.YYYY"
            sel_dateRange = st.slider('Selektiere Zeitraum', min_value=start_date, value=(start_date, end_date), max_value=end_date, format=format)
            df = df[(df['Tag'] >= np.datetime64(sel_dateRange[0])) & (df['Tag'] <= np.datetime64(sel_dateRange[1]))]
        if sel_datePicker == 'Tage letzte 90':
            end_date = datetime.date.today()
            start_date = end_date - datetime.timedelta(days=90)
            format = "DD.MM.YYYY"
            sel_dateRange = st.slider('Selektiere Zeitraum', min_value=start_date, value=(start_date, end_date), max_value=end_date, format=format)
            df = df[(df['Tag'] >= np.datetime64(sel_dateRange[0])) & (df['Tag'] <= np.datetime64(sel_dateRange[1]))]
        if sel_datePicker == 'Woche':
            # sort by week by greater to lower 
            df = df.sort_values(by=['Woche'], ascending=False)
            
            sel_weekRange = st.selectbox('Woche:', df['Woche'].unique(),)
            df = df[df['Woche'] == sel_weekRange]
    # Nach Wochentag filtern
    with col3:
        sel_Wochentag = st.selectbox('Wochentag Filtern:', ['Alle', 'Montag', 'Dienstag', 'Mittwoch', 'Donnerstag', 'Freitag', 'Samstag', 'Sonntag'])
        if sel_Wochentag != 'Alle':
            if sel_Wochentag == 'Montag':
                df = df[df['Wochentag'] == 'Monday']
            elif sel_Wochentag == 'Dienstag':
                df = df[df['Wochentag'] == 'Tuesday']
            elif sel_Wochentag == 'Mittwoch':
                df = df[df['Wochentag'] == 'Wednesday']
            elif sel_Wochentag == 'Donnerstag':
                df = df[df['Wochentag'] == 'Thursday']
            elif sel_Wochentag == 'Freitag':
                df = df[df['Wochentag'] == 'Friday']
            elif sel_Wochentag == 'Samstag':
                df = df[df['Wochentag'] == 'Saturday']
            elif sel_Wochentag == 'Sonntag':
                df = df[df['Wochentag'] == 'Sunday']

    return df

def berechneAlleDepots(dfOr, dfHannover):
    #to string dfHannover = dfHannover['Delivery'] 
    dfHannover['Delivery'] = dfHannover['Delivery'].astype(str)
    #dfHannover group by Delivery and Date
    dfHannover = dfHannover.groupby(['Picking Date','Delivery','Name of the ship-to party','TSP',]).agg({'Picks Gesamt':'sum','Picks CS':'sum','Picks PAL':'sum','Picks OUT':'sum'}).reset_index()
    #rename dfHannover Delivery to SapOrderNumber, Picking Date to PlannedDate, Name of the ship-to party to PartnerName, TSP to DeliveryDepot, Picks CS to Picks Karton, Picks OUT to Picks Stangen, Picks PAL to Picks Paletten
    dfHannover = dfHannover.rename(columns={'Delivery':'SapOrderNumber','Picking Date':'PlannedDate', 'Name of the ship-to party':'PartnerName', 'TSP':'DeliveryDepot', 'Picks CS':'Picks Karton', 'Picks OUT':'Picks Stangen', 'Picks PAL':'Picks Paletten'})
    #concat rows with same column names to df
    df = pd.concat([dfOr, dfHannover], ignore_index=True)
    #if in Delivery Depot  'Bielefeld': 'Bielefeld',   'DE54 - KN Hamburg': 'Hamburg','DE59 - KN Stuttgart': 'Stuttgart', 'HAJ - KN Hannover': 'Hannover','KNBFE': 'Bielefeld', 'KNLEJ': 'Leipzig','KNSTR': 'Stuttgart','Unbekannt': 'Hannover'
    df['DeliveryDepot'] = df['DeliveryDepot'].replace({'Bielefeld': 'Bielefeld',   'DE54 - KN Hamburg': 'Hamburg','DE59 - KN Stuttgart': 'Stuttgart', 'HAJ - KN Hannover': 'Hannover','KNBFE': 'Bielefeld', 'KNLEJ': 'Leipzig','KNSTR': 'Stuttgart','Unbekannt': 'Hannover'})
    # Filter by Depot
    depot = st.multiselect('Depot', ['Stuttgart','Hannover','Bielefeld','Hamburg','Leipzig'], ['Stuttgart' ,'Leipzig'])
    df = df[df['DeliveryDepot'].isin(depot)]
    return df

# Grafiken ###################################################
def expanderFigGesamtPicks(df):

        def figPicksGesamtKunden(df,unterteilen,tabelle,sel_barmode):
            df['Picks Gesamt'] = df['Picks Gesamt'].round(0).astype(int)
            #df PlannedDate to dd:mm:yyyy
            df['PlannedDate'] = pd.to_datetime(df['PlannedDate'])
            #i as double  = sum of Picks Gesamt by PlannedDate
            i = df.groupby('PlannedDate')['Picks Gesamt'].sum()
            try:
                fig = px.bar(df, x="PlannedDate", y="Picks Gesamt", color="PartnerName", barmode=sel_barmode, facet_col=unterteilen,hover_data=["Picks Gesamt","DeliveryDepot","PlannedDate","Lieferschein erhalten"])
            except:
                st.warning('Der Filter liefert keine Ergebnisse')

            fig.update_xaxes(tickformat='%d.%m.%Y')
            fig.update_xaxes(showticklabels=True)
            if unterteilen != None:
            # Create the faceted plot
                #updatedate each in facet_col
                fig.update_xaxes(showticklabels=True, row=1, col=1)
                fig.update_xaxes(showticklabels=True, row=1, col=2)
                fig.update_xaxes(showticklabels=True, row=1, col=3)
                fig.update_xaxes(showticklabels=True, row=1, col=4)
                ###### umbauen
                fig.update_layout(title_text="Picks Gesamt nach Kunde", title_x=0.5, title_font_size=20, title_font_family="Montserrat", title_font_color="#0F2B63", legend_title_text="Kunde", legend_title_font_color="#0F2B63", legend_title_font_family="Montserrat", legend_title_font_size=14, legend_font_size=12, legend_font_family="Montserrat", legend_font_color="#0F2B63", legend_orientation="h", legend=dict(x=0.5, y=-0.2), margin=dict(l=0, r=0, t=50, b=0), height=800)
                fig.update_layout(font_family="Montserrat",font_color="#0F2B63",title_font_family="Montserrat",title_font_color="#0F2B63")
            fig.update_layout(
                    annotations=[
                        {"x": x, "y": total * 1.05, "text": str(total), "showarrow": False}
                        for x, total in df.groupby("PlannedDate", as_index=False).agg({"Picks Gesamt": "sum"}).values])
            
            #renmove legend
            if unterteilen != None:
                fig.update_layout(showlegend=False)
            else:
            
                
            
                st.plotly_chart(fig, use_container_width=True)

            if tabelle == True:
                st.dataframe(df)

        def figPicksGesamtnachTagUndVerfügbarkeit(df,unterteilen,tabelle,sel_barmode):
            #round df Picks Gesamt to int
            df['Picks Gesamt'] = df['Picks Gesamt'].round(0).astype(int)
            # Convert 'PlannedDate' to datetime format
            df['PlannedDate'] = pd.to_datetime(df['PlannedDate'], format='%Y-%m-%d %H:%M:%S.%f')
            df['Lieferschein erhalten'] = df['Lieferschein erhalten'].fillna(df['PlannedDate'])
            #Convert 'Lieferschein erhalten' to datetime format
            df['Lieferschein erhalten'] = pd.to_datetime(df['Lieferschein erhalten'])   
            df.sort_values("PlannedDate", inplace=True)
            df = df.reset_index()
            df['Lieferschein erhalten'] = df['Lieferschein erhalten'].dt.date
            # PlannedDate to date only
            df['PlannedDate'] = df['PlannedDate'].dt.date
            try:
                df.loc[df['Lieferschein erhalten'] < df['PlannedDate'], 'Verfügbarkeit'] = 'Vortag'
                df.loc[df['Lieferschein erhalten'] >= df['PlannedDate'], 'Verfügbarkeit'] = 'Verladetag'
            except:
                #all values are Vortag
                df['Verfügbarkeit'] = 'Verladetag'
                st.warning('Der Filter liefert keine Ergebnisse')
            df_grouped = df.groupby(["PlannedDate", "Verfügbarkeit","DeliveryDepot"])["Picks Gesamt"].sum().reset_index()     
            df_grouped = df_grouped.sort_values(by=['PlannedDate','Verfügbarkeit','DeliveryDepot'], ascending=[False,False,False])
            # Create a bar chart of 'Picks Gesamt' grouped by delivery Depot and stacked by sum Vortag and Verladetag
            fig = px.bar(df_grouped, x="PlannedDate", y="Picks Gesamt", color="Verfügbarkeit", barmode=sel_barmode, facet_col=unterteilen,hover_data=["Picks Gesamt","DeliveryDepot","PlannedDate"])
            #remove timespamp from xaxis
            fig.update_xaxes(tickformat='%d.%m.%Y')
            #### DAten Update Wenn DEPOT FILTER updatedate each in facet_col
            if unterteilen != None:
            # Create the faceted plot
                #updatedate each in facet_col
                fig.update_xaxes(showticklabels=True, row=1, col=1)
                fig.update_xaxes(showticklabels=True, row=1, col=2)
                fig.update_xaxes(showticklabels=True, row=1, col=3)
                fig.update_xaxes(showticklabels=True, row=1, col=4)
                fig.update_layout(title_text="Picks Gesamt Unterteilt in Zieldepot und Verfügbarkeit", title_x=0.5, title_font_size=20, title_font_family="Montserrat", title_font_color="#0F2B63", legend_title_font_color="#0F2B63", legend_title_font_family="Montserrat", legend_title_font_size=14, legend_font_size=12, legend_font_family="Montserrat", legend_font_color="#0F2B63", height=700)
                df_groupedStr = df_grouped[df_grouped['DeliveryDepot'] == 'Stuttgart']
                df_groupedStrVerl = df_groupedStr[df_groupedStr['Verfügbarkeit'] == 'Verladetag']
                df_groupedStrVerl = df_groupedStrVerl.sort_values(by=['PlannedDate'], ascending=[False])
                fig.update_traces( text= df_groupedStrVerl['Picks Gesamt'].astype(str), textposition='inside',selector=dict(name='Verladetag'), row=1, col=1)
                df_groupedStrVor = df_groupedStr[df_groupedStr['Verfügbarkeit'] == 'Vortag']
                df_groupedStrVor = df_groupedStrVor.sort_values(by=['PlannedDate'], ascending=[False])
                fig.update_traces( text= df_groupedStrVor['Picks Gesamt'].astype(str), textposition='inside',selector=dict(name='Vortag'), row=1, col=1)
                df_groupedLei = df_grouped[df_grouped['DeliveryDepot'] == 'Leipzig']
                df_groupedLeiVerl = df_groupedLei[df_groupedLei['Verfügbarkeit'] == 'Verladetag']
                df_groupedLeiVerl = df_groupedLeiVerl.sort_values(by=['PlannedDate'], ascending=[False])
                fig.update_traces( text= df_groupedLeiVerl['Picks Gesamt'].astype(str), textposition='inside',selector=dict(name='Verladetag'), row=1, col=2)
                df_groupedLeiVor = df_groupedLei[df_groupedLei['Verfügbarkeit'] == 'Vortag']
                df_groupedLeiVor = df_groupedLeiVor.sort_values(by=['PlannedDate'], ascending=[False])
                fig.update_traces( text= df_groupedLeiVor['Picks Gesamt'].astype(str), textposition='inside',selector=dict(name='Vortag'), row=1, col=2)
                df_groupedHan = df_grouped[df_grouped['DeliveryDepot'] == 'Hannover']
                df_groupedHanVerl = df_groupedHan[df_groupedHan['Verfügbarkeit'] == 'Verladetag']
                df_groupedHanVerl = df_groupedHanVerl.sort_values(by=['PlannedDate'], ascending=[False])
                fig.update_traces( text= df_groupedHanVerl['Picks Gesamt'].astype(str), textposition='inside',selector=dict(name='Verladetag'), row=1, col=3)
                df_groupedHanVor = df_groupedHan[df_groupedHan['Verfügbarkeit'] == 'Vortag']
                df_groupedHanVor = df_groupedHanVor.sort_values(by=['PlannedDate'], ascending=[False])
                fig.update_traces( text= df_groupedHanVor['Picks Gesamt'].astype(str), textposition='inside',selector=dict(name='Vortag'), row=1, col=3)
                df_groupedBil = df_grouped[df_grouped['DeliveryDepot'] == 'Bielefeld']
                df_groupedBilVerl = df_groupedBil[df_groupedBil['Verfügbarkeit'] == 'Verladetag']
                df_groupedBilVerl = df_groupedBilVerl.sort_values(by=['PlannedDate'], ascending=[False])
                fig.update_traces( text= df_groupedBilVerl['Picks Gesamt'].astype(str), textposition='inside',selector=dict(name='Verladetag'), row=1, col=4)
                df_groupedBilVor = df_groupedBil[df_groupedBil['Verfügbarkeit'] == 'Vortag']
                df_groupedBilVor = df_groupedBilVor.sort_values(by=['PlannedDate'], ascending=[False])
                fig.update_traces( text= df_groupedBilVor['Picks Gesamt'].astype(str), textposition='inside',selector=dict(name='Vortag'), row=1, col=4)
                fig.update_layout(font_family="Montserrat",font_color="#0F2B63",title_font_family="Montserrat",title_font_color="#0F2B63")


            else:
                    #add text to each bar
                df_groupedVor = df_grouped[df_grouped['Verfügbarkeit'] == 'Vortag']
                fig.update_traces( text= df_groupedVor['Picks Gesamt'].astype(str) + '<br>'+df_groupedVor['DeliveryDepot'], textposition='inside',selector=dict(name='Vortag'))
                df_groupedVer = df_grouped[df_grouped['Verfügbarkeit'] == 'Verladetag']
                fig.update_traces( text=df_groupedVer['Picks Gesamt'].astype(str) + '<br>'+df_groupedVer['DeliveryDepot'], textposition='inside',selector=dict(name='Verladetag'))
            fig.update_layout(title_text="Picks Gesamt DE30 nach Verfügbarkeit", title_x=0.5, title_font_size=20, title_font_family="Montserrat", title_font_color="#0F2B63", legend_title_font_color="#0F2B63", legend_title_font_family="Montserrat", legend_title_font_size=14, legend_font_size=12, legend_font_family="Montserrat", legend_font_color="#0F2B63", legend_orientation="h", height=700)
                 
            fig.update_layout(
                    annotations=[
                        {"x": x, "y": total * 1.05, "text": str(total), "showarrow": False}
                        for x, total in df.groupby("PlannedDate", as_index=False).agg({"Picks Gesamt": "sum"}).values])
                
            fig.update_traces(marker_color='#50af47', selector=dict(name='Vortag'))
            fig.update_traces(marker_color='#e72582', selector=dict(name='Verladetag'))
            fig.update_layout(font_family="Montserrat",font_color="#0F2B63",title_font_family="Montserrat",title_font_color="#0F2B63")

        

            
            #
            st.plotly_chart(fig, use_container_width=True)       
            ## FARBEN
            if tabelle == True:
                st.dataframe(df)
                
    
        with st.expander('Pick Volumen', expanded=True):

            col1, col2, col3 = st.columns(3)
            #form selectbox
            with col1:
                sel_NachDepot = st.selectbox('Gliederung nach:', ['Gesamtvolumen','Depot'])
                sel_tabelle = st.checkbox('Tabelle Anzeigen:', value=False)
            with col2:
                sel_GesamtOderNachDepot = st.selectbox('Unterteilt in:', ['Verfügbarkeit','Kunden'])
                if st.checkbox('Gestapelt', value=True):
                    sel_barmode = 'stack'
                else:
                    sel_barmode = 'group'
            with col3:
                 sel_Mengeneinheit = st.selectbox('Mengeneinheit:', ['Picks','KG/TH'])
            # unterteilen ja nein       
            if sel_NachDepot == 'Depot':
                    unterteilen = 'DeliveryDepot'
            if sel_NachDepot == 'Gesamtvolumen':
                    unterteilen = None
            #wich SumOf
            if sel_GesamtOderNachDepot == 'Kunden':
                figPicksGesamtKunden(df,unterteilen,sel_tabelle,sel_barmode=sel_barmode)
            if sel_GesamtOderNachDepot == 'Verfügbarkeit':
                figPicksGesamtnachTagUndVerfügbarkeit(df,unterteilen,sel_tabelle,sel_barmode=sel_barmode)

def expanderPicksLager(df,dflt22):

        def figLieferscheinFertigTag(df,unterteilen,tabelle,sel_barmode):
            #round df Picks Gesamt to int
            df['Picks Gesamt'] = df['Picks Gesamt'].round(0).astype(int)
            # Convert 'PlannedDate' to datetime format
            df['PlannedDate'] = pd.to_datetime(df['PlannedDate'], format='%Y-%m-%d %H:%M:%S.%f')
            df['PlannedDate'] = df['PlannedDate'].fillna(pd.to_datetime('1900-01-01'))

            df['Fertiggestellt'] = df['Fertiggestellt'].fillna(df['PlannedDate'])
            # fill <NA> values in Fertiggestellt with PlannedDate


            df['Fertiggestellt'] = pd.to_datetime(df['Fertiggestellt'])
            
            df['Lieferschein erhalten'] = pd.to_datetime(df['Lieferschein erhalten'])   
            df.sort_values("PlannedDate", inplace=True)
            df = df.reset_index()
            df['Lieferschein erhalten'] = df['Lieferschein erhalten'].dt.date
            # PlannedDate to date only
            df['PlannedDate'] = df['PlannedDate'].dt.date
            try:
                df.loc[df['Lieferschein erhalten'] < df['PlannedDate'], 'Verfügbarkeit'] = 'Vortag'
                df.loc[df['Lieferschein erhalten'] >= df['PlannedDate'], 'Verfügbarkeit'] = 'Verladetag'
            except:
                #all values are Vortag
                df['Verfügbarkeit'] = 'Verladetag'
                st.warning('Der Filter liefert keine Ergebnisse')
            df_grouped = df.groupby(["PlannedDate", "Verfügbarkeit","DeliveryDepot"])["Picks Gesamt"].sum().reset_index()     
            df_grouped = df_grouped.sort_values(by=['PlannedDate','Verfügbarkeit','DeliveryDepot'], ascending=[False,False,False])
            # Create a bar chart of 'Picks Gesamt' grouped by delivery Depot and stacked by sum Vortag and Verladetag
            fig = px.bar(df_grouped, x="PlannedDate", y="Picks Gesamt", color="Verfügbarkeit", barmode=sel_barmode, facet_col=unterteilen,hover_data=["Picks Gesamt","DeliveryDepot","PlannedDate"])
            #remove timespamp from xaxis
            fig.update_xaxes(tickformat='%d.%m.%Y')
            #### DAten Update Wenn DEPOT FILTER updatedate each in facet_col
            # if unterteilen != None:
            # # Create the faceted plot
            #     #updatedate each in facet_col
            #     fig.update_xaxes(showticklabels=True, row=1, col=1)
            #     fig.update_xaxes(showticklabels=True, row=1, col=2)
            #     fig.update_xaxes(showticklabels=True, row=1, col=3)
            #     fig.update_xaxes(showticklabels=True, row=1, col=4)
            #     fig.update_layout(title_text="Picks Gesamt Unterteilt in Zieldepot und Verfügbarkeit", title_x=0.5, title_font_size=20, title_font_family="Montserrat", title_font_color="#0F2B63", legend_title_font_color="#0F2B63", legend_title_font_family="Montserrat", legend_title_font_size=14, legend_font_size=12, legend_font_family="Montserrat", legend_font_color="#0F2B63", height=700)
            #     df_groupedStr = df_grouped[df_grouped['DeliveryDepot'] == 'Stuttgart']
            #     df_groupedStrVerl = df_groupedStr[df_groupedStr['Verfügbarkeit'] == 'Verladetag']
            #     df_groupedStrVerl = df_groupedStrVerl.sort_values(by=['PlannedDate'], ascending=[False])
            #     fig.update_traces( text= df_groupedStrVerl['Picks Gesamt'].astype(str), textposition='inside',selector=dict(name='Verladetag'), row=1, col=1)
            #     df_groupedStrVor = df_groupedStr[df_groupedStr['Verfügbarkeit'] == 'Vortag']
            #     df_groupedStrVor = df_groupedStrVor.sort_values(by=['PlannedDate'], ascending=[False])
            #     fig.update_traces( text= df_groupedStrVor['Picks Gesamt'].astype(str), textposition='inside',selector=dict(name='Vortag'), row=1, col=1)
            #     df_groupedLei = df_grouped[df_grouped['DeliveryDepot'] == 'Leipzig']
            #     df_groupedLeiVerl = df_groupedLei[df_groupedLei['Verfügbarkeit'] == 'Verladetag']
            #     df_groupedLeiVerl = df_groupedLeiVerl.sort_values(by=['PlannedDate'], ascending=[False])
            #     fig.update_traces( text= df_groupedLeiVerl['Picks Gesamt'].astype(str), textposition='inside',selector=dict(name='Verladetag'), row=1, col=2)
            #     df_groupedLeiVor = df_groupedLei[df_groupedLei['Verfügbarkeit'] == 'Vortag']
            #     df_groupedLeiVor = df_groupedLeiVor.sort_values(by=['PlannedDate'], ascending=[False])
            #     fig.update_traces( text= df_groupedLeiVor['Picks Gesamt'].astype(str), textposition='inside',selector=dict(name='Vortag'), row=1, col=2)
            #     df_groupedHan = df_grouped[df_grouped['DeliveryDepot'] == 'Hannover']
            #     df_groupedHanVerl = df_groupedHan[df_groupedHan['Verfügbarkeit'] == 'Verladetag']
            #     df_groupedHanVerl = df_groupedHanVerl.sort_values(by=['PlannedDate'], ascending=[False])
            #     fig.update_traces( text= df_groupedHanVerl['Picks Gesamt'].astype(str), textposition='inside',selector=dict(name='Verladetag'), row=1, col=3)
            #     df_groupedHanVor = df_groupedHan[df_groupedHan['Verfügbarkeit'] == 'Vortag']
            #     df_groupedHanVor = df_groupedHanVor.sort_values(by=['PlannedDate'], ascending=[False])
            #     fig.update_traces( text= df_groupedHanVor['Picks Gesamt'].astype(str), textposition='inside',selector=dict(name='Vortag'), row=1, col=3)
            #     df_groupedBil = df_grouped[df_grouped['DeliveryDepot'] == 'Bielefeld']
            #     df_groupedBilVerl = df_groupedBil[df_groupedBil['Verfügbarkeit'] == 'Verladetag']
            #     df_groupedBilVerl = df_groupedBilVerl.sort_values(by=['PlannedDate'], ascending=[False])
            #     fig.update_traces( text= df_groupedBilVerl['Picks Gesamt'].astype(str), textposition='inside',selector=dict(name='Verladetag'), row=1, col=4)
            #     df_groupedBilVor = df_groupedBil[df_groupedBil['Verfügbarkeit'] == 'Vortag']
            #     df_groupedBilVor = df_groupedBilVor.sort_values(by=['PlannedDate'], ascending=[False])
            #     fig.update_traces( text= df_groupedBilVor['Picks Gesamt'].astype(str), textposition='inside',selector=dict(name='Vortag'), row=1, col=4)
            #     fig.update_layout(font_family="Montserrat",font_color="#0F2B63",title_font_family="Montserrat",title_font_color="#0F2B63")


            # else:
            #         #add text to each bar
            #     df_groupedVor = df_grouped[df_grouped['Verfügbarkeit'] == 'Vortag']
            #     fig.update_traces( text= df_groupedVor['Picks Gesamt'].astype(str) + '<br>'+df_groupedVor['DeliveryDepot'], textposition='inside',selector=dict(name='Vortag'))
            #     df_groupedVer = df_grouped[df_grouped['Verfügbarkeit'] == 'Verladetag']
            #     fig.update_traces( text=df_groupedVer['Picks Gesamt'].astype(str) + '<br>'+df_groupedVer['DeliveryDepot'], textposition='inside',selector=dict(name='Verladetag'))
            # fig.update_layout(title_text="Picks Gesamt DE30 nach Verfügbarkeit", title_x=0.5, title_font_size=20, title_font_family="Montserrat", title_font_color="#0F2B63", legend_title_font_color="#0F2B63", legend_title_font_family="Montserrat", legend_title_font_size=14, legend_font_size=12, legend_font_family="Montserrat", legend_font_color="#0F2B63", legend_orientation="h", height=700)
                 
            # fig.update_layout(
            #         annotations=[
            #             {"x": x, "y": total * 1.05, "text": str(total), "showarrow": False}
            #             for x, total in df.groupby("PlannedDate", as_index=False).agg({"Picks Gesamt": "sum"}).values])
                
            # fig.update_traces(marker_color='#50af47', selector=dict(name='Vortag'))
            # fig.update_traces(marker_color='#e72582', selector=dict(name='Verladetag'))
            # fig.update_layout(font_family="Montserrat",font_color="#0F2B63",title_font_family="Montserrat",title_font_color="#0F2B63")

        

            
            #
            st.plotly_chart(fig, use_container_width=True)       
            ## FARBEN
            if tabelle == True:
                st.dataframe(df)

        def figSAPpicks(dflt22,df):
            df = df.sort_values(by=['PlannedDate'], ascending=[False])
            df_grouped = df.groupby(['PlannedDate'], as_index=False).agg({'Picks Gesamt': 'sum'})
            
        with st.expander('Warehouse', expanded=True):

            col1, col2, col3 = st.columns(3)
            #form selectbox
            with col1:
                sel_NachDepotP = st.selectbox('Gliederung', ['Gesamt','Depot'],key='1NachDepotP')
                sel_tabelleP = st.checkbox('Tabelle Anzeigen:', value=False, key='1tableP')
            with col2:
                sel_GesamtOderNachDepot = st.selectbox('Unterteilt in:', ['Lieferscheine','Picks WH'],key='1GesamtOderNachDepotP')
                if st.checkbox('Gestapelt', value=True, key='1GestapeltP'):
                    sel_barmodeP = 'stack'
                else:
                    sel_barmodeP = 'group'
            with col3:
                    sel_MengeneinheitP = st.selectbox('Mengeneinheit:', ['Picks','KG/TH'],key='1MengeP')
            # unterteilen ja nein       
            if sel_NachDepotP == 'Depot':
                    unterteilen = 'DeliveryDepot'
            if sel_NachDepotP == 'Gesamtvolumen':
                    unterteilen = None
            #wich SumOf
            # if sel_GesamtOderNachDepot == 'Kunden':
            #     figPicksGesamtKunden(df,unterteilen,sel_tabelle,sel_barmode=sel_barmode)
            if sel_GesamtOderNachDepot == 'Verfügbarkeit':
                figLieferscheinFertigTag(df,unterteilen,sel_tabelleP,sel_barmode=sel_barmodeP)
        
            figSAPpicks(dflt22)
    

def expanderTruckAuslastung(df):
        def figPalTruckAuslastung(df):
            # Create a bar chart of 'Picks Gesamt' grouped by delivery Depot and stacked by sum Vortag and Verladetag
            fig = px.bar(df, x="PlannedDate", y='Fertige Paletten', color="Truck Kennzeichen", barmode='group', facet_col="DeliveryDepot",hover_data=["Picks Gesamt","DeliveryDepot","PlannedDate","Lieferschein erhalten"])
            fig.update_layout(showlegend=False)
            fig.update_layout(font_family="Montserrat",font_color="#0F2B63",title_font_family="Montserrat",title_font_color="#0F2B63")
            #remove timespamp from xaxis
            fig.update_xaxes(tickformat='%d.%m.%Y')
            st.plotly_chart(fig, use_container_width=True)
            #plotly sum of stacked bar

        with st.expander('Truck Auslastung', expanded=True):
            figPalTruckAuslastung(df)

def expanderKundenVerhalten(df):
    pass
#main function ###########################################
def ddsPage():
    dfLT22 = pd.read_parquet('Data/upload/lt22.parquet')
    dfOr = sql.sql_datenTabelleLaden('prod_Kundenbestellungen')
    dfHannover = pd.read_parquet('Data/appData/dfDe55.parquet')
   #pd.set_option("display.precision", 2)   
    df = berechneAlleDepots(dfOr, dfHannover)
    df = dateFilter(df)

    
    expanderFigGesamtPicks(df)
    expanderPicksLager(df,dfLT22)
    #expanderKundenVerhalten(df)
    expanderTruckAuslastung(df)
    #st.dataframe(df)       

