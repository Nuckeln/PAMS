import streamlit as st
import pandas as pd
import numpy as np

import streamlit_autorefresh as sar
from PIL import Image
import plotly_express as px
from annotated_text import annotated_text, annotation
import streamlit_timeline as timeline
from PIL import Image, ImageDraw, ImageFont

from Data_Class.wetter.api import getWetterBayreuth
from Data_Class.sql import SQL
import datetime
import pytz

import matplotlib.pyplot as plt
from matplotlib.patches import Arc
import time

@st.cache_data
def loadDF(day1=None, day2=None): 
    # lade Daten
    ngp_detail_tabelle = pd.read_csv('Data/Berechnete_NGP_Daten.csv')
    ngp_Delivery_level = pd.read_csv('Data/Berechnete_NGP_Kosten.csv')
    ngp_detail_tabelle['Deliv. date(From/to)'] = pd.to_datetime(ngp_detail_tabelle['Deliv. date(From/to)'])
    ngp_Delivery_level['Deliv. date(From/to)'] = pd.to_datetime(ngp_Delivery_level['Deliv. date(From/to)'])
    return ngp_detail_tabelle, ngp_Delivery_level

def filtereDaten(df, day1, day2):
    # Konvertiere day1 und day2 in datetime
    day1 = pd.to_datetime(day1)
    day2 = pd.to_datetime(day2)
    
    # Filtere Daten
    df['Deliv. date(From/to)'] = pd.to_datetime(df['Deliv. date(From/to)'])
    df = df[(df['Deliv. date(From/to)'] >= day1) & (df['Deliv. date(From/to)'] <= day2)]
    df['Tag'] = df['Deliv. date(From/to)']
    return df


