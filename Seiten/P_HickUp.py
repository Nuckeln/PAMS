
import streamlit as st
import pandas as pd
import datetime 
import uuid
import os
import hydralit_components as hc

from Data_Class.st_int_to_textbox import Int_to_Textbox
from Data_Class.MMSQL_connection import read_Table,save_Table_append
from Data_Class.eml_msg_to_pdf import process_uploaded_file
from Data_Class.st_func_Return_selectDF import AG_Select_Grid
import fitz  # PyMuPDF
from PIL import Image
import io

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
    return data

def neuer_vorgang():

    with st.form('Vorgang Details', clear_on_submit=True):
    
        ## Kopfdaten Vorgang
        # TODO Systemzeit an Berlin anpassen
        erstellungs_datum = datetime.date.today()
        geloest_datum = None
        vorgang_id = uuid.uuid4()
        vorgang_status = 'Neu'
        
        
        col1, col15, col2 = st.columns([2,0.2,2])

        with col1:
            vorgang_datum = st.date_input('Vorfallsdatum', value=datetime.date.today())
            
            vorgang_bereich = st.selectbox('Fachbereich',['DIET', 'C&F', 'LEAF', 'Domestic', 'Management', 'LOG-IN', 'K&N'], placeholder='Fachbereich wählen', index=None)
            vorgang_art = st.selectbox('Art',['Kommunikation' , 'Operativ', 'Administrativ', 'KPI', 'Beobachtung','Sonstiges'], index=None,placeholder='Vorfallsart wählen')
            vorgang_art_detail = st.selectbox('Katergorie', ['Mehrmenge', 'Mindermenge', 'Vertauscher', 'Beschädigung Gebäude', 'Beschädigung Ware', 'SOS','Fehlende Dokumente','Falsche ausgefertigte Dokumente', 'Sonstiges'], index=None, placeholder='Kategorie wählen')
            
            with col15:
                pass
            
        with col2:
            erstellungs_datum = st.text_input('Erstellungsdatum', value=erstellungs_datum,disabled=True)
            ersteller = st.text_input('Ersteller', value=st.session_state.user,disabled=True)
            version = st.text_input('Version', value='1.0', disabled=True)
        col1, col2 , col3 = st.columns([1,2,5])
        with col1:
            kosten_ja_nein = st.radio('Kosten', ['Ja','Eventuell' ,'Nein'], index=2)
        with col2:   
            kosten = st.number_input('Kosten', value=0, min_value=0, max_value=1000000)
        with col3:
            pass
        
        # Vorgang Details
        col1, col2, col3 = st.columns([2,1,2])

        with col1:
            upload_files = st.file_uploader('Anhänge hochladen', type=['pdf', 'png', 'jpg', 'jpeg', 'docx', 'xlsx', 'csv', 'txt'], accept_multiple_files=True)
        with col2:
            pass
        with col3:
            zugeteilt_an = st.selectbox('Verantwortlicher User', ['User1', 'User2', 'User3', 'User4', 'User5'], index=None, placeholder='User wählen')
        
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

            # Erstelle einen String mit den Namen der hochgeladenen Dateien, getrennt durch Kommas
            file_names = ", ".join([file.name for file in upload_files])

            # Speichere die hochgeladenen Dateien in einem temporären Verzeichnis
            for file in upload_files:
                with open(os.path.join('Data/tmp', file.name), 'wb') as f:
                    f.write(file.getbuffer())

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

