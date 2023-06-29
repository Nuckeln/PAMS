import streamlit as st
import pandas as pd

from Data_Class.DB_Daten_SAP import DatenAgregieren as DA
from Data_Class.SQL import SQL_TabellenLadenBearbeiten as SQL

from Seiten.P_UserLogin import Login

import streamlit_authenticator as stauth
import datetime
import Data_Class.AzureStorage

class Admin:

    def passwortÄndern():
        Login.newPasswort_Admin(Login)

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
                SQL.sql_updateTabelle('user',df)
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
            saveLoc = st.button('Als Locale File ablegen')
            if saveLoc:
                st.warning('Daten werden aktualisiert')
                DB.UpdateDaten.updateAlle_Daten_()
                df.to_parquet('prod_Kundenbestellungen.parquet.gzip')



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

    def zeigeDFOrderLines():
        with st.expander("Bestellungen Lines", expanded=True):
            #df = dfLines.parquet.gzip
            if st.button("Update"):
                heute = datetime.datetime.now()
                vorgestern = heute - datetime.timedelta(days=6)
                dfLines = DB.DatenAgregieren.orderDatenLines(heute , vorgestern)
                st.dataframe(dfLines)
                dfLines.to_parquet('dfLines.parquet.gzip')
                st.success("Daten wurden aktualisiert")
            # heute = datetime.datetime.now()
            # gestern = heute - datetime.timedelta(days=1)
            # dfLines = DB.DatenAgregieren.orderDatenLines(heute , gestern)
            # st.dataframe(dfLines)
    def erstelleDB():
        with st.expander("Datenbank Erstellen", expanded=True):
            name = st.text_input("Datenbank Name")
            df = st.file_uploader("Upload Excel", type=["xlsx"])
            if df is not None:
                df = pd.read_excel(df)
                st.dataframe(df)
            if st.button("Erstellen"):
                if df is not None:
                    SQL.sql_createTable(name,df)
                    st.success("Datenbank wurde erfolgreich erstellt")
                else:
                    st.warning("Keine Datenbank angelegt")
                st.experimental_rerun()
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

    def Azure():    

        def downloadFilesFromBlob():
            st.warning('Datei in Blob Donwloaden vorher Filenamewählen!!!')
            Data_Class.AzureStorage.st_Azure_downloadBtn()

        def showDateinBlob():
            st.warning('Zeige alle Dateien in Blob')
            df = SQL.sql_datenTabelleLaden('AzureStorage')
            st.dataframe(df)
        def löschealleFiles():
            Data_Class.AzureStorage.st_Azure_deleteBtn()
        def ladeFileinBlob():
            df = SQL.sql_datenTabelleLaden('AzureStorage')
            st.warning('Datei in Blob laden vorher die Anwendung auswählen!!!')
            anwendugen = df['anwendung'].unique()
            sel_anwendung = st.selectbox('Anwendung',anwendugen)


            Data_Class.AzureStorage.st_Azure_uploadBtn(sel_anwendung)


        with st.expander("Azure", expanded=True):
            downloadFilesFromBlob()
            ladeFileinBlob()
            showDateinBlob()
            löschealleFiles()
    def page():
        df=SQL.sql_datenTabelleLaden('user')      

        Admin.Azure()
        Admin.erstelleDB()
        Admin.SqlDownload()
        Admin.UserAnlegen(df)
        Admin.passwortÄndern()

        # Admin.zeigeDFOrderLines() 
        # Admin.uploadExcel() 
        # Admin.checkDB()
        # Admin.userLöschen(df)    
        # Admin.UserAnlegen(df)
        #Admin.zeigeDFOrder()
       # Admin.showOrderDatenGo()
