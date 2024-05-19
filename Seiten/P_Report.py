# Funktion: Report Page
import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
import plotly.graph_objs as go

from Data_Class.MMSQL_connection import read_Table


''' BAT Colurs
#0e2b63 darkBlue
#004f9f MidBlue
#00b1eb LightBlue
#ef7d00 Orange
#ffbb00 Yellow
#ffaf47 Green
#afca0b lightGreen
#5a328a Purple
#e72582 Pink
'''

##### LOAD AND FILTER DATA #####
BATColurs = ['#0e2b63','#004f9f','#00b1eb','#ef7d00','#ffbb00','#ffaf47','#afca0b','#5a328a','#e72582']
@st.cache_data(show_spinner=False)
def load_data():

    df = read_Table('prod_Kundenbestellungen')
    dfIssues = read_Table('PAMS_SD_Issues')
    return df, dfIssues

def filterDate(df: pd,dfIssues: pd):
    df.PlannedDate = pd.to_datetime(df.PlannedDate)
    df['Packtag'] = df.PlannedDate.dt.strftime('%d.%m.%Y')
    df['Packtag'] = df['Packtag'].astype(str)
    df['Jahr'] = df.PlannedDate.dt.strftime('%Y')
    df['Wochentag'] = df['PlannedDate'].dt.strftime('%A')
    df['Woche'] = df['PlannedDate'].dt.strftime('%V.%Y')
    df['Monat'] = df['PlannedDate'].dt.strftime('%m.%Y')
    df.PlannedDate = df.PlannedDate.dt.strftime('%d.%m.%Y')

    col1, col2, col3 = st.columns(3)

    with col1:
        sel_filter = st.radio(
        "Filtern nach:",
        ["Monat", "Woche", 'Jahr' ],
        key="visibility",
        horizontal=True)       

    with col2:
        if sel_filter == 'Zeitraum':
            start_date = st.date_input('Start Date')
            with col3:
                end_date = st.date_input('End Date')
            df.PlannedDate = pd.to_datetime(df.PlannedDate)

            df = df[(df['PlannedDate'] > start_date) & (df['PlannedDate'] <= end_date)]

        if sel_filter == 'Woche':
            #sort df by Woche
            dfWeek = df['Woche'].unique()
            dfWeek_sorted = sorted(dfWeek, key=lambda x: (x.split('.')[1], x.split('.')[0]), reverse=True)
            sel_weekRange = st.selectbox('Wähle Woche', dfWeek_sorted)
            df = df[df['Woche'] == sel_weekRange]

        if sel_filter == 'Monat':
            #sort df by PlannedDate acciending
            df2 = df.sort_values(by=['PlannedDate'], ascending=False)
            #select unique values in column Monat
            dfMonth = df2['Monat'].unique()
            dfMonth_sorted = sorted(dfMonth, key=lambda x: (x.split('.')[1], x.split('.')[0]), reverse=True)
            sel_monthRange = st.selectbox('Wähle Monat', dfMonth_sorted)
            df = df[df['Monat'] == sel_monthRange]
        if sel_filter == 'Jahr':
            #sort df by PlannedDate acciending
            df2 = df.sort_values(by=['PlannedDate'], ascending=False)
            #select unique values in column Monat
            dfYear = df2['Jahr'].unique()
            dfYear_sorted = sorted(dfYear, key=lambda x: (x.split('.')[1], x.split('.')[0]) if '.' in x else (x, x), reverse=True)
            sel_yearRange = st.selectbox('Wähle Jahr', dfYear_sorted)
            df = df[df['Jahr'] == sel_yearRange]

    #to datetime
    try:
        sel_day_max = df['PlannedDate'].max()
        sel_day_max = datetime.strptime(sel_day_max, '%d.%m.%Y')
        sel_day_min = df['PlannedDate'].min()
        sel_day_min = datetime.strptime(sel_day_min, '%d.%m.%Y')
        dfIssues = dfIssues[(dfIssues['Datum gemeldet'] >= sel_day_min) & (dfIssues['Datum gemeldet'] <= sel_day_max)]
        if sel_filter == 'Woche':
            dfIssues = dfIssues[dfIssues['Datum gemeldet'].dt.strftime('%V.%Y') == sel_weekRange]
            #create new column for week
            dfIssues['Datum gemeldet'] = dfIssues['Datum gemeldet'].dt.strftime('%d.%m.%Y')
        if sel_filter == 'Monat':
            dfIssues = dfIssues[dfIssues['Datum gemeldet'].dt.strftime('%m.%Y') == sel_monthRange]
            #create new column for month
            dfIssues['Datum gemeldet'] = dfIssues['Datum gemeldet'].dt.strftime('%d.%m.%Y')
    except:
        pass
    #to datetime


    # filter dfIssues
    col1, col2 = st.columns(2)
    with col1:
        tabelle = st.checkbox('Tabellen einblenden')
    with col2:
        sel_Day_week = st.radio("Zeige in: ", ["Tagen", "Wochen","Monaten","Jahren"], key="zeigeIn", horizontal=True)
    if sel_Day_week == 'Wochen':
        sel_Day_week = 'Woche'
    if sel_Day_week == 'Tagen':
        sel_Day_week = 'PlannedDate'
    if sel_Day_week == 'Monaten':
        sel_Day_week = 'Monat'
    if sel_Day_week == 'Jahren':
        sel_Day_week = 'Jahr'
    return df, dfIssues, tabelle, sel_Day_week


