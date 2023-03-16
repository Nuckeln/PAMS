from Data_Class.SQL import SQL_TabellenLadenBearbeiten as sql
import pandas as pd
from sklearn.linear_model import LinearRegression
from statsmodels.tsa.holtwinters import ExponentialSmoothing

dfOr = sql.sql_datenTabelleLaden('prod_Kundenbestellungen')

# drop all other columns they not PickingDate and PicksGesamt
df = dfOr[['PlannedDate', 'Picks Gesamt']]
# rename columns PlannedDate and PicksGesamt to Datum and Bestellungen
df = df.rename(columns={'PlannedDate': 'Datum', 'Picks Gesamt': 'Bestellungen'})
# group by Datum and sum Bestellungen
df = df.groupby('Datum').sum()
print(df)

df.index = pd.to_datetime(df.index)

# Filtere die Daten auf den April des letzten Jahres
df_last_year = df.loc['2022-04-01':'2022-04-30']

# Berechne den durchschnittlichen täglichen Bestellwert
df_last_year['Tag'] = df_last_year.index.day
daily_avg = df_last_year.groupby('Tag')['Bestellungen'].mean()

# Erstelle ein Holt-Winters-Modell und trainiere es auf den historischen Daten
model = ExponentialSmoothing(daily_avg, seasonal_periods=7, trend='add', seasonal='add')
model_fit = model.fit()

# Erstelle ein DataFrame mit allen Tagen im April dieses Jahres
dates = pd.date_range(start='2023-04-01', end='2023-04-30', freq='D')
df_next_month = pd.DataFrame({'Tag': dates.day})
df_next_month.set_index('Tag', inplace=True)

# Füge eine Spalte hinzu, die die Vorhersagen enthält
y_pred = model_fit.predict(start=0, end=29)
df_next_month['Vorhersage'] = y_pred

# Gib das Ergebnis aus
print(df_next_month)
