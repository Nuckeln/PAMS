import streamlit as st
import pandas as pd


#from Data_Class.SQL import read_table,save_table_to_SQL,return_table_names
from Data_Class.AzureStorage import get_blob_file, get_blob_list
from Data_Class.MMSQL_connection import save_Table, read_Table, save_Table_append

from ARCHIV.P_UserLogin import Login

import streamlit_authenticator as stauth
import datetime
import os
import bcrypt


def userverwaltung():
    
    df = read_Table('user')
    
    
    with st.expander('Userverwaltung'):
        all_funktionen = df['function'].unique()
        sel_user = st.selectbox('User',df['name'])
        df_filtered = df[df['name'] == sel_user]
        name = df_filtered['name'].values[0]
        user = df_filtered['username'].values[0]
        password = df_filtered['password'].values[0]
        function = df_filtered['function'].values[0]
        recht = df_filtered['rechte'].values[0]
        st.write(sel_user)
        col1, col2 = st.columns(2)
        with col1:
            st.write('User: ',user)
            st.write('Password: ',password)
        with col2:
            st.write('Funktion: ',function)
            st.write('Recht: ',recht)
        
        col1, col2, st.columns([1.10])
        with col1:
            with st.popover('Zugriffsrechte und Menüoptionen:'):
            # read rechte.md file and display it
                file = open('Rechte.md', 'r')
                rechte = file.read()
                st.write(rechte)
        with col2:
            st.write('')
            
            
        col1, col2, col3, = st.columns(3)
        with col1:
            with st.popover('passwort ändern'):
                new_password = st.text_input('Neues Passwort')
                if st.button('Passwort Speichern'):
                    hashed_password = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()
                    new_user_data = pd.DataFrame({
                        "username": [user],
                        "name": [name],  # oder wie auch immer deine Spalte für den Klarnamen heißt
                        "password": [hashed_password],  # Gehashtes Passwort speichern
                        "function": [function],
                        "rechte": [recht]
                    })
                    save_Table_append(new_user_data, "user")  # Speichert die Daten in der Datenbank
                    st.success('Passwort wurde geändert')
        with col2:
            with st.popover('User löschen'):
                if st.button('Löschen'):
                    df = df[df['name'] != sel_user]
                    save_Table('user',df)
                    st.success('User wurde gelöscht')
                    st.rerun()
        with col3:
            with st.popover('Funktion anpassen'):
                
                new_function = st.selectbox('Funktion',all_funktionen)
                def ordne_funk_rechte_zu(funktion):
                    if funktion == 'Admin Vollzugriff':
                        return 1
                    elif funktion == 'Manager BAT':
                        return 2
                    elif funktion == 'Mitarbeiter BAT AD' :
                        return 3
                    elif funktion == 'Mitarbeiter Fremd':
                        return 4
                    elif funktion == 'Live Bildschirm':
                        return 5
                    elif funktion == 'Mitarbeiter Extern Sachbearbeiter/Teamleiter':
                        return 6
                    
                if st.button('Speichern Funktion'):
                    df_filtered['function'] = new_function
                    df_filtered['rechte'] = ordne_funk_rechte_zu(new_function)
                    #replace old user with new user
                    df = df[df['name'] != sel_user]
                    df = pd.concat([df,df_filtered])
                    save_Table(df,'user')
                    st.success('Funktion wurde geändert')
                    st.rerun()
                    
        

def aktualisier_Issues_Table():
    with st.expander('Issues aktualisieren'):
        upload = st.file_uploader('Issues hochladen')
        if upload != None:
            df = pd.read_excel(upload)
            df = st.data_editor(df)
            if st.button('Hochladen'):
                df['Datum eingetragen'] = df['Datum eingetragen'].astype(str)
                save_table_to_SQL(df, 'PAMS_Issues')
                st.data_editor(df)
                st.success('Issues wurden hochgeladen')
                upload = None

def show_All_Databases():
    with st.expander('Alle Datenbanken'):
        tables = return_table_names()
        st.write(tables)
        sel_Table = st.selectbox('Tabelle',tables)
        df = read_table(sel_Table)
        st.dataframe(df)

def berechtigungen_anzeigen():
#    data = {
#         '1': ["Live Status", 'Reports', 'User Reports', 'Forecast', 'Admin'],
#         '2': ["Live Status", 'Reports', 'User Reports', 'Admin', 'Forecast'],
#         '3': ["Live Status", 'Reports', 'Forecast', None, None],
#         '4': ["Live Status", 'Forecast', None, None, None],
#         '5': ["Live Status", 'Forecast', None, None, None]
#     }
#     df = pd.DataFrame(data)
#     df.to_csv('Data/appData/berechtigungen_user.csv')
    df = pd.read_csv('Data/appData/berechtigungen_user.csv',index_col=0)
    with st.expander('Berechtigungen'):
        col1, col2 = st.columns(2)
        with col1:
            st.data_editor(df)
            if st.button('Speichern'):
                df.to_csv('Data/appData/berechtigungen_user.csv')
                st.success('Berechtigungen wurden gespeichert')
                st.experimental_rerun()
        with col2:
            df_user = read_table('user')
            st.dataframe(df_user)

