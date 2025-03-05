
import streamlit as st
import pandas as pd
import datetime 
import uuid
import os
import hydralit_components as hc

from Data_Class.AzureStorage import upload_file_to_folder
from Data_Class.st_int_to_textbox import Int_to_Textbox
from Data_Class.MMSQL_connection import read_Table,save_Table_append,loesche_Zeile
from Data_Class.sql import SQL
from Data_Class.eml_msg_to_pdf import process_uploaded_file
from Data_Class.st_AgGridCheckBox import AG_Select_Grid
import fitz  # PyMuPDF
from PIL import Image
import io
import streamlit_autorefresh as sar
#from Seiten.subpages.hick_up_change import vorgang_bearbeiten

# TODO 
# - Vorgang Anlegen 
# - Deadline zum erledigen 


def display_pdf(file_bytes):
    # PDF aus Bytes laden
    pdf_document = fitz.open("pdf", file_bytes)

    # Durch jede Seite im PDF iterieren
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        pix = page.get_pixmap()

        # Bild aus dem Pixmap-Objekt erstellen
        img = Image.open(io.BytesIO(pix.tobytes()))

        # Bild in Streamlit anzeigen
        st.image(img, caption=f'Seite {page_num + 1}', use_column_width=True)

def load_data():
    # Lade die Daten aus der Datenbank
    data = read_Table('PAMS_HICKUP')

    users = read_Table('user')
    return data


def neuer_vorgang():
    users = read_Table('user')
   
    with st.form('Vorgang Details', clear_on_submit=True):
        # Kopfdaten Vorgang
        erstellungs_datum = datetime.date.today()
        geloest_datum = None
        file_names = None
        vorgang_id = uuid.uuid4()
        vorgang_status = 'Neu'

        col1, col15, col2 = st.columns([2,0.2,2])

        with col1:
            vorgang_datum = st.date_input('Vorfallsdatum', value=datetime.date.today())
            vorgang_bereich = st.selectbox('Fachbereich', ['DIET', 'C&F', 'LEAF', 'Domestic', 'Management', 'LOG-IN', 'K&N'], placeholder='Fachbereich wählen', index=None)
            vorgang_art = st.selectbox('Art', ['Kommunikation', 'Operativ', 'Administrativ', 'KPI', 'Beobachtung', 'Sonstiges'], index=None, placeholder='Vorfallsart wählen')
            vorgang_art_detail = st.selectbox('Kategorie', ['Mehrmenge', 'Mindermenge', 'ATTP','Vertauscher', 'Beschädigung Gebäude', 'Beschädigung Ware', 'SOS', 'Fehlende Dokumente', 'Falsche ausgefertigte Dokumente', 'Sonstiges'], index=None, placeholder='Kategorie wählen')

        with col2:
            erstellungs_datum = st.text_input('Erstellungsdatum', value=erstellungs_datum, disabled=True)
            ersteller = st.text_input('Ersteller', value=st.session_state.user, disabled=True)
            version = st.text_input('Version', value='1.0', disabled=True)

        col1, col2 , col3 = st.columns([1,2,5])
        with col1:
            kosten_ja_nein = st.radio('Kosten', ['Ja', 'Eventuell', 'Nein'], index=2)
        with col2:
            kosten = st.number_input('Kosten', value=0, min_value=0, max_value=1000000)

        # Vorgang Details
        col1, col2, col3 = st.columns([2,1,2])
        with col1:
            upload_files = st.file_uploader('Anhänge hochladen', type=['msg','eml','pdf', 'png', 'jpg', 'jpeg', 'docx', 'xlsx', 'xls','csv', 'txt'], accept_multiple_files=True)
        with col3:
            sel_users = users['username'].tolist()
            zugeteilt_an = st.selectbox('Verantwortlicher User', sel_users, index=None, placeholder='User wählen')

        st.subheader('Details')
        col1, col15, col2 = st.columns([2,0.2,2])
        with col1:
            kurze_beschreibung = st.text_input('Kurze Beschreibung', value='', max_chars=100)
        with col2:
            st.text('')
            i = st.toggle('Vorgang gelöst', value=False)

        sachverhalt = st.text_area('Sachverhalt', value='', max_chars=3000)

        if i == True:
            geloest_datum = st.date_input('Gelöst am', value=datetime.date.today())
            vorgang_status = 'Gelöst'

        if st.form_submit_button('Vorgang speichern'):
            if upload_files and vorgang_id:
                for file in upload_files:
                    new_file_name = f"{vorgang_id}_{file.name}"
                    file_names = ", ".join([new_file_name])
                    # Temporäre Datei speichern
                    temp_file_path = os.path.join("/tmp", new_file_name)
                    with open(temp_file_path, "wb") as temp_file:
                        temp_file.write(file.getbuffer())
                    # Datei in Azure hochladen
                    upload_file_to_folder(temp_file_path, "Hick_Up_Uploads")
                    # Temporäre Datei löschen
                    os.remove(temp_file_path)
                st.success("Vorgang erfolgreich gespeichert.")
            # Prüfe ob file_names existiert

            # Speichere die Vorgangsdaten in einem DataFrame 
            vorgang_data = pd.DataFrame({
                'Vorgang ID': [vorgang_id],
                'Version': [version],
                'Ersteller': [ersteller],
                'Zugeteilt an': [zugeteilt_an],
                'Erstellungsdatum': [erstellungs_datum],
                'Vorfallsdatum': [vorgang_datum],
                'Fachbereich': [vorgang_bereich],
                'Art': [vorgang_art],
                'Kategorie': [vorgang_art_detail],
                'Kosten': [kosten_ja_nein],
                'Kosten in €': [kosten],
                'Kurze Beschreibung': [kurze_beschreibung],
                'Sachverhalt': [sachverhalt],
                'Anhänge': [file_names],
                'Gelöst am': [geloest_datum],
                'Status': [vorgang_status]
            })
            st.data_editor(vorgang_data)
            # Speichere die Vorgangsdaten in der Datenbank
            save_Table_append(vorgang_data, 'PAMS_HICKUP')
            with st.spinner('Daten werden geladen...'):
                st.write('Daten erfolgreich gespeichert.')
                st.rerun()

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
        st.error("Vorgang nicht gefunden. Bitte wählen Sie einen Vorgang aus der Liste (Vorne Anklicken).")
        return

