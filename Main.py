# Python Module
import streamlit as st # Streamlit Web App Framework
import os
from streamlit_option_menu import option_menu # pip install streamlit-option-menu # CSS Style für Main Menu # https://icons.getbootstrap.com
from PIL import Image # Bilder
import logging # Logging

#Eigene Klassen
from Seiten.P_UserLogin import Login
from Seiten.P_Live import LIVE
from Seiten.P_Report import reportPage
from Seiten.P_Admin import adminPage
from Seiten.P_User_Reports import pageUserReport
from Seiten.P_Forecast import main as pageForecast
from Seiten.P_Nachschub import pageStellplatzverwaltung
from Data_Class.SQL import read_table, updateTable



# Logging Konfiguration
logging.basicConfig(filename='pams_app.log', level=logging.INFO,
                    format='%(asctime)s:%(levelname)s:%(message)s')

# Log-Eintrag für den Start der App
logging.info('App gestartet')

def checkSystem():
    try:
        a = os.environ['SQLAZURECONNSTR_DbConnection']
        return 'Dev System'
    except:
        return 'IDE System'
# Zum Ausführenv
#MAC#   streamlit run "/Users/martinwolf/Python/PAMS 2.0/main.py"
 
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


# ----- Config Main Menue -----
img = Image.open('Data/img/logo.png', mode='r')

# ----- Config Main Menue -----
def berechtigung():
    if st.session_state.rechte == 1:
        #admin Vollzugriff
        return ["Live Status",'Reports','User Reports','Forecast','Admin', 'Lagerverwaltung']
    # else:
    #     return ['Wartung']
    elif st.session_state.rechte == 2: 
        # Manager
        return ["Live Status",'Reports','User Reports','Admin', 'Forecast','Lagerverwaltung']
    
    elif st.session_state.rechte == 3:
        # Mitarbeiter AD 
        return ["Live Status",'Reports','Forecast','Lagerverwaltung']
    
    elif st.session_state.rechte == 4:
        # Mitarbeiter Fremd
        return ["Live Status",'Forecast']
        # Lager
    
    elif st.session_state.rechte == 5:
        return ["Live Status",'Forecast']

# ----- Login -----
authentication_status = None
authentication_status = Login.Login(self=Login)
logging.info(f'Authentifizierungsstatus: {authentication_status}')

if authentication_status == True:
    user = st.session_state.user
    logging.info(f'User: {user}')
    with st.sidebar: 
        check = checkSystem()
        st.write(f'**{check}**')
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
            Login.newPasswort(Login)
        except:
            pass
if authentication_status == True:
    if sel_main_m == 'Live Status':
        LIVE.PageTagesReport()
        logging.info('User läd Seite Live Status')
    if sel_main_m == 'Reports':
         reportPage()   
    if sel_main_m == 'User Reports':
        pageUserReport()
        logging.info('User läd Seite User Reports')
    if sel_main_m == 'Admin':
        adminPage() 
        logging.info('User läd Seite Admin')
    if sel_main_m == 'Forecast':
        pageForecast()
        logging.info('User läd Seite Forecast')
    if sel_main_m == 'Lagerverwaltung':
        pageStellplatzverwaltung()