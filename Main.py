# Python Module
import streamlit as st # Streamlit Web App Framework
from streamlit_option_menu import option_menu # pip install streamlit-option-menu # CSS Style für Main Menu # https://icons.getbootstrap.com
from PIL import Image # Bilder

#Eigene Klassen
from Seiten.P_UserLogin import Login
from Seiten.P_Live import LIVE
from Seiten.P_Report import reportPage
from Seiten.P_Admin import adminPage
from Seiten.P_User_Reports import pageUserReport

# Zum Ausführenv
#MAC#   streamlit run "/Users/martinwolf/Python/PAMS 2.0/main.py"
 
# --- Set Global Page Configs ---
st.set_page_config(layout="wide", page_title="PAMS Report-Tool", page_icon=":bar_chart:",initial_sidebar_state="expanded")
if 'key' not in st.session_state:
    st.session_state['key'] = 'value'


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
        return ["Live Status",'Reports','User Reports','Admin']
    # else:
    #     return ['Wartung']
    elif st.session_state.rechte == 2: 
        # Manager
        return ["Live Status",'Reports','User Reports','Admin']
    
    elif st.session_state.rechte == 3:
        # Mitarbeiter AD 
        return ["Live Status",'Reports',]
    
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
            Login.newPasswort(Login)
        except:
            pass
if authentication_status == True:
    if sel_main_m == 'Live Status':
        LIVE.PageTagesReport()
    if sel_main_m == 'Reports':
         reportPage()   
    if sel_main_m == 'User Reports':
        pageUserReport()
    if sel_main_m == 'Admin':
        adminPage() 
