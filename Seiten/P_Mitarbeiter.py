import streamlit as st
import pandas as pd

from Data_Class.DB_Daten_SAP import DatenAgregieren as DA
from Data_Class.SQL import SQL_TabellenLadenBearbeiten as SQL
from Seiten.F_LaufwegLieferschein import pageLaufwegDN



class Daten_Update:      
    def mitarbeiterPflegen(df):
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
                    SQL.sql_updateTabelle('Mitarbeiter' ,df=df)
                    st.success("Mitarbeiter wurde angelegt")
                    #rerun script
                    st.experimental_rerun()
        with st.form(key='mitarbeiterloeschen', clear_on_submit=True):
            selMitarbeiter = st.selectbox("Mitarbeiter", df['Name'],key='selMitarbeiter')
            löschen = st.form_submit_button("Löschen")
            if löschen:
                    df = df[df['Name'] != selMitarbeiter]
                    df = df.reset_index(drop=True)
                    SQL.sql_updateTabelle('Mitarbeiter' ,df=df)
                    st.experimental_rerun()

    def datenUpdate():
        with st.expander('Bewegungsdaten LT22', expanded=True):
            sel_upload = st.file_uploader("LT22 Update", type=["xlsx"]
            ,key='LT22')
            st.write('Lade deine Datei hoch und klicke auf "Daten Update"')
            if st.button("Daten Update"):
                
                if sel_upload is not None:
                    st.warning("Daten werden geupdated bitte auf die Ballons warten")
                    df = pd.read_excel(sel_upload)
                    
                    DA.sapLt22DatenBerechnen(df)
                    #change all columns to string
                    df = df.astype(str)
                    SQL.sql_createTable('Depot_SAP_LT22',df)
                    
                    st.balloons()
                    sel_upload = None
                    st.success("Daten erfolgreich geupdated")
                else:
                    st.warning("Bitte Datei auswählen")

    def page():
        df = SQL.sql_datenTabelleLaden('Mitarbeiter')

        Daten_Update.mitarbeiterPflegen(df)
        st.dataframe(df)
        Daten_Update.datenUpdate()

class User :            
    def ich():
        st.write("Hallo ")
        st.write(st.session_state.name)
        
        with st.form("Passwort ändern"):
            neupassword = st.text_input("neues password",key='password_anlegen_neu')
            X = st.form_submit_button("änderung speichern")
            # if X:
            #     pw = stauth.Hasher(neupassword)._hash(neupassword)
            #     df = SQL.sql_datenTabelleLaden(SQL.tabelleUser)
            #     df.loc[df['username'] == st.session_state.user, 'password'] = pw
            #     SQL.sql_updateTabelle(SQL.tabelleUser,df)
            #     st.success("Passwort erfolgreich geändert")
            #     st.experimental_rerun()