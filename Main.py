#Python Module
import streamlit as st
import os
from streamlit_option_menu import option_menu 
from PIL import Image 

#Eigene Klassen
from Seiten.P_UserLogin import Login
from Seiten.P_Live import LIVE
from Seiten.P_Report import reportPage
from Seiten.P_Admin import adminPage
from Seiten.P_User_Reports import pageUserReport
from Seiten.P_Forecast import main as pageForecast
from Seiten.P_Nachschub import pageStellplatzverwaltung
from Seiten.P_Ladeplan import main as pageLadeplan
import mimetypes
mimetypes.add_type('application/javascript', '.js')
mimetypes.add_type('text/css', '.css')
# Logging Konfiguration
if 'authentication_status' not in st.session_state:
    st.session_state['authentication_status'] = False  # oder ein anderer Standardwert


def checkSystem():
    try:
        a = os.environ['SQLAZURECONNSTR_DbConnection']
        #if you found "pp" in the string, then it's a production environment
        a = a.find("pp")
        if a == -1:
            return 'System: Test'
        else:
            return 'System: Produktiv'
    except:
        return 'System: Test'

#MAC#   streamlit run "/Library/Python_local/Superdepot Reporting/Main.py"
 
# --- Set Global Page Configs ---
st.set_page_config(layout="wide", page_title="PAMS Report-Tool", page_icon=":bar_chart:",initial_sidebar_state="expanded")
hide_full_screen = '''
<style>
.element-container:nth-child(3) .overlayBtn {visibility: hidden;}
.element-container:nth-child(12) .overlayBtn {visibility: hidden;}
</style>
'''

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
                 div.block-container{padding-top:0rem;}
                </style>
                """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)
st.markdown(hide_full_screen, unsafe_allow_html=True)
# ----- Config Main Menue -----
img = Image.open('Data/img/logo.png', mode='r')

# ----- Config Main Menue -----

with st.sidebar: 
        st.image(img)

        st.text('')

        sel_main_m = option_menu('PAMS', ['Depot Live Status',"LC Monitor",'Depot Reports','Forecast','Lagerverwaltung','Admin'], 
            icons=[''], 
            menu_icon='kanban-fill',
            styles={'container':{'font':'Montserrat'}},)
# ----- Login -----
authentication_status = None
authentication_status = Login.Login(self=Login)
#logging.info(f'Authentifizierungsstatus: {authentication_status}')
def berechtigung():
    if st.session_state.rechte == 1:
        #admin Vollzugriff
        return ['Depot Live Status',"LC Monitor",'Depot Reports','Forecast','Lagerverwaltung','Admin']
    elif st.session_state.rechte == 2: 
        # Manager
        return ['Depot Live Status',"LC Monitor",'Depot Reports','Forecast','Lagerverwaltung']
    elif st.session_state.rechte == 3:
        # Mitarbeiter AD 
        return ['Depot Live Status','Depot Reports','Forecast','Lagerverwaltung']
    elif st.session_state.rechte == 4:
        # Mitarbeiter Fremd
        return ["Depot Live Status"]
        # Lager
    elif st.session_state.rechte == 5:
        return ["Depot Live Status"]

if authentication_status == True:
    user = st.session_state.user
    #logging.info(f'User: {user}')

with st.sidebar:
        Login.authenticator.logout('Logout')
        
        with st.popover('Passwort ändern'):
            try:
                Login.newPasswort(Login)
            except:
                st.stop()
check = berechtigung()
if check == []:
    st.rerun()
if sel_main_m == "Depot Live Status":
    # Prüfe Berechtigung ist Depot Live Status in der Liste
    if 'Depot Live Status' in check:
        LIVE.PageTagesReport()
    else:
        st.error('Keine Berechtigung für diese Seite')
if sel_main_m == 'Depot Reports':
    if 'Depot Reports' in check:
        reportPage()   
    else:
        st.error('Keine Berechtigung für diese Seite')        
if sel_main_m == 'Forecast':
    if 'Forecast' in check:
        pageForecast()
    else:
        st.error('Keine Berechtigung für diese Seite')        
if sel_main_m == 'Lagerverwaltung':
    if 'Lagerverwaltung' in check:
        pageStellplatzverwaltung()
    else:
        st.error('Keine Berechtigung für diese Seite')        
if sel_main_m == 'Admin':
    if 'Admin' in check:
        adminPage()
    else:
        st.error('Keine Berechtigung für diese Seite')        
if sel_main_m == 'LC Monitor':
    if 'LC Monitor' in check:
        pageLadeplan()
    else:
        st.error('Keine Berechtigung für diese Seite')        
