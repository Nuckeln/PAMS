import streamlit as st
from streamlit_navigation_bar import st_navbar
import streamlit_authenticator as stauth
import bcrypt

import pandas as pd
from Seiten.P_Live import LIVE
from Seiten.P_Report import reportPage
from Seiten.P_Admin import adminPage
from Seiten.P_Forecast import main as pageForecast
from Seiten.P_Nachschub import pageStellplatzverwaltung
from Seiten.P_Ladeplan import main as pageLadeplan
from Seiten.C_E_check import main as pageC_E_check
from Data_Class.MMSQL_connection import read_Table,save_Table_append
#MAC#   streamlit run "/Library/Python_local/Superdepot Reporting/main.py"

st.set_page_config(layout="wide", page_title="PAMS Report-Tool", page_icon=":bar_chart:",)


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
# ----- Config Main Menue -----
def user_menue_rechte():
    # Sicherstellen, dass 'rechte' initialisiert ist
    if 'rechte' not in st.session_state:
        st.session_state.rechte = None  # oder einen anderen Standardwert, falls geeignet
    # Logik zur Bestimmung der Menürechte basierend auf den Benutzerrechten
    if st.session_state.rechte == 1:
        # Admin Vollzugriff
        return ['Depot Live Status', "LC Monitor", 'Depot Reports', 'Forecast', 'Lagerverwaltung','C&E check', 'Admin']
    
    elif st.session_state.rechte == 2:
        # Manager BAT
        return ['Depot Live Status', "LC Monitor", 'Depot Reports', 'Forecast', 'Lagerverwaltung','C&E check']
    
    elif st.session_state.rechte == 3:
        # Mitarbeiter BAT AD 
        return ['Depot Live Status', "LC Monitor", 'Depot Reports', 'Forecast', 'Lagerverwaltung']
    
    elif st.session_state.rechte == 4:
        # Mitarbeiter Fremd
        return ["Depot Live Status"]
    
    elif st.session_state.rechte == 5:
        # Live Bildschirm
        return ["Depot Live Status"]
   
    elif st.session_state.rechte == 6:
        # Mitarbeiter Extern Sachbearbeiter/Teamleiter
        return ["Depot Live Status", 'Depot Reports', 'Forecast', 'Lagerverwaltung']


def user_menue_frontend():
    styles = {
    "nav": {
        "background-color": "#0e2b63",
        "text-color": "#e72582",
    },
    "div": {
        "max-width": "70rem",
    },
    "span": {
        "color": "white",
        "border-radius": "0.5rem",
        "padding": "0.4375rem 0.625rem",
        "margin": "0 0.125rem",
    },
    "active": {
        "background-color": "rgba(255, 255, 255, 0.25)",
    },
    "hover": {
        "background-color": "rgba(255, 255, 255, 0.35)",
    },
    }


    page = st_navbar(user_menue_rechte(), styles=styles, options={"use_padding": True,'show_menu': False},logo_path='Data/img/logo_white.svg',selected='Depot Live Status')
    #Seitenlogik hier...
    if page == 'Depot Live Status':
        LIVE.PageTagesReport()
    if page == 'LC Monitor':
        pageLadeplan()
    if page == 'Depot Reports':
        reportPage()
    if page == 'Forecast':
        pageForecast()
    if page == 'Lagerverwaltung':
        pageStellplatzverwaltung()
    if page == 'Admin':
        adminPage()
    if page == 'C&E check':
        pageC_E_check()
        
    if page == 'Logout':
        st.session_state.user = None
        st.session_state.rechte = None
        
               
def main():
    with open("style.css") as css:
        st.markdown(f'<style>{css.read()}</style>', unsafe_allow_html=True)
    if 'user' not in st.session_state:
        st.session_state.user = None  
    
    users_df = read_Table("user")
    users_df.set_index('username', inplace=True)

    # Umstrukturieren des DataFrames, um den erwarteten Schlüsseln zu entsprechen
    credentials = {
        'usernames': dict()
    }
    for idx, row in users_df.iterrows():
        credentials['usernames'][idx] = {
            'name': row['name'],
            'password': row['password'],
            'email': row.get('email', ''),  
            'access_rights': row['rechte']  
        }

    # Authentifizierungsobjekt erstellen
    authenticator = stauth.Authenticate(
        credentials=credentials,
        cookie_name='mein_cookie_name',
        cookie_key='mein_sehr_geheimer_schlüssel',
        cookie_expiry_days=30
    )
    # Authentifizierungsfunktion aufrufen
    fields = {
        'username': 'Benutzername',
        'password': 'Passwort',
        'submit_button': 'Einloggen'
    }
    st.session_state.user, authentication_status, username = authenticator.login(
        location='main', 
        fields=fields,
        clear_on_submit=True
    )

    if authentication_status:
        st.session_state.rechte = credentials['usernames'][username]['access_rights']  # Zugriffsrechte aus den Benutzerdaten setzen
        if st.session_state.rechte == 0:
            st.error("Sie haben noch keine Berechtigung für diese Anwendung bitte Kontaktieren Sie Christian Hammann oder Martin Wolf.")
            authenticator.logout()
            st.stop()
        user_menue_frontend()
        #authenticator.logout()
    elif authentication_status is False:
        st.error("Benutzername oder Passwort ist falsch.")
    else:
        st.warning("Bitte Benutzername und Passwort eingeben.")
    if st.session_state.user is None:
        
        with st.popover("Registrieren", help = "Hier können Sie sich als neuer Benutzer registrieren."):
            with st.form(key="register_form"):
                new_user = st.text_input("Username")
                new_username = st.text_input("Klarname")
                new_password = st.text_input("Passwort", type="password")
                register_button = st.form_submit_button("Registrieren")
            #TODO: Passwortstärkeprüfung eventuell einbauen? Momentan kann alles als Passwort eingegeben werden.
            # Wenn der Registrierungsbutton gedrückt wird, Benutzerdaten speichern
            if register_button:
                #Prüfe ob es den Benutzer schon gibt
                if new_user in users_df.index:
                    st.error("Benutzer existiert bereits.")
                    return
                if new_user == "":
                    st.error('Bitte geben Sie einen User ein')
                if new_username == "":
                    st.error("Bitte geben Sie einen Namen ein.")
                    return
                if new_password == "":
                    st.error("Bitte geben Sie ein Passwort ein.")
                # Passwort hashen
                function = "None"
                recht = 0
                hashed_password = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()
                new_user_data = pd.DataFrame({
                    "username": [new_user],
                    "name": [new_username],  # o
                    "password": [hashed_password],  # Gehashtes Passwort speichern
                    "function": [function],
                    "rechte": [recht]
                })
                save_Table_append(new_user_data, "user")  # Speichert die Daten in der Datenbank
                st.success("Benutzer erfolgreich registriert, Bitte Kontaktieren Sie Christian Hammann oder Martin Wolf um Berechtigungen zu erhalten.")
        
    
        
if __name__ == "__main__":
    main()
