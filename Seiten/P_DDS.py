
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
import plotly.graph_objs as go
import plotly.subplots as sp
from PIL import Image




#Berichtsdaten laden und berechnen und Filtern ##############
def dateFilterdfOr(df: pd,dflt22: pd):
    '''erwartet df (DB_Daten_Agg) und dflt22 (DB_Daten_SAP) als pd.DataFrame'''
    #dflt22['Pick Datum'] to datetime
    dflt22['Pick Datum'] = pd.to_datetime(dflt22['Pick Datum'])

    df['PlannedDate'] = df['PlannedDate'].astype(str)
    df['PlannedDate'] = pd.to_datetime(df['PlannedDate'].str[:10])
    df['Tag'] = df['PlannedDate'].dt.strftime('%d.%m.%Y')
    dflt22['Tag'] = dflt22['Pick Datum']

   # df tag to datetime.date
    df['Tag'] = pd.to_datetime(df['Tag'])
    df['Wochentag'] = df['PlannedDate'].dt.strftime('%A')
    dflt22['Wochentag'] = dflt22['Pick Datum'].dt.strftime('%A')
    # df['Woche'] = Wochennummer und Jahr
    df['Woche'] = df['PlannedDate'].dt.strftime('%V.%Y')
    dflt22['Woche'] = dflt22['Pick Datum'].dt.strftime('%V.%Y')
    
    df['Monat'] = df['PlannedDate'].dt.strftime('%m.%Y')
    dflt22['Monat'] = dflt22['Pick Datum'].dt.strftime('%m.%Y')

    col1, col2, col3 = st.columns(3)
    # Nach Zeitraum Devinieren
    with col1:
        sel_datePicker = st.selectbox('Zeitraum:', ['Woche','Tag','Tage letzte 30', 'Tage letzte 90'])
    # Nach Tage filtern
    with col2:
        if sel_datePicker == 'Tag':
            sel_date = st.date_input('Wähle Tag')
            sel_date = sel_date.strftime('%d.%m.%Y')
            df = df[df['Tag'] == sel_date]
            dflt22 = dflt22[dflt22['Tag'] == sel_date]
        if sel_datePicker == 'Tage letzte 30':
            end_date = datetime.date.today()
            start_date = end_date - datetime.timedelta(days=30)
            format = "DD.MM.YYYY"
            sel_dateRange = st.slider('Selektiere Zeitraum', min_value=start_date, value=(start_date, end_date), max_value=end_date, format=format)
            df = df[(df['Tag'] >= np.datetime64(sel_dateRange[0])) & (df['Tag'] <= np.datetime64(sel_dateRange[1]))]
            dflt22 = dflt22[(dflt22['Tag'] >= np.datetime64(sel_dateRange[0])) & (dflt22['Tag'] <= np.datetime64(sel_dateRange[1]))]
        if sel_datePicker == 'Tage letzte 90':
            end_date = datetime.date.today()
            start_date = end_date - datetime.timedelta(days=90)
            format = "DD.MM.YYYY"
            sel_dateRange = st.slider('Selektiere Zeitraum', min_value=start_date, value=(start_date, end_date), max_value=end_date, format=format)
            df = df[(df['Tag'] >= np.datetime64(sel_dateRange[0])) & (df['Tag'] <= np.datetime64(sel_dateRange[1]))]
            dflt22 = dflt22[(dflt22['Tag'] >= np.datetime64(sel_dateRange[0])) & (dflt22['Tag'] <= np.datetime64(sel_dateRange[1]))]
        if sel_datePicker == 'Woche':
            dfWeek = df['Woche'].unique()
            dfWeek = np.sort(dfWeek)
            sel_weekRange = st.selectbox('Wähle Woche', dfWeek)
            df = df[df['Woche'] == sel_weekRange]
            dflt22 = dflt22[dflt22['Woche'] == sel_weekRange]
    # Nach Wochentag filtern
    with col3:
        sel_Wochentag = st.selectbox('Wochentag Filtern:', ['Alle', 'Montag', 'Dienstag', 'Mittwoch', 'Donnerstag', 'Freitag', 'Samstag', 'Sonntag'])
        if sel_Wochentag != 'Alle':
            if sel_Wochentag == 'Montag':
                df = df[df['Wochentag'] == 'Monday']
                dflt22 = dflt22[dflt22['Wochentag'] == 'Monday']
            elif sel_Wochentag == 'Dienstag':
                df = df[df['Wochentag'] == 'Tuesday']#
                dflt22 = dflt22[dflt22['Wochentag'] == 'Tuesday']
            elif sel_Wochentag == 'Mittwoch':
                df = df[df['Wochentag'] == 'Wednesday']
                dflt22 = dflt22[dflt22['Wochentag'] == 'Wednesday']
            elif sel_Wochentag == 'Donnerstag':
                df = df[df['Wochentag'] == 'Thursday']
                dflt22 = dflt22[dflt22['Wochentag'] == 'Thursday']
            elif sel_Wochentag == 'Freitag':
                df = df[df['Wochentag'] == 'Friday']
                dflt22 = dflt22[dflt22['Wochentag'] == 'Friday']
            elif sel_Wochentag == 'Samstag':
                df = df[df['Wochentag'] == 'Saturday']
                dflt22 = dflt22[dflt22['Wochentag'] == 'Saturday']
            elif sel_Wochentag == 'Sonntag':
                df = df[df['Wochentag'] == 'Sunday']
                dflt22 = dflt22[dflt22['Wochentag'] == 'Sunday']

    return df, dflt22


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
    data = {
    'city': ['Leipzig', 'Stuttgart', 'Hannover', 'Bielefeld'],
    'latitude': [51.339695, 48.775846, 52.375892, 52.031257],
    'longitude': [12.373075, 9.182932, 9.732010, 8.523864]}
    #merge df with databy Depot
    df = pd.merge(df, pd.DataFrame(data), left_on='DeliveryDepot', right_on='city')
    return df