def plot_data(df,ngp_Delivery_level, plot_as_DD_or_W_MM_or_YY, sum_or_mean):
    ''' 
    BAT Colours
    #0e2b63 darkBlue
    #004f9f MidBlue
    #00b1eb LightBlue
    #ef7d00 Orange
    #ffbb00 Yellow
    #ffaf47 Green
    #afca0b lightGreen
    #5a328a Purple
    #e72582 Pink
    '''
    # # Runde Werte auf 2 Nachkommastellen
    # df['Kosten Picking Bayreuth'] = df['Kosten Picking Bayreuth'].round(2)
    # df['K&N_Kosten'] = df['K&N_Kosten'].round(2)
    # df['Actual delivery qty'] = df['Actual delivery qty'].round(2)
    # df['Anzahl_Einheiten'] = df['Anzahl_Einheiten'].round(2)
    # ngp_Delivery_level['Transportkosten'] = ngp_Delivery_level['Transportkosten'].round(2)
    # ngp_Delivery_level['TransportkostenLastMile_Fix_Kg_Preis'] = ngp_Delivery_level['TransportkostenLastMile_Fix_Kg_Preis'].round(2)
    # df['Paletten'] = df['Paletten'].round(2)
    # df['Cases'] = df['Cases'].round(2)
    # df['Packs'] = df['Packs'].round(2)
    
    
    ########################################################
    # Kosten Picking Bayreuth############################################
    ############################################
    if sum_or_mean == 'Summe':
        df_kosten_monat_bay = df.groupby(
            [plot_as_DD_or_W_MM_or_YY], as_index=False)[['Kosten Picking Bayreuth']].sum()
    elif sum_or_mean == 'Median':
        df_kosten_monat_bay = df.groupby(
            [plot_as_DD_or_W_MM_or_YY], as_index=False)[['Kosten Picking Bayreuth']].median()
    else:
        df_kosten_monat_bay = df.groupby(
            [plot_as_DD_or_W_MM_or_YY], as_index=False)[['Kosten Picking Bayreuth']].mean()

    fig1 = px.bar(df_kosten_monat_bay, x=plot_as_DD_or_W_MM_or_YY, y='Kosten Picking Bayreuth', 
                  title=f'Kosten Picking Bayreuth pro {plot_as_DD_or_W_MM_or_YY}', text_auto=True)
    fig1.update_traces(marker_color='#0e2b63')
    
    # Kosten K&N
    if sum_or_mean == 'Summe':
        df_kosten_monat_plot_KN = df.groupby(
            [plot_as_DD_or_W_MM_or_YY], as_index=False)[['K&N_Kosten']].sum()
    elif sum_or_mean == 'Median':
        df_kosten_monat_plot_KN = df.groupby(
            [plot_as_DD_or_W_MM_or_YY], as_index=False)[['K&N_Kosten']].median()
    else:
        df_kosten_monat_plot_KN = df.groupby(
            [plot_as_DD_or_W_MM_or_YY], as_index=False)[['K&N_Kosten']].mean()

    fig2 = px.bar(df_kosten_monat_plot_KN, x=plot_as_DD_or_W_MM_or_YY, y='K&N_Kosten',
                title=f'Kosten K&N pro {plot_as_DD_or_W_MM_or_YY}', text_auto=True)
    fig2.update_traces(marker_color='#0e2b63')
    
    # Actual delivery qty
    if sum_or_mean == 'Summe':
        df_kosten_monat_delq_plot = df.groupby(
            [plot_as_DD_or_W_MM_or_YY], as_index=False)[['Actual delivery qty']].sum()
    elif sum_or_mean == 'Median':
        df_kosten_monat_delq_plot = df.groupby(
            [plot_as_DD_or_W_MM_or_YY], as_index=False)[['Actual delivery qty']].median()
    else:
        df_kosten_monat_delq_plot = df.groupby(
            [plot_as_DD_or_W_MM_or_YY], as_index=False)[['Actual delivery qty']].mean()
    fig4 = px.bar(df_kosten_monat_delq_plot, x=plot_as_DD_or_W_MM_or_YY, y='Actual delivery qty',
                    title=f'Actual delivery qty pro {plot_as_DD_or_W_MM_or_YY}', text_auto=True)
    fig4.update_traces(marker_color='#0e2b63')
    
    # Picks Gesamt
    if sum_or_mean == 'Summe':
        df_kosten_Picks = df.groupby(
            [plot_as_DD_or_W_MM_or_YY], as_index=False)[['Anzahl_Einheiten']].sum()
    elif sum_or_mean == 'Median':
        df_kosten_Picks = df.groupby(
            [plot_as_DD_or_W_MM_or_YY], as_index=False)[['Anzahl_Einheiten']].median()
    else:
        df_kosten_Picks = df.groupby(
            [plot_as_DD_or_W_MM_or_YY], as_index=False)[['Anzahl_Einheiten']].mean()
    fig5 = px.bar(df_kosten_Picks, x=plot_as_DD_or_W_MM_or_YY, y='Anzahl_Einheiten',
                    title=f'Anzahl Einheiten pro {plot_as_DD_or_W_MM_or_YY}', text_auto=True)
    fig5.update_traces(marker_color='#0e2b63')
    
    col1, col2 = st.columns(2)

    with col1:
        st.plotly_chart(fig4)
        if st.checkbox('📊 Daten anzeigen: Actual delivery qty', value=False, key='data_qty'):
            st.dataframe(df_kosten_monat_delq_plot)
            
        st.plotly_chart(fig2)
        if st.checkbox('📊 Daten anzeigen: Kosten Picking exK&N', value=False, key='data_kn'):
            st.dataframe(df_kosten_monat_plot_KN)
            
    with col2:
        st.plotly_chart(fig5)
        if st.checkbox('📊 Daten anzeigen: Anzahl Einheiten', value=False, key='data_picks'):
            st.dataframe(df_kosten_Picks)
        st.plotly_chart(fig1)
        if st.checkbox('📊 Daten anzeigen: Kosten Picking exBayreuth', value=False, key='data_picking'):
            st.dataframe(df_kosten_monat_bay)

    ###### Tranportkosten
    # if transportkosten NaN fill with TransportkostenLastMile_Fix_Kg_Preis
    ngp_Delivery_level['Transportkosten'] = ngp_Delivery_level['Transportkosten'].fillna(ngp_Delivery_level['TransportkostenLastMile_Fix_Kg_Preis'])
    # ermittle Tag Monat Jahr aus Deliv. date(From/to)
    ngp_Delivery_level['Tag'] = ngp_Delivery_level['Deliv. date(From/to)']
    ngp_Delivery_level['Monat'] = ngp_Delivery_level['Deliv. date(From/to)'].dt.to_period('M')
    ngp_Delivery_level['Jahr'] = ngp_Delivery_level['Deliv. date(From/to)'].dt.to_period('Y')
    ngp_Delivery_level['Kalenderwoche'] = ngp_Delivery_level['Deliv. date(From/to)'].dt.isocalendar().week
    st.info('Transportkosten NaN = Keine PLZ Daten vorhanden anteil ca 30% mit TransportkostenLastMile_Fix_Kg_Preis gefüllt')
    st.info('Transportkosten nach Kilometern und Gewichtstabellen Kühne+Nagel ACHTUNG: Die Werte sind nicht konsolidiert Anhame ist der einzelne Transport pro Lieferschein.')
    if sum_or_mean == 'Summe':
        ngp_Delivery_level_plot = ngp_Delivery_level.groupby(
            [plot_as_DD_or_W_MM_or_YY], as_index=False)[['Transportkosten']].sum()
    elif sum_or_mean == 'Median':
        ngp_Delivery_level_plot = ngp_Delivery_level.groupby(
            [plot_as_DD_or_W_MM_or_YY], as_index=False)[['Transportkosten']].median()
    else:
        ngp_Delivery_level_plot = ngp_Delivery_level.groupby(
            [plot_as_DD_or_W_MM_or_YY], as_index=False)[['Transportkosten']].mean()
    try: 
        fig3 = px.bar(ngp_Delivery_level_plot, x=plot_as_DD_or_W_MM_or_YY, y='Transportkosten',
                    title=f'Transportkosten pro {plot_as_DD_or_W_MM_or_YY}', text_auto=True)
        fig3.update_traces(marker_color='#0e2b63')
        st.plotly_chart(fig3)
    except:
        st.warning('Der Filter liefert keine Ergebnisse')
    if st.checkbox('📊 Daten anzeigen: Transportkosten', value=False, key='data_transport'):
        st.dataframe(ngp_Delivery_level_plot)
    try:
        if sum_or_mean == 'Summe':
            ngp_Delivery_level_plot = ngp_Delivery_level.groupby(
                [plot_as_DD_or_W_MM_or_YY], as_index=False)[['TransportkostenLastMile_Fix_Kg_Preis']].sum()
        elif sum_or_mean == 'Median':
            ngp_Delivery_level_plot = ngp_Delivery_level.groupby(
                [plot_as_DD_or_W_MM_or_YY], as_index=False)[['TransportkostenLastMile_Fix_Kg_Preis']].median()
        else:
            ngp_Delivery_level_plot = ngp_Delivery_level.groupby(
                [plot_as_DD_or_W_MM_or_YY], as_index=False)[['TransportkostenLastMile_Fix_Kg_Preis']].mean()
        
        fig8 = px.bar(ngp_Delivery_level_plot, x=plot_as_DD_or_W_MM_or_YY, y='TransportkostenLastMile_Fix_Kg_Preis',
                        title=f'Transportkosten Last Mile FIX KILO Preis 0.1714€ pro {plot_as_DD_or_W_MM_or_YY}', text_auto=True)
        st.plotly_chart(fig8)
    except:
        st.warning('Der Filter liefert keine Ergebnisse')
    if st.checkbox('📊 Daten anzeigen: Transportkosten Last Mile FIX KILO Preis', value=False, key='data_transport_lastmile'):
        st.dataframe(ngp_Delivery_level_plot)


