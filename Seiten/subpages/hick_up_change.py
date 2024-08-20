

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

def vorgang_bearbeiten(vorgang_data):
    st.write('Vorgang bearbeiten')
    # Lade bestehende Vorgangsdaten aus der Datenbank
    # if vorgang_data.empty:
    #     st.error("Vorgang nicht gefunden.")
    #     return
    
    # # Sicherstellen, dass es eine erste Zeile gibt
    # if 0 not in vorgang_data.index:
    #     st.error("Der angegebene Vorgang hat keine gültigen Daten.")
    #     return
    
    # # Zugriff auf die erste Zeile
    # existing_data = vorgang_data.iloc[0]

    # with st.form('Vorgang Bearbeitung', clear_on_submit=False):
    #     # Kopfdaten Vorgang
    #     erstellungs_datum = existing_data['Erstellungsdatum']
    #     geloest_datum = existing_data['Gelöst am']
    #     vorgang_id = existing_data['Vorgang ID']
    #     vorgang_status = existing_data['Status']
    #     version = str(float(existing_data['Version']) + 1)

    #     col1, col15, col2 = st.columns([2, 0.2, 2])
    #     with col1:
    #         vorgang_datum = st.date_input('Vorfallsdatum', value=existing_data['Vorfallsdatum'])
    #         vorgang_bereich = st.selectbox('Fachbereich', ['DIET', 'C&F', 'LEAF', 'Domestic', 'Management', 'LOG-IN', 'K&N'], index=None)
    #         vorgang_art = st.selectbox('Art', ['Kommunikation', 'Operativ', 'Administrativ', 'KPI', 'Beobachtung', 'Sonstiges'], index=None)
    #         vorgang_art_detail = st.selectbox('Kategorie', ['Mehrmenge', 'Mindermenge', 'Vertauscher', 'Beschädigung Gebäude', 'Beschädigung Ware', 'SOS', 'Fehlende Dokumente', 'Falsche ausgefertigte Dokumente', 'Sonstiges'], index=None)

    #     with col2:
    #         st.text_input('Erstellungsdatum', value=erstellungs_datum, disabled=True)
    #         ersteller = st.text_input('Ersteller', value=existing_data['Ersteller'], disabled=True)
    #         st.text_input('Version', value=version, disabled=True)

    #     col1, col2, col3 = st.columns([1, 2, 5])
    #     with col1:
    #         kosten_ja_nein = st.radio('Kosten', ['Ja', 'Eventuell', 'Nein'], index=['Ja', 'Eventuell', 'Nein'].index(existing_data['Kosten']))
    #     with col2:
    #         kosten = st.number_input('Kosten', value=existing_data['Kosten in €'], min_value=0, max_value=1000000)
        
    #     # Vorgang Details
    #     col1, col2, col3 = st.columns([2, 1, 2])
    #     with col1:
    #         upload_files = st.file_uploader('Anhänge hochladen', type=['pdf', 'png', 'jpg', 'jpeg', 'docx', 'xlsx', 'csv', 'txt'], accept_multiple_files=True)
    #     with col3:
    #         zugeteilt_an = st.selectbox('Verantwortlicher User', ['User1', 'User2', 'User3', 'User4', 'User5'], index=None)

    #     st.subheader('Details')
    #     col1, col15, col2 = st.columns([2, 0.2, 2])
    #     with col1:
    #         kurze_beschreibung = st.text_input('Kurze Beschreibung', value=existing_data['Kurze Beschreibung'], max_chars=100)
    #     with col2:
    #         st.text('')
    #         i = st.toggle('Vorgang gelöst', value=(vorgang_status == 'Gelöst'))

    #     sachverhalt = st.text_area('Sachverhalt', value=existing_data['Sachverhalt'], max_chars=3000)

    #     if i:
    #         geloest_datum = st.date_input('Gelöst am', value=datetime.date.today())
    #         vorgang_status = 'Gelöst'
        
    #     if st.form_submit_button('Änderungen speichern'):
    #         file_names = ", ".join([file.name for file in upload_files])
    #         for file in upload_files:
    #             with open(os.path.join('Data/tmp', file.name), 'wb') as f:
    #                 f.write(file.getbuffer())
            
    #         updated_data = pd.DataFrame({
    #             'Vorgang ID': [vorgang_id],
    #             'Version': [version],
    #             'Ersteller': [ersteller],
    #             'Zugeteilt an': [zugeteilt_an],
    #             'Erstellungsdatum': [erstellungs_datum],
    #             'Vorfallsdatum': [vorgang_datum],
    #             'Fachbereich': [vorgang_bereich],
    #             'Art': [vorgang_art],
    #             'Kategorie': [vorgang_art_detail],
    #             'Kosten': [kosten_ja_nein],
    #             'Kosten in €': [kosten],
    #             'Kurze Beschreibung': [kurze_beschreibung],
    #             'Sachverhalt': [sachverhalt],
    #             'Anhänge': [file_names],
    #             'Gelöst am': [geloest_datum],
    #             'Status': [vorgang_status]
    #         })
            
    #         st.data_editor(updated_data)