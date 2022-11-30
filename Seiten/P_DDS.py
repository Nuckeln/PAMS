import base64
import streamlit as st
import pandas as pd
import numpy as np
import extract_msg
from streamlit_option_menu import option_menu
import os
from data_Class.SQL import datenLadenFehlverladungen , datenSpeichernFehlverladungen
import datetime
import plotly.express as px

class DDS:
    day1 = datetime.date.today()
    day2 = day1 - datetime.timedelta(days=30)

    def __init__(self,df):
        self.df = df

def ddsSQL():
    df = pd.read_excel('data/dds.xlsx')
    return df
def menueLaden():
    selected2 = option_menu(None, ["Dashboard", "DDS Tag Erfassen",'DDS Bearbeiten'],
    icons=['house', 'cloud-upload', "list-task"], 
    menu_icon="cast", default_index=0, orientation="horizontal")
    return selected2   



def FilterNachDatum(day1, day2,df):
    df['Date'] = df['Date'].dt.strftime('%m/%d/%y')
    df['Date'] = df['Date'].astype('datetime64[ns]').dt.date

    mask = (df['Date'] >= day1) & (df['Date'] <= day2)         
    df = df.loc[mask]
    return df

def ddsDashboard(df):

    col1, col2 = st.columns(2)
    with col1:
        startdate = st.date_input('Startdatum', DDS.day2)
    with col2:
        enddate = st.date_input('Enddatum', DDS.day1)
    df = FilterNachDatum(startdate, enddate,df)

    def fig_Bar_Chart(df, spaltenName):
        a = df[spaltenName].mean()
        df = df.groupby(['Date'])[spaltenName].mean().reset_index()
        # add plotly bar chart with a as middelline 
        fig = px.bar(df, x='Date', y=df[spaltenName], title=spaltenName)
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

    col3, col4 = st.columns(2)
    with col3:
        fig_Bar_Chart(df, 'Amount of picks')
    with col4:
        fig_Bar_Chart(df, 'Amount of picks for next Day')

    userBauDirDiagramm(df)
    st.dataframe(df)
        
def ddsTagErfassen(df):

    with st.form(key='my_form'):
        col1, col2 = st.columns(2)
        with col1:
            date = st.date_input('Datum', DDS.day1)
        with col2:
            amountOfPicks = st.number_input('Anzahl Picks', min_value=0, max_value=1000, value=0, step=1)




def ddsPage():
    df = ddsSQL()
    selMenue = menueLaden()
    if selMenue == 'Dashboard':
        ddsDashboard(df)
    elif selMenue == 'DDS Tag Erfassen':
        ddsTagErfassen(df)



















