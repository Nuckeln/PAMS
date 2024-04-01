#Python Module
import streamlit as st
import os
import streamlit_option_menu #import option_menu 
from PIL import Image 
import streamlit_authenticator as stauth
from st_on_hover_tabs import on_hover_tabs

from Seiten.P_UserLogin import Login
from Seiten.P_Live import LIVE
from Seiten.P_Report import reportPage
from Seiten.P_Admin import adminPage
from Seiten.P_User_Reports import pageUserReport
from Seiten.P_Forecast import main as pageForecast
from Seiten.P_Nachschub import pageStellplatzverwaltung
from Seiten.P_Ladeplan import main as pageLadeplan
from Data_Class.SQL import read_table, updateTable


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

def berechtigung(rechte):
            
    #admin Vollzugriff
    if rechte == 1:
        pages = ['Depot Live Status',"LC Monitor",'Depot Reports','Forecast','Lagerverwaltung','Admin']
        icons = ['autorenew', 'monitoring','analytics', 'science','warehouse','admin_panel_settings']
        return pages, icons
    # Manager
    elif rechte == 2: 
        pages = ['Depot Live Status',"LC Monitor",'Depot Reports','Forecast','Lagerverwaltung']
        icons = ['autorenew', 'monitoring','analytics', 'science','warehouse']
        return pages, icons
    
    # Mitarbeiter AD 
    elif rechte == 3:
        pages = ['Depot Live Status','Depot Reports','Forecast','Lagerverwaltung']
        icons = ['autorenew','analytics', 'science','warehouse']
        return pages, icons
    
    # Mitarbeiter Fremd
    elif rechte == 4:
        pages = ['Depot Live Status','Depot Reports','Forecast']
        icons = ['autorenew','analytics', 'science']
        return pages, icons
    
    # Lager
    elif rechte == 5:
        pages = ['Depot Live Status']
        icons = ['autorenew']
        return pages, icons


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
img = Image.open('Data/img/logo_white.png', mode='r')

if st.session_state.get('Counter') is None:
    st.session_state['Counter'] = 0

# ----- Config Main Menue -----
#authentication_status,user,rechte = Login()
authentication_status = Login.Login(self=Login)

rechte = st.session_state.rechte
if authentication_status == True:
        

    def user_menue(pages,icons):

        st.markdown('<style>' + open('./style.css').read() + '</style>', unsafe_allow_html=True)

        with st.sidebar:

            try:
                st.image(img, caption='Logo')
            except:
                st.text('')
            
            
            st.markdown('<div id="sidebar-header"</div>', unsafe_allow_html=True)  # Logo Bereich
            # Load Menue
            sel_main_m = on_hover_tabs(tabName=pages,
                                iconName=icons, default_choice=0,
                                styles = {'navtab': {'background-color':'#0e2b63', #Hintergrundfarbe der Tabs
                                                    'color': '#ffffff', #Farbe der Schrift und Icons
                                                    'font-size': '18px',
                                                    'transition': '.3s',
                                                    'white-space': 'nowrap',
                                                    'text-transform': 'uppercase'},
                                        'tabOptionsStyle': {':hover :hover': {'color': '#ef7d00',
                                                                        'cursor': 'pointer'}},
                                        'iconStyle':{'position':'fixed',
                                                        'left':'7.5px',
                                                        'text-align': 'left'},
                                        'tabStyle' : {'list-style-type': 'none',
                                                        'margin-bottom': '30px',
                                                        'padding-left': '30px'}},
                                key="1")         

        #     st.markdown("""
        #     <style>
        #         /* Button standardmäßig verstecken */
        #         #logout-button {
        #             display: none;
        #         }

        #         /* Button anzeigen, wenn Sidebar ausgeklappt ist */
        #         section[data-testid='stSidebar']:hover #logout-button {
        #             display: block;
        #         }
        #     </style>
        #     <button id="logout-button" onclick="alert('Logout');">Logout</button>
        # """, unsafe_allow_html=True)
            
            

            # with st.popover('Passwort ändern'):
            #     LOGIN.newPasswort(Login)

            
        if sel_main_m == "Depot Live Status":
            LIVE.PageTagesReport()
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
        if sel_main_m == 'LC Monitor':
            pageLadeplan()        
    pages,icons = berechtigung(rechte)
    user_menue(pages,icons)

    Login.authenticator.logout('Logout')
    with st.popover('Passwort ändern'):
        st.write(rechte)
        st.write(pages)
        st.write(st.session_state.rechte)
        Login.newPasswort(Login)   

if st.session_state.get('Counter') is not None:
    st.session_state['Counter'] += 1
#st.write(st.session_state['Counter'])
#wenn kleiner als 2 dann st.rerun()
if st.session_state['Counter'] < 2:
    st.rerun()