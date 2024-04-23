import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.statespace.sarimax import SARIMAX
import uuid

import matplotlib.dates as mdates


import streamlit as st
import datetime
from datetime import datetime


from PIL import Image 
from Data_Class.MMSQL_connection import read_Table, save_Table_append
import plotly.graph_objects as go

@st.cache_data
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

def new_forecast(data, depot_name, spalte_summe):
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
        forecast = model_fit.get_forecast(steps=45)
        forecast_df = forecast.summary_frame()
        
        return forecast_df

    # SARIMA Modellparameter definieren
    p, d, q = 1, 1, 1
    P, D, Q, s = 1, 1, 1, 5  # Annahme einer wöchentlichen Saisonalität

    # Modell für ein spezifisches Depot anpassen (z.B. KNSTR)
    forecast_df = fit_sarima_model(daily_picks, depot_name, (p, d, q), (P, D, Q, s))

    return forecast_df

def plot_forecast(dates, actual, forecast, lower_ci, upper_ci, depot_name):
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
        title=f'Prognose der Picks für {depot_name}',
        xaxis_title='Datum',
        yaxis_title='Anzahl der Picks',
        hovermode='x',
        showlegend=True
    )

    # Figur zusammenstellen
    fig = go.Figure(data=[actual_trace, forecast_trace, ci_trace], layout=layout)

    # Diagramm anzeigen
    return st.plotly_chart(fig, use_container_width=True)

def main():
    dfOrders = readData()
    def lade_bisherige_forecasts_add_to_df(dfOrders: pd.DataFrame, depot_name: str, df_existing_forecasts: pd.DataFrame, typ: str):
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
                dfOrders = dfOrders.set_index('PlannedDate')[typ].asfreq('B', fill_value=0)

            # filter nach type
            df_existing_forecasts = df_existing_forecasts[df_existing_forecasts['typ'] == typ]
            daily_type_depot_averages = df_existing_forecasts.groupby(['dates', 'typ', 'depotName']).agg({
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
    df_existing_forecasts = read_Table('PAMS_Forecast')  
    col1, col2, col3 = st.columns([2,2,2])
    with col1:
        typ = st.radio('Prognose für', ['Picks'], index=0)
        if typ == 'Picks':
            typ = 'Picks Gesamt'
        elif typ == 'Kommissionierte Ladeträger':
            typ = 'Gepackte Paletten'
    with col2:
        depots = ['KNSTR', 'KNLEJ', 'KNBFE', 'KNHAJ', 'Alle Depots']
        depot_name = st.multiselect('Depot auswählen', depots, default='Alle Depots')
    with col3:
        with st.popover('Erklärung ℹ️'):
                st.write('folgt')
        st.write('')
    
####Erstellle Plots für jedes Depot
    
    for depot_name in depot_name:
    
        #
    
        forecast_df = new_forecast(dfOrders,depot_name, typ)
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
        plot_forecast(dates, actual, forecast, lower_ci, upper_ci, depot_name)
        #df = lade_bisherige_forecasts_add_to_df(dfOrders, depot_name,df_existing_forecasts, typ)
        #st.dataframe(df)

