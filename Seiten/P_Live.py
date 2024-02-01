import streamlit as st
import pandas as pd
import numpy as np
import datetime
import streamlit_autorefresh as sar
from PIL import Image
import plotly_express as px
import plotly.graph_objects as go
from annotated_text import annotated_text, annotation

from Data_Class.wetter.api import getWetterBayreuth
from Data_Class.SQL import read_table
import matplotlib.pyplot as plt




class LIVE:
    
    def loadDF(day1=None, day2=None): 
        dfOr = read_table('prod_Kundenbestellungen_14days')
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
            # ...

            if img_type == 'Outer':
                img_type = img_outer
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.image(img_type, width=32,clamp=True)
                with col2:
                    #green
                    annotated_text('',annotation(str(done_value),'', "#50af47", font_family="Montserrat"),'   / ')
                with col3:
                    #red
                    annotated_text(annotation(str(open_value),'', "#ef7d00", font_family="Montserrat"),'')
            if img_type == 'Mastercase':
                img_type = img_mastercase
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.image(img_type, width=32)
                with col2:
                    #green
                    annotated_text('',annotation(str(done_value),'', "#50af47", font_family="Montserrat"),'   / ')
                with col3:
                    #red
                    annotated_text(annotation(str(open_value),'', "#ef7d00", font_family="Montserrat"),'')                    
            elif img_type == 'Pallet':
                img_type = img_pallet
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.image(img_type, width=32)
                with col2:
                    #green
                    annotated_text('',annotation(str(done_value),'', "#50af47", font_family="Montserrat"),'   / ')
                with col3:
                    #red
                    annotated_text(annotation(str(open_value),'', "#ef7d00", font_family="Montserrat"),'')
            elif img_type == 'Delivery':
                img_type = img_Delivery
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.image(img_type, width=32)
                with col2:
                    #green
                    annotated_text('',annotation(str(done_value),'', "#50af47", font_family="Montserrat"),'   / ')
                with col3:
                    #red
                    annotated_text(annotation(str(open_value),'', "#ef7d00", font_family="Montserrat"),'')
            elif img_type == 'Sum':
                img_type = icon_path_Sum
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.image(img_type, width=32)
                with col2:
                    #green
                    annotated_text('',annotation(str(done_value),'', "#50af47", font_family="Montserrat"),'   / ')
                with col3:
                    #red
                    annotated_text('',annotation(str(open_value),'', "#ef7d00", font_family="Montserrat"),'')
        st.write('Mengen in Picks nach Kategorie:')    
        cities = [("Gesamt", ""), ("Stuttgart", "KNSTR"), ("Leipzig", "KNLEJ"), ("Hannover", "KNHAJ"), ("Bielefeld", "KNBFE")]
        cols = st.columns(len(cities))
        
        for i, (city, depot) in enumerate(cities):
            with cols[i]:
                st.markdown("""
                    <style>
                    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@700&display=swap');
                    </style>
                    <h1 style='text-align: center; color: #0F2B63; font-family: Montserrat; font-weight: bold;'>{}</h1>
                    """.format(city), unsafe_allow_html=True)    
        cols = st.columns(len(cities))  # Erstellen Sie eine Spalte für jedes Depot
        for i, (city, depot) in enumerate(cities):
            with cols[i]:
                if city == "Gesamt":
                    
                    picks = df
            
                    count_SAP_open = picks[picks['AllSSCCLabelsPrinted']==0]['SapOrderNumber'].nunique()
                    count_SAP_done = picks[picks['AllSSCCLabelsPrinted']==1]['SapOrderNumber'].nunique()
                    
                    done__mastercase = picks[picks['AllSSCCLabelsPrinted']==0]['Picks Karton'].sum()       
                    done_outer = picks[picks['AllSSCCLabelsPrinted']==0]['Picks Stangen'].sum()
                    done_pallet = picks[picks['AllSSCCLabelsPrinted']==0]['Picks Paletten'].sum()              
                                       
                    open_mastercase = picks[picks['AllSSCCLabelsPrinted']==1]['Picks Karton'].sum()
                    open_outer = picks[picks['AllSSCCLabelsPrinted']==1]['Picks Stangen'].sum()
                    open_pallet = picks[picks['AllSSCCLabelsPrinted']==1]['Picks Paletten'].sum()      
                    picks_offen = picks[picks['AllSSCCLabelsPrinted']==0]['Picks Gesamt'].sum()
                    picks_fertig = picks[picks['AllSSCCLabelsPrinted']==1]['Picks Gesamt'].sum()              

                    masterCase_Outer_Pal_Icoons('Delivery' ,count_SAP_done, count_SAP_open)
                    masterCase_Outer_Pal_Icoons('Outer' ,open_outer, done_outer) 
                    masterCase_Outer_Pal_Icoons('Mastercase' ,open_mastercase, done__mastercase) 
                    masterCase_Outer_Pal_Icoons('Pallet' ,open_pallet, done_pallet)
                    masterCase_Outer_Pal_Icoons('Sum' ,picks_fertig, picks_offen)
                else:
                    picks = df.loc[df['DeliveryDepot']==depot]
            
                    count_SAP_open = picks[picks['AllSSCCLabelsPrinted']==0]['SapOrderNumber'].nunique()
                    count_SAP_done = picks[picks['AllSSCCLabelsPrinted']==1]['SapOrderNumber'].nunique()
                                        
        
                    done__mastercase = picks[picks['AllSSCCLabelsPrinted']==0]['Picks Karton'].sum()       
                    done_outer = picks[picks['AllSSCCLabelsPrinted']==0]['Picks Stangen'].sum()
                    done_pallet = picks[picks['AllSSCCLabelsPrinted']==0]['Picks Paletten'].sum()              
                                       
                    open_mastercase = picks[picks['AllSSCCLabelsPrinted']==1]['Picks Karton'].sum()
                    open_outer = picks[picks['AllSSCCLabelsPrinted']==1]['Picks Stangen'].sum()
                    open_pallet = picks[picks['AllSSCCLabelsPrinted']==1]['Picks Paletten'].sum()                    
                    picks_offen = picks[picks['AllSSCCLabelsPrinted']==0]['Picks Gesamt'].sum()
                    picks_fertig = picks[picks['AllSSCCLabelsPrinted']==1]['Picks Gesamt'].sum()              

                    masterCase_Outer_Pal_Icoons('Delivery' ,count_SAP_done, count_SAP_open)
                    masterCase_Outer_Pal_Icoons('Outer' ,open_outer, done_outer ) 
                    masterCase_Outer_Pal_Icoons('Mastercase' ,open_mastercase, done__mastercase) 
                    masterCase_Outer_Pal_Icoons('Pallet' ,open_pallet, done_pallet)
                    masterCase_Outer_Pal_Icoons('Sum' ,picks_fertig, picks_offen)
    

        cols = st.columns(len(cities))  # Erstellen Sie eine Spalte für jedes Depot

                


            
    ## Plotly Charts ###
    def Test2(df):
        sum_karton_offen = df['Picks Karton offen'].sum()
        sum_paletten_offen = df['Picks Paletten offen'].sum()
        sum_stangen_offen = df['Picks Stangen offen'].sum()

        sum_karton_fertig = df['Picks Karton fertig'].sum()
        sum_paletten_fertig = df['Picks Paletten fertig'].sum()
        sum_stangen_fertig = df['Picks Stangen fertig'].sum()

        total_offen = sum_karton_offen + sum_paletten_offen + sum_stangen_offen
        total_fertig = sum_karton_fertig + sum_paletten_fertig + sum_stangen_fertig

        categories = ['Karton', 'Paletten', 'Stangen']

        # Calculate the total for the entire bar (should be 100%)
        total_bar = total_offen + total_fertig

        # Calculate the percentages for each category
        percent_karton_offen = (sum_karton_offen / total_bar) * 100 if total_bar != 0 else 0
        percent_paletten_offen = (sum_paletten_offen / total_bar) * 100 if total_bar != 0 else 0
        percent_stangen_offen = (sum_stangen_offen / total_bar) * 100 if total_bar != 0 else 0

        percent_karton_fertig = (sum_karton_fertig / total_bar) * 100 if total_bar != 0 else 0
        percent_paletten_fertig = (sum_paletten_fertig / total_bar) * 100 if total_bar != 0 else 0
        percent_stangen_fertig = (sum_stangen_fertig / total_bar) * 100 if total_bar != 0 else 0

        # Prepare the data in a way that allows stacking in the horizontal bar chart
        cumulative_fertig = np.cumsum([0, percent_karton_fertig, percent_paletten_fertig, percent_stangen_fertig])
        cumulative_offen = cumulative_fertig[-1] + np.cumsum([0, percent_karton_offen, percent_paletten_offen, percent_stangen_offen])

        # Define custom colors based on user input
        colors_fertig = ['#4FAF46', '#4FAF46', '#4FAF46']
        colors_offen = ['#ef7d00', '#ef7d00', '#ef7d00']

        # Create the horizontal bar chart
        plt.figure(figsize=(14, 2))

        # Schwarzen Trennbalken hinzufügen
        # black_bar_width = 20  # Breite in Prozent
        # plt.barh('Total', black_bar_width, left=cumulative_fertig[-1], color='black')
    



        # Add bars and labels for 'Fertig' categories with custom colors
        for i, category in enumerate(categories):
            plt.barh('Total', cumulative_fertig[i+1] - cumulative_fertig[i], left=cumulative_fertig[i], color=colors_fertig[i])
            plt.text(
                cumulative_fertig[i] + (cumulative_fertig[i+1] - cumulative_fertig[i]) / 2, 
                0, 
                f"{category}\n{cumulative_fertig[i+1] - cumulative_fertig[i]:.2f}%\n({int(cumulative_fertig[i+1]*total_bar/100)})",
                va='center', 
                ha='center', 
                color='white'
            )

        # Add bars and labels for 'Offen' categories with custom colors
        for i, category in enumerate(categories):
            plt.barh('Total', cumulative_offen[i+1] - cumulative_offen[i], left=cumulative_offen[i], color=colors_offen[i])
            plt.text(
                cumulative_offen[i] + (cumulative_offen[i+1] - cumulative_offen[i]) / 2, 
                0, 
                f"{category}\n{cumulative_offen[i+1] - cumulative_offen[i]:.2f}%\n({int(cumulative_offen[i+1]*total_bar/100)})",
                va='center', 
                ha='center', 
                color='white'
            )

        # Add titles and labels
        plt.title('Anteil der Fertigen und Offenen Werte (100% Balken)')
        plt.xlabel('Anteil (%)')
        plt.yticks([])  # Hide y-ticks as they are not needed

        plt.show()


