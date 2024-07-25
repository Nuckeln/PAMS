
import streamlit as st
import pandas as pd
import numpy as np
import datetime
import streamlit_autorefresh as sar
from PIL import Image
import plotly_express as px
from annotated_text import annotated_text, annotation
import streamlit_timeline as timeline

from Data_Class.wetter.api import getWetterBayreuth
from Data_Class.MMSQL_connection import read_Table

import matplotlib.pyplot as plt
from matplotlib.patches import Arc




def loadDF(day1=None, day2=None): 
    dfOr = read_Table('prod_Kundenbestellungen_14days')
    #load parquet
    #dfOr = pq.read_table('df.parquet.gzip').to_pandas()
    dfOr['PlannedDate'] = dfOr['PlannedDate'].astype(str)
    dfOr['PlannedDate'] = pd.to_datetime(dfOr['PlannedDate'].str[:10])
    if day1 is None:
        day1 = pd.to_datetime('today').date()
    else:
        day1 = pd.to_datetime(day1).date()
    if day2 is None:
        day2 = pd.to_datetime('today').date()
    else:
        day2 = pd.to_datetime(day2).date()
    #filter nach Datum
    dfOr = dfOr[(dfOr['PlannedDate'].dt.date >= day1) & (dfOr['PlannedDate'].dt.date <= day2)]
    dfOr = dfOr[dfOr['Picks Gesamt'] != 0]
    
    dfOr['Fertiggestellt'] = pd.to_datetime(dfOr['Fertiggestellt'], format='%Y-%m-%d %H:%M:%S')
    #add two hours to Feritggestellt
    dfOr['Fertiggestellt'] = dfOr['Fertiggestellt'] + pd.to_timedelta('2:00:00')

    return dfOr