###CREATE PLOTS###
## Kennzahlen PLOTS
def figPICKS_GesamtVolumen(df,tabelle,show_in_day_Week):
    dfOriginal = df
    df['Picks Gesamt'] = pd.to_numeric(df['Picks Gesamt'], errors='coerce')
    df = df.groupby([show_in_day_Week]).agg({'Picks Gesamt':'sum'}).reset_index()

    fig = px.bar(df, x=show_in_day_Week, y="Picks Gesamt",hover_data=["Picks Gesamt",show_in_day_Week])
    fig.update_traces(marker_color='#0e2b63')
    fig.update_layout(title_text="Picks Gesamt DE30", title_font_size=20, title_font_family="Montserrat", title_font_color="#0F2B63", height=700)
    #add sum of each bar to tex
    fig.update_layout(
        annotations=[
            {"x": x, "y": total * 1.05, "text": str(total), "showarrow": False}
            for x, total in df.groupby(show_in_day_Week, as_index=False).agg({"Picks Gesamt": "sum"}).values])
    #update font to Montserrat
    fig.update_layout(font_family="Montserrat")

    st.plotly_chart(fig,use_container_width=True,config={'displayModeBar': False})

    if tabelle == True:
        st.data_editor(dfOriginal)
    
def figPicksGesamtKunden(df,tabelle,show_in_day_Week):
    dfOriginal = df
    #sort by PlannedDate
    df.sort_values(show_in_day_Week, inplace=False)
    try:
        fig = px.bar(df, x=show_in_day_Week, y="Picks Gesamt", color="PartnerName",hover_data=["Picks Gesamt","DeliveryDepot",show_in_day_Week,"Lieferschein erhalten",'SapOrderNumber'])
    except:
        st.warning('Der Filter liefert keine Ergebnisse')

    fig.update_xaxes(tickformat='%d.%m.%Y')
    fig.update_xaxes(showticklabels=True)

    fig.update_layout(title_text="Picks Gesamt DE30 nach Kunden", title_font_size=20, title_font_family="Montserrat", title_font_color="#0F2B63", height=700)
    #add sum of Picks Gesamt to text
    agg_data = df.groupby(show_in_day_Week, as_index=False).agg({"Picks Gesamt": lambda x: pd.to_numeric(x, errors="coerce").sum()})
    annotations=[
        {"x": x, "y": total * 1.05, "text": str(total), "showarrow": False}
        for x, total in agg_data.values]
    #add sum of each bar to text
    fig.update_layout(
        annotations=annotations)

    st.plotly_chart(fig, use_container_width=True,config={'displayModeBar': False})       
    ## FARBEN
    if tabelle == True:
        st.data_editor(dfOriginal,key='KundenFIG')
        
