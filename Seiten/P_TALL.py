
import streamlit as st
import hydralit_components as hc
from Data_Class.cal_lt22_TALL_Data import fuege_Stammdaten_zu_LT22

def page():
    st.write('TALL PALL')
# for 1 (index=5) from the standard loader group

    df = fuege_Stammdaten_zu_LT22()
    st.data_editor(df)
    # filtr by 'Queue' == 'GITPD'
    dfGITPD = df[df['Queue'] == 'GITPD']
    st.data_editor(dfGITPD)
    
    # create df with Pal_ID, Teilbar_durch, Teilhöhe, height_PAL
    
    dfPal = df[['Pal_ID', 'Teilbar_durch', 'Teilhöhe', 'height_PAL']]
    #save as csv
    dfPal.to_csv('dfPal.csv', index=False)
    
