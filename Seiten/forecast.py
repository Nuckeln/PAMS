import pandas as pd
from statsmodels.tsa.statespace.sarimax import SARIMAX
import uuid

import streamlit as st
import datetime
from datetime import datetime

from Data_Class.MMSQL_connection import read_Table, save_Table_append
import plotly.graph_objects as go
import plotly.express as px
from PIL import Image
from Data_Class.sql import SQL


def new_forecast(data, spalte_summe,sel_Zeitraum):
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
    #data = data[data['DeliveryDepot'].isin(['KNSTR', 'KNLEJ', 'KNBFE', 'KNHAJ'])]
    
    # Ändere "None" Werte in PartnerNo mit Kd nicht Gepflegt

    # Angenommen, df ist Ihr DataFrame
    data['PartnerNo'].replace("None", 'Kd nicht Gepflegt', inplace=True)
 
    # Datumsspalte in datetime umwandeln und Daten aggregieren
    data['PlannedDate'] = pd.to_datetime(data['PlannedDate'])
    # löche die letzen 60 Tage
    daily_picks = data.groupby(['PlannedDate', 'DeliveryDepot']).agg({spalte_summe: 'sum'}).reset_index()

    # Funktion zum Anpassen und Vorhersagen mit dem SARIMA-Modell
    def fit_sarima_model(data, order, seasonal_order):
        # Daten für das spezifische Depot filtern und auf Geschäftstage normalisieren
        depot_data = data.groupby('PlannedDate').sum()[spalte_summe].asfreq('B', fill_value=0)
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
    forecast_df = fit_sarima_model(daily_picks, (p, d, q), (P, D, Q, s))

    return forecast_df