def figPicksGesamtnachTagUndVerfügbarkeit(df,tabelle,show_in_day_Week):

    df['Lieferschein erhalten'] = df['Lieferschein erhalten'].fillna(df['PlannedDate'])
    df['Lieferschein erhalten'] = pd.to_datetime(df['Lieferschein erhalten'])   
    df['Lieferschein erhalten'] = df['Lieferschein erhalten'].dt.strftime('%d.%m.%Y')

    #df['PlannedDate'] = df['PlannedDate'].dt.strftime('%d.%m.%Y')
    df.loc[df['Lieferschein erhalten'] < df['PlannedDate'], 'Verfügbarkeit'] = 'Vortag'
    df.loc[df['Lieferschein erhalten'] >= df['PlannedDate'], 'Verfügbarkeit'] = 'Verladedatum'
    df['Picks Gesamt'] = pd.to_numeric(df['Picks Gesamt'], errors='coerce')
    dfOr = df 
    df_grouped = df.groupby([show_in_day_Week,'Verfügbarkeit']).agg({'Picks Gesamt': 'sum'}).reset_index()

    # Create a bar chart of 'Picks Gesamt' grouped by delivery Depot and stacked by sum Vortag and Verladedatum
    fig = px.bar(df_grouped, x=show_in_day_Week, y="Picks Gesamt", color="Verfügbarkeit", hover_data=["Picks Gesamt",show_in_day_Week],title="Picks Gesamt DE30 nach Verfügbarkeit Lieferschein")

    fig.update_traces(marker_color='#50af47', selector=dict(name='Vortag'))
    fig.update_traces(marker_color='#ef7d00', selector=dict(name='Verladedatum'))
    fig.update_layout(font_family="Montserrat",font_color="#0F2B63",title_font_family="Montserrat",title_font_color="#0F2B63")

    # add sum of Vortag Picks Gesamt to text and sum of Verladedatum Picks Gesamt to text
    agg_data = df_grouped.groupby(show_in_day_Week, as_index=False).agg({"Picks Gesamt": lambda x: pd.to_numeric(x, errors="coerce").sum()})
    annotations=[
        {"x": x, "y": total * 1.05, "text": str(total), "showarrow": False}
        for x, total in agg_data.values]
    #add sum of each bar to text
    fig.update_layout(
        annotations=annotations)
    colurs = ['#4FAF46', '#4FAF46', '#4FAF46']

    st.plotly_chart(fig, use_container_width=True,config={'displayModeBar': False})

    ## FARBEN
    if tabelle == True:
        st.data_editor(dfOr,key='VerfügbarkeitFIG')

def fig_Picksgesamt_kategorie(df, tabelle, show_in_day_Week):
    df['Picks Karton'] = pd.to_numeric(df['Picks Karton'], errors='coerce')
    df['Picks Stangen'] = pd.to_numeric(df['Picks Stangen'], errors='coerce')
    df['Picks Paletten'] = pd.to_numeric(df['Picks Paletten'], errors='coerce')

    df = df.groupby([show_in_day_Week]).agg({'Picks Karton':'sum', 'Picks Stangen':'sum', 'Picks Paletten':'sum'}).reset_index()
    title = "<b>Picks nach Katergorie: </b> <span style='color:#ef7d00'>Stangen</span> / <span style='color:#0F2B63'>Karton</span> / <span style='color:#4FAF46'>Paletten</span>"

    figPicksBySAPOrder = px.bar(df, y=['Picks Karton','Picks Paletten','Picks Stangen'], title=title,height=600)
    figPicksBySAPOrder.update_traces(marker_color='#0F2B63', selector=dict(name='Picks Karton'))
    figPicksBySAPOrder.update_traces(marker_color='#4FAF46', selector=dict(name='Picks Paletten'))
    figPicksBySAPOrder.update_traces(marker_color='#ef7d00', selector=dict(name='Picks Stangen'))
    figPicksBySAPOrder.update_layout(showlegend=False)
    figPicksBySAPOrder.layout.xaxis.tickangle = 70

    figPicksBySAPOrder.update_layout(font_family="Montserrat",font_color="#0F2B63",title_font_family="Montserrat",title_font_color="#0F2B63")
    figPicksBySAPOrder.update_traces(text=df['Picks Karton'], selector=dict(name='Picks Karton'),textposition='inside')
    figPicksBySAPOrder.update_traces(text=df['Picks Paletten'], selector=dict(name='Picks Paletten'),textposition='inside')
    figPicksBySAPOrder.update_traces(text=df['Picks Stangen'], selector=dict(name='Picks Stangen'),textposition='inside')
    figPicksBySAPOrder.update_yaxes(title_text='')
    # Zeige PlannedDate auf der x-Achse
    figPicksBySAPOrder.update_xaxes(title_text='')
    figPicksBySAPOrder.update_xaxes(tickformat='%d.%m.%Y')
    figPicksBySAPOrder.update_xaxes(showticklabels=True)
    
    # Diagramm und Datentabelle in Streamlit anzeigen
    st.plotly_chart(figPicksBySAPOrder, use_container_width=True,config={'displayModeBar': False})
    if tabelle == True:
         st.dataframe(df)

