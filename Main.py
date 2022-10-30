# Python Module
import streamlit as st # Streamlit Web App Framework
from streamlit_option_menu import option_menu # pip install streamlit-option-menu # CSS Style für Main Menu # https://icons.getbootstrap.com
import pandas as pd # Dataframes
from Pages.P_Auftragsübersicht import Page_Auftragsübersicht #Pip install pandas
from PIL import Image # Bilder
#Eigene Klassen
from Pages.P_Login import Login
from Pages.P_Mitarbeiterauswertung import *
from Pages.P_Bewegungsdaten import *
#from Data_Class.C_Daten_Lieferscheine import *
# ist das jetzt ein Kommentar?

# Zum Ausführen
#MAC#    streamlit run "/Users/martinwolf/Python/Superdepot Reporting/Main.py"
#WIN#    streamlit run "D:\SuperDepot Python 2\App.py"

# --- Set Global Page Configs ---
st.set_page_config(layout="wide", page_title="SuperDepot", page_icon=":bar_chart:",initial_sidebar_state="collapsed")
st.markdown("<style> ul {display: none;} </style>", unsafe_allow_html=True)
img = Image.open('Data/Logo.png')
# ----- Load aggregated data -----
@st.cache(allow_output_mutation=True)
def LadeBewegungsdaten():
    dfDaten = pd.read_excel('Data/Bewegungsdaten.xlsx')
    return dfDaten
@st.cache(allow_output_mutation=True)
def LadeLSDaten():
    df = pd.read_excel('Data/df.xlsx')
    return df

# ----- Config Main Menue -----
# BAT LOGO 
st.sidebar.image(img, width=200)
with st.sidebar:
    selected2 = option_menu('"Menu', ["Live Status", "Lagerbewegungen", 'Mitarbeiterauswertung', "Auftragsübersicht", 'Einstellungen'], 
        icons=['cloud-fog2', 'award', "list-task", 'back'], 
        menu_icon="cast", )#default_index=0, orientation="horizontal")
#selected2
# ----- Login -----
Login = Login()
authentication_status = Login.Login()
if authentication_status == True:
    #erfolgreich eingelogt dann Code ausführen!
    # ----- gewählte Page Laden -----
    if selected2 == 'Live Status':
        st.markdown("Hier kommt der Live Status Screen")
    if selected2 == 'Mitarbeiterauswertung':
        dfDaten = LadeBewegungsdaten()
        Seite = Seite1()
        Seite.Ladeseite(dfDaten)
    if selected2 == 'Lagerbewegungen':
        dfDaten = LadeBewegungsdaten()
        pageLager = Page_Bewegungsdaten()
        pageLager.LadeBewegungsdaten(dfDaten)
    if selected2 == 'Auftragsübersicht':
        df = LadeLSDaten()
        pageLieferscheine = Page_Auftragsübersicht()
        pageLieferscheine.LadeAuftragsübersicht(df)
        



