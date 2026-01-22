import streamlit as st
import streamlit_authenticator as stauth
import bcrypt
import pandas as pd
import hydralit_components as hc

# Deine Seiten-Imports
from Seiten.P_Live import PageTagesReport
from Seiten.P_Report import reportPage
from Seiten.P_Admin import adminPage
from Seiten.P_Nachschub import pageStellplatzverwaltung
from Seiten.C_E_check import main as pageC_E_check
from Data_Class.MMSQL_connection import read_Table, save_Table_append
from Seiten.forecast_prophet import main as pageForecastProp
import Seiten.WarehouseConditions_details as WarehouseConditions_details
import Seiten.WarehouseConditions as warehouseConditions

pd.set_option("display.precision", 3)

st.set_page_config(layout="wide", page_title="PAMS Report-Tool", page_icon=":bar_chart:")





def user_menue_rechte():
    if 'rechte' not in st.session_state:
        st.session_state.rechte = None
        
    if st.session_state.rechte == 1: 
        return ['Depot Live Status', 'Depot Reports', 'Forecast', 'Lagerverwaltung','C&E check','Hick-Up','Admin','Warehouse Conditions', 'Warehouse Conditions Details','"What\'s Next"']
    elif st.session_state.rechte == 2:
        return ['Depot Live Status','Depot Reports', 'Forecast', 'Lagerverwaltung','C&E check','Hick-Up', 'Warehouse Conditions', 'Warehouse Conditions Details','"What\'s Next"']
    elif st.session_state.rechte == 3:
        return ['Depot Live Status', 'Depot Reports', 'Forecast', 'Lagerverwaltung']
    elif st.session_state.rechte == 4:
        return ["Depot Live Status"]
    elif st.session_state.rechte == 5:
        return ["Depot Live Status"]
    elif st.session_state.rechte == 6:
        return ["Depot Live Status", 'Depot Reports', 'Forecast', 'Lagerverwaltung']
    return []



def user_menue_frontend():

    # 1. Verfügbare Seiten holen
    seiten = user_menue_rechte()
    