def auslastung_der_trucks(df, tabelle, show_in_day_Week):
        dfOriginal = df
        dfOriginal.EstimatedNumberOfPallets = dfOriginal.EstimatedNumberOfPallets.astype(float)
        # Filter dfOriginal UnloadingListIdentifier is not none
        dfOriginal = dfOriginal[dfOriginal['UnloadingListIdentifier'].notna()]
        depots = ['KNSTR', 'KNLEJ', 'KNBFE', 'KNHAJ']
        dfOriginal['Gepackte Paletten'] = dfOriginal['Gepackte Paletten'].astype(float)
        df = pd.DataFrame()
        for depot in depots:
            df1 = dfOriginal[dfOriginal['DeliveryDepot'] == depot]
            df1['Gepackte Paletten'] = df1['Gepackte Paletten'].astype(float)
            
            df1 = df1.groupby(['DeliveryDepot', 'PlannedDate']).agg({'UnloadingListIdentifier': 'nunique', 'EstimatedNumberOfPallets': 'sum', 'Gepackte Paletten':'sum'}).reset_index()
            df = pd.concat([df, df1])
        # round values to 0 decimal
        df = df.round(0)
        df = df.rename(columns={'UnloadingListIdentifier': 'Anzahl_Trucks', 'EstimatedNumberOfPallets': 'Anzahl_Paletten_geschätzt'})
        df['Stellplätze'] = (df['Anzahl_Trucks'] * 33)
        df['Auslastung_Steplätze'] = (df['Gepackte Paletten'] / df['Stellplätze']) * 100
        
        # erstllen Lineplot
        fig = px.line(df, x='PlannedDate', y='Auslastung_Steplätze', color='DeliveryDepot', title='Auslastung der Trucks', height=600)
        fig.update_layout(title_font_size=20, title_font_family="Montserrat", title_font_color="#0F2B63", legend_title_font_color="#0F2B63", legend_title_font_family="Montserrat", legend_title_font_size=14, legend_font_size=12, legend_font_family="Montserrat", legend_font_color="#0F2B63", legend_orientation="h")
        fig.update_traces(mode='lines+markers')
        fig.update_xaxes(tickformat='%d.%m.%Y')
        fig.update_xaxes(showticklabels=True)
        fig.update_layout(font_family="Montserrat")
        # Legende unter Überschrift
        fig.update_layout(legend=dict(title='Depots', orientation='h', y=1.1, yanchor='top', x=0.5, xanchor='center'))
        # Füge Text Auslastung_Steplätze zu den Linien hinzu
        for depot in depots:
            fig.add_trace(go.Scatter
            (x=df[df['DeliveryDepot'] == depot]['PlannedDate'],
            y=df[df['DeliveryDepot'] == depot]['Auslastung_Steplätze'],
            mode='text',
            text=df[df['DeliveryDepot'] == depot]['Auslastung_Steplätze'].round(2),
            textposition='top center',
            textfont=dict(family='Montserrat', size=12, color='#0F2B63'),
            showlegend=False))
        
        # Anzeigen des Diagramms
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        if tabelle == True:
            st.data_editor(df)
    
