
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

def menueLaden():
    selected2 = option_menu(None, ["Dashboard", "DDS Tag Erfassen",'DDS Bearbeiten'],
    icons=['house', 'cloud-upload', "list-task"], 
    menu_icon="cast", default_index=0, orientation="horizontal")
    return selected2   
def dateFilter(df):
    df['PlannedDate'] = df['PlannedDate'].astype(str)
    df['PlannedDate'] = pd.to_datetime(df['PlannedDate'].str[:10])
    df['Tag'] = df['PlannedDate'].dt.strftime('%d.%m.%Y')
   # df tag to datetime.date
    df['Tag'] = pd.to_datetime(df['Tag'])
    df['Woche'] = df['PlannedDate'].dt.strftime('%U')
    df['Monat'] = df['PlannedDate'].dt.strftime('%m.%Y')

    col1, col2 = st.columns(2)

    with col1:
        sel_datePicker = st.selectbox('Select', ['Tage', 'Wochen', 'Monate'])
    with col2:
        if sel_datePicker == 'Tage':
            end_date = datetime.date.today()
            start_date = end_date - datetime.timedelta(days=10)
            format = "DD.MM.YYYY"
            sel_dateRange = st.slider('Select date', min_value=start_date, value=(start_date, end_date), max_value=end_date, format=format)
            df = df[(df['Tag'] >= np.datetime64(sel_dateRange[0])) & (df['Tag'] <= np.datetime64(sel_dateRange[1]))]

        # elif sel_datePicker == 'Wochen':
        #     end_week = datetime.date.today().isocalendar()[1]
        #     end_week = str(end_week)
        #     start_week = "1"
        #     sel_weekRange = st.slider('Select week', min_value=start_week, value=(start_week, end_week), max_value=end_week)
        #     df = df[(df['Woche'] >= sel_weekRange[0]) & (df['Woche'] <= sel_weekRange[1])]

        # elif sel_datePicker == 'Monate':
        #     end_month = datetime.date.today().strftime('%m.%Y')
        #     start_month = (datetime.date.today() - datetime.timedelta(days=365)).strftime('%m.%Y')
        #     sel_monthRange = st.slider('Select month', min_value=start_month, value=(start_month, end_month), max_value=end_month)
        #     df = df[(df['Monat'] >= sel_monthRange[0]) & (df['Monat'] <= sel_monthRange[1])]

    return df

def berechneAlleDepots(dfOr, dfHannover):
    #to string dfHannover = dfHannover['Delivery'] 
    dfHannover['Delivery'] = dfHannover['Delivery'].astype(str)
    #dfHannover group by Delivery and Date
    dfHannover = dfHannover.groupby(['Picking Date','Delivery','Name of the ship-to party','TSP']).agg({'Picks Gesamt':'sum','Picks CS':'sum','Picks PAL':'sum','Picks OUT':'sum'}).reset_index()
    #rename dfHannover Delivery to SapOrderNumber, Picking Date to PlannedDate, Name of the ship-to party to PartnerName, TSP to DeliveryDepot, Picks CS to Picks Karton, Picks OUT to Picks Stangen, Picks PAL to Picks Paletten
    dfHannover = dfHannover.rename(columns={'Delivery':'SapOrderNumber','Picking Date':'PlannedDate', 'Name of the ship-to party':'PartnerName', 'TSP':'DeliveryDepot', 'Picks CS':'Picks Karton', 'Picks OUT':'Picks Stangen', 'Picks PAL':'Picks Paletten'})
    #concat rows with same column names to df
    df = pd.concat([dfOr, dfHannover], ignore_index=True)
    #if in Delivery Depot  'Bielefeld': 'Bielefeld',   'DE54 - KN Hamburg': 'Hamburg','DE59 - KN Stuttgart': 'Stuttgart', 'HAJ - KN Hannover': 'Hannover','KNBFE': 'Bielefeld', 'KNLEJ': 'Leipzig','KNSTR': 'Stuttgart','Unbekannt': 'Hannover'
    df['DeliveryDepot'] = df['DeliveryDepot'].replace({'Bielefeld': 'Bielefeld',   'DE54 - KN Hamburg': 'Hamburg','DE59 - KN Stuttgart': 'Stuttgart', 'HAJ - KN Hannover': 'Hannover','KNBFE': 'Bielefeld', 'KNLEJ': 'Leipzig','KNSTR': 'Stuttgart','Unbekannt': 'Hannover'})
    # Filter by Depot
    depot = st.multiselect('Depot', ['Stuttgart','Hannover','Bielefeld','Hamburg','Leipzig'], ['Stuttgart','Hannover','Bielefeld','Hamburg','Leipzig'])
    df = df[df['DeliveryDepot'].isin(depot)]
    return df