#### Bearbeiten
    with st.form('Details', clear_on_submit=True ):
        st.data_editor(vorgang_data)
        
        # Lade die vorhandenen Daten in die Formularfelder
        vorgang_id = vorgang_data['Vorgang ID'].values[0]
        version = vorgang_data['Version'].values[0]
        ersteller = vorgang_data['Ersteller'].values[0]
        zugeteilt_an = vorgang_data['Zugeteilt an'].values[0]
        erstellungs_datum = vorgang_data['Erstellungsdatum'].values[0]
        vorgang_datum = vorgang_data['Vorfallsdatum'].values[0]
        vorgang_bereich = vorgang_data['Fachbereich'].values[0]
        vorgang_art = vorgang_data['Art'].values[0]
        vorgang_art_detail = vorgang_data['Kategorie'].values[0]
        kosten_ja_nein = vorgang_data['Kosten'].values[0]
        kosten = vorgang_data['Kosten in €'].values[0]
        kurze_beschreibung = vorgang_data['Kurze Beschreibung'].values[0]
        sachverhalt = vorgang_data['Sachverhalt'].values[0]
        anhaenge = vorgang_data['Anhänge'].values[0]
        geloest_am = vorgang_data['Gelöst am'].values[0]
        status = vorgang_data['Status'].values[0]
        
        col1, col15, col2 = st.columns([2,0.2,2])

        with col1:
            vorgang_datum = st.date_input('Vorfallsdatum', value=vorgang_datum)
            vorgang_bereich_neu = st.selectbox('Fachbereich', ['DIET', 'C&F', 'LEAF', 'Domestic', 'Management', 'LOG-IN', 'K&N'],index=None ,placeholder=vorgang_bereich)
            vorgang_art_neu = st.selectbox('Art', ['Kommunikation', 'Operativ', 'Administrativ', 'KPI', 'Beobachtung', 'Sonstiges'],index=None, placeholder=vorgang_art)
            st.write(f'Kategorie: {vorgang_art_neu}')
            vorgang_art_detail_neu = st.selectbox('Kategorie', ['Mehrmenge', 'Mindermenge', 'ATTP','Vertauscher', 'Beschädigung Gebäude', 'Beschädigung Ware', 'SOS', 'Fehlende Dokumente', 'Falsche ausgefertigte Dokumente', 'Sonstiges'], index=None,placeholder=vorgang_art_detail)
        with col2:
            erstellungs_datum = st.text_input('Erstellungsdatum', value=erstellungs_datum, disabled=True)
            ersteller = st.text_input('Ersteller', value=ersteller, disabled=True)
            version = st.text_input('Version', value=version, disabled=True)
        col1, col2 , col3 = st.columns([1,2,5])
        with col1:
            kosten_ja_nein = st.radio('Kosten', ['Ja', 'Eventuell', 'Nein'], index=2)
        with col2:
            kosten = st.number_input('Kosten', value=kosten, min_value=0, max_value=1000000)
        
        # Vorgang Details
        col1, col2, col3 = st.columns([2,1,2])
        with col1:
            pass
            #upload_files = st.file_uploader('Anhänge hochladen', type=['msg','eml','pdf', 'png', 'jpg', 'jpeg', 'docx', 'xlsx', 'xls','csv', 'txt'], accept_multiple_files=True)
        with col3:
            pass
            #zugeteilt_an = st.selectbox('Verantwortlicher User', sel_users, index=None, placeholder=zugeteilt_an)
        
        st.subheader('Details')
        col1, col15, col2 = st.columns([2,0.2,2])
        with col1:
            kurze_beschreibung = st.text_input('Kurze Beschreibung', value=kurze_beschreibung, max_chars=100)
        with col2:
            st.text('')
            i = st.toggle('Vorgang gelöst', value=False)
        
        sachverhalt = st.text_area('Sachverhalt', value=sachverhalt, max_chars=3000)
        vorgang_status = status
        if i == True:
            geloest_datum = st.date_input('Gelöst am', value=datetime.date.today())
            vorgang_status = 'Gelöst'
        
        col1, col2 = st.columns([1,1])
        with col1:
            if st.form_submit_button('Speichern'):
                data = pd.DataFrame({
                    'Vorgang ID': [vorgang_id],
                    'Version': [version],
                    'Ersteller': [ersteller],
                    'Zugeteilt an': [zugeteilt_an],
                    'Erstellungsdatum': [erstellungs_datum],
                    'Vorfallsdatum': [vorgang_datum],
                    'Fachbereich': [vorgang_bereich_neu],
                    'Art': [vorgang_art_neu],
                    'Kategorie': [vorgang_art_detail_neu],
                    'Kosten': [kosten_ja_nein],
                    'Kosten in €': [kosten],
                    'Kurze Beschreibung': [kurze_beschreibung],
                    'Sachverhalt': [sachverhalt],
                    'Anhänge': [anhaenge],
                    'Gelöst am': [geloest_am],
                    'Status': [vorgang_status]
                })
                st.data_editor(data)
        with col2:    
            if st.form_submit_button('Löschen'):
               loesche_Zeile('PAMS_HICKUP', 'Vorgang ID', wert_str=vorgang_id)    
            
            



            
