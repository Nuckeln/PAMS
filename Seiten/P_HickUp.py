
import streamlit as st
import pandas as pd
import datetime 
import uuid
import os
import hydralit_components as hc

from Data_Class.AzureStorage import upload_file_to_folder
from Data_Class.st_int_to_textbox import Int_to_Textbox
from Data_Class.MMSQL_connection import read_Table,save_Table_append
from Data_Class.eml_msg_to_pdf import process_uploaded_file
from Data_Class.st_AgGridCheckBox import AG_Select_Grid
import fitz  # PyMuPDF
from PIL import Image
import io
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
    with st.form('Vorgang Details', clear_on_submit=True):
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
        
        if i == True:
            geloest_datum = st.date_input('Gelöst am', value=datetime.date.today())
            vorgang_status = 'Gelöst'
        

        if st.form_submit_button('Vorgang ändern'):
            # Speichere die Vorgangsdaten in einem DataFrame 
            st.warning("Wird nicht gespeichert ist noch in Arbeit")
            if vorgang_art_neu == None:
                vorgang_art_neu = vorgang_art
            if vorgang_art_detail_neu == None:
                vorgang_art_detail_neu = vorgang_art_detail
            if vorgang_bereich_neu == None:
                vorgang_bereich_neu = vorgang_bereich
            
def main():
    st.container(border=True)
    col1,col2 , col3, col4 = st.columns([1, 1, 1,1])    
    # define what option labels and icons to display
    option_data = [
    {'icon': "new", 'label':"Neuer Vorgang"},
    {'icon': "", 'label':"Vorgang bearbeiten"},
    ]

    # override the theme, else it will use the Streamlit applied theme
    over_theme = {'txc_inactive': 'white','menu_background':'#0e2b63','txc_active':'yellow','option_active':'blue'}
    font_fmt = {'font-class':'h2','font-size':'150%'}

    # display a horizontal version of the option bar
    op = hc.option_bar(option_definition=option_data,title=' ',key='PrimaryOption',override_theme=over_theme,font_styling=font_fmt,horizontal_orientation=True)


    if "df" not in st.session_state:
        st.session_state.df = load_data()

    if op == 'Neuer Vorgang':
        neuer_vorgang()

    elif op == 'Vorgang bearbeiten':

        st.session_state.df.sort_values(by='Erstellungsdatum', ascending=False, inplace=True)

        event = st.dataframe(
            st.session_state.df,
            key="data",
            on_select="rerun",
            selection_mode=["single-row"],
        )

        sel_id = list(event.selection.values())[0]   
        try:
        #wert aus df ermitteln in Zeile sel_id
            df = st.session_state.df.iloc[sel_id]
        except:
            df = None
        if df is not None:
            vorgang_bearbeiten(df)
        

    #     schneller_vorgang()



