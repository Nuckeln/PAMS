

import streamlit as st
import pandas as pd
import datetime 
import uuid
import os
import hydralit_components as hc

from Data_Class.AzureStorage import upload_file_to_folder
from Data_Class.st_int_to_textbox import Int_to_Textbox
from Data_Class.MMSQL_connection import read_Table,save_Table_append , save_Table, lade_tab_by
from Data_Class.eml_msg_to_pdf import process_uploaded_file
from Data_Class.st_AgGridCheckBox import AG_Select_Grid
import fitz  # PyMuPDF
from PIL import Image
import io

# TODO 
def vorgang_bearbeiten(vorgang_data):
# Folgende Spalten sind in der Tabelle vorhanden:
# 'Vorgang ID',
# 'Version',
# 'Ersteller',
# 'Zugeteilt an',
# 'Erstellungsdatum',
# 'Vorfallsdatum',
# 'Fachbereich',
# 'Art',
# 'Kategorie',
# 'Kosten',
# 'Kosten in €',
# 'Kurze Beschreibung',
# 'Sachverhalt',
# 'Anhänge',
# 'Gelöst am',
# 'Status'
#Prüfen ob Vorgang vorhanden
    if vorgang_data.empty:  
        st.error("Vorgang nicht gefunden.")
    return

    #
        