def berechne_dfOr_Pickdauer(df, dflt22):
    # create culumn df['ErsterPickTime'] and df['LetzterPickTime'] with value 0
    df['ErsterPickTime'] = 0
    df['LetzterPickTime'] = 0
    df['PickDauer'] = 0
    
    df['ErsterPickTime'] = df.apply(lambda x: dflt22[dflt22['DestBin'] == x['SapOrderNumber']]['Pick Zeit'].max(), axis=1)
    df['LetzterPickTime'] = df.apply(lambda x: dflt22[dflt22['DestBin'] == x['SapOrderNumber']]['Pick Zeit'].min(), axis=1)
    df['PickDauer'] = df.apply(lambda x: x['ErsterPickTime'] - x['LetzterPickTime'], axis=1)
    df['PickDauer'] = df['PickDauer'].dt.total_seconds()
    #in minutes


    df['LetzterPickDate'] = df.apply(lambda x: dflt22[dflt22['DestBin'] == x['SapOrderNumber']]['Pick Datum'].max(), axis=1)
    df['ErsterPickDate'] = df.apply(lambda x: dflt22[dflt22['DestBin'] == x['SapOrderNumber']]['Pick Datum'].min(), axis=1)
    def calculate_picks_per_minute(row):
        if row['Picks Gesamt'] == 0:
            return 0
        else:
            return row['PickDauer'] / row['Picks Gesamt']
    def calculate_duration(row):
        start_time = row['LetzterPickTime']
        end_time = row['ErsterPickTime']
        start_date = row['LetzterPickDate']
        end_date = row['ErsterPickDate']
        duration = end_time - start_time
        if end_date > start_date:
            duration - 28800
        return duration.total_seconds() / 60.

    df['PickDauer'] = df.apply(calculate_duration, axis=1)
    #round to 2 decimals
    df['PickDauer'] = df['PickDauer'].round()
    df['PicksProMinute'] = df.apply(calculate_picks_per_minute, axis=1)
    df['PicksProMinute'] = df['PicksProMinute'].round()

    def calculate_picks_per_stunde(row):
        if row['Picks Gesamt'] == 0:
            return 0
        else:
            return (row['PickDauer']*60) / row['Picks Gesamt']

    df['PicksProStunde'] = df.apply(calculate_picks_per_stunde, axis=1)
    df['PicksProStunde'] = df['PicksProStunde'].round()
    df['PlannedDate'] = pd.to_datetime(df['PlannedDate'])
    return df

