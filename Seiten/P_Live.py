import streamlit as st
import pandas as pd
import numpy as np
import datetime
import streamlit_autorefresh as sar
from PIL import Image
import plotly_express as px
import plotly.graph_objects as go
from annotated_text import annotated_text, annotation
import streamlit_timeline as timeline

from Data_Class.wetter.api import getWetterBayreuth
from Data_Class.MMSQL_connection import read_Table


class LIVE:
    #@st.cache_data
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

        return dfOr

    def wetter():
        try:
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
            st.write("Wetter in Bayreuth:")
            if weather == "Clouds":
                st.write("Bewölkt " + f"{ temp}" + "°C")
            elif weather == "Rain":
                st.write("Regen " + f"{ temp}" + "°C")
            elif weather == "Clear":
                st.write("Klar  " + f"{ temp}" + "°C")
            elif weather == "Snow":
                st.write("Schneefall " + f"{ temp}" + "°C")
            else:
                st.write("WTF " + f"{ temp}" + "°C")
        except:
            st.write("Wetterdaten konnten nicht geladen werden")
    ## Filter für Live Allhttps://dev.azure.com/BATCloudMES/Superdepot%20ReportingSSCCLabelsPrinted Func ###
    def FilterNachDatum(day1, day2,df):
        #df['PlannedDate'] = df['PlannedDate'].dt.strftime('%m/%d/%y')
        df['PlannedDate'] = df['PlannedDate'].astype('datetime64[ns]').dt.date
        #filter nach Datum
        df = df[(df['PlannedDate'] >= day1) & (df['PlannedDate'] <= day2)]
        #mask = (df['PlannedDate'] >= day1) & (df['PlannedDate'] <= day2)         
        #df = df.loc[mask]
        return df

    ## Plotly Charts ###
    def fig_Status_nach_Katergorie(df):
        # Das Balkendiagram Teilt Fertige und Offene Gesamt Picks in Kategorien auf Karton, Paletten und Stangen aus 
            df = df.groupby(['AllSSCCLabelsPrinted'])[['Picks Karton','Picks Paletten','Picks Stangen']].sum().reset_index()        #set index to SapOrderNumber
            df['Picks Gesamt'] = df['Picks Karton'] + df['Picks Paletten'] + df['Picks Stangen']
            df['Picks Gesamt'] = df['Picks Gesamt'].round(0).astype(int)
            df['Picks Karton'] = df['Picks Karton'].round(0).astype(int)
            df['Picks Stangen'] = df['Picks Stangen'].round(0).astype(int)
            df['Picks Paletten'] = df['Picks Paletten'].round(0).astype(int)
            df = df.sort_values(by=['Picks Gesamt'], ascending=False)
            #reset index
            title = "<b>Status: </b> <span style='color:#0F2B63'>Karton</span> / <span style='color:#ef7d00'>Stangen</span> / <span style='color:#4FAF46'>Paletten</span>"
        
            df = df.reset_index(drop=True)
            figPicksBySAPOrder = px.bar(df, x=['Picks Karton','Picks Stangen','Picks Paletten',],y=df['AllSSCCLabelsPrinted'], title=title,height=300, orientation='h')
            figPicksBySAPOrder.update_traces(marker_color='#0F2B63', selector=dict(name='Picks Karton'))
            figPicksBySAPOrder.update_traces(marker_color='#4FAF46', selector=dict(name='Picks Paletten'))
            figPicksBySAPOrder.update_traces(marker_color='#ef7d00', selector=dict(name='Picks Stangen'))
            figPicksBySAPOrder.update_layout(showlegend=False)
            figPicksBySAPOrder.layout.xaxis.tickangle = 70
            figPicksBySAPOrder.update_traces(text=df['Picks Karton'], selector=dict(name='Picks Karton'),textposition='inside')
            figPicksBySAPOrder.update_traces(text=df['Picks Paletten'], selector=dict(name='Picks Paletten'),textposition='inside')
            figPicksBySAPOrder.update_traces(text=df['Picks Stangen'], selector=dict(name='Picks Stangen'),textposition='inside')
            figPicksBySAPOrder.update_layout(font_family="Montserrat",font_color="#0F2B63",title_font_family="Montserrat",title_font_color="#0F2B63")
            df['Transparency'] = np.where(df['AllSSCCLabelsPrinted']==True, 0.6, 1)
            figPicksBySAPOrder.update_traces(marker=dict(opacity=df['Transparency']))
            #passe y axis an von True zu "FERTIG" and False zu "OFFEN"
            #blende den titel auf der y axis aus
            figPicksBySAPOrder.update_yaxes(ticktext=['Offen','Fertig'])
            figPicksBySAPOrder.update_yaxes(tickvals=[0,1])
            figPicksBySAPOrder.update_xaxes(showticklabels=False)
            figPicksBySAPOrder.update_yaxes(title_text='')
            figPicksBySAPOrder.update_xaxes(title_text='')

            st.plotly_chart(figPicksBySAPOrder,use_container_width=True,config={'displayModeBar': False})
    
    def fig_trucks_Org(df):
        #st.dataframe(df)
        dfOriginal = df[df['LoadingLaneId'].notna()]
        depots = ['KNSTR', 'KNLEJ', 'KNBFE', 'KNHAJ']

        all_dfs = []  # Liste zum Sammeln der Datenframes für jedes Depot
        for depot in depots:
            dfDepot = dfOriginal[dfOriginal['DeliveryDepot'] == depot]
            dfDepot.loc[:, 'Picks Gesamt'] = dfDepot['Picks Gesamt'].astype(float)
            dfDepotAggregated = dfDepot.groupby(['DeliveryDepot', 'PlannedDate']).agg({'LoadingLaneId': 'nunique', 'Picks Gesamt': 'sum', 'Gepackte Paletten': 'sum', 'Geschätzte Paletten' : 'sum' }).reset_index()
            
            # Erstelle 'label' innerhalb der Schleife
            dfDepotAggregated['label'] = dfDepotAggregated.apply(lambda row: f"{row['DeliveryDepot']}: {row['LoadingLaneId']} LKW <br>{row['Picks Gesamt']} Picks <br>{row['Gepackte Paletten']} Bereits gepackte Paletten'",axis =1) # <br> {row['Geschätzte Paletten']} noch zu packende Paletten" , axis=1)
            
            all_dfs.append(dfDepotAggregated)

        dfAggregated = pd.concat(all_dfs)
        dfAggregated = dfAggregated.round(0)
        colors = ['#0e2b63', '#004f9f', '#ef7d00', '#ffbb00']
        # Erstelle Balkendiagramm
        # Erstellen Sie ein Farbwörterbuch
        color_dict = {depot: color for depot, color in zip(depots, colors)}

        # Erstelle Balkendiagramm
        fig = px.bar(dfAggregated, x='PlannedDate', y='Gepackte Paletten', color='DeliveryDepot', barmode='group',
                     title='LKW Pro Depot', height=600, text='label', hover_data=['Geschätzte Paletten'],
                     color_discrete_map=color_dict)  # Weisen Sie das Farbwörterbuch zu

        # Update der Layout-Einstellungen
        fig.update_layout(
            font_family="Montserrat",
            font_color="#0F2B63",
            title_font_family="Montserrat",
            title_font_color="#0F2B63",
            showlegend=False
        )
        fig.update_xaxes(showticklabels=True)
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    ############
# Funktion zur Erstellung des Diagramms
    def figUebermitteltInDeadline(df):    


        # Laden der CSV-Da

        # Setzen der Deadlines
        sel_deadStr = datetime.time(14, 0)
        sel_deadLej = datetime.time(14, 0)
        sel_deadBfe = datetime.time(14, 0)
        sel_deadHaj = datetime.time(15, 0)

        # Hinzufügen der Deadlines zum DataFrame
        df.loc[df['DeliveryDepot'] == 'KNSTR', 'Deadline'] = sel_deadStr
        df.loc[df['DeliveryDepot'] == 'KNLEJ', 'Deadline'] = sel_deadLej
        df.loc[df['DeliveryDepot'] == 'KNBFE', 'Deadline'] = sel_deadBfe
        df.loc[df['DeliveryDepot'] == 'KNHAJ', 'Deadline'] = sel_deadHaj

        # Konvertieren von 'PlannedDate' in datetime
        df['PlannedDate'] = pd.to_datetime(df['PlannedDate'])

        # Erstellen einer Datumsspalte als String
        df['Datum_string'] = df['PlannedDate'].dt.strftime('%Y-%m-%d')

        # Hinzufügen der Deadline zu PlannedDate
        df['Deadline'] = pd.to_datetime(df['PlannedDate'].astype(str) + ' ' + df['Deadline'].astype(str))

        # Filtern des DataFrames nach 'Status' = 'SSCCInformationSent'
        df['Status'] = np.where(df['Status'] == 'SSCCInformationSent', True, False)

        # Konvertieren von 'Fertiggestellt' in datetime und Hinzufügen von zwei Stunden
        df['Fertiggestellt'] = pd.to_datetime(df['Fertiggestellt'])
        df['Fertiggestellt'] = df['Fertiggestellt'] + pd.to_timedelta('2:00:00')

        # Füllen von None in 'PartnerName' mit 'Unbekannt'
        df['PartnerName'] = df['PartnerName'].fillna('Unbekannt')

        # Erstellen einer gekürzten Version des Partnernamens
        df['PartnerName_kurz'] = df['PartnerName'].apply(lambda x: x[:8] if len(x) > 15 else x)

        # Sicherstellen, dass beide Spalten tz-naive sind
        df['Fertiggestellt'] = df['Fertiggestellt'].dt.tz_localize(None)
        df['Deadline'] = df['Deadline'].dt.tz_localize(None)

        # Festlegen der Farben
        color_done = '#34c759'  # Grün für innerhalb der Deadline
        color_open = '#ff2d55'  # Rot für außerhalb der Deadline

        # Erstellen der gestapelten Balken
        fig = go.Figure()

        # Hinzufügen der Daten für jede Lieferung
        for depot in ['KNSTR', 'KNLEJ', 'KNBFE', 'KNHAJ']:
            df_depot = df[df['DeliveryDepot'] == depot]
            fertig_in_time = df_depot[df_depot['Fertiggestellt'] <= df_depot['Deadline']]
            fertig_out_time = df_depot[df_depot['Fertiggestellt'] > df_depot['Deadline']]
            
            fig.add_trace(go.Bar(
                x=fertig_in_time['Fertiggestellt'],
                y=[depot] * len(fertig_in_time),
                name=f'{depot} - In Time',
                marker_color=color_done,
                orientation='h'
            ))
            
            fig.add_trace(go.Bar(
                x=fertig_out_time['Fertiggestellt'],
                y=[depot] * len(fertig_out_time),
                name=f'{depot} - Out Time',
                marker_color=color_open,
                orientation='h'
            ))

        # Layout-Anpassungen
        fig.update_layout(
            barmode='stack',
            title='Fertiggestellt innerhalb und außerhalb der Deadline',
            xaxis=dict(title='Zeit'),
            yaxis=dict(title='Depot'),
            legend=dict(title='Legende'),
        )

        # Speichern des Diagramms als HTML-Datei

        # st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})


    def figUebermitteltInDeadlineURALT(df):        
        sel_deadStr = '14:00:00'
        sel_deadLej = '14:00:00'
        sel_deadHan = '14:00:00'
        sel_deadBiel = '14:00:00'
        #add deadlines to df by DeliveryDepot
        df['Deadline'] = np.where(df['DeliveryDepot'] == 'KNLEJ', sel_deadStr, sel_deadLej)
        df['PlannedDate'] = df['PlannedDate'] + pd.to_timedelta(df['Deadline'])
        #convert to datetime
        df['PlannedDate'] = pd.to_datetime(df['PlannedDate'])
        
        
        # filter by fertiggestellt = '0'
        dfFertig = df[df['Fertiggestellt'] != '0']
        dfFertig['Fertiggestellt'] = pd.to_datetime(dfFertig['Fertiggestellt'], format='%Y-%m-%d %H:%M:%S.%f%z')
        #add two hours to Feritggestellt
        #dfFertig['Fertiggestellt'] = dfFertig['Fertiggestellt'] + pd.to_timedelta('2:00:00')
        #drop utc
        dfFertig['Fertiggestellt'] = dfFertig['Fertiggestellt'].dt.tz_localize(None)
        dfFertig['InTime'] = (dfFertig['Fertiggestellt'] < dfFertig['PlannedDate'])
         #.astype(int)
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
        title = "<b>Lieferschein in Deadline Fertiggestellt  </b> <span style='color:#4FAF46'>ja</span> / <span style='color:#E72482'>nein</span>"

        fig = px.bar(dfFertig, x='Fertiggestellt', y="Picks Gesamt", color="InTime", hover_data=['PartnerName','Fertig um','SapOrderNumber','DeliveryDepot'],height=600, title=title)
        #if in Time 1 set to green else to red
        fig.update_traces(marker_color=['#4FAF46' if x == 1 else '#E72482' for x in dfFertig['InTime']])
        fig.data[0].text = dfFertig['PartnerName'] + '<br>' + dfFertig['Picks Gesamt'].astype(str)
        fig.layout.xaxis.type = 'category'
        # x aaxis text horizontal
        fig.layout.xaxis.tickangle = 70
        # remove xaxis and yaxis title
        fig.update_layout(font_family="Montserrat",font_color="#0F2B63",title_font_family="Montserrat",title_font_color="#0F2B63")
        fig.update_layout(legend_title_text='InTime')
        fig.update_yaxes(title_text='')
        fig.update_xaxes(title_text='')
        # Date PartnerName to text
        st.plotly_chart(fig, use_container_width=True,config={'displayModeBar': False})

    # def pick_stunden(df):
    #     import matplotlib.pyplot as plt
    #     data = df
    #     # Convert 'Fertiggestellt' to datetime
    #     data['Fertiggestellt'] = pd.to_datetime(data['Fertiggestellt'])

    #     # Combine all Picks columns
    #     picks_columns = ['Picks Karton fertig', 'Picks Paletten fertig', 'Picks Stangen fertig']
    #     data['Total Picks'] = data[picks_columns].sum(axis=1, skipna=True)

    #     # Group by hour and sum the total picks
    #     data.set_index('Fertiggestellt', inplace=True)
    #     hourly_picks = data['Total Picks'].resample('H').sum()

    #     # Plot the data
    #     plt.figure(figsize=(12, 6))
    #     hourly_picks.plot(kind='line')
    #     plt.title('Summe der Picks pro Stunde')
    #     plt.xlabel('Stunde')
    #     plt.ylabel('Summe der Picks')
    #     plt.grid(True)
    #     st.pyplot()


    def status(df):
        # if in df Staus is SSCCInformationSent then change to 1 else 0
        df['Status'] = np.where(df['Status'] == 'SSCCInformationSent', True, False)
        df = df.groupby(['PartnerName', 'SapOrderNumber', "Status", 'DeliveryDepot', 'Fertiggestellt', 'Lieferschein erhalten']).agg({'Picks Gesamt': 'sum'}).reset_index()
        df = df.sort_values(by=['Picks Gesamt', 'Status'], ascending=False)
        
        # HTML-formatted title with different word colors
        title = "<b>Order an K&N Übermittelt je Depot:</b> <span style='color:#E72482'>Nein</span> / <span style='color:#4FAF46'>Ja</span>"
        figTagKunden = px.bar(df, x="DeliveryDepot", y="Picks Gesamt", title=title, hover_data=['Picks Gesamt','PartnerName', 'SapOrderNumber','Lieferschein erhalten', 'Fertiggestellt'], height=900)
        
        figTagKunden.update_traces(marker_color=np.where(df['Status'] == 1, '#4FAF46', '#E72482'))
        figTagKunden.update_traces(texttemplate='%{text:.3}', text=df['Picks Gesamt'], textposition='inside')
        figTagKunden.update_layout(uniformtext_minsize=13, uniformtext_mode='hide', showlegend=False)
        #figTagKunden.layout.xaxis.tickangle = 70
        figTagKunden.update_layout(font_family="Montserrat", font_color="#0F2B63", title_font_family="Montserrat", title_font_color="#0F2B63",)
        #disable xaxis title
        figTagKunden.update_xaxes(title_text='')
        
        # figTagKunden.update_layout(
        #             annotations=[
        #                 {"x": x, "y": total * 1.05, "text": str(total), "showarrow": False}
        #                 for x, total in df.groupby("PartnerName", as_index=False).agg({"Picks Gesamt": "sum"}).values])
        figTagKunden.update_yaxes(title_text='')
        figTagKunden.update_xaxes(title_text='')

        st.plotly_chart(figTagKunden, use_container_width=True,config={'displayModeBar': False})
        with st.popover("Tabellenansicht"):
            #rename column AllSSCCLabelsPrinted to Übermittelt an K&N Ja/Nein
            dfnew = df.rename(columns={'Status': 'Übermittelt an K&N Ja/Nein'})
            st.dataframe(dfnew)

    def figPicksKunde(df):
        df = df.groupby(['PartnerName', 'SapOrderNumber', "AllSSCCLabelsPrinted", 'DeliveryDepot', 'Fertiggestellt', 'Lieferschein erhalten']).agg({'Picks Gesamt': 'sum'}).reset_index()
        df = df.sort_values(by=['Picks Gesamt', 'AllSSCCLabelsPrinted'], ascending=False)
        
        # HTML-formatted title with different word colors
        title = "<b>Kundenübersicht nach Status:</b> <span style='color:#E72482'>Offen</span> / <span style='color:#4FAF46'>Fertig</span>"
        figTagKunden = px.bar(df, x="PartnerName", y="Picks Gesamt", title=title, hover_data=['Picks Gesamt', 'SapOrderNumber','Lieferschein erhalten', 'Fertiggestellt'], height=900)
        
        figTagKunden.update_traces(marker_color=np.where(df['AllSSCCLabelsPrinted'] == 1, '#4FAF46', '#E72482'))
        figTagKunden.update_traces(texttemplate='%{text:.3}', text=df['Picks Gesamt'], textposition='inside')
        figTagKunden.update_layout(uniformtext_minsize=10, uniformtext_mode='hide', showlegend=False)
        figTagKunden.layout.xaxis.tickangle = 70
        figTagKunden.update_layout(font_family="Montserrat", font_color="#0F2B63", title_font_family="Montserrat", title_font_color="#0F2B63",)
        #disable xaxis title
        figTagKunden.update_xaxes(title_text='')
        
        figTagKunden.update_layout(
                    annotations=[
                        {"x": x, "y": total * 1.05, "text": str(total), "showarrow": False}
                        for x, total in df.groupby("PartnerName", as_index=False).agg({"Picks Gesamt": "sum"}).values])
        figTagKunden.update_yaxes(title_text='')
        figTagKunden.update_xaxes(title_text='')

        st.plotly_chart(figTagKunden, use_container_width=True,config={'displayModeBar': False})

    def figPicksBy_SAP_Order_CS_PAL(df):
        df = df.groupby(['SapOrderNumber','PartnerName','AllSSCCLabelsPrinted'])[['Picks Karton','Picks Paletten','Picks Stangen']].sum().reset_index()        #set index to SapOrderNumber
        df['Picks Gesamt'] = df['Picks Karton'] + df['Picks Paletten'] + df['Picks Stangen']
        df['Picks Gesamt'] = df['Picks Gesamt'].round(0).astype(int)
        df['Picks Karton'] = df['Picks Karton'].round(0).astype(int)
        df['Picks Stangen'] = df['Picks Stangen'].round(0).astype(int)
        df['Picks Paletten'] = df['Picks Paletten'].round(0).astype(int)
        df = df.sort_values(by=['Picks Gesamt'], ascending=False)
        #reset index
        title = "<b>Picks Pro Lieferschein: </b> <span style='color:#ef7d00'>Stangen</span> / <span style='color:#0F2B63'>Karton</span> / <span style='color:#4FAF46'>Paletten</span>"
    
        df = df.reset_index(drop=True)
        figPicksBySAPOrder = px.bar(df, y=['Picks Karton','Picks Paletten','Picks Stangen'], title=title,hover_data=['SapOrderNumber','Picks Gesamt','PartnerName',],height=600)
        figPicksBySAPOrder.update_traces(marker_color='#0F2B63', selector=dict(name='Picks Karton'))
        figPicksBySAPOrder.update_traces(marker_color='#4FAF46', selector=dict(name='Picks Paletten'))
        figPicksBySAPOrder.update_traces(marker_color='#ef7d00', selector=dict(name='Picks Stangen'))
        figPicksBySAPOrder.update_layout(showlegend=False)
        figPicksBySAPOrder.layout.xaxis.tickangle = 70
        df['Transparency'] = np.where(df['AllSSCCLabelsPrinted']==True, 0.3, 1)
        figPicksBySAPOrder.update_traces(marker=dict(opacity=df['Transparency']))
        figPicksBySAPOrder.update_layout(font_family="Montserrat",font_color="#0F2B63",title_font_family="Montserrat",title_font_color="#0F2B63")
        figPicksBySAPOrder.update_traces(text=df['Picks Karton'], selector=dict(name='Picks Karton'),textposition='inside')
        figPicksBySAPOrder.update_traces(text=df['Picks Paletten'], selector=dict(name='Picks Paletten'),textposition='inside')
        figPicksBySAPOrder.update_traces(text=df['Picks Stangen'], selector=dict(name='Picks Stangen'),textposition='inside')
        #hide xaxis title and ticks
        figPicksBySAPOrder.update_xaxes(showticklabels=False)
        #disable index
        figPicksBySAPOrder.update_yaxes(title_text='')
        figPicksBySAPOrder.update_xaxes(title_text='')


        st.plotly_chart(figPicksBySAPOrder,use_container_width=True,config={'displayModeBar': False})

    def figTachoDiagramm_VEGA(df, delivery_depot):
        with st.container(border=True):
            if delivery_depot == "Gesamt":
                df = df
            else:
                df = df[df['DeliveryDepot'] == delivery_depot]  
                if delivery_depot == "KNLEJ":
                    delivery_depot = "Leipzig"
                elif delivery_depot == "KNSTR":
                    delivery_depot = "Stuttgart"
                elif delivery_depot == "KNHAJ":
                    delivery_depot = "Hannover"
                elif delivery_depot == "KNBFE":
                    delivery_depot = "Bielefeld"
                else:
                    delivery_depot = "Gesamt"
            
            def calPicks(df):
                    open_DN = df[df['AllSSCCLabelsPrinted']==0]['SapOrderNumber'].nunique()
                    done_DN = df[df['AllSSCCLabelsPrinted']==1]['SapOrderNumber'].nunique()
                    done_mastercase = df[df['AllSSCCLabelsPrinted']==0]['Picks Karton'].sum()       
                    done_outer = df[df['AllSSCCLabelsPrinted']==0]['Picks Stangen'].sum()
                    done_pallet = df[df['AllSSCCLabelsPrinted']==0]['Picks Paletten'].sum()                       
                    open_mastercase = df[df['AllSSCCLabelsPrinted']==1]['Picks Karton'].sum()
                    open_outer = df[df['AllSSCCLabelsPrinted']==1]['Picks Stangen'].sum()
                    open_pallet = df[df['AllSSCCLabelsPrinted']==1]['Picks Paletten'].sum()                    
                    open_ALL = df[df['AllSSCCLabelsPrinted']==0]['Picks Gesamt'].sum()
                    done_All = df[df['AllSSCCLabelsPrinted']==1]['Picks Gesamt'].sum()     
                    return open_DN, done_DN, done_mastercase, done_outer, done_pallet, open_mastercase, open_outer, open_pallet, open_ALL, done_All
            open_DN, done_DN, done_mastercase, done_outer, done_pallet, open_mastercase, open_outer, open_pallet, open_ALL, done_All = calPicks(df)
            sum_picks = open_ALL + done_All 
            completion_rate = round((done_All / sum_picks) * 100, 2)
            # Farbgebung basierend auf dem Fortschritt
            if completion_rate < 25:
                bar_color = '#e72582'
            elif 25 <= completion_rate < 50:
                bar_color = '#ef7d00'
            elif 50 <= completion_rate < 75:
                bar_color = '#ef7d00'
            else:
                bar_color = 'green'
            # Erstellen des Tacho-Diagramms

            fig = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = completion_rate,
                gauge = {
                    'axis': {'range': [None, 100], 'tickvals': [i for i in range(0, 101, 10)], 'ticktext': [f'{int(sum_picks * i / 100)}' for i in range(0, 101, 10)]},
                    'bar': {'color': bar_color},  # Farbe des Balkens
                    'steps': [
                        {'range': [0, 25], 'color': '#0e2b63'},
                        {'range': [25, 50], 'color': '#0e2b63'},
                        {'range': [50, 75], 'color': "#0e2b63"},
                        {'range': [75, 100], 'color': "#0e2b63"}],
                }))
            fig.update_layout(
                title={
                    'text': f"{delivery_depot}",
                    'y':0.9,
                    'x':0.5,
                    'xanchor': 'center',
                    'yanchor': 'top'
                },
                showlegend=False,
                font_family="Montserrat",
                font_color="#0F2B63",
                title_font_family="Montserrat",
                title_font_color="#0F2B63",
                title_font_size=25,
                autosize=True,
                # margin=dict(t=78, b=95, l=5, r=5)
            )
            fig.update_layout(height=330)
            fig.add_annotation(x=0.5, y=-0.15, text=f"Gesamt: {sum_picks}", showarrow=False, font=dict(size=14))
            fig.add_annotation(x=0.1, y=-0.25, text=f"Fertig: {done_All}", showarrow=False, font=dict(size=12))
            fig.add_annotation(x=0.9, y=-0.25, text=f"Offen: {open_ALL}", showarrow=False, font=dict(size=12))

            
            # Anzeigen des Diagramms in Streamlit
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})



            def masterCase_Outer_Pal_Icoons(img_type,done_value,open_value):
                '''Function to display the MasterCase, OuterCase and Pallet Icons in the Live Status Page
                Args:
                    img_type (str): Type of Icon to display
                    done_value (int): Value of done picks
                    open_value (int): Value of open picks
                '''
                icon_path_mastercase = 'Data/appData/ico/mastercase_favicon.ico'
                icon_path_outer = 'Data/appData/ico/favicon_outer.ico'
                icon_path_pallet = 'Data/appData/ico/pallet_favicon.ico'   
                icon_path_Delivery = 'Data/appData/ico/delivery-note.ico' 

                #select img type by string
                if img_type == 'Mastercase':
                    img = Image.open(icon_path_mastercase)
                elif img_type == 'Outer':
                    img = Image.open(icon_path_outer)
                elif img_type == 'Pallet':
                    img = Image.open(icon_path_pallet)  
                elif img_type == 'Delivery':
                    img = Image.open(icon_path_Delivery)
                    

                img_type = img
                col1, col2,col3,col4 = st.columns([0.1,0.1,0.4,0.1])
                with col1:
                    st.write('')
                with col2:
                    st.image(img_type, width=32,clamp=False)
                    hide_img_fs = '''
                    <style>
                    button[title="View fullscreen"]{
                        visibility: hidden;}
                    </style>
                    '''
                    st.markdown(hide_img_fs, unsafe_allow_html=True)
                with col3:
                    annotated_text(annotation(str(done_value),'', "#50af47", font_family="Montserrat"),'  / ',annotation(str(open_value),'', "#ef7d00", font_family="Montserrat"))
            
            # with st.container(border=True):
            masterCase_Outer_Pal_Icoons('Delivery' ,done_DN, open_DN)
            masterCase_Outer_Pal_Icoons('Outer' ,open_outer, done_outer)
            masterCase_Outer_Pal_Icoons('Mastercase' ,open_mastercase, done_mastercase)
            masterCase_Outer_Pal_Icoons('Pallet' ,open_pallet, done_pallet)        
    def figTachoDiagramm(df, delivery_depot):
        with st.container(border=True):
            if delivery_depot == "Gesamt":
                df = df
            else:
                df = df[df['DeliveryDepot'] == delivery_depot]  
                if delivery_depot == "KNLEJ":
                    delivery_depot = "Leipzig"
                elif delivery_depot == "KNSTR":
                    delivery_depot = "Stuttgart"
                elif delivery_depot == "KNHAJ":
                    delivery_depot = "Hannover"
                elif delivery_depot == "KNBFE":
                    delivery_depot = "Bielefeld"
                else:
                    delivery_depot = "Gesamt"
            
            def calPicks(df):
                    open_DN = df[df['AllSSCCLabelsPrinted']==0]['SapOrderNumber'].nunique()
                    done_DN = df[df['AllSSCCLabelsPrinted']==1]['SapOrderNumber'].nunique()
                    done_mastercase = df[df['AllSSCCLabelsPrinted']==0]['Picks Karton'].sum()       
                    done_outer = df[df['AllSSCCLabelsPrinted']==0]['Picks Stangen'].sum()
                    done_pallet = df[df['AllSSCCLabelsPrinted']==0]['Picks Paletten'].sum()                       
                    open_mastercase = df[df['AllSSCCLabelsPrinted']==1]['Picks Karton'].sum()
                    open_outer = df[df['AllSSCCLabelsPrinted']==1]['Picks Stangen'].sum()
                    open_pallet = df[df['AllSSCCLabelsPrinted']==1]['Picks Paletten'].sum()                    
                    open_ALL = df[df['AllSSCCLabelsPrinted']==0]['Picks Gesamt'].sum()
                    done_All = df[df['AllSSCCLabelsPrinted']==1]['Picks Gesamt'].sum()     
                    return open_DN, done_DN, done_mastercase, done_outer, done_pallet, open_mastercase, open_outer, open_pallet, open_ALL, done_All
            open_DN, done_DN, done_mastercase, done_outer, done_pallet, open_mastercase, open_outer, open_pallet, open_ALL, done_All = calPicks(df)
            sum_picks = open_ALL + done_All 
            completion_rate = round((done_All / sum_picks) * 100, 2)
