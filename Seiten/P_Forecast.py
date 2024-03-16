import streamlit as st
import pandas as pd
import numpy as np
import datetime
import streamlit_autorefresh as sar
from PIL import Image
import plotly_express as px
import plotly.graph_objects as go

from Data_Class.cal_forecast import cal_forecast
from Data_Class.wetter.api import getWetterBayreuth
from Data_Class.SQL import read_table
import matplotlib.pyplot as plt
import matplotlib.pyplot as plt
from statsmodels.tsa.arima.model import ARIMA


def readData():
    df_Bestellungen = read_table('Prod_Kundenbestellungen')
    return df_Bestellungen
####
## Im vorhersagemodell ist ein Fehler Feiertage und Wochenenden in Bayern Deutschland werden nicht berücksichtigt in der Zukunft


def forecast():
    df = readData()
    #st.data_editor(df)

    # Datentyp der 'PlannedDate' Spalte konvertieren


    # Datentyp der 'PlannedDate' Spalte konvertieren
    df['PlannedDate'] = pd.to_datetime(df['PlannedDate'])
    df['Picks Gesamt'] = df['Picks Gesamt'].astype(float)
    # filter depots = ['KNSTR', 'KNLEJ', 'KNBFE', 'KNHAJ']
    df = df[df['DeliveryDepot'].isin(['KNSTR', 'KNLEJ', 'KNBFE', 'KNHAJ'])]
    # Eindeutige Depots
    depot_list = df['DeliveryDepot'].unique()

    # Visualisierung vorbereiten
    fig, axs = plt.subplots(len(depot_list), 1, figsize=(10, 5 * len(depot_list)))

    if len(depot_list) == 1:
        axs = [axs]  # Einzelnen Plot in Liste umwandeln für Konsistenz

    def add_labels(ax, bars):
        for bar in bars:
            height = bar.get_height()
            ax.annotate(f'{height:.0f}',
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3),  # 3 Punkte vertikaler Offset
                        textcoords="offset points",
                        ha='center', va='bottom')

    for i, depot in enumerate(depot_list):
        # Daten für das aktuelle Depot filtern
        depot_data = df[df['DeliveryDepot'] == depot]
        depot_data = depot_data.set_index('PlannedDate')
        depot_data = depot_data.resample('D').sum()['Picks Gesamt']  # Tägliche Summation

        # Beschränkung auf die Tage mit verfügbaren Daten (ohne Wochenenden und Feiertage)
        depot_data = depot_data[depot_data.index.dayofweek < 5]  # Filtert Tage von Montag bis Freitag

        # Beschränkung auf die letzten 14 Tage
        depot_data_last_14 = depot_data[-14:]

        # ARIMA-Modell erstellen und anpassen
        model = ARIMA(depot_data_last_14, order=(5,1,0))
        model_fit = model.fit()

        # Vorhersage für die nächsten 7 Tage
        forecast = model_fit.forecast(steps=7)

        # Plotting
        actual_bars = axs[i].bar(depot_data_last_14.index, depot_data_last_14, label='Tatsächliche Picks Gesamt')
        forecast_bars = axs[i].bar(pd.date_range(start=depot_data_last_14.index[-1], periods=8, freq='D')[1:], forecast, label='Vorhergesagte Picks Gesamt')
        axs[i].set_title(f'Picks Gesamt Vorhersage für {depot}')
        axs[i].set_xlabel('Datum')
        axs[i].set_ylabel('Picks Gesamt')

        add_labels(axs[i], actual_bars)
        add_labels(axs[i], forecast_bars)

        axs[i].legend()

    plt.tight_layout()
    plt.show()
        # st.pyplot(fig)  # Streamlit plot anzeigen, falls benötigt

    st.pyplot(fig)


def main():
    st.title("PAMS Forecast Tool")
    with st.spinner('Datenmodell wird gelesen...'):
        forecast()
    st.success('Done!')