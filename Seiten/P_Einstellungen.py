import streamlit as st
import pandas as pd
import numpy as np
from streamlit_option_menu import option_menu

from Data_Class.SQL import datenLadenMitarbeiter , datenSpeichernMitarbeiter , createnewTable, datenLadenUser, updateUser
import streamlit_authenticator as stauth

class Einstellungen:

    def seiteEinstellungen():
        if 'key' not in st.session_state:
            st.session_state['key'] = 'value'
        if 'key' not in st.session_state:
            st.session_state.key = +1

    def menueLaden():
        selected2 = option_menu(None, ["Ich", "Mitarbeiter pflegen", "Daten Update"], 
        icons=['house', 'cloud-upload', "list-task"], 
        menu_icon="cast", default_index=0, orientation="horizontal")
        return selected2            

    def ich():
        st.write("Ich")

        with st.form("User Anlegen"):
            df=datenLadenUser()
            neuname = st.text_input("name",key='name')
            neuuser = st.text_input("user",key='user')
            neupassword = st.text_input("password",key='password')
            # funktion = st.selectbox("Funktion",["Operativ",'Administration','Management'],key='funktion')
            # rechte = st.selectbox("Rechte", ['1', '2','3','4','5'], key='rechte')
            
            X = st.form_submit_button("Speichern")
            if X:
                hasched_passwords = stauth.Hasher(neupassword).generate()
                #df = df.append({'name':name,'username':user,'password':hasched_passwords,'funktion':funktion,'rechte':rechte},ignore_index=True)
                df = df.append({'name':neuname,'username':neuuser,'password':hasched_passwords},ignore_index=True)
                updateUser(df)
                st.success("User erfolgreich angelegt")
        st.dataframe(df) 

    def mitarbeiterPflegen():
        #dfMitarbeiter = pd.read_feather('/Users/martinwolf/Python/Superdepot Reporting/data/user.feather') 
        dfMitarbeiter = datenLadenMitarbeiter()
        with st.expander("Mitarbeiter Anlegen"):
            with st.form(key='my_form', clear_on_submit=True):
                col1, col2 = st.columns(2)
                with col1:
                    #id = dfMitarbeiter.index.max() + 1       
                    name = st.text_input("Name",key='name')
                    oneid = st.text_input("One ID",key='oneId')
                    status = st.radio("Status", ('aktiv', 'inaktiv'),key='status')

                with col2:
                    funktion = st.selectbox('Funktion',["Operativ",'Administration','Management'],key='funktion')
                    firma = st.selectbox("Unternehmen", ['BAT', 'LOG-IN'], key='firma')
                    fachbereich = st.selectbox("Fachbereich", ['Super-Depot'],  key='fachbereich')
                
                speichern = st.form_submit_button("Speichern")  
                if speichern:
                    #check user input  
                    if aktiv == True:
                        aktiv = 1
                    if name == "":
                        st.error("Bitte Name eingeben")
                    elif oneid == "":
                        st.error("Bitte One ID eingeben")
                    else:
                        oneid = int(oneid)
                        dfMitarbeiter = dfMitarbeiter.append({'Name':name,'One ID':oneid,'Funktion':funktion,'Unternehmen':firma,'Fachbereich':fachbereich,'Status':status},ignore_index=True)
                        datenSpeichernMitarbeiter(dfMitarbeiter)
                        #dfMitarbeiter.to_feather('/Users/martinwolf/Python/Superdepot Reporting/data/user.feather')
                        st.success("Mitarbeiter wurde angelegt")

        with st.expander("Mitarbeiter Löschen"):
            with st.form(key='my_form2', clear_on_submit=True):
                selMitarbeiter = st.selectbox("Mitarbeiter", dfMitarbeiter['Name'],key='selMitarbeiter')
                löschen = st.form_submit_button("Löschen")
                if löschen:
                        dfMitarbeiter = dfMitarbeiter[dfMitarbeiter['Name'] != selMitarbeiter]
                        dfMitarbeiter = dfMitarbeiter.reset_index(drop=True)
                        dfMitarbeiter.to_feather('/Users/martinwolf/Python/Superdepot Reporting/data/user.feather')
                
                    #st.experimental_rerun()
        st.dataframe(dfMitarbeiter, use_container_width=True)     

    def datenUpdate():
        st.markdown("Welche Daten möchtest du Updaten?")

        ##TODO Bild von SAP Layout einstellungen und Prozess
        with st.expander('Bewegungsdaten LT22', expanded=False):
                uploaded_file = st.file_uploader("Choose a file")
                if uploaded_file is not None:
                    # To read file as dataframe:
                    df = pd.read_excel(uploaded_file)
                    try:
                        #dfcheck = df
                        #dfcheck.columns = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z','AA','AB','AC']
                        #load file

                        df1 = pd.read_feather('Data/LT22.feather')
                        st.dataframe(df1, use_container_width=True)
                        
                        df1.set_index('Transfer Order Number', inplace=True)
                        df.set_index('Transfer Order Number', inplace=True)
                        df1 = pd.concat([df1[~df1.index.isin(df.index)], df],)
                        df1.reset_index(inplace=True)
                        st.dataframe(df1,use_container_width=True)
                        # #df1.to_feather('Data/LT22.feather')
                        # st.success("Daten wurden erfolgreich aktualisiert")
                    except:
                        st.error("Bitte die richtige Excel Datei auswählen")
                        st.stop()
                    #safeloce file
                    # df.to_feather('Data/temp/uploadlt22.feather')
                    #load file
                    # df1 = pd.read_feather('Data/LT22.feather')
                    # df2 = pd.read_feather('Data/temp/uploadlt22.feather')
                    # df1.set_index('Transfer Order Number', inplace=True)
                    # df2.set_index('Transfer Order Number', inplace=True)
                    # df1 = pd.concat([df1[~df1.index.isin(df2.index)], df2],)
                    # df1.reset_index(inplace=True)
                    # st.dataframe(df1,use_container_width=True)
                    # df1.to_feather('Data/LT22.feather')
                    # st.success("Daten wurden erfolgreich aktualisiert")

def seiteLaden():
    selected2 = Einstellungen.menueLaden()
    if selected2 == "Mitarbeiter pflegen":
        Einstellungen.mitarbeiterPflegen()
    elif selected2 == "Daten Update":
        Einstellungen.datenUpdate()
    elif selected2 == "Ich":
        Einstellungen.ich()

