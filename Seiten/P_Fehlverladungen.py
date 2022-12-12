import base64
import streamlit as st
import pandas as pd
import numpy as np
import extract_msg
from streamlit_option_menu import option_menu
import os
from Data_Class.SQL import datenLadenFehlverladungen , datenSpeichernFehlverladungen
import datetime
import plotly.express as px


def fehlverladungSQL():
    df = datenLadenFehlverladungen()
    return df
def menueLaden():
    selected2 = option_menu(None, ["Dashboard", "Fehlverladung Erfassen",'Fehlverladung Bearbeiten', "Fehlverladung Anzeigen"],
    icons=['house', 'cloud-upload', "list-task"], 
    menu_icon="cast", default_index=0, orientation="horizontal")
    return selected2   

def filterFehlverladungen(df):        
        stati = df['Status'].unique()
        bereiche = df['Bereich'].unique()
        typ = df['Typ'].unique()
        version = df['V'].unique()
        #new column with month by verladedatum
        df['VerladeMonat'] = pd.DatetimeIndex(df['Verladedatum']).month
        df['VerladeMonat'] = df['VerladeMonat'].replace([1,2,3,4,5,6,7,8,9,10,11,12],['Januar','Februar','März','April','Mai','Juni','Juli','August','September','Oktober','November','Dezember'])
        col1, col2 = st.columns(2)
        with col1:
            selstati = st.multiselect('Status', stati, stati)
            monat = st.multiselect('Monat', ['Januar','Februar','März','April','Mai','Juni','Juli','August','September','Oktober','November','Dezember'], ['Januar','Februar','März','April','Mai','Juni','Juli','August','September','Oktober','November','Dezember'])
        with col2:
            selbereiche = st.multiselect('Bereich', bereiche, bereiche)
        col3 , col4 = st.columns(2)
        with col3:
            seltyp = st.multiselect('Typ', typ, typ)
        with col4:
            selversion = st.multiselect('Version', version, version)
        df = df[df['Status'].isin(selstati)]
        df = df[df['Bereich'].isin(selbereiche)]
        df = df[df['Typ'].isin(seltyp)]
        df = df[df['V'].isin(selversion)]
        df = df[df['VerladeMonat'].isin(monat)]
        
        return df

def fehlverladungErfassen(df):
    
    with st.expander("Fehlverladung erfassen"):
        version = 1
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
                dfnew = pd.DataFrame({'ID': [id], 'Bereich': [bereich], 'AD oder OP': [adop], 'Status': [status], 'Kurzbeschreibung': [kurztext], 'Gemeldet von': [gemledetvon], 'Kunde oder Endmarkt': [kunde], 'Verursacher': [verursacher], 'Gespräch durchgeführt?': [gesp], 'Verladedatum': [verladedatum], 'Meldedatum': [meldeDatum], 'Typ': [typ], 'Lieferschein': [leiferschein], 'PO': [po], 'Menge': [menge], 'Einheit': [einheit], 'Mail': [mailpath], 'Upload': [uploadverpath], 'Maßnahme': [maßnahme], 'Beschreibung': [beschreibung] ,'V': [version]})
                
                dfnew = pd.concat([df, dfnew], ignore_index=True)
                datenSpeichernFehlverladungen(dfnew)
                #createnewTable(dfnew, 'issues')
                #dfnew.to_excel('/Users/martinwolf/Python/Superdepot Reporting/data/fehlverladungen.xlsx', index=False)
    
    st.dataframe(df)

