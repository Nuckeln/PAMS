# Python Module
import streamlit as st # Streamlit Web App Framework
from streamlit_option_menu import option_menu # pip install streamlit-option-menu # CSS Style für Main Menu # https://icons.getbootstrap.com
import pandas as pd # Dataframes
from PIL import Image # Bilder

#Eigene Klassen
from Seiten.P_Login import Login
from Seiten.P_Mitarbeiterauswertung import *
from Seiten.P_Bewegungsdaten import *
from Seiten.P_Auftragsübersicht import *
from Seiten.P_Forecast import *
from Seiten.P_Einstellungen import *

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
st.markdown(hide_streamlit_style, unsafe_allow_html=True) 


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

# ----- Config Main Menue -----
# BAT LOGO 
st.sidebar.image(img, width=300)
with st.sidebar:
    selected2 = option_menu('"Menu', ["Live Status","Auftragsübersicht","Lagerbewegungen",'Mitarbeiter','Forecast', 'Einstellungen'], 
        icons=['cloud-fog2', 'award', "list-task", 'back'], 
        menu_icon="cast", )
#selected2
# ----- Login -----
Login = Login()
authentication_status = Login.Login()
if authentication_status == True:
    #erfolgreich eingelogt dann Code ausführen!
    # ----- gewählte Page Laden -----
    if selected2 == 'Live Status':
        st.markdown("Hier kommt der Live Status Screen")
        dfDaten = LadeBewegungsdaten()
        

        st.dataframe(dfDaten)
        fig = px.line(dfDaten, x="Pick Datum", y="Umlagerung")
        st.plotly_chart(fig)


    if selected2 == 'Mitarbeiter':
        dfDaten = LadeBewegungsdaten()
        Seite = Seite1()
        Seite.Ladeseite(dfDaten)
    if selected2 == 'Lagerbewegungen':
        dfDaten = LadeBewegungsdaten()
        pageLager = Page_Bewegungsdaten()
        pageLager.GoGO(dfDaten)
    if selected2 == 'Auftragsübersicht':
        dfLS = LadeLSDaten()
        pageAuftrag = Page_Auftragsübersicht()
        pageAuftrag.Auftragsübersicht_Page(dfLS)
    if selected2 == 'Forecast':
        pageForecast = Forecast()
        pageForecast.LadeForecast()
    if selected2 == 'Einstellungen':
        pageEinstellungen = Einstellungen()
        pageEinstellungen.SeiteEinstellungen()

        



