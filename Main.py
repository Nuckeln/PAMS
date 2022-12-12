# Python Module
import streamlit as st # Streamlit Web App Framework
from streamlit_option_menu import option_menu # pip install streamlit-option-menu # CSS Style für Main Menu # https://icons.getbootstrap.com
import pandas as pd # Dataframes
from PIL import Image # Bilder

#Eigene Klassen
from Seiten.P_UserLogin import Login
from Seiten.P_Live import LIVE
from Seiten.P_SAP_WM import SAPWM
from Seiten.P_Mitarbeiterauswertung import *
from Seiten.P_Bewegungsdaten import *
from Seiten.P_Auftragsübersicht import *
#from Seiten.P_Forecast import *
from Seiten.P_Einstellungen import *
from Seiten.P_Fehlverladungen import fehlverladungenPage
from Seiten.P_DDS import ddsPage
from Seiten.P_Infocenter import Infocenter
#from Data_Class.SQL import sql_datenLadenLabel,sql_datenLadenOderItems,sql_datenLadenStammdaten,sql_datenLadenOder


# Zum Ausführen
#MAC#    streamlit run "/Users/martinwolf/Python/Superdepot Reporting/Main.py"
#WIN#    streamlit run "

# --- Set Global Page Configs ---
st.set_page_config(layout="wide", page_title="PAMS Report-Tool", page_icon=":bar_chart:",initial_sidebar_state="expanded")

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
#st.sidebar.image(img, width=300)
with st.sidebar:
    #st.write('Hallo ' + Login.user + '!')'DDS','Fehlverladungen','SAP WM Daten','Forecast','Infocenter'
    sel_main_m = option_menu('"Menu', ["Live Status",'SAP WM Daten'], 
        icons=[''], 
        menu_icon="cast", )


# ----- Login -----
Login = Login()
authentication_status = Login.Login()
if authentication_status == True:
    # erfolgreich eingelogt dann Code ausführen!
    # ----- gewählte Page Laden -----
    if sel_main_m == 'Live Status':
        LIVE.PageTagesReport()
    if sel_main_m == 'Einstellungen': 
        seiteLaden()
    if sel_main_m == 'Fehlverladungen':
        fehlverladungenPage()
    if sel_main_m == 'DDS':
        ddsPage()
    if sel_main_m == 'SAP WM Daten':
        SAPWM.sap_wm_page()
    if sel_main_m == 'Infocenter':
        Infocenter.page()


        



