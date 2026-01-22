import streamlit as st
import streamlit_authenticator as stauth
import pandas as pd
import hydralit_components as hc

# --- DEINE IMPORTS ---
# Stellen Sie sicher, dass diese Dateien existieren und fehlerfrei sind
from Seiten.P_Live import PageTagesReport
from Seiten.P_Report import reportPage
from Seiten.P_Admin import adminPage
from Seiten.P_Nachschub import pageStellplatzverwaltung
from Seiten.C_E_check import main as pageC_E_check
from Data_Class.MMSQL_connection import read_Table
from Seiten.forecast_prophet import main as pageForecastProp
import Seiten.WarehouseConditions_details as WarehouseConditions_details
import Seiten.WarehouseConditions as warehouseConditions
import base64
import os # Hilfreich, um zu prüfen, ob die Datei existiert

# --- 1. PAGE CONFIG (Muss immer ganz oben stehen) ---
st.set_page_config(layout="wide", page_title="PAMS Report-Tool", page_icon=":bar_chart:")
def get_base64_of_bin_file(bin_file):
    """
    Liest eine Datei und gibt den Base64-String zurück.
    """
    try:
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except FileNotFoundError:
        return None
pd.set_option("display.precision", 3)

# --- 2. HELPER FUNKTIONEN ---

def page_loader_wrapper(func, title):
    """
    Wrapper für Ladeanimationen.
    ACHTUNG: hc.HyLoader ist hier vorerst deaktiviert, um den 'White Page' Fehler zu beheben.
    """
    def wrapper():
        # Falls du den Loader wieder aktivieren willst, entferne die Kommentare unten.
        # Aber teste erst ohne!
        
        # with hc.HyLoader(f'Lade {title}', hc.Loaders.pacman, primary_color='Blue'):
        #     func()
        
        # Stattdessen rufen wir die Funktion direkt auf:
        func()
        
    return wrapper

def logout_page():
    st.session_state.user = None
    st.session_state.rechte = None
    st.rerun()

# --- 3. SEITEN KONFIGURATION ---
PAGES_CONFIG = {
    'Depot Live Status': {'func': PageTagesReport},
    'Depot Reports': {'func': reportPage, 'color': 'green'},
    'Forecast': {'func': pageForecastProp,},
    'Lagerverwaltung': {'func': pageStellplatzverwaltung},
    'C&E check': {'func': pageC_E_check, },
    'Admin': {'func': adminPage},
    'Warehouse Conditions': {'func': warehouseConditions.app},
    'Warehouse Conditions Details': {'func': WarehouseConditions_details.app},
    '"What\'s Next"': {'func': lambda: st.write("Coming Soon")},
}


def apply_styling():
    # --- LOGO RECHTS VORBEREITEN ---
    # Pfad zu deinem rechten Logo
    logo_path = "Data/img/bat_logo White.svg"
    
    logo_css = ""
    img_b64 = get_base64_of_bin_file(logo_path)
    
    if img_b64:
        # Hier wird das Logo via CSS 'eingeschleust'
        logo_css = f"""
            header[data-testid="stHeader"]::after {{
                content: "";
                background-image: url("data:image/svg+xml;base64,{img_b64}");
                background-size: contain;
                background-repeat: no-repeat;
                background-position: right center;
                /* Größe und Position anpassen: */
                height: 35px; 
                width: 120px; 
                position: absolute;
                top: 0.5rem; 
                right: 0.5rem; /* Abstand von rechts */
                z-index: 999;
            }}
        """

    st.markdown(f"""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700&display=swap');
            
            html, body, [class*="css"]  {{
                font-family: 'Montserrat', sans-serif;
            }}

            /* --- 1. HEADER (TOP NAVIGATION) EINFÄRBEN --- */
            header[data-testid="stHeader"] {{
                background-color: #0e2b63 !important;
            }}

            /* --- 2. TEXT & ICONS WEISS MACHEN --- */
            header[data-testid="stHeader"] * {{
                color: white !important;
            }}
            
            /* --- 3. HAMBURGER MENU ANPASSEN --- */
            header[data-testid="stHeader"] button {{
                color: white !important;
            }}

            /* --- 4. LOGO RECHTS EINÜGEN --- */
            {logo_css}
            /* Padding oben anpassen, damit das Logo nicht abgeschnitten wird */
            header[data-testid="stHeader"] {{
                padding-top: 1.5rem;
                padding-bottom: 1.5rem;
            }}

            [data-testid="stSidebar"] {{
                background-color: #f0f2f6;
            }}
            
            /* Elemente ausblenden wie gewünscht */
            div[data-testid="stStatusWidget"] {{
                visibility: hidden;
                height: 0%;
                position: fixed;
            }}
            #MainMenu {{
                visibility: hidden;
                height: 0%;
            }}
        </style>
    """, unsafe_allow_html=True)


