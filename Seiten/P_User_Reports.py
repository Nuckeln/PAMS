import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
from Data_Class.st_AgGridCheckBox import createAGgrid_withCheckbox
from Data_Class.MMSQL_connection import read_Table_by_Date
from datetime import datetime

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
    return df

def filterDate(df: pd):
    df.PlannedDate = pd.to_datetime(df.PlannedDate)
    df['Packtag'] = df.PlannedDate.dt.strftime('%d.%m.%Y')
    df['Packtag'] = df['Packtag'].astype(str)

    df['Wochentag'] = df['PlannedDate'].dt.strftime('%A')
    df['Woche'] = df['PlannedDate'].dt.strftime('%V.%Y')
    df['Monat'] = df['PlannedDate'].dt.strftime('%m.%Y')
    df.PlannedDate = df.PlannedDate.dt.strftime('%d.%m.%Y')

    col1, col2, col3 = st.columns(3)

    with col1:
        sel_filter = st.radio(
        "Filtern nach:",
        ["Monat", "Woche" ],
        key="visibility",
        horizontal=True)       

    with col2:
        if sel_filter == 'Zeitraum':
            start_date = st.date_input('Start Date')
            with col3:
                end_date = st.date_input('End Date')
            df.PlannedDate = pd.to_datetime(df.PlannedDate)

            df = df[(df['PlannedDate'] > start_date) & (df['PlannedDate'] <= end_date)]

        if sel_filter == 'Woche':
            #sort df by Woche
            dfWeek = df['Woche'].unique()
            dfWeek_sorted = sorted(dfWeek, key=lambda x: (x.split('.')[1], x.split('.')[0]), reverse=True)
            sel_weekRange = st.selectbox('Wähle Woche', dfWeek_sorted)
            df = df[df['Woche'] == sel_weekRange]

        if sel_filter == 'Monat':
            #sort df by PlannedDate acciending
            df2 = df.sort_values(by=['PlannedDate'], ascending=False)
            #select unique values in column Monat
            dfMonth = df2['Monat'].unique()
            dfMonth_sorted = sorted(dfMonth, key=lambda x: (x.split('.')[1], x.split('.')[0]), reverse=True)


            
            
            sel_monthRange = st.selectbox('Wähle Monat', dfMonth_sorted)
            df = df[df['Monat'] == sel_monthRange]

    
    
    #to datetime
    sel_day_max = df['PlannedDate'].max()
    sel_day_max = datetime.strptime(sel_day_max, '%d.%m.%Y')
    sel_day_min = df['PlannedDate'].min()
    sel_day_min = datetime.strptime(sel_day_min, '%d.%m.%Y')
    #filter dfItems by sel_day_max and sel_day_min 
    dfItems = read_Table_by_Date(sel_day_min, sel_day_max, 'PAMS_SAP_Orders_Items_LT22','PickDateTime')
#to datetime
    #dfItems['PickDateTime'] = pd.to_datetime(dfItems['PickDateTime'], format='%Y-%m-%d %H:%M:%S')  
    

#    st.write('Von', sel_day_min, 'bis', sel_day_max)
    # filter dfIssues
    col1, col2 = st.columns(2)
    with col1:
        tabelle = st.checkbox('Tabellen einblenden')
    with col2:
        sel_Day_week = st.radio("Zeige in: ", ["Tagen", "Wochen"], key="zeigeIn", horizontal=True)
    if sel_Day_week == 'Wochen':
        sel_Day_week = 'Woche'
    if sel_Day_week == 'Tagen':
        sel_Day_week = 'PlannedDate'
    return df, dfItems, tabelle, sel_Day_week


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
    st.radio('Nach:', ['Mitarbeiter', 'Lieferscheine'])
    sel = createAGgrid_withCheckbox(df, 300, 'df')
    st.write(sel)
    st.data_editor(dfItems,key='dfItems')
    # #plot by Mitarbeiter.count PickDateTime
    # fig = plt.figure(figsize=(15, 8))
    # dfItems.groupby('Name').count()['PickDateTime'].plot(kind='bar', ax=plt.gca())
    # plt.title("Picks per Minute by Planned Date")
    # plt.xlabel("Planned Week and Year")
    # plt.ylabel("Picks per Minute")
    # plt.legend(title="Categories")
    # plt.grid(True)
    # plt.xticks(rotation=45)
    # #show plot
    # st.pyplot(fig)




def pageUserReport():
    df = load_data()    
    df, dfItems,tabelle, sel_Day_week = filterDate(df)

    with st.expander("Picks Mitarbeiter",expanded=True):
        plot_User_Picks(df, dfItems)
    with st.expander("Value strean mapping",expanded=False):
        
        fig = plotAsDay(df)
        st.pyplot(fig)
        # fig = plotAsWeek(df)
        # st.pyplot(fig)
        
    if st.button('Neu Laden'):
        st.cache_data.clear()
        st.experimental_rerun()