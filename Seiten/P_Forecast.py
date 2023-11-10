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

def readData():
    df_Bestellungen = read_table('Prod_Kundenbestellungen')
    return df_Bestellungen


def main():
    df = readData()
    st.title("Forecast Tool")
    # SARIMAX
    # Wenn es in (https://towardsdatascience.com/time-series-forecasting-with-arima-sarima-and-sarimax-ee61099e78f6)


    df_ForeCast, fig_forecast = cal_forecast(df)
    st.plotly_chart(fig_forecast, use_container_width=True)
    st.write('Die Daten werden mittels eines SARIMAX-Modells ermittelt, wer sich dafür interesiert kann sich hier einlesen: https://towardsdatascience.com/time-series-forecasting-with-arima-sarima-and-sarimax-ee61099e78f6')
    st.write(df_ForeCast)