# Grafiken ###################################################
def expanderFigGesamtPicks(df,dflt22):
        
        def figGesamtVolumen(df,unterteilen,tabelle,sel_barmode):
            df = df.groupby(['PlannedDate','DeliveryDepot']).agg({'Picks Gesamt':'sum','Picks Karton':'sum','Picks Stangen':'sum','Picks Paletten':'sum'}).reset_index()
            df['Picks Gesamt'] = df['Picks Gesamt'].round(0).astype(int)
            df['Picks Karton'] = df['Picks Karton'].round(0).astype(int)
            df['Picks Stangen'] = df['Picks Stangen'].round(0).astype(int)
            df['Picks Paletten'] = df['Picks Paletten'].round(0).astype(int)
            #df PlannedDate to dd:mm:yyyy
            df['PlannedDate'] = df['PlannedDate'].dt.strftime('%d.%m.%Y')
            #i as double  = sum of Picks Gesamt by PlannedDate

            fig = px.bar(df, x="PlannedDate", y="Picks Gesamt", barmode=sel_barmode, facet_col=unterteilen,hover_data=["Picks Gesamt","DeliveryDepot","PlannedDate"])
            fig.update_traces(marker_color='#0e2b63')
            fig.update_layout(title_text="Picks Gesamt DE30", title_font_size=20, title_font_family="Montserrat", title_font_color="#0F2B63", height=700)

            if unterteilen == 'DeliveryDepot':
                fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
                #sum of each bar to tex
            else:
                fig.update_layout(
                    annotations=[
                        {"x": x, "y": total * 1.05, "text": str(total), "showarrow": False}
                        for x, total in df.groupby("PlannedDate", as_index=False).agg({"Picks Gesamt": "sum"}).values])
    
            st.plotly_chart(fig,use_container_width=True)

            if tabelle == 'Ja':
                st.write(df)
                    
        def figMap(df,tabelle):
            df = df.groupby(['DeliveryDepot','latitude','longitude']).agg({'Picks Gesamt':'sum'}).reset_index()
            df['text'] = df['DeliveryDepot'] + "<br>Picks Gesamt: " + df['Picks Gesamt'].astype(str)
            fig = px.scatter_mapbox(df, lat="latitude", lon="longitude", hover_name="DeliveryDepot", hover_data=["Picks Gesamt"], color_discrete_sequence=["fuchsia"], size="Picks Gesamt", size_max=50, zoom=5, height=600)
            fig.update_layout(mapbox_style="carto-positron", showlegend=False)
            fig.update_traces(marker_color='#0e2b63', text=df['text'])
            
            st.plotly_chart(fig,use_container_width=True)
            if tabelle == True:
                st.dataframe(df)





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
            df_grouped = df
            #### DAten Update Wenn DEPOT FILTER updatedate each in facet_col
            if unterteilen == None:
                fig.update_layout(title_text="Picks Gesamt DE30 nach Kunden", title_font_size=20, title_font_family="Montserrat", title_font_color="#0F2B63", height=700)
                fig.update_layout(
                        annotations=[
                            {"x": x, "y": total * 1.05, "text": str(total), "showarrow": False}
                            for x, total in df.groupby("PlannedDate", as_index=False).agg({"Picks Gesamt": "sum"}).values])            
            else:
                fig.update_layout(title_text="Picks Gesamt DE30 nach Kunden und Depot", title_font_size=20, title_font_family="Montserrat", title_font_color="#0F2B63", height=700)
             

                
            fig.update_traces(marker_color='#50af47', selector=dict(name='Vortag'))
            fig.update_traces(marker_color='#e72582', selector=dict(name='Verladetag'))
            fig.update_layout(font_family="Montserrat",font_color="#0F2B63",title_font_family="Montserrat",title_font_color="#0F2B63")

            st.plotly_chart(fig, use_container_width=True)       
            ## FARBEN
            if tabelle == True:
                st.dataframe(df)
                
        def figPicksGesamtnachTagUndVerfügbarkeit(df,unterteilen,tabelle,sel_barmode):
            ##TODO Try Except if not all Depots selectet
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
            fig.update_xaxes(showticklabels=True)
            #### DAten Update Wenn DEPOT FILTER updatedate each in facet_col
            if unterteilen != None:
            # Create the faceted plot
                #updatedate each in facet_col
                fig.update_xaxes(showticklabels=True, row=1, col=1)
                fig.update_xaxes(showticklabels=True, row=1, col=2)
                fig.update_xaxes(showticklabels=True, row=1, col=3)
                fig.update_xaxes(showticklabels=True, row=1, col=4)
                fig.update_layout(title_text="Picks Gesamt Unterteilt in Zieldepot und Verfügbarkeit", title_x=0.5, title_font_size=20, title_font_family="Montserrat", title_font_color="#0F2B63", legend_title_font_color="#0F2B63", legend_title_font_family="Montserrat", legend_title_font_size=14, legend_font_size=12, legend_font_family="Montserrat", legend_font_color="#0F2B63", height=700)
                try:
                    df_groupedStr = df_grouped[df_grouped['DeliveryDepot'] == 'Stuttgart']
                    df_groupedStrVerl = df_groupedStr[df_groupedStr['Verfügbarkeit'] == 'Verladetag']
                    df_groupedStrVerl = df_groupedStrVerl.sort_values(by=['PlannedDate'], ascending=[False])
                    fig.update_traces( text= df_groupedStrVerl['Picks Gesamt'].astype(str), textposition='inside',selector=dict(name='Verladetag'), row=1, col=1)
                    df_groupedStrVor = df_groupedStr[df_groupedStr['Verfügbarkeit'] == 'Vortag']
                    df_groupedStrVor = df_groupedStrVor.sort_values(by=['PlannedDate'], ascending=[False])
                except:
                     pass
                try:
                    fig.update_traces( text= df_groupedStrVor['Picks Gesamt'].astype(str), textposition='inside',selector=dict(name='Vortag'), row=1, col=1)
                    df_groupedLei = df_grouped[df_grouped['DeliveryDepot'] == 'Leipzig']
                    df_groupedLeiVerl = df_groupedLei[df_groupedLei['Verfügbarkeit'] == 'Verladetag']
                    df_groupedLeiVerl = df_groupedLeiVerl.sort_values(by=['PlannedDate'], ascending=[False])
                    fig.update_traces( text= df_groupedLeiVerl['Picks Gesamt'].astype(str), textposition='inside',selector=dict(name='Verladetag'), row=1, col=2)
                    df_groupedLeiVor = df_groupedLei[df_groupedLei['Verfügbarkeit'] == 'Vortag']
                    df_groupedLeiVor = df_groupedLeiVor.sort_values(by=['PlannedDate'], ascending=[False])
                except:
                    pass
                try:
                    fig.update_traces( text= df_groupedLeiVor['Picks Gesamt'].astype(str), textposition='inside',selector=dict(name='Vortag'), row=1, col=2)
                    df_groupedHan = df_grouped[df_grouped['DeliveryDepot'] == 'Hannover']
                    df_groupedHanVerl = df_groupedHan[df_groupedHan['Verfügbarkeit'] == 'Verladetag']
                    df_groupedHanVerl = df_groupedHanVerl.sort_values(by=['PlannedDate'], ascending=[False])
                    fig.update_traces( text= df_groupedHanVerl['Picks Gesamt'].astype(str), textposition='inside',selector=dict(name='Verladetag'), row=1, col=3)
                    df_groupedHanVor = df_groupedHan[df_groupedHan['Verfügbarkeit'] == 'Vortag']
                    df_groupedHanVor = df_groupedHanVor.sort_values(by=['PlannedDate'], ascending=[False])
                except:
                    pass
                try:
                    fig.update_traces( text= df_groupedHanVor['Picks Gesamt'].astype(str), textposition='inside',selector=dict(name='Vortag'), row=1, col=3)
                    df_groupedBil = df_grouped[df_grouped['DeliveryDepot'] == 'Bielefeld']
                    df_groupedBilVerl = df_groupedBil[df_groupedBil['Verfügbarkeit'] == 'Verladetag']
                    df_groupedBilVerl = df_groupedBilVerl.sort_values(by=['PlannedDate'], ascending=[False])
                    fig.update_traces( text= df_groupedBilVerl['Picks Gesamt'].astype(str), textposition='inside',selector=dict(name='Verladetag'), row=1, col=4)
                    df_groupedBilVor = df_groupedBil[df_groupedBil['Verfügbarkeit'] == 'Vortag']
                    df_groupedBilVor = df_groupedBilVor.sort_values(by=['PlannedDate'], ascending=[False])
                    fig.update_traces( text= df_groupedBilVor['Picks Gesamt'].astype(str), textposition='inside',selector=dict(name='Vortag'), row=1, col=4)
                except:
                    pass
                # fig.update_layout(font_family="Montserrat",font_color="#0F2B63",title_font_family="Montserrat",title_font_color="#0F2B63")
                # fig.update_layout(
                #         annotations=[
                #             {"x": x, "y": total * 1.05, "text": str(total), "showarrow": False}
                #             for x, total in df.groupby("PlannedDate", as_index=False).agg({"Picks Gesamt": "sum"}).values])

            else:
                
                df_groupedVor = df_grouped[df_grouped['Verfügbarkeit'] == 'Vortag']
                fig.update_traces( text= df_groupedVor['Picks Gesamt'].astype(str) + '<br>'+df_groupedVor['DeliveryDepot'], textposition='inside',selector=dict(name='Vortag'))
                df_groupedVer = df_grouped[df_grouped['Verfügbarkeit'] == 'Verladetag']
                fig.update_traces( text=df_groupedVer['Picks Gesamt'].astype(str) + '<br>'+df_groupedVer['DeliveryDepot'], textposition='inside',selector=dict(name='Verladetag'))
            fig.update_layout(title_text="Picks Gesamt DE30 nach Verfügbarkeit", title_x=0.5, title_font_size=20, title_font_family="Montserrat", title_font_color="#0F2B63", legend_title_font_color="#0F2B63", legend_title_font_family="Montserrat", legend_title_font_size=14, legend_font_size=12, legend_font_family="Montserrat", legend_font_color="#0F2B63", legend_orientation="h", height=700)
                 

                
            fig.update_traces(marker_color='#50af47', selector=dict(name='Vortag'))
            fig.update_traces(marker_color='#ef7d00', selector=dict(name='Verladetag'))
            fig.update_layout(font_family="Montserrat",font_color="#0F2B63",title_font_family="Montserrat",title_font_color="#0F2B63")

        

            
            #
            st.plotly_chart(fig, use_container_width=True)       
            ## FARBEN
            if tabelle == True:
                st.dataframe(df)
                
        def figStudeneinsatz(df,dflt22, tabelle,sel_barmodeP,unterteilen):
            col1, col2 = st.columns(2)
            with col1:    
                sel_inProzent= st.selectbox('Total Summen',['In Prozent', 'in Stunden'],key='stundeinStudeneinsatz')            #create px Area Chart by PlannedDate and Bearbeitungszeit
                # rename PickDauer in Bearbeitungszeit
                df = df.rename(columns={'PickDauer':'Bearbeitungszeit'})
            with col2:
                anzal_MaStunden = st.number_input('Anzahl Mitarbeiterstunden', min_value=8, max_value=900, value=168, step=1, key='anzal_MAStunden')

            #sort by Bearbeitungszeit
            df = df.sort_values(by=['Bearbeitungszeit'], ascending=[False])
            df['Bearbeitungszeit'] = df['Bearbeitungszeit']/60

            df = df.groupby(["PlannedDate",'Picks Gesamt','DeliveryDepot'])["Bearbeitungszeit"].sum().reset_index()
            #add to df_groupby[Mitarbeiterstunden] = anzal_MaStunden
            df['Mitarbeiterstunden'] = anzal_MaStunden
            #add to df_groupby[Picks Pro Stunde] = df_groupby['Picks Gesamt']/df_groupby['Mitarbeiterstunden']
            df['Picks Pro Stunde'] = df['Picks Gesamt']/df['Mitarbeiterstunden']
            dfPicksStunde = df.groupby(["PlannedDate"])["Picks Pro Stunde"].sum().reset_index()
            dfStundenEinsatz = df.groupby(["PlannedDate"])["Bearbeitungszeit"].sum().reset_index()

            # fig histogramm
            # merge to df for fig
            df = pd.merge(dfStundenEinsatz, dfPicksStunde, on='PlannedDate', how='left')
            #df planeddate to string for fig in dd.mm.yyyy
            df['Mitarbeiterstunden'] = anzal_MaStunden

            df['PlannedDate'] = df['PlannedDate'].dt.strftime('%d.%m.%Y')
            #to string for fig
            df['PlannedDate'] = df['PlannedDate'].astype(str)

            #create px Area Chart by PlannedDate and Bearbeitungszeit
            if sel_inProzent == 'In Prozent':
                fig = px.bar(df, x="PlannedDate", y=["Bearbeitungszeit", "Mitarbeiterstunden"], barmode=sel_barmodeP)
                fig.update_layout(title_text="Stundeneinsatz DE30 für Verladetag", title_x=0.5, title_font_size=20, title_font_family="Montserrat", title_font_color="#0F2B63", legend_title_font_color="#0F2B63", legend_title_font_family="Montserrat", legend_title_font_size=14, legend_font_size=12, legend_font_family="Montserrat", legend_font_color="#0F2B63", legend_orientation="h", height=700)
                fig.update_traces(marker_color='#0e2b63', selector=dict(name='Bearbeitungszeit'))
                fig.update_traces(marker_color='#ffbb00', selector=dict(name='Mitarbeiterstunden'))
                fig.update_layout(font_family="Montserrat",font_color="#0F2B63",title_font_family="Montserrat",title_font_color="#0F2B63")
                fig.update_layout(
                    annotations=[
                        {"x": x, "y": total * 1.05, "text": str(total), "showarrow": False}
                        for x, total in df.groupby("PlannedDate", as_index=False).agg({"Bearbeitungszeit": "sum"}).values])                
            else:
                fig = px.bar(df, x="PlannedDate", y=["Bearbeitungszeit", "Mitarbeiterstunden"], barmode=sel_barmodeP)
                fig.update_layout(title_text="Stundeneinsatz DE30 für Verladetag", title_x=0.5, title_font_size=20, title_font_family="Montserrat", title_font_color="#0F2B63", legend_title_font_color="#0F2B63", legend_title_font_family="Montserrat", legend_title_font_size=14, legend_font_size=12, legend_font_family="Montserrat", legend_font_color="#0F2B63", legend_orientation="h", height=700)
                fig.update_traces(marker_color='#0e2b63', selector=dict(name='Bearbeitungszeit'))
                fig.update_traces(marker_color='#ffbb00', selector=dict(name='Mitarbeiterstunden'))
                fig.update_layout(font_family="Montserrat",font_color="#0F2B63",title_font_family="Montserrat",title_font_color="#0F2B63")
                fig.update_layout(
                    annotations=[
                        {"x": x, "y": total * 1.05, "text": str(total), "showarrow": False}
                        for x, total in df.groupby("PlannedDate", as_index=False).agg({"Bearbeitungszeit": "sum"}).values])
    
            st.plotly_chart(fig, use_container_width=True)
            if tabelle == True:
                st.dataframe(df)

        def figUebermitteltInDeadline(df):
        # Kannst du mir ein Plotly chart geben welches eine Zeitachse hat und darauf die Lieferschiene ausgibt und anzeigt ob inTime oder nicht 
            
            col1, col2 = st.columns(2)
            with col1:
                sel_deadStr = st.text_input('Deadline Lej', '14:00:00')
            with col2:
                sel_deadLej = st.text_input('Deadline Str', '14:00:00')
            #add deadlines to df by DeliveryDepot
            df['Deadline'] = np.where(df['DeliveryDepot'] == 'KNLEJ', sel_deadStr, sel_deadLej)
            df['PlannedDate'] = df['PlannedDate'] + pd.to_timedelta(df['Deadline'])
            #convert to datetime
            df['PlannedDate'] = pd.to_datetime(df['PlannedDate'])
            # filter by fertiggestellt = '0'
            dfOffen = df[df['Fertiggestellt'] == '0']
            dfFertig = df[df['Fertiggestellt'] != '0']
            dfFertig.Fertiggestellt = pd.to_datetime(dfFertig.Fertiggestellt)
            #chek if is inTime
            dfFertig['InTime'] = (dfFertig['Fertiggestellt'] < dfFertig['PlannedDate']).astype(int)
            dfFertig['Fertig um'] = dfFertig['Fertiggestellt']
            dfFertig['Fertig um'] = dfFertig['Fertig um'].dt.strftime('%d.%m.%Y %H:%M')
            #round to hour
            dfFertig['Fertiggestellt'] = dfFertig['Fertiggestellt'].dt.round('H')
            #change format to day as text and hour
            dfFertig['Fertiggestellt'] = dfFertig['Fertiggestellt'].dt.strftime('%d.%m.%Y %H:%M')
            #group by
            dfFertig = dfFertig.groupby(['PlannedDate','PartnerName','Fertiggestellt','SapOrderNumber','DeliveryDepot','InTime','Fertig um']).agg({'Picks Gesamt':'sum'}).reset_index()
            #sort by Fertiggestellt
            dfFertig = dfFertig.sort_values(by=['Fertiggestellt'], ascending=True)
            #Create Plotly Chart
            fig = px.bar(dfFertig, x='Fertiggestellt', y="Picks Gesamt", color="InTime", hover_data=['PartnerName','Fertig um','SapOrderNumber','DeliveryDepot'],height=600)
            #if in Time 1 set to green else to red
            fig.update_traces(marker_color=['#4FAF46' if x == 1 else '#E72482' for x in dfFertig['InTime']])
            fig.data[0].text = dfFertig['PartnerName'] + '<br>' + dfFertig['Picks Gesamt'].astype(str)
            fig.layout.xaxis.type = 'category'
            # x aaxis text horizontal
            fig.layout.xaxis.tickangle = 70
            # remove xaxis and yaxis title
            fig.update_xaxes(title_text='')
            fig.update_yaxes(title_text='')
            fig.update_layout(font_family="Montserrat",font_color="#0F2B63",title_font_family="Montserrat",title_font_color="#0F2B63")
            fig.update_layout(legend_title_text='InTime')
            
            # Date PartnerName to text
            st.plotly_chart(fig, use_container_width=True)


        with st.expander('Volumen', expanded=True):

            col1, col2, col3 = st.columns(3)
            #form selectbox
            with col1:
                sel_NachDepot = st.selectbox('Gliederung nach:', ['Alle Depots zusammen','Depot unterteilt'])
                sel_tabelle = st.checkbox('Tabelle Anzeigen:', value=False)
            with col2:
                sel_Auswertungstyp = st.selectbox('Auswertung:', ['Gesamtvolumen','Übermittelt in Deadline','Verfügbarkeit','Kunden','Stundeneinsatz','Karte'],key='AuswertungstypGesamt')
                if st.checkbox('Gestapelt', value=True):
                    sel_barmode = 'stack'
                else:
                    sel_barmode = 'group'
            with col3:
                sel_Mengeneinheit = st.selectbox('Mengeneinheit:', ['Picks','KG/TH'])
            # unterteilen ja nein       
            if sel_NachDepot == 'Depot unterteilt':
                    unterteilen = 'DeliveryDepot'
            if sel_NachDepot == 'Alle Depots zusammen':
                    unterteilen = None
            #wich SumOf
            if sel_Auswertungstyp == 'Gesamtvolumen':
                figGesamtVolumen(df,unterteilen,sel_tabelle,sel_barmode)
            if sel_Auswertungstyp == 'Kunden':
                figPicksGesamtKunden(df,unterteilen,sel_tabelle,sel_barmode=sel_barmode)
            if sel_Auswertungstyp == 'Verfügbarkeit':
                figPicksGesamtnachTagUndVerfügbarkeit(df,unterteilen,sel_tabelle,sel_barmode=sel_barmode)
            if sel_Auswertungstyp == 'Stundeneinsatz':
                figStudeneinsatz(df,dflt22,sel_tabelle,sel_barmode,unterteilen)
            if sel_Auswertungstyp == 'Übermittelt in Deadline':
                figUebermitteltInDeadline(df,unterteilen,sel_tabelle,sel_barmode=sel_barmode)
            if sel_Auswertungstyp == 'Karte':
                figMap(df,sel_tabelle)



