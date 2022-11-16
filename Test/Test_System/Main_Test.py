# Python Module
import streamlit as st # Streamlit Web App Framework
from streamlit_option_menu import option_menu # pip install streamlit-option-menu # CSS Style für Main Menu # https://icons.getbootstrap.com
import pandas as pd # Dataframes
from PIL import Image # Bilder

#Eigene Klassen

from SQL_Verbindung import datenLadenLabel , datenLadenAufträge , datenLadenStammdaten

# Zum Ausführen
#MAC#    streamlit run "/Users/martinwolf/Python/Superdepot Reporting/Test/Test_System/Main_Test.py"
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

dfAufträge = datenLadenAufträge()
dfStammdaten = datenLadenStammdaten()
dfLabel = datenLadenLabel()
st.dataframe(dfLabel)
st.dataframe(dfAufträge)
st.dataframe(dfStammdaten)