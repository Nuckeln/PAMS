import streamlit as st
import pandas as pd
import numpy as np
import datetime
#from Data_Class.SQL import sql_datenLadenLabel,sql_datenLadenOderItems,sql_datenLadenStammdaten,sql_datenLadenOder
from Data_Class.DB_Daten_Agg import orderDatenAgg
from Data_Class.wetter.api import getWetterBayreuth
import plotly_express as px

class LIVE:
    
    heute  = datetime.date.today()
    morgen =heute + datetime.timedelta(days=1)
    def __init__(self,df):
        self.df = df


    def sessionstate():
        if 'key' not in st.session_state:
            st.session_state['key'] = 'value'
        if 'key' not in st.session_state:
            st.session_state.key = +1
    def wetter():
        df = getWetterBayreuth()
        temp = df.loc[0,'Temp']
        temp_max = df.loc[0,'Temp Max']
        temp_min = df.loc[0,'Temp Min']
        humidity = df.loc[0,'Humidity']
        wind_speed = df.loc[0,'Wind Speed']
        wind_degree = df.loc[0,'Wind Degree']
        clouds = df.loc[0,'Clouds']
        weather = df.loc[0,'Weather']
        #temp to int
        temp = int(temp)
        st.write(f"Temperatur: {temp}" + "°C")
        if weather == "Clouds":
            st.write("Wolkig")
        elif weather == "Rain":
            st.write("Regen")
        elif weather == "Clear":
            st.write("Klar")
        elif weather == "Snow":
            st.write("Schnee")
        else:
            st.write("Sonstiges")

