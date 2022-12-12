import streamlit as st
import pandas as pd
import numpy as np
import datetime
#from Data_Class.SQL import sql_datenLadenLabel,sql_datenLadenOderItems,sql_datenLadenStammdaten,sql_datenLadenOder
#from Data_Class.DB_Daten_Agg import orderDatenAgg
import plotly_express as px
from streamlit_option_menu import option_menu

from Data_Class.SQL import createnewTable, sql_datenLadenMLGT

class Infocenter:
    
    
    
    def menueLaden():
        selected2 = option_menu(None, ["Schulungsunterlagen", "Arbeitsanweisungen","Sicherheitsunterweisungen",'Daten Bearbeiten' ],
        icons=['house', 'cloud-upload', "list-task"], 
        menu_icon="cast", default_index=0, orientation="horizontal")
        return selected2   
    
    def showSchulungsunterlagen():
        st.header("Schulungsunterlagen")

    def page():
        selected2 = Infocenter.menueLaden()
        if selected2 == "Schulungsunterlagen":
            Infocenter.showSchulungsunterlagen()
        # elif selected2 == "Arbeitsanweisungen":
        #     #Infocenter.datenUpdate()
        # elif selected2 == "Sicherheitsunterweisungen":
        #     #Infocenter.ich()
        # elif selected2 == "Daten Bearbeiten":
        #     #Infocenter.ich()