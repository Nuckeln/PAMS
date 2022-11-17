import streamlit as st
import pandas as pd
import numpy as np
from streamlit_option_menu import option_menu
from streamlit import cache
import Test.rerun 
from Test.toFeather import *
#from Data_Class.C_Daten_LT22 import *

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
    def mitarbeiterPflegen():
        dfMitarbeiter = pd.read_feather('/Users/martinwolf/Python/Superdepot Reporting/data/user.feather') 
        with st.expander("Mitarbeiter Anlegen"):
            with st.form(key='my_form', clear_on_submit=True):
                col1, col2 = st.columns(2)
                with col1:
                    #id = dfMitarbeiter.index.max() + 1       
                    name = st.text_input("Name",key='name')
                    oneid = st.text_input("One ID",key='oneId')
                with col2:
                    funktion = st.selectbox('Funktion',["Operativ",'Administration','Management'],key='funktion')
                    firma = st.selectbox("Unternehmen", ['BAT', 'LOG-IN'], key='firma')
                    fachbereich = st.selectbox("Fachbereich", ['Super-Depot'],  key='fachbereich')
                
                speichern = st.form_submit_button("Speichern")  
                if speichern:
                    #check user input  
                    if name == "":
                        st.error("Bitte Name eingeben")
                    elif oneid == "":
                        st.error("Bitte One ID eingeben")
                    else:
                        oneid = int(oneid)
                        dfMitarbeiter = dfMitarbeiter.append({'Name':name,'One ID':oneid,'Funktion':funktion,'Unternehmen':firma,'Fachbereich':fachbereich},ignore_index=True)
                        dfMitarbeiter.to_feather('/Users/martinwolf/Python/Superdepot Reporting/data/user.feather')
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
                        dfcheck = df
                        dfcheck.columns = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z','AA','AB','AC']
                        df.to_feather('Data/temp/uploadlt22.feather')
                        #load file
                        df1 = pd.read_feather('Data/LT22.feather')
                        df2 = pd.read_feather('Data/temp/uploadlt22.feather')
                        df1.set_index('Transfer Order Number', inplace=True)
                        df2.set_index('Transfer Order Number', inplace=True)
                        df1 = pd.concat([df1[~df1.index.isin(df2.index)], df2],)
                        df1.reset_index(inplace=True)
                        st.dataframe(df1,use_container_width=True)
                        #df1.to_feather('Data/LT22.feather')
                        st.success("Daten wurden erfolgreich aktualisiert")
                    except:
                        st.error("Bitte die richtige Excel Datei auswählen")
                        st.stop()
                    #safeloce file
                    df.to_feather('Data/temp/uploadlt22.feather')
                    #load file
                    df1 = pd.read_feather('Data/LT22.feather')
                    df2 = pd.read_feather('Data/temp/uploadlt22.feather')
                    df1.set_index('Transfer Order Number', inplace=True)
                    df2.set_index('Transfer Order Number', inplace=True)
                    df1 = pd.concat([df1[~df1.index.isin(df2.index)], df2],)
                    df1.reset_index(inplace=True)
                    st.dataframe(df1,use_container_width=True)
                    df1.to_feather('Data/LT22.feather')
                    st.success("Daten wurden erfolgreich aktualisiert")

def seiteLaden():
    selected2 = Einstellungen.menueLaden()
    if selected2 == "Mitarbeiter pflegen":
        Einstellungen.mitarbeiterPflegen()
    elif selected2 == "Daten Update":
        Einstellungen.datenUpdate()
    else:
        st.write("Hier kommt die Startseite rein")

