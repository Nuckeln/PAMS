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
from Seiten.P_Admin import Admin
from Seiten.P_Daten_Update import Daten_Update
from Seiten.P_Fehlverladungen import fehlverladungenPage
from Seiten.P_DDS import ddsPage
from Seiten.P_Infocenter import Infocenter
from Seiten.P_SAP_PicksMA import LoadPageSapPicksMA
from Seiten.P_Wartung import Wartung
import datetime

# Zum Ausführen
#MAC#   streamlit run "/Users/martinwolf/Python/Superdepot Reporting/Main.py"
 
# --- Set Global Page Configs ---
st.set_page_config(layout="wide", page_title="PAMS Report-Tool", page_icon=":bar_chart:",initial_sidebar_state="collapsed")
hide_streamlit_style = """
                <style>
                @import url('https://fonts.googleapis.com/css?family=Montserrat');
                html, body, [class*="css"]  {
                font-family: 'Montserrat';
                }
                
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
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

img = Image.open('Data/img/img_bat_logo_blau.png', mode='r')

# ----- Config Main Menue -----
def berechtigung():

    # Berechtigungen für die Seiten
    try :
        a = st.session_state.rechte
    except:
        a = st.session_state.rechte = 0
    # Berechtigungen für die Seiten
    if st.session_state.rechte == 1:
        #admin Vollzugriff
        return ["Live Status",'SAP WM Daten','SAP Bewegungsdaten','Fehlverladungen','DDS','Infocenter','Daten Updaten','Admin','Einstellungen','Wartung']
        #return ['Wartung']
    else:
        return ['Wartung']
    
    # elif st.session_state.rechte == 2:
    #     # Manager
    #     return ["Live Status",'SAP Mitarbeiter','SAP Bewegungsdaten','Fehlverladungen','DDS','Infocenter','Daten Updaten','Einstellungen']
    
    # elif st.session_state.rechte == 3:
    #     # Mitarbeiter AD 
    #     return ["Live Status",'SAP WM Daten','Einstellungen']
    
    # elif st.session_state.rechte == 4:
    #     # Mitarbeiter Fremd
    #     return ["Live Status",'SAP WM Daten','Einstellungen']
    #     # Lager
    
    # elif st.session_state.rechte == 5:
    #     return ["Live Status"]

# ----- Login -----

authentication_status = Login.Login(self=Login)

with st.sidebar: 
    a = ("""
        <style>
            .css-18e3th9 {
                    padding-top: 0rem;
                    padding-bottom: 10rem;
                    padding-left: 5rem;
                    padding-right: 5rem;
                }
            .css-1d391kg {
                    padding-top: 0rem;
                    padding-right: 1rem;
                    padding-bottom: 3.5rem;
                    padding-left: 1rem;
                }
        </style>
        """) 

    st.markdown(a, unsafe_allow_html=True)  
    try:
        st.image(img)
    except:
        st.text('Bild nicht gefunden')
    try:     
        sel_main_m = option_menu('PAMS', berechtigung(), 
            icons=[''], 
            menu_icon='kanban-fill',
            styles={'container':{'font':'arial'}},)
    except:
        sel_main_m = option_menu('PAMS', ['Home'], 
            icons=[''], 
            menu_icon="cast", )

if authentication_status == True:
    # erfolgreich eingelogt dann Code ausführen!
    # ----- gewählte Page Laden -----
    
    if sel_main_m == 'Home':
        st.write('Hallo ' '!')
        st.write(st.session_state['user'])
        st.write()
        st.text('Willkommen in der PAMS BETA Version')
        st.text('Zur Zeit aktualisiert sich das tool jede Stunde')
        st.text('Bei Fragen oder Problemen bitte an Martin Wolf wenden')
        st.text('Viel Spaß beim Auswerten.')
        a = st.session_state.user       
        Login.authenticator.logout('Logout')
        if st.session_state.user is None:
            st.success("Logout successful!")
            #timer 10 sec und dann neu laden


    if sel_main_m == 'Live Status':
        LIVE.PageTagesReport()
        #expand st.sidebar false

    if sel_main_m == 'Wartung':
        Wartung.page()
    if sel_main_m == 'Admin': 
        Admin.page()
    if sel_main_m == 'Fehlverladungen':
        fehlverladungenPage()
    if sel_main_m == 'DDS':
        ddsPage()
    if sel_main_m == 'SAP Bewegungsdaten':
        LoadPageSapPicksMA.mitarbeiterPage()
    if sel_main_m == 'SAP WM Daten':
        SAPWM.sap_wm_page()
    if sel_main_m == 'Infocenter':
        Infocenter.page()
    if sel_main_m == 'Daten Updaten':
        Daten_Update.page()

with st.sidebar:
    Login.authenticator.logout('Logout')
    #reload page
    


