
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
                </style>
                """
                # div[data-testid="stStatusWidget"] {
                # visibility: hidden;
                # height: 0%;
                # position: fixed;
                # }
#                 #MainMenu {
#                 visibility: hidden;
#                 height: 0%;
#                 }
#                 header {
#                 visibility: hidden;
#                 height: 0%;
#                 }
#                 footer {
#                 visibility: hidden;
#                 height: 0%;
#                 }
#                 .css-18e3th9 {
#                      padding-top: 0rem;
#                      padding-bottom: 10rem;
#                      padding-left: 5rem;
#                      padding-right: 5rem;
#                  }
#                 .css-1d391kg {
#                      padding-top: 0rem;
#                      padding-right: 1rem;
#                      padding-bottom: 3.5rem;
#                      padding-left: 1rem;
#                  }
#                  div.block-container{padding-top:0rem;}
#                 """
#st.markdown(hide_streamlit_style, unsafe_allow_html=True)

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
        "background-color": "#7BD192",
    },
    "div": {
        "max-width": "32rem",
    },
    "span": {
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
    
    
    page = st_navbar(user_menue_rechte())#, styles=styles)
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
        

# def login():

#     df = read_table('user')
#     usernames = df['username'].tolist()
#     names = df['name'].tolist()
#     passwords = df['password'].tolist()
#     funktionen = df['function'].tolist()
#     rechte = df['rechte'].tolist()
#     credentials = {"usernames":{}}
    

#     # Extract the values from the DataFrame and add them to the 'credentials' dictionary.
#     for uname,name,pwd,funktion,rechte in zip(usernames,names,passwords,funktionen,rechte):
#         user_dict = {"name": name, "password": pwd, "function": funktion, "rechte": rechte}
#         credentials["usernames"].update({uname: user_dict})
    
#     authenticator = stauth.Authenticate(credentials, "PamsReportingTool", "random_key",
#                                             cookie_expiry_days=30)
#     authenticator.login()
#     st.session_state.user = name
#     st.session_state.rechte = df.loc[df['name'] == name, 'rechte'].iloc[0]

#     user_menue_frontend()
    
# def logout():
    
#     authenticator = login()
#     authenticator.logout('Logout', 'main')
    
#     if st.session_state.user is None:
#         st.success("Logout successful!", key='logout_success')
#         st.session_state.rechte = 0
#         st.session_state.user = ''
#         st.session_state.password = ''
#         st.rerun()


def main():
    if 'rechte' not in st.session_state:
        authentication_status = Login.Login(self=Login)
    else:
        user_menue_frontend()

if __name__ == '__main__':
    main()