def fig_trucks_Org(df, tabelle, show_in_day_Week):
    dfOriginal = df
    #st.data_editor(df)
    # Filter dfOriginal UnloadingListIdentifier is not none
    dfOriginal = dfOriginal[dfOriginal['UnloadingListIdentifier'].notna()]
    depots = ['KNSTR', 'KNLEJ', 'KNBFE', 'KNHAJ']
    dfOriginal['Gepackte Paletten'] = dfOriginal['Gepackte Paletten'].astype(float)
    df = pd.DataFrame()
    for depot in depots:
        df1 = dfOriginal[dfOriginal['DeliveryDepot'] == depot]
        df1['Picks Gesamt'] = df1['Picks Gesamt'].astype(float)
        df1 = df1.groupby(['DeliveryDepot', 'PlannedDate']).agg({'UnloadingListIdentifier': 'nunique', 'Picks Gesamt': 'sum', 'Gepackte Paletten':'sum'}).reset_index()
        df = pd.concat([df, df1])
    # round values to 0 decimal
    df = df.round(0)

    df = pd.DataFrame(columns=['DeliveryDepot', 'PlannedDate', 'UnloadingListIdentifier', 'Picks Gesamt', 'Gepackte Paletten'])

    for depot in depots:
        df1 = dfOriginal[dfOriginal['DeliveryDepot'] == depot]
        df1['Picks Gesamt'] = df1['Picks Gesamt'].astype(float)
        df1 = df1.groupby(['DeliveryDepot', 'PlannedDate']).agg({'UnloadingListIdentifier': 'nunique', 'Picks Gesamt': 'sum', 'Gepackte Paletten':'sum'}).reset_index()
        df = pd.concat([df, df1])

    # Erstellen der Beschriftungen direkt im DataFrame
    df['label'] = df['DeliveryDepot'] + ": " + df['UnloadingListIdentifier'].astype(str) + " LKW <br>" + df['Picks Gesamt'].astype(str) + " Picks <br>" + df['Gepackte Paletten'].astype(str) + " Paletten"

    # Erstellen des Balkendiagramms mit Beschriftungen
    fig = px.bar(df, x='PlannedDate', y='Picks Gesamt', text='label', color='DeliveryDepot', barmode='group', title='LKW Pro Depot', height=600)


    # Anzeigen des Diagramms
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    if tabelle == True:
        st.dataframe(dfOriginal)
### Fehler PLOTS ###
def figIssuesTotal(dfIssues,show_in_day_Week, show_tables):  
    # Unique values in column 'Art' to array
    dfIssues = dfIssues.groupby(['Datum gemeldet','Art']).size().reset_index(name='Anzahl')
    fig = px.bar(dfIssues, x="Datum gemeldet", y='Anzahl', color="Art", hover_data=["Anzahl","Art","Datum gemeldet"])
    fig.update_xaxes(tickformat='%d.%m.%Y')
    fig.update_xaxes(showticklabels=True)
    fig.update_layout(title_text="Fehler pro Tag", title_font_size=20, title_font_family="Montserrat", title_font_color="#0F2B63", legend_title_font_color="#0F2B63", legend_title_font_family="Montserrat", legend_title_font_size=14, legend_font_size=12, legend_font_family="Montserrat", legend_font_color="#0F2B63", legend_orientation="h", height=700)
    #count sum of each bar
    agg_data = dfIssues.groupby('Datum gemeldet', as_index=False).agg({"Anzahl": lambda x: pd.to_numeric(x, errors="coerce").sum()})
    #add sum of each bar to text
    annotations=[
        {"x": x, "y": total * 1.05, "text": str(total), "showarrow": False}
        for x, total in agg_data.values]
    #show figure
    fig.update_layout(
        annotations=annotations)
    
    BATColurs = ['#0e2b63','#004f9f','#00b1eb','#ef7d00','#ffbb00','#ffaf47','#afca0b','#5a328a','#e72582']
    x = dfIssues.Art.unique()
    y = dfIssues.Anzahl.unique()
    #change color of each bar
    for i in range(len(x)):
        fig.data[i].marker.color = BATColurs[i]



    st.plotly_chart(fig, use_container_width=True)
    if show_tables == True:
        st.dataframe(dfIssues)

def figFehlerVsLieferscheine(dfIssues,df,show_tables,show_in_day_Week):
        dfIssuesOriginal = dfIssues
        df = df.groupby(['PlannedDate']).agg({'SapOrderNumber':'count'}).reset_index()
        dfIssues = dfIssues.groupby(['Datum gemeldet','Art']).size().reset_index(name='Anzahl')
        # Berechne die Summen der Issues und der Orders
        sumOfIssues = dfIssues['Anzahl'].sum()
        sumOfOrders = df['SapOrderNumber'].sum()

        # Erstelle Tortendiagramm für Fehler vs. Lieferscheine
        fig1 = go.Figure(data=[go.Pie(labels=['Fehler', 'Lieferscheine'], values=[sumOfIssues, sumOfOrders], hole=.3)])
        fig1.update_traces(marker_colors=['#ef7d00', '#0e2b63'])
        fig1.update_layout(title_text="Fehler vs. Lieferscheine", title_font_size=20, title_font_family="Montserrat", title_font_color="#0F2B63", height=700)

        # Hinzufügen der Gesamtsumme zu der Überschrift des Diagramms
        fig1.update_layout(annotations=[dict(text=f"LS: {sumOfOrders} \n Fehler: {sumOfIssues}", showarrow=False, font_size=16)], showlegend=False)

        # Erstelle Tortendiagramm für Fehler nach Art
        fig2 = go.Figure(data=[go.Pie(labels=dfIssues.Art, values=dfIssues.Anzahl, hole=.3, textinfo='label+percent', texttemplate='%{label}: %{percent}')])
        fig2.update_traces(marker_colors=BATColurs)
        fig2.update_layout(title_text="Fehler nach Art", title_font_size=20, title_font_family="Montserrat", title_font_color="#0F2B63", height=700)

        # Hinzufügen der Gesamtsumme zu der Überschrift des Diagramms
        fig2.update_layout(annotations=[dict(text=f"Summe Total: {sumOfIssues}", showarrow=False, font_size=16)], showlegend=False)

        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(fig1, use_container_width=True, config={'displayModeBar': False})
        with col2:
            st.plotly_chart(fig2, use_container_width=True, config={'displayModeBar': False})

        if show_tables:
            st.dataframe(dfIssuesOriginal)
    
