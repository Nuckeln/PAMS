import pandas as pd
import numpy as np
import datetime
import plotly.graph_objects as go
import streamlit as st

from ipyvizzu import Chart, Data, Config, Style
from streamlit_vizzu import VizzuChart
st.set_page_config(layout="wide", page_title="test ipyvizu", page_icon=":bar_chart:",)

#    streamlit run "/Library/Python_local/Superdepot Reporting/ipvizzuuu.py"


def calculate_and_plot_cumulative_picks(df):
    # Laden der Daten
    data = df

    # Umwandeln der 'Fertiggestellt' Spalte in datetime
    data['Fertiggestellt'] = pd.to_datetime(data['Fertiggestellt'])

    # Kombinieren der relevanten Picks-Spalten und Berechnung der Summe
    picks_columns = ['Picks Karton fertig', 'Picks Paletten fertig', 'Picks Stangen fertig']
    data['Total Picks'] = data[picks_columns].sum(axis=1, skipna=True)

    # Daten nach 'Fertiggestellt' sortieren
    data.set_index('Fertiggestellt', inplace=True)
    data.sort_index(inplace=True)

    # Berechnung der kumulativen Summe der Picks
    data['Cumulative Picks'] = data['Total Picks'].cumsum()

    # Visualisierung der kumulativen Summe
    # plt.figure(figsize=(12, 6))
    # data['Cumulative Picks'].plot(kind='line')
    # plt.title('Kumulative Summe der Picks über die Zeit')
    # plt.xlabel('Zeitpunkt der Fertigstellung')
    # plt.ylabel('Kumulative Summe der Picks')
    # plt.grid(True)
    # plt.show()
    return data
    
def main():
    st.title('Kumulative Picks über die Zeit')
    df = pd.read_csv('dfOr.csv')
    df.loc[df['DeliveryDepot'] == 'KNSTR']
    # Aufrufen der Funktion mit dem Pfad zur Datei
    df = calculate_and_plot_cumulative_picks(df)
    st.write('Hallo')
    # behalte nur Feritggestellt und Cumulative Picks
    df = df[['Cumulative Picks']]
    # erstelle spalte Date aus index
    df['Date'] = df.index
    #reset index
    df.reset_index(drop=True, inplace=True)

    # Create a VizzuChart object with the default height and width
    chart = VizzuChart()
    # Generate some data and add it to the chart
    data = Data()
    chart.animate(data)

    # Add some configuration to tell Vizzu how to display the data
    chart.animate(Config({"x": "Date", "title": "Look at my plot!"}))

    # Show the chart in the app!
    chart.show()
    
if __name__ == '__main__':  
    main()