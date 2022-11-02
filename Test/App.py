# Python Module
import streamlit as st
from streamlit_option_menu import option_menu # pip install streamlit-option-menu # CSS Style für Main Menu # https://icons.getbootstrap.com
import pandas as pd #Pip install pandas
import plotly_express as px #pip install plotly_expression
#Eigene Klassen


# Zum Ausführen
#     streamlit run "/Users/martinwolf/Python/Superdepot Reporting/Test/App.py"

# --- Set Global Page Configs ---
st.set_page_config(layout="wide", page_title="SuperDepot", page_icon=":bar_chart:")
# ----- Load aggregated data -----
@st.cache(allow_output_mutation=True)
def LoadData():
    dfDaten = pd.read_csv('/Users/martinwolf/Python/Superdepot Reporting/Test/valid.csv', sep=';', encoding='utf-8')
    return dfDaten
# ----- Config Main Menue -----
selected2 = option_menu(None, ["Live Status", "Lagerbewegungen", 'Mitarbeiterauswertung', "Auftragsübersicht", 'Einstellungen'], 
    icons=['cloud-fog2', 'award', "list-task", 'back'], 
    menu_icon="cast", default_index=0, orientation="horizontal")
#selected2
# ----- Login -----
if selected2 == "Live Status":
    df = LoadData()
    #df.index to date
    df['Datum'] = pd.to_datetime(df.index)
    st.dataframe(df)
    fig = px.bar(df, x='Datum', y="Picks Gesamt", barmode="group")
    st.plotly_chart(fig)


