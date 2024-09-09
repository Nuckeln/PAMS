import streamlit as st
import pandas as pd
import numpy as np
import datetime
import streamlit_autorefresh as sar
from PIL import Image
import plotly_express as px
from annotated_text import annotated_text, annotation
import streamlit_timeline as timeline
from Data_Class.AzureStorage_dev import get_blob_list_dev, get_file_dev
from Data_Class.wetter.api import getWetterBayreuth
from Data_Class.MMSQL_connection import read_Table
from io import BytesIO

import matplotlib.pyplot as plt
from matplotlib.patches import Arc

import plotly.graph_objects as go


#@st.cache_data
def load_data():
    # Read Data from SQL
    df_Bestellungen = read_Table('prod_Kundenbestellungen')
    data = get_file_dev("CW_SDDS.xlsm")
    df_fehler = pd.read_excel(BytesIO(data),sheet_name='ISSUES')
    df_deadlines = pd.read_excel(BytesIO(data),sheet_name='Verlängerungen Deadlines')
    
    try: 
        #lösche die ersten 3 Reihen, und alle Spalten ab der 14. Spalte
        df_deadlines = df_deadlines.iloc[3:,:14]
    except:
        st.warning("Fehler beim Einlesen der Fehlerdaten, bitte Prüfe das sich Spaltenanzahl und Reihenanzahl im Excel nicht geändert haben")


    return df_Bestellungen, df_fehler, df_deadlines


def filter_datum_von_bis(df, vonDatum, bisDatum, Datumsspalte):
    # Prüfe ob die Datumsspalte in df vorhanden ist und ob sie das 'datetime64[ns, UTC]' Format hat, wenn nicht, konvertiere sie
    if df[Datumsspalte].dtypes != 'datetime64[ns, UTC]':
        df[Datumsspalte] = pd.to_datetime(df[Datumsspalte], utc=True)
    
    # Konvertiere vonDatum und bisDatum zu Timestamps und stelle sicher, dass sie die gleiche Zeitzone wie die Datumsspalte haben
    if isinstance(vonDatum, pd.Timestamp):
        vonDatum = vonDatum.tz_convert('UTC') if vonDatum.tzinfo else vonDatum.tz_localize('UTC')
    else:
        vonDatum = pd.to_datetime(vonDatum).tz_localize('UTC')
    
    if isinstance(bisDatum, pd.Timestamp):
        bisDatum = bisDatum.tz_convert('UTC') if bisDatum.tzinfo else bisDatum.tz_localize('UTC')
    else:
        bisDatum = pd.to_datetime(bisDatum).tz_localize('UTC')
    
    # Filtern nach Datum
    df = df[(df[Datumsspalte] >= vonDatum) & (df[Datumsspalte] <= bisDatum)]
    return df




# def Deadline(df):



def main():
    st.title("KPI")
    df_Bestellungen, df_fehler, df_deadlines  = load_data()
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
    # set Startdate and Enddate
    # Retail soll immer der ganze laufende Monat angezeigt werden
        von_datum = st.date_input("Startdatum", datetime.date.today().replace(day=1))
    with col2:
        bis_datum = st.date_input("Enddatum", datetime.date.today())

    # Filter Data by Dates
    df_Bestellungen = filter_datum_von_bis(df_Bestellungen, von_datum, bis_datum, 'PlannedDate')
    df_fehler = filter_datum_von_bis(df_fehler, von_datum, bis_datum, 'Datum gemeldet')
    st.data_editor(df_Bestellungen)
    st.data_editor(df_fehler)
    st.data_editor(df_deadlines)
    

    
    