def figFehlerBarDay(dfIssues,df,show_tables,show_in_day_Week):
    dfIssues = dfIssues.groupby(['Datum gemeldet','Art']).size().reset_index(name='Anzahl')
    fig = px.bar(dfIssues, x="Datum gemeldet", y='Anzahl', color="Art", hover_data=["Anzahl","Art","Datum gemeldet"])
    st.plotly_chart(fig, use_container_width=True)

# BAU DIR WAS
@st.cache_resource
def get_pygwalker(dataframe)-> "StreamlitRenderer":

    # When you need to publish your app to the public, you should set the debug parameter to False to prevent other users from writing to your chart configuration file.
    return StreamlitRenderer(dataframe, spec="./gw_config.json", debug=False)
        
def bau_dir_was():
    
    
    tables = return_table_names()
    sel_Table = st.selectbox('Tabelle',tables)
    df = read_table(sel_Table)

    
    renderer = get_pygwalker(df)
    renderer.explorer()



###Show Page###

def reportPage():
    pd.set_option("display.precision", 2)
    df, dfIssues = load_data()
    df, dfIssues, show_tables, show_in_day_Week = filterDate(df,dfIssues)

    with st.expander("Kennzahlen Mengen", expanded=True):
        sel_filter = st.multiselect(
        "Zeige:",
        ["Picks Gesamt", "Picks nach Kunde", "Picks nach Verfügbarket",'Picks nach Kategorie', 'LKW Pro Depot','Auslastung der Trucks'], ['Picks Gesamt'])  
        if 'Picks Gesamt' in sel_filter:
            figPICKS_GesamtVolumen(df,show_tables,show_in_day_Week)
        if 'Picks nach Kunde' in sel_filter:
            figPicksGesamtKunden(df,show_tables,show_in_day_Week)
        if 'Picks nach Verfügbarket' in sel_filter:
            figPicksGesamtnachTagUndVerfügbarkeit(df,show_tables,show_in_day_Week)
        if 'Picks nach Kategorie' in sel_filter:
            fig_Picksgesamt_kategorie(df,show_tables,show_in_day_Week)
        if 'LKW Pro Depot' in sel_filter:
            fig_trucks_Org(df,show_tables,show_in_day_Week)
        if 'Auslastung der Trucks' in sel_filter:
            auslastung_der_trucks(df,show_tables,show_in_day_Week)
        if sel_filter == []:
            st.warning('Bitte wähle eine Auswertung aus')
    with st.expander("Kennzahlen Fehler", expanded=True):
        sel_filterIssues = st.multiselect(
        "Zeige:",
        ["Fehler vs. Lieferscheine", "Fehler Total nach Art"], ['Fehler vs. Lieferscheine'])  
        if 'Fehler vs. Lieferscheine' in sel_filterIssues:
            figFehlerVsLieferscheine(dfIssues,df,show_tables,show_in_day_Week)
        if 'Fehler Total nach Art' in sel_filterIssues:
            figIssuesTotal(dfIssues,show_in_day_Week,show_tables)
        figFehlerBarDay(dfIssues,df,show_tables,show_in_day_Week)
    # with st.expander("Bau dir was", expanded=True):
    #     bau_dir_was()
        
    if st.button('Daten vom Server neu laden'):
        st.cache_data.clear()
        #rerun page
        st.experimental_rerun()






















