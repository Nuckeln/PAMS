import streamlit as st
from streamlit_navigation_bar import st_navbar

from Seiten.LOGIN import Login
from Seiten.P_Live import LIVE
from Seiten.P_Report import reportPage
from Seiten.P_Admin import adminPage
from Seiten.P_Forecast import main as pageForecast
from Seiten.P_Nachschub import pageStellplatzverwaltung
from Seiten.P_Ladeplan import main as pageLadeplan
#MAC#   streamlit run "/Library/Python_local/Superdepot Reporting/main.py"

st.set_page_config(layout="wide", page_title="PAMS Report-Tool", page_icon=":bar_chart:",)

Login.einloggen(self=Login)


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
#st.markdown(hide_full_screen, unsafe_allow_html=True)
# ----- Config Main Menue -----









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


    page = st_navbar(user_menue_rechte(), styles=styles, options={"use_padding": True},logo_path='Data/img/logo_white.svg',selected='Depot Live Status')
    # Ihre Seitenlogik hier...
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
    if page == 'Logout':
        Login().Logout()
               
def main():
    with open( "style.css" ) as css:
        st.markdown( f'<style>{css.read()}</style>' , unsafe_allow_html= True)

    try:
        user_menue_frontend()
    except:
        pass


if __name__ == '__main__':
    main()