#########''



            fig = go.Figure(go.Indicator(
                domain = {'x': [0, 1], 'y': [0, 1]},
                value = completion_rate,
                mode = "gauge+number+delta",
                title = {'text': f"{delivery_depot} Ziel (%)"},
                number = {'suffix': "%"},
                gauge = {
                    'axis': {
                        'range': [0, 100],
                        'tickangle': -90,
                        'tickvals': [],
                        'ticktext': []
                    },
                    'steps': [{'range': [0, 100], 'color': "#0F2B63"}],
                }
            ))

            fig.update_layout(
                title={
                    'text': f"{delivery_depot}",
                    'y':0.9,
                    'x':0.5,
                    'xanchor': 'center',
                    'yanchor': 'top'
                },
                showlegend=False,
                font_family="Montserrat",
                font_color="#0F2B63",
                title_font_family="Montserrat",
                title_font_color="#0F2B63",
                title_font_size=25,
                autosize=True,
                margin=dict(t=78, b=95, l=5, r=5)
            )

            # Relative Positionierung für die Annotationen
            fig.add_annotation(x=0.5, y=-0.15, text=f"Gesamt: {sum_picks}", showarrow=False, font=dict(size=14))
            fig.add_annotation(x=0.1, y=-0.25, text=f"Fertig: {done_All}", showarrow=False, font=dict(size=12))
            fig.add_annotation(x=0.9, y=-0.25, text=f"Offen: {open_ALL}", showarrow=False, font=dict(size=12))

            fig.update_layout(height=330)
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})




            
            def masterCase_Outer_Pal_Icoons(img_type,done_value,open_value):
                '''Function to display the MasterCase, OuterCase and Pallet Icons in the Live Status Page
                Args:
                    img_type (str): Type of Icon to display
                    done_value (int): Value of done picks
                    open_value (int): Value of open picks
                '''
                icon_path_mastercase = 'Data/appData/ico/mastercase_favicon.ico'
                icon_path_outer = 'Data/appData/ico/favicon_outer.ico'
                icon_path_pallet = 'Data/appData/ico/pallet_favicon.ico'   
                icon_path_Delivery = 'Data/appData/ico/delivery-note.ico' 
                icon_path_Sum = 'Data/appData/ico/summe.ico'
                img_mastercase = Image.open(icon_path_mastercase)
                img_outer = Image.open(icon_path_outer)
                img_pallet = Image.open(icon_path_pallet)
                img_Delivery = Image.open(icon_path_Delivery)
                icon_path_Sum = Image.open(icon_path_Sum)

                #select img type by string
                if img_type == 'Mastercase':
                    img = Image.open(icon_path_mastercase)
                elif img_type == 'Outer':
                    img = Image.open(icon_path_outer)
                elif img_type == 'Pallet':
                    img = Image.open(icon_path_pallet)  
                elif img_type == 'Delivery':
                    img = Image.open(icon_path_Delivery)
                    

                img_type = img
                col1, col2,col3,col4 = st.columns([0.1,0.1,0.4,0.1])
                with col1:
                    st.write('')
                with col2:
                    st.image(img_type, width=32,clamp=False)
                    hide_img_fs = '''
                    <style>
                    button[title="View fullscreen"]{
                        visibility: hidden;}
                    </style>
                    '''
                    st.markdown(hide_img_fs, unsafe_allow_html=True)
                with col3:
                    annotated_text(annotation(str(done_value),'', "#50af47", font_family="Montserrat"),'  / ',annotation(str(open_value),'', "#ef7d00", font_family="Montserrat"))
            # with st.container(border=True):
            masterCase_Outer_Pal_Icoons('Delivery' ,done_DN, open_DN)
            masterCase_Outer_Pal_Icoons('Outer' ,open_outer, done_outer)
            masterCase_Outer_Pal_Icoons('Mastercase' ,open_mastercase, done_mastercase)
            masterCase_Outer_Pal_Icoons('Pallet' ,open_pallet, done_pallet)        

    def figUebermitteltInDeadline_Grundlage(df):        
        sel_deadStr = '14:00:00'
        sel_deadLej = '14:00:00'
        sel_deadBfe = '14:00:00'
        sel_deadHaj = '14:00:00'

        #add deadlines to df by DeliveryDepot 
        df.loc[df['DeliveryDepot'] == 'KNSTR', 'Deadline'] = sel_deadStr
        df.loc[df['DeliveryDepot'] == 'KNLEJ', 'Deadline'] = sel_deadLej
        df.loc[df['DeliveryDepot'] == 'KNBFE', 'Deadline'] = sel_deadBfe
        df.loc[df['DeliveryDepot'] == 'KNHAJ', 'Deadline'] = sel_deadHaj
        
        df['PlannedDate'] = df['PlannedDate'] + pd.to_timedelta(df['Deadline'])
        # filter df by AllSSCCLabelsPrinted = 1
        df = df[df['AllSSCCLabelsPrinted'] == 1]
        df['PlannedDate'] = pd.to_datetime(df['PlannedDate'])
        #Fertiggestellt to datetime
        df['Fertiggestellt'] = pd.to_datetime(df['Fertiggestellt'])
        #add two hours to Feritggestellt

        def kategorisieren(volume):
            if volume <= 25:
                return '1-25'
            elif volume <= 100:
                return '26-100'
            elif volume <= 200:
                return '101-200'
            else:
                return '201+'

        def fehlerprüfung(row):
            # Fertiggestellt zu datetime konvertieren
            row['Fertiggestellt'] = pd.to_datetime(row['Fertiggestellt'])
            # First_Picking zu datetime konvertieren
            row['First_Picking'] = pd.to_datetime(row['First_Picking'])
            row['Fertiggestellt'] = pd.to_datetime(row['Fertiggestellt']).tz_localize(None)
            # First_Picking zu datetime konvertieren
            row['First_Picking'] = pd.to_datetime(row['First_Picking']).tz_localize(None)
            if pd.isnull(row['Fertiggestellt']) or row['Fertiggestellt'] - row['First_Picking'] < pd.Timedelta(hours=0):
                row['Fehlerspalte'] = row['First_Picking']
                row['First_Picking'] = row['Fertiggestellt'] - pd.Timedelta(hours=3)
                # Prüfe ob Fertiggestellt - FirstPick größer als 36h ist wenn ja kopiere wieder
                if row['Fertiggestellt'] - row['First_Picking'] > pd.Timedelta(hours=36):
                    row['Fehlerspalte'] = row['First_Picking']
                    row['First_Picking'] = row['Fertiggestellt'] - pd.Timedelta(hours=3)            
            return row

        df = df.apply(fehlerprüfung, axis=1)
        df['Volumen Kategorie'] = df['Picks Gesamt'].apply(kategorisieren)
        # add 2 hours to Fertiggestellt
        df['Fertiggestellt'] = df['Fertiggestellt'] + pd.to_timedelta('2:00:00')
        df['First_Picking'] = df['First_Picking'] + pd.to_timedelta('2:00:00')
        df = df.rename(columns={'First_Picking': 'Start Bearbeitung', 'Fertiggestellt': 'Ende Bearbeitung'})
        df['PartnerName_kurz'] = df['PartnerName'].apply(lambda x: x[:8] + '...' if len(x) > 15 else x)
        df.sort_values(by='Start Bearbeitung', inplace=True)

        # Funktion zur Bestimmung der Stapel-Ebene für jeden Balken
        def calculate_levels(df, start_column, end_column):
            levels = [0]  # Start mit Ebene 0
            for index, row in df.iterrows():
                current_start = row[start_column]
                for level in range(len(levels)):
                    if all(current_start >= df.loc[df['level'] == level, end_column]):
                        break
                else:
                    levels.append(level + 1)
                    level = len(levels) - 1
                df.at[index, 'level'] = level
            return df

        df['level'] = 0  # Initialisiere die Ebene mit 0
        df = calculate_levels(df, 'Start Bearbeitung', 'Ende Bearbeitung')
        # Text für die Balken kürzen (beispielsweise auf 15 Zeichen begrenzen)
        df['PartnerName_kurz'] = df['PartnerName'].apply(lambda x: x[:15] + '...' if len(x) > 15 else x)

        # Erstellen des Zeitstrahls mit Plotly
        fig = px.timeline(
            df,
            x_start='Start Bearbeitung',
            x_end='Ende Bearbeitung',
            y='level',
            color='Volumen Kategorie',
            text='PartnerName_kurz',  # Verwendung des gekürzten Namens
            # hover_data={
            #     'PartnerName': True,  # Zeigt den vollen Partner-Namen an
            #     'SapOrderNumber': True,  # Zeigt die SapOrderNumber an
            
            #     'Volumen Kategorie': False,  # Verstecke die Volumen Kategorie, da sie als Farbe dargestellt wird
            #     'level': False,  # Verstecke die Ebene, da sie nur für die Anordnung verwendet wird
            #     'PartnerName_kurz': False  # Versteckt den gekürzten Partner-Namen
            # },
            title='Auftragsbearbeitungszeitraum',
            color_discrete_map={
                '1-25': '#ef7d00',
                '26-100': '#ffbb00',
                '101-200': '#ffaf47',
                '201+': '#afca0b'
            }
        )

        # Schriftart und weitere Layout-Anpassungen
        fig.update_layout(
            font_family="Montserrat",
            xaxis_title='Zeit',
            yaxis_title='Ebene',
            yaxis={'visible': False},
            showlegend=False,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )

        # Rahmen hinzufügen
        fig.update_traces(marker_line_width=2, marker_line_color="black")

        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    def timeline(df):
        #https://timeline.knightlab.com/docs/json-format.html#json-text
        # filter df by AllSSCCLabelsPrinted = 1
        df = df[df['AllSSCCLabelsPrinted'] == 1].copy()  # Erstellen Sie eine Kopie des gefilterten DataFrames
        df.loc[:, 'PlannedDate'] = pd.to_datetime(df['PlannedDate'])
        #Fertiggestellt to datetime
        df.loc[:, 'Fertiggestellt'] = pd.to_datetime(df['Fertiggestellt'])
        #add two hours to Feritggestellt
        df['Fertiggestellt'] = df['Fertiggestellt'] + pd.to_timedelta('2:00:00')
        

        def kategorisieren(volume):
            if volume <= 25:
                return '1-25'
            elif volume <= 100:
                return '26-100'
            elif volume <= 200:
                return '101-200'
            else:
                return '201+'

        def fehlerprüfung(row):
            # Fertiggestellt zu datetime konvertieren
            row['Fertiggestellt'] = pd.to_datetime(row['Fertiggestellt'])
            # First_Picking zu datetime konvertieren
            row['First_Picking'] = pd.to_datetime(row['First_Picking'])
            row['Fertiggestellt'] = pd.to_datetime(row['Fertiggestellt']).tz_localize(None)
            # First_Picking zu datetime konvertieren
            row['First_Picking'] = pd.to_datetime(row['First_Picking']).tz_localize(None)
            if pd.isnull(row['Fertiggestellt']) or row['Fertiggestellt'] - row['First_Picking'] < pd.Timedelta(hours=0):
                row['Fehlerspalte'] = row['First_Picking']
                row['First_Picking'] = row['Fertiggestellt'] - pd.Timedelta(hours=3)
                # Prüfe ob Fertiggestellt - FirstPick größer als 36h ist wenn ja kopiere wieder
                if row['Fertiggestellt'] - row['First_Picking'] > pd.Timedelta(hours=36):
                    row['Fehlerspalte'] = row['First_Picking']
                    row['First_Picking'] = row['Fertiggestellt'] - pd.Timedelta(hours=3)            
            return row

        df = df.apply(fehlerprüfung, axis=1)
        df['Volumen Kategorie'] = df['Picks Gesamt'].apply(kategorisieren)
        df['First_Picking'] = df['First_Picking'] + pd.to_timedelta('2:00:00')
        df = df.rename(columns={'First_Picking': 'Start Bearbeitung', 'Fertiggestellt': 'Ende Bearbeitung'})
        df.sort_values(by='Start Bearbeitung', inplace=True)

        # Funktion zur Bestimmung der Stapel-Ebene für jeden Balken
        def calculate_levels(df, start_column, end_column):
            levels = [0]  # Start mit Ebene 0
            for index, row in df.iterrows():
                current_start = row[start_column]
                for level in range(len(levels)):
                    if all(current_start >= df.loc[df['level'] == level, end_column]):
                        break
                else:
                    levels.append(level + 1)
                    level = len(levels) - 1
                df.at[index, 'level'] = level
            return df
        # cal levels
        df['level'] = 0  # Initialisiere die Ebene mit 0
        df = calculate_levels(df, 'Start Bearbeitung', 'Ende Bearbeitung')
        
        def convert_to_timeline_json(df):
            # Basisstruktur des JSON für TimelineJS
            timeline_json = {
                "title": {
                    "text": {
                        "headline": "Auftragsbearbeitung",
                        "text": "Zeitstrahl der Bearbeitungsdauer"
                    }
                },
                "events": []
            }

            for _, row in df.iterrows():
                details = f"""
                <ul>
                <li>Ziel Depot: {row['DeliveryDepot']}</li>
                <li>SapOrderNumber: {row['SapOrderNumber']}</li>
                <li>Gesamt Picks: {row['Picks Gesamt']}</li>
                <li>Picks in Stangen: {row['Picks Stangen']}</li>
                <li>Picks in Karton: {row['Picks Karton']}</li>
                <li>Picks in Paletten: {row['Picks Paletten']}</li>
                <li>Kommissionierte Paletten: {row['Fertige Paletten']}</li>
                <li> Start Bearbeitung: {row['Start Bearbeitung']}</li>
                <li> Ende Bearbeitung: {row['Ende Bearbeitung']}</li>
                <li> Gesamtbearbeitungszeit: {row['Ende Bearbeitung'] - row['Start Bearbeitung']}</li>
                
                </ul>
                """          
                event = {
                    "start_date": {
                        "year": row['Start Bearbeitung'].year,
                        "month": row['Start Bearbeitung'].month,
                        "day": row['Start Bearbeitung'].day,
                        "hour": row['Start Bearbeitung'].hour,
                        "minute": row['Start Bearbeitung'].minute,
                        "second": row['Start Bearbeitung'].second
                    },
                    "end_date": {
                        "year": row['Ende Bearbeitung'].year,
                        "month": row['Ende Bearbeitung'].month,
                        "day": row['Ende Bearbeitung'].day,
                        "hour": row['Ende Bearbeitung'].hour,
                        "minute": row['Ende Bearbeitung'].minute,
                        "second": row['Ende Bearbeitung'].second
                    },
                        "text": {
                            "headline": row['PartnerName'],
                            "text": details
                        }
                }
                timeline_json['events'].append(event)

            return timeline_json
        timeline_json = convert_to_timeline_json(df)
        timeline.timeline(timeline_json)
    ## AG-Grid Func ####
    def tabelleAnzeigen(df):
        #new df with only the columns we need 'PlannedDate' ,'SapOrderNumber','PartnerName']#'Fertiggestellt','Picks Gesamt','Picks Karton','Picks Paletten','Picks Stangen','Lieferschein erhalten','Fertiggestellt'
        dfAG = df[['PlannedDate','Lieferschein erhalten','DeliveryDepot','SapOrderNumber','PartnerName','Fertiggestellt','Fertige Paletten','Picks Gesamt','UnloadingListIdentifier','ActualNumberOfPallets','EstimatedNumberOfPallets']]


        st.dataframe(data=dfAG, use_container_width=True)
    
    def downLoadTagesReport(df):
    
        
        def convert_df(df):
            return df.to_csv(index=False).encode('utf-8')
        csv = convert_df(df)
        # LIVE.heute to string
        tagimfilename= datetime.date.today().strftime("%d.%m.%Y")

        st.download_button(
        "Download Tagesreport als csv",
        csv,
        tagimfilename + "_Tagesreport.csv",
        "text/csv",
        key='download-csv'
            )

    def picksDepot(df):
        pass
    

    #######------------------Main------------------########

    def PageTagesReport():
        pd.set_option("display.precision", 2)
        sar.st_autorefresh(interval=48000, debounce=True)
        colhead1, colhead2 ,colhead3, colhead4 = st.columns(4)
        with colhead2:
            lastUpdate = read_Table('prod_KundenbestellungenUpdateTime')
            lastUpdateDate = lastUpdate['time'].iloc[0]
            st.write('Letztes Update:')
            st.write(lastUpdateDate)
        with colhead1:
            sel_date = datetime.date.today()  
            sel_date = st.date_input('Datum', sel_date)   
            dfOr = LIVE.loadDF(sel_date,sel_date) 
            
        with colhead3:
            st.write(f'Hi {st.session_state.user} 👋')
        with colhead4:                
            LIVE.wetter()
        img_strip = Image.open('Data/img/strip.png')   
        img_strip = img_strip.resize((1000, 15))     

        st.image(img_strip, use_column_width=True, caption='',)      

        col33 ,col34, col35, col36, col37 = st.columns(5)
        with col33:
            LIVE.figTachoDiagramm_VEGA(dfOr,'Gesamt')
        with col34:
            LIVE.figTachoDiagramm_VEGA(dfOr,'KNSTR')
        with col35:
            LIVE.figTachoDiagramm_VEGA(dfOr,'KNLEJ')
        with col36:
            LIVE.figTachoDiagramm_VEGA(dfOr,'KNBFE')
        with col37:
            LIVE.figTachoDiagramm_VEGA(dfOr,'KNHAJ')

        try:
            with st.popover('Auftragsdetails in Timeline',help='Details zu den Aufträgen', use_container_width=True, ):
                    LIVE.timeline(dfOr)         
        except:
            st.write('Keine Daten vorhanden')   
        # try:
        #     LIVE.pick_stunden(dfOr)
        # except:
        #     st.write('Keine Daten vorhanden')
        try:
            LIVE.figUebermitteltInDeadline(dfOr)
        except:
            st.write('Keine Daten vorhanden')
        try:
            LIVE.figPicksKunde(dfOr)
        except:
            st.write('Keine Daten vorhanden')
        # try:
        #     LIVE.status(dfOr)
        # except:
        #     st.write('Keine Daten vorhanden')
        try:
            LIVE.fig_trucks_Org(dfOr)
        except:
            st.write('Keine Daten vorhanden')
        try:
            LIVE.fig_Status_nach_Katergorie(dfOr)
        except:
            st.write('Keine Daten vorhanden')
        try:
            LIVE.figPicksBy_SAP_Order_CS_PAL(dfOr) 
        except:
            st.write('Keine Daten vorhanden')
        try:
            LIVE.tabelleAnzeigen(dfOr)
        except:
            st.write('Keine Daten vorhanden')


