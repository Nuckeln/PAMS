import streamlit as st
import pandas as pd
import numpy as np
from streamlit_option_menu import option_menu

from Data_Class.DB_Daten_SAP import DatenAgregieren as DA
from Data_Class.SQL import SQL_TabellenLadenBearbeiten as SQL
import Data_Class.DB_Daten_Agg as DB
import streamlit_authenticator as stauth
import datetime

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
            byAll = st.button('Update Alle Daten')
            if byAll:
                st.warning('Daten werden aktualisiert')
                DB.UpdateDaten.updateAlle_Daten_()
                st.success('Daten wurden aktualisiert')
                dftime = pd.DataFrame({'time':[datetime.datetime.now()]})
                dftime['time'] = dftime['time'] + datetime.timedelta(hours=1)
                SQL.sql_updateTabelle('prod_KundenbestellungenUpdateTime',dftime)



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

    def SqlDownload():
        with st.expander("Datenbank Download", expanded=True):
            tabellen = SQL.readAlltablesNames()
            sel_tab = st.selectbox("Tabelle",tabellen)


            if st.button("Zeige Tabelle",key='zeigeTabelle'):
                df = SQL.sql_datenTabelleLaden(sel_tab)
                st.success('Tabelle wurde geladen'+ sel_tab)
                st.dataframe(df)
            if st.button('Lösche Tabelle',key='löschen'):
                SQL.sql_deleteTabelle(sel_tab)
                st.success('Tabelle wurde gelöscht')
            

            if st.button("Download als csv",key='download'):
                def convert_df(df):
                    return df.to_csv(index=False, sep=';', encoding='utf-8').encode("utf-8")
                df = SQL.sql_datenTabelleLaden(sel_tab)
                st.download_button(
                    label="Download",
                    data=convert_df(df),
                    file_name=sel_tab+".csv",
                    mime="text/csv",
                )
                st.success('Tabelle wurde geladen'+ sel_tab)
                st.dataframe(df)

    def checkDB():
        with st.expander("Datenbank Check", expanded=True):
            if st.button("Check"):
                DB.neuUpdate()

    def uploadExcel():
        with st.expander("Datenbank Upload", expanded=True):
            a = st.file_uploader("Upload Excel", type=["xls"])
            if a is not None:
                a = pd.read_excel(a)
                st.dataframe(a)
            table_name = st.text_input("Tabelle Name")
            if st.button("Upload"):
                SQL.sql_updateTabelle(table_name,a)
                st.success("Tabelle wurde erfolgreich erstellt")
                st.experimental_rerun()
    def showOrderDatenGo():
        with st.expander("Bestellungen", expanded=True):
            DB.UpdateDaten.neuUpdate()
            
       

    def page():
        df=SQL.sql_datenTabelleLaden(SQL.tabelleUser)       
        Admin.uploadExcel() 
        Admin.checkDB()
        Admin.SqlDownload()
        Admin.userLöschen(df)    
        Admin.UserAnlegen(df)
        Admin.zeigeDFOrder()
        Admin.showOrderDatenGo()
