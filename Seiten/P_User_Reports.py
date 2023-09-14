import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import streamlit as st
from Data_Class.st_AgGridCheckBox import AG_Select_Grid
from Data_Class.MMSQL_connection import read_Table_by_Date
from Data_Class.st_int_to_textbox import checkboxes_in_Col
from datetime import datetime
from PIL import Image

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
    df['Picks Gesamt'] = df['Picks Karton'] + df['Picks Stangen'] + df['Picks Paletten']
    df.PlannedDate = pd.to_datetime(df.PlannedDate)
    df['Packtag'] = df.PlannedDate.dt.strftime('%d.%m.%Y')
    df['Packtag'] = df['Packtag'].astype(str)

    df['Wochentag'] = df['PlannedDate'].dt.strftime('%A')
    df['Woche'] = df['PlannedDate'].dt.strftime('%V.%Y')
    df['Monat'] = df['PlannedDate'].dt.strftime('%m.%Y')
    df.PlannedDate = df.PlannedDate.dt.strftime('%d.%m.%Y')
    dfWeek = df['Woche'].unique()
    dfWeek_sorted = sorted(dfWeek, key=lambda x: (x.split('.')[1], x.split('.')[0]), reverse=True)
    df2 = df.sort_values(by=['PlannedDate'], ascending=False)
    #select unique values in column Monat
    dfMonth = df2['Monat'].unique()
    dfMonth_sorted = sorted(dfMonth, key=lambda x: (x.split('.')[1], x.split('.')[0]), reverse=True)

    return df, dfWeek_sorted, dfMonth_sorted

def filterDateUI(df: pd,dfWeek_sorted: list, dfMonth_sorted: list):

    start_date = None
    end_date = None
    sel_weekRange = None
    sel_monthRange = None
    col1, col2, col3 = st.columns(3)

    with col1:
        sel_filter = st.radio(
        "Filtern nach:",
        ["Woche","Monat",'Zeitraum' ],
        key="visibility",
        horizontal=True)       

    with col2:
        if sel_filter == 'Zeitraum':
            start_date = st.date_input('Start Date')
            with col3:
                end_date = st.date_input('End Date')

        if sel_filter == 'Woche':

            #sort df by Woche
            sel_weekRange = st.selectbox('Wähle Woche', dfWeek_sorted)


        if sel_filter == 'Monat':
            #sort df by PlannedDate acciending  
            sel_monthRange = st.selectbox('Wähle Monat', dfMonth_sorted)

    col1, col2 = st.columns(2)
    with col1:
        tabelle = st.checkbox('Tabellen einblenden')
    with col2:
        sel_Day_week = st.radio("Zeige in: ", ["Tagen", "Wochen"], key="zeigeIn", horizontal=True)
    if sel_Day_week == 'Wochen':
        sel_Day_week = 'Woche'
    if sel_Day_week == 'Tagen':
        sel_Day_week = 'PlannedDate'

    
    
    return sel_filter, start_date, end_date, sel_weekRange, sel_monthRange, tabelle, sel_Day_week
st.cache_data
def filter_dataframe(df: pd, sel_filter: str, start_date: str, end_date: str, sel_weekRange: str, sel_monthRange: str):

    if sel_filter == 'Zeitraum':
        #df.PlannedDate = pd.to_datetime(df.PlannedDate)
        #start_date to string
        start_date = start_date.strftime('%d.%m.%Y')

        #end_date to datetime
        end_date = end_date.strftime('%d.%m.%Y')

        df = df[(df['PlannedDate'] > start_date) & (df['PlannedDate'] <= end_date)]
        
    if sel_filter == 'Woche':
        #sort df by Woche
        df = df[df['Woche'] == sel_weekRange]

    if sel_filter == 'Monat':
        #sort df by PlannedDate acciending  
        df = df[df['Monat'] == sel_monthRange]



    #to datetime
    sel_day_max = df['PlannedDate'].max()
    sel_day_max = datetime.strptime(sel_day_max, '%d.%m.%Y')
    sel_day_min = df['PlannedDate'].min()
    sel_day_min = datetime.strptime(sel_day_min, '%d.%m.%Y')
    #filter dfItems by sel_day_max and sel_day_min 
    dfItems = read_Table_by_Date(sel_day_min, sel_day_max, 'PAMS_SAP_Orders_Items_LT22','PickDateTime')
    #drop rows with Fachbereich == nan
    dfItems = dfItems[dfItems['Fachbereich'] != 'nan']
    dfOrders = read_Table_by_Date(sel_day_min, sel_day_max, 'Prod_Kundenbestellungen','PlannedDate')


    return df, dfItems, dfOrders

