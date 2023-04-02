# Python Module
import streamlit as st # Streamlit Web App Framework
from streamlit_option_menu import option_menu # pip install streamlit-option-menu # CSS Style für Main Menu # https://icons.getbootstrap.com
from PIL import Image # Bilder

#Eigene Klassen
from Seiten.P_UserLogin import Login
from Seiten.P_Live import LIVE
from Seiten.P_Nachschub import SAPWM
#from Seiten.P_Forecast import *
from Seiten.P_Admin import Admin
from Seiten.P_Daten_Update import Daten_Update
from Seiten.P_Fehlverladungen import fehlverladungenPage
from Seiten.P_DDS_neu import ddsPage
from Seiten.P_Infocenter import Infocenter
from Seiten.P_SAP_PicksMA import LoadPageSapPicksMA
from Seiten.P_Wartung import Wartung

# Zum Ausführen
#MAC#   streamlit run "/Users/martinwolf/Python/Superdepot Reporting/Main.py"
 
# --- Set Global Page Configs ---
st.set_page_config(layout="wide", page_title="PAMS Report-Tool", page_icon=":bar_chart:",initial_sidebar_state="expanded")

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
                """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)
st.write('<style>div.block-container{padding-top:0rem;}</style>', unsafe_allow_html=True)

img = Image.open('Data/img/logo.png', mode='r')

##
# ----- Config Main Menue -----
def berechtigung():
    if st.session_state.rechte == 1:
        #admin Vollzugriff
        return ["Live Status",'Datenanalyse','SAP Bewegungsdaten','Nachschub','Fehlverladungen','Daten Updaten','Admin','Infocenter','Wartung','Einstellungen']
    # else:
    #     return ['Wartung']
    elif st.session_state.rechte == 2:
        # Manager
        return ["Live Status",'Datenanalyse','SAP Bewegungsdaten','Nachschub']
    
    elif st.session_state.rechte == 3:
        # Mitarbeiter AD 
        return ["Live Status",'Datenanalyse','Nachschub',]
    
    elif st.session_state.rechte == 4:
        # Mitarbeiter Fremd
        return ["Live Status"]
        # Lager
    
    elif st.session_state.rechte == 5:
        return ["Live Status"]

# ----- Login -----

authentication_status = Login.Login(self=Login)
if authentication_status == True:
    with st.sidebar: 
        try:
            st.image(img)
        except:
            st.text('')
        try:     
            sel_main_m = option_menu('PAMS', berechtigung(), 
                icons=[''], 
                menu_icon='kanban-fill',
                styles={'container':{'font':'Montserrat'}},)
            Login.authenticator.logout('Logout')
        except:
            pass
if authentication_status == True:
    if sel_main_m == 'Live Status':
        LIVE.PageTagesReport()
    if sel_main_m == 'Wartung':
        Wartung.page()
    if sel_main_m == 'Admin': 
        Admin.page()
    if sel_main_m == 'Fehlverladungen':
        fehlverladungenPage()
    if sel_main_m == 'Datenanalyse':
        ddsPage()
    if sel_main_m == 'SAP Bewegungsdaten':
        LoadPageSapPicksMA.mitarbeiterPage()
    if sel_main_m == 'Nachschub':
        SAPWM.sap_wm_page()
    if sel_main_m == 'Infocenter':
        Infocenter.page()
    if sel_main_m == 'Daten Updaten':
        Daten_Update.page()



