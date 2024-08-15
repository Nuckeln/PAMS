import streamlit as st
import pandas as pd


#from Data_Class.SQL import read_table,save_table_to_SQL,return_table_names
from Data_Class.AzureStorage import get_blob_file, get_blob_list
from Data_Class.MMSQL_connection import save_Table, read_Table, save_Table_append

import time
import bcrypt
@st.fragment

def berechtigungen(user_berechtigungen):
        funktionen = ['Depot Live Status', "LC Monitor", 'Depot Reports', 'Forecast', 'Lagerverwaltung','C&E check','Hick-Up','Admin']
        if user_berechtigungen == None:
            user_berechtigungen = ''
        
        col1, col2, col3, col4 = st.columns(4)
        columns = [col1, col2, col3, col4]
        selected_labels = []
        input_list_count = len(funktionen) // 4  # Anzahl der Elemente in jeder Spalte
        for i in range(len(funktionen)):
            unique_label = funktionen[i]
            unique_key = 'HE' + str(i + 1)
            
            # Wähle die entsprechende Spalte aus
            current_col = columns[i // input_list_count]
            # prüfe ob die Checkbox ausgewählt ist anhand ob es in user_berechtigungen ist
            #def_value = unique_label in user_berechtigungen
            
            # Erstelle die Checkbox in der aktuellen Spalte
            value = current_col.checkbox(unique_label, key=unique_key, value=unique_label in user_berechtigungen)
            
            # Wenn die Checkbox ausgewählt ist, füge ihr Label dem selected_labels Array hinzu
            if value:
                selected_labels.append(unique_label)
        return selected_labels        
     

def userverwaltung_neu():

    with st.expander('Userverwaltung'):
        if "df_user" not in st.session_state:
                st.session_state.df_user = read_Table('user')
                #sort by 'Erstellungsdatum'
                
        event = st.dataframe(
            st.session_state.df_user,
            key="data",
            on_select="rerun",
            selection_mode=["single-row"],
            use_container_width=    True,
        )
        if event == None:
            st.warning("Bitte einen User auswählen")
            pass
            return
        
        sel_id = list(event.selection.values())[0]   
        #wert aus df ermitteln in Zeile sel_id
        df_org = st.session_state.df_user
        try:
            df_filtered = st.session_state.df_user.iloc[sel_id]
            # all_funktionen = df['function'].unique()

            name = df_filtered['name'].values[0]
            user = df_filtered['username'].values[0]
            password = df_filtered['password'].values[0]
            function = df_filtered['function'].values[0]
            recht = df_filtered['rechte'].values[0]
            user_berechtigungen = df_filtered['berechtigungen'].values[0]

            col1, col2 = st.columns(2)
            with col1:
                st.write('User: ',user)
                st.write('Password: ',password)
            with col2:
                st.write('Funktion: ',function)
                st.write('Recht: ',recht)
            
                
            col1, col2, col3, = st.columns(3)
            with col1:
                with st.popover('passwort ändern'):
                    with st.form('Passwort ändern'):
                        new_password = st.text_input('Neues Passwort')
                        if st.form_submit_button('Speichern'):
                            hashed_password = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()
                            new_user_data = pd.DataFrame({
                                "username": [user],
                                "name": [name],  # oder wie auch immer deine Spalte für den Klarnamen heißt
                                "password": [hashed_password],  # Gehashtes Passwort speichern
                                "function": [function],
                                "rechte": [recht]
                            })
                            st.data_editor(new_user_data)
                            save_Table_append(new_user_data, "user")  # Speichert die Daten in der Datenbank
                            st.success('Passwort wurde geändert')
                            with st.spinner('Passwort wurde geändert'):
                                time.sleep(2)
                                
                            st.rerun()
            with col2:
                pass
                with st.popover('User löschen'):
                    with st.form('User'):
                        if st.form_submit_button('Löschen'):
                            df = df_org[df_org['name'] != name]
                            save_Table(df,'user')
                            st.success('User wurde gelöscht')
                            with st.spinner('User wird gelöscht'):
                                time.sleep(2)
                                st.rerun()
            with col3:
                pass
                # with st.popover('Funktion anpassen'):
                    
                #     with st.form('Funktion ändern'):
                #         new_function = st.selectbox('Funktion',['Manager BAT AD','Mitarbeiter BAT AD','Mitarbeiter Fremd','Live Bildschirm','Mitarbeiter Extern Sachbearbeiter/Teamleiter'])
                #         # pages = ['Depot Live Status', "LC Monitor", 'Depot Reports', 'Forecast', 'Lagerverwaltung','C&E check','SFG Reports','TALL','Admin']
                        
                #         def ordne_funk_rechte_zu(funktion):
                #             if funktion == 'admin':
                #                 return 1
                #             elif funktion == 'Manager BAT':
                #                 return 2
                #             elif funktion == 'Mitarbeiter BAT AD' :
                #                 return 3
                #             elif funktion == 'Mitarbeiter Fremd':
                #                 return 4
                #             elif funktion == 'Live Bildschirm':
                #                 return 5
                #             elif funktion == 'Mitarbeiter Extern Sachbearbeiter/Teamleiter':
                #                 return 6
                #         if st.form_submit_button('Speichern Funktion'):
                #             df_filtered['function'] = new_function
                #             df_filtered['rechte'] = ordne_funk_rechte_zu(new_function)
                #             #replace old user with new user
                #             df = df[df['name'] != sel_user]
                #             df = pd.concat([df,df_filtered])
                #             save_Table(df,'user')
                #             st.success('Funktion wurde geändert')
                #             with st.spinner('Funktion wurde geändert'):
                #                 time.sleep(2)
                #             st.rerun()
            
            with st.popover('Berechtigungen', use_container_width=True):
                    selected_labels = berechtigungen(user_berechtigungen)
                    # selected_labels = berechtigungen(user_berechtigungen)
                    if st.button('Speichern Berechtigungen'):
                        #erstelle str aus liste trenne mit ','
                        selected_labels = ', '.join(selected_labels)
                        # add new user data
                        new_user_data = pd.DataFrame({
                            "username": [user],
                            "name": [name],  # oder wie auch immer deine Spalte für den Klarnamen heißt
                            "password": [password],  # Gehashtes Passwort speichern
                            "function": [function],
                            "rechte": [recht],
                            "berechtigungen": [selected_labels]
                        })
                        # ersetze alten user mit neuen user
                        df = df_org[df_org['name'] != name]
                        df = pd.concat([df,new_user_data])
                        save_Table(df,'user')
                        #reset session state
                        st.session_state.df_user = read_Table('user')
                        st.success('Berechtigungen wurden gespeichert')
                        with st.spinner('Berechtigungen werden gespeichert'):
                            time.sleep(2)
                        st.rerun()
        except:
            st.error('Wählen Sie einen User aus')
            
def userverwaltung():
    
    df = read_Table('user')
    
    
    with st.expander('Userverwaltung'):
        st.dataframe(df)
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
                with st.form('Passwort ändern'):
                    new_password = st.text_input('Neues Passwort')
                    if st.form_submit_button('Speichern'):
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
                        with st.spinner('Passwort wurde geändert'):
                            time.sleep(2)
                            
                        st.rerun()
        with col2:
            with st.popover('User löschen'):
                with st.form('User'):
                    if st.form_submit_button('Löschen'):
                        df = df[df['name'] != sel_user]
                        save_Table(df,'user')
                        st.success('User wurde gelöscht')
                        with st.spinner('User wird gelöscht'):
                            time.sleep(2)
                            
                        st.rerun()
        with col3:
            with st.popover('Funktion anpassen'):
                
                with st.form('Funktion ändern'):
                    new_function = st.selectbox('Funktion',all_funktionen)
                    # pages = ['Depot Live Status', "LC Monitor", 'Depot Reports', 'Forecast', 'Lagerverwaltung','C&E check','SFG Reports','TALL','Admin']
                    
                    def ordne_funk_rechte_zu(funktion):
                        if funktion == 'admin':
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
                    if st.form_submit_button('Speichern Funktion'):
                        df_filtered['function'] = new_function
                        df_filtered['rechte'] = ordne_funk_rechte_zu(new_function)
                        #replace old user with new user
                        df = df[df['name'] != sel_user]
                        df = pd.concat([df,df_filtered])
                        save_Table(df,'user')
                        st.success('Funktion wurde geändert')
                        with st.spinner('Funktion wurde geändert'):
                            time.sleep(2)
                        st.rerun()
                    
       
def aktualisier_Issues_Table():
    with st.expander('Issues aktualisieren'):
        upload = st.file_uploader('Issues hochladen')
        if upload != None:
            df = pd.read_excel(upload)
            df = st.data_editor(df)
            if st.button('Hochladen'):
                df['Datum eingetragen'] = df['Datum eingetragen'].astype(str)
                save_Table(df, 'PAMS_Issues')
                st.data_editor(df)
                st.success('Issues wurden hochgeladen')
                upload = None

def Azure():    

    with st.expander("Azure", expanded=False):
        df = get_blob_list()
        st.dataframe(df)
    
    sel_file = st.selectbox('Dateien auswählen', df)
    if st.button('Download'):
            file = get_blob_file(sel_file)
            st.download_button('Download', file, sel_file)
            st.success('Download erfolgreich')
    

def adminPage():
    #a = berechtigungen()
    #st.write(a)
    userverwaltung_neu() 
    st.button("Inflate more balloons", help="Full rerun")
   #userverwaltung()
    aktualisier_Issues_Table()
    Azure()

