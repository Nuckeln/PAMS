import pandas as pd
from statsmodels.tsa.statespace.sarimax import SARIMAX
import uuid

import streamlit as st
import datetime
from datetime import datetime
from Data_Class.MMSQL_connection import read_Table, save_Table_append
#from Data_Class.MMSQL_connection import read_Table, save_Table_append
import plotly.graph_objects as go
import plotly.express as px
from PIL import Image
from Data_Class.sql import SQL

import holidays
de_holidays = holidays.country_holidays(country='DE', subdiv='BY')

@st.cache_data()
def read_actuals_Pick():
    df = SQL.read_table('business_depotDEBYKN-DepotDEBYKNOrders', ['SapOrderNumber', 'PlannedDate'])
    
    df2 = SQL.read_table('business_depotDEBYKN-DepotDEBYKNOrderItems', ['SapOrderNumber', 'CorrespondingMastercases', 'CorrespondingOuters', 'CorrespondingPallets'])
    dfOrders = pd.merge(df, df2, on='SapOrderNumber', how='inner')
    #Group by PlannedDate
    dfOrders = dfOrders.groupby('PlannedDate').sum().reset_index()
    return dfOrders

def new_forecast(data, spalte_summe,sel_Zeitraum):
    '''
    Args:
        data ([type]): [Packtyp]
        spalte_summe ([int]): [Summenspalte]
        sel_Zeitraum ([int]): [Zu berechnender Zeitraum in der Zukunft]
    '''    


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
        
        # Prognose für die nächsten X Geschäftstage
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
    sel_Zeitraum = 14#st.slider('Zeitraum in Tagen anzeigen', 0, 60, 14)
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




def create_new_Pallet_forecast():
    df = read_Table('business_depotDEBYKN-DepotDEBYKNOrders')
    sel_Zeitraum = 14
    pal_forecast  = new_forecast(df, 'ActualNumberOfPallets', sel_Zeitraum)


def plot_stacked_bar_chart_plotly(df, colors=None,dfOrders=None):
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
    

