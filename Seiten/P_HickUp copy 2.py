import streamlit as st
import pandas as pd
import datetime
import uuid
import os
import hydralit_components as hc

from Data_Class.AzureStorage import upload_file_to_folder
from Data_Class.st_int_to_textbox import Int_to_Textbox
from Data_Class.MMSQL_connection import read_Table, save_Table_append
from Data_Class.sql import SQL
from Data_Class.eml_msg_to_pdf import process_uploaded_file
from Data_Class.st_AgGridCheckBox import AG_Select_Grid
import fitz  # PyMuPDF
from PIL import Image
import io
import streamlit_autorefresh as sar

# PDF-Anzeige
def display_pdf(file_bytes):
    pdf_document = fitz.open("pdf", file_bytes)
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        pix = page.get_pixmap()
        img = Image.open(io.BytesIO(pix.tobytes()))
        st.image(img, caption=f'Seite {page_num + 1}', use_column_width=True)

def load_data():
    data = read_Table('PAMS_HICKUP')
    users = read_Table('user')
    return data

# Neuer Vorgang
def neuer_vorgang():
    users = read_Table('user')
    with st.form('Vorgang_Details', clear_on_submit=True):
        erstellungs_datum = datetime.date.today()
        geloest_datum = None
        file_names = ""
        vorgang_id = uuid.uuid4()
        vorgang_status = 'Neu'

        col1, col15, col2 = st.columns([2, 0.2, 2])
        with col1:
            vorgang_datum = st.date_input('Vorfallsdatum', value=datetime.date.today())
            fachbereich_options = ['Bitte wählen', 'DIET', 'C&F', 'LEAF', 'Domestic', 'Management', 'LOG-IN', 'K&N']
            vorgang_bereich = st.selectbox('Fachbereich', fachbereich_options, index=0)
            art_options = ['Bitte wählen', 'Kommunikation', 'Operativ', 'Administrativ', 'KPI', 'Beobachtung', 'Sonstiges']
            vorgang_art = st.selectbox('Art', art_options, index=0)
            kategorie_options = ['Bitte wählen', 'Mehrmenge', 'Mindermenge', 'ATTP', 'Vertauscher', 'Beschädigung Gebäude', 'Beschädigung Ware', 'SOS', 'Fehlende Dokumente', 'Falsche ausgefertigte Dokumente', 'Sonstiges']
            vorgang_art_detail = st.selectbox('Kategorie', kategorie_options, index=0)
        with col2:
            st.text_input('Erstellungsdatum', value=str(erstellungs_datum), disabled=True)
            ersteller = st.text_input('Ersteller', value=st.session_state.get("user", "Unbekannt"), disabled=True)
            version = st.text_input('Version', value='1.0', disabled=True)

        col1, col2, col3 = st.columns([1, 2, 5])
        with col1:
            kosten_ja_nein = st.radio('Kosten', ['Ja', 'Eventuell', 'Nein'], index=2)
        with col2:
            kosten = st.number_input('Kosten', value=0, min_value=0, max_value=1000000)
        
        col1, col2, col3 = st.columns([2, 1, 2])
        with col1:
            upload_files = st.file_uploader('Anhänge hochladen',
                                            type=['msg', 'eml', 'pdf', 'png', 'jpg', 'jpeg', 'docx', 'xlsx', 'xls', 'csv', 'txt'],
                                            accept_multiple_files=True)
        with col3:
            sel_users = users['username'].tolist() if 'username' in users.columns else []
            zugeteilt_an = st.selectbox('Verantwortlicher User', ['Bitte wählen'] + sel_users, index=0)
        
        st.subheader('Details')
        col1, col15, col2 = st.columns([2, 0.2, 2])
        with col1:
            kurze_beschreibung = st.text_input('Kurze Beschreibung', value='', max_chars=100)
        with col2:
            vorgang_geloest = st.toggle('Vorgang gelöst', value=False)
        
        sachverhalt = st.text_area('Sachverhalt', value='', max_chars=3000)
        if vorgang_geloest:
            geloest_datum = st.date_input('Gelöst am', value=datetime.date.today())
            vorgang_status = 'Gelöst'
        
        if st.form_submit_button('Vorgang speichern'):
            if upload_files:
                file_names_list = []
                for file in upload_files:
                    new_file_name = f"{vorgang_id}_{file.name}"
                    file_names_list.append(new_file_name)
                    temp_file_path = os.path.join("/tmp", new_file_name)
                    with open(temp_file_path, "wb") as temp_file:
                        temp_file.write(file.getbuffer())
                    upload_file_to_folder(temp_file_path, "Hick_Up_Uploads")
                    os.remove(temp_file_path)
                file_names = ", ".join(file_names_list)
            vorgang_data = pd.DataFrame({
                'Vorgang ID': [str(vorgang_id)],
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
            save_Table_append(vorgang_data, 'PAMS_HICKUP')
            st.success("Vorgang erfolgreich gespeichert.")
            st.rerun()

# Vorgang bearbeiten
def vorgang_bearbeiten(vorgang_data):
    if vorgang_data.empty:
        st.error("Vorgang nicht gefunden. Bitte wählen Sie einen Vorgang aus der Liste.")
        return

    st.subheader("Aktuelle Vorgangsdaten")
    st.dataframe(vorgang_data)

    # Formular zur Aktualisierung
    with st.form('vorgang_bearbeiten_update', clear_on_submit=True):
        # Vorhandene Daten laden (erste Zeile)
        vorgang_id = vorgang_data['Vorgang ID'].iloc[0]
        version = vorgang_data['Version'].iloc[0]
        ersteller = vorgang_data['Ersteller'].iloc[0]
        zugeteilt_an = vorgang_data['Zugeteilt an'].iloc[0]
        erstellungs_datum = vorgang_data['Erstellungsdatum'].iloc[0]
        vorgang_datum = vorgang_data['Vorfallsdatum'].iloc[0]
        vorgang_bereich_alt = vorgang_data['Fachbereich'].iloc[0]
        vorgang_art_alt = vorgang_data['Art'].iloc[0]
        vorgang_art_detail_alt = vorgang_data['Kategorie'].iloc[0]
        kosten_ja_nein_alt = vorgang_data['Kosten'].iloc[0]
        kosten = vorgang_data['Kosten in €'].iloc[0]
        kurze_beschreibung = vorgang_data['Kurze Beschreibung'].iloc[0]
        sachverhalt = vorgang_data['Sachverhalt'].iloc[0]
        anhaenge = vorgang_data['Anhänge'].iloc[0]
        geloest_am_alt = vorgang_data['Gelöst am'].iloc[0]
        status_alt = vorgang_data['Status'].iloc[0]

        col1, col15, col2 = st.columns([2, 0.2, 2])
        with col1:
            vorgang_datum_new = st.date_input('Vorfallsdatum', value=pd.to_datetime(vorgang_datum).date())
            fachbereich_options = ['Bitte wählen', 'DIET', 'C&F', 'LEAF', 'Domestic', 'Management', 'LOG-IN', 'K&N']
            index_fb = fachbereich_options.index(vorgang_bereich_alt) if vorgang_bereich_alt in fachbereich_options else 0
            vorgang_bereich_new = st.selectbox('Fachbereich', fachbereich_options, index=index_fb)
            
            art_options = ['Bitte wählen', 'Kommunikation', 'Operativ', 'Administrativ', 'KPI', 'Beobachtung', 'Sonstiges']
            index_art = art_options.index(vorgang_art_alt) if vorgang_art_alt in art_options else 0
            vorgang_art_new = st.selectbox('Art', art_options, index=index_art)
            
            kategorie_options = ['Bitte wählen', 'Mehrmenge', 'Mindermenge', 'ATTP', 'Vertauscher', 'Beschädigung Gebäude', 'Beschädigung Ware', 'SOS', 'Fehlende Dokumente', 'Falsche ausgefertigte Dokumente', 'Sonstiges']
            index_kat = kategorie_options.index(vorgang_art_detail_alt) if vorgang_art_detail_alt in kategorie_options else 0
            vorgang_art_detail_new = st.selectbox('Kategorie', kategorie_options, index=index_kat)
        with col2:
            st.text_input('Erstellungsdatum', value=str(erstellungs_datum), disabled=True)
            st.text_input('Ersteller', value=ersteller, disabled=True)
            st.text_input('Version', value=version, disabled=True)
        
        col1, col2 = st.columns(2)
        with col1:
            kosten_ja_nein_new = st.radio('Kosten', ['Ja', 'Eventuell', 'Nein'], index=['Ja', 'Eventuell', 'Nein'].index(kosten_ja_nein_alt) if kosten_ja_nein_alt in ['Ja', 'Eventuell', 'Nein'] else 2)
        with col2:
            kosten_new = st.number_input('Kosten', value=kosten, min_value=0, max_value=1000000)
        
        st.subheader('Details')
        col1, col15, col2 = st.columns([2, 0.2, 2])
        with col1:
            kurze_beschreibung_new = st.text_input('Kurze Beschreibung', value=kurze_beschreibung, max_chars=100)
        with col2:
            vorgang_geloest_toggle = st.toggle('Vorgang gelöst', value=(status_alt == 'Gelöst'))
        
        sachverhalt_new = st.text_area('Sachverhalt', value=sachverhalt, max_chars=3000)
        geloest_datum_new = geloest_am_alt
        if vorgang_geloest_toggle:
            geloest_datum_new = st.date_input('Gelöst am', value=datetime.date.today())
            status_new = 'Gelöst'
        else:
            status_new = status_alt
        
        if st.form_submit_button('Speichern'):
            updated_data = pd.DataFrame({
                'Vorgang ID': [vorgang_id],
                'Version': [version],
                'Ersteller': [ersteller],
                'Zugeteilt an': [zugeteilt_an],
                'Erstellungsdatum': [erstellungs_datum],
                'Vorfallsdatum': [vorgang_datum_new],
                'Fachbereich': [vorgang_bereich_new],
                'Art': [vorgang_art_new],
                'Kategorie': [vorgang_art_detail_new],
                'Kosten': [kosten_ja_nein_new],
                'Kosten in €': [kosten_new],
                'Kurze Beschreibung': [kurze_beschreibung_new],
                'Sachverhalt': [sachverhalt_new],
                'Anhänge': [anhaenge],
                'Gelöst am': [geloest_datum_new],
                'Status': [status_new]
            })
            
def main():
    with st.expander("Neuer Vorgang"):
        neuer_vorgang()
    
    with st.expander("Vorgang bearbeiten"):
        df = read_Table('PAMS_HICKUP')
        selected_row = st.dataframe(df,
                                    use_container_width=True,
                                    hide_index=True,
                                    on_select="rerun",
                                    selection_mode="single-row")
        if selected_row is not None and 'selection' in selected_row:
            sel_id = list(selected_row.selection.values())[0]
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
                    st.write('Geht NOCH NICHT')   
                    
        except:
            pass
if __name__ == '__main__':
    main()