def packnaehe(df2):
    def abweichung_modulo(x, pack_size):
        if pd.isna(x) or pd.isna(pack_size) or pack_size == 0:
            return np.nan
        return x % pack_size

    # Beispiel: df2 existiert bereits, und die Spalten sind vorhanden:
    # 'Name', 'Actual delivery qty', 'Paletten', 'Cases', 'Outers', 'Packs'

    # Neue Spalten: Abweichung von der vollen Gebindegröße
    df2['Abweichung_voll_Palette'] = df2.apply(
        lambda row: abweichung_modulo(row['Actual delivery qty'], row['Paletten']),
        axis=1
    )
    df2['Abweichung_voll_Case'] = df2.apply(
        lambda row: abweichung_modulo(row['Actual delivery qty'], row['Cases']),
        axis=1
    )
    df2['Abweichung_voll_Pack'] = df2.apply(
        lambda row: abweichung_modulo(row['Actual delivery qty'], row['Packs']),
        axis=1
    )

    df_packnaehe = (
        df2.groupby('Name', as_index=False)
        .agg({
            'Abweichung_voll_Palette': lambda x: (x == 0).mean() * 100,
            'Abweichung_voll_Case': lambda x: (x == 0).mean() * 100,
            'Abweichung_voll_Pack': lambda x: (x == 0).mean() * 100,
        })
    )

    df_packnaehe.rename(columns={
        'Name': 'Kunde',
        'Abweichung_voll_Palette': '%_Vollpaletten',
        'Abweichung_voll_Case': '%_VollCases',
        'Abweichung_voll_Pack': '%_VollPacks'
    }, inplace=True)
    def plot_packnaehe_sunburst(df_packnaehe):
        fig = px.sunburst(
            df_packnaehe, 
            path=['Kunde', '%_Vollpaletten', '%_VollCases', '%_VollPacks'],  # Hierarchie
            values='%_Vollpaletten',  # Werte für die Größe der Kreissegmente
            color='%_Vollpaletten',  # Farbverlauf anhand der Palettenvollständigkeit
            color_continuous_scale="Blues",
            title="Packungsnähe als Sunburst-Diagramm"
        )

        st.plotly_chart(fig, use_container_width=True)

        if st.checkbox("📊 Daten als Tabelle anzeigen (Sunburst)", value=False):
            st.data_editor(df_packnaehe)
    plot_packnaehe_sunburst(df_packnaehe)

