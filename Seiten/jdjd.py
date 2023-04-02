import Data_Class.SQL as SQL
import streamlit as st
import Data_Class.AzureStorage as Azure
import pandas as pd
import numpy as np

def FehlverladungNeu():
    
    with st.expander("Fehlverladung erfassen"):
        
        with st.form(key='my_form', clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                bereich = st.selectbox("Bereich", ['Super-Depot', 'LOG-IN CW', 'LOG-IN C&F', 'LOG-IN Leaf', ],  key='bereich')
                adop = st.selectbox("AD oder OP Fehler", ['OP', 'AD'],  key='adop')
                status = st.selectbox("Status", ['Offen', 'In Bearbeitung', 'Erledigt'],  key='status')                    
                kurztext = st.text_input("Kurzbeschreibung",key='kurztext')   
                gemledetvon = st.text_input("Gemeldet von",key='gemledetvon')
                kunde = st.text_input("Kunde oder Endmarkt",key='kunde') 
                verursacher = st.text_input("Verursacher",key='verursacher')
                gesp = st.selectbox("Gespräch durchgeführt?", ['','N/A','Ja', 'Nein'],  key='gesp')
            with col2:
                verladedatum = st.date_input("Verladedatum",key='verladedatum')
                meldeDatum = st.date_input("Meldedatum",key='meldeDatum')
                typ = st.selectbox("Typ", ['Schaden','Mehrmenge', 'Fehlmenge','Packvorschrift', 'Kennzeichnung'], key='typ')
                leiferschein = st.text_input("Lieferschein",key='lieferschein')
                po = st.text_input("PO",key='po')
                menge = st.text_input("Menge ",key='menge') 
                einheit = st.selectbox("Einheit", ['','TH', 'KG', 'CS', 'Out'],  key='einheit')                                                   
            mailpath = ""
            uploadverpath = ""
            maßnahme =  st.text_area("Maßnahme",key='maßnahme')
            st.write("Achtung: Es ist jeweils nur ein Dokument pro Auswahl (Mail oder Datei) Zum Hochladen möglich")
            col3, col4 = st.columns(2)
            with col3:
                mail = st.file_uploader("Mail",type=['msg','eml'],key='mail')                 
            with col4:
                uploadAndere = st.file_uploader("Upload",type=['pdf'],key='uploadAndere')
        
            beschreibung = st.text_area("Beschreibung",key='beschreibung')
            speichern = st.form_submit_button("Speichern",)  

            if speichern:
                st.write("Fehlverladung wurde gespeichert")
                file_name = ""
                if mail is not None:
                    mailpath = '' + mail.name
                    file_name = Azure.upload_file_to_blob_storage(mailpath, mail,'SD-Issues')
                
                filename2 = ""
                if uploadAndere is not None:
                    uploadverpath = '' + uploadAndere.name
                    filename2 = Azure.upload_file_to_blob_storage(uploadverpath, uploadAndere,'SD-Issues')
                
                id = np.random.randint(10000,99999)
                dfnew = pd.DataFrame({'ID': [id], 'Bereich': [bereich], 'AD oder OP': [adop], 'Status': [status], 'Kurzbeschreibung': [kurztext], 'Gemeldet von': [gemledetvon], 'Kunde oder Endmarkt': [kunde], 'Verursacher': [verursacher], 'Gespräch durchgeführt?': [gesp], 'Verladedatum': [verladedatum], 'Meldedatum': [meldeDatum], 'Typ': [typ], 'Lieferschein': [leiferschein], 'PO': [po], 'Menge': [menge], 'Einheit': [einheit], 'Mail': [file_name], 'Upload': [filename2], 'Maßnahme': [maßnahme], 'Beschreibung': [beschreibung]})
                
              #  dfnew = pd.concat([df, dfnew], ignore_index=True)
                SQL.SQL_TabellenLadenBearbeiten.sql_createTable('issues',dfnew)