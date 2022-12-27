import streamlit as st
import pandas as pd
import numpy as np
from streamlit_option_menu import option_menu
from Seiten.P_UserLogin import Login

from Data_Class.DB_Daten_SAP import DatenAgregieren as DA
from Data_Class.SQL import SQL_TabellenLadenBearbeiten as SQL
import streamlit_authenticator as stauth

class Einstellungen:
    def __init__(self):
        self.seiteEinstellungen()
        self.menueLaden()
        self.admin()
        self.passwortÄndern()
        self.eingelogterUser()
        self.userLöschen()
        self.UserAnlegen()
        self.authentication_status = Login.Login(self=Login)
        

    def seiteEinstellungen():
        if 'key' not in st.session_state:
            st.session_state['key'] = 'value'
        if 'key' not in st.session_state:
            st.session_state.key = +1

    def menueLaden():
        if st.session_state.rechte == 1:
            selected2 = option_menu(None, ['Ich',"Administration", "Mitarbeiter pflegen", "Daten Update"], 
            icons=['house', 'cloud-upload', "list-task"], 
            menu_icon="cast", default_index=0, orientation="horizontal")
            st.session_state.rechte
            return selected2
        else:
            selected2 = option_menu(None, ['Ich'], 
            icons=['house', 'cloud-upload', "list-task"], 
            menu_icon="cast", default_index=0, orientation="horizontal")
            return selected2            

    def admin():
        def userLöschen(df):

                with st.form("User Löschen"):
                    df=SQL.sql_datenTabelleLaden(SQL.tabelleUser)
                    sel_user = st.selectbox("User",df['username'])
                    X = st.form_submit_button("Löschen")
                    if X:
                        df = df[df['username'] != sel_user]
                        SQL.sql_updateTabelle(SQL.tabelleUser,df)
                        st.success("User erfolgreich gelöscht")
                        st.experimental_rerun()
                    
        def UserAnlegen(df):            
            with st.form("User Anlegen"):
                neuname = st.text_input("name (Anzeigename)",key='name_anlegen')
                neuuser = st.text_input("user (login Name)",key='user_anlegen')
                neupassword = st.text_input("password",key='password_anlegen')
                funktion = st.selectbox("Funktion",["Operativ",'Administration','Management','admin'],key='funktion_anlegen')
                rechte = st.selectbox("Rechte", ['1', '2','3','4','5'], key='rechte_anlegen')
                rechte = int(rechte)
                X = st.form_submit_button("Speichern")
                if X:
                    pw = stauth.Hasher(neupassword)._hash(neupassword)
                    df = df.append({'name':neuname,'username':neuuser,'password':pw,'function':funktion,'rechte':rechte},ignore_index=True)
                    SQL.sql_updateTabelle(SQL.tabelleUser,df)
                    st.success("User erfolgreich angelegt")
                    st.experimental_rerun()

        def eingelogterUser():
            st.write("Eingelogter User")
            st.write(st.session_state.user)
            st.write(st.session_state.name)
        def page():
            df=SQL.sql_datenTabelleLaden(SQL.tabelleUser)            
            userLöschen(df)    
            UserAnlegen(df)
            eingelogterUser()
            st.dataframe(df)
            
        page()      

    def ich():
        st.write("Hallo ")
        st.write(st.session_state.name)
        
        with st.form("Passwort ändern"):
            neupassword = st.text_input("neues password",key='password_anlegen_neu')
            X = st.form_submit_button("änderung speichern")
            if X:
                pw = stauth.Hasher(neupassword)._hash(neupassword)
                df = SQL.sql_datenTabelleLaden(SQL.tabelleUser)
                df.loc[df['username'] == st.session_state.user, 'password'] = pw
                SQL.sql_updateTabelle(SQL.tabelleUser,df)
                st.success("Passwort erfolgreich geändert")
                st.experimental_rerun()
      
  
    def mitarbeiterPflegen():
        #dfMitarbeiter = pd.read_feather('/Users/martinwolf/Python/Superdepot Reporting/data/user.feather') 
        dfMitarbeiter = SQL.sql_datenTabelleLaden(SQL.tabellemitarbeiter)
        #set index 1 to len(dfMitarbeiter)
        dfMitarbeiter.index = np.arange(1, len(dfMitarbeiter) + 1)
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
                        SQL.sql_updateTabelle( tabellenName=SQL.tabellemitarbeiter ,df=dfMitarbeiter)
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
            sel_upload = st.file_uploader("LT22 Update", type=["xlsx"]
            ,key='LT22')
            st.write('Lade deine Datei hoch und klicke auf "Daten Update"')
            if st.button("Daten Update"):
                st.write("Daten werden geupdated")
                if sel_upload is not None:
                    df = pd.read_excel(sel_upload)
                    DA.sapLt22DatenBerechnen(df)


                #TODO Daten werde

    def page():
        selected2 = Einstellungen.menueLaden()
        if selected2 == "Ich":
            Einstellungen.ich()
        if selected2 == "Mitarbeiter pflegen":
            Einstellungen.mitarbeiterPflegen()
        elif selected2 == "Daten Update":
            Einstellungen.datenUpdate()
        elif selected2 == "Administration":
            Einstellungen.admin()

