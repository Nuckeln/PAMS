import streamlit as st
import pandas as pd
import numpy as np
from streamlit_option_menu import option_menu
from Seiten.P_UserLogin import Login

from Data_Class.DB_Daten_SAP import DatenAgregieren as DA
from Data_Class.SQL import SQL_TabellenLadenBearbeiten as SQL
import streamlit_authenticator as stauth

class Einstellungen:


    def menueLaden():
        if st.session_state.rechte == 1:
            selected2 = option_menu(None, ['Ich',"Administration", "Mitarbeiter pflegen", "Daten Update"], 
            icons=['house', 'cloud-upload', "list-task"], 
            menu_icon="cast", default_index=0, orientation="horizontal")
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
        df = SQL.sql_datenTabelleLaden(SQL.tabellemitarbeiter)
        with st.expander("Mitarbeiter Anlegen"):
            with st.form(key='mitarbeiter_anlegen', clear_on_submit=True):
                col1, col2 = st.columns(2)
                with col1:
                    #id = df.index.max() + 1       
                    name = st.text_input("Name",key='name')
                    oneid = st.text_input("One ID",key='oneId')
                    status = st.radio("Status", ('aktiv', 'inaktiv'),key='status')
                with col2:
                    funktion = st.selectbox('Funktion',["Operativ",'Administration','Management'],key='funktion')
                    firma = st.selectbox("Unternehmen", ['BAT', 'LOG-IN'], key='firma')
                    fachbereich = st.selectbox("Fachbereich", ['Super-Depot'],  key='fachbereich')
                speichern = st.form_submit_button("Speichern")  

                # if speichern:
                #     # #check user input  
                #     # if aktiv == True:
                #     #     aktiv = 1
                #     # if name == "":
                #     #     st.error("Bitte Name eingeben")
                #     # elif oneid == "":
                #     #     st.error("Bitte One ID eingeben")
                #     # else:
                #     #     oneid = int(oneid)
                #         #df = pd.concat([df, pd.DataFrame([[name, oneid, funktion, firma, fachbereich, status]], columns=['Name', 'One ID', 'Funktion', 'Unternehmen', 'Fachbereich', 'Status'])], ignore_index=True)                        #SQL.sql_updateTabelle( tabellenName=SQL.tabellemitarbeiter ,df=df)
                        
                #         st.success("Mitarbeiter wurde angelegt")

        # with st.expander("Mitarbeiter Löschen"):
        #     with st.form(key='my_form2', clear_on_submit=True):
        #         selMitarbeiter = st.selectbox("Mitarbeiter", df['Name'],key='selMitarbeiter')
        #         löschen = st.form_submit_button("Löschen")
        #         if löschen:
        #                 df = df[df['Name'] != selMitarbeiter]
        #                 df = df.reset_index(drop=True)
        #                 df.to_feather('/Users/martinwolf/Python/Superdepot Reporting/data/user.feather')
        # st.dataframe(df, use_container_width=True)     

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

