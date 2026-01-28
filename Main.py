import streamlit as st
import streamlit_authenticator as stauth
import pandas as pd
import bcrypt  # WICHTIG: Für die Registrierung
import base64
import os

# --- DEINE IMPORTS ---
from Seiten.P_Live import PageTagesReport
from Seiten.P_Report import reportPage
from Seiten.P_Admin import adminPage
from Seiten.C_E_check import main as pageC_E_check
from Seiten.forecast_prophet import main as pageForecastProp
import Seiten.lastMile as lastMile
import Seiten.WarehouseConditions_details as WarehouseConditions_details
import Seiten.WarehouseConditions as warehouseConditions
import Seiten.whatsNext as whatsNext
import Seiten.StockInventory as StockInventory

# WICHTIG: save_Table_append für die Registrierung hinzugefügt
from Data_Class.MMSQL_connection import read_Table, save_Table_append 

# --- 1. PAGE CONFIG ---
st.set_page_config(layout="wide", page_title="PAMS Report-Tool", page_icon=":bar_chart:")
pd.set_option("display.precision", 3)

def get_base64_of_bin_file(bin_file):
    try:
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except FileNotFoundError:
        return None

# --- 2. HELPER FUNKTIONEN ---

def page_loader_wrapper(func, title):
    def wrapper():
        func()
    return wrapper

def logout_page():
    st.title("Abmelden")
    st.write("Bitte bestätigen Sie die Abmeldung.")
    # Der Authenticator-Logout-Button kümmert sich um Cookie-Löschung und Session-Bereinigung.
    st.session_state.authenticator.logout('Abmelden', 'main')

def show_registration_form(users_df):
    """Zeigt das Registrierungs-Formular als Popover an."""
    with st.popover("Registrieren", help="Hier können Sie sich als neuer Benutzer registrieren."):
        with st.form(key="register_form"):
            new_user = st.text_input("Username")
            new_username = st.text_input("Klarname")
            new_password = st.text_input("Passwort", type="password")
            register_button = st.form_submit_button("Registrieren")
            
        if register_button:
            if new_user in users_df.index:
                st.error("Benutzer existiert bereits.")
                return
            if new_user == "":
                st.error('Bitte geben Sie einen User ein')
                return
            if new_username == "":
                st.error("Bitte geben Sie einen Namen ein.")
                return
            if new_password == "":
                st.error("Bitte geben Sie ein Passwort ein.")
                return
                
            # Passwort hashen und speichern
            try:
                from streamlit_authenticator.utilities.hasher import Hasher
                hashed_password = Hasher([new_password]).generate()[0]
            except Exception as e:
                st.error(f"Fehler beim Hashen des Passworts: {e}")
                return

            new_user_data = pd.DataFrame({
                "username": [new_user],
                "name": [new_username],
                "password": [hashed_password],
                "function": ["None"],
                "rechte": [0]
            })
            save_Table_append(new_user_data, "user")
            st.success("Benutzer erfolgreich registriert. Bitte kontaktieren Sie Christian Hammann oder Martin Wolf, um Berechtigungen zu erhalten.")
            read_user.clear()
            st.rerun()

# --- 3. SEITEN KONFIGURATION & STYLING ---
PAGES_CONFIG = {
    'Depot Live Status': {'func': PageTagesReport},
    'Depot Reports': {'func': reportPage, 'color': 'green'},
    'Forecast': {'func': pageForecastProp},
    'C&E check': {'func': pageC_E_check},
    'Admin': {'func': adminPage},
    'Warehouse Conditions': {'func': warehouseConditions.app},
    'Warehouse Conditions Details': {'func': WarehouseConditions_details.app},
    '"What\'s Next"': {'func': whatsNext.app},
    'Last Mile': {'func': lastMile.app},
    'Stock Inventory': {'func': StockInventory.app},
}

def apply_styling():
    logo_path = "Data/img/bat_logo White.svg"
    img_b64 = get_base64_of_bin_file(logo_path)
    logo_css = ""
    if img_b64:
        logo_css = f"""
            header[data-testid="stHeader"]::after {{
                content: ""; background-image: url("data:image/svg+xml;base64,{img_b64}");
                background-size: contain; background-repeat: no-repeat; background-position: right center;
                height: 35px; width: 120px; position: absolute; top: 0.8rem; right: 1rem; z-index: 999; pointer-events: none;
            }}
        """
    st.markdown(f"""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Montserrat:ital,wght@0,400;0,700;1,400;1,700&display=swap');
            @import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200');
            html, body, p, h1, h2, h3, h4, h5, h6, label, button, input, textarea {{ font-family: 'Montserrat', sans-serif !important; }}
            .material-symbols-rounded {{ font-family: 'Material Symbols Rounded' !important; }}
            header[data-testid="stHeader"] {{ background-color: #0e2b63 !important; padding-top: 1.5rem; padding-bottom: 1.5rem; height: 3.5rem; }}
            header[data-testid="stHeader"] * {{ color: white !important; }}
            header[data-testid="stHeader"] button {{ color: white !important; }}
            {logo_css}
            [data-testid="stMainBlockContainer"] {{ padding-top: 2.5rem !important; padding-left: 5rem !important; padding-right: 5rem !important; max-width: 100%; }}
            .stAppViewMain {{ margin-top: -2.5rem !important; }}
            [data-testid="stSidebar"] {{ background-color: #f0f2f6; }}
            div[data-testid="stStatusWidget"], #MainMenu {{ visibility: hidden; height: 0%; }}
        </style>
    """, unsafe_allow_html=True)

