import streamlit as st
import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
from PIL import Image
from Data_Class.st_func_Return_selectDF import sel_DataFrameAG
from Data_Class.SQL_Neu import read_table
from datetime import datetime, date, time
import plotly.express as px


def pageLaufwegDN():
    # streamlit run /Users/martinwolf/Python/IPYNB/Value_stream/Streamlit/main.py 
    #st.set_page_config(layout="wide", page_title="Value", page_icon="🚚",initial_sidebar_state='expanded')
    st.subheader("Laufweg des Mitarbeiters pro Auftrag")

    @st.cache_data
    def load_DF():
        dfLager = pd.read_excel('Data/appData/LagerNeu.xlsx')
        dfZUgriffe = read_table('SAP_lt22')
        dfOrders = read_table('prod_Kundenbestellungen')

        return dfLager,dfZUgriffe,dfOrders

    dfLager,dfZUgriffe,dfOrders  = load_DF()
    #filter df Zugriffe die ersten beiden stellen sind [Source Storage Type] == 'SN'
    dfZUgriffe = dfZUgriffe[dfZUgriffe['Source Storage Type'] == 'SN1']
    # Konvertiere die 'PlannedDate'-Spalte in einen datetime-Datentyp
    dfOrders['PlannedDate'] = pd.to_datetime(dfOrders['PlannedDate'])
    # Filtern nach den Monaten April 2023 und August 2022
    dfOrders = dfOrders[((dfOrders['PlannedDate'].dt.month == 4) & (dfOrders['PlannedDate'].dt.year == 2023)) | 
                        ((dfOrders['PlannedDate'].dt.month == 12) & (dfOrders['PlannedDate'].dt.year == 2022))]



    sel_order = sel_DataFrameAG.AG_Select_Grid(dfOrders, 250, 'test')


    def showPlot(sel_order, dfLager, dfZUgriffe):
        # Filtern Sie die Zugriffe
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
        try:
            st.write('Gewählter Auftrag: ', sel_order)
        except:
            st.write('Bitte wählen Sie einen Auftrag aus')
        st.write('Anzahl der Positionen aus dem Kartonlager: ', dfVisited['Datapoints'].max())
        
    with col2:
        # filter_gangwechsel = ['Gangwechsel 1' , 'Gangwechsel 2']
        # dfgang = dfVisited[dfVisited['Source Storage Bin'].isin(filter_gangwechsel)]
        st.write('Anzahl der Gangwechsel: folgt') #dfVisited['Source Storage Bin'].str.contains('Gangwechsel').sum()/2)
        st.write("Die Gesamtwegstrecke beträgt:", gesamt_wegstrecke / 100, "m")
        st.write("Die Bearbeitungszeit beträgt:", bearbeitungszeit)

    st.pyplot(fig)
    st.dataframe(dfVisited)