def value_plotAsDay(grouped_data: pd.DataFrame):
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

def value_plotAsWeek(grouped_data):
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
    #st.write(sel)
    #st.data_editor(dfItems,key='dfItemsds')
    dfItems = dfItems[dfItems['Source target qty'].astype(float) > 0]
    dfItems['Source target qty'] = dfItems['Source target qty'].astype(float)
    dfItems['OUT'] = dfItems['OUT'].astype(float)
    dfItems['CS'] = dfItems['CS'].astype(float)
    dfItems['PAL'] = dfItems['PAL'].astype(float)

    dfItems['In_Karton'] = dfItems.apply(
    lambda row: (row['Source target qty'] * row['OUT']) / row['CS'] 
    if (row['Alternative Unit of Measure'] == 'OUT' and row['Art'] == 'Mastercase') 
    else None, 
    axis=1
    )
    #if none then 0
    dfItems['In_Karton'] = dfItems['In_Karton'].fillna(0)
    dfItems['In_PAL'] = dfItems.apply(
    lambda row: (row['Source target qty'] * row['OUT']) / row['PAL'] 
    if (row['Alternative Unit of Measure'] == 'OUT' and row['Art'] == 'Pallet')
    else None, 
    axis=1
    )
    #if none then 0
    dfItems['In_PAL'] = dfItems['In_PAL'].fillna(0)
    
    dfItems.loc[(dfItems['Art'] == 'Outer') & (dfItems['Alternative Unit of Measure'] == 'OUT'), 'In_Stangen'] = dfItems['Source target qty']
    dfItems['In_Stangen'] = dfItems['In_Stangen'].fillna(0)
    #sum of all to PickQty
    dfItems['PickQty'] = dfItems['In_Karton'] + dfItems['In_PAL'] + dfItems['In_Stangen']


    # str PickDateTime to string YYYY-MM-DD
    dfItems['PickDate'] = dfItems['PickDateTime'].str[:10]

    #plot PickQty by Mitarbeiter per PickDateTime
    
    dfItems_grouped = dfItems.groupby(['PickDate', 'Name']).sum()[['PickQty','In_Karton', 'In_PAL', 'In_Stangen']]

    title = ''#"<b>Picks nach Katergorie: </b> <span style='color:#ef7d00'>Stangen</span> / <span style='color:#0F2B63'>Karton</span> / <span style='color:#4FAF46'>Paletten</span>"

    fig_dfItems_grouped = px.bar(dfItems_grouped, x=dfItems_grouped.index.get_level_values(0), y=dfItems_grouped['PickQty'], color=dfItems_grouped.index.get_level_values(1), title=title, barmode='stack')
    # fig_dfItems_grouped.update_layout(
    #     xaxis_title="Datum",
    #     yaxis_title="Picks",
    #     font_family="Montserrat",
    #     font_color="#0F2B63",
    #     title_font_family="Montserrat",
    #     title_font_color="#0F2B63",
    #     legend_title_font_color="#0F2B63",
    #     legend_title_text='Mitarbeiter',
    #     legend=dict(
    #         orientation="h",
    #         yanchor="bottom",
    #         y=1.02,
    #         xanchor="right",
    #         x=1
    #     ),
    #     showlegend=True
    # )
    # fig_dfItems_grouped.update_traces(marker_color='#0F2B63', selector=dict(name='In_Karton'))
    # fig_dfItems_grouped.update_traces(marker_color='#4FAF46', selector=dict(name='In_PAL'))
    # fig_dfItems_grouped.update_traces(marker_color='#ef7d00', selector=dict(name='In_Stangen'))
    # fig_dfItems_grouped.layout.xaxis.tickangle = 70
    st.plotly_chart(fig_dfItems_grouped, use_container_width=True,config={'displayModeBar': False})






    st.dataframe(dfItems_grouped)

    st.data_editor(dfItems,key='dfItems')
    