def liveStatusPage(df,dfL):

    ## Filter für Live Status Func ###
    def FilterNachDatum(day1, day2,df):
        #df['PlannedDate'] = df['PlannedDate'].dt.strftime('%m/%d/%y')
        df['PlannedDate'] = df['PlannedDate'].astype('datetime64[ns]').dt.date
        #filter nach Datum
        df = df[(df['PlannedDate'] >= day1) & (df['PlannedDate'] <= day2)]
        #mask = (df['PlannedDate'] >= day1) & (df['PlannedDate'] <= day2)         
        #df = df.loc[mask]
        return df

    def FilterNachDatumLabel(day1, day2,df):
        # df['DATUM'] = df['DATUM'].dt.strftime('%m/%d/%y')
        # df['DATUM'] = df['DATUM'].astype('datetime64[ns]').dt.date
        #filter nach Datum
        df = df[(df['DATUM'] >= day1) & (df['DATUM'] <= day2)]


        return df

    ## Page Layout Func ### 
    def headerAndWetter():
        colhead1, colhead2 ,colhead3, = st.columns(3)
        with colhead1:
            st.title("Live Status")
        with colhead2:
            st.header("")
        with colhead3:
            LIVE.wetter()

    def columnsKennzahlen(df,dfL,dfapicksDepot,dfapicksOffen,dfapicksFertig):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.subheader("Gesamt Picks Tag")
            #dfapicksDepot = df.groupby(['DeliveryDepot'],dropna =False)['Picks Gesamt'].sum().reset_index()
            pickges = dfapicksDepot['Picks Gesamt'].sum()
            st.write(f"Gesamtvolumen:  {pickges}")
            #---##---#
            dfapicksDepotKNSTR = dfapicksDepot.loc[dfapicksDepot['DeliveryDepot']=='KNSTR']
            picksStr = dfapicksDepotKNSTR['Picks Gesamt'].sum()
            st.write(f"Stuttgart:  {picksStr}")
            #---##---#
            dfapicksDepotKNLEJ = dfapicksDepot.loc[dfapicksDepot['DeliveryDepot']=='KNLEJ']
            picksLej = dfapicksDepotKNLEJ['Picks Gesamt'].sum()
            st.write(f"Leipzig:  {picksLej}")
        with col2:
            st.subheader("Noch zu Picken")
            pickOffenges = dfapicksOffen['Picks Gesamt'].sum()
            st.write(f"Gesamtvolumen:  {pickOffenges}")
            #---##---#
            dfapicksOffen = dfapicksOffen.loc[dfapicksOffen['DeliveryDepot']=='KNSTR']
            picksoffenStr = dfapicksOffen['Picks Gesamt'].sum()
            st.write(f"Stuttgart:  {picksoffenStr}")
            #---##---#
            dfapicksOffen = dfapicksOffen.loc[dfapicksOffen['DeliveryDepot']=='KNLEJ']
            picksoffenLej = dfapicksOffen['Picks Gesamt'].sum()
            st.write(f"Leipzig:  {picksoffenLej}")            
        with col3:
            st.subheader("Fertig")
            pickFertigges = dfapicksFertig['Picks Gesamt'].sum()
            st.write(f"Gesamtvolumen:  {pickFertigges}")
            #---##---#
            dfapicks = dfapicksFertig.loc[dfapicksFertig['DeliveryDepot']=='KNSTR']
            picksFertigStr = dfapicks['Picks Gesamt'].sum()
            st.write(f"Stuttgart:  {picksFertigStr}")
            #---##---#
            dfapicksh = dfapicksFertig.loc[dfapicksFertig['DeliveryDepot']=='KNLEJ']
            picksFertigLej = dfapicksh['Picks Gesamt'].sum()
            st.write(f"Leipzig:  {picksFertigLej}")

    def fig_Bar_Chart(df, spaltenName):
        a = df[spaltenName].mean()
        df = df.groupby(['PlannedDate'])[spaltenName].mean().reset_index()
        # add plotly bar chart with a as middelline 
        fig = px.bar(df, x='PlannedDate', y=df[spaltenName], title=spaltenName)
        fig.add_hline(y=a, line_dash="dash", line_color="red")
        # if value of spaltenName is higher than a, color the bar in red
        fig.update_traces(marker_color=np.where(df[spaltenName] > a, 'red', 'green'))
        # add total value of spaltenName to each bar
        fig.update_traces(texttemplate='%{text:.2s}', text=df[spaltenName])
        fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')

        st.plotly_chart(fig, use_container_width=True)
    
    def fig_Bar_Chart2(df):
        df = df.groupby(['PlannedDate'])['PicksGesamt', 'PicksOffen', 'PicksFertig'].mean().reset_index()
        # add plotly bar chart with a as middelline 
        fig = px.bar(df, x='PlannedDate', y=['PicksGesamt', 'PicksOffen', 'PicksFertig']) 
        # fig.add_hline(y=a, line_dash="dash", line_color="red")
        # # if value of spaltenName is higher than a, color the bar in red
        # fig.update_traces(marker_color=np.where(df[spaltenName] > a, 'red', 'green'))
        # # add total value of spaltenName to each bar
        # fig.update_traces(texttemplate='%{text:.2s}', text=df[spaltenName])
        # fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')

        st.plotly_chart(fig, use_container_width=True)

    def userBauDirDiagramm(df):
        userAuswahl = ['Amount of DNs',	'DESADV','Amount of picks',	'Amount of picks for next Day'	,'Volume available for next Day in %' ,'Amount transmissions w/o TPD' ,'Operational activities completed',]
        spaltenName = st.selectbox('Spalte', userAuswahl)
        fig_Bar_Chart(df, spaltenName)     
    
    def kundenPicks(df,dfL):
        #dfKunden = df.groupby(['PartnerName', 'SapOrderNumber'],dropna =False)['Picks Gesamt'].sum().reset_index()
        #st.dataframe(dfKunden)
        return 
    
    headerAndWetter()

    seldate= st.date_input('Datum')
    if seldate:
        df = FilterNachDatum(seldate,seldate,df)
        df = df.fillna(0)
        dfapicksDepot = df.groupby(['PlannedDate','DeliveryDepot'],dropna =False)['Picks Gesamt'].sum().reset_index()
        dfOffen = df[df['AllSSCCLabelsPrinted'] == 0]
        dfapicksOffen = dfOffen.groupby(['PlannedDate','DeliveryDepot'],dropna =False)['Picks Gesamt'].sum().reset_index()
        dfaFertig = df[df['AllSSCCLabelsPrinted'] == 1]
        dfapicksFertig = dfaFertig.groupby(['PlannedDate','DeliveryDepot'],dropna =False)['Picks Gesamt'].sum().reset_index()
        #dfL = FilterNachDatumLabel(seldate,seldate,dfL)

    columnsKennzahlen(df,dfL,dfapicksDepot=dfapicksDepot,dfapicksOffen=dfapicksOffen,dfapicksFertig=dfapicksFertig)
    fig_Bar_Chart2(df)
    st.dataframe(df)
    #fig_Bar_Chart(df,'Picks Gesamt')
    kundenPicks(df,dfL)


    #df = df[df['SapOrderNumber'].isin(selLs)]