def fehlverladungBearbeiten(df):
    df1 = df
    if "counter" not in st.session_state:
        st.session_state.counter = 0
    st.session_state.counter  =  st.selectbox('ID',df['ID'],key='id')
    df = df[df['ID'] == st.session_state.counter]
    id = df['ID'].values[0]
    ktext = df['Kurzbeschreibung'].values[0]
    ls = df['Lieferschein'].values[0]
    pos = df['PO'].values[0]
    ber = df['Bereich'].values[0] 
    adop = df['AD oder OP'].values[0]
    sta = df['Status'].values[0]
    verladeda = df['Verladedatum'].values[0]
    meldeDa = df['Meldedatum'].values[0]
    gemledetv = df['Gemeldet von'].values[0]
    me = df['Menge'].values[0]
    ei = df['Einheit'].values[0]
    beschr = df['Beschreibung'].values[0]
    ma = df['Maßnahme'].values[0]
    typ = df['Typ'].values[0]
    kunde = df['Kunde oder Endmarkt'].values[0]
    verursacher = df['Verursacher'].values[0]
    gesp = df['Gespräch durchgeführt?'].values[0]
    # Anzeige / User bearbeitungen
    col1, col2 = st.columns(2)
    with col1:
        bereich = st.selectbox("Bereich", [ber,'Super-Depot', 'LOG-IN CW', 'LOG-IN C&F', 'LOG-IN Leaf', ],  key='bereich')
        adop = st.selectbox("AD oder OP Fehler", [adop ,'OP', 'AD'],  key='adop')
        status = st.selectbox("Status", [sta,'Offen', 'In Bearbeitung', 'Gelöst'],  key='status')                    
        kurztext = st.text_input("Kurzbeschreibung",key='kurztext',value=ktext)   
        gemledetvon = st.text_input("Gemeldet von",key='gemledetvon',value=gemledetv)
        kunde = st.text_input("Kunde oder Endmarkt",key='kunde',value=kunde) 

        verursacher = st.text_input("Verursacher",key='verursacher',value=verursacher)
        gesp = st.selectbox("Gespräch durchgeführt?", ['','N/A','Ja', 'Nein'],  key='gesp')
    with col2:
        verladedatum = st.date_input("Verladedatum",key='verladedatum',value=verladeda)
        meldeDatum = st.date_input("Meldedatum",key='meldeDatum',value=meldeDa)
        typ = st.selectbox("Typ", [typ,'Schaden','Mehrmenge', 'Fehlmenge','Packvorschrift', 'Kennzeichnung'], key='typ')
        leiferschein = st.text_input("Lieferschein",key='lieferschein',value=ls)
        po = st.text_input("PO",key='po',value=pos)
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
    speichern = st.button("Speichern")

    if speichern:

                version = df['V'].values[0] +1
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
                # add new row to df
                dfnew = pd.DataFrame({'ID': [id],
                                        'Bereich': [bereich],
                                        'AD oder OP': [adop],
                                        'Status': [status],
                                        'Kurzbeschreibung': [kurztext],
                                        'Gemeldet von': [gemledetvon], 
                                        'Kunde oder Endmarkt': [kunde], 
                                        'Verursacher': [verursacher], 
                                        'Gespräch durchgeführt?': [gesp], 
                                        'Verladedatum': [verladedatum], 
                                        'Meldedatum': [meldeDatum], 'Typ': [typ], 
                                        'Lieferschein': [leiferschein], 
                                        'PO': [po], 
                                        'Menge': [menge], 
                                        'Einheit': [einheit], 
                                        'Mail': [mailpath], 
                                        'Upload': [uploadverpath], 
                                        'Maßnahme': [maßnahme], 
                                        'Beschreibung': [beschreibung],
                                        'V':[version]})
                # save to DB and update
                dfnew = pd.concat([df1, dfnew], ignore_index=True)
                datenSpeichernFehlverladungen(dfnew)
                
    st.dataframe(df1)

def fehlverladungAnzeigen(df):
    st.dataframe(df, use_container_width=True, height=160)
    dfbestand = df   
    c1 ,c2 = st.columns(2)
    with c1:
        selid = st.selectbox('ID',dfbestand['ID'])
    with c2:
        selversion = st.selectbox('Version',dfbestand['V'].unique())
    mask = (df['ID'] == selid) & (df['V'] == selversion)
    df = df.loc[mask]
 
    pdffile = df['Upload'].values[0]
    mail = df['Mail'].values[0]
    def pdfAnzeigen(pdffile):
        try:
            if pdffile != "":
                pdf = open(pdffile, 'rb')
                base64_pdf = base64.b64encode(pdf.read()).decode('utf-8')
                pdf_display = f'<embed src="data:application/pdf;base64,{base64_pdf}" width="100%" height="600px" type="application/pdf">'
                st.markdown(pdf_display, unsafe_allow_html=True)
        except:
            st.write("Kein PDF vorhanden")
    def mailAnzeigen(mail):
        try:
            if mail != "":
                # if mail .msg file
                if mail.endswith('.msg'):
                    mail = open(mail, 'rb')
                    msg = extract_msg.Message(mail)
        # print sender name
                    st.write('Sender: {}'.format(msg.sender))
        # print subject
                    st.write('Subject: {}'.format(msg.subject))
        # print body
                    st.write('Body: {}'.format(msg.body))
        # print attachments
        except:
            st.write("Keine Mail vorhanden")
    def fehlverladungImDetail(selid):
        df = dfbestand[dfbestand['ID'] == selid]
        col1, col2, col3 = st.columns(3)
        with col1:
            st.caption('Bereich')
            st.code(df['Bereich'].values[0])
            st.caption('AD oder OP')
            st.code(df['AD oder OP'].values[0])
            st.caption('Status')
            st.code(df['Status'].values[0])
            st.caption('Gemeldet von')
            st.code(df['Gemeldet von'].values[0])
            st.caption('Typ')
            st.code(df['Typ'].values[0])
        with col2:
            st.caption('Kunde oder Endmarkt')
            st.code(df['Kunde oder Endmarkt'].values[0])
            st.caption('Verladedatum')
            st.code(df['Verladedatum'].values[0])
            st.caption('Meldedatum')
            st.code(df['Meldedatum'].values[0])
            st.caption('Verursacher')
            st.code(df['Verursacher'].values[0])
            st.caption('Gespräch durchgeführt?')
            st.code(df['Gespräch durchgeführt?'].values[0])            
        with col3:
            st.caption('Lieferschein')
            st.code(df['Lieferschein'].values[0])
            st.caption('PO')
            st.code(df['PO'].values[0])
            st.caption('Menge')
            st.code(df['Menge'].values[0])
            st.caption('Einheit')
            st.code(df['Einheit'].values[0])
            st.caption('Maßnahme')
            st.code(df['Maßnahme'].values[0])
        st.subheader('Kurzbeschreibung')
        st.code(df['Kurzbeschreibung'].values[0])
        st.subheader('Beschreibung')
        st.code(df['Beschreibung'].values[0])