def create_new_forecast():
    # Daten laden
    df = read_Table('business_depotDEBYKN-DepotDEBYKNOrders')
    df2 = read_Table('business_depotDEBYKN-DepotDEBYKNOrderItems')
    dfOrders = pd.merge(df, df2, on='SapOrderNumber', how='inner')
    #dfOrders({'CorrespondingMastercases': 0, 'CorrespondingOuters': 0, 'CorrespondingPallets': 0}, inplace=True)
    to_cal = ['CorrespondingMastercases', 'CorrespondingOuters', 'CorrespondingPallets']
    sel_Zeitraum = st.slider('Zeitraum in Tagen anzeigen', 0, 60, 14)
    forecast_df = pd.DataFrame()
    for each in to_cal:
        new_forecast_df = new_forecast(dfOrders, each, sel_Zeitraum)
        # Rename new Columns to each + '_mean' and each + '_ci_lower' and each + '_ci_upper'
        new_forecast_df = new_forecast_df.rename(columns={'mean': each + '_mean', 'mean_ci_lower': each + '_ci_lower', 'mean_ci_upper': each + '_ci_upper', 'mean_se': each + '_se'})
        forecast_df = pd.concat([forecast_df, new_forecast_df], axis=1)
    forecast_df = forecast_df.reset_index()
    # Apped 
    forecast_df['erstellungsDatum'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    forecast_df['run_ID'] = uuid.uuid4()     
    forecast_df['erstellt von'] = st.session_state.user
    return forecast_df

def plot_stacked_bar_chart(df):
    """
    Erstellt ein gestapeltes Balkendiagramm für die Summen der Kategorien
    'CorrespondingMastercases_mean', 'CorrespondingOuters_mean', 'CorrespondingPallets_mean' 
    pro Tag und fügt Datenbeschriftungen hinzu.
    
    Parameter:
    df (DataFrame): DataFrame mit Datumsspalte 'index' und numerischen Spalten der Kategorien.

    Rückgabe:
    None (zeigt die Grafik an)
    """
    import matplotlib.pyplot as plt
    import numpy as np

    # Datumsspalte sicherstellen
    df['index'] = pd.to_datetime(df['index'], errors='coerce')
    # entferne Uhrzeit aus Datum
    df['index'] = df['index'].dt.date

    # Gruppieren und Summieren nach Datum
    df_grouped = df.groupby('index')[
        ['CorrespondingMastercases_mean', 'CorrespondingOuters_mean', 'CorrespondingPallets_mean']
    ].sum().reset_index()

    # Plot erstellen
    fig, ax = plt.subplots(figsize=(12, 6))
    bars = df_grouped.set_index('index').plot(kind='bar', stacked=True, ax=ax, figsize=(12, 6))

    # Datenbeschriftung je Kategorie hinzufügen
    for container in ax.containers:
        ax.bar_label(container, fmt='%.0f', label_type='center', fontsize=10, color='white')

    # Gesamtsumme über jedem Balken hinzufügen
    totals = df_grouped[['CorrespondingMastercases_mean', 'CorrespondingOuters_mean', 'CorrespondingPallets_mean']].sum(axis=1)
    for idx, total in enumerate(totals):
        ax.text(idx, total + max(totals) * 0.01, f'{total:.0f}', ha='center', fontsize=12, fontweight='bold', color='black')

    # Diagrammbeschriftungen
    ax.set_xlabel('Datum')
    ax.set_ylabel('Summe')
    ax.set_title('Forecast Mastercases, Outers und Pallets')
    ax.legend(title='Kategorie')
    plt.xticks(rotation=45)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    # passe die höhe des Gesamten Diagramms an auf 400 px
    plt.tight_layout()

    return st.pyplot(fig, use_container_width=True)


def plot_stacked_bar_chart_plotly(df, colors=None):
    """
    Erstellt ein gestapeltes Balkendiagramm mit Plotly für die Summen der Kategorien
    'CorrespondingMastercases_mean', 'CorrespondingOuters_mean', 'CorrespondingPallets_mean' 
    pro Tag und fügt Datenbeschriftungen hinzu.

    Parameter:
    df (DataFrame): DataFrame mit Datumsspalte 'index' und numerischen Spalten der Kategorien.
    colors (dict): Ein Dictionary mit Farben für die einzelnen Kategorien.

    Rückgabe:
    fig (plotly.graph_objects.Figure): Die generierte Plotly-Grafik.
    """
    # Standardfarben definieren, falls nicht übergeben
    if colors is None:
        colors = {
            'CorrespondingMastercases_mean': '#0F2B63',
            'CorrespondingOuters_mean': '#ef7d00',
            'CorrespondingPallets_mean': '#4FAF46'
        }

    # Datumsspalte sicherstellen und Uhrzeit entfernen
    df['index'] = pd.to_datetime(df['forecastDate'], errors='coerce').dt.date

    # Gruppieren und Summieren nach Datum
    df_grouped = df.groupby('index')[
        ['CorrespondingMastercases_mean', 'CorrespondingOuters_mean', 'CorrespondingPallets_mean']
    ].sum().reset_index()

    # Stacked Bar Chart mit Plotly erstellen
    fig = go.Figure()

    for column in ['CorrespondingMastercases_mean', 'CorrespondingOuters_mean', 'CorrespondingPallets_mean']:
        fig.add_trace(go.Bar(
            x=df_grouped['index'],
            y=df_grouped[column],
            name=column.replace('_mean', ''),
            text=df_grouped[column].astype(int),
            textposition='inside',
            marker_color=colors[column]
        ))

    # Gesamtsumme über jedem Balken hinzufügen
    df_grouped['total'] = df_grouped[['CorrespondingMastercases_mean', 'CorrespondingOuters_mean', 'CorrespondingPallets_mean']].sum(axis=1)
    for i, total in enumerate(df_grouped['total']):
        fig.add_annotation(
            x=df_grouped['index'][i],
            y=total + max(df_grouped['total']) * 0.01,
            text=f'{total:.0f}',
            showarrow=False,
            font=dict(size=12, color='black', family="Arial"),
        )

    # Layout anpassen
    fig.update_layout(
        title='Forecast Mastercases, Outers und Pallets',
        xaxis_title='Datum',
        yaxis_title='Summe',
        barmode='stack',
        legend_title='Kategorie',
        height=600,
        template='plotly_white'
    )

    return st.plotly_chart(fig, use_container_width=True)
    

# Dashboard aufbauen
def main():
    try: 
        exestierende_forecasts = read_Table('PAMS_Forecast')
        runs = exestierende_forecasts[['run_ID', 'erstellungsDatum', 'erstellt von']].drop_duplicates()
        #Fasse alle Daten zusammen
        runs['Bisherige Prognosen'] = runs['erstellungsDatum']  + ' - ' + runs['erstellt von'] + ' - ' + runs['run_ID']
        # erstelle ein Array aus Bisheigen Prognosen
        runs = runs['Bisherige Prognosen'].to_list()
        
        # Extrahiere nur die gewählte RUN ID aus runs 

    except:
        runs = ['Keine Prognose vorhanden Bitte ADMIN kontaktieren','']
        
    col1, col2, col3 = st.columns([2, 1,2])
    with col1:
        st.title("📦 Forecast DE30")
    with col2:
        show_Forecast = st.selectbox('Bisherige Prognosen', runs)  
        #Extrahiere nur die gewählte RUN ID aus show_Forecast
        sel_runs = show_Forecast.split(' - ')[2]
    with col3:
        neu = st.button('Neue Prognose erstellen', help='Erstellt eine neue Prognose und speichert sie in der Datenbank.')
    if neu:
        new_F = create_new_forecast()
        #erstelle neue Spalte forecastDate aus der Index Spalte
        new_F['forecastDate'] = new_F['index']
        # nur Datum
        new_F['forecastDate'] = new_F['forecastDate'].dt.date
        new_F.drop('index', axis=1, inplace=True)
        # Kombiniere mit bestehenden Daten
        #SQL.update_Table('PAMS_Forecast', forecast_df, 'run_ID')
        save_Table_append(new_F, 'PAMS_Forecast')
    img_strip = Image.open('Data/img/strip.png')
    img_strip = img_strip.resize((1000, 15))
    st.image(img_strip, use_column_width=True)

    sel_forecastID = exestierende_forecasts[exestierende_forecasts['run_ID'] == sel_runs].copy()
    if show_Forecast == 'Keine Prognose vorhanden Bitte ADMIN kontaktieren':
        pass
    else:
        with st.expander(f"Prognose Details von {show_Forecast} anzeigen", expanded=False):
            st.dataframe(sel_forecastID)
    
    plot_stacked_bar_chart_plotly(sel_forecastID)

    
if __name__ == "__main__":
    main()