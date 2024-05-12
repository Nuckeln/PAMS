import pandas as pd
from statsmodels.tsa.statespace.sarimax import SARIMAX
import uuid

import streamlit as st
import datetime
from datetime import datetime

from Data_Class.MMSQL_connection import read_Table, save_Table_append
import plotly.graph_objects as go

@st.cache_data(show_spinner=False)
def readData():
    '''Lese die Daten aus der Tabelle Prod_Kundenbestellungen und bereite sie für die Prognose vor'''
    df_Bestellungen = read_Table('Prod_Kundenbestellungen')
    #df_Bestellungen = pd.read_csv('/Library/Python_local/Superdepot Reporting/Seiten/prod_Kundenbestellungen.csv')
    #sortiere nach PlannedDate absteigend
    df_Bestellungen = df_Bestellungen.sort_values(by='PlannedDate', ascending=False)
    #entferne die ersten 300 Zeilen
    df_Bestellungen['PlannedDate'] = pd.to_datetime(df_Bestellungen['PlannedDate'])
    # Entferne Timezone von PlannedDate
    df_Bestellungen['PlannedDate'] = df_Bestellungen['PlannedDate'].dt.tz_localize(None)
    df_Bestellungen['Picks Stangen'] = df_Bestellungen['Picks Stangen'].astype(float)
    df_Bestellungen['Picks Karton'] = df_Bestellungen['Picks Karton'].astype(float)
    df_Bestellungen['Picks Paletten'] = df_Bestellungen['Picks Paletten'].astype(float)
    df_Bestellungen['Picks Gesamt'] = df_Bestellungen['Picks Gesamt'].astype(float)
    df_Bestellungen['Gepackte Paletten'] = df_Bestellungen['Gepackte Paletten'].astype(float)
    # ziehe die letzten 60 Tage ab    
    return df_Bestellungen

def filter_data_by_date(data, days: int,date_column: str, zukunft: bool = False, vergangenheit: bool = False):
    '''Filtere die Daten nach einem bestimmten Zeitraum vor oder nach dem aktuellen Datum
    Args:
        data (pd.DataFrame): DataFrame mit den Daten
        days (int): Anzahl der Tage, die gefiltert werden sollen
        date_column (str): Name der Spalte mit den Datumswerten
        zukunft (bool): True, wenn die Daten für die Zukunft gefiltert werden sollen
        vergangenheit (bool): True, wenn die Daten für die Vergangenheit gefiltert werden sollen
    Returns:
        pd.DataFrame: Gefilterter DataFrame
    '''
    # Aktuelles Datum abrufen
    current_date = datetime.now().date()
    current_date = pd.to_datetime(current_date)
    # Prüfe den Datentyp des Datums und passe ihn an, falls erforderlich zu datetime
    if isinstance(data[date_column].iloc[0], str):
        data[date_column] = pd.to_datetime(data[date_column])
    # Filtere die Daten nach dem gewünschten Zeitraum
    if vergangenheit == True:
        # filtere das df von ergebnis = heute - days  bis ergebniss - days
        filtered_data = data[(data[date_column] >= current_date - pd.Timedelta(days=days)) & (data[date_column] <= current_date)]
    elif zukunft == True:
        # filtere das df von heute bis heute + days
        filtered_data = data[(data[date_column] >= current_date) & (data[date_column] <= current_date + pd.Timedelta(days=days))]
    
    return filtered_data