def laufweg_showPlot(sel_order, dfLager, dfZUgriffe):
    dfZUgriffe = dfZUgriffe[dfZUgriffe['Source Storage Type'] == 'SN1']
    dfZUgriffe_filtered = dfZUgriffe[dfZUgriffe['Dest.Storage Bin'] == sel_order]
    dfZUgriffe_filtered = dfZUgriffe_filtered.sort_values(by='Confirmation time.1')
    #reset index
    dfZUgriffe_filtered = dfZUgriffe_filtered.reset_index(drop=True)
    try:
        st.subheader('Lagerzugriffe für Storage section SN1 in DN: '+sel_order)
    except:
        pass
    st.dataframe(dfZUgriffe_filtered,height=250)

    def gangwechsel(df):
        # Create an empty list to store the new rows
        new_rows = []

        # Iterate over each row in the original dataframe
        for i in range(len(df)):
            # Append the current row to the new_rows list
            new_rows.append(df.iloc[i].tolist())

            # Check if we are not at the last row
            if i != len(df)-1:
                # Get the current and next 'Stellplatz' values
                curr_stellplatz = df.iloc[i]['Source Storage Bin'][:3]
                next_stellplatz = df.iloc[i+1]['Source Storage Bin'][:3]

                # If the current 'Stellplatz' is not equal to the next one
                if curr_stellplatz != next_stellplatz:
                    # Copy the current row
                    new_row1 = df.iloc[i].tolist()

                    # Replace the 'Source Storage Bin' value with 'Gangwechsel'
                    new_row1[df.columns.get_loc('Source Storage Bin')] = 'Gangwechsel ' + curr_stellplatz[2:]

                    # Append the new row to the new_rows list
                    new_rows.append(new_row1)

                    # Copy the next row
                    new_row2 = df.iloc[i+1].tolist()

                    # Replace the 'Source Storage Bin' value with 'Gangwechsel'
                    new_row2[df.columns.get_loc('Source Storage Bin')] = 'Gangwechsel ' + next_stellplatz[2:]

                    # Append the new row to the new_rows list
                    new_rows.append(new_row2)

        # Convert the list of new rows to a dataframe
        new_df = pd.DataFrame(new_rows, columns=df.columns)

        return new_df

    
    # Fügen Sie die Spalte Laufweg hinzu
    dfZUgriffe_filtered   = gangwechsel(dfZUgriffe_filtered)

    # übergebe Laufweg in dfLager
    #dfZUgriffe_filtered_sorted = dfZUgriffe_filtered.sort_values('Source Storage Bin')
    dfZUgriffe_filtered['Laufweg'] = range(1, len(dfZUgriffe_filtered) + 1)
    # suche Source Storage Bin' in dfLager und übergebe Stellplatz, X, Y

        # Search for 'Source Storage Bin' in dfLager and retrieve 'Stellplatz', 'X', 'Y'
    dfLager['Stellplatz'] = dfLager['Stellplatz'].astype(str)  # Convert 'Stellplatz' to string for comparison
    dfZUgriffe_filtered['Stellplatz'] = dfZUgriffe_filtered['Source Storage Bin'].apply(
        lambda x: dfLager.loc[dfLager['Stellplatz'] == x, 'Stellplatz'].values[0] if x in dfLager['Stellplatz'].values else 'Regalgang'
    )
    dfZUgriffe_filtered['X'] = dfZUgriffe_filtered['Source Storage Bin'].apply(
        lambda x: dfLager.loc[dfLager['Stellplatz'] == x, 'X'].values[0] if x in dfLager['Stellplatz'].values else np.nan
    )
    dfZUgriffe_filtered['Y'] = dfZUgriffe_filtered['Source Storage Bin'].apply(
        lambda x: dfLager.loc[dfLager['Stellplatz'] == x, 'Y'].values[0] if x in dfLager['Stellplatz'].values else np.nan
    )
    dfZUgriffe_filtered['X'] = dfZUgriffe_filtered['X'].fillna(0)
    dfZUgriffe_filtered['Y'] = dfZUgriffe_filtered['Y'].fillna(0)

    


