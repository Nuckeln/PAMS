import streamlit as st
import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
from PIL import Image
from src.st_func_Return_selectDF import sel_DataFrameAG
from datetime import datetime, date, time
import plotly.express as px

# streamlit run /Users/martinwolf/Python/IPYNB/Value_stream/Streamlit/main.py 
st.set_page_config(layout="wide", page_title="Value", page_icon="🚚",initial_sidebar_state='expanded')
st.subheader("Laufweg des Mitarbeiters pro Auftrag")

@st.cache_data
def load_DF():
    dfLager = pd.read_excel('Value_stream/Streamlit/LagerNeu.xlsx')
    dfZUgriffe = pd.read_excel('Value_stream/Streamlit/LT22April2023.XLSX')
    dfOrders = pd.read_pickle('Value_stream/Streamlit/prod_Kundenbestellungen.pkl')

    return dfLager,dfZUgriffe,dfOrders

dfLager,dfZUgriffe,dfOrders  = load_DF()
#filter df Zugriffe die ersten beiden stellen sind [Source Storage Type] == 'SN'
dfZUgriffe = dfZUgriffe[dfZUgriffe['Source Storage Type'] == 'SN1']

# dfZUgriffe = dfZUgriffe[dfZUgriffe['Picks Karton'] > 0]

# Konvertiere die 'PlannedDate'-Spalte in einen datetime-Datentyp
dfOrders['PlannedDate'] = pd.to_datetime(dfOrders['PlannedDate'])

# Filtern nach den Monaten April 2023 und August 2022
dfOrders = dfOrders[((dfOrders['PlannedDate'].dt.month == 4) & (dfOrders['PlannedDate'].dt.year == 2023)) | 
                    ((dfOrders['PlannedDate'].dt.month == 12) & (dfOrders['PlannedDate'].dt.year == 2022))]

sel_order = sel_DataFrameAG.AG_Select_Grid(dfOrders, 250, 'test')


def showPlot(sel_order, dfLager, dfZUgriffe):
    # Filtern Sie die Zugriffe
    dfZUgriffe_filtered = dfZUgriffe[dfZUgriffe['Dest.Storage Bin'] == sel_order]

    # Sortieren Sie nach Confirmation Time
    dfZUgriffe_filtered = dfZUgriffe_filtered.sort_values(by='Confirmation time.1')
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
    dfZUgriffe_filtered['Laufweg'] = range(1, len(dfZUgriffe_filtered) + 1)
    # übergebe Laufweg in dfLager
    #dfZUgriffe_filtered_sorted = dfZUgriffe_filtered.sort_values('Source Storage Bin')
    dfMerged = pd.merge(dfZUgriffe_filtered, dfLager, right_on='Stellplatz', left_on='Source Storage Bin', how='inner', suffixes=('_lager', '_zugriffe'))
    dfMerged = dfMerged.sort_values(by='Laufweg')
    img = Image.open('Value_stream/Streamlit/Lager.png')

    # Filtern Sie die Daten, um nur die besuchten Stellplätze darzustellen
    dfVisited = dfMerged
    add_value = 0

    # Sortieren nach der Spalte "Laufweg"
    dfVisited = dfVisited.sort_values('Laufweg')
    #if Stellplatz None dann ersetze mit Source Storage Bin
    dfVisited['Stellplatz'] = dfVisited['Stellplatz'].fillna(dfVisited['Source Storage Bin'])
    #suche in 'Stellplatz' nach Gangwechsel und verändere den wert in X in dem du immer bei 5 anfängst und um 5 erhöhst 
    for i in range(len(dfVisited)):
        # if the value in the 'Source Storage Bin' column contains 'Gangwechsel'
         
        
        if 'Gangwechsel' in str(dfVisited.iloc[i]['Source Storage Bin']):
            # set the value in the 'X' column to 5 plus the current value
            dfVisited.at[i, 'X'] = add_value + 7
            # increase the value by 5
            add_value += 7

    # Erstellen Sie eine Figur und Achsen mit matplotlib
    # Die Größe der Figur wird auf die Größe des Bildes in Zoll eingestellt (1 Zoll = 80 Pixel)
    fig, ax = plt.subplots(figsize=(img.size[0]/80, img.size[1]/80))

    # Entfernen Sie die Achsen
    ax.axis('off')

    # Zeigen Sie das Bild
    ax.imshow(img)

    # Zeichnen Sie jeden Punkt aus der Tabelle dfVisited und verbinden Sie sie mit Linien
    ax.plot(dfVisited['X'], dfVisited['Y'], 'ro-')  # 'ro-' steht für rote Punkte verbunden mit einer Linie

    # Fügen Sie Dreiecke hinzu, um die Laufrichtung darzustellen
    for i in range(len(dfVisited)-1):
        ax.annotate("", xy=(dfVisited['X'].values[i+1], dfVisited['Y'].values[i+1]), 
                    xytext=(dfVisited['X'].values[i], dfVisited['Y'].values[i]),
                    arrowprops=dict(arrowstyle='-|>', color='blue', lw=1.5),
                    size=20)

    # Fügen Sie den Text hinzu (rot und fett)
    for idx, row in dfVisited.iterrows():
        ax.text(row['X'], row['Y'], str(row['Laufweg']), color='red', weight='bold', fontsize=18)

    # Bearbeitungszeit ermitteln 
    #dfZUgriffe_filtered['Confirmation time.1'] = pd.to_datetime(dfZUgriffe_filtered['Confirmation time.1'])
    try:
        kleinsteZeit = datetime.combine(date.today(), dfZUgriffe_filtered['Confirmation time.1'].max())
        groessteZeit = datetime.combine(date.today(), dfZUgriffe_filtered['Confirmation time.1'].min())
        bearbeitungszeit = kleinsteZeit - groessteZeit
    except:
        bearbeitungszeit = 'Keine Daten vorhanden'
    


    return fig, dfVisited, dfLager, bearbeitungszeit

