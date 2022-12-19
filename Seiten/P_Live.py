import streamlit as st
import pandas as pd
import numpy as np
import datetime
import st_aggrid as ag

#from Data_Class.SQL import sql_datenLadenLabel,sql_datenLadenOderItems,sql_datenLadenStammdaten,sql_datenLadenOder
from Data_Class.DB_Daten_Agg import DatenAgregieren as DA
from Data_Class.wetter.api import getWetterBayreuth
from Data_Class.SQL import SQL_TabellenLadenBearbeiten
import plotly_express as px
import plotly.graph_objects as go



#from streamlit import caching
#caching.clear_cache()



class LIVE:
    
    heute  = datetime.date.today()
    morgen =heute + datetime.timedelta(days=3)
    vorgestern = heute - datetime.timedelta(days=3)

    def __init__(self,df):
        self.df = df

    ## Function to reload the page all 2 min 

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
            st.experimental_memo.clear()

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

    ## Plotly Func ###

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
        st.plotly_chart(fig, use_container_width=True)



    def figPicksDepot_open_close_in_CS_OUT_PAL(df):
        depota = st.multiselect('DeliveryDepot', ['KNSTR','KNLEJ'],['KNSTR','KNLEJ'])
        df = df[df['DeliveryDepot'].isin(depota)]


   #function to create a bar chart to visualize the sum of columns df['Picks Karton offen'] df['Picks Paletten offen']  df['Picks Stangen offen'] df['Picks Karton fertig'] df['Picks Paletten fertig'] df['Picks Stangen fertig'] for each depot
        df = df.groupby(['DeliveryDepot']).agg({'Picks Karton offen':'sum','Picks Paletten offen':'sum','Picks Stangen offen':'sum','Picks Karton fertig':'sum','Picks Paletten fertig':'sum','Picks Stangen fertig':'sum'}).reset_index()
        fig = go.Figure(data=[
            go.Bar(name='Picks Karton offen', x=df['DeliveryDepot'], y=df['Picks Karton offen'],constraintext='inside',text='Picks Karton offen',textangle=-90),
            go.Bar(name='Picks Paletten offen', x=df['DeliveryDepot'], y=df['Picks Paletten offen'],constraintext='inside',text='Picks Paletten offen',textangle=-90),
            go.Bar(name='Picks Stangen offen', x=df['DeliveryDepot'], y=df['Picks Stangen offen'], constraintext='inside',text='Picks Stangen offen',textangle=-90),
            go.Bar(name='Picks Karton fertig', x=df['DeliveryDepot'], y=df['Picks Karton fertig'],constraintext='inside',text='Picks Karton fertig',textangle=-90),
            go.Bar(name='Picks Paletten fertig', x=df['DeliveryDepot'], y=df['Picks Paletten fertig'],constraintext='inside',text='Picks Paletten fertig',textangle=-90),
            go.Bar(name='Picks Stangen fertig', x=df['DeliveryDepot'], y=df['Picks Stangen fertig'],constraintext='inside',text='Picks Stangen fertig',textangle=-90)       
        ])

        # update bar color of Picks Stangen offen to #7030A0
        fig.update_traces(marker_color=['#7030A0','#7030A0','#7030A0','#002060','#002060','#002060'],selector=dict(name='Picks Stangen offen'))

        # Change the bar mode
        fig.update_layout(barmode='group')
        fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')


        fig.update_layout(title_text='Depotverteilung')
        st.plotly_chart(fig, use_container_width=True)

    def figPicksKunde(df):


        df = df.groupby(['PartnerName','SapOrderNumber',"AllSSCCLabelsPrinted",'DeliveryDepot','Fertiggestellt']).agg({'Picks Gesamt':'sum'}).reset_index()
        depoth = st.multiselect('Depot', ['KNSTR','KNLEJ'],['KNSTR','KNLEJ'])
        df = df[df['DeliveryDepot'].isin(depoth)]
        #sort by picks and second by 
        df = df.sort_values(by=['Picks Gesamt','AllSSCCLabelsPrinted'], ascending=False)
        figTagKunden = px.bar(df, x="PartnerName", y="Picks Gesamt",  title="Kundenverteilung",hover_data=['Picks Gesamt','SapOrderNumber','Fertiggestellt'],color='Picks Gesamt')
        figTagKunden.update_traces(marker_color=np.where(df['AllSSCCLabelsPrinted'] == 1, '#4FAF46', '#E72482'))
        figTagKunden.update_traces(texttemplate='%{text:.2s}', text=df['Picks Gesamt'])
        figTagKunden.update_layout(uniformtext_minsize=10, uniformtext_mode='hide',showlegend=False)
        st.plotly_chart(figTagKunden,use_container_width=True)      

    def figPicksBy_SAP_Order_CS_PAL(df):
        
        sel = st.multiselect('Depot  ', ['KNSTR','KNLEJ'],['KNSTR','KNLEJ'])
        df = df[df['DeliveryDepot'].isin(sel)]
        df= df.groupby(['SapOrderNumber','PartnerName'])['Picks Karton','Picks Paletten','Picks Stangen'].sum().reset_index()
        #sort by Picks CS+ PAL + OUT 
        df['Picks Gesamt'] = df['Picks Karton'] + df['Picks Paletten'] + df['Picks Stangen']
        df = df.sort_values(by=['Picks Gesamt'], ascending=False)
        figPicksBySAPOrder = px.bar(df, x="SapOrderNumber", y=['Picks Karton','Picks Paletten','Picks Stangen'], title="Picks SAP Order in CS/PAL/OUT")
        figPicksBySAPOrder.update_layout(showlegend=False)
        st.plotly_chart(figPicksBySAPOrder,use_container_width=True)
    def tester(df): 
        col1, col2 = st.columns(2)
        with col1:
            sel_deadStr = st.text_input('Deadline Lej', '14:00:00')
        with col2:
            sel_deadLej = st.text_input('Deadline Str', '16:00:00')
        #add deadlines to df by DeliveryDepot
        df['Deadline'] = np.where(df['DeliveryDepot'] == 'KNLEJ', sel_deadStr, sel_deadLej)
        df['PlannedDate'] = df['PlannedDate'] + pd.to_timedelta(df['Deadline'])
        #convert to datetime
        df['PlannedDate'] = pd.to_datetime(df['PlannedDate'])
        # filter by fertiggestellt = '0'
        dfOffen = df[df['Fertiggestellt'] == '0']
        dfFertig = df[df['Fertiggestellt'] != '0']
        dfFertig.Fertiggestellt = pd.to_datetime(dfFertig.Fertiggestellt)

        dfFertig['InTime'] = (dfFertig['Fertiggestellt'] < dfFertig['PlannedDate']).astype(int)
        #add to df.InTime = 1 if fertiggestellt < planneddate
        dfOffen['InTime'] = (dfOffen['Fertiggestellt'] < dfOffen['PlannedDate']).astype(int)
        #group by DeliveryDepot and count InTime
        dfFertig = dfFertig.groupby(['DeliveryDepot'])['InTime'].sum().reset_index()
        dfOffen = dfOffen.groupby(['DeliveryDepot'])['InTime'].sum().reset_index()
        #merge dfFertig und dfOffen
        df = dfFertig.merge(dfOffen, on='DeliveryDepot')
        #add column InTime
        df['InTime'] = df['InTime_x'] + df['InTime_y']
        #add column Offen
        df['Offen'] = df['Picks Gesamt'] - df['InTime']
        #add column InTime % 
        df['InTime %'] = df['InTime'] / df['Picks Gesamt']
        #add column Offen % 
        df['Offen %'] = df['Offen'] / df['Picks Gesamt']
        #add column Offen % 
        df['Fertig %'] = df['InTime'] / df['Picks Gesamt']
        #remove columns
        df = df.drop(columns=['InTime_x','InTime_y'])
        #rename columns
        df = df.rename(columns={'DeliveryDepot':'Depot','Picks Gesamt':'Picks Gesamt','InTime':'InTime','Offen':'Offen','InTime %':'InTime %','Offen %':'Offen %','Fertig %':'Fertig %'})
        #sort by InTime %
        df = df.sort_values(by=['InTime %'], ascending=False)
        #add columns to df
        df['InTime %'] = df['InTime %'].apply(lambda x: "{:.2%}".format(x))
        df['Offen %'] = df['Offen %'].apply(lambda x: "{:.2%}".format(x))
        df['Fertig %'] = df['Fertig %'].apply(lambda x: "{:.2%}".format(x))
        st.dataframe(df)

