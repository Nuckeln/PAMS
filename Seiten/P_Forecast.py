import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.arima.model import ARIMA
import matplotlib.dates as mdates
import requests

import streamlit as st
import datetime
from datetime import datetime

import matplotlib.image as mpimg
from PIL import Image 
from Data_Class.SQL import read_table, save_table_to_SQL
from Data_Class.AzureStorage import upload_file_to_blob_storage, get_blob_list, get_blob_file


def readData():
    df_Bestellungen = read_table('Prod_Kundenbestellungen')
    return df_Bestellungen
####
def save_forecast(depot_data, forecast, depot, forecast_dates,forecast_type):
    # Konvertieren Sie die Schlüssel in Strings
    actual_dict = {date.strftime('%Y-%m-%d'): value for date, value in depot_data[-14:].to_dict().items()}

    data_to_save = {
        'depot': depot,
        'actual': actual_dict,
        'forecast': forecast[:len(forecast_dates)].tolist(),  # Verwenden Sie die Länge von forecast_dates
        'forecast_dates': [date.strftime('%Y-%m-%d') for date in forecast_dates]
    }

    filename = f'{forecast_type}forecast_{depot}_{datetime.now().strftime("%Y-%m-%d")}.json'
 
    #save Json to Azure Storage
    #crate a jarson file in temp folder Data/tmp
    # with open(f'Data/tmp/{filename}', 'w') as f:
    #     json.dump(data_to_save, f)
    #upload the file to Azure Storage
    upload_file_to_blob_storage(filename, data_to_save, 'Forecast')
    #delete the file in temp folder
    #os.remove(f'Data/tmp/{filename}')
    
def forecast():
    df = readData()
    df['PlannedDate'] = pd.to_datetime(df['PlannedDate'])
    df['Picks Gesamt'] = df['Picks Gesamt'].astype(float)

    # Laden der Feiertagsdaten für Bayern
    feiertage_url = 'https://feiertage-api.de/api/?jahr=2024&nur_land=BY'
    feiertage_response = requests.get(feiertage_url)
    feiertage_data = feiertage_response.json()
    feiertage = [item['datum'] for item in feiertage_data.values()]

    # Feiertage in datetime umwandeln
    feiertage = pd.to_datetime(feiertage)

    # Ausschluss von Wochenenden und Feiertagen
    df = df[~df['PlannedDate'].isin(feiertage)]
    df['Wochentag'] = df['PlannedDate'].dt.weekday
    df = df[(df['Wochentag'] >= 0) & (df['Wochentag'] <= 4)]  # Nur Montag bis Freitag

    # Filtern nach Depots
    df = df[df['DeliveryDepot'].isin(['KNSTR', 'KNLEJ', 'KNBFE', 'KNHAJ'])]
    depot_list = df['DeliveryDepot'].unique()

    # Summe der Picks Gesamt für alle Depots berechnen
    gesamt_data = df.resample('D', on='PlannedDate').sum()['Picks Gesamt']
    gesamt_data = gesamt_data[(gesamt_data.index.dayofweek >= 0) & (gesamt_data.index.dayofweek <= 4)]
    gesamt_data_last_14 = gesamt_data[-300:]

    # Vorhersage für gesamte Picks berechnen
    model_gesamt = ARIMA(gesamt_data_last_14, order=(5,1,0))
    model_fit_gesamt = model_gesamt.fit()
    forecast_gesamt = model_fit_gesamt.forecast(steps=14)

    fig, axs = plt.subplots(len(depot_list) + 1, 1, figsize=(10, 5 * (len(depot_list) + 1)))  # +1 für die Gesamtsumme
    if len(depot_list) + 1 == 1:
        axs = [axs]

    for i, depot in enumerate(depot_list):
        depot_data = df[df['DeliveryDepot'] == depot]
        depot_data = depot_data.set_index('PlannedDate')
        depot_data = depot_data.resample('D').sum()['Picks Gesamt']
        depot_data = depot_data[(depot_data.index.dayofweek >= 0) & (depot_data.index.dayofweek <= 4)]
        depot_data_last_14 = depot_data[-14:]
        model = ARIMA(depot_data_last_14, order=(5,1,0))
        model_fit = model.fit()
        forecast = model_fit.forecast(steps=14)  # Erhöhte Schritte für die anfängliche Berechnung

        # Berechnung des gefilterten Datumsbereichs für die Vorhersage
        extended_days = 14
        extended_forecast_range = pd.date_range(start=depot_data_last_14.index[-1] + pd.Timedelta(days=1), periods=extended_days, freq='D')
        is_weekday = extended_forecast_range.weekday < 5
        filtered_forecast_range = extended_forecast_range[is_weekday][:7]

        axs[i].bar(depot_data_last_14.index, depot_data_last_14, label='Tatsächliche Picks Gesamt')
        axs[i].bar(filtered_forecast_range, forecast[:len(filtered_forecast_range)], label='Vorhergesagte Picks Gesamt')
        axs[i].set_title(f'Picks Gesamt Vorhersage für {depot}')
        axs[i].set_xlabel('Datum')
        axs[i].set_ylabel('Picks Gesamt')
        axs[i].xaxis.set_major_locator(mdates.DayLocator())
        axs[i].xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        plt.setp(axs[i].xaxis.get_majorticklabels(), rotation=90)
        axs[i].legend()
        actual_bars = axs[i].bar(depot_data_last_14.index, depot_data_last_14, label='Tatsächliche Picks Gesamt')
        forecast_bars = axs[i].bar(filtered_forecast_range, forecast[:len(filtered_forecast_range)], label='Vorhergesagte Picks Gesamt')

        for bar in actual_bars:
            axs[i].annotate(f'{bar.get_height():.0f}', (bar.get_x() + bar.get_width() / 2, bar.get_height()), textcoords="offset points", xytext=(0,3), ha='center')

        for bar in forecast_bars:
            axs[i].annotate(f'{bar.get_height():.0f}', (bar.get_x() + bar.get_width() / 2, bar.get_height()), textcoords="offset points", xytext=(0,3), ha='center')

        save_forecast(depot_data_last_14, forecast, depot, filtered_forecast_range, 'Picks_')
    gesamt_data_last_14 = gesamt_data_last_14[-14:]
    # Visualisierung für Gesamtsumme
    axs[-1].bar(gesamt_data_last_14.index, gesamt_data_last_14, label='Tatsächliche Picks Gesamt')
    axs[-1].bar(filtered_forecast_range, forecast_gesamt[:len(filtered_forecast_range)], label='Vorhergesagte Picks Gesamt')
    axs[-1].set_title('Picks Gesamt Vorhersage für alle Depots')
    axs[-1].set_xlabel('Datum')
    axs[-1].set_ylabel('Picks Gesamt')
    axs[-1].xaxis.set_major_locator(mdates.DayLocator())
    axs[-1].xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    plt.setp(axs[-1].xaxis.get_majorticklabels(), rotation=90)
    axs[-1].legend()
    actual_bars_gesamt = axs[-1].bar(gesamt_data_last_14.index, gesamt_data_last_14, label='Tatsächliche Picks Gesamt')
    forecast_bars_gesamt = axs[-1].bar(filtered_forecast_range, forecast_gesamt[:len(filtered_forecast_range)], label='Vorhergesagte Picks Gesamt')

    for bar in actual_bars_gesamt:
        axs[-1].annotate(f'{bar.get_height():.0f}', (bar.get_x() + bar.get_width() / 2, bar.get_height()), textcoords="offset points", xytext=(0,3), ha='center')

    for bar in forecast_bars_gesamt:
        axs[-1].annotate(f'{bar.get_height():.0f}', (bar.get_x() + bar.get_width() / 2, bar.get_height()), textcoords="offset points", xytext=(0,3), ha='center')

    plt.tight_layout()
    current_date = datetime.now().strftime('%Y-%m-%d')
    #save data locally in Data/appData with Pick and anctual Date in the name
    fig.savefig(f'Data/appData/forecast/Forecast_Picks_KNBFE_{current_date}.png')