def mitarbeiterPflegen():
    df = read_table('Mitarbeiter')
    with st.expander('Mitarbeiter pflegen'):
        with st.form(key='mitarbeiter_anlegenAABC', clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1: 
                mitarbeitername = st.text_input("Name",key='mitarbeitername')
                oneid = st.text_input("One ID",key='oneId')
                aktiv = st.radio("Status", ('aktiv', 'inaktiv'),key='aktiv')
            with col2:
                funktion = st.selectbox('Funktion',["Operativ",'Administration','Management'],key='funktion')
                firma = st.selectbox("Unternehmen", ['BAT', 'LOG-IN'], key='firma')
                fachbereich = st.selectbox("Fachbereich", ['Super-Depot'],  key='fachbereich')
            speichern = st.form_submit_button("Speichern")  
            if speichern:
                #check user input  
                if aktiv == True:
                    aktiv = 1
                if mitarbeitername == "":
                    st.error("Bitte Name eingeben")
                elif oneid == "":
                    st.error("Bitte One ID eingeben")
                else:
                    oneid = int(oneid)
                    df = pd.concat([df, pd.DataFrame([[mitarbeitername, oneid, funktion, firma, fachbereich, aktiv]], columns=['Name', 'One ID', 'Funktion', 'Unternehmen', 'Fachbereich', 'Status'])], ignore_index=True)                        #SQL.sql_updateTabelle( tabellenName=SQL.tabellemitarbeiter ,df=df)
                    save_table_to_SQL(df, 'Mitarbeiter')
                    st.success("Mitarbeiter wurde angelegt")
                    #rerun script
                    st.experimental_rerun()
        with st.form(key='mitarbeiterloeschen', clear_on_submit=True):
            selMitarbeiter = st.selectbox("Mitarbeiter", df['Name'],key='selMitarbeiter')
            löschen = st.form_submit_button("Löschen")
            if löschen:
                    df = df[df['Name'] != selMitarbeiter]
                    df = df.reset_index(drop=True)
                    save_table_to_SQL(df, 'Mitarbeiter')
                    st.experimental_rerun()
        st.data_editor(df)


def passwortÄndern():
    Login.newPasswort_Admin(Login)

def userLöschen(df):

        with st.form("User Löschen"):
            df=read_table('user')
            sel_user = st.selectbox("User",df['username'])
            X = st.form_submit_button("Löschen")
            if X:
                df = df[df['username'] != sel_user]
                SQL.sql_updateTabelle(SQL.tabelleUser,df)
                st.success("User erfolgreich gelöscht")
                st.experimental_rerun()


         

def UserAnlegen():      
    df = read_table('user')      
    neuname = st.text_input("name (Anzeigename)",key='name_anlegen')
    neuuser = st.text_input("user (login Name)",key='user_anlegen')
    neupassword = st.text_input("password",key='password_anlegen')
    funktion = st.selectbox("Funktion",["Operativ",'Administration','Management','admin'],key='funktion_anlegen')
    rechte = st.selectbox("Rechte", ['1', '2','3','4','5'], key='rechte_anlegen')
    rechte = int(rechte)
    save_btn = st.button("Save",key='save_btn')
    if save_btn:        
        neupassword = stauth.Hasher(neupassword).generate()
        st.write(neupassword)
        # new_data = {'name': neuname, 'username': neuuser, 'password': neupassword, 'function': funktion, 'rechte': rechte}
        # df = pd.concat([df, pd.DataFrame(new_data, index=[0])], ignore_index=True)
        # st.write()
        #save_table_to_SQL(df,'user2')
        st.success("User erfolgreich angelegt")
        #st.rerun()


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

    with st.expander("Azure", expanded=True):
        df = get_blob_list()
        st.dataframe(df)
    
    sel_file = st.selectbox('Dateien auswählen', df)
    if st.button('Download'):
            file = get_blob_file(sel_file)
            st.download_button('Download', file, sel_file)
            st.success('Download erfolgreich')
    

def adminPage():
    userverwaltung()
# #    aktualisier_Issues_Table()    
#     #show_All_Databases()
# #    mitarbeiterPflegen()
#     UserAnlegen()
#     berechtigungen_anzeigen()
    #Azure()

    # try:
    #     a = os.environ['SQLAZURECONNSTR_DbConnection']
    #     st.write(a)
    # except:
    #     st.error('Keine Azure Connection')

    
    # Admin.erstelleDB()
    # Admin.SqlDownload()
    # Admin.UserAnlegen(df)

    # Admin.zeigeDFOrderLines() 
    # Admin.uploadExcel() 
    # Admin.checkDB()
    # Admin.userLöschen(df)    
    # Admin.UserAnlegen(df)
    #Admin.zeigeDFOrder()
    # Admin.showOrderDatenGo()
