import streamlit as st
import pandas as pd

import matplotlib.pyplot as plt
from PIL import Image
from src.st_func_Return_selectDF import sel_DataFrameAG

#       streamlit run /Users/martinwolf/Python/IPYNB/Value_stream/Streamlit/main.py 
st.set_page_config(layout="wide", page_title="Value", page_icon="🚚",initial_sidebar_state='expanded')
st.header("Value Stream Mapping")
st.subheader("Laufweg des Mitarbeiters pro Auftrag") 



@st.cache_data
def load_DF():
    dfLager = pd.read_excel('Value_stream/Streamlit/Lager.xlsx')
    dfZUgriffe = pd.read_excel('Value_stream/Streamlit/LT22April2023.XLSX')
    dfOrders = pd.read_pickle('Value_stream/Streamlit/prod_Kundenbestellungen.pkl')
    return dfLager,dfZUgriffe,dfOrders

dfLager,dfZUgriffe,dfOrders = load_DF()

#filter dfOrders'PlannedDate' nach den Monaten April 2023 und August 2022
# Konvertiere die 'PlannedDate'-Spalte in einen datetime-Datentyp
dfOrders['PlannedDate'] = pd.to_datetime(dfOrders['PlannedDate'])

# Filtern nach den Monaten April 2023 und August 2022
dfOrders = dfOrders[(dfOrders['PlannedDate'].dt.month == 4) & (dfOrders['PlannedDate'].dt.year == 2023) | 
                    (dfOrders['PlannedDate'].dt.month == 12) & (dfOrders['PlannedDate'].dt.year == 2022)]


sel_order = sel_DataFrameAG.AG_Select_Grid(dfOrders,250,'test')

st.write('Gewählter Auftrag: ',sel_order)


# Filtern Sie die Zugriffe
dfZUgriffe_filtered = dfZUgriffe[dfZUgriffe['Dest.Storage Bin'] == sel_order]

# Sortieren Sie nach Confirmation Time
dfZUgriffe_filtered = dfZUgriffe_filtered.sort_values(by='Confirmation time.1')

# Fügen Sie die Spalte Laufweg hinzu
dfZUgriffe_filtered['Laufweg'] = range(1, len(dfZUgriffe_filtered) + 1)
#übergebe Laufweg in dfLager
dfMerged = pd.merge(dfLager, dfZUgriffe_filtered, left_on='Stellplatz', right_on='Source Storage Bin', how='left', suffixes=('_lager', '_zugriffe'))

dfLager['Pickzeit'] = dfMerged['Confirmation time.1']# Berechnen Sie die Zugriffe pro Stellplatz
dfLager['Zugriffe'] = dfLager.apply(lambda x: dfZUgriffe_filtered[dfZUgriffe_filtered['Source Storage Bin'] == x['Stellplatz']].shape[0], axis=1)
dfLager['Laufweg'] = dfMerged['Laufweg']# Berechnen Sie die Zugriffe pro Stellplatz

# Berechnen Sie die Zugriffe pro Stellplatz
dfLager['Zugriffe'] = dfLager.apply(lambda x: dfZUgriffe_filtered[dfZUgriffe_filtered['Source Storage Bin'] == x['Stellplatz']].shape[0], axis=1)

# Bild laden
img = Image.open('Value_stream/Streamlit/Lager.png')

# Filtern Sie die Daten, um nur die besuchten Stellplätze darzustellen
dfVisited = dfLager[dfLager['Laufweg'].notna()]

# Sortieren Sie die Daten nach Laufweg
dfVisited = dfVisited.sort_values('Laufweg')

# Erstellen Sie eine Figur und Achsen mit matplotlib
# Die Größe der Figur wird auf die Größe des Bildes in Zoll eingestellt (1 Zoll = 80 Pixel)
fig, ax = plt.subplots(figsize=(img.size[0]/80, img.size[1]/80))

# Entfernen Sie die Achsen
ax.axis('off')

# Zeigen Sie das Bild
ax.imshow(img)

# Zeichnen Sie jeden Punkt aus der Tabelle dfVisited und verbinden Sie sie mit Linien
ax.plot(dfVisited['X'], dfVisited['Y'], 'bo-')  # 'bo-' steht für blaue Punkte verbunden mit einer Linie

# Fügen Sie den Text hinzu (rot und fett)
for idx, row in dfVisited.iterrows():
    ax.text(row['X'], row['Y'], str(row['Laufweg']), color='red', weight='bold', fontsize=18)

# Zeigen Sie die Figur
st.pyplot(fig)


st.dataframe(dfVisited)
st.dataframe(dfLager)