def new_forecast(data, depot_name, spalte_summe,sel_Zeitraum):
    '''erstelle eine Prognose für die Spalte zb. Picks Gesamt und das Depot zb. KNSTR
    data: DataFrame mit den Daten
    depot_name: Name des Depots für das die Prognose erstellt werden soll
    spalte_summe: Spalte für die die Prognose erstellt werden soll
    return: DataFrame mit den Prognosewerten
    
    Args:
        data ([type]): [description]
        depot_name ([type]): [description]
        spalte_summe ([type]): [description]
    '''    
    # entferne zeilen wenn DeliveryDepot ist nicht ['KNSTR', 'KNLEJ', 'KNBFE', 'KNHAJ']
    data = data[data['DeliveryDepot'].isin(['KNSTR', 'KNLEJ', 'KNBFE', 'KNHAJ'])]
    
    # Ändere "None" Werte in PartnerNo mit Kd nicht Gepflegt

    # Angenommen, df ist Ihr DataFrame
    data['PartnerNo'].replace("None", 'Kd nicht Gepflegt', inplace=True)
 
    # Datumsspalte in datetime umwandeln und Daten aggregieren
    data['PlannedDate'] = pd.to_datetime(data['PlannedDate'])
    # löche die letzen 60 Tage
    daily_picks = data.groupby(['PlannedDate', 'DeliveryDepot']).agg({spalte_summe: 'sum'}).reset_index()

    # Funktion zum Anpassen und Vorhersagen mit dem SARIMA-Modell
    def fit_sarima_model(data, depot_name, order, seasonal_order):
        # Daten für das spezifische Depot filtern und auf Geschäftstage normalisieren
        if depot_name == 'Alle Depots':
            depot_data = data.groupby('PlannedDate').sum()[spalte_summe].asfreq('B', fill_value=0)
        else:
            depot_data = data[data['DeliveryDepot'] == depot_name]
            depot_data = depot_data.set_index('PlannedDate')[spalte_summe].asfreq('B', fill_value=0)
        
        # SARIMA-Modell anpassen
        model = SARIMAX(depot_data, order=order, seasonal_order=seasonal_order, enforce_stationarity=False, enforce_invertibility=False)
        model_fit = model.fit(disp=False)
        
        # Prognose für die nächsten 30 Geschäftstage
        forecast = model_fit.get_forecast(steps=sel_Zeitraum)
        forecast_df = forecast.summary_frame()
        
        return forecast_df

    # SARIMA Modellparameter definieren
    p, d, q = 1, 1, 1
    P, D, Q, s = 1, 1, 1, 5  # Annahme einer wöchentlichen Saisonalität

    # Modell für ein spezifisches Depot anpassen (z.B. KNSTR)
    forecast_df = fit_sarima_model(daily_picks, depot_name, (p, d, q), (P, D, Q, s))

    return forecast_df

def plot_forecast(dates, actual, forecast, lower_ci, upper_ci, depot_name,show_actual=False):
    # Trace für die tatsächlichen Daten
    actual_trace = go.Scatter(
        x=dates,
        y=actual,
        mode='lines+markers+text',
        name='Tatsächliche Picks',
        text=[f'{y:.0f}' if y is not None else '' for y in actual],  # Formatierung der Beschriftung für Nicht-None-Werte
        textposition='top center'
    )

    # Trace für die prognostizierten Daten
    forecast_trace = go.Scatter(
        x=dates,
        y=forecast,
        mode='lines+markers+text',
        name='Prognostizierte Picks',
        text=[f'{y:.1f}' for y in forecast],
        textposition='top center'
    )

    # Trace für das Konfidenzintervall
    combined_dates = list(dates) + list(dates[::-1])
    combined_ci = list(upper_ci) + list(lower_ci[::-1])
    ci_trace = go.Scatter(
        x=combined_dates,
        y=combined_ci,
        fill='toself',
        fillcolor='rgba(0,100,80,0.2)',
        line=dict(color='rgba(255,255,255,0)'),
        name='Konfidenzintervall'
    )

    # Layout-Einstellungen

    layout = go.Layout(
        xaxis_title='Datum',
        yaxis_title='Summe',
        hovermode='x',
        showlegend=True
    )

    if show_actual:
        fig = go.Figure(data=[actual_trace, forecast_trace, ci_trace], layout=layout)
    else:
        fig = go.Figure(data=[forecast_trace, ci_trace], layout=layout)
    # Diagramm anzeigen
    return st.plotly_chart(fig, use_container_width=True)

