
import hydralit_components as hc


from PIL import Image 
import streamlit as st
#Eigene Klassen

from Data_Class.Authenticator import login
from Seiten.LOGIN import Login
from Seiten.P_Live import LIVE
from Seiten.P_Report import reportPage
from Seiten.P_Admin import adminPage
from Seiten.P_Forecast import main as pageForecast
from Seiten.P_Nachschub import pageStellplatzverwaltung
from Seiten.P_Ladeplan import main as pageLadeplan

#MAC#   streamlit run "/Library/Python_local/Superdepot Reporting/Main.py"
st.set_page_config(layout="wide", page_title="PAMS Report-Tool", page_icon=":bar_chart:",initial_sidebar_state="expanded")
# prüfe ob st.session_state.rechte vorhanden ist


if 'rechte' not in st.session_state:
    st.session_state['rechte'] = None  # oder ein anderer Standardwert


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



img = Image.open('Data/img/logo.png', mode='r')


menu_data = [
    {'id':'Depot Reports','icon':"🟰",'label':"Depot Reports"},
    {'id':'Forecast','icon':"🟰",'label':"Forecast"},
    {'id':'Lagerverwaltung','icon':"🟰",'label':"Lagerverwaltung"},
    {'id':'Admin','icon':"🟰",'label':"Admin"}
    ] 

over_theme = {'txc_inactive': '#ef7d00','txc_active': '#004f9f',}
col1, col2 = st.columns([1, 7])
with col1:
    st.image(img)
with col2:
    menu_id = hc.nav_bar(
    menu_definition=menu_data,
    override_theme=over_theme,
    home_name='Live Status Depot',
    hide_streamlit_markers=True, #will show the st hamburger as well as the navbar now!
    sticky_nav=False, #at the top or not
    sticky_mode='pinned', #jumpy or not-jumpy, but sticky or pinned
)

authentication_status = Login.Login(self=Login)

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

    st.write(berechtigung())
optionen = ['Depot Live Status',"LC Monitor",'Depot Reports','Forecast','Lagerverwaltung','Admin']
if menu_id == 'Live Status Depot':
    Prüfe ob es in rec