apply_styling()
def user_menue_rechte():
    if 'rechte' not in st.session_state:
        st.session_state.rechte = None
        
    rights = st.session_state.rechte
    
    # Hier deine Logik
    if rights == 1: 
        return ['Depot Live Status', 'Depot Reports', 'Forecast', 'Lagerverwaltung','C&E check','Hick-Up','Admin','Warehouse Conditions', 'Warehouse Conditions Details','"What\'s Next"']
    elif rights == 2:
        return ['Depot Live Status','Depot Reports', 'Forecast', 'Lagerverwaltung','C&E check','Hick-Up', 'Warehouse Conditions', 'Warehouse Conditions Details','"What\'s Next"']
    elif rights == 3:
        return ['Depot Live Status', 'Depot Reports', 'Forecast', 'Lagerverwaltung']
    elif rights == 4:
        return ["Depot Live Status"]
    elif rights == 5:
        return ["Depot Live Status"]
    elif rights == 6:
        return ["Depot Live Status", 'Depot Reports', 'Forecast', 'Lagerverwaltung']
    return []

# --- 4. DATENBANK & STYLE ---
@st.cache_data()
def read_user():
    return read_Table("user")


# --- 5. MAIN LOGIK ---
def main():

    
    # Session State initialisieren
    if 'user' not in st.session_state:
        st.session_state.user = None  

    # ----------------------------
    # A) LOGIN BEREICH (Nicht eingeloggt)
    # ----------------------------
    if not st.session_state.user:
        with st.spinner("Lade System..."):
            users_df = read_user()
            # Sicherheitscheck: Wenn DB leer oder Fehler
            if users_df is None or users_df.empty:
                st.error("Konnte User-Tabelle nicht laden.")
                st.stop()
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
            cookie_key='super_secret_key', # Sollte idealerweise in secrets.toml liegen
            cookie_expiry_days=30
        )
        
        # Login Widget anzeigen
        try:
            name, authentication_status, username = authenticator.login(
                location='main', 
                fields={'username':'Benutzername', 'password':'Passwort', 'submit_button':'Einloggen'}
            )
        except Exception as e:
            st.error(f"Fehler beim Login-Widget: {e}")
            return
        
        if authentication_status:
            st.session_state.user = name
            st.session_state.rechte = credentials['usernames'][username]['access_rights']
            st.rerun() # WICHTIG: Seite neu laden um Navigation zu starten
            
        elif authentication_status is False:
            st.error("Benutzername oder Passwort falsch.")
            
        # Registrierungshinweis (nur sichtbar wenn nicht eingeloggt)
        if not authentication_status:
            with st.popover("Registrieren (Admin only)"):
                st.write("Wende dich an den Admin.")


    else:
        # 1. Rechte prüfen
        if st.session_state.rechte == 0:
            st.error("Keine Berechtigung.")
            if st.button("Logout"):
                logout_page()
            st.stop()

        # 2. Logo setzen
        st.logo("/Users/martinwolf/Python/PAMS/Data/img/PAMS.svg") 

        # 3. Seiten zusammenstellen
        allowed_page_names = user_menue_rechte()
        st_pages = []
        
        if not allowed_page_names:
            st.error("Keine Seiten für deine Rechtegruppe gefunden.")
            if st.button("Logout"):
                logout_page()
            st.stop()

        for page_name in allowed_page_names:
            if page_name in PAGES_CONFIG:
                cfg = PAGES_CONFIG[page_name]
                
                wrapped_func = page_loader_wrapper(cfg['func'], page_name)
                
                # URL Pfad säubern (Fix für "wrapper" Fehler)
                safe_url_path = page_name.replace(" ", "_").replace("'", "").replace('"', "")
                
                st_pages.append(
                    st.Page(
                        wrapped_func, 
                        title=page_name, 
                        icon=cfg.get('icon'),
                        url_path=safe_url_path 
                    )
                )
        
        # Logout Seite hinzufügen
        st_pages.append(
            st.Page(logout_page, title="Logout", icon="🚪", url_path="logout")
        )

        try:
            pg = st.navigation(st_pages, position='top',expanded=True)
            pg.run()
        except Exception as e:
            st.error(f"Kritischer Fehler in der Navigation: {e}")

if __name__ == "__main__":
    main()