def lade_bisherige_forecasts_add_to_df(dfOrders: pd.DataFrame, depot_name: str, df_existing_forecasts: pd.DataFrame, typ: str, kummuliert: bool = False, sel_uuid: str = None):
        '''Lade bisherige Prognosen aus der Tabelle PAMS_Forecast und füge sie zum DataFrame hinzu
        Args:
            forecast_df (pd.DataFrame): DataFrame mit den aktuellen Prognosewerten
            depot_name (str): Name des Depots
            df_existing_forecasts (pd.DataFrame): DataFrame mit bisherigen Prognosen
        '''
        dfOrders = dfOrders[dfOrders['DeliveryDepot'].isin(['KNSTR', 'KNLEJ', 'KNBFE', 'KNHAJ'])]
        if depot_name == 'Alle Depots':
            dfOrders = dfOrders.groupby('PlannedDate').sum()[typ].asfreq('B', fill_value=0)
        else:
            dfOrders = dfOrders[dfOrders['DeliveryDepot'] == depot_name]
            dfOrders = dfOrders.groupby('PlannedDate').sum()[typ].asfreq('B', fill_value=0)
        # filter nach type
        df_existing_forecasts = df_existing_forecasts[df_existing_forecasts['typ'] == typ]
        # filter nach depot

        df_existing_forecasts = df_existing_forecasts[df_existing_forecasts['depotName'].isin([depot_name])]
        # else:
        #     df_existing_forecasts = df_existing_forecasts[df_existing_forecasts['DeliveryDepot'] == depot_name]
        daily_type_depot_averages = df_existing_forecasts.groupby(['dates', 'typ', 'depotName']).agg({
            'mean': 'mean',
            'mean_se': 'mean',
            'mean_ci_lower': 'mean',
            'mean_ci_upper': 'mean'
        }).reset_index()
        
        
        dfOrders.index = pd.to_datetime(dfOrders.index).strftime('%Y-%m-%d')
        # to string
        daily_type_depot_averages['dates'] = daily_type_depot_averages['dates'].astype(str)
        #entferne alle Spalten Planned Date und Picks Gesamt aus dfOrders
        dfOrders = dfOrders.drop(columns=['PlannedDate', 'Picks Gesamt'])
        df = pd.merge(daily_type_depot_averages, dfOrders, left_on='dates', right_on='PlannedDate', how='left')
        return df


def main():
    pd.set_option("display.precision", 2)

    dfOrders = readData()
    df_existing_forecasts = read_Table('PAMS_Forecast')  
    col1, col2, col3 = st.columns([2,4,1])
    with col1:
        typ = st.radio('Prognose für', ['Picks','Kommissionierte Ladeträger'], index=0,horizontal=True)
        if typ == 'Picks':
            typ = 'Picks Gesamt'
        elif typ == 'Kommissionierte Ladeträger':
            typ = 'Gepackte Paletten'
    with col2:
        depots = ['KNSTR', 'KNLEJ', 'KNBFE', 'KNHAJ', 'Alle Depots']
        depot_name = st.multiselect('Depot auswählen', depots, default='Alle Depots')
    with col3:
        st.write('')
        st.write('')
        with st.popover('Erklärung ℹ️'):
                st.write('folgt')
        st.write('')
    col1, col2, col3 = st.columns([2,4,1])
    with col1:
        show_old_forecasts = st.checkbox('Zeige bisherige Prognosen', value=False)  
        if show_old_forecasts:
            kummuliert = st.toggle('Kummuliert', value=True)
            if kummuliert == False:
                sel_uuid = st.selectbox('Wähle eine Prognose aus', df_existing_forecasts['run_ID'].unique())
            
    with col2:
        sel_Zeitraum = st.slider('Zeitraum in Tagen anzeigen', 0, 60, 14)

####Erstellle Plots für jedes Depot
    
    for depot_name in depot_name:
    
        #
    
        forecast_df = new_forecast(dfOrders,depot_name, typ, sel_Zeitraum)
        dates = forecast_df.index
        actual = [None] * len(dates)  # Setzen Sie hier Ihre tatsächlichen Werte, falls verfügbar
        forecast = forecast_df['mean']
        lower_ci = forecast_df['mean_ci_lower']
        upper_ci = forecast_df['mean_ci_upper']
        forecast_df['depotName'] = depot_name
        erstellungs_Datum = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        forecast_df['erstellungsDatum'] = erstellungs_Datum
        #erstelle Spalte dates und füge dates hinzu 
        forecast_df['dates'] = dates
        # erstelle eine UUID run in depots und füge sie zum DataFrame hinzu
        forecast_df['run_ID'] = uuid.uuid4()
        # erstelle eine Spalte typ und füge den ausgewählten Typ hinzu
        forecast_df['typ'] = typ        
        save_Table_append(forecast_df, 'PAMS_Forecast')
        st.write(f'Prognose für {depot_name}')
        plot_forecast(dates, actual, forecast, lower_ci, upper_ci, depot_name,show_actual=False)
        
        if show_old_forecasts:

            df = lade_bisherige_forecasts_add_to_df(dfOrders, depot_name, df_existing_forecasts, typ,kummuliert, sel_uuid=None)
            df = filter_data_by_date(df, sel_Zeitraum, 'dates', vergangenheit=True)
            st.write(f'Zeige bisherige Prognosen für {depot_name}')
            plot_forecast(df['dates'],df[typ], df['mean'], df['mean_ci_lower'], df['mean_ci_upper'], depot_name, show_actual=True)
        

