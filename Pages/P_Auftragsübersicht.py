from distutils.log import info
from email.header import Header
from enum import unique
from itertools import count
import datetime
from folium import Tooltip
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from requests import head
import streamlit as st
from PIL import Image

class Page_Auftragsübersicht:
        
        def LadeAuftragsübersicht(self, df):
            # ------ Änderungen am Dataframe
            # Rundung auf 5 min takt
            st.header("Auftragsübersicht")
            st.dataframe(df)
            
 