def expanderFigGesamtPicks(df):

        def figPicksGesamtKunden(df,unterteilen,tabelle):
            if st.checkbox('Gestapelt', value=True):
                sel_barmode = 'stack'
            else:
                sel_barmode = 'group'
            
            #df PlannedDate to dd:mm:yyyy
            df['PlannedDate'] = pd.to_datetime(df['PlannedDate'])
            #i as double  = sum of Picks Gesamt by PlannedDate
            i = df.groupby('PlannedDate')['Picks Gesamt'].sum()
            fig = px.bar(df, x="PlannedDate", y="Picks Gesamt", color="PartnerName", barmode=sel_barmode, facet_col=unterteilen,hover_data=["Picks Gesamt","DeliveryDepot","PlannedDate","Lieferschein erhalten"])
            # drop empty ticks on x
            fig.layout.xaxis.type = 'category'
            fig.layout.xaxis.tickangle = 70
            

            fig.update_layout(showlegend=False)
            fig.update_layout(font_family="Montserrat",font_color="#0F2B63",title_font_family="Montserrat",title_font_color="#0F2B63")
            st.plotly_chart(fig, use_container_width=True)



            if tabelle == True:
                st.dataframe(df)

        def figPicksGesamtnachTagUndVerfügbarkeit(df,unterteilen,tabelle):
            
            # Convert 'PlannedDate' to datetime format
            df['PlannedDate'] = pd.to_datetime(df['PlannedDate'], format='%Y-%m-%d %H:%M:%S.%f')
            df['Lieferschein erhalten'] = pd.to_datetime(df['Lieferschein erhalten'], format='%Y-%m-%d %H:%M:%S.%f')

            # Fill missing values in 'Lieferschein erhalten' with values from 'PlannedDate'
            df['Lieferschein erhalten'] = df['Lieferschein erhalten'].fillna(df['PlannedDate'])
            # Convert 'Lieferschein erhalten' to datetime format
            df['Lieferschein erhalten'] = pd.to_datetime(df['Lieferschein erhalten'], format='%Y-%m-%d %H:%M:%S.%f')
            # Round the datetime values in 'Lieferschein erhalten' to nearest hour
            df['Lieferschein erhalten'] = df['Lieferschein erhalten'].dt.round('H')
            

            # Sort the dataframe by 'PlannedDate'
            df.sort_values("PlannedDate", inplace=True)
            # if 'Lieferschein erhalten' is lower than 'PlannedDate' then add to Verfügbarkeit 'Vortag', else add to 'Verladetag'
            df.loc[df['Lieferschein erhalten'] < df['PlannedDate'], 'Verfügbarkeit'] = 'Vortag'
            df.loc[df['Lieferschein erhalten'] >= df['PlannedDate'], 'Verfügbarkeit'] = 'Verladetag'

            # Group the dataframe by 'PlannedDate' and 'Lieferschein erhalten'
            df_grouped = df.groupby(["PlannedDate", "Verfügbarkeit","DeliveryDepot",'Lieferschein erhalten'])["Picks Gesamt"].sum().reset_index()
            #change PlannedDate to dd:mm:yyyy
            #df_grouped['PlannedDate'] = df_grouped['PlannedDate'].dt.strdate('%d.%m.%Y')
            # Create a bar chart of 'Picks Gesamt' grouped by delivery Depot and stacked by sum Vortag and Verladetag
            fig = px.bar(df_grouped, x="PlannedDate", y="Picks Gesamt", color="Verfügbarkeit", barmode="stack", facet_col=unterteilen,hover_data=["Picks Gesamt","DeliveryDepot","PlannedDate","Lieferschein erhalten"])
            fig.update_layout(showlegend=False)
            fig.update_layout(font_family="Montserrat",font_color="#0F2B63",title_font_family="Montserrat",title_font_color="#0F2B63")
            #remove timespamp from xaxis
            fig.update_xaxes(tickformat='%d.%m.%Y')
            st.plotly_chart(fig, use_container_width=True)
            if tabelle == True:
                st.dataframe(df_grouped)
        
    
        with st.expander('PickVolumen Nach:'):

            col1, col2, col3 = st.columns(3)
            #form selectbox
            with col1:
                sel_NachDepot = st.selectbox('Gliederung nach:', ['Depot','Gesamtvolumen'])
            with col2:
                sel_GesamtOderNachDepot = st.selectbox('Unterteilt in:', ['Kunden','Verfügbarkeit'])
            with col3:
                 sel_tabelle = st.checkbox('Tabelle Anzeigen:', value=False)
            # unterteilen ja nein       
            if sel_NachDepot == 'Depot':
                    unterteilen = 'DeliveryDepot'
            if sel_NachDepot == 'Gesamtvolumen':
                    unterteilen = None
            #wich SumOf
            if sel_GesamtOderNachDepot == 'Kunden':
                figPicksGesamtKunden(df,unterteilen,sel_tabelle)
            if sel_GesamtOderNachDepot == 'Verfügbarkeit':
                figPicksGesamtnachTagUndVerfügbarkeit(df,unterteilen,sel_tabelle)
            
def expanderTruckAuslastung(df):
        def figPalTruckAuslastung(df):
            # Create a bar chart of 'Picks Gesamt' grouped by delivery Depot and stacked by sum Vortag and Verladetag
            fig = px.bar(df, x="PlannedDate", y="Picks Gesamt", color="Truck Kennzeichen", barmode="stack", facet_col="DeliveryDepot",hover_data=["Picks Gesamt","DeliveryDepot","PlannedDate","Lieferschein erhalten"])
            fig.update_layout(showlegend=False)
            fig.update_layout(font_family="Montserrat",font_color="#0F2B63",title_font_family="Montserrat",title_font_color="#0F2B63")
            #remove timespamp from xaxis
            fig.update_xaxes(tickformat='%d.%m.%Y')
            st.plotly_chart(fig, use_container_width=True)
            #st.dataframe(df)
        with st.expander('Truck Auslastung'):
            figPalTruckAuslastung(df)

def ddsPage():
    dfLT22 = pd.read_parquet('Data/upload/lt22.parquet')
    dfOr = sql.sql_datenTabelleLaden('prod_Kundenbestellungen')
    dfHannover = pd.read_parquet('Data/appData/dfDe55.parquet')
    pd.set_option("display.precision", 2)
    

    selMenue = menueLaden()     
    if selMenue == 'Dashboard':
        
        df = berechneAlleDepots(dfOr, dfHannover)
        df = dateFilter(df)
        expanderTruckAuslastung(df)
        expanderFigGesamtPicks(df)
        st.dataframe(df)

        

    elif selMenue == 'DDS Tag Erfassen':
        st.write('DDS Tag Erfassen')