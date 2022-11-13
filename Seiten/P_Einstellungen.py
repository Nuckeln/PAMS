import streamlit as st
import pandas as pd
import numpy as np
from streamlit_option_menu import option_menu
from streamlit import cache
import Data_Class.rerun 
from Data_Class.toFeather import *
from Data_Class.C_Daten_LT22 import *

class Einstellungen:
    pass
    def SeiteEinstellungen(self):
        if 'key' not in st.session_state:
            st.session_state['key'] = 'value'

    # Session State also supports attribute based syntax
        if 'key' not in st.session_state:
            st.session_state.key = +1

        def MenueLaden(self):
            selected2 = option_menu(None, ["Ich", "Mitarbeiter pflegen", "Daten Update"], 
            icons=['house', 'cloud-upload', "list-task"], 
            menu_icon="cast", default_index=0, orientation="horizontal")
            return selected2
        
        def MitarbeiterPflegen(self):
            dfMitarbeiter = pd.read_feather('Data/user.feather')
            # set id to index
            #dfMitarbeiter.set_index('ID', inplace=True)
            name = st.text_input("Name")
            oneId = st.text_input("One ID")
            funktion = st.text_input("Funktion")
            col1,col2,col3 = st.columns(3)
            with col1:
                speichern = st.button("Speichern")
                
            with col2:
                selMitarbeiter = st.selectbox("Mitarbeiter", dfMitarbeiter['Name'])
            with col3:
                st.write("")
                st.write("")
                löschen = st.button("gewählten Mitarbeiter Löschen")
            st.dataframe(dfMitarbeiter,use_container_width=True)
            if speichern:
                # convert oneId to int
                try:
                    oneId = int(oneId)
                    dfMitarbeiter = dfMitarbeiter.append({'Name': name, 'One ID': oneId, 'Funktion': funktion}, ignore_index=True)
                    dfMitarbeiter.reset_index(inplace=True)
                    dfMitarbeiter.to_feather('Data/user.feather')
                    dfMitarbeiter = pd.read_feather('Data/user.feather')                    
                    st.success("Mitarbeiter wurde gespeichert")
                    #rerun script
                    st.experimental_rerun()
                except:
                    st.error("One ID muss eine Zahl sein")
            if löschen:
                #drop row
                dfMitarbeiter = dfMitarbeiter[dfMitarbeiter['Name'] != selMitarbeiter]
                #reset index
                dfMitarbeiter = dfMitarbeiter.reset_index(drop=True)
                dfMitarbeiter.to_feather('Data/user.feather')
                dfMitarbeiter = pd.read_feather('Data/user.feather')  
                #rerun script
                st.experimental_rerun()

     
        #------------------Daten Update------------------
        def DatenUpdate(self):
            st.markdown("Welche Daten möchtest du Updaten?")

            ##TODO Bild von SAP Layout einstellungen und Prozess
            with st.expander('Bewegungsdaten LT22', expanded=False):
                 uploaded_file = st.file_uploader("Choose a file")
                 if uploaded_file is not None:
                        # To read file as dataframe:
                        df = pd.read_excel(uploaded_file)
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
            if st.button("Daten Berechen"):
                load = LT22Auswerten()
                load.go()

            

        selected2 = MenueLaden(self)
        if selected2 == 'Ich':
            st.text("Ich")
            d = st.button("Daten reperen")
            start = Data_Class.toFeather.Reperatur()
            if d:
                start.go()
                st.success("Daten wurden erfolgreich reperiert")
            df1 = pd.read_feather('Data/LT22.feather')
            st.dataframe(df1,use_container_width=True)
        if selected2 == 'Mitarbeiter pflegen':
            MitarbeiterPflegen(self)
        if selected2 == 'Daten Update':
            DatenUpdate(self)
