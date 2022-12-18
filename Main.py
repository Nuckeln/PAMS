# Python Module
import streamlit as st # Streamlit Web App Framework
from streamlit_option_menu import option_menu # pip install streamlit-option-menu # CSS Style für Main Menu # https://icons.getbootstrap.com
import pandas as pd # Dataframes
from PIL import Image # Bilder

#Eigene Klassen
from Seiten.P_UserLogin import Login
from Seiten.P_Live import LIVE
from Seiten.P_SAP_WM import SAPWM
#from Seiten.P_Forecast import *
from Seiten.P_Einstellungen import Einstellungen
from Seiten.P_Fehlverladungen import fehlverladungenPage
from Seiten.P_DDS import ddsPage
from Seiten.P_Infocenter import Infocenter
from Seiten.P_SAP_PicksMA import LoadPageSapPicksMA



# Zum Ausführen
#MAC#    streamlit run "/Users/martinwolf/Python/Superdepot Reporting/Main.py"
#WIN#    streamlit run "

# --- Set Global Page Configs ---
st.set_page_config(layout="wide", page_title="PAMS Report-Tool", page_icon=":bar_chart:",initial_sidebar_state="expanded")
# Session State also supports the attribute based syntax
hide_streamlit_style = """
                <style>
                div[data-testid="stToolbar"] {
                visibility: hidden;
                height: 0%;
                position: fixed;
                }
                div[data-testid="stDecoration"] {
                visibility: hidden;
                height: 0%;
                position: fixed;
                }
                div[data-testid="stStatusWidget"] {
                visibility: hidden;
                height: 0%;
                position: fixed;
                }
                #MainMenu {
                visibility: hidden;
                height: 0%;
                }
                header {
                visibility: hidden;
                height: 0%;
                }
                footer {
                visibility: hidden;
                height: 0%;
                }
                </style>
                """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)
st.markdown("""
        <style>
               .css-18e3th9 {
                    padding-top: 0rem;
                    padding-bottom: 10rem;
                    padding-left: 5rem;
                    padding-right: 5rem;
                }
               .css-1d391kg {
                    padding-top: 3.5rem;
                    padding-right: 1rem;
                    padding-bottom: 3.5rem;
                    padding-left: 1rem;
                }
        </style>
        """, unsafe_allow_html=True)



#img = Image.open('Data/img/logo.png', mode='r')
# ----- Config Main Menue -----
# BAT LOGO  

def berechtigung():
    # Berechtigungen für die Seiten
    try :
        st.session_state.rechte
    except:
        st.session_state.rechte = 0
    # Berechtigungen für die Seiten
    if st.session_state.rechte == 1:
        #admin Vollzugriff
        return ['Home',"Live Status",'SAP WM Daten','SAP Mitarbeiter','Einstellungen','Fehlverladungen','DDS','Infocenter']
    
    elif st.session_state.rechte == 2:
        # Manager
        return ['Home',"Live Status",'SAP Mitarbeiter','SAP WM Daten','Einstellungen','Fehlverladungen','DDS','Infocenter']
    
    elif st.session_state.rechte == 3:
        # Mitarbeiter AD 
        return ['Home',"Live Status",'SAP WM Daten','Einstellungen']
    
    elif st.session_state.rechte == 4:
        # Mitarbeiter Fremd
        return ['Home',"Live Status",'SAP WM Daten','Einstellungen']
        # Lager
    
    elif st.session_state.rechte == 5:
        return ['Home',"Live Status"]

# ----- Login -----

authentication_status = Login.Login(self=Login)

with st.sidebar:
    try:      
        sel_main_m = option_menu('Menu', berechtigung(), 
            icons=[''], 
            menu_icon="cast", )
    except:
        sel_main_m = option_menu('Menu', ['Home'], 
            icons=[''], 
            menu_icon="cast", )

if authentication_status == True:
    # erfolgreich eingelogt dann Code ausführen!
    # ----- gewählte Page Laden -----
    
    if sel_main_m == 'Home':
        st.write('Hallo ' '!')
        st.write(st.session_state['user'])
        st.write()
        st.text('Willkommen in PAMS Report-Tool BETA Version')
        st.text('Zur Zeit sind aktualisiert sich das tool jede Stunde')
        st.text('Bei Fragen oder Problemen bitte an Martin Wolf wenden')
        st.text('Viel Spaß beim Auswerten')
        a = st.session_state.user       
        b = st.session_state.rechte 
        st.write(b)
        Login.authenticator.logout('Logout')
        if st.session_state.user is None:
            st.success("Logout successful!")
            #timer 10 sec und dann neu laden


    if sel_main_m == 'Live Status':
        LIVE.PageTagesReport()
    if sel_main_m == 'Einstellungen': 
        Einstellungen.page()
    if sel_main_m == 'Fehlverladungen':
        fehlverladungenPage()
    if sel_main_m == 'DDS':
        ddsPage()
    if sel_main_m == 'SAP Mitarbeiter':
        LoadPageSapPicksMA.mitarbeiterPage()

    if sel_main_m == 'SAP WM Daten':
        SAPWM.sap_wm_page()
    if sel_main_m == 'Infocenter':
        Infocenter.page()


        



