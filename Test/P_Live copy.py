import streamlit as st
import pandas as pd
import numpy as np
import datetime
import st_aggrid as ag

#from Data_Class.SQL import sql_datenLadenLabel,sql_datenLadenOderItems,sql_datenLadenStammdaten,sql_datenLadenOder
from Data_Class.DB_Daten_Agg import orderDatenAgg
from Data_Class.wetter.api import getWetterBayreuth
from Data_Class.SQL import SQL_TabellenLadenBearbeiten
import plotly_express as px

#from streamlit import caching
#caching.clear_cache()



class LIVE:
    
    heute  = datetime.date.today()
    morgen =heute + datetime.timedelta(days=3)
    vorgestern = heute - datetime.timedelta(days=3)

    def __init__(self,df):
        self.df = df


    def sessionstate():
        if 'key' not in st.session_state:
            st.session_state['key'] = 'value'
        if 'key' not in st.session_state:
            st.session_state.key = +1
    def wetter():
        df = getWetterBayreuth()
        temp = df.loc[0,'Temp']
        temp_max = df.loc[0,'Temp Max']
        temp_min = df.loc[0,'Temp Min']
        humidity = df.loc[0,'Humidity']
        wind_speed = df.loc[0,'Wind Speed']
        wind_degree = df.loc[0,'Wind Degree']
        clouds = df.loc[0,'Clouds']
        weather = df.loc[0,'Weather']
        #temp to int
        temp = int(temp)
        st.write(f"Temperatur: {temp}" + "°C")
        if weather == "Clouds":
            st.write("Wolkig")
        elif weather == "Rain":
            st.write("Regen")
        elif weather == "Clear":
            st.write("Klar")
        elif weather == "Snow":
            st.write("Schnee")
        else:
            st.write("Sonstiges")
    def reload():
        if st.button("Reload"):
            st.experimental_rerun()

