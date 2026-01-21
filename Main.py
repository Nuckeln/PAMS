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
from Seiten.P_HickUp import main as pageHickUp
from Data_Class.MMSQL_connection import read_Table, save_Table_append
from Seiten.forecast_prophet import main as pageForecastProp
import Seiten.WarehouseConditions_details as WarehouseConditions_details
import Seiten.WarehouseConditions as warehouseConditions

pd.set_option("display.precision", 3)

st.set_page_config(layout="wide", page_title="PAMS Report-Tool", page_icon=":bar_chart:")

# --- MINIMALES CSS FÜR STICKY MENU ---
# Nur das Nötigste: Header ausblenden und Menü oben festkleben

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
            /* 1. Alles von Streamlit ausblenden, was Platz wegnimmt */
            header[data-testid="stHeader"],
            div[data-testid="stToolbar"],
            div[data-testid="stDecoration"] {
                display: none !important;
                visibility: hidden !important;
            }
            
            /* 2. Der Haupt-Container: Startet GANZ OBEN */
            .block-container {
                padding-top: 1rem !important; /* Etwas Abstand für den Inhalt nach oben */
                padding-left: 2rem !important;
                padding-right: 2rem !important;
                padding-bottom: 0rem !important;
                max-width: 100% !important;
            }

            /* 3. Der Blaue Hintergrund (ABSOLUTE POSITION) */
            /* WICHTIG: absolute statt fixed, damit er mitscrollt! */
            div[data-testid="stAppViewContainer"]::before {
                content: "";
                position: fixed; 
                top: 0;
                left: 0;
                width: 100%;
                height: 8rem; /* Höhe des Headers */
                background-color: #0e2b63; 
                z-index: 0; /* Ganz hinten */
            }
            
            /* 4. Inhalt (Logo/Menü) muss über dem Hintergrund liegen */
            div[data-testid="stVerticalBlock"] > div:nth-child(3){
                position: relative;
                z-index: 1; 
            }

            /* --- PILLS (BUTTONS) STYLING --- */
            
            /* Container Hintergrund transparent */
            div[data-testid="stPills"] {
                background-color: transparent !important;
            }

            /* TEXT: Immer Weiß erzwingen (für inaktive Buttons) */
            div[data-testid="stPills"] p {
                color: white !important;
                font-family: 'Montserrat', sans-serif;
                font-weight: 500;
            }
            div[data-testid="stPills"] span {
                color: white !important;
            }

            /* INAKTIVE Buttons: Transparent */
            div[data-testid="stPills"] div[role="option"][aria-selected="false"] {
                background-color: transparent !important;
                border: 1px solid transparent !important;
            }

            /* HOVER: Leicht weiß */
            div[data-testid="stPills"] div[role="option"]:hover {
                background-color: rgba(255,255,255,0.1) !important;
            }

            /* AKTIVER Button: WEISS mit BLAUER Schrift */
            /* Das löst das Problem, dass man nicht sieht, was gewählt ist */
            div[data-testid="stPills"] div[role="option"][aria-selected="true"] {
                background-color: #ffffff !important;
                border: none !important;
            }
            
            /* WICHTIG: Schriftfarbe im aktiven Button auf Blau ändern */
            div[data-testid="stPills"] div[role="option"][aria-selected="true"] p {
                color: #0e2b63 !important;
                font-weight: bold !important;
            }

        </style>
    """, unsafe_allow_html=True)

    # 3. Menü Aufbau
    with st.container():
        # Layout: Logo links, Navigation rechts
        # Wir nutzen columns, um sie nebeneinander zu packen
        col_logo, col_nav = st.columns([1.2, 8.8], vertical_alignment="center")
        
        with col_logo:
            # Logo
            st.image('Data/img/logo_white.svg', use_container_width=True) 
            
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

    # 4. Abstandshalter NACH dem Header
    # Damit der Inhalt der Seite nicht direkt am Header klebt
    st.markdown("<div style='margin-bottom: 2rem;'></div>", unsafe_allow_html=True)

    page = st.session_state.current_page

    # Seitenlogik
    if page == 'Depot Live Status':
        PageTagesReport()
    elif page == 'Depot Reports':
        reportPage()
    elif page == 'Forecast':
        pageForecastProp()
    elif page == 'Lagerverwaltung':
        pageStellplatzverwaltung()
    elif page == 'C&E check':
        pageC_E_check()
    elif page == 'Hick-Up':
        pageHickUp()
    elif page == 'Admin':
        adminPage()
    elif page == 'Warehouse Conditions':
        warehouseConditions.app()
    elif page == 'Warehouse Conditions Details':
        WarehouseConditions_details.app()



@st.cache_data()
def read_user():
    return read_Table("user")
             
def main():
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