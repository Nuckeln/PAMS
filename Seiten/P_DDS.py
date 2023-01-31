
import pytz
import streamlit as st
import pandas as pd
import numpy as np
from streamlit_option_menu import option_menu
import datetime
import plotly.express as px
import pyarrow.parquet as pq
from Data_Class.SQL import SQL_TabellenLadenBearbeiten as sql

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

def fig_PicksPerDay(df):
    df = df.groupby(['Tag']).agg({'Picks Gesamt': 'sum'}).reset_index()
    fig = px.bar(df, x='Tag', y='Picks Gesamt', title='Picks pro Tag')
    st.plotly_chart(fig)
    return fig
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
    fig = px.bar(dfFertig, x='Fertiggestellt', y="Picks Gesamt", color="InTime", hover_data=['PartnerName','Fertig um','SapOrderNumber','DeliveryDepot'])
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
    st.plotly_chart(fig, use_container_width=True,height=800)


def ddsPage():
    dfLT22 = pd.read_parquet('Data/upload/lt22.parquet')
    dfOr = sql.sql_datenTabelleLaden('prod_Kundenbestellungen')
    #dfHannover = pd.read_parquet('Data/upload/hannover.parquet')
    pd.set_option("display.precision", 2)
    


    selMenue = menueLaden()     
    if selMenue == 'Dashboard':
        dfOr = dateFilter(dfOr)
        fig_PicksPerDay(dfOr)
        figUebermitteltInDeadline(dfOr)
        st.dataframe(dfOr)

    elif selMenue == 'DDS Tag Erfassen':
        st.write('DDS Tag Erfassen')