# 2. CSS: Perfektes Layout & Styling
    st.markdown("""
        <style>
            /* --- 0. FONTS LADEN --- */
            @import url('https://fonts.googleapis.com/css2?family=Montserrat:ital,wght@0,400;0,700;1,400;1,700&display=swap');
            @import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200');

            /* --- 1. GLOBALER FONT --- */
            /* WICHTIG: Wir setzen den Font auf 'html' und 'body'. */
            /* Alle anderen Elemente (div, span, p) erben das automatisch. */
            /* Wir zwingen es NICHT direkt auf 'span', damit Icons überleben. */
            
            html, body {
                font-family: 'Montserrat', sans-serif !important;
            }

            /* Nur Elemente, die oft eigene Fonts haben, zwingen wir sanft: */
            h1, h2, h3, h4, h5, h6, p, a, button, input, textarea, label {
                 font-family: 'Montserrat', sans-serif !important;
            }

            /* --- 2. ICON-SCHUTZ (Sicherheitsnetz) --- */
            /* Falls doch mal was schief geht, zwingen wir Icons zurück */
            .material-symbols-rounded, 
            .material-icons,
            .material-icons-outlined {
                font-family: 'Material Symbols Rounded' !important;
                font-weight: normal !important;
                font-style: normal !important;
                /* Sicherstellen, dass Ligaturen funktionieren */
                display: inline-block;
                white-space: nowrap;
                word-wrap: normal;
                direction: ltr;
                -webkit-font-feature-settings: 'liga'; 
                -webkit-font-smoothing: antialiased;
            }

            /* --- 3. LAYOUT BEREINIGUNG (Dein restlicher Code) --- */
            header[data-testid="stHeader"],
            div[data-testid="stToolbar"],
            div[data-testid="stDecoration"] {
                display: none !important;
                visibility: hidden !important;
            }
            /* --- 5. MENÜ INHALT (LOGO & PILLS) FIXIEREN --- */
            /* KORREKTUR: Wir nutzen jetzt einen strikten Pfad ("Child Combinator" >). */
            /* Wir starten beim Haupt-Container (.block-container) und gehen zum ERSTEN Vertical Block. */
            /* Dadurch werden alle anderen Container (LKWs weiter unten) ignoriert. */
            
            .block-container > div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlock"]:nth-of-type(1) > div[data-testid="stHorizontalBlock"] {
                position: fixed !important;
                top: 0 !important;
                left: 0 !important;
                width: 100% !important;
                height: 8rem !important;
                z-index: 999 !important; 
                padding-top: 1.5rem !important; 
                padding-left: 3rem !important; 
                padding-right: 3rem !important;
                pointer-events: none; 
            }
            
            /* Klickbarkeit wiederherstellen */
            .block-container > div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlock"]:nth-of-type(1) > div[data-testid="stHorizontalBlock"] * {
                pointer-events: auto !important;
            }
            .block-container {
                padding-top: 0rem !important;
                padding-left: 2rem !important;
                padding-right: 2rem !important;
                padding-bottom: 0rem !important;
                max-width: 100% !important;
            }

            div[data-testid="stAppViewContainer"]::before {
                content: "";
                position: fixed; 
                top: 0;
                left: 0;
                width: 100%;
                height: 8rem;
                background-color: #0e2b63; 
                z-index: 0;
            }
            
            div[data-testid="stVerticalBlock"] > div:nth-child(3){
                position: relative;
                z-index: 1; 
            }

            /* --- PILLS (BUTTONS) --- */
            div[data-testid="stPills"] {
                background-color: transparent !important;
            }

            div[data-testid="stPills"] p {
                color: white !important;
                /* Hier ist es okay, weil p Text ist */
                font-family: 'Montserrat', sans-serif !important; 
                font-weight: 500;
            }
            
            div[data-testid="stPills"] span {
                color: white !important;
                /* HIER KEIN FONT FAMILY SETZEN! */
            }

            div[data-testid="stPills"] div[role="option"][aria-selected="false"] {
                background-color: transparent !important;
                border: 1px solid transparent !important;
            }

            div[data-testid="stPills"] div[role="option"]:hover {
                background-color: rgba(255,255,255,0.1) !important;
            }

            div[data-testid="stPills"] div[role="option"][aria-selected="true"] {
                background-color: #ef7d00 !important;
                border: none !important;
            }
            
            div[data-testid="stPills"] div[role="option"][aria-selected="true"] p {
                color: #ef7d00 !important;
                font-weight: bold !important;
            }

        </style>
    """, unsafe_allow_html=True)



    # 3. Menü Aufbau
    with st.container():
        # Layout: Logo links, Navigation rechts
        col_logo, col_nav = st.columns([1.2, 8.8], vertical_alignment="center")
        
        with col_logo:
            st.image('Data/img/logo_white.svg', width='stretch') 
            
        with col_nav:
            if "current_page" not in st.session_state:
                st.session_state.current_page = "Depot Live Status"
                
            selection = st.pills(
                label="Navigation", 
                options=seiten, 
                selection_mode="single",
                default=st.session_state.current_page,
                label_visibility="collapsed"
            )
            
            if selection:
                st.session_state.current_page = selection

    st.markdown("<div style='margin-bottom: 2rem;'></div>", unsafe_allow_html=True)

    page = st.session_state.current_page

    # Seitenlogik
    if page == 'Depot Live Status':
        PageTagesReport()
    elif page == 'Depot Reports':
        with hc.HyLoader(f'Lade {page}',hc.Loaders.pacman, primary_color='Blue'):
            reportPage()
    elif page == 'Forecast':
        with hc.HyLoader(f'Lade {page}',hc.Loaders.pacman, primary_color='Blue'):
            pageForecastProp()
    elif page == 'Lagerverwaltung':
        with hc.HyLoader(f'Lade {page}',hc.Loaders.pacman, primary_color='Blue'):
            pageStellplatzverwaltung()
    elif page == 'C&E check':
        with hc.HyLoader(f'Lade {page}',hc.Loaders.pacman, primary_color='Blue'):
            pageC_E_check()
    elif page == 'Warehouse Conditions':
        with hc.HyLoader(f'Lade {page}',hc.Loaders.pacman, primary_color='Blue'):
            warehouseConditions.app()
    elif page == 'Warehouse Conditions Details':
        with hc.HyLoader(f'Lade {page}',hc.Loaders.pacman, primary_color='Blue'):
            WarehouseConditions_details.app()
    elif page == 'Admin':
        with hc.HyLoader(f'Lade {page}',hc.Loaders.pacman, primary_color='Blue'):
            adminPage()
    # elif page == '"What\'s Next"':
    #     with hc.HyLoader(f'Lade {page}',hc.Loaders.pretty_loaders,primary_color='blue '):
    #         PageWhatsNext()
    elif page == 'Logout':
        st.session_state.user = None
        st.session_state.rechte = None



@st.cache_data()
def read_user():
    return read_Table("user")
             
def main():
    with open("style.css") as css:
        st.markdown(f'<style>{css.read()}</style>', unsafe_allow_html=True)
    if 'user' not in st.session_state:
        st.session_state.user = None  

    with st.spinner("Lade Datenbanken..."):
        users_df = read_user()
        users_df.set_index('username', inplace=True)

    credentials = {'usernames': dict()}
    for idx, row in users_df.iterrows():
        credentials['usernames'][idx] = {
            'name': row['name'],
            'password': row['password'],
            'email': row.get('email', ''),  
            'access_rights': row['rechte']  
        }

    authenticator = stauth.Authenticate(
        credentials=credentials,
        cookie_name='pams_cookie',
        cookie_key='super_secret_key',
        cookie_expiry_days=30
    )
    
    st.session_state.user, authentication_status, username = authenticator.login(
        location='main', fields={'username':'Benutzername', 'password':'Passwort', 'submit_button':'Einloggen'}
    )

    if authentication_status:
        st.session_state.rechte = credentials['usernames'][username]['access_rights']
        if st.session_state.rechte == 0:
            st.error("Keine Berechtigung.")
            st.stop()
        
        # Aufruf des Menüs
        user_menue_frontend()
        
    elif authentication_status is False:
        st.error("Falsches Login.")
    
    # Registrierung nur anzeigen wenn nicht eingeloggt
    if not authentication_status and st.session_state.user is None:
        with st.popover("Registrieren"):
            with st.form("reg"):
                u = st.text_input("User")
                n = st.text_input("Name")
                p = st.text_input("Pass", type="password")
                if st.form_submit_button("Go"):
                    # ... (Registrierungslogik hier) ...
                    st.success("Registriert")

if __name__ == "__main__":
    main()