def forecast_TRUCKS():
    df = readData()
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
    # ...
    # Vor der Schleife, initialisieren Sie 'df' mit den entsprechenden Spalten
    df = pd.DataFrame(columns=['DeliveryDepot', 'PlannedDate', 'UnloadingListIdentifier', 'Picks Gesamt', 'Gepackte Paletten'])

    for depot in depots:
        df1 = dfOriginal[dfOriginal['DeliveryDepot'] == depot]
        df1['Picks Gesamt'] = df1['Picks Gesamt'].astype(float)
        df1 = df1.groupby(['DeliveryDepot', 'PlannedDate']).agg({'UnloadingListIdentifier': 'nunique', 'Picks Gesamt': 'sum', 'Gepackte Paletten':'sum'}).reset_index()
        df = pd.concat([df, df1])
    
    # rename UnloadingListIdentifier to Trucks
    df = df.rename(columns={'UnloadingListIdentifier': 'Trucks'})
    df['PlannedDate'] = pd.to_datetime(df['PlannedDate'])
    df['Trucks'] = df['Trucks'].astype(float)

    # Laden der Feiertagsdaten für Bayern
    feiertage_url = 'https://feiertage-api.de/api/?jahr=2023&nur_land=BY'
    feiertage_response = requests.get(feiertage_url)
    feiertage_data = feiertage_response.json()
    feiertage = [item['datum'] for item in feiertage_data.values()]

    # Feiertage in datetime umwandeln
    feiertage = pd.to_datetime(feiertage)

    # Ausschluss von Wochenenden und Feiertagen
    df = df[~df['PlannedDate'].isin(feiertage)]
    df['Wochentag'] = df['PlannedDate'].dt.weekday
    df = df[(df['Wochentag'] >= 0) & (df['Wochentag'] <= 4)]  # Nur Montag bis Freitag

    # Filtern nach Depots
    df = df[df['DeliveryDepot'].isin(['KNSTR', 'KNLEJ', 'KNBFE', 'KNHAJ'])]
    depot_list = df['DeliveryDepot'].unique()

    fig, axs = plt.subplots(len(depot_list), 1, figsize=(10, 5 * len(depot_list)))
    if len(depot_list) == 1:
        axs = [axs]

    for i, depot in enumerate(depot_list):
        depot_data = df[df['DeliveryDepot'] == depot]
        depot_data = depot_data.set_index('PlannedDate')
        depot_data = depot_data.resample('D').sum()['Trucks']

        # Wochenenden und Feiertage aus der Analyse ausschließen
        depot_data = depot_data[(depot_data.index.dayofweek >= 0) & (depot_data.index.dayofweek <= 4)]

        depot_data_last_14 = depot_data[-14:]
        model = ARIMA(depot_data_last_14, order=(5,1,0))
        model_fit = model.fit()
        forecast = model_fit.forecast(steps=14)  # Erhöhte Schritte für die anfängliche Berechnung

        # Berechnung des gefilterten Datumsbereichs für die Vorhersage
        extended_days = 14
        extended_forecast_range = pd.date_range(start=depot_data_last_14.index[-1] + pd.Timedelta(days=1), periods=extended_days, freq='D')
        is_weekday = extended_forecast_range.weekday < 5
        filtered_forecast_range = extended_forecast_range[is_weekday][:7]

        actual_bars = axs[i].bar(depot_data_last_14.index, depot_data_last_14, label='Tatsächliche Trucks')
        forecast_bars = axs[i].bar(filtered_forecast_range, forecast[:len(filtered_forecast_range)], label='Vorhergesagte Trucks')
        axs[i].set_title(f'Trucks Vorhersage für {depot}')
        axs[i].set_xlabel('Datum')
        axs[i].set_ylabel('Trucks')

        axs[i].xaxis.set_major_locator(mdates.DayLocator())
        axs[i].xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        plt.setp(axs[i].xaxis.get_majorticklabels(), rotation=90)

        for bar in actual_bars:
            axs[i].annotate(f'{bar.get_height():.0f}', (bar.get_x() + bar.get_width() / 2, bar.get_height()), textcoords="offset points", xytext=(0,3), ha='center')

        for bar in forecast_bars:
            axs[i].annotate(f'{bar.get_height():.0f}', (bar.get_x() + bar.get_width() / 2, bar.get_height()), textcoords="offset points", xytext=(0,3), ha='center')

        axs[i].legend()
        save_forecast(depot_data_last_14, forecast, depot, filtered_forecast_range, 'Trucks_')
    plt.tight_layout()
    #save fig locally in Data/appData with Truck and anctual Date in the name

    current_date = datetime.now().strftime('%Y-%m-%d')
    import io

    # Erstellen Sie ein BytesIO-Objekt und speichern Sie das Bild darin
    image_io = io.BytesIO()
    fig.savefig(image_io, format='png')

    # Setzen Sie den Cursor des BytesIO-Objekts zurück an den Anfang
    image_io.seek(0)
    fig.savefig(f'Data/appData/forecast/Forecast_Trucks_{depot}_{current_date}.png')
    
    
