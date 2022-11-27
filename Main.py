# Python Module
import streamlit as st # Streamlit Web App Framework
from streamlit_option_menu import option_menu # pip install streamlit-option-menu # CSS Style für Main Menu # https://icons.getbootstrap.com
import pandas as pd # Dataframes
from PIL import Image # Bilder

#Eigene Klassen
from Seiten.P_Login import Login
from Seiten.P_Live import liveStatusPage
from Seiten.P_Mitarbeiterauswertung import *
from Seiten.P_Bewegungsdaten import *
from Seiten.P_Auftragsübersicht import *
from Seiten.P_Forecast import *
from Seiten.P_Einstellungen import *
from Seiten.P_Fehlverladungen import fehlverladungenPage
from data_Class.SQL import sql_datenLadenLabel,sql_datenLadenOderItems,sql_datenLadenStammdaten,sql_datenLadenOder
from data_Class.DB_Daten_Agg import orderDatenAgg

from data_Class.wetter.api import getWetterBayreuth

# Zum Ausführen
#MAC#    streamlit run "/Users/martinwolf/Python/Superdepot Reporting/Main.py"
#WIN#    streamlit run "

# --- Set Global Page Configs ---
st.set_page_config(layout="wide", page_title="SuperDepot", page_icon=":bar_chart:",initial_sidebar_state="expanded")

hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
pages {visibility: hidden;}

</style>

"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True,) 
img = Image.open('Data/img/logo.png', mode='r')
# ----- Load aggregated data -----
#@st.cache(allow_output_mutation=True)
def LadeBewegungsdaten():
    dfDaten = pd.read_feather('Data/Bewegungsdaten.feather')
    return dfDaten
@st.cache(allow_output_mutation=True)
def LadeLSDaten():
    dfLS = pd.read_excel('Data/df.xlsx')
    return dfLS
@st.cache(allow_output_mutation=True)
def labeOrderDaten():
    df = orderDatenAgg()
    return df

# ----- Config Main Menue -----
# BAT LOGO  
st.sidebar.image(img, width=300)

with st.sidebar:
    sel_main_m = option_menu('"Menu', ["Live Status","Auftragsübersicht","Lagerbewegungen",'Fehlverladungen','Mitarbeiter','Forecast', 'Einstellungen'], 
        icons=['cloud-fog2', 'award', "list-task", 'back'], 
        menu_icon="cast", )


# ----- Login -----
Login = Login()
authentication_status = Login.Login()
if authentication_status == True:
    #erfolgreich eingelogt dann Code ausführen!
    # ----- gewählte Page Laden -----
    if sel_main_m == 'Live Status':
        df = labeOrderDaten()
        liveStatusPage(df)
    if sel_main_m == 'Mitarbeiter':
        dfDaten = LadeBewegungsdaten()
        Seite = Seite1()
        Seite.Ladeseite(dfDaten)
    if sel_main_m == 'Lagerbewegungen':
        dfDaten = LadeBewegungsdaten()
        pageLager = Page_Bewegungsdaten()
        pageLager.GoGO(dfDaten)
    if sel_main_m == 'Auftragsübersicht':
        dfLS = LadeLSDaten()
        pageAuftrag = Page_Auftragsübersicht()
        pageAuftrag.Auftragsübersicht_Page(dfLS)
    if sel_main_m == 'Forecast':
        pageForecast = Forecast()
        pageForecast.LadeForecast()
    if sel_main_m == 'Einstellungen': 
        seiteLaden()
    if sel_main_m == 'Fehlverladungen':
        fehlverladungenPage()

        