def expanderPicksLager(df,dflt22):
 

        def figSAPpicks(dflt22, df):

            dflt22 = dflt22[dflt22['SuperDepot'] == True]
            #group df by PlannedDate and SapOrderNumber

            dfOrder_grouped = df.groupby(['PlannedDate']).agg({'Picks Gesamt':'sum'}).reset_index()
            dflt22_grouped = dflt22.groupby(['Pick Datum']).agg({'PICKS':'sum'}).reset_index()

            # create first plot
            bar_plot = go.Bar(x=dfOrder_grouped['PlannedDate'], y=dfOrder_grouped['Picks Gesamt'], name='Picks Gesamt')

            # create second plot
            line_plot = go.Line(x=dflt22_grouped['Pick Datum'], y=dflt22_grouped['PICKS'], name='PICKS', mode='lines+markers')

            # create subplots
            fig = sp.make_subplots(rows=1, cols=2, shared_yaxes=True, subplot_titles=('Picks by Date and SAP Order', 'Picks by Date and DestBin'))
            fig.add_trace(bar_plot, row=1, col=1)
            fig.add_trace(line_plot, row=1, col=2)

            # update subplot titles
            fig.update_layout(title='Picks by Date and SAP Order', xaxis_title='Date', yaxis_title='Picks')

            st.plotly_chart(fig, use_container_width=True)


            st.dataframe(dflt22_grouped)
            st.dataframe(dfOrder_grouped)

        def figBearbeitungsdauerLS(df,dflt22, tabelle,sel_barmodeP,unterteilen):
        
            col1, col2 = st.columns(2)
            with col1:    
                sel_stunde_minute = st.selectbox('Zeiteinheit',['in Minuten', 'in Stunden'],key='stundeinBearbeitungs')            #create px Area Chart by PlannedDate and Bearbeitungszeit
                # rename PickDauer in Bearbeitungszeit
                df = df.rename(columns={'PickDauer':'Bearbeitungszeit'})
            with col2:
                pass

            #sort by Bearbeitungszeit
            df = df.sort_values(by=['Bearbeitungszeit'], ascending=[False])
            if sel_stunde_minute == 'in Stunden':
                df['Bearbeitungszeit'] = df['Bearbeitungszeit']/60
            df_grouped = df.groupby(["PlannedDate"])["Bearbeitungszeit"].sum().reset_index()     
            #df_grouped = df_grouped.sort_values(by=['PlannedDate','DeliveryDepot'], ascending=[False,False])

            fig = px.bar(df, x="PlannedDate", y="Bearbeitungszeit",color='SapOrderNumber',barmode=sel_barmodeP,facet_col=unterteilen, title="Bearbeitungszeit pro Lieferschein", color_discrete_sequence=px.colors.qualitative.Dark24)

            if unterteilen != None:
            # Create the faceted plot
                #updatedate each in facet_col
                fig.update_xaxes(showticklabels=True, row=1, col=1)
                fig.update_xaxes(showticklabels=True, row=1, col=2)
                fig.update_xaxes(showticklabels=True, row=1, col=3)
                fig.update_xaxes(showticklabels=True, row=1, col=4)
                fig.update_layout(title_text="Picks Gesamt Unterteilt in Zieldepot und Verfügbarkeit", title_x=0.5, title_font_size=20, title_font_family="Montserrat", title_font_color="#0F2B63", legend_title_font_color="#0F2B63", legend_title_font_family="Montserrat", legend_title_font_size=14, legend_font_size=12, legend_font_family="Montserrat", legend_font_color="#0F2B63", height=700)
                try:
                    df_groupedStr = df_grouped[df_grouped['DeliveryDepot'] == 'Stuttgart']
                    df_groupedStrVerl = df_groupedStr[df_groupedStr['Verfügbarkeit'] == 'Verladetag']
                    df_groupedStrVerl = df_groupedStrVerl.sort_values(by=['PlannedDate'], ascending=[False])
                    fig.update_traces( text= df_groupedStrVerl['Picks Gesamt'].astype(str), textposition='inside',selector=dict(name='Verladetag'), row=1, col=1)
                    df_groupedStrVor = df_groupedStr[df_groupedStr['Verfügbarkeit'] == 'Vortag']
                    df_groupedStrVor = df_groupedStrVor.sort_values(by=['PlannedDate'], ascending=[False])
                except:
                     pass
                try:
                    fig.update_traces( text= df_groupedStrVor['Picks Gesamt'].astype(str), textposition='inside',selector=dict(name='Vortag'), row=1, col=1)
                    df_groupedLei = df_grouped[df_grouped['DeliveryDepot'] == 'Leipzig']
                    df_groupedLeiVerl = df_groupedLei[df_groupedLei['Verfügbarkeit'] == 'Verladetag']
                    df_groupedLeiVerl = df_groupedLeiVerl.sort_values(by=['PlannedDate'], ascending=[False])
                    fig.update_traces( text= df_groupedLeiVerl['Picks Gesamt'].astype(str), textposition='inside',selector=dict(name='Verladetag'), row=1, col=2)
                    df_groupedLeiVor = df_groupedLei[df_groupedLei['Verfügbarkeit'] == 'Vortag']
                    df_groupedLeiVor = df_groupedLeiVor.sort_values(by=['PlannedDate'], ascending=[False])
                except:
                    pass
                try:
                    fig.update_traces( text= df_groupedLeiVor['Picks Gesamt'].astype(str), textposition='inside',selector=dict(name='Vortag'), row=1, col=2)
                    df_groupedHan = df_grouped[df_grouped['DeliveryDepot'] == 'Hannover']
                    df_groupedHanVerl = df_groupedHan[df_groupedHan['Verfügbarkeit'] == 'Verladetag']
                    df_groupedHanVerl = df_groupedHanVerl.sort_values(by=['PlannedDate'], ascending=[False])
                    fig.update_traces( text= df_groupedHanVerl['Picks Gesamt'].astype(str), textposition='inside',selector=dict(name='Verladetag'), row=1, col=3)
                    df_groupedHanVor = df_groupedHan[df_groupedHan['Verfügbarkeit'] == 'Vortag']
                    df_groupedHanVor = df_groupedHanVor.sort_values(by=['PlannedDate'], ascending=[False])
                except:
                    pass
                try:
                    fig.update_traces( text= df_groupedHanVor['Picks Gesamt'].astype(str), textposition='inside',selector=dict(name='Vortag'), row=1, col=3)
                    df_groupedBil = df_grouped[df_grouped['DeliveryDepot'] == 'Bielefeld']
                    df_groupedBilVerl = df_groupedBil[df_groupedBil['Verfügbarkeit'] == 'Verladetag']
                    df_groupedBilVerl = df_groupedBilVerl.sort_values(by=['PlannedDate'], ascending=[False])
                    fig.update_traces( text= df_groupedBilVerl['Picks Gesamt'].astype(str), textposition='inside',selector=dict(name='Verladetag'), row=1, col=4)
                    df_groupedBilVor = df_groupedBil[df_groupedBil['Verfügbarkeit'] == 'Vortag']
                    df_groupedBilVor = df_groupedBilVor.sort_values(by=['PlannedDate'], ascending=[False])
                    fig.update_traces( text= df_groupedBilVor['Picks Gesamt'].astype(str), textposition='inside',selector=dict(name='Vortag'), row=1, col=4)
                except:
                    pass
                fig.update_layout(font_family="Montserrat",font_color="#0F2B63",title_font_family="Montserrat",title_font_color="#0F2B63")

                
                
            fig = px.bar(df, x="SapOrderNumber", y="Bearbeitungszeit",color='SapOrderNumber',barmode=sel_barmodeP,facet_col=unterteilen, title="Bearbeitungszeit nach Depot", color_discrete_sequence=px.colors.qualitative.Dark24)
            st.plotly_chart(fig, use_container_width=True)
            
            
            
            if tabelle == True:
                st.dataframe(df_grouped)

        def figBearbeitungsdauerKunden(df,dflt22, tabelle,sel_barmodeP,unterteilen):
        
            col1, col2 = st.columns(2)
            with col1:    
                sel_stunde_minute = st.selectbox('Zeiteinheit',['in Minuten', 'in Stunden'],key='stundeinBearbeitungs')            #create px Area Chart by PlannedDate and Bearbeitungszeit
                # rename PickDauer in Bearbeitungszeit
                df = df.rename(columns={'PickDauer':'Bearbeitungszeit'})
            with col2:
                pass

            #sort by Bearbeitungszeit
            df = df.sort_values(by=['Bearbeitungszeit'], ascending=[False])
            if sel_stunde_minute == 'in Stunden':
                df['Bearbeitungszeit'] = df['Bearbeitungszeit']/60
      #      df_grouped = df.groupby(["PlannedDate"])["Bearbeitungszeit"].sum().reset_index()     
            #df_grouped = df_grouped.sort_values(by=['PlannedDate','DeliveryDepot'], ascending=[False,False])
            if unterteilen == None:
                fig = px.treemap(df, path=['PartnerName'], values='Bearbeitungszeit')
                fig.update_layout(font_family="Montserrat",font_color="#0F2B63",title_font_family="Montserrat",title_font_color="#0F2B63",title_text='Bearbeitungszeit pro Kunde Gesamt')
            else:
                fig = px.treemap(df, path=['DeliveryDepot', 'PartnerName'], values='Bearbeitungszeit')
                fig.update_layout(font_family="Montserrat",font_color="#0F2B63",title_font_family="Montserrat",title_font_color="#0F2B63",title_text='Bearbeitungszeit pro Kunde und Depot')

            #fig.update_traces(root_color="lightgrey")
            fig.update_layout(margin = dict(t=50, l=25, r=25, b=25))
            fig.update_layout(font_family="Montserrat",font_color="#0F2B63",title_font_family="Montserrat",title_font_color="#0F2B63",title_text='Bearbeitungszeit pro Kunde')
            #fig.show()
            st.plotly_chart(fig, use_container_width=True)

        def figPick(df,dflt22, tabelle,sel_barmodeP,unterteilen):
            pass
            #group by Planned Date and PickDauer

        with st.expander('Warehouse', expanded=True):
            col1, col2 = st.columns(2)
            #form selectbox
            with col1:
                sel_NachDepotP = st.selectbox('Gliederung', ['Alle Depots zusammen','Depot unterteilt'],key='1NachDepotP')
                sel_tabelleP = st.checkbox('Tabelle Anzeigen:', value=False, key='1tableP')
                if sel_tabelleP == True:
                    tabelle = True
            with col2:
                sel_Auswertungstyp = st.selectbox('Auswertung:', ['Bearbeitungszeit pro Kunde','Bearbeitungszeit pro LS','Studeneinsatz','Picks gegen Bedarf'],key='1GesamtOderNachDepotP')
                if st.checkbox('Gestapelt', value=True, key='1GestapeltP'):
                    sel_barmodeP = 'stack'
                else:
                    sel_barmodeP = 'group'
            # unterteilen ja nein       
            if sel_NachDepotP == 'Depot unterteilt':
                    unterteilen = 'DeliveryDepot'
            if sel_NachDepotP == 'Alle Depots zusammen':
                    unterteilen = None
            if sel_Auswertungstyp == 'Bearbeitungszeit pro LS':
                figBearbeitungsdauerLS(df,dflt22,sel_tabelleP,sel_barmodeP,unterteilen)
            if sel_Auswertungstyp == 'Bearbeitungszeit pro Kunde':
                figBearbeitungsdauerKunden(df,dflt22,sel_tabelleP,sel_barmodeP,unterteilen)
            if sel_Auswertungstyp == 'Picks gegen Bedarf':
                pass
                

            
            #figSAPpicks(dflt22,dfOrder)
    

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
    df = pd.read_parquet('Data/appData/dfOrAnalyse_Page.parquet')
    pd.set_option("display.precision", 2)   
    img_strip = Image.open('Data/img/strip.png')   
    img_strip = img_strip.resize((1000, 15))     
    st.title('SuperDepot Datenanalyse')
    st.image(img_strip, use_column_width=True, caption='',)     
    depot = st.multiselect('Depot', ['Stuttgart','Hannover','Bielefeld','Hamburg','Leipzig'], ['Stuttgart' ,'Leipzig'])
    df = df[df['DeliveryDepot'].isin(depot)]

    df, dfLT22 = dateFilterdfOr(df,dfLT22)
   
    expanderFigGesamtPicks(df,dfLT22)
    expanderPicksLager(df,dfLT22)

    sel_reload = st.button('Reload Data',key='reloadAnalyse')
    if sel_reload == True:
        dfOr = sql.sql_datenTabelleLaden('prod_Kundenbestellungen')
        dfHannover = pd.read_parquet('Data/appData/dfDe55.parquet')
        dfLT22 = pd.read_parquet('Data/upload/lt22.parquet')        
        df = berechneAlleDepots(dfOr, dfHannover)
        df = berechne_dfOr_Pickdauer(df,dfLT22)
        #df to parquet
        df.to_parquet('Data/appData/dfOrAnalyse_Page.parquet')
        st.success('Data reloaded')
    #expanderTruckAuslastung(df)
    st.dataframe(df)
      