def liveStatusPage():

    ## Filter für Live AllSSCCLabelsPrinted Func ###
    def FilterNachDatum(day1, day2,df):
        #df['PlannedDate'] = df['PlannedDate'].dt.strftime('%m/%d/%y')
        df['PlannedDate'] = df['PlannedDate'].astype('datetime64[ns]').dt.date
        #filter nach Datum
        df = df[(df['PlannedDate'] >= day1) & (df['PlannedDate'] <= day2)]
        #mask = (df['PlannedDate'] >= day1) & (df['PlannedDate'] <= day2)         
        #df = df.loc[mask]
        return df

    def FilterNachDatumLabel(day1, day2,df):
        # df['DATUM'] = df['DATUM'].dt.strftime('%m/%d/%y')
        # df['DATUM'] = df['DATUM'].astype('datetime64[ns]').dt.date
        #filter nach Datum
        df = df[(df['DATUM'] >= day1) & (df['DATUM'] <= day2)]


        return df



    ## Page Layout Func ### 
    def headerAndWetter():
        colhead1, colhead2 ,colhead3, = st.columns(3)
        with colhead1:
            st.title("Live Status")
        with colhead2:
            LIVE.reload()
        with colhead3:
            LIVE.wetter()
        

    def columnsKennzahlen(df):
        col1, col2, col3 = st.columns(3)
        with col1:
            #---GesamtPicks---#
            st.subheader("Gesamt Picks Tag")
            pickges = df['Picks Gesamt'].sum()
            pickges = int(pickges)
            st.write(f"Gesamtvolumen:  {pickges}")
            #---PicksSTR---#
            picksSTR = df.loc[df['DeliveryDepot']=='KNSTR']
            picksSTR = picksSTR['Picks Gesamt'].sum()
            picksSTR = int(picksSTR)
            st.write(f"Stuttgart:  {picksSTR}")
            #---PicksLEJ---#
            picksLEJ = df.loc[df['DeliveryDepot']=='KNLEJ']
            picksLEJ = picksLEJ['Picks Gesamt'].sum()
            picksLEJ = int(picksLEJ)
            st.write(f"Leipzig:  {picksLEJ}")
            #---Lieferscheine---#            
            lieferscheine = df['SapOrderNumber'].nunique()
            st.write(f"Lieferscheine:  {lieferscheine}")
        with col2:
            st.subheader("Noch zu Picken")
            #---PicksOffen---#
            pickOffenges = df.loc[df['AllSSCCLabelsPrinted']==0]
            pickOffenges = pickOffenges['Picks Gesamt'].sum()
            pickOffenges = int(pickOffenges)
            st.write(f"Gesamtvolumen:  {pickOffenges}")
            #---PicksOffenSTR---#
            picksoffenSTR = df.loc[(df['AllSSCCLabelsPrinted']==0) & (df['DeliveryDepot']=='KNSTR')]
            picksoffenSTR = picksoffenSTR['Picks Gesamt'].sum()
            picksoffenSTR = int(picksoffenSTR)
            st.write(f"Stuttgart:  {picksoffenSTR}")
            #---PicksOffenLEJ---#
            picksoffenLEJ = df.loc[(df['AllSSCCLabelsPrinted']==0) & (df['DeliveryDepot']=='KNLEJ')]
            picksoffenLEJ = picksoffenLEJ['Picks Gesamt'].sum()
            picksoffenLEJ = int(picksoffenLEJ)
            st.write(f"Leipzig:  {picksoffenLEJ}")
            #---LieferscheineOffen---#
            lieferscheineOffen = df.loc[df['AllSSCCLabelsPrinted']==0]
            lieferscheineOffen = lieferscheineOffen['SapOrderNumber'].nunique()
            st.write(f"Lieferscheine:  {lieferscheineOffen}")
        with col3:
            st.subheader("Fertig")
            #---PicksFertig---#
            pickFertigges = df.loc[df['AllSSCCLabelsPrinted']==1]
            pickFertigges = pickFertigges['Picks Gesamt'].sum()
            pickFertigges = int(pickFertigges)
            st.write(f"Gesamtvolumen:  {pickFertigges}")
            #---PicksFertigSTR---#
            picksFertigSTR = df.loc[(df['AllSSCCLabelsPrinted']==1) & (df['DeliveryDepot']=='KNSTR')]
            picksFertigSTR = picksFertigSTR['Picks Gesamt'].sum()
            picksFertigSTR = int(picksFertigSTR)
            st.write(f"Stuttgart:  {picksFertigSTR}")
            #---PicksFertigLEJ---#
            picksFertigLEJ = df.loc[(df['AllSSCCLabelsPrinted']==1) & (df['DeliveryDepot']=='KNLEJ')]
            picksFertigLEJ = picksFertigLEJ['Picks Gesamt'].sum()
            picksFertigLEJ = int(picksFertigLEJ)
            st.write(f"Leipzig:  {picksFertigLEJ}")
            #---LieferscheineFertig---#
            lieferscheineFertig = df.loc[df['AllSSCCLabelsPrinted']==1]
            lieferscheineFertig = lieferscheineFertig['SapOrderNumber'].nunique()
            st.write(f"Lieferscheine:  {lieferscheineFertig}")

    ## Plotly Func ###
    def userBauDirDiagramm(df):
        userAuswahl = ['Amount of DNs',	'DESADV','Amount of picks',	'Amount of picks for next Day'	,'Volume available for next Day in %' ,'Amount transmissions w/o TPD' ,'Operational activities completed',]
        spaltenName = st.selectbox('Spalte', userAuswahl)
        fig_Bar_Chart(df, spaltenName)     

    def fig_Bar_Chart(df, spaltenName):
        a = df[spaltenName].mean()
        df = df.groupby(['PlannedDate'])[spaltenName].mean().reset_index()
        # add plotly bar chart with a as middelline 
        fig = px.bar(df, x='PlannedDate', y=df[spaltenName], title=spaltenName)
        fig.add_hline(y=a, line_dash="dash", line_color="red")
        # if value of spaltenName is higher than a, color the bar in red
        fig.update_traces(marker_color=np.where(df[spaltenName] > a, 'red', 'green'))
        # add total value of spaltenName to each bar
        fig.update_traces(texttemplate='%{text:.2s}', text=df[spaltenName])
        fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')

        st.plotly_chart(fig, use_container_width=True)
   
    def figPickStatusNachDepot(df):
        df = df.groupby(['DeliveryDepot','AllSSCCLabelsPrinted']).agg({'Picks Gesamt':'sum'}).reset_index()
        df['AllSSCCLabelsPrinted'] = df['AllSSCCLabelsPrinted'].replace({0:'Offen',1:'Fertig'})
        fig = px.bar(df, x="DeliveryDepot", y="Picks Gesamt", color="AllSSCCLabelsPrinted", barmode="group")
        fig.update_layout(
            title="Picks Status nach Depot",
            xaxis_title="Depot",
            yaxis_title="Picks Gesamt",
            
        #     font=dict(
        #         family="Courier New, monospace",
        #         size=18,
        #         color="#7f7f7f"
            )
        fig.update_traces(texttemplate='%{text:.2s}', text=df['Picks Gesamt'])
        fig.update_layout(uniformtext_minsize=10, uniformtext_mode='hide',showlegend=False)

        
        st.plotly_chart(fig, use_container_width=True)        
 
    def figPicksKunde(df):
        df = df.groupby(['PartnerName','SapOrderNumber',"AllSSCCLabelsPrinted"]).agg({'Picks Gesamt':'sum'}).reset_index()
        #sort by picks and second by 
        df = df.sort_values(by=['Picks Gesamt','AllSSCCLabelsPrinted'], ascending=False)
        figTagKunden = px.bar(df, x="PartnerName", y="Picks Gesamt",  title="Kundenverteilung",hover_data=['Picks Gesamt','SapOrderNumber'],color='Picks Gesamt')
        figTagKunden.update_traces(marker_color=np.where(df['AllSSCCLabelsPrinted'] == 1, 'green', 'red'))
        figTagKunden.update_traces(texttemplate='%{text:.2s}', text=df['Picks Gesamt'])
        figTagKunden.update_layout(uniformtext_minsize=10, uniformtext_mode='hide',showlegend=False)
        st.plotly_chart(figTagKunden,use_container_width=True)      

    def figPicksBy_SAP_Order_CS_PAL(df):
        df= df.groupby(['SapOrderNumber','PartnerName'])['Picks CS','Picks PAL','Picks OUT'].sum().reset_index()
        #sort by Picks CS+ PAL + OUT 
        df['Picks Gesamt'] = df['Picks CS'] + df['Picks PAL'] + df['Picks OUT']
        df = df.sort_values(by=['Picks Gesamt'], ascending=False)
        figPicksBySAPOrder = px.bar(df, x="SapOrderNumber", y=['Picks CS','Picks PAL','Picks OUT'], title="Picks SAP Order in CS/PAL/OUT")
        figPicksBySAPOrder.update_layout(showlegend=False)
        st.plotly_chart(figPicksBySAPOrder,use_container_width=True)
    
   ## AG-Grid Func ###

    def ordersOhneLinesMitLabelDaten(df):
        dfLabel = SQL_TabellenLadenBearbeiten.sql_datenLadenDatum(LIVE.vorgestern, LIVE.morgen ,SQL_TabellenLadenBearbeiten.tabelleSSCCLabel,'CreatedTimestamp')       
        df1 = df
            
        df = df.groupby(['PartnerName','SapOrderNumber',"AllSSCCLabelsPrinted",'DeliveryDepot']).agg({'Picks Gesamt':'sum'}).reset_index()
        # add column with CreatedTimestamp from df1 to df by first hit of SapOrderNumber
        df['Lieferschein erhalten'] = df['SapOrderNumber'].apply(lambda x: df1.loc[df1['SapOrderNumber'] == x]['CreatedTimestamp'].iloc[0])
        df['Fertiggestellt'] = df['SapOrderNumber'].apply(lambda x: df1.loc[df1['SapOrderNumber'] == x]['QuantityCheckTimestamp'].iloc[0])
        df['Truck Kennzeichen'] = df['SapOrderNumber'].apply(lambda x: df1.loc[df1['SapOrderNumber'] == x]['UnloadingListIdentifier'].iloc[0])
        # sum for each in df.SapOrderNumber of df1'Picks CS'  with same SapOrderNumber
        df['Picks Karton'] = df['SapOrderNumber'].apply(lambda x: df1.loc[df1['SapOrderNumber'] == x]['Picks CS'].sum())
        df['Picks Paletten'] = df['SapOrderNumber'].apply(lambda x: df1.loc[df1['SapOrderNumber'] == x]['Picks PAL'].sum())
        df['Picks Stangen'] = df['SapOrderNumber'].apply(lambda x: df1.loc[df1['SapOrderNumber'] == x]['Picks OUT'].sum())

        #df PartnerName, SapOrderNumber, AllSSCCLabelsPrinted, Picks Gesamt to str
        df['PartnerName'] = df['PartnerName'].astype(str)
        df['SapOrderNumber'] = df['SapOrderNumber'].astype(str)
        df['AllSSCCLabelsPrinted'] = df['AllSSCCLabelsPrinted'].astype(str)
        #df['Picks Gesamt'] to int
        df['Picks Gesamt'] = df['Picks Gesamt'].astype(int)
        # count for each in df.SapOrderNumber how many D97 entrys are in dfLabel.UnitOfMeasure with same SapOrderNumber
        df['Paletten Label'] = df['SapOrderNumber'].apply(lambda x: dfLabel[dfLabel['UnitOfMeasure'] == 'D97'].loc[dfLabel['SapOrderNumber'] == x].shape[0])
        
        return df

    def downLoadTagesReport(df):
        df = ordersOhneLinesMitLabelDaten(df)

        @st.experimental_memo
        def convert_df(df):
            return df.to_csv(index=False).encode('utf-8')
        csv = convert_df(df)
        # LIVE.heute to string
        tagimfilename= LIVE.heute.strftime("%d.%m.%Y")

        st.download_button(
        "Download Tagesreport als csv",
        csv,
        tagimfilename + "_Tagesreport.csv",
        "text/csv",
        key='download-csv'
            )




    #######------------------Main------------------########
    ##TODO Funktion orderDatenAgg() Datum 
    df = orderDatenAgg()

    headerAndWetter()
    downLoadTagesReport(df)
    seldate= st.date_input('Datum')
    if seldate:
        df = FilterNachDatum(seldate,seldate,df)
        df = df.fillna(0)

    pd.set_option("display.precision", 2)
    columnsKennzahlen(df)

    figPickStatusNachDepot(df)  
    figPicksBy_SAP_Order_CS_PAL(df)
    figPicksKunde(df)
  
    st.write(ordersOhneLinesMitLabelDaten(df))
    st.dataframe(df)


