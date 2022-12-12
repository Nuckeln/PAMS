from distutils.log import info
from email.header import Header
from enum import unique
from itertools import count
import datetime
from folium import Tooltip
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from requests import head
import streamlit as st
from PIL import Image
import altair as alt
import plotly.express as px
import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, LSTM

class Forecast:

    def __init__(self):
        self.LadeForecast()

        
#         def LadeForecast(self):
            
#             st.header("Forecast")
#             st.write("Hier kannst du sehen wie sich die Daten entwickeln")
#             st.write("Datenzeitraum ab 01.04.2022")
#             df = pd.read_csv('Data/valid.csv', sep=';')
#             #rename columns
#             df = df.rename(columns={'Unnamed: 0': 'Date'})
#             df = df[-15:]
#             #df Picks Gesamt to int
#             df['Picks Gesamt'] = df['Picks Gesamt'].astype(int)
#             df['Predictions'] = df['Predictions'].astype(int)


#             # create pltoly figure of df by Date bar1 is Picks Gesamt Bar2 is Predictions
#             fig = go.Figure()
#             fig.add_trace(go.Bar(x=df['Date'], y=df['Picks Gesamt'], name='Picks Gesamt'))
#             fig.add_trace(go.Bar(x=df['Date'], y=df['Predictions'], name='Predictions'))
#             fig.update_layout(barmode='group')
#             st.plotly_chart(fig)
#             df['Abweichung'] = (1 - (df ['Predictions'] / df ['Picks Gesamt'])) * 100
#             #df['Abweichung'] in %
#             df['Abweichung'] = df['Abweichung'].round(2)
#             # create pltoly figure of df by Date bar1 is Picks Gesamt Bar2 is Predictions and line is Abweichung on top
#             fig = go.Figure()
#             fig.add_trace(go.Bar(x=df['Date'], y=df['Picks Gesamt'], name='Picks Gesamt'))
#             fig.add_trace(go.Bar(x=df['Date'], y=df['Predictions'], name='Predictions'))
#             fig.add_trace(go.Scatter
#             (x=df['Date'], y=df['Abweichung'], name='Abweichung', line=dict(color='firebrick', width=4)))
#             fig.update_layout(barmode='group')
#             st.plotly_chart(fig)
#             # create pltoly figure of df by Date line is Abweichung
#             fig = go.Figure()
#             fig.add_trace(go.Scatter
#             (x=df['Date'], y=df['Abweichung'], name='Abweichung', line=dict(color='firebrick', width=4, dash='dot')))
#             st.plotly_chart(fig)

#             # create pltoly figure of df by Date line is Abweichung

            
#             st.dataframe(df)

#         def forecast_berechen():

# df = dfPicks[['Pick Datum','Picks Gesamt']]
# df.index = df['Pick Datum']
# del df['Pick Datum']
# test_days = 20

# picksProTag = df.filter(['Picks Gesamt'])
# picksProTag = picksProTag.append(pd.DataFrame({'Picks Gesamt': [0,0,0,0,0]}, index=[picksProTag.index[-1] + pd.DateOffset(days=x) for x in range(1,6)]))
# picksProTag_data = picksProTag.values

# import math

# training_len = math.ceil(len(picksProTag) * 0.8)

# scaler = MinMaxScaler(feature_range=(0,1))
# scaled_data = scaler.fit_transform(picksProTag_data)
# train_data = scaled_data[:training_len]
# train_data.shape
# x_train = []
# y_train = []

# for i in range (test_days, len(train_data)):
#     x_train.append(train_data[i- test_days:i])
#     y_train.append(train_data[i])

# x_train, y_train = np.array(x_train), np.array(y_train)
# x_train = np.reshape(x_train, (x_train.shape[0], x_train.shape[1], 1))
# x_train.shape

# model = Sequential()
# model.add(LSTM(32, return_sequences=True, input_shape=(x_train.shape[1], 1)))
# model.add(LSTM(32, return_sequences=False))
# model.add(Dense(16))
# model.add(Dense(1))

# model.compile(optimizer='adam', loss='mean_squared_error')
# # die Epochen legen die Durchläufe fest
# model.fit(x_train, y_train, batch_size=1, epochs=40)

# test_data = scaled_data[training_len - test_days: , :]
# x_test = []
# y_test = picksProTag_data[training_len:, :]

# for i in range (test_days, len(test_data)):
#     x_test.append(test_data[i- test_days:i])
# x_test = np.array(x_test)
# x_test = np.reshape(x_test, (x_test.shape[0], x_test.shape[1], 1))

# predictions = model.predict(x_test)
# predictions = scaler.inverse_transform(predictions)

# rmse = np.sqrt(np.mean(predictions - y_test)**2)
# train = picksProTag[:training_len]
# valid = picksProTag[training_len:]
# valid['Predictions'] = predictions