apply_styling()

def user_menue_rechte():
    rights = st.session_state.get('rechte', None)
    if rights == 1: return ['Depot Live Status', 'Depot Reports', 'Forecast','C&E check','Hick-Up','Admin','Warehouse Conditions', 'Warehouse Conditions Details','"What\'s Next"', 'Last Mile', 'Stock Inventory']
    elif rights == 2: return ['Depot Live Status', 'Depot Reports', 'Forecast','C&E check','Hick-Up','Warehouse Conditions', 'Warehouse Conditions Details','"What\'s Next"', 'Last Mile', 'Stock Inventory']
    elif rights == 3: return ['Depot Live Status', 'Depot Reports', 'Forecast']
    elif rights == 4 or rights == 5: return ["Depot Live Status"]
    elif rights == 6: return ["Depot Live Status", 'Depot Reports', 'Forecast']
    return []

# --- 4. DATENBANK ---

def read_user():    
    return read_Table("user")


# --- 5. MAIN LOGIK ---
def main():
    # 1. User Daten laden
    with st.spinner("Lade System..."):
        users_df = read_user()
        if users_df is None or users_df.empty:
            st.error("Konnte User-Tabelle nicht laden.")
            st.stop()
        users_df.set_index('username', inplace=True)

    # 2. Credentials aufbauen
    credentials = {'usernames': dict()}
    for idx, row in users_df.iterrows():
        credentials['usernames'][idx] = {
            'name': row['name'],
            'password': row['password'],
            'email': row.get('email', ''),  
            'access_rights': row['rechte']  
        }

    # 3. Authenticator instanziieren
    # Wir speichern den Authenticator NICHT im Session State, da sich die Credentials (z.B. nach Registrierung)
    # ändern können. Das Objekt muss bei jedem Rerun mit den aktuellen Daten erstellt werden.
    authenticator = stauth.Authenticate(
        credentials=credentials,
        cookie_name='pams_cookie',
        cookie_key='super_secret_key', # Muss auf PROD und DEV identisch sein
        cookie_expiry_days=30
    )
    
    # Authenticator im Session State für Logout-Funktion verfügbar machen (falls benötigt)
    st.session_state.authenticator = authenticator

    # 4. Login-Check (Prüft automatisch Cookies!)
    name, authentication_status, username = authenticator.login(location='main')

    # ---------------------------------------------------------
    # B) LOGIK-WEICHE BASIEREND AUF AUTHENTICATOR-STATUS
    # ---------------------------------------------------------
    
    if authentication_status:
        # User erfolgreich validiert (durch Login oder Cookie)
        st.session_state.user = name
        st.session_state.rechte = credentials['usernames'][username]['access_rights']
        
        # Rechteprüfung
        if st.session_state.rechte == 0:
            st.error("Sie haben noch keine Berechtigung für diese Anwendung. Bitte Kontaktieren Sie den Admin.")
            logout_page()
            st.stop()

        # --- NAVIGATION LADEN ---
        st.logo("Data/img/PAMS.svg") 
        allowed_page_names = user_menue_rechte()
        st_pages = []
        
        for page_name in allowed_page_names:
            if page_name in PAGES_CONFIG:
                cfg = PAGES_CONFIG[page_name]
                wrapped_func = page_loader_wrapper(cfg['func'], page_name)
                safe_url_path = page_name.replace(" ", "_").replace("'", "").replace('"', "")
                st_pages.append(st.Page(wrapped_func, title=page_name, icon=cfg.get('icon'), url_path=safe_url_path))
        
        # Logout ganz unten anfügen
        st_pages.append(st.Page(logout_page, title="Logout", icon="🚪", url_path="logout"))

        try:
            pg = st.navigation(st_pages, position='top', expanded=True)
            pg.run()
        except Exception as e:
            st.error(f"Kritischer Fehler in der Navigation: {e}")

    elif authentication_status is False:
        st.error("Benutzername oder Passwort falsch.")
        show_registration_form(users_df)
            
    elif authentication_status is None:
        # Startbildschirm (weder Cookie noch Login)
        st.warning("Bitte Benutzername und Passwort eingeben.")
        show_registration_form(users_df)

if __name__ == "__main__":
    main()