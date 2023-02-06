import streamlit as st
import pandas as pd
import numpy as np
import datetime
import st_aggrid as ag
#parquet
import pyarrow.parquet as pq
import time

#from Data_Class.SQL import sql_datenLadenLabel,sql_datenLadenOderItems,sql_datenLadenStammdaten,sql_datenLadenOder

from Data_Class.wetter.api import getWetterBayreuth
from Data_Class.SQL import SQL_TabellenLadenBearbeiten
import plotly_express as px
import plotly.graph_objects as go
import Data_Class.DB_Daten_Agg as DB_Daten



class LIVE:
    
    heute  = datetime.date.today()
    morgen =heute + datetime.timedelta(days=3)
    vorgestern = heute - datetime.timedelta(days=3)

    def timer():
        st.markdown("5-Minute Timer")
        time_left = st.empty()
        start_time = time.time()
        time_left.text("5:00")

        while time.time() - start_time <= 300:  # 300 seconds is 5 minutes
            time_left.text("{:02d}:{:02d}".format(*divmod(int(time.time() - start_time), 60)))
            time.sleep(1)

        time_left.text("Time's up!")

    def loadDF(day1=None, day2=None): 
        dfOr = SQL_TabellenLadenBearbeiten.sql_datenTabelleLaden('prod_Kundenbestellungen')


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
        return dfOr

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

    ## Filter für Live AllSSCCLabelsPrinted Func ###
    def FilterNachDatum(day1, day2,df):
        #df['PlannedDate'] = df['PlannedDate'].dt.strftime('%m/%d/%y')
        df['PlannedDate'] = df['PlannedDate'].astype('datetime64[ns]').dt.date
        #filter nach Datum
        df = df[(df['PlannedDate'] >= day1) & (df['PlannedDate'] <= day2)]
        #mask = (df['PlannedDate'] >= day1) & (df['PlannedDate'] <= day2)         
        #df = df.loc[mask]
        return df
     
    def columnsKennzahlen(df):
        col1, col2, col3 = st.columns(3)
        with col1:
            #---GesamtPicks---#
            st.subheader("Gesamt")
            pickges = df['Picks Gesamt'].sum()
            pickges = int(pickges)
            st.write(f"Gesamt Picks:  {pickges}")
            #---PicksSTR---#
            picksSTR = df.loc[df['DeliveryDepot']=='KNSTR']
            picksSTR = picksSTR['Picks Gesamt'].sum()
            picksSTR = int(picksSTR)
            st.write(f"Gesamt Stuttgart:  {picksSTR}")
            #---PicksLEJ---#
            picksLEJ = df.loc[df['DeliveryDepot']=='KNLEJ']
            picksLEJ = picksLEJ['Picks Gesamt'].sum()
            picksLEJ = int(picksLEJ)
            st.write(f"Gesamt Leipzig:  {picksLEJ}")
            #---Lieferscheine---#            
            lieferscheine = df['SapOrderNumber'].nunique()
            st.write(f"Gesamt Lieferscheine:  {lieferscheine}")
        with col2:
            st.subheader("Offen")
            df1 = df[df['AllSSCCLabelsPrinted']==0]
            st.write(f"Offene Picks: {df1['Picks Gesamt'].sum()}")
            st.write(f'Offen Leipzig: {df1.loc[df1["DeliveryDepot"] == "KNLEJ"]["Picks Gesamt"].sum()}')
            st.write(f'Offen Stuttgart: {df1.loc[df1["DeliveryDepot"] == "KNSTR"]["Picks Gesamt"].sum()}')
            st.write(f"Offene Lieferscheine: {df1['SapOrderNumber'].nunique()}")

        with col3:
            st.subheader("Fertig")
            df2 = df[df['AllSSCCLabelsPrinted']==1]
            st.write(f"Fertige Picks: {df2['Picks Gesamt'].sum()}")
            st.write(f'Fertig Leipzig: {df2.loc[df2["DeliveryDepot"] == "KNLEJ"]["Picks Gesamt"].sum()}')
            st.write(f'Fertig Stuttgart: {df2.loc[df2["DeliveryDepot"] == "KNSTR"]["Picks Gesamt"].sum()}')
            st.write(f"Fertige Lieferscheine: {df2['SapOrderNumber'].nunique()}")

    ## Plotly Flexibles Bar Chart ###
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
   
    ## Plotly Charts ###
    def figPickStatusNachDepot(df):
        df = df.groupby(['DeliveryDepot','AllSSCCLabelsPrinted']).agg({'Picks Gesamt':'sum'}).reset_index()
        df['AllSSCCLabelsPrinted'] = df['AllSSCCLabelsPrinted'].replace({0:'Offen',1:'Fertig'})
        fig = px.bar(df, x="DeliveryDepot", y="Picks Gesamt", color="AllSSCCLabelsPrinted", barmode="group")
        fig.update_layout(
            title="Picks Status nach Depot",
            xaxis_title="Depot",
            yaxis_title="Picks Gesamt",
            font=dict(
                family="Montserrat, sans-serif",
                size=18,
                color="#7f7f7f"),
            showlegend=True)
        fig.update_traces(hovertemplate='Depot: %{x}<br>Picks Gesamt: %{y:.2f}')
        fig.update_layout(uniformtext_minsize=10, uniformtext_mode='hide')
        fig.update_layout(font_family="Montserrat",font_color="#0F2B63",title_font_family="Montserrat",title_font_color="#0F2B63")
        st.plotly_chart(fig, use_container_width=True)

    def figPicksKunde(df):


        df = df.groupby(['PartnerName','SapOrderNumber',"AllSSCCLabelsPrinted",'DeliveryDepot','Fertiggestellt']).agg({'Picks Gesamt':'sum'}).reset_index()
        depoth = st.multiselect('Depot', ['KNSTR','KNLEJ'],['KNSTR','KNLEJ'])
        df = df[df['DeliveryDepot'].isin(depoth)]
        #sort by picks and second by 
        df = df.sort_values(by=['Picks Gesamt','AllSSCCLabelsPrinted'], ascending=False)
        figTagKunden = px.bar(df, x="PartnerName", y="Picks Gesamt",  title="Kundenverteilung",hover_data=['Picks Gesamt','SapOrderNumber','Fertiggestellt'],color='Picks Gesamt',height=900)
        figTagKunden.update_traces(marker_color=np.where(df['AllSSCCLabelsPrinted'] == 1, '#4FAF46', '#E72482'))
        figTagKunden.update_traces(texttemplate='%{text:.3}', text=df['Picks Gesamt'],textposition='inside')
        figTagKunden.update_layout(uniformtext_minsize=10, uniformtext_mode='hide',showlegend=False)
        figTagKunden.update_layout(title_text='')
        figTagKunden.update_xaxes(title_text='')
        figTagKunden.update_yaxes(title_text='')
        figTagKunden.layout.xaxis.tickangle = 70
        figTagKunden.update_layout(font_family="Montserrat",font_color="#0F2B63",title_font_family="Montserrat",title_font_color="#0F2B63")
        
        figTagKunden.update_layout(
                    annotations=[
                        {"x": x, "y": total * 1.05, "text": str(total), "showarrow": False}
                        for x, total in df.groupby("PartnerName", as_index=False).agg({"Picks Gesamt": "sum"}).values])
             

        st.plotly_chart(figTagKunden,use_container_width=True)      

    def figPicksBy_SAP_Order_CS_PAL(df):
        sel = st.multiselect('Depot  ', ['KNSTR','KNLEJ'],['KNSTR','KNLEJ'])
        df = df[df['DeliveryDepot'].isin(sel)]
        df= df.groupby(['SapOrderNumber','PartnerName','AllSSCCLabelsPrinted'])['Picks Karton','Picks Paletten','Picks Stangen'].sum().reset_index()
        #sort by Picks CS+ PAL + OUT 
        df['Picks Gesamt'] = df['Picks Karton'] + df['Picks Paletten'] + df['Picks Stangen']
        df = df.sort_values(by=['Picks Gesamt'], ascending=False)
        figPicksBySAPOrder = px.bar(df, x="SapOrderNumber", y=['Picks Karton','Picks Paletten','Picks Stangen'], title="Picks SAP Order in CS/PAL/OUT",hover_data=['Picks Gesamt','PartnerName',],height=600)
        # change color Picks Karton = #0F2B63 Picks Paletten = #4FAF46 Picks Stangen = #E72482
        figPicksBySAPOrder.update_traces(marker_color='#0F2B63', selector=dict(name='Picks Karton'))
        figPicksBySAPOrder.update_traces(marker_color='#4FAF46', selector=dict(name='Picks Paletten'))
        figPicksBySAPOrder.update_traces(marker_color='#E72482', selector=dict(name='Picks Stangen'))
        figPicksBySAPOrder.update_layout(showlegend=False)
        figPicksBySAPOrder.update_layout(title_text='')
        figPicksBySAPOrder.update_xaxes(title_text='')
        figPicksBySAPOrder.update_yaxes(title_text='')
        figPicksBySAPOrder.layout.xaxis.tickangle = 70
        df['Transparency'] = np.where(df['AllSSCCLabelsPrinted']==True, 0.3, 1)
        figPicksBySAPOrder.update_traces(marker=dict(opacity=df['Transparency']))
        figPicksBySAPOrder.update_layout(font_family="Montserrat",font_color="#0F2B63",title_font_family="Montserrat",title_font_color="#0F2B63")
        figPicksBySAPOrder.update_traces(text=df['Picks Karton'], selector=dict(name='Picks Karton'),textposition='inside')
        figPicksBySAPOrder.update_traces(text=df['Picks Paletten'], selector=dict(name='Picks Paletten'),textposition='inside')
        figPicksBySAPOrder.update_traces(text=df['Picks Stangen'], selector=dict(name='Picks Stangen'),textposition='inside')

        st.plotly_chart(figPicksBySAPOrder,use_container_width=True)

    def figTachoDiagrammPicksLei(df):
        #TODO: Skaliert nicht auf dem Ipad sieht extrem klein aus
        
        df1 = df[df['AllSSCCLabelsPrinted']==0]
        offenLei = df1.loc[df1["DeliveryDepot"] == "KNLEJ"]["Picks Gesamt"].sum()
        offenStu = df1.loc[df1["DeliveryDepot"] == "KNSTR"]["Picks Gesamt"].sum()

        df2 = df[df['AllSSCCLabelsPrinted']==1]
        fertigLei = df2.loc[df2["DeliveryDepot"] == "KNLEJ"]["Picks Gesamt"].sum()
        fertigStu = df2.loc[df2["DeliveryDepot"] == "KNSTR"]["Picks Gesamt"].sum()

        data = {'Offen': [offenLei, offenStu],
                'Fertig': [fertigLei, fertigStu]}
        df = pd.DataFrame(data, index=['Leipzig', 'Stuttgart'])

        # Berechnen Sie den Prozentsatz der abgeschlossenen Lieferungen
        completion_rate = (fertigLei / (fertigLei + offenLei)) * 100

        fig = go.Figure(go.Indicator(
            domain = {'x': [0, 1], 'y': [0, 1]},
            value = completion_rate,
            mode = "gauge+number+delta",
            title = {'text': "Leipzig Ziel (%)"},
            delta = {'reference': 100,'increasing': {'color': "#4FAF46"}},
            gauge = {'axis': {'range': [0, 100], 'tickangle': -90},
                    'steps' : [
                        {'range': [0, 100], 'color': "#0F2B63"},
                        ],

                    'threshold' : {'line': {'color': "#E72482", 'width': 4}, 'thickness': 0.75, 'value': 100}}))
        #update fig to high 600
        fig.update_traces(number_suffix=" %")
        # add suffix to delta = {'reference': 100,'increasing': {'color': "#4FAF46"}},
        fig.update_traces(delta_suffix=" %")
        fig.update_layout(font_family="Montserrat",font_color="#0F2B63",title_font_family="Montserrat",title_font_color="#0F2B63")
        fig.update_layout(uniformtext_minsize=10, uniformtext_mode='hide',showlegend=False)
        fig.update_layout(title_text='')
        fig.update_xaxes(title_text='')
        fig.update_yaxes(title_text='')
        fig.layout.xaxis.tickangle = 70
        st.plotly_chart(fig,use_container_width=True,use_container_height=True,sharing='streamlit')

    def figTachoDiagrammPicksStr(df):
            

            df1 = df[df['AllSSCCLabelsPrinted']==0]
            offenLei = df1.loc[df1["DeliveryDepot"] == "KNLEJ"]["Picks Gesamt"].sum()
            offenStu = df1.loc[df1["DeliveryDepot"] == "KNSTR"]["Picks Gesamt"].sum()
    
            df2 = df[df['AllSSCCLabelsPrinted']==1]
            fertigLei = df2.loc[df2["DeliveryDepot"] == "KNLEJ"]["Picks Gesamt"].sum()
            fertigStu = df2.loc[df2["DeliveryDepot"] == "KNSTR"]["Picks Gesamt"].sum()
    
            data = {'Offen': [offenLei, offenStu],
                    'Fertig': [fertigLei, fertigStu]}
            df = pd.DataFrame(data, index=['Leipzig', 'Stuttgart'])
    
            # Berechnen Sie den Prozentsatz der abgeschlossenen Lieferungen
            completion_rate = (fertigStu / (fertigStu + offenStu)) * 100
    
            fig = go.Figure(go.Indicator(
                domain = {'x': [0, 1], 'y': [0, 1]},
                value = completion_rate,
                mode = "gauge+number+delta",
                title = {'text': "Stuttgart Ziel (%)"},
                delta = {'reference': 100,'increasing': {'color': "#4FAF46"}},
                gauge = {'axis': {'range': [0, 100], 'tickangle': -90},
                        'steps' : [
                            {'range': [0, 100], 'color': "#0F2B63"},
                            ],
    
                        'threshold' : {'line': {'color': "#E72482", 'width': 4}, 'thickness': 0.75, 'value': 100}}))
            fig.update_traces(number_suffix=" %")
            # add suffix to delta = {'reference': 100,'increasing': {'color': "#4FAF46"}},
            fig.update_traces(delta_suffix=" %")
            fig.update_layout(font_family="Montserrat",font_color="#0F2B63",title_font_family="Montserrat",title_font_color="#0F2B63")
            fig.update_layout(uniformtext_minsize=10, uniformtext_mode='hide',showlegend=False)
            fig.update_layout(title_text='')
            fig.update_xaxes(title_text='')
            fig.update_yaxes(title_text='')
            fig.layout.xaxis.tickangle = 70
            #fig.update_layout(height=320)

            st.plotly_chart(fig,use_container_width=True)
    
    def figTachoDiagrammMitarbeiterstunden(sel_date):
        früh = 8
        spät = 6
        # früschicht von Uhrzeit bis Uhrzeit 
        frühSchicht = ['06:00:00', '14:00:00']
        # spätschicht von Uhrzeit bis Uhrzeit
        spätSchicht = ['14:00:00', '22:00:00']
        verfügbar = 0

        # Berechnen der noch verfügbaren Mitarbeiterstunden
        istTag =  datetime.datetime.now().date()
        istZeit = datetime.datetime.now().time()

        if istTag < sel_date:
            verfügbar = früh * 7.5
        if istTag == sel_date:
            if istZeit > datetime.time(6,0,0) and istZeit < datetime.time(14,0,0):
                verfügbar = früh * 7.5
            if istZeit > datetime.time(14,0,0) and istZeit < datetime.time(22,0,0):
                verfügbar = früh * 7.5 + spät * 7.5
            if istZeit > datetime.time(22,0,0) and istZeit < datetime.time(23,59,59):
                verfügbar = spät * 7.5
        if istTag > sel_date:
            verfügbar = 0
        # Berechnen Sie den Prozentsatz der noch verfügbaren stunden  von den Gesamtstunden
        completion_rate = (verfügbar / 150) * 100
        

        fig = go.Figure(go.Indicator(
            domain = {'x': [0, 1], 'y': [0, 1]},
            value = completion_rate,
            mode = "gauge+number+delta",
            title = {'text': "Verfügbare Mitarbeiterstunden in H"},
                            delta = {'reference': 100,'increasing': {'color': "#4FAF46"}},
            gauge = {'axis': {'range': [0, (früh+spät * 7.5)], 'tickangle': -90},
                    'steps' : [
                        {'range': [0, 100], 'color': "#0F2B63"},
                        ],
    
                    'threshold' : {'line': {'color': "#E72482", 'width': 4}, 'thickness': 0.75, 'value': verfügbar}}))
        fig.update_traces(number_suffix=" h")
        # add suffix to delta = {'reference': 100,'increasing': {'color': "#4FAF46"}},
        fig.update_traces(delta_suffix=" h")
        fig.update_layout(font_family="Montserrat",font_color="#0F2B63",title_font_family="Montserrat",title_font_color="#0F2B63")
        fig.update_layout(uniformtext_minsize=10, uniformtext_mode='hide',showlegend=False)
        fig.update_layout(title_text='')
        fig.update_xaxes(title_text='')
        fig.update_yaxes(title_text='')
        fig.layout.xaxis.tickangle = 70
        fig.update_layout(height=280)

        st.plotly_chart(fig,use_container_width=True)
        return completion_rate

    def figUebermitteltInDeadline(df):
       # Kannst du mir ein Plotly chart geben welches eine Zeitachse hat und darauf die Lieferschiene ausgibt und anzeigt ob inTime oder nicht 
        
        col1, col2 = st.columns(2)
        with col1:
            sel_deadStr = st.text_input('Deadline Lej', '14:00:00')
        with col2:
            sel_deadLej = st.text_input('Deadline Str', '14:00:00')
        #add deadlines to df by DeliveryDepot
        df['Deadline'] = np.where(df['DeliveryDepot'] == 'KNLEJ', sel_deadStr, sel_deadLej)
        df['PlannedDate'] = df['PlannedDate'] + pd.to_timedelta(df['Deadline'])
        #convert to datetime
        df['PlannedDate'] = pd.to_datetime(df['PlannedDate'])
        # filter by fertiggestellt = '0'
        dfOffen = df[df['Fertiggestellt'] == '0']
        dfFertig = df[df['Fertiggestellt'] != '0']
        dfFertig.Fertiggestellt = pd.to_datetime(dfFertig.Fertiggestellt)
        #chek if is inTime
        dfFertig['InTime'] = (dfFertig['Fertiggestellt'] < dfFertig['PlannedDate']).astype(int)
        dfFertig['Fertig um'] = dfFertig['Fertiggestellt']
        dfFertig['Fertig um'] = dfFertig['Fertig um'].dt.strftime('%d.%m.%Y %H:%M')
        #round to hour
        dfFertig['Fertiggestellt'] = dfFertig['Fertiggestellt'].dt.round('H')
        #change format to day as text and hour
        dfFertig['Fertiggestellt'] = dfFertig['Fertiggestellt'].dt.strftime('%d.%m.%Y %H:%M')
        #group by
        dfFertig = dfFertig.groupby(['PlannedDate','PartnerName','Fertiggestellt','SapOrderNumber','DeliveryDepot','InTime','Fertig um']).agg({'Picks Gesamt':'sum'}).reset_index()
        #sort by Fertiggestellt
        dfFertig = dfFertig.sort_values(by=['Fertiggestellt'], ascending=True)
        #Create Plotly Chart
        fig = px.bar(dfFertig, x='Fertiggestellt', y="Picks Gesamt", color="InTime", hover_data=['PartnerName','Fertig um','SapOrderNumber','DeliveryDepot'],height=600)
        #if in Time 1 set to green else to red
        fig.update_traces(marker_color=['#4FAF46' if x == 1 else '#E72482' for x in dfFertig['InTime']])
        fig.data[0].text = dfFertig['PartnerName'] + '<br>' + dfFertig['Picks Gesamt'].astype(str)
        fig.layout.xaxis.type = 'category'
        # x aaxis text horizontal
        fig.layout.xaxis.tickangle = 70
        # remove xaxis and yaxis title
        fig.update_xaxes(title_text='')
        fig.update_yaxes(title_text='')
        fig.update_layout(font_family="Montserrat",font_color="#0F2B63",title_font_family="Montserrat",title_font_color="#0F2B63")
        fig.update_layout(legend_title_text='InTime')
         
        # Date PartnerName to text
        st.plotly_chart(fig, use_container_width=True)

   ## AG-Grid Func ###

    def tabelleAnzeigen(df):
        #new df with only the columns we need 'PlannedDate' ,'SapOrderNumber','PartnerName']#'Fertiggestellt','Picks Gesamt','Picks Karton','Picks Paletten','Picks Stangen','Lieferschein erhalten','Fertiggestellt'
        dfAG = df[['PlannedDate','DeliveryDepot' ,'SapOrderNumber','PartnerName','Fertiggestellt','Fertige Paletten','Picks Gesamt','Lieferschein erhalten']]


        ag.AgGrid(dfAG)
    
    def downLoadTagesReport(df):
    
        
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

    def PageTagesReport():

        pd.set_option("display.precision", 2)
        #rerun script all 2 minutes

        colhead1, colhead2 ,colhead3, = st.columns(3)
        with colhead1:
            sel_date = st.date_input('Datum', LIVE.heute)
            dfOr = LIVE.loadDF(sel_date,sel_date)
            sel_reload = st.button('Reload')
        with colhead2:
            dfUpdatetime = SQL_TabellenLadenBearbeiten.sql_datenTabelleLaden('prod_KundenbestellungenUpdateTime')
            dfUpdatetime = dfUpdatetime.rename(columns={'time':'Last Update'})
            st.dataframe(dfUpdatetime)
            LIVE.downLoadTagesReport(dfOr)
        with colhead3:
            if sel_reload:
                dfUpdate = SQL_TabellenLadenBearbeiten.sql_datenTabelleLaden('prod_Kundenbestellungen')
                DB_Daten.UpdateDaten.updateDaten_byDate(dfUpdate)
                dfOr = LIVE.loadDF(sel_date,sel_date)
                st.success('Daten wurden aktualisiert')
                
            LIVE.wetter()

        LIVE.columnsKennzahlen(dfOr)
        with st.expander('Zielerfüllung', expanded=True):
            try:
                col34, col35 = st.columns(2)
                with col34:
                    LIVE.figTachoDiagrammPicksLei(dfOr)
                with col35:
                    LIVE.figTachoDiagrammPicksStr(dfOr)
            except:
               st.write('Keine Daten vorhanden')

        with st.expander('Kundenübersicht, grün = Fertig, rot = Offen', expanded=True):
            try:
                LIVE.figPicksKunde(dfOr)
            except:
                st.write('Keine Daten vorhanden')
        with st.expander('Lieferscheine nach Volumen in Stangen, Karton, Paletten', expanded=True):
            try:
                LIVE.figPicksBy_SAP_Order_CS_PAL(dfOr) 
            except:
                st.write('Keine Daten vorhanden')
        with st.expander('Deadline eingehalten? Grün = Ja, Rot = Nein', expanded=True):     
            try:    
                LIVE.figUebermitteltInDeadline(dfOr)
            except:
                st.write('Keine Daten vorhanden, schreibweise beachtet?')


        LIVE.tabelleAnzeigen(dfOr)
        



