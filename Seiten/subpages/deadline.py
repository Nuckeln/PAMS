import streamlit as st
import pandas as pd
import numpy as np
import datetime
import streamlit_autorefresh as sar
from PIL import Image
import plotly_express as px
from annotated_text import annotated_text, annotation
import streamlit_timeline as timeline

from Data_Class.wetter.api import getWetterBayreuth
from Data_Class.MMSQL_connection import read_Table

import matplotlib.pyplot as plt
from matplotlib.patches import Arc

import plotly.graph_objects as go








def figUebermitteltInDeadline(df):      
    with st.container():
        col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
        with col1:  
            
            sel_deadStr = st.time_input('Stuttgart', datetime.time(14, 0))
        with col2:
            sel_deadLej = st.time_input('Leipzig', datetime.time(14, 0))
        with col3:    
            sel_deadHan = st.time_input('Hannover', datetime.time(14, 0))
        with col4:
            sel_deadBiel = st.time_input('Bielefeld', datetime.time(14, 0))
    
    
    #add deadlines to df by DeliveryDepot
    df.loc[df['DeliveryDepot'] == 'KNSTR', 'Deadline'] = sel_deadStr
    df.loc[df['DeliveryDepot'] == 'KNLEJ', 'Deadline'] = sel_deadLej
    df.loc[df['DeliveryDepot'] == 'KNHAJ', 'Deadline'] = sel_deadHan
    df.loc[df['DeliveryDepot'] == 'KNBFE', 'Deadline'] = sel_deadBiel
    
    
    # Zeige nur übermittelte Aufträge an
    df['Status'] == 'SSCCInformationSent', True, False
    df['Deadline'] = df['Deadline'].astype(str)
    df['PlannedDate'] = df['PlannedDate'] + pd.to_timedelta(df['Deadline']) 
    #convert to datetime
    df['PlannedDate'] = pd.to_datetime(df['PlannedDate'])
    # filter by fertiggestellt = '0'
    dfFertig = df[df['Fertiggestellt'] != '0']
    dfFertig['Fertiggestellt'] = pd.to_datetime(dfFertig['Fertiggestellt'], format='%Y-%m-%d %H:%M:%S')
    #add two hours to Feritggestellt
    dfFertig['Fertiggestellt'] = dfFertig['Fertiggestellt'].dt.tz_localize(None)
    # Prüfe in dfFertig['InTime'] ob der Zeitstempel von Fertiggestellt vor dem Zeitstempel von Deadline liegt
    dfFertig['InTime'] = dfFertig['Fertiggestellt'] <= dfFertig['PlannedDate']
    # Füge eine neue Spalte hinzu, um die Zeit zu runden
    dfFertig['Fertig um'] = dfFertig['Fertiggestellt']
    dfFertig['Fertig um'] = dfFertig['Fertig um'].dt.strftime('%d.%m.%Y %H:%M')
    #rename Feritggestellt to Gerundeter
    dfFertig['Fertiggestellt'] = dfFertig['Fertiggestellt'].dt.round('H')
    #change format to day as text and hour
    dfFertig['Fertiggestellt'] = dfFertig['Fertiggestellt'].dt.strftime('%d.%m.%Y %H:%M')
    #group by
    dfFertig = dfFertig.groupby(['PlannedDate','PartnerName','Fertiggestellt','SapOrderNumber','DeliveryDepot','InTime','Fertig um']).agg({'Picks Gesamt':'sum'}).reset_index()
    #sort by Fertiggestellt
    dfFertig = dfFertig.sort_values(by=['Fertiggestellt'], ascending=True)
    #Create Plotly Chart
    title = "<b>Lieferschein in Deadline Fertiggestellt  </b> <span style='color:#4FAF46'>ja</span> / <span style='color:#E72482'>nein</span>"

    fig = px.bar(dfFertig, x='Fertiggestellt', y="Picks Gesamt", color="InTime", 
                    hover_data=['PlannedDate','PartnerName','Fertig um','SapOrderNumber','DeliveryDepot'],
                    height=600, title=title, 
                    color_discrete_map={True: '#4FAF46', False: '#E72482'})
    
    fig.data[0].text = dfFertig['PartnerName'] + '<br>' + dfFertig['Picks Gesamt'].astype(str)
    fig.layout.xaxis.type = 'category'
    # x aaxis text horizontal
    fig.layout.xaxis.tickangle = 70
    # remove xaxis and yaxis title
    fig.update_layout(font_family="Montserrat",font_color="#0F2B63",title_font_family="Montserrat",title_font_color="#0F2B63")
    fig.update_layout(showlegend=False)
    fig.update_traces(text=dfFertig['PartnerName'], textposition='inside')
    st.plotly_chart(fig, use_container_width=True,config={'displayModeBar': False})




def main():
    st.title("Deadline")
    st.markdown("Hier können Sie die Deadline für die einzelnen Depots festlegen. Die Deadline ist die Zeit, zu der die Lieferscheine an die Depots übermittelt werden müssen.")
    #read data from SQL
    # df = read_Table('KNAPP_DEMO')
    # #call function
    # figUebermitteltInDeadline(df)