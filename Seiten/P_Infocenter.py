import base64
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
        pdf1 = ('/Users/martinwolf/Desktop/Ret.pdf')
        with st.expander("Schulungsunterlagen", expanded=True):
            st.write("Hier finden Sie alle Schulungsunterlagen")
            Infocenter.pdfAnzeigen(pdf1)
            #st.markdo
        
    def pdfAnzeigen(pdffile):
        if pdffile != "":
            pdf = open(pdffile, 'rb')
            base64_pdf = base64.b64encode(pdf.read()).decode('utf-8')
            pdf_display = f'<embed src="data:application/pdf;base64,{base64_pdf}" width="100%" height="600px" type="application/pdf">'
            st.markdown(pdf_display, unsafe_allow_html=True)

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