#Dieser Code gibt folgenden fehler aus AttributeError: 'Series' object has no attribute 'hour'
    def figUebermitteltInDeadline(df):
       # Kannst du mir ein Plotly chart geben welches eine Zeitachse hat und darauf die Lieferschiene ausgibt und anzeigt ob inTime oder nicht 

        col1, col2 = st.columns(2)
        with col1:
            sel_deadStr = st.text_input('Deadline Lej', '14:00:00')
        with col2:
            sel_deadLej = st.text_input('Deadline Str', '16:00:00')
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
        #round to hour
        dfFertig['Fertiggestellt'] = dfFertig['Fertiggestellt'].dt.round('H')
        #group by 'df = df.groupby(['PartnerName','Fertiggestellt',SapOrderNumber',"InTime",'DeliveryDepot']).agg({'Picks Gesamt':'sum'}).reset_index()
        dfFertig = dfFertig.groupby(['PlannedDate','PartnerName','Fertiggestellt','SapOrderNumber','DeliveryDepot','InTime']).agg({'Picks Gesamt':'sum'}).reset_index()
        #Create Plotly Chart
        fig = px.bar(dfFertig, x="Fertiggestellt", y="Picks Gesamt", color="InTime", hover_data=['PartnerName','SapOrderNumber','DeliveryDepot'])
        #if in Time 1 set to green else to red
        fig.update_traces(marker_color=['#4FAF46' if x == 1 else '#E72482' for x in dfFertig['InTime']])
        fig.data[0].text = dfFertig['PartnerName'] + '<br>' + dfFertig['Picks Gesamt'].astype(str)
        # Date PartnerName to text
        st.plotly_chart(fig, use_container_width=True,height=800)


    def new_figUebermitteltInDeadline(df):
       # Kannst du mir ein Plotly chart geben welches eine Zeitachse hat und darauf die Lieferschiene ausgibt und anzeigt ob inTime oder nicht 

            col1, col2 = st.columns(2)
            with col1:
                sel_deadStr = st.text_input('Deadline Lej', '14:00:00')
            with col2:
                sel_deadLej = st.text_input('Deadline Str', '16:00:00')
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
            #group by 'df = df.groupby(['PartnerName','Fertiggestellt',SapOrderNumber',"InTime",'DeliveryDepot']).agg({'Picks Gesamt':'sum'}).reset_index()
            dfFertig = dfFertig.groupby(['PlannedDate','PartnerName','Fertiggestellt','SapOrderNumber','DeliveryDepot','InTime']).agg({'Picks Gesamt':'sum'}).reset_index()
    # create a column with the deadline status
            dfFertig['Deadline Status'] = np.where(dfFertig['Fertiggestellt'] <= dfFertig['PlannedDate'], 'On Time', 'Late')

            # create the data for the chart
            data = [
                go.Bar(
                    x = dfFertig['PlannedDate'],
                    y = dfFertig['Picks Gesamt'],
                    text = dfFertig['Deadline Status'],
                    marker = dict(
                        color = np.where(dfFertig['Deadline Status'] == 'On Time', 'green', 'red')
                    )
                )
            ]

            # create the layout for the chart
            layout = go.Layout(
                xaxis = dict(title = 'Planned Date'),
                yaxis = dict(title = 'Picks Gesamt'),
                title = 'Delivery Chain'
            )

            # create the figure and plot the chart
            fig = go.Figure(data = data, layout = layout)
            st.plotly_chart(fig)
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
    ##TODO Funktion orderDatenAgg() Datum 
        #st.markdown('<meta http-equiv="refresh" content="120">', unsafe_allow_html=True)
        @st.experimental_memo
        def loadDF(day1=LIVE.heute, day2=LIVE.heute):
            dfOr = DA.orderDatenGo(day1=day1, day2=day2)
            dfOr = dfOr.reset_index(drop=True)
            return dfOr

        
        pd.set_option("display.precision", 2)
        
        st.header('Tagesreport')
        colhead1, colhead2 ,colhead3, = st.columns(3)
        with colhead1:
            sel_date = st.date_input('Datum', LIVE.heute)
            day1 = sel_date
            day2 = sel_date
            dfOr = loadDF(sel_date,sel_date)
        with colhead2:
            LIVE.reload()
            LIVE.downLoadTagesReport(dfOr)
        with colhead3:
            LIVE.wetter()

        

        LIVE.columnsKennzahlen(dfOr)
        #LIVE.new_figUebermitteltInDeadline(dfOr)
        LIVE.figPicksKunde(dfOr)
        LIVE.figPicksBy_SAP_Order_CS_PAL(dfOr)      
        LIVE.figUebermitteltInDeadline(dfOr)
        #LIVE.figPickStatusNachDepot(dfOr)
        #LIVE.figPicksDepot_open_close_in_CS_OUT_PAL(dfOr)


        
        
        LIVE.tabelleAnzeigen(dfOr)
        


