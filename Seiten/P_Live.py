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

    ## Filter für Live AllSSCCLabelsPrinted Func ###
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

    def columnsKennzahlen(df):
        col1, col2, col3 = st.columns(3)
        with col1:
            #---GesamtPicks---#
            st.subheader("Gesamt Picks Tag")
            pickges = df['Picks Gesamt'].sum()
            pickges = int(pickges)
            st.write(f"Gesamtvolumen:  {pickges}")
            #---PicksSTR---#
            picksSTR = df.loc[df['DeliveryDepot']=='KNSTR']
            picksSTR = picksSTR['Picks Gesamt'].sum()
            picksSTR = int(picksSTR)
            st.write(f"Stuttgart:  {picksSTR}")
            #---PicksLEJ---#
            picksLEJ = df.loc[df['DeliveryDepot']=='KNLEJ']
            picksLEJ = picksLEJ['Picks Gesamt'].sum()
            picksLEJ = int(picksLEJ)
            st.write(f"Leipzig:  {picksLEJ}")
            #---Lieferscheine---#            
            lieferscheine = df['SapOrderNumber'].nunique()
            st.write(f"Lieferscheine:  {lieferscheine}")

        with col2:
            st.subheader("Noch zu Picken")
            #---PicksOffen---#
            pickOffenges = df.loc[df['AllSSCCLabelsPrinted']==0]
            pickOffenges = pickOffenges['Picks Gesamt'].sum()
            pickOffenges = int(pickOffenges)
            st.write(f"Gesamtvolumen:  {pickOffenges}")
            #---PicksOffenSTR---#
            picksoffenSTR = df.loc[(df['AllSSCCLabelsPrinted']==0) & (df['DeliveryDepot']=='KNSTR')]
            picksoffenSTR = picksoffenSTR['Picks Gesamt'].sum()
            picksoffenSTR = int(picksoffenSTR)
            st.write(f"Stuttgart:  {picksoffenSTR}")
            #---PicksOffenLEJ---#
            picksoffenLEJ = df.loc[(df['AllSSCCLabelsPrinted']==0) & (df['DeliveryDepot']=='KNLEJ')]
            picksoffenLEJ = picksoffenLEJ['Picks Gesamt'].sum()
            picksoffenLEJ = int(picksoffenLEJ)
            st.write(f"Leipzig:  {picksoffenLEJ}")
            #---LieferscheineOffen---#
            lieferscheineOffen = df.loc[df['AllSSCCLabelsPrinted']==0]
            lieferscheineOffen = lieferscheineOffen['SapOrderNumber'].nunique()
            st.write(f"Lieferscheine:  {lieferscheineOffen}")
        with col3:
            st.subheader("Fertig")
            #---PicksFertig---#
            pickFertigges = df.loc[df['AllSSCCLabelsPrinted']==1]
            pickFertigges = pickFertigges['Picks Gesamt'].sum()
            pickFertigges = int(pickFertigges)
            st.write(f"Gesamtvolumen:  {pickFertigges}")
            #---PicksFertigSTR---#
            picksFertigSTR = df.loc[(df['AllSSCCLabelsPrinted']==1) & (df['DeliveryDepot']=='KNSTR')]
            picksFertigSTR = picksFertigSTR['Picks Gesamt'].sum()
            picksFertigSTR = int(picksFertigSTR)
            st.write(f"Stuttgart:  {picksFertigSTR}")
            #---PicksFertigLEJ---#
            picksFertigLEJ = df.loc[(df['AllSSCCLabelsPrinted']==1) & (df['DeliveryDepot']=='KNLEJ')]
            picksFertigLEJ = picksFertigLEJ['Picks Gesamt'].sum()
            picksFertigLEJ = int(picksFertigLEJ)
            st.write(f"Leipzig:  {picksFertigLEJ}")
            #---LieferscheineFertig---#
            lieferscheineFertig = df.loc[df['AllSSCCLabelsPrinted']==1]
            lieferscheineFertig = lieferscheineFertig['SapOrderNumber'].nunique()
            st.write(f"Lieferscheine:  {lieferscheineFertig}")

    def figPickStatusNachDepot(df):
        df = df.groupby(['DeliveryDepot','AllSSCCLabelsPrinted']).agg({'Picks Gesamt':'sum'}).reset_index()
        df['AllSSCCLabelsPrinted'] = df['AllSSCCLabelsPrinted'].replace({0:'Offen',1:'Fertig'})
        fig = px.bar(df, x="DeliveryDepot", y="Picks Gesamt", color="AllSSCCLabelsPrinted", barmode="group")
        fig.update_layout(
            title="Picks Status nach Depot",
            xaxis_title="Depot",
            yaxis_title="Picks Gesamt",
            font=dict(
                family="Courier New, monospace",
                size=18,
                color="#7f7f7f"
            )
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # fig = px.pie(df, names='PicksOffen', title='PickStatus')
        # st.plotly_chart(fig)




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
    def userBauDirDiagramm(df):
        userAuswahl = ['Amount of DNs',	'DESADV','Amount of picks',	'Amount of picks for next Day'	,'Volume available for next Day in %' ,'Amount transmissions w/o TPD' ,'Operational activities completed',]
        spaltenName = st.selectbox('Spalte', userAuswahl)
        fig_Bar_Chart(df, spaltenName)     
    

    
    headerAndWetter()

    seldate= st.date_input('Datum')
    if seldate:
        df = FilterNachDatum(seldate,seldate,df)
        df = df.fillna(0)

    pd.set_option("display.precision", 2)
    columnsKennzahlen(df)
    figPickStatusNachDepot(df)

    st.dataframe(df)