# Führe den Sverweis durch
    #dfMerged = pd.merge(dfZUgriffe_filtered, dfLager, how='left', left_on='Source Storage Bin', right_on='Stellplatz')
    dfVisited = dfZUgriffe_filtered
    #dfVisited['Stellplatz'] = dfVisited['Stellplatz'].fillna(dfVisited['Source Storage Bin'])
    dfVisited = dfVisited.sort_values('Laufweg')

    img = Image.open('Data/appData/Lager.png')
    
    #suche in 'Stellplatz' nach Gangwechsel und verändere den wert in X in dem du immer bei 5 anfängst und um 5 erhöhst 
    add_value = 0
    count = 1
    dfVisited['Datapoints'] = ""
    for i in range(len(dfVisited)):
        # if the value in the 'Source Storage Bin' column contains 'Gangwechsel'
        if 'Gangwechsel' in str(dfVisited.iloc[i]['Source Storage Bin']):
            # set the value in the 'X' column to 5 plus the current value
            #dfVisited.at[i, 'X'] = add_value + 1
            dfVisited.at[i, 'Datapoints'] = 0
            # increase the value by 5
            add_value += 1
    
    for i in range(len(dfVisited)):
        # if the value in the 'Source Storage Bin' column contains 'Gangwechsel'
        if dfVisited.at[i, 'Datapoints'] == "":
                dfVisited.at[i, 'Datapoints'] = count
                count += 1
        
            


    dfVisited = dfVisited.sort_values('Laufweg')
    # Erstellen Sie eine Figur und Achsen mit matplotlib
    # Die Größe der Figur wird auf die Größe des Bildes in Zoll eingestellt (1 Zoll = 80 Pixel)
    fig, ax = plt.subplots(figsize=(img.size[0]/80, img.size[1]/80))

    # Entfernen Sie die Achsen
    ax.axis('off')
    # Zeigen Sie das Bild
    ax.imshow(img)
    ax.plot(dfVisited['X'], dfVisited['Y'], 'ro-')  # 'ro-' steht für rote Punkte verbunden mit einer Linie

    # Fügen Sie Dreiecke hinzu, um die Laufrichtung darzustellen

    for i in range(len(dfVisited)-1):
        ax.annotate("", xy=(dfVisited['X'].values[i+1], dfVisited['Y'].values[i+1]), 
                    xytext=(dfVisited['X'].values[i], dfVisited['Y'].values[i]),
                    arrowprops=dict(arrowstyle='-|>', color='blue', lw=1.5),
                    size=20)
    # Durchnummeren von Datapoints is not 0 
    for idx, row in dfVisited.iterrows():
        if row['Datapoints'] != 0:
            ax.text(row['X'], row['Y'], str(row['Datapoints']), color='Black', weight='bold', fontsize=20)
    # Bearbeitungszeit ermitteln 
    dfZUgriffe_filtered['Confirmation time.1'] = pd.to_datetime(dfZUgriffe_filtered['Confirmation time.1'])
    try:
        kleinsteZeit =  dfZUgriffe_filtered['Confirmation time.1'].max()
        groessteZeit = dfZUgriffe_filtered['Confirmation time.1'].min()
        bearbeitungszeit = kleinsteZeit - groessteZeit
    except:
        bearbeitungszeit = 'Keine Daten vorhanden'
    

    
    return fig, dfVisited, dfLager, bearbeitungszeit




def pageUserReport():
    #Daten Laden
    check = False
    df,dfWeek_sorted, dfMonth_sorted = load_data() 
    
    #Filter UI erstellen und dataframes nach Datum filtern
    sel_filter, start_date, end_date, sel_weekRange, sel_monthRange, tabelle, sel_Day_week = filterDateUI(df,dfWeek_sorted, dfMonth_sorted)
    df, dfItems,dfOrders = filter_dataframe(df, sel_filter, start_date, end_date, sel_weekRange, sel_monthRange)

    # Trennlinie darstellen  
    img_strip = Image.open('Data/img/strip.png')   
    img_strip = img_strip.resize((1000, 15))     
    st.image(img_strip, use_column_width=True, caption='',)     
    # Selection des Anzeigemodus
    col1, col2 = st.columns(2)
    with col1:
        sel_view_MA_DN = st.radio('Filter nach:', ['Mitarbeiter', 'Laufweg','value stream'],horizontal=True)
    with col2:
        sel_all = st.checkbox('Alle auswählen')
    
    # Form Checkboxen für Mitarbeiter erstellen 
    if sel_view_MA_DN == 'Mitarbeiter':
        with st.form(key='form_MA'):
                dfItems_MA = dfItems[['Name', 'User.1']].drop_duplicates()
                sel_mitarbeiter = checkboxes_in_Col(dfItems_MA, 'Name', sel_all, 'MA'  )
                #filter dfItems by sel_mitarbeiter  
                dfItems = dfItems[dfItems['Name'].isin(sel_mitarbeiter)]      
                check =  st.form_submit_button(label='Anzeigen')
    if sel_view_MA_DN == 'Laufweg':
        sel_order = AG_Select_Grid(dfOrders, 200, 'DN')
        dfLager = pd.read_excel('Data/appData/LagerNeu.xlsx')
        laufweg_showPlot(sel_order, dfLager, dfItems)
    if sel_view_MA_DN == 'value stream':
        fig = value_plotAsDay(df)
        st.pyplot(fig)
        fig = value_plotAsDay(df)
        st.pyplot(fig)
        
    if check == True:
        try:
            plot_User_Picks(df, dfItems)
        except:
            st.error('Keine Daten vorhanden')





    if st.button('Daten vom Server neu laden'):
        st.cache_data.clear()
        #rerun page
        st.experimental_rerun()
