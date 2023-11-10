
import pandas as pd
from matplotlib import pyplot as plt
import plotly.express as px
from statsmodels.tsa.statespace.sarimax import SARIMAX
import plotly.graph_objects as go

    # Load the data
def cal_forecast(df: pd.DataFrame ):

    

    # Convert timestamps to datetime objects for proper handling
    df['CreatedTimestamp'] = pd.to_datetime(df['CreatedTimestamp'])
    df['PlannedDate'] = pd.to_datetime(df['PlannedDate'])

    # 'Picks Gesamt'  to float
    df['Picks Gesamt'] = df['Picks Gesamt'].astype(float)

    # Group by PlannedDate to get the sum of 'Picks Gesamt' for each day and reindex to fill missing dates
    daily_picks = df.groupby(df['PlannedDate'].dt.date)['Picks Gesamt'].sum().reset_index()
    daily_picks['PlannedDate'] = pd.to_datetime(daily_picks['PlannedDate'])
    daily_picks.set_index('PlannedDate', inplace=True)
    full_date_range = pd.date_range(start=daily_picks.index.min(), end=daily_picks.index.max(), freq='D')
    daily_picks_reindexed = daily_picks.reindex(full_date_range, fill_value=0)

    # Fit the SARIMAX model
    sarimax_model = SARIMAX(daily_picks_reindexed['Picks Gesamt'], 
                            order=(1, 1, 1), 
                            seasonal_order=(1, 1, 1, 7),
                            enforce_stationarity=False,
                            enforce_invertibility=False)
    sarimax_result = sarimax_model.fit(disp=False)

    # Get the last two weeks of actual data for the bar chart
    last_two_weeks_ago = daily_picks_reindexed.index.max() - pd.Timedelta(days=14)
    last_two_weeks_data_bar = daily_picks_reindexed[last_two_weeks_ago:]

    # Forecast the next 2 weeks (14 days)
    sarimax_forecast = sarimax_result.get_forecast(steps=14)
    forecast_dates = pd.date_range(start=daily_picks_reindexed.index[-1] + pd.Timedelta(days=1), periods=14, freq='D')
    sarimax_forecast_values = sarimax_forecast.predicted_mean.clip(lower=0)

    fig = go.Figure()

    # Actual Picks
    for date, total in zip(last_two_weeks_data_bar.index, last_two_weeks_data_bar['Picks Gesamt']):
        day_of_week = date.strftime("%A")  # Ermittle den Wochentag
        label = f"{day_of_week}<br>{round(total, 2)}"
        fig.add_trace(go.Bar(x=[date],
                             y=[total],
                             name='Actual Picks',
                             marker_color='#0e2b63',  # Farbe anpassen
                             text=label,  # Datenbeschriftung mit Wochentag
                             hoverinfo='text'))

    # SARIMAX Forecast
    for date, total in zip(forecast_dates, sarimax_forecast_values):
        day_of_week = date.strftime("%A")  # Ermittle den Wochentag
        label = f"{day_of_week}<br>{round(total, 2)}"
        fig.add_trace(go.Bar(x=[date],
                             y=[total],
                             name='SARIMAX Forecast',
                             marker_color='#FF0000',  # Farbe anpassen
                             text=label,  # Datenbeschriftung mit Wochentag
                             hoverinfo='text'))

    fig.update_layout(title='Picks der letzten 2 Wochen und SARIMAX Forecast für die nächsten 2 Wochen',
                      xaxis_title='Date',
                      yaxis_title='Total Picks',
                      xaxis=dict(tickangle=-45),
                      barmode='group')

    # Schriftart aktualisieren
    fig.update_layout(font_family="Montserrat")
    #remove legend
    fig.update_layout(showlegend=False)

    return sarimax_forecast_values, fig

#sa

# # Save the plot as a bar chart with no negative values
# forecast_bar_chart_path = 'sarimax_forecast_bar_chart_no_neg.png'
# plt.savefig(forecast_bar_chart_path)