if sel_order == None:
    st.warning('Bitte wählen Sie einen Auftrag aus')
# Zeigen Sie die Figur
fig, dfVisited, dfLager, bearbeitungszeit = showPlot(sel_order, dfLager, dfZUgriffe)
# Berechnen Laufweg


# Abstand zwischen den Stellplätzen (in cm)
stellplatz_breite = 120

# Liste zur Speicherung der Wegstrecke
wegstrecke = []
# Iteriere über die Zeilen im Datenframe
for index, row in dfVisited.iterrows():
    # Berechne die Position des Stellplatzes auf der X-Achse
    x_position = row['X'] - (stellplatz_breite / 2)
    # Füge den Stellplatz zur Wegstrecke hinzu
    wegstrecke.append((x_position, row['Y']))

# Berechne die Gesamtwegstrecke
gesamt_wegstrecke = 0
for i in range(len(wegstrecke) - 1):
    x1, y1 = wegstrecke[i]
    x2, y2 = wegstrecke[i+1]
    dist = ((x2 - x1)**2 + (y2 - y1)**2)**0.5
    gesamt_wegstrecke += dist

# Ausgabe der Gesamtwegstrecke

col1, col2 = st.columns (2)
with col1:
    st.write('Gewählter Auftrag: ', sel_order)
    
with col2:
    st.write('Anzahl der Gangwechsel: ', dfVisited['Source Storage Bin'].str.contains('Gangwechsel').sum()/2)
    st.write("Die Gesamtwegstrecke beträgt:", gesamt_wegstrecke / 100, "m")
    st.write("Die Bearbeitungszeit beträgt:", bearbeitungszeit)

st.pyplot(fig)






# st.subheader('Stanzeit der Ware zwischen Vollständig Kommisioniert und Versandbereit')

# dfOrdersNew = pd.read_pickle('Value_stream/Streamlit/dfOrdersBerechnet.pkl')
# dfOrdersNew['Datum'] = pd.to_datetime(dfOrdersNew['ErstesLabel'])
# dfOrdersNew['Datum'] = dfOrdersNew['Datum'].dt.date

# # Konvertieren der Spalten in numerische Werte
# dfOrdersNew = pd.read_pickle('Value_stream/Streamlit/dfOrdersBerechnet.pkl')
# dfOrdersNew['Datum'] = pd.to_datetime(dfOrdersNew['ErstesLabel'])
# dfOrdersNew['Datum'] = dfOrdersNew['Datum'].dt.date

# # Konvertieren der Spalten in numerische Werte
# dfOrdersNew['BearbeitungszeitLabel'] = pd.to_numeric(dfOrdersNew['BearbeitungszeitLabel'], errors='coerce')
# dfOrdersNew['BearbeitungszeitPick'] = pd.to_numeric(dfOrdersNew['BearbeitungszeitPick'], errors='coerce')
# dfOrdersNew['Standzeit Ware bis erstes Label'] = pd.to_numeric(dfOrdersNew['Standzeit Ware bis erstes Label'], errors='coerce')

# # round to 2 decimals
# dfOrdersNew['BearbeitungszeitLabel'] = dfOrdersNew['BearbeitungszeitLabel'].round(2)
# dfOrdersNew['BearbeitungszeitPick'] = dfOrdersNew['BearbeitungszeitPick'].round(2)
# dfOrdersNew['Standzeit Ware bis erstes Label'] = dfOrdersNew['Standzeit Ware bis erstes Label'].round(2)

# # Gruppieren nach Datum und Berechnen der Medianwerte
# grouped = dfOrdersNew.groupby('Datum').agg({'BearbeitungszeitLabel': 'sum', 'BearbeitungszeitPick': 'sum', 'Standzeit Ware bis erstes Label': 'sum'})


# # erstelle ein plotly express Line Chart
# fig = px.line(grouped, x=grouped.index, y=['BearbeitungszeitLabel', 'BearbeitungszeitPick', 'Standzeit Ware bis erstes Label'], title='Bearbeitungszeit der Aufträge')
# fig.update_layout(
#     xaxis_title="Datum",
#     yaxis_title="Zeit in Minuten",
#     legend_title="Legende",
#     font=dict(
#         family="Courier New, monospace",
#         size=12,
#         color="RebeccaPurple"
#     )
# )
# fig.update_xaxes(rangeslider_visible=True)
# st.plotly_chart(fig,use_container_width=True)

st.dataframe(dfVisited)