def bearbeiten_vorgang(data):

    def dataframe_with_selections(df):
        df_with_selections = df.copy()
        df_with_selections.insert(0, "Select", False)

        # Get dataframe row-selections from user with st.data_editor
        edited_df = st.data_editor(
            df_with_selections,
            hide_index=True,
            column_config={"Select": st.column_config.CheckboxColumn(required=True)},
            disabled=df.columns,
        )

        # Filter the dataframe using the temporary column, then drop the column
        selected_rows = edited_df[edited_df.Select]
        return selected_rows.drop('Select', axis=1)


    selection = dataframe_with_selections(data)
    

    if st.button('Vorgang laden'):
        vorgang_data = selection
        
        if not vorgang_data.empty:
    
            with st.form('Vorgang Bearbeitung', clear_on_submit=False):
                # Kopfdaten Vorgang
                erstellungs_datum = vorgang_data.at[0, 'Erstellungsdatum']
                geloest_datum = vorgang_data.at[0, 'Gelöst am']
                vorgang_id = vorgang_data.at[0, 'Vorgang ID']
                vorgang_status = vorgang_data.at[0, 'Status']
                version = str(float(vorgang_data.at[0, 'Version']) + 1)

                col1, col15, col2 = st.columns([2, 0.2, 2])
                with col1:
                    vorgang_datum = st.date_input('Vorfallsdatum', value=vorgang_data.at[0, 'Vorfallsdatum'])
                    vorgang_bereich = st.selectbox('Fachbereich', ['DIET', 'C&F', 'LEAF', 'Domestic', 'Management', 'LOG-IN', 'K&N'], index=None)
                    vorgang_art = st.selectbox('Art', ['Kommunikation', 'Operativ', 'Administrativ', 'KPI', 'Beobachtung', 'Sonstiges'], index=None)
                    vorgang_art_detail = st.selectbox('Katergorie', ['Mehrmenge', 'Mindermenge', 'Vertauscher', 'Beschädigung Gebäude', 'Beschädigung Ware', 'SOS', 'Fehlende Dokumente', 'Falsche ausgefertigte Dokumente', 'Sonstiges'], index=None)

                with col2:
                    st.text_input('Erstellungsdatum', value=erstellungs_datum, disabled=True)
                    ersteller = st.text_input('Ersteller', value=vorgang_data.at[0, 'Ersteller'], disabled=True)
                    st.text_input('Version', value=version, disabled=True)

                col1, col2, col3 = st.columns([1, 2, 5])
                with col1:
                    kosten_ja_nein = st.radio('Kosten', ['Ja', 'Eventuell', 'Nein'], index=['Ja', 'Eventuell', 'Nein'].index(vorgang_data.at[0, 'Kosten']))
                with col2:
                    kosten = st.number_input('Kosten', value=vorgang_data.at[0, 'Kosten in €'], min_value=0, max_value=1000000)
                
                # Vorgang Details
                col1, col2, col3 = st.columns([2, 1, 2])
                with col1:
                    upload_files = st.file_uploader('Anhänge hochladen', type=['pdf', 'png', 'jpg', 'jpeg', 'docx', 'xlsx', 'csv', 'txt'], accept_multiple_files=True)
                with col3:
                    zugeteilt_an = st.selectbox('Verantwortlicher User', ['User1', 'User2', 'User3', 'User4', 'User5'], index=None)

                st.subheader('Details')
                col1, col15, col2 = st.columns([2, 0.2, 2])
                with col1:
                    kurze_beschreibung = st.text_input('Kurze Beschreibung', value=vorgang_data.at[0, 'Kurze Beschreibung'], max_chars=100)
                with col2:
                    st.text('')
                    i = st.toggle('Vorgang gelöst', value=(vorgang_status == 'Gelöst'))

                sachverhalt = st.text_area('Sachverhalt', value=vorgang_data.at[0, 'Sachverhalt'], max_chars=3000)

                if i:
                    geloest_datum = st.date_input('Gelöst am', value=datetime.date.today())
                    vorgang_status = 'Gelöst'
                
                if st.form_submit_button('Änderungen speichern'):
                    file_names = ", ".join([file.name for file in upload_files])
                    for file in upload_files:
                        with open(os.path.join('Data/tmp', file.name), 'wb') as f:
                            f.write(file.getbuffer())
                    
                    updated_data = pd.DataFrame({
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
                    
                    st.data_editor(updated_data)
                    save_table_append(updated_data, 'PAMS_HICKUP')

def schneller_vorgang():
    erstellungs_datum = datetime.date.today()
    geloest_datum = None
    vorgang_id = uuid.uuid4()
    vorgang_status = 'Neu'
    version = '1.0'
    ersteller = st.session_state.user
    zugeteilt_an = 'User1'
    vorgang_datum = datetime.date.today()
    vorgang_bereich = st.selectbox('Fachbereich', ['DIET', 'C&F', 'LEAF', 'Domestic', 'Management', 'LOG-IN', 'K&N'], index=None)
    vorgang_art = 'Quick'
    vorgang_art_detail = ''
    kosten_ja_nein = 'Nein'
    kosten = 0
    file_upload = st.camera_input('Kamera')
    kurze_beschreibung = st.text_input('Kurze Beschreibung', value='', max_chars=64)
    sachverhalt = st.text_area('Sachverhalt', value='', max_chars=3000)
    if st.button('Vorgang speichern'):
        # save the uploaded file to a temporary directory
        with open(os.path.join('Data/tmp', 'camera.jpg'), 'wb') as f:
            f.write(file_upload.getvalue())
            
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
            'Anhänge': [file_upload],
            'Gelöst am': [geloest_datum],
            'Status': [vorgang_status]
        })
        st.data_editor(vorgang_data)
        save_Table_append(vorgang_data, 'PAMS_HICKUP')
    
def daten_anzeigen(data):

    
    selection = AG_Select_Grid(data, 300, 'PAMS_HICKUP')
    

    st.write(selection)
        
        
        



    # # Datei-Upload
    # uploaded_file = st.file_uploader('Laden Sie eine EML- oder MSG-Datei hoch', type=['eml', 'msg'])

    # if uploaded_file is not None:
    #     process_uploaded_file(uploaded_file)


  
def main():
    st.container(border=True)
    col1,col2 , col3, col4 = st.columns([1, 1, 1,1])    
    # define what option labels and icons to display
    option_data = [
    {'icon': "new", 'label':"Neuer Vorgang"},
    {'icon':"",'label':"Schneller Vorgang"},
    {'icon': "", 'label':"Vorgang bearbeiten"},
    {'icon': "", 'label':"Daten anzeigen"}
    ]

    # override the theme, else it will use the Streamlit applied theme
    over_theme = {'txc_inactive': 'white','menu_background':'#0e2b63','txc_active':'yellow','option_active':'blue'}
    font_fmt = {'font-class':'h2','font-size':'150%'}

    # display a horizontal version of the option bar
    op = hc.option_bar(option_definition=option_data,title=' ',key='PrimaryOption',override_theme=over_theme,font_styling=font_fmt,horizontal_orientation=True)



    if op == 'Neuer Vorgang':
        neuer_vorgang()
    if op == 'Vorgang bearbeiten':
        bearbeiten_vorgang(load_data())
    if op == 'Daten anzeigen':
        daten_anzeigen(load_data())
    if op == 'Schneller Vorgang':
        schneller_vorgang()



