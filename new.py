
import hydralit_components as hc


from PIL import Image 
import streamlit as st
#Eigene Klassen
from Seiten.P_UserLogin import Login
from Seiten.P_Live import LIVE
from Seiten.P_Report import reportPage
from Seiten.P_Admin import adminPage
from Seiten.P_Forecast import main as pageForecast
from Seiten.P_Nachschub import pageStellplatzverwaltung
from Seiten.P_Ladeplan import main as pageLadeplan


st.set_page_config(layout="wide", page_title="PAMS Report-Tool", page_icon=":bar_chart:",initial_sidebar_state="expanded")

# hide_streamlit_style = """
#                 <style>
#                 @import url('https://fonts.googleapis.com/css?family=Montserrat');
#                 html, body, [class*="css"]  {
#                 font-family: 'Montserrat';
#                 }
                
#                 div[data-testid="stToolbar"] {
#                 visibility: hidden;
#                 height: 0%;
#                 position: fixed;
#                 }
#                 div[data-testid="stDecoration"] {
#                 visibility: hidden;
#                 height: 0%;
#                 position: fixed;
#                 }
#                 div[data-testid="stStatusWidget"] {
#                 visibility: hidden;
#                 height: 0%;
#                 position: fixed;
#                 }
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
#                 </style>
#                 """

# st.markdown(hide_streamlit_style, unsafe_allow_html=True)



img = Image.open('Data/img/logo.png', mode='r')


# authentication_status = None
authentication_status = Login.Login(self=Login)



menu_data = [
    {'icon': "far fa-copy", 'label':"Left End"},
    {'id':'Copy','icon':"🐙",'label':"Copy"},
    {'icon': "fa-solid fa-radar",'label':"Dropdown1", 'submenu':[{'id':' subid11','icon': "fa fa-paperclip", 'label':"Sub-item 1"},{'id':'subid12','icon': "💀", 'label':"Sub-item 2"},{'id':'subid13','icon': "fa fa-database", 'label':"Sub-item 3"}]},
    {'icon': "far fa-chart-bar", 'label':"Chart"},#no tooltip message
    {'id':' Crazy return value 💀','icon': "💀", 'label':"Calendar"},
    {'icon': "fas fa-tachometer-alt", 'label':"Dashboard",'ttip':"I'm the Dashboard tooltip!"}, #can add a tooltip message
    {'icon': "far fa-copy", 'label':"Right End"},
    {'icon': "fa-solid fa-radar",'label':"Dropdown2", 'submenu':[{'label':"Sub-item 1", 'icon': "fa fa-meh"},{'label':"Sub-item 2"},{'icon':'🙉','label':"Sub-item 3",}]},
]

over_theme = {'txc_inactive': '#FFFFFF'}
menu_id = hc.nav_bar(
    menu_definition=menu_data,
    override_theme=over_theme,
    home_name='Home',
    login_name='Logout',
    hide_streamlit_markers=True, #will show the st hamburger as well as the navbar now!
    sticky_nav=False, #at the top or not
    sticky_mode='pinned', #jumpy or not-jumpy, but sticky or pinned
)

st.write(f"Menu ID: {menu_id}")

LIVE.PageTagesReport()










# # Logging Konfiguration
# if 'authentication_status' not in st.session_state:
#     st.session_state['authentication_status'] = False  # oder ein anderer Standardwert
# #MAC#   streamlit run "/Library/Python_local/Superdepot Reporting/Main.py"
 
# # --- Set Global Page Configs ---
# with st.sidebar: 
#         st.image(img)

#         st.text('')
        
#         sel_main_m = option_menu('PAMS', ['Depot Live Status',"LC Monitor",'Depot Reports','Forecast','Lagerverwaltung','Admin'], 
#             icons=[''], 
#             menu_icon='kanban-fill',
#             styles={'container':{'font':'Montserrat'}},)
        
# hide_full_screen = '''
# <style>
# .element-container:nth-child(3) .overlayBtn {visibility: hidden;}
# .element-container:nth-child(12) .overlayBtn {visibility: hidden;}
# </style>
# '''

# st.markdown(hide_full_screen, unsafe_allow_html=True)
# # ----- Config Main Menue -----

# # ----- Config Main Menue -----

# # ----- Login -----
# authentication_status = None
# authentication_status = Login.Login(self=Login)
# #logging.info(f'Authentifizierungsstatus: {authentication_status}')
# def berechtigung():
#     if st.session_state.rechte == 1:
#         #admin Vollzugriff
#         return ['Depot Live Status',"LC Monitor",'Depot Reports','Forecast','Lagerverwaltung','Admin']
#     elif st.session_state.rechte == 2: 
#         # Manager
#         return ['Depot Live Status',"LC Monitor",'Depot Reports','Forecast','Lagerverwaltung']
#     elif st.session_state.rechte == 3:
#         # Mitarbeiter AD 
#         return ['Depot Live Status','Depot Reports','Forecast','Lagerverwaltung']
#     elif st.session_state.rechte == 4:
#         # Mitarbeiter Fremd
#         return ["Depot Live Status"]
#         # Lager
#     elif st.session_state.rechte == 5:
#         return ["Depot Live Status"]

# if authentication_status == True:
#     user = st.session_state.user
#     #logging.info(f'User: {user}')

# with st.sidebar:
#         Login.authenticator.logout('Logout')
        
#         with st.popover('Passwort ändern'):
#             try:
#                 Login.newPasswort(Login)
#             except:
#                 st.stop()
# check = berechtigung()
# if check == []:
#     st.rerun()
# if sel_main_m == "Depot Live Status":
#     # Prüfe Berechtigung ist Depot Live Status in der Liste
#     if 'Depot Live Status' in check:
#         LIVE.PageTagesReport()
#     else:
#         st.error('Keine Berechtigung für diese Seite')
# if sel_main_m == 'Depot Reports':
#     if 'Depot Reports' in check:
#         reportPage()   
#     else:
#         st.error('Keine Berechtigung für diese Seite')        
# if sel_main_m == 'Forecast':
#     if 'Forecast' in check:
#         pageForecast()
#     else:
#         st.error('Keine Berechtigung für diese Seite')        
# if sel_main_m == 'Lagerverwaltung':
#     if 'Lagerverwaltung' in check:
#         pageStellplatzverwaltung()
#     else:
#         st.error('Keine Berechtigung für diese Seite')        
# if sel_main_m == 'Admin':
#     if 'Admin' in check:
#         adminPage()
#     else:
#         st.error('Keine Berechtigung für diese Seite')        
# if sel_main_m == 'LC Monitor':
#     if 'LC Monitor' in check:
#         pageLadeplan()
#     else:
#         st.error('Keine Berechtigung für diese Seite')        
