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

def cal_data(): 

    import pandas as pd

    # dfBew.to_csv('bewegung.csv', sep=';', index=False)
    dfBew = pd.read_excel('SAP.xlsx')
    dfOrders = read_table('prod_Kundenbestellungen')
    #filter dfOrders by AllSSCCLabelsPrinted = True
    dfOrders['Picks Gesamt'] = pd.to_numeric(dfOrders['Picks Gesamt'], errors='coerce')
    dfOrders['Picks Karton'] = pd.to_numeric(dfOrders['Picks Karton'], errors='coerce')
    dfOrders['Picks Stangen'] = pd.to_numeric(dfOrders['Picks Stangen'], errors='coerce')
    dfOrders['Picks Paletten'] = pd.to_numeric(dfOrders['Picks Paletten'], errors='coerce')
    dfOrders = dfOrders[dfOrders['AllSSCCLabelsPrinted'] == 'True']
    # SapOrderNumber in dfOrders to int
    dfOrders['SapOrderNumber'] = dfOrders['SapOrderNumber'].astype(str)

    dfBew = pd.merge(dfBew, dfOrders[['SapOrderNumber','PlannedDate']],left_on='Dest.Storage Bin', right_on='SapOrderNumber',how='left')
    #change name of Colunm 11 to PickZeit
    dfBew.rename(columns={'Confirmation time':'PickZeit'}, inplace=True)
    dfBew.rename(columns={'Confirmation date':'PickDatum'}, inplace=True)
    #combine PickZeit and PickDatum to PickDateTime
    dfBew['PickDateTime'] = dfBew['PickDatum'].astype(str) + ' ' + dfBew['PickZeit'].astype(str)
    #convert PickDateTime to datetime
    dfBew['PickDateTime'] = pd.to_datetime(dfBew['PickDateTime'])
    dfBew['PlannedDate'] = pd.to_datetime(dfBew['PlannedDate'])

    import pandas as pd
    import matplotlib.pyplot as plt

    #############################
    #### Berechnung der LT22 ####
    #############################

    #---Art des Picks und Dauer des Picks Berechnen---

    # Load the csv file using semicolon as the separator
    bewegung_df = dfBew
    #filter if PlannedDate is not null
    bewegung_df = bewegung_df[bewegung_df['PlannedDate'].notnull()]
    # Sort the data by "Dest.Storage Bin" and "PickDateTime"
    bewegung_df = bewegung_df.sort_values(by=['Dest.Storage Bin', 'PickDateTime'])
    # Calculate the time difference between each row and the next row within the same "Dest.Storage Bin"
    bewegung_df['PickDuration'] = bewegung_df.groupby('Dest.Storage Bin')['PickDateTime'].diff()
    # Mark positions with more than 15 minutes difference with an "X" in a new column "Fehler"
    bewegung_df['Fehler'] = bewegung_df['PickDuration'].apply(lambda x: 'X' if x > pd.Timedelta(minutes=15) else '')
    #if Source Storage Type SN* add to new column "Art" = Karton if Source Storage Type TN* add to new column "Art" = Outher if Source Storage Type BS* or RS* add to new column "Art" = Pallet
    bewegung_df['Art'] = bewegung_df['Source Storage Type'].apply(lambda x: 'Mastercase' if x.startswith('SN') else ('Outer' if x.startswith('TN') else ('Pallet' if x.startswith('BS') or x.startswith('RS') else 'other')))
    #Create a new Column aufgrund der Art der Picks
    bewegung_df['Palette'] = bewegung_df['Art'].apply(lambda x: 1 if x == 'Pallet' else 0)
    bewegung_df['Karton'] = bewegung_df['Art'].apply(lambda x: 1 if x == 'Mastercase' else 0)
    bewegung_df['Stangen'] = bewegung_df['Art'].apply(lambda x: 1 if x == 'Outer' else 0)
    bewegung_df['Other'] = bewegung_df['Art'].apply(lambda x: 1 if x == 'other' else 0)
    #copy PickDuration to new column "PickDurationOriginal"
    bewegung_df['PickDurationOriginal'] = bewegung_df['PickDuration']
    #if PickDuration greater as 30 min replace value with 10 min 
    bewegung_df['PickDuration'] = bewegung_df['PickDuration'].apply(lambda x: pd.Timedelta(minutes=10) if x > pd.Timedelta(minutes=30) else x) 


    #------ Berechnung anreichern um Mitarbeiterklarname----

    #Daten Fehlen noch 

    #------ Upload in die Datenbank ----

    #save bewegung_df to csv


    #################################
    #### Berechnung der dfOrders ####
    #################################
    # Hier ist noch ein Fehler bewegungen_grouped ist falsch 

    bewegungen_grouped = bewegung_df.groupby(['Dest.Storage Bin','Palette','Karton','Stangen','Other'])['PickDuration'].sum().reset_index()

    merged_df = pd.merge(dfOrders, bewegungen_grouped[bewegungen_grouped['Palette'] == 1][['Dest.Storage Bin','PickDuration']],left_on='SapOrderNumber', right_on='Dest.Storage Bin',how='left')
    #rename PickDuration to PickDuration_Karton
    merged_df.rename(columns={'PickDuration': 'PickDuration_Palette'}, inplace=True)
    merged_df = pd.merge(merged_df, bewegungen_grouped[bewegungen_grouped['Karton'] == 1][['Dest.Storage Bin','PickDuration']],left_on='SapOrderNumber', right_on='Dest.Storage Bin',how='left')
    #rename PickDuration to PickDuration_Karton
    merged_df = merged_df.loc[:,~merged_df.columns.str.startswith('Dest.Storage')]
    merged_df.rename(columns={'PickDuration': 'PickDuration_Karton'}, inplace=True)
    merged_df = pd.merge(merged_df, bewegungen_grouped[bewegungen_grouped['Stangen'] == 1][['Dest.Storage Bin','PickDuration']],left_on='SapOrderNumber', right_on='Dest.Storage Bin',how='left')
    # #rename PickDuration to PickDuration_Stangen
    merged_df = merged_df.loc[:,~merged_df.columns.str.startswith('Dest.Storage')]
    merged_df.rename(columns={'PickDuration': 'PickDuration_Stangen'}, inplace=True)
    merged_df = pd.merge(merged_df, bewegungen_grouped[bewegungen_grouped['Other'] == 1][['Dest.Storage Bin','PickDuration']],left_on='SapOrderNumber', right_on='Dest.Storage Bin',how='left')
    # #rename PickDuration to PickDuration_Other
    merged_df = merged_df.loc[:,~merged_df.columns.str.startswith('Dest.Storage')]
    merged_df.rename(columns={'PickDuration': 'PickDuration_Other'}, inplace=True)

    merged_df = merged_df.loc[:,~merged_df.columns.str.startswith('Dest.Storage')]

    # Gebe die Zeitwerte nochmal in Minuten, Sekunden und Stunden an
    merged_df['PickDurationMinutes_Karton'] = pd.to_timedelta(merged_df['PickDuration_Karton']).dt.total_seconds() / 60
    merged_df['PickDurationSeconds_Karton'] = pd.to_timedelta(merged_df['PickDuration_Karton']).dt.total_seconds()
    merged_df['PickDurationHours_Karton'] = pd.to_timedelta(merged_df['PickDuration_Karton']).dt.total_seconds() / 3600 

    merged_df['PickDurationMinutes_Palette'] = pd.to_timedelta(merged_df['PickDuration_Palette']).dt.total_seconds() / 60
    merged_df['PickDurationSeconds_Palette'] = pd.to_timedelta(merged_df['PickDuration_Palette']).dt.total_seconds()
    merged_df['PickDurationHours_Palette'] = pd.to_timedelta(merged_df['PickDuration_Palette']).dt.total_seconds() / 3600

    merged_df['PickDurationMinutes_Stangen'] = pd.to_timedelta(merged_df['PickDuration_Stangen']).dt.total_seconds() / 60
    merged_df['PickDurationSeconds_Stangen'] = pd.to_timedelta(merged_df['PickDuration_Stangen']).dt.total_seconds()
    merged_df['PickDurationHours_Stangen'] = pd.to_timedelta(merged_df['PickDuration_Stangen']).dt.total_seconds() / 3600

    merged_df['PickDurationMinutes_Other'] = pd.to_timedelta(merged_df['PickDuration_Other']).dt.total_seconds() / 60
    merged_df['PickDurationSeconds_Other'] = pd.to_timedelta(merged_df['PickDuration_Other']).dt.total_seconds()
    merged_df['PickDurationHours_Other'] = pd.to_timedelta(merged_df['PickDuration_Other']).dt.total_seconds() / 3600

    # ##-- Datensatz für Plot berechnen --##



    grouped_data = merged_df.groupby(['PlannedDate'])[['Picks Karton','Picks Stangen','Picks Paletten','PickDurationMinutes_Karton','PickDurationSeconds_Karton','PickDurationMinutes_Stangen','PickDurationSeconds_Stangen','PickDurationMinutes_Palette','PickDurationSeconds_Palette','PickDurationMinutes_Other']].sum().reset_index()
    grouped_data['PicksPerMinute_Karton'] = grouped_data['Picks Karton'] / grouped_data['PickDurationMinutes_Karton']
    grouped_data['PicksPerSeconds_Karton'] = grouped_data['Picks Karton'] / grouped_data['PickDurationSeconds_Karton']
    grouped_data['PicksPerMinute_Palette'] = grouped_data['Picks Paletten'] / grouped_data['PickDurationMinutes_Palette']
    grouped_data['PicksPerSeconds_Palette'] = grouped_data['Picks Paletten'] / grouped_data['PickDurationSeconds_Palette']
    grouped_data['PicksPerMinute_Stangen'] = grouped_data['Picks Stangen'] / grouped_data['PickDurationMinutes_Stangen']
    grouped_data['PicksPerSeconds_Stangen'] = grouped_data['Picks Stangen'] / grouped_data['PickDurationSeconds_Stangen']
    return grouped_data

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

def pageUserReport():
    #data = cal_data()
    #read data
    df = pd.read_csv('data.csv', sep=';')
    st.data_editor(df)
    fig = plotAsDay(df)
    st.pyplot(fig)
    fig = plotAsWeek(df)
    st.pyplot(fig)