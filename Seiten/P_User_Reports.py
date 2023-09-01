import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

from Data_Class.SQL import read_table

# def convert_datetime_to_string(df):
#     for column in df.columns:
#         if pd.api.types.is_datetime64_any_dtype(df[column]):
#             df[column] = df[column].dt.strftime('%Y-%m-%d %H:%M:%S')
#     return df

# def convert_string_to_datetime(df, datetime_format='%Y-%m-%d %H:%M:%S'):
#     for column in df.columns:
#         if df[column].dtype == "object":
#             try:
#                 df[column] = pd.to_datetime(df[column], format=datetime_format)
#             except ValueError:
#                 print(f"Could not convert column {column} to datetime")
#                 # Wenn die Umwandlung für die gesamte Spalte nicht funktioniert, 
#                 # lassen wir die Spalte unverändert
#                 continue
#     return df
st.cache_data
def load_data():
    df = read_table('PAMS_SAP_Orders_Header_LT22')
    dfItems = read_table('PAMS_SAP_Orders_Items_LT22')  
    return df, dfItems

def plotAsDay(grouped_data: pd.DataFrame):
    grouped_data = grouped_data[grouped_data['PickDurationMinutes_Karton'].notnull()]

    grouped_by_date = grouped_data.groupby('PlannedDate').sum()[['PicksPerMinute_Karton', 'PicksPerMinute_Stangen', 'PicksPerMinute_Palette']]
    grouped_data = grouped_data[grouped_data['PickDurationMinutes_Karton'].notnull()]

    # Plot the data
    plt.figure(figsize=(15, 8))
    grouped_by_date.plot(ax=plt.gca())
    plt.title("Picks per Minute by Planned Date")
    plt.xlabel("Planned Date")
    plt.ylabel("Picks per Minute")
    plt.legend(title="Categories")
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    return plt

def plotAsWeek(grouped_data):
    # Calculate mean values for different categories grouped by PlannedDate
    grouped_data['PlannedDate'] = pd.to_datetime(grouped_data['PlannedDate'])
    grouped_data['WeekandYear'] = grouped_data['PlannedDate'].dt.strftime('%Y-%U')  # Adjusted format
    grouped_by_WeekandYear = grouped_data.groupby('WeekandYear').mean()[['PicksPerMinute_Karton']]#, 'PicksPerMinute_Stangen', 'PicksPerMinute_Palette']]
    grouped_by_WeekandYear = grouped_by_WeekandYear.reset_index()
    grouped_by_WeekandYear.set_index('WeekandYear', inplace=True)  # Set WeekandYear as index

    # Plot the data
    plt.figure(figsize=(15, 8))
    grouped_by_WeekandYear.plot(kind='bar', ax=plt.gca())  # Use 'kind' parameter to specify bar chart
    plt.title("Picks per Minute by Planned Date")
    plt.xlabel("Planned Week and Year")
    plt.ylabel("Picks per Minute")
    plt.legend(title="Categories")
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    return plt.show()

def plot_User_Picks(df, dfItems):


    st.data_editor(df,key='df')
    st.data_editor(dfItems,key='dfItems')
    

def savecal_data():
    data , bewegung_df= cal_data()
    bewegung_df.to_csv('dataBew.csv', sep=';')
    data.to_csv('data.csv', sep=';')


def pageUserReport():
    df, dfItems = load_data()
    if st.button('Berechnung'):
        savecal_data()
    

    with st.expander("Picks Mitarbeiter",expanded=True):
        plot_User_Picks(df, dfItems)
    with st.expander("Value strean mapping",expanded=False):
        
        fig = plotAsDay(df)
        st.pyplot(fig)
        fig = plotAsWeek(df)
        st.pyplot(fig)