# Detaildaten anzeigen   
    with st.expander("PDF", expanded=False):
        pdfAnzeigen(pdffile)
    st.write(" ")
    with st.expander("Mail", expanded=False):
        mailAnzeigen(mail)        
    fehlverladungImDetail(selid)

def fehlverladungDashboard(df):
    day1 = datetime.date.today()
    day2 = day1 - datetime.timedelta(days=30)



    def fig_Bar_Chart(df):
        
        # goub by verladetag and count
        dfIssueDay = df.groupby(['Verladedatum'])['Typ'].count().reset_index()
        # create a dataframe with all days in the range
        # dfalldays = pd.DataFrame({'Verladedatum': pd.date_range(start='2022-01-01', end='2023-12-31')})
        # # set index
        # dfalldays = dfalldays.set_index(np.arange(1000,1000+len(dfalldays)))
        # # convert to date
        # dfalldays['Verladedatum'] = dfalldays['Verladedatum'].dt.date
        # # add values from df to dfalldays
        # dfalldays = dfalldays.merge(dfIssueDay, how='left', left_on='Verladedatum', right_on='Verladedatum')
        #create plot
        fig = px.line(dfIssueDay, x="Verladedatum", y="Typ", title="Fehlverladungen pro Tag")
        


        st.plotly_chart(fig, use_container_width=True)

    # def fig_anzahlFehlverladungen(df,day1,day2):
    #     dfIssueDay = df.groupby(['Verladedatum'])['Typ'].count().reset_index()
    #     dfalldays = pd.DataFrame({'Verladedatum': pd.date_range(start='2022-01-01', end='2023-12-31')})
    #     dfalldays = dfalldays.set_index(np.arange(1000,1000+len(dfalldays)))
    #     dfalldays['Verladedatum'] = dfalldays['Verladedatum'].dt.date
    #     # add values from df to dfalldays
    #     dfalldays = dfalldays.merge(dfIssueDay, how='left', left_on='Verladedatum', right_on='Verladedatum')
    #     #count values by day in df
    #     dfalldays = dfalldays.groupby(['Verladedatum']).count()
    #     today = datetime.date.today()
    #     today_minus_30 = today - datetime.timedelta(days=30)

    #     dfalldays = dfalldays.loc[today_minus_30:today]
    #     st.bar_chart(dfalldays, y='Typ', width=0, height=200, use_container_width=True,)
        
    
    #show fig_anzahlFehlverladungen

    fig_Bar_Chart(df)
    
    st.dataframe(df)


def fehlverladungenPage():
    df = datenLadenFehlverladungen()

    selected2 = menueLaden()
    if selected2 == 'Fehlverladung Erfassen':
        fehlverladungErfassen(df)
    elif selected2 == 'Fehlverladung Bearbeiten':
         df = filterFehlverladungen(df)
         fehlverladungBearbeiten(df)
    elif selected2 == 'Fehlverladung Anzeigen':
         df = filterFehlverladungen(df)
         fehlverladungAnzeigen(df)
    elif selected2 == 'Dashboard':
        df = filterFehlverladungen(df)
        fehlverladungDashboard(df)


    
