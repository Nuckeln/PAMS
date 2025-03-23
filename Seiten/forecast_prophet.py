import pandas as pd
from statsmodels.tsa.statespace.sarimax import SARIMAX
import uuid
from prophet import Prophet
import warnings
warnings.filterwarnings("ignore")

import streamlit as st
import datetime
from datetime import datetime
from Data_Class.MMSQL_connection import read_Table, save_Table_append
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image
from Data_Class.sql import SQL

import holidays
# Feiertage Bayern
de_holidays = holidays.country_holidays(country='DE', subdiv='BY')
def is_bavarian_holiday(date):
    return date in de_holidays

def read_actuals_Pick():
    df = SQL.read_table('business_depotDEBYKN-DepotDEBYKNOrders', ['SapOrderNumber', 'PlannedDate', 'IsDeleted', 'IsReturnDelivery'])
    df = df[(df['IsDeleted'] == 0) & (df['IsReturnDelivery'] == 0)]
    #drop both columns
    df.drop(['IsDeleted', 'IsReturnDelivery'], axis=1, inplace=True)
    df2 = SQL.read_table('business_depotDEBYKN-DepotDEBYKNOrderItems', ['SapOrderNumber', 'CorrespondingMastercases', 'CorrespondingOuters', 'CorrespondingPallets'])
    dfOrders = pd.merge(df, df2, on='SapOrderNumber', how='inner')
    dfOrders['PlannedDate'] = pd.to_datetime(dfOrders['PlannedDate']).dt.tz_localize(None)
    dfOrders = dfOrders[dfOrders['PlannedDate'] >= (pd.Timestamp.today().normalize() - pd.Timedelta(days=600))]
    dfOrders = dfOrders.groupby('PlannedDate').sum().reset_index()
    return dfOrders

def new_forecast(data, spalte_summe, sel_Zeitraum):
    # Daten filtern & vorbereiten
    data['PlannedDate'] = pd.to_datetime(data['PlannedDate']).dt.tz_localize(None)
    data = data[data['PlannedDate'] >= (pd.Timestamp.today().normalize() - pd.Timedelta(days=600))]
    data['Weekday'] = data['PlannedDate'].dt.weekday
    data['IsHoliday'] = data['PlannedDate'].dt.date.apply(is_bavarian_holiday)
    data = data[data['IsHoliday'] == False]

    # Aggregieren auf Tagesebene
    df = data.groupby('PlannedDate')[spalte_summe].sum().reset_index()
    df.rename(columns={'PlannedDate': 'ds', spalte_summe: 'y'}, inplace=True)

    # Feiertage-DataFrame für Prophet
    holidays_df = pd.DataFrame({
        'ds': [pd.Timestamp(d) for d in de_holidays if pd.Timestamp(d) >= df['ds'].min()],
        'holiday': 'BavarianHoliday'
    })

    # Prophet-Modell anlernen
    model = Prophet(holidays=holidays_df)
    model.fit(df)

    # Zukünftige Daten generieren (werktagsbasiert)
    future = model.make_future_dataframe(periods=sel_Zeitraum, freq='B')
    forecast = model.predict(future)

    # Feiertage in Zukunft auf 0 setzen
    forecast['IsHoliday'] = forecast['ds'].dt.date.apply(is_bavarian_holiday)
    forecast.loc[forecast['IsHoliday'] == True, ['yhat','yhat_lower','yhat_upper']] = 0

    # Für den gewünschten Zeitraum (sel_Zeitraum) filtern & Spalten umbenennen
    forecast = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(sel_Zeitraum).copy()
    forecast.rename(columns={
        'ds': 'forecastDate',
        'yhat': spalte_summe + '_mean',
        'yhat_lower': spalte_summe + '_ci_lower',
        'yhat_upper': spalte_summe + '_ci_upper'
    }, inplace=True)

    return forecast.set_index('forecastDate')

