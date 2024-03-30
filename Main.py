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
def berechtigung():
    if st.session_state.rechte == 1:
        #admin Vollzugriff
        return ['Depot Live Status',"Logistics Live Monitor",'Depot Reports','Forecast','Lagerverwaltung','Admin']
    # else:
    #     return ['Wartung']
    elif st.session_state.rechte == 2: 
        # Manager
        return ["Depot Live Status",'Logistics Live Monitor','Depot Reports','Lagerverwaltung','Forecast']
    
    elif st.session_state.rechte == 3:
        # Mitarbeiter AD 
        return ["Depot Live Status",'Logistics Live Monitor','Depot Reports','Depot Forecast','Lagerverwaltung']
    
    elif st.session_state.rechte == 4:
        # Mitarbeiter Fremd
        return ["Live Status",'Forecast','Logistics Live Monitor']
        # Lager
    
    elif st.session_state.rechte == 5:
        return ["Live Status",'Forecast','Logistics Live Monitor']

# ----- Login -----
authentication_status = None
authentication_status = Login.Login(self=Login)
#logging.info(f'Authentifizierungsstatus: {authentication_status}')

if authentication_status == True:
    user = st.session_state.user
    #logging.info(f'User: {user}')
    with st.sidebar: 
        check = checkSystem()
        #st.write(f'**{check}**')
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
            with st.popover('Passwort ändern'):
                Login.newPasswort(Login)
        except:
            pass
if authentication_status == True:
    if sel_main_m == "Depot Live Status":
        LIVE.PageTagesReport()
        #logging.info('User läd Seite Live Status')
    if sel_main_m == 'Depot Reports':
         reportPage()   
    if sel_main_m == 'Warehouse Reports':
        pageUserReport()
        #logging.info('User läd Seite User Reports')
    if sel_main_m == 'Admin':
        adminPage() 
        #logging.info('User läd Seite Admin')
    if sel_main_m == 'Forecast':
        pageForecast()
        #logging.info('User läd Seite Forecast')
    if sel_main_m == 'Lagerverwaltung':
        pageStellplatzverwaltung()
    if sel_main_m == 'Logistics Live Monitor':
        pageLadeplan()        
    