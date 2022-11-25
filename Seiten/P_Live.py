import streamlit as st
import pandas as pd
import numpy as np
from data_Class.SQL import sql_datenLadenLabel,sql_datenLadenOderItems,sql_datenLadenStammdaten,sql_datenLadenOder
from data_Class.DB_Daten_Agg import test



def sessionstate():
    if 'key' not in st.session_state:
        st.session_state['key'] = 'value'
    if 'key' not in st.session_state:
        st.session_state.key = +1

def liveStatusPage():
    df = test()
    st.write(df)