def create_new_forecast():
    # Daten laden
    df = read_Table('business_depotDEBYKN-DepotDEBYKNOrders')
    df2 = read_Table('business_depotDEBYKN-DepotDEBYKNOrderItems')
    df['PlannedDate'] = pd.to_datetime(df['PlannedDate']).dt.tz_localize(None)
    df = df[df['PlannedDate'] < (pd.Timestamp.today().normalize() - pd.Timedelta(days=40))]

    #'die Kunden stehen in der Spalte PartnerNo'
    df['PartnerNo'].replace("None", 'Kd nicht Gepflegt', inplace=True)

    dfOrders = pd.merge(df, df2, on='SapOrderNumber', how='inner')
    to_cal = ['CorrespondingMastercases', 'CorrespondingOuters', 'CorrespondingPallets']
    sel_Zeitraum = 28
    forecast_df = pd.DataFrame()
    for each in to_cal:
        new_forecast_df = new_forecast(dfOrders, each, sel_Zeitraum)
        # Rename new Columns to each + '_mean' and each + '_ci_lower' and each + '_ci_upper'
        new_forecast_df = new_forecast_df.rename(columns={'mean': each + '_mean', 'mean_ci_lower': each + '_ci_lower', 'mean_ci_upper': each + '_ci_upper', 'mean_se': each + '_se'})
        if forecast_df.empty:
            forecast_df = new_forecast_df.copy()
        else:
            forecast_df = pd.concat([forecast_df, new_forecast_df], axis=1)
    forecast_df = forecast_df.reset_index()
    # Apped 
    forecast_df['erstellungsDatum'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    forecast_df['run_ID'] = uuid.uuid4()     
    forecast_df['erstellt von'] = st.session_state.user
    
    new_F = forecast_df.reset_index()
    new_F['forecastDate'] = new_F['forecastDate'].dt.date

    return new_F

def create_new_Pallet_forecast():
    df = read_Table('business_depotDEBYKN-DepotDEBYKNOrders')
    sel_Zeitraum = 28
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

    # erstelle vergleichsstatistik von line zu df
    df_line['PlannedDate'] = pd.to_datetime(df_line['PlannedDate']).dt.date
    df_grouped['index'] = pd.to_datetime(df_grouped['index']).dt.date
    df_line = df_line.merge(df_grouped, left_on='PlannedDate', right_on='index', how='inner')
    df_line['diff_Mastercases'] = df_line['CorrespondingMastercases'] - df_line['CorrespondingMastercases_mean']
    df_line['diff_Outers'] = df_line['CorrespondingOuters'] - df_line['CorrespondingOuters_mean']
    df_line['diff_Pallets'] = df_line['CorrespondingPallets'] - df_line['CorrespondingPallets_mean']
    # Abweichung Total in Prozent
    df_line['diff_Total_in%'] = (df_line['total_actual'] - df_line['total_forecast']) / df_line['total_forecast'] * 100
    df_line['diff_Total_in%'] = df_line['diff_Total_in%'].round(2)
    #abweichung in Prozent Mastercases
    df_line['diff_Mastercases_in%'] = (df_line['diff_Mastercases'] / df_line['CorrespondingMastercases_mean']) * 100
    df_line['diff_Mastercases_in%'] = df_line['diff_Mastercases_in%'].round(2)
    #abweichung in Prozent Outers
    df_line['diff_Outers_in%'] = (df_line['diff_Outers'] / df_line['CorrespondingOuters_mean']) * 100
    df_line['diff_Outers_in%'] = df_line['diff_Outers_in%'].round(2)
    #abweichung in Prozent Pallets
    df_line['diff_Pallets_in%'] = (df_line['diff_Pallets'] / df_line['CorrespondingPallets_mean']) * 100
    df_line['diff_Pallets_in%'] = df_line['diff_Pallets_in%'].round(2)
    st.dataframe(df_line)
    #st.write(df_line)
    # show barchart toatal vs total forecast
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df_line['PlannedDate'],
        y=df_line['total_actual'],
        name='Actual Total',
        text=df_line['total_actual'],
        textposition='inside',
        marker_color='black'
    ))
    fig.add_trace(go.Bar(
        x=df_line['PlannedDate'],
        y=df_line['total_forecast'],
        name='Forecast Total',
        text=df_line['total_forecast'],
        textposition='inside',
        marker_color='grey'
    ))
    fig.update_layout(
        title='Actual vs Forecast Total',
        xaxis_title='Datum',
        yaxis_title='Summe',
        barmode='group',
        legend_title='Kategorie',
        height=600,
        template='plotly_white'
    )
    st.plotly_chart(fig, use_container_width=True)


# Dashboard aufbauen
def main():
    try: 
        exestierende_forecasts = SQL.read_table('PAMS_Forecast_NEW')

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
        st.write(new_F)
        # Kombiniere mit bestehenden Daten

        save_Table_append(new_F, 'PAMS_Forecast_NEW')

        
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
    # wenn new_F exestiert dann zeige es an
    if 'new_F' in locals():
        st.success('Neue Prognose wurde erstellt und gespeichert.')
        st.write('Prognose Rohdaten:')
        st.dataframe(new_F)
    else:
        pass

    
if __name__ == "__main__":
    main()