def figGesamtKunden(df,tabelle, plot_as_DD_or_W_MM_or_YY):
    dfOriginal = df
    #sort by PlannedDate
    df.sort_values('Deliv. date(From/to)', inplace=False)
    # group by Monat and Name
    # Beispiel: Du hast Spalten 'Transportkosten' und 'Kosten Picking Bayreuth Bayreuth'
    df_kosten_monat = df.groupby([plot_as_DD_or_W_MM_or_YY, 'Name of the ship-to party'], as_index=False)[['Kosten Picking Bayreuth','K&N_Kosten', 'TransportkostenLastMile', 'Paletten', 'Cases', 'Packs','Actual delivery qty']].sum()

    #try:
    fig = px.bar(df_kosten_monat, x=plot_as_DD_or_W_MM_or_YY, y="Actual delivery qty", color="Name of the ship-to party",hover_data=["Actual delivery qty"])
    #except:
    #    st.warning('Der Filter liefert keine Ergebnisse')

    fig.update_xaxes(tickformat='%d.%m.%Y')
    fig.update_xaxes(showticklabels=True)

    fig.update_layout(title_text="Actual delivery qty DE11 nach Kunden", title_font_size=20, title_font_family="Montserrat", title_font_color="#0F2B63", height=700)
    #add sum of Picks Gesamt to text
    agg_data = df.groupby('Deliv. date(From/to)', as_index=False).agg({"Actual delivery qty": lambda x: pd.to_numeric(x, errors="coerce").sum()})
    annotations=[
        {"x": x, "y": total * 1.05, "text": str(total), "showarrow": False}
        for x, total in agg_data.values]
    #add sum of each bar to text
    fig.update_layout(
        annotations=annotations)

    st.plotly_chart(fig, use_container_width=True,config={'displayModeBar': False})       
    ## FARBEN
    if tabelle == True:
        st.data_editor(dfOriginal,key='KundenFIG')


def main(): 
    pd.set_option("display.precision", 0)
    ngp_detail_tabelle, ngp_Delivery_level = loadDF()
    # Konvertiere 'Deliv. date(From/to)' in datetime
    
    min_day = ngp_detail_tabelle['Deliv. date(From/to)'].min().date()
    max_day = ngp_detail_tabelle['Deliv. date(From/to)'].max().date()
    
    col, col2, col3, col4= st.columns([0.2, 0.2, 0.2, 1])
    with col:
        st.subheader('Datenfilter')
        day1 = st.date_input('Startdatum', min_day)
        day2 = st.date_input('Enddatum', max_day)
    with col2:
        # plot Daten in Tag, Wochen Monat oder Jahr 
        plot_as_DD_or_W_MM_or_YY = st.radio('Ansicht der Daten', ['Tag', 'Kalenderwoche', 'Monat', 'Jahr'])
    with col3:
        sum_or_mean = st.radio('Summe oder Durchschnitt', ['Summe', 'Durchschnitt', 'Median'])
    with col4:
        reset_button = st.button('Reset Filter')
    if reset_button:
        day1 = min_day
        day2 = max_day
        st.rerun()
    
    ngp_detail_tabelle = filtereDaten(ngp_detail_tabelle, day1, day2)
    with st.expander('📊 Detail Daten'):
        st.data_editor(ngp_detail_tabelle)
    plot_data(ngp_detail_tabelle,ngp_Delivery_level, plot_as_DD_or_W_MM_or_YY, sum_or_mean)
    try:
        figGesamtKunden(ngp_detail_tabelle,"No",plot_as_DD_or_W_MM_or_YY)
    except:
        pass

if __name__ == "__main__":
    main()