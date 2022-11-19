import base64
import streamlit as st
import pandas as pd
import numpy as np
import extract_msg
from streamlit_option_menu import option_menu
from Test.toFeather import *
import os
from data_Class.SQL import createnewTable , datenLadenFehlverladungen , datenLadenMitarbeiter , datenSpeichernFehlverladungen , datenSpeichernMitarbeiter



class Fehlverladungen:

    def menueLaden():
        selected2 = option_menu(None, ["Dashboard", "Fehlverladung Erfassen",'Fehlverladung Bearbeiten', "Fehlverladung Anzeigen"],
        icons=['house', 'cloud-upload', "list-task"], 
        menu_icon="cast", default_index=0, orientation="horizontal")
        return selected2   

    def fehlverladungErfassen():
        
        with st.expander("Fehlverladung erfassen"):
            with st.form(key='my_form', clear_on_submit=True):
                col1, col2 = st.columns(2)
                with col1:
                    bereich = st.selectbox("Bereich", ['Super-Depot', 'LOG-IN CW', 'LOG-IN C&F', 'LOG-IN Leaf', ],  key='bereich')
                    adop = st.selectbox("AD oder OP Fehler", ['OP', 'AD'],  key='adop')
                    status = st.selectbox("Status", ['Offen', 'In Bearbeitung', 'Gelöst'],  key='status')                    
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
                st.write("Achtung: Es kann nur ein File pro Typ Mail/Andere Uploads hochgeladen werden")
                col3, col4 = st.columns(2)
                with col3:
                    mail = st.file_uploader("Mail",type=['msg','eml'],key='mail')                 
                with col4:
                    uploadAndere = st.file_uploader("Upload",type=['pdf'],key='uploadAndere')
         
                beschreibung = st.text_area("Beschreibung",key='beschreibung')
                speichern = st.form_submit_button("Speichern",)  

                if speichern:
                    st.write("Fehlverladung wurde gespeichert")
                    if mail is not None:
                        mailpath1 = '/Users/martinwolf/Python/Superdepot Reporting/data/temp/' + mail.name
                        with open(mailpath1,
                                    'wb') as f:
                                f.write(mail.getbuffer())
                                mailpath = (str(mailpath1))
                                st.write(mailpath)
                    if uploadAndere is not None:
                        uploadverpath1 = '/Users/martinwolf/Python/Superdepot Reporting/data/temp/' + uploadAndere.name
                        with open(uploadverpath1,
                                    'wb') as f:
                                f.write(uploadAndere.getbuffer())
                                uploadverpath = (str(uploadverpath1))
                                st.write(uploadverpath)
                    
                    id = np.random.randint(10000,99999)
                    dfnew = pd.DataFrame({'ID': [id], 'Bereich': [bereich], 'AD oder OP': [adop], 'Status': [status], 'Kurzbeschreibung': [kurztext], 'Gemeldet von': [gemledetvon], 'Kunde oder Endmarkt': [kunde], 'Verursacher': [verursacher], 'Gespräch durchgeführt?': [gesp], 'Verladedatum': [verladedatum], 'Meldedatum': [meldeDatum], 'Typ': [typ], 'Lieferschein': [leiferschein], 'PO': [po], 'Menge': [menge], 'Einheit': [einheit], 'Mail': [mailpath], 'Upload': [uploadverpath], 'Maßnahme': [maßnahme], 'Beschreibung': [beschreibung]})
                    dfa = datenLadenFehlverladungen()
                    dfnew = pd.concat([dfa, dfnew], ignore_index=True)
                    datenSpeichernFehlverladungen(dfnew)
                    #createnewTable(dfnew, 'issues')
        dfa = datenLadenFehlverladungen()
        st.dataframe(dfa)


    def fehlverladungBearbeiten():
        #TODO: Bearbeitung ist noch nicht fertig
        #Löschen ist fertig 
        df = pd.read_feather('/Users/martinwolf/Python/Superdepot Reporting/data/issues.feather')
        dfbestand = df
        with st.expander("Fehlverladung bearbeiten"):
            st.header("Finger weg ist noch zu Bugy")
        # Bearbeiten
            with st.form(key='my_form2', clear_on_submit=False):

                input  =  st.selectbox('ID',df['ID'],key='id')
                df = df[df['ID'] == input]

                bearbeiten = st.form_submit_button("Laden")
                if bearbeiten:
                    #load data
                    id = df['ID'].values[0]
                    ktext = df['Kurzbeschreibung'].values[0]
                    ls = df['Lieferschein'].values[0]
                    pos = df['PO'].values[0]
                    ber = df['Bereich'].values[0]
                    ado = df['AD oder OP Fehler'].values[0]
                    sta = df['Status'].values[0]
                    verladeda = df['Verladedatum'].values[0]
                    meldeDa = df['Meldedatum'].values[0]
                    gemledetv = df['Gemeldet von'].values[0]
                    me = df['Menge'].values[0]
                    ei = df['Einheit'].values[0]
                    beschr = df['Beschreibung'].values[0]
                    # Anzeige / User bearbeitungen
                    col1, col2 = st.columns(2)
                    with col1:                        
                        kurztext = st.text_input("Kurzbeschreibung", value= ktext ,key='kurztext')    
                        leiferschein = st.text_input("Lieferschein",value=ls, key='lieferschein')
                        po = st.text_input("PO",value=pos, key='po')
                        bereich = st.selectbox("Bereich", [ber,'Super-Depot', 'LOG-IN CW', 'LOG-IN C&F', 'LOG-IN Leaf', ], key='bereich')
                        adop = st.selectbox("AD oder OP Fehler", [ado,'OP', 'AD'],  key='adop')
                        status = st.selectbox("Status", [sta,'Offen', 'In Bearbeitung', 'Gelöst'],  key='status')
                    with col2:
                        verladedatum = st.date_input("Verladedatum",value=verladeda ,key='verladedatum')
                        meldeDatum = st.date_input("MeldeDatum",key='meldeDatum',value=meldeDa)
                        gemledetvon = st.text_input("Gemeldet von",key='gemledetvon',value=gemledetv)
                        menge = st.text_input("Menge ",key='menge',value=me) 
                        einheit = st.text_input("In Einheit",key='einheit',value=ei)
                        st.text(id)
                    #Datei Upload          
                    mailpath = ""
                    uploadverpath = ""
                    st.write("Achtung: Es kann nur ein File pro Typ Mail/Andere Uploads hochgeladen werden")
                    st.write("Achtung: Die alten Files werden archiviert und nicht gelöscht")
                    col3, col4 = st.columns(2)
                    with col3:
                        mail = st.file_uploader("Mail",type=['msg','eml'],key='mail')                 
                    with col4:
                        uploadAndere = st.file_uploader("Upload",type=['pdf'],key='uploadAndere')
                    bescheibung =  st.text_area("Beschreibung",value=beschr, height=200, key='beschreibung')
                    # Speicher Eingaben     
                    speichern = st.form_submit_button("Speichern")                      
                    if speichern:
                        st.write("Fehlverladung wurde gespeichert")
                        if mail is not None:
                            mailpath1 = '/Users/martinwolf/Python/Superdepot Reporting/data/temp/' + mail.name
                            with open(mailpath1,
                                        'wb') as f:
                                    f.write(mail.getbuffer())
                                    mailpath = (str(mailpath1))
                                    st.write(mailpath)
                        if uploadAndere is not None:
                            uploadverpath1 = '/Users/martinwolf/Python/Superdepot Reporting/data/temp/' + uploadAndere.name
                            with open(uploadverpath1,
                                        'wb') as f:
                                    f.write(uploadAndere.getbuffer())
                                    uploadverpath = (str(uploadverpath1))
                                    st.write(uploadverpath)



                        # Ändern im Datenframe
                        dfbestand.loc[dfbestand['ID'] == id, 'Kurzbeschreibung'] = kurztext
                        dfbestand.loc[dfbestand['ID'] == id, 'Lieferschein'] = leiferschein
                        dfbestand.loc[dfbestand['ID'] == id, 'PO'] = po
                        dfbestand.loc[dfbestand['ID'] == id, 'Bereich'] = bereich
                        dfbestand.loc[dfbestand['ID'] == id, 'AD oder OP Fehler'] = adop
                        dfbestand.loc[dfbestand['ID'] == id, 'Status'] = status
                        dfbestand.loc[dfbestand['ID'] == id, 'Verladedatum'] = verladedatum
                        dfbestand.loc[dfbestand['ID'] == id, 'Meldedatum'] = meldeDatum
                        dfbestand.loc[dfbestand['ID'] == id, 'Gemeldet von'] = gemledetvon
                        dfbestand.loc[dfbestand['ID'] == id, 'Menge'] = menge
                        dfbestand.loc[dfbestand['ID'] == id, 'Einheit'] = einheit
                        dfbestand.loc[dfbestand['ID'] == id, 'Beschreibung'] = bescheibung
                        
                        #dfbestand.loc[dfbestand['ID'] == id, 'Mail'] = mailpath


                        #dfbestand = df.append({'ID': id,'Kurzbeschreibung': kurztext, 'Lieferschein': leiferschein, 'PO': po, 'Bereich': bereich, 'AD oder OP Fehler': adop, 'Status': status, 'Verladedatum': verladedatum, 'Meldedatum': meldeDatum, 'Gemeldet von': gemledetvon, 'Menge': menge, 'Einheit': einheit, 'Beschreibung': bescheibung, 'Mail': mailpath, 'Upload': uploadverpath}, ignore_index=True)
                        dfbestand.to_feather('/Users/martinwolf/Python/Superdepot Reporting/data/issues.feather')                       
        #Löschen
        with st.form(key='my_form6', clear_on_submit=True):
                selid  =  st.selectbox('ID',dfbestand['ID'],key='selid')
                loeschen = st.form_submit_button("Löschen")
                if loeschen:
                    dfbestand = dfbestand[dfbestand['ID'] != selid]
                    dfbestand.reset_index(drop=True)
                    dfbestand.to_feather('/Users/martinwolf/Python/Superdepot Reporting/data/issues.feather')  
                    st.success("Fehlverladung wurde gelöscht")
       
        st.dataframe(dfbestand.head(10), use_container_width=True)


    def fehlverladungAnzeigen():
        dfbestand = datenLadenFehlverladungen()
        selid = st.selectbox('ID',dfbestand['ID'])
        df = dfbestand[dfbestand['ID'] == selid]
        pdffile = df['Upload'].values[0]
        #load pdf into streamlit
        if pdffile != "":
            pdf = open(pdffile, 'rb')
            base64_pdf = base64.b64encode(pdf.read()).decode('utf-8')
            pdf_display = f'<embed src="data:application/pdf;base64,{base64_pdf}" width="100%" height="600px" type="application/pdf">'
            st.markdown(pdf_display, unsafe_allow_html=True)
        mail = df['Mail'].values[0]
        if mail != "":
            # if mail .msg file
            if mail.endswith('.msg'):
                mail = open(mail, 'rb')
                msg = extract_msg.Message(mail)
# print sender name
                st.write('Sender: {}'.format(msg.sender))


        st.dataframe(df, use_container_width=True)

def fehlverladungenPage():
    selected2 = Fehlverladungen.menueLaden()
    if selected2 == 'Fehlverladung Erfassen':
        Fehlverladungen.fehlverladungErfassen()
    elif selected2 == 'Fehlverladung Bearbeiten':
        Fehlverladungen.fehlverladungBearbeiten()
    elif selected2 == 'Fehlverladung Anzeigen':
        Fehlverladungen.fehlverladungAnzeigen()


    