# Add titles 

        fig = plt.gcf()
        st.pyplot(fig)

    def fig_Status_nach_Katergorie(df):
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
            figPicksBySAPOrder.update_yaxes(ticktext=['Fertig','Offen'])
            figPicksBySAPOrder.update_yaxes(tickvals=[0,1])
            figPicksBySAPOrder.update_xaxes(showticklabels=False)
            figPicksBySAPOrder.update_yaxes(title_text='')
            figPicksBySAPOrder.update_xaxes(title_text='')

            st.plotly_chart(figPicksBySAPOrder,use_container_width=True,config={'displayModeBar': False})


    def figPicksKunde(df):
        df = df.groupby(['PartnerName', 'SapOrderNumber', "AllSSCCLabelsPrinted", 'DeliveryDepot', 'Fertiggestellt']).agg({'Picks Gesamt': 'sum'}).reset_index()
        df = df.sort_values(by=['Picks Gesamt', 'AllSSCCLabelsPrinted'], ascending=False)
        
        # HTML-formatted title with different word colors
        title = "<b>Kundenübersicht nach Status:</b> <span style='color:#E72482'>Offen</span> / <span style='color:#4FAF46'>Fertig</span>"
        figTagKunden = px.bar(df, x="PartnerName", y="Picks Gesamt", title=title, hover_data=['Picks Gesamt', 'SapOrderNumber', 'Fertiggestellt'], color='Picks Gesamt', height=900)
        
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
        st.plotly_chart(fig,use_container_width=True,use_container_height=True,sharing='streamlit',config={'displayModeBar': False})

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

            st.plotly_chart(fig,use_container_width=True,config={'displayModeBar': False})

    def figTachoDiagrammPicksStrHannover(df):
        df1 = df[df['AllSSCCLabelsPrinted']==0]
        offenHan = df1.loc[df1["DeliveryDepot"] == "KNHAJ"]["Picks Gesamt"].sum()

        df2 = df[df['AllSSCCLabelsPrinted']==1]
        fertigHan = df2.loc[df2["DeliveryDepot"] == "KNHAJ"]["Picks Gesamt"].sum()

        data = {'Offen': [offenHan],
                'Fertig': [fertigHan]}
        df = pd.DataFrame(data, index=['Hannover'])

        # Berechnen Sie den Prozentsatz der abgeschlossenen Lieferungen
        completion_rate = (fertigHan / (fertigHan + offenHan)) * 100

        fig = go.Figure(go.Indicator(
            domain = {'x': [0, 1], 'y': [0, 1]},
            value = completion_rate,
            mode = "gauge+number+delta",
            title = {'text': "Hannover Ziel (%)"},
            delta = {'reference': 100,'increasing': {'color': "#4FAF46"}},
            gauge = {'axis': {'range': [0, 100], 'tickangle': -90},
                    'steps' : [
                        {'range': [0, 100], 'color': "#0F2B63"},
                        ],

                    'threshold' : {'line': {'color': "#E72482", 'width': 4}, 'thickness': 0.75, 'value': 100}}))
        fig.update_traces(number_suffix=" %")
        fig.update_traces(delta_suffix=" %")
        fig.update_layout(font_family="Montserrat",font_color="#0F2B63",title_font_family="Montserrat",title_font_color="#0F2B63")
        fig.update_layout(uniformtext_minsize=10, uniformtext_mode='hide',showlegend=False)
        fig.update_layout(title_text='')
        fig.update_xaxes(title_text='')
        fig.update_yaxes(title_text='')
        fig.layout.xaxis.tickangle = 70

        st.plotly_chart(fig,use_container_width=True,config={'displayModeBar': False})

    def figTachoDiagrammPicksStrKNBFE(df):
        df1 = df[df['AllSSCCLabelsPrinted']==0]
        offenKNBFE = df1.loc[df1["DeliveryDepot"] == "KNBFE"]["Picks Gesamt"].sum()

        df2 = df[df['AllSSCCLabelsPrinted']==1]
        fertigKNBFE = df2.loc[df2["DeliveryDepot"] == "KNBFE"]["Picks Gesamt"].sum()

        data = {'Offen': [offenKNBFE],
                'Fertig': [fertigKNBFE]}
        df = pd.DataFrame(data, index=['KNBFE'])

        # Berechnen Sie den Prozentsatz der abgeschlossenen Lieferungen
        completion_rate = (fertigKNBFE / (fertigKNBFE + offenKNBFE)) * 100

        fig = go.Figure(go.Indicator(
            domain = {'x': [0, 1], 'y': [0, 1]},
            value = completion_rate,
            mode = "gauge+number+delta",
            title = {'text': "Bielefeld Ziel (%)"},
            delta = {'reference': 100,'increasing': {'color': "#4FAF46"}},
            gauge = {'axis': {'range': [0, 100], 'tickangle': -90},
                    'steps' : [
                        {'range': [0, 100], 'color': "#0F2B63"},
                        ],

                    'threshold' : {'line': {'color': "#E72482", 'width': 4}, 'thickness': 0.75, 'value': 100}}))
        fig.update_traces(number_suffix=" %")
        fig.update_traces(delta_suffix=" %")
        fig.update_layout(font_family="Montserrat",font_color="#0F2B63",title_font_family="Montserrat",title_font_color="#0F2B63")
        fig.update_layout(uniformtext_minsize=10, uniformtext_mode='hide',showlegend=False)
        fig.update_layout(title_text='')
        fig.update_xaxes(title_text='')
        fig.update_yaxes(title_text='')
        fig.layout.xaxis.tickangle = 70

        st.plotly_chart(fig,use_container_width=True,config={'displayModeBar': False})

    def figUebermitteltInDeadline(df):        
        sel_deadStr = '14:00:00'
        sel_deadLej = '14:00:00'

        #add deadlines to df by DeliveryDepot
        df['Deadline'] = np.where(df['DeliveryDepot'] == 'KNLEJ', sel_deadStr, sel_deadLej)
        df['PlannedDate'] = df['PlannedDate'] + pd.to_timedelta(df['Deadline'])
        #convert to datetime
        df['PlannedDate'] = pd.to_datetime(df['PlannedDate'])
        # filter by fertiggestellt = '0'
        dfOffen = df[df['Fertiggestellt'] == '0']
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

   ## AG-Grid Func ###

    def tabelleAnzeigen(df):
        #new df with only the columns we need 'PlannedDate' ,'SapOrderNumber','PartnerName']#'Fertiggestellt','Picks Gesamt','Picks Karton','Picks Paletten','Picks Stangen','Lieferschein erhalten','Fertiggestellt'
        dfAG = df[['PlannedDate','DeliveryDepot' ,'SapOrderNumber','PartnerName','Fertiggestellt','Fertige Paletten','Picks Gesamt','Lieferschein erhalten']]


        st.data_editor(data=dfAG, use_container_width=True)
    
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

    #######------------------Main------------------########

    def PageTagesReport():
        pd.set_option("display.precision", 2)
        sar.st_autorefresh(interval=48000)
        colhead1, colhead2 ,colhead3, colhead4 = st.columns(4)
        with colhead3:
            lastUpdate = read_table('prod_KundenbestellungenUpdateTime')
            lastUpdateDate = lastUpdate['time'].iloc[0]
            st.write('Letztes Update:')
            st.write(lastUpdateDate)
        with colhead1:
            sel_date = datetime.date.today()  
            sel_date = st.date_input('Datum', sel_date)   
            dfOr = LIVE.loadDF(sel_date,sel_date) 

        with colhead2:
            sel = st.multiselect('Depot  ', ['KNSTR','KNLEJ'],['KNSTR','KNLEJ'],key='choise Depot')
            dfOr = dfOr[dfOr['DeliveryDepot'].isin(sel)]
            
        with colhead4:                
            LIVE.wetter()
        img_strip = Image.open('Data/img/strip.png')   
        img_strip = img_strip.resize((1000, 15))     

        st.image(img_strip, use_column_width=True, caption='',)     
        LIVE.columnsKennzahlen(dfOr)
    
        try:
            col34, col35, col36, col37 = st.columns(4)
            with col34:
                LIVE.figTachoDiagrammPicksStr(dfOr)
            with col35:
                LIVE.figTachoDiagrammPicksLei(dfOr)
                
            with col36:
                LIVE.figTachoDiagrammPicksStrHannover(dfOr)
            with col37:
                LIVE.figTachoDiagrammPicksStrKNBFE(dfOr)
        except:
            st.write('Keine Daten vorhanden')

        try:
            LIVE.fig_Status_nach_Katergorie(dfOr)
        except:
            st.write('Keine Daten vorhanden')

        try:
            LIVE.figPicksKunde(dfOr)
        except:
            st.write('Keine Daten vorhanden')

        try:
            LIVE.figPicksBy_SAP_Order_CS_PAL(dfOr) 
        except:
            st.write('Keine Daten vorhanden')

        try:    
            LIVE.figUebermitteltInDeadline(dfOr)
        except:
            st.write('Keine Daten vorhanden, schreibweise beachtet?')
        LIVE.downLoadTagesReport(dfOr)
        LIVE.tabelleAnzeigen(dfOr)
        #save df to csv
        dfOr.to_csv('df.csv', index=False)



