import pandas as pd
from Data_Class.SynapseReader import SynapseReader
import streamlit as st


@st.cache_data
def load_datasets():
    try:
        lastMileT_T = SynapseReader.load_delta("silver/Logistics/Germany/Supplychain/LastMile/DDN/thirdparty_kn_ddn_bat_statusreporting/", as_pandas=True)
    except Exception as e:
        st.error(f"Fehler beim Laden der Daten: {e}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
    return lastMileT_T
 
def app(): 
    pass