def main():
    
    
    with st.expander("Neuer Vorgang"):
        neuer_vorgang()
    
    with st.expander("Vorgang bearbeiten"):
        df = read_Table('PAMS_HICKUP')
        
        selvorgang = st.dataframe(df,
        use_container_width=True,
        hide_index=True,
        on_select="rerun",
        selection_mode="single-row",
        )

        if selvorgang is not None:

            sel_id = list(selvorgang.selection.values())[0]  
            
            vorgang_bearbeiten(df.iloc[sel_id])

    with st.expander("Vorgang Löschen", expanded=False):
        df = read_Table('PAMS_HICKUP')
        
        selvorgang = st.dataframe(df,
        use_container_width=True,
        hide_index=True,
        on_select="rerun",
        selection_mode="single-row",key='Vorgang Löschen'
        )
        try:
            if selvorgang is not None:

                sel_id = list(selvorgang.selection.values())[0]  
                st.write(f'Vorgang ID: {df.iloc[sel_id]["Vorgang ID"]}')
                if st.button('Vorgang Löschen'):
                    # Delete the row from Dataframe
                    df = df.drop([sel_id])
                    SQL.update_Table('PAMS_HICKUP', df, 'Vorgang ID')
                    st.success(f'Vorgang {df.iloc[sel_id]["Vorgang ID"]} wurde gelöscht.')
                    sar.st_autorefresh(interval=88000, debounce=True)
        except:
            pass
