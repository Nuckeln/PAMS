import streamlit as st
import pandas as pd
from streamlit_option_menu import option_menu
from streamlit import cache
import Data_Class.rerun 
class Einstellungen:
    pass
    def SeiteEinstellungen(self):
        if 'key' not in st.session_state:
            st.session_state['key'] = 'value'

    # Session State also supports attribute based syntax
        if 'key' not in st.session_state:
            st.session_state.key = 'value'

        def MenueLaden(self):
            selected2 = option_menu(None, ["Ich", "Mitarbeiter pflegen", "Daten Update"], 
            icons=['house', 'cloud-upload', "list-task"], 
            menu_icon="cast", default_index=0, orientation="horizontal")
            return selected2
        
        def MitarbeiterPflegen(self):
            dfMitarbeiter = pd.read_feather('Data/user.feather')
            # set id to index
            dfMitarbeiter.set_index('ID', inplace=True)
            def Textboxen(self):
                name = st.text_input("Name")
                oneId = st.text_input("One ID")
                funktion = st.text_input("Funktion")
            Textboxen(self)
            
            col1,col2,col3 = st.columns(3)
            with col1:
                speichern = st.button("Speichern")
                eingabeloeschen = st.button("Eingabe löschen")
            with col2:
                selMitarbeiter = st.selectbox("Mitarbeiter", dfMitarbeiter['Name'])
            with col3:
                löschen = st.button("gewählten Mitarbeiter Löschen")
            st.dataframe(dfMitarbeiter,use_container_width=True)
            if speichern:
                # convert oneId to int
                try:
                    oneId = int(oneId)
                    dfMitarbeiter = dfMitarbeiter.append({'Name': name, 'One ID': oneId, 'Funktion': funktion}, ignore_index=True)
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
            if eingabeloeschen: # beende methode
                st.experimental_rerun(MenueLaden)
        #------------------Daten Update------------------
        def DatenUpdate(self):
            st.markdown("Hier kommt der Daten Update Screen")
                    
        selected2 = MenueLaden(self)
        if selected2 == 'Ich':
            st.text("Ich")
        if selected2 == 'Mitarbeiter pflegen':
            MitarbeiterPflegen(self)
        if selected2 == 'Daten Update':
            DatenUpdate(self)