def plot_stacked_bars_with_line(df, dfOrders, colors=None):
    # 1) Datumsspalten parsen
    df['forecastDate'] = pd.to_datetime(df['forecastDate']).dt.date
    dfOrders['PlannedDate'] = pd.to_datetime(dfOrders['PlannedDate']).dt.date

    # 2) Zusammenführen
    merged_df = df.merge(dfOrders, left_on='forecastDate', right_on='PlannedDate', how='inner')
    #st.write(merged_df)

    if merged_df.empty:
        plot_stacked_bar_chart_plotly(df, colors)
        return

    # 3) Standardfarben, falls nicht übergeben
    if colors is None:
        colors = {
            'CorrespondingMastercases_mean': '#0F2B63',
            'CorrespondingOuters_mean': '#ef7d00',
            'CorrespondingPallets_mean': '#4FAF46'
        }

    # ─────────────────────────────────────────────────────────────────────────
    # TEIL A: Stacked Bars aus Forecast-Daten (df_grouped)
    # ─────────────────────────────────────────────────────────────────────────
    df['index'] = pd.to_datetime(df['forecastDate'], errors='coerce').dt.date
    df_grouped = (
        df.groupby('index')[['CorrespondingMastercases_mean',
                             'CorrespondingOuters_mean',
                             'CorrespondingPallets_mean']]
          .sum()
          .reset_index()
    )

    # Plotly-Figure erzeugen
    fig = go.Figure()

    # Gestapelte Balken je Kategorie
    for column in ['CorrespondingMastercases_mean', 'CorrespondingOuters_mean', 'CorrespondingPallets_mean']:
        fig.add_trace(go.Bar(
            x=df_grouped['index'],
            y=df_grouped[column],
            name=column.replace('_mean', ''),
            text=df_grouped[column].astype(int),
            textposition='inside',
            marker_color=colors[column],
            hovertemplate=(
                "<b>%{x}</b><br>" +
                f"{column.replace('_mean','')}: " +
                "%{y}<extra></extra>"
            )
        ))

    # Gesamtsumme berechnen (nur Forecast-Seite)
    df_grouped['total_forecast'] = (
        df_grouped['CorrespondingMastercases_mean'] +
        df_grouped['CorrespondingOuters_mean'] +
        df_grouped['CorrespondingPallets_mean']
    )

    # Summen-Werte als Annotation über die Balken
    for i, total_val in enumerate(df_grouped['total_forecast']):
        fig.add_annotation(
            x=df_grouped['index'][i],
            y=total_val + max(df_grouped['total_forecast']) * 0.01,
            text=f'{int(total_val)}',
            showarrow=False,
            font=dict(size=12, color='black', family="Arial"),
        )

    # ─────────────────────────────────────────────────────────────────────────
    # TEIL B: Linie aus merged_df-Daten (Actuals)
    # ─────────────────────────────────────────────────────────────────────────
    # Hier z.B. Summe der echten CorrespondingMastercases/Outers/Pallets
    # pro 'PlannedDate' bilden:
    df_line = (
        merged_df.groupby('PlannedDate')[['CorrespondingMastercases',
                                          'CorrespondingOuters',
                                          'CorrespondingPallets']]
                 .sum()
                 .reset_index()
    )

    df_line['total_actual'] = (
        df_line['CorrespondingMastercases'] +
        df_line['CorrespondingOuters'] +
        df_line['CorrespondingPallets']
    )

    # Scatter-Linie mit customdata für den Hover
    fig.add_trace(go.Scatter(
        x=df_line['PlannedDate'],
        y=df_line['total_actual'],
        mode='lines+markers',
        name='Summe Actuals',
        marker=dict(color='black'),
        customdata=df_line[['CorrespondingMastercases',
                            'CorrespondingOuters',
                            'CorrespondingPallets']],
        hovertemplate=(
            "<b>Datum: %{x}</b><br>" +
            "Gesamt (Ist Werte zu Stichtag): %{y}<br>" +
            "Mastercases: %{customdata[0]}<br>" +
            "Outers: %{customdata[1]}<br>" +
            "Pallets: %{customdata[2]}<extra></extra>"
        )
    ))

    # ─────────────────────────────────────────────────────────────────────────
    # TEIL C: Layout anpassen
    # ─────────────────────────────────────────────────────────────────────────
    fig.update_layout(
        title='Forecast (Stacked) + Actual (Linie)',
        xaxis_title='Datum',
        yaxis_title='Summe',
        barmode='stack',
        legend_title='Kategorie',
        height=800,
        template='plotly_white',
        hovermode='x'
    )

    st.plotly_chart(fig, use_container_width=True)


# Dashboard aufbauen
def main():
    try: 
        exestierende_forecasts = SQL.read_table('PAMS_Forecast')

        # Extrahiere nur die gewählte RUN ID aus runs 
        runs = exestierende_forecasts[['run_ID', 'erstellungsDatum', 'erstellt von']].drop_duplicates()

        # Stelle sicher, dass 'erstellungsDatum' wirklich ein Datums-/Zeitformat ist:
        runs['erstellungsDatum'] = pd.to_datetime(runs['erstellungsDatum'])

        # Nach Datum absteigend sortieren
        runs = runs.sort_values(by='erstellungsDatum', ascending=False)

        runs['Bisherige Prognosen'] = (
            runs['erstellungsDatum'].astype(str) 
            + ' - ' 
            + runs['erstellt von'] 
            + ' - ' 
            + runs['run_ID']
        )

        # Array/Listenwert für das selectbox
        runs_list = runs['Bisherige Prognosen'].tolist()
    except:
        runs = ['Keine Prognose vorhanden Bitte ADMIN kontaktieren','']
        
    col1, col2, col3 = st.columns([2, 1,2])
    with col1:
        st.title("📦 Forecast DE30")
    with col2:
        show_Forecast = st.selectbox('Bisherige Prognosen', runs_list)  
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
    
    #plot_stacked_bar_chart_plotly(sel_forecastID)
    df_orders = read_actuals_Pick()
    plot_stacked_bars_with_line(sel_forecastID, df_orders)

    
if __name__ == "__main__":
    main()