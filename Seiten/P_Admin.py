import streamlit as st
import pandas as pd
import numpy as np
from streamlit_option_menu import option_menu

from Data_Class.DB_Daten_SAP import DatenAgregieren as DA
from Data_Class.SQL import SQL_TabellenLadenBearbeiten as SQL
import streamlit_authenticator as stauth
from Data_Class.DB_Daten_SAP import DatenAgregieren as DA

class Admin:

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
    
    def zeigeDFOrder():
        with st.expander("Bestellungen", expanded=True):
            df = SQL.sql_datenTabelleLaden('prod_Kundenbestellungen')
            st.dataframe(df)
        with st.expander("Bestellungen Lines", expanded=True):
            #df = dfLines.parquet.gzip
            dfLines = pd.read_parquet('dfLines.parquet.gzip')
            st.dataframe(dfLines)
        with st.expander("Berechnungen", expanded=True):
            dflt22 = pd.read_parquet('Data/upload/lt22.parquet')

            update = st.button("Update lt22")
            if update:
                dflt22 = DA.sapLt22DatenBerechnen(dflt22)
            st.dataframe(dflt22)

    def eingelogterUser():
        st.write("Eingelogter User")
        st.write(st.session_state.user)
        st.write(st.session_state.name)
    def page():
        df=SQL.sql_datenTabelleLaden(SQL.tabelleUser)            
        Admin.userLöschen(df)    
        Admin.UserAnlegen(df)
        Admin.zeigeDFOrder()
        Admin.eingelogterUser()
        st.dataframe(df)            
