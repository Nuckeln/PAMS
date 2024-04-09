
import hydralit_components as hc


from PIL import Image 
import streamlit as st
from streamlit_navigation_bar import st_navbar
#Eigene Klassen

# from Data_Class.Authenticator import login
import streamlit_authenticator as stauth
from Data_Class.SQL import read_table, updateTable


#from Data_Class.Authenticator import login
from Seiten.LOGIN import Login
from Seiten.P_Live import LIVE
from Seiten.P_Report import reportPage
from Seiten.P_Admin import adminPage
from Seiten.P_Forecast import main as pageForecast
from Seiten.P_Nachschub import pageStellplatzverwaltung
from Seiten.P_Ladeplan import main as pageLadeplan

#MAC#   streamlit run "/Library/Python_local/Superdepot Reporting/main.py"
st.set_page_config(layout="wide", page_title="PAMS Report-Tool", page_icon=":bar_chart:",initial_sidebar_state="expanded")

# st.header('PAMS Report-Tool-DEV System')
# st.write('Momentan abgeschaltet')

img = Image.open('Data/img/logo.png', mode='r')


def user_menue_rechte():
    if st.session_state.rechte == 1:
        #admin Vollzugriff
        return ['Depot Live Status',"LC Monitor",'Depot Reports','Forecast','Lagerverwaltung','Admin','Logout']
    elif st.session_state.rechte == 2: 
        # Manager
        return ['Depot Live Status',"LC Monitor",'Depot Reports','Forecast','Lagerverwaltung','Logout']
    elif st.session_state.rechte == 3:
        # Mitarbeiter AD 
        return ['Depot Live Status','Depot Reports','Forecast','Lagerverwaltung','Logout']
    elif st.session_state.rechte == 4:
        # Mitarbeiter Fremd
        return ["Depot Live Status",'Logout']
        # Lager
    elif st.session_state.rechte == 5:
        return ["Depot Live Status",'Logout']

def user_menue_frontend():
    styles = {
        "nav": {
            "background-color": "#0e2b63",
        },
        "a": {
            "color": "white",  # Setzt die Textfarbe auf Weiß
        },
        "img": {
            "src": "Data/img/logo.png",  # Pfad zu Ihrem Logo
            "height": "30px",  # Höhe des Logos anpassen
            "width": "auto",  # Breite des Logos automatisch anpassen
        }
    }
    
    page = st_navbar(user_menue_rechte(), styles=styles, options={"use_padding": False})
    # Ihre Seitenlogik hier...
    if page == 'Depot Live Status':
        LIVE.PageTagesReport()
    elif page == 'LC Monitor':
        pageLadeplan()
    elif page == 'Depot Reports':
        reportPage()
    elif page == 'Forecast':
        pageForecast()
    elif page == 'Lagerverwaltung':
        pageStellplatzverwaltung()
    elif page == 'Admin':
        adminPage()
    elif page == 'Logout':
        Login.Logout(self=Login)
        

def main():
    if 'rechte' not in st.session_state or 'user' not in st.session_state:
        authentication_status = Login.einloggen(self=Login)
        user_menue_frontend()
    else:
        user_menue_frontend()

if __name__ == '__main__':
    main()