def main():
    st.title("PAMS Forecast Tool")
    
    datein = get_blob_list()
    
    # filter behalte alles was mit forecast anfängt
    dates = [date for date in datein if date.startswith('Forecast')]    
    
    # behalte nur das Datum aus dem string das sind immer die letzten 10 Zeichen vor dem punkt
    dates = [date[-14:-4] for date in dates]    
    # remove duplicates
    dates = list(set(dates))
    # sort the list by Date jjjj-mm-tt
    dates = sorted(dates, reverse=True)

    col1, col2 = st.columns(2)
    with col1:
        sel_Date = st.selectbox('Select Date', dates)
        filename_1 = f'Forecast_Picks_KNBFE_{sel_Date}.png'
        filename_2 = f'Forecast_Trucks_KNHAJ_{sel_Date}.png'
        # get the images from Azure Storage
        
        
        
    with col2:
        if st.button('Berechne neues Forecast-Datenmodell'):
            with st.spinner('Datenmodell wird erstellt... ladezeit bis zu 1 Minute'):
                forecast()
                forecast_TRUCKS()
                st.balloons()
                #warte 3 sekunden
                st.success('Done!')
                #lade die Seite neu
                st.rerun()
    
    # Lade die Bilder aus dem tmp-Ordner
    img1 = Image.open(f'Data/appData/forecast/{filename_1}')
    img2 = Image.open(f'Data/appData/forecast/{filename_2}')
    # Anzeige der Bilder
    st.image(img1, caption='Picks Forecast', use_column_width=True)
    st.image(img2, caption='Trucks Forecast', use_column_width=True)
    