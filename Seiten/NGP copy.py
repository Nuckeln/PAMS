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


def loadDF(day1=None, day2=None): 
    # Erfasse in Variable Funktionsdauer in Sekunden
    start = time.time()
    
    dfKunden = SQL.read_table('Kunden_mit_Packinfos')
    dfOrderLabels = SQL.read_table('business_depotDEBYKN-LabelPrintOrders',day1=day1- pd.Timedelta(days=5),day2=day2,date_column='CreatedTimestamp')
    
    df = SQL.read_table('business_depotDEBYKN-DepotDEBYKNOrders', ['SapOrderNumber', 'PlannedDate','Status',
                                                                   'UnloadingListIdentifier','ActualNumberOfPallets',
                                                                   'DeliveryDepot','EstimatedNumberOfPallets','PartnerNo','CreatedTimestamp','AllSSCCLabelsPrinted',
                                                                   'QuantityCheckTimestamp','UpdatedTimestamp','LoadingLaneId', 'IsReturnDelivery','IsDeleted'],
                        day1, day2, 'PlannedDate')
    # Filter nach IsDeleted == 0 and IsReturnDelivery == 0
    df = df[(df['IsDeleted'] == 0) & (df['IsReturnDelivery'] == 0)]
    
    SapOrderNumberList = df['SapOrderNumber'].tolist()
    ##------------------ Order Items von DB Laden ------------------##
    df2 = SQL.load_table_by_Col_Content('business_depotDEBYKN-DepotDEBYKNOrderItems','SapOrderNumber',SapOrderNumberList)    
    
    #df2 = SQL.read_table('business_depotDEBYKN-DepotDEBYKNOrderItems', ['SapOrderNumber','CorrespondingMastercases', 'CorrespondingOuters', 'CorrespondingPallets'])

    # Tabellen geladen 
    ende = time.time()
    # kürze auf 2 Nachkommastellen
    
    dauerSQL = ende - start
    dauerSQL = round(dauerSQL, 2)
    
    dfOrders = pd.merge(df, df2, on='SapOrderNumber', how='inner')


    # Fehlende Daten Berechnen
    dfOrders['Picks Gesamt'] = dfOrders['CorrespondingMastercases'] + dfOrders['CorrespondingOuters'] + dfOrders['CorrespondingPallets']

    # 1) Gruppieren nach SapOrderNumber, Min und Max der CreatedTimestamp bestimmen
    dfOrderLabelsAgg = dfOrderLabels.groupby('SapOrderNumber')['CreatedTimestamp'].agg(['min','max']).reset_index()
    dfOrderLabelsAgg.rename(columns={'min':'First_Picking','max':'Fertiggestellt'}, inplace=True)

    # 2) Mit dfOrders mergen
    dfOrders = dfOrders.merge(dfOrderLabelsAgg, on='SapOrderNumber', how='left')

    # Rename columns
    dfOrders['Gepackte Paletten'] = dfOrders.ActualNumberOfPallets
    dfOrders['Fertige Paletten'] = dfOrders.ActualNumberOfPallets
    dfOrders['Geschätzte Paletten'] = dfOrders.EstimatedNumberOfPallets
    dfOrders.rename(columns={'CorrespondingMastercases': 'Picks Karton', 'CorrespondingOuters': 'Picks Stangen', 'CorrespondingPallets': 'Picks Paletten'}, inplace=True)
    dfOrders['Lieferschein erhalten'] = dfOrders['CreatedTimestamp']
    
    # Add Costumer Name
    dfKunden['PartnerNo'] = dfKunden['PartnerNo'].astype(str)
    dfKunden = dfKunden.drop_duplicates(subset='PartnerNo', keep='first')
    dfOrders = pd.merge(dfOrders, dfKunden[['PartnerNo', 'PartnerName']], on='PartnerNo', how='left')
    dfOr = dfOrders
    
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
    # Group df by SapOrderNumber
    #dfOr = dfOr.groupby(['SapOrderNumber','PartnerName','AllSSCCLabelsPrinted','DeliveryDepot','Fertiggestellt','Lieferschein erhalten','Fertige Paletten','EstimatedNumberOfPallets']).agg({'Picks Gesamt':'sum'}).reset_index()
    # Change Fertiggestellt to local time Berlin
    #dfOr['Fertiggestellt'] = dfOr['Fertiggestellt'].dt.tz_localize('UTC').dt.tz_convert('Europe/Berlin')
    # Tabellen geladen 
    ende = time.time()
    # kürze auf 2 Nachkommastellen
    
    dauerSQL = ende - start
    dauerSQL = round(dauerSQL, 2)
    return dfOr, dauerSQL
import plotly.express as px
import streamlit as st

def plot_data(df):
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

    df_kosten_monat = df.groupby(
        ['Monat', 'Name of the ship-to party', 'Name'], as_index=False
    )[['Kosten Picking Bayreuth', 'K&N_Kosten', 'TransportkostenLastMile', 
       'Paletten', 'Cases', 'Packs', 'Actual delivery qty','Anzahl_Einheiten']].sum()

    # Kosten Picking Bayreuth
    df_kosten_monat_plot = df_kosten_monat.groupby('Monat', as_index=False)['Kosten Picking Bayreuth'].sum()
    fig1 = px.bar(df_kosten_monat_plot, x='Monat', y='Kosten Picking Bayreuth', 
                  title='Kosten Picking Bayreuth pro Monat', text_auto=True)
    fig1.update_traces(marker_color='#0e2b63')

    # Kosten K&N
    df_kosten_monat_plot_KN = df_kosten_monat.groupby('Monat', as_index=False)['K&N_Kosten'].sum()
    fig2 = px.bar(df_kosten_monat_plot_KN, x='Monat', y='K&N_Kosten', 
                  title='Kosten Picking K&N pro Monat', text_auto=True)
    fig2.update_traces(marker_color='#0e2b63')

    # Transportkosten Last Mile
    df_kosten_monat_trans_plot = df_kosten_monat.groupby('Monat', as_index=False)['TransportkostenLastMile'].sum()
    fig3 = px.bar(df_kosten_monat_trans_plot, x='Monat', y='TransportkostenLastMile', 
                  title='Transportkosten pro Monat Last Mile', text_auto=True)
    fig3.update_traces(marker_color='#0e2b63')
    # Anzahl Einheiten
    df_kosten_monat_anzahl_plot = df_kosten_monat.groupby('Monat', as_index=False)['Anzahl_Einheiten'].sum()
    fig4 = px.bar(df_kosten_monat_anzahl_plot, x='Monat', y='Anzahl_Einheiten', 
                  title='Anzahl Einheiten pro Monat', text_auto=True)
    fig4.update_traces(marker_color='#0e2b63')
    # Streamlit Darstellung
    col1, col2 = st.columns(2)

    with col1:
        st.plotly_chart(fig1)
        if st.checkbox('📊 Daten anzeigen: Picking Bayreuth', value=False, key='data_picking'):
            st.dataframe(df_kosten_monat_plot)

        st.plotly_chart(fig3)
        if st.checkbox('📊 Daten anzeigen: Transportkosten Last Mile', value=False, key='data_transport'):
            st.dataframe(df_kosten_monat_trans_plot)

    with col2:
        st.plotly_chart(fig2)
        if st.checkbox('📊 Daten anzeigen: Kosten K&N', value=False, key='data_kn'):
            st.dataframe(df_kosten_monat_plot_KN)

        st.plotly_chart(fig4)
        if st.checkbox('📊 Daten anzeigen: Anzahl Einheiten', value=False, key='data_qty'):
            st.dataframe(df_kosten_monat_anzahl_plot)

def plot_data2(df):
 # Actual delivery qty
    df_kosten_monat = df.groupby(
        ['Monat', 'Name of the ship-to party', 'Name'], as_index=False
    )[['Kosten Picking Bayreuth', 'K&N_Kosten', 'TransportkostenLastMile', 
       'Paletten', 'Cases', 'Packs', 'Actual delivery qty']].sum()

    # Kosten Picking Bayreuth
    df_kosten_monat_plot = df_kosten_monat.groupby('Monat', as_index=False)['Actual delivery qty'].sum()
    fig1 = px.bar(df_kosten_monat_plot, x='Monat', y='Actual delivery qty', 
                  title='Actual delivery qty pro Monat', text_auto=True)
    fig1.update_traces(marker_color='#0e2b63')
    st.plotly_chart(fig1) 
 
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


def figGesamtKunden(df,tabelle=True,):
    dfOriginal = df
    #sort by PlannedDate
    df.sort_values('Deliv. date(From/to)', inplace=False)
    # group by Monat and Name
    # Beispiel: Du hast Spalten 'Transportkosten' und 'Kosten Picking Bayreuth Bayreuth'
    df_kosten_monat = df.groupby(['Monat', 'Name of the ship-to party'], as_index=False)[['Kosten Picking Bayreuth','K&N_Kosten', 'TransportkostenLastMile', 'Paletten', 'Cases', 'Packs','Actual delivery qty']].sum()

    #try:
    fig = px.bar(df_kosten_monat, x='Monat', y="Actual delivery qty", color="Name of the ship-to party",hover_data=["Actual delivery qty"])
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
    df = pd.read_csv('/Library/Python_local/Synapse/NGP Projekt/Berechnete_NGP_Daten.csv')
    st.data_editor(df)
    plot_data(df)
    plot_data2(df)
    
