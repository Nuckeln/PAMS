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
from Data_Class.SQL import read_table
import matplotlib.pyplot as plt
import hydralit_components as hc


class LIVE:
    @st.cache_data
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
                col1, col2, = st.columns([0.3, 0.4])
                with col2:
                    st.image(img_type, width=32,clamp=False)
                    hide_img_fs = '''
                    <style>
                    button[title="View fullscreen"]{
                        visibility: hidden;}
                    </style>
                    '''
                    st.markdown(hide_img_fs, unsafe_allow_html=True)
                with col1:
                    annotated_text(annotation(str(done_value),'', "#50af47", font_family="Montserrat"),'  / ',annotation(str(open_value),'', "#ef7d00", font_family="Montserrat"))

            if img_type == 'Mastercase':
                img_type = img_mastercase
                col1, col2 = st.columns([0.3, 0.4])
                with col2:
                    st.image(img_type, width=32)
                with col1:
                    annotated_text('',annotation(str(done_value),'', "#50af47", font_family="Montserrat"),'  / ',annotation(str(open_value),'', "#ef7d00", font_family="Montserrat"))
                  
            elif img_type == 'Pallet':
                img_type = img_pallet
                col1, col2 = st.columns([0.3, 0.4])
                with col2:
                    st.image(img_type, width=32)
                with col1:
                    #green
                    annotated_text('',annotation(str(done_value),'', "#50af47", font_family="Montserrat"),'  / ',annotation(str(open_value),'', "#ef7d00", font_family="Montserrat"))

            elif img_type == 'Delivery':
                img_type = img_Delivery
                col1, col2, = st.columns([0.3, 0.4])
                with col2:
                    st.image(img_type, width=32)
                with col1:
                    #green
                    annotated_text('',annotation(str(done_value),'', "#50af47", font_family="Montserrat"),'   / ',annotation(str(open_value),'', "#ef7d00", font_family="Montserrat"))
               
            elif img_type == 'Sum':
                img_type = icon_path_Sum
                col1, col2  = st.columns([0.3, 0.4])
                with col2:
                    st.image(img_type, width=32)
                with col1:
                    #green
                    annotated_text('',annotation(str(done_value),'', "#50af47", font_family="Montserrat"),'   / ',annotation(str(open_value),'', "#ef7d00", font_family="Montserrat"))
        
        
        cities = [("Gesamt", ""), ("Stuttgart", "KNSTR"), ("Leipzig", "KNLEJ"), ("Hannover", "KNHAJ"), ("Bielefeld", "KNBFE")]
        cols = st.columns(len(cities))
        
        for i, (city, depot) in enumerate(cities):
            with cols[i]:
                # st.markdown("""
                #     <style>
                #     @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@700&display=swap');
                #     </style>
                #     <h2 style='text-align: left; color: #0F2B63; font-family: Montserrat; font-weight: bold;'>{}</h2>
                #     """.format(city), unsafe_allow_html=True)   
                #Picks Gesamt of the Depot
                if city == "Gesamt":
                    sum_picks = df['Picks Gesamt'].sum()

                else:
                    sum_picks = df.loc[df['DeliveryDepot']==depot]['Picks Gesamt'].sum()

                



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
    
    # import datetime

    def hc_blocks(df, delivery_depot):
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
        
        current_datetime = datetime.datetime.now()
        sel_plannedDate = df['PlannedDate'].dt.date
        deadline = datetime.time(14, 0)  # Setzen Sie die Deadline auf 14:00 Uhr
        try:
            deadline = datetime.datetime.combine(sel_plannedDate.iloc[0], deadline)
            is_after_deadline = current_datetime > deadline
        except:
            is_after_deadline = False
        st.write(f"Deadline: {is_after_deadline}")

        #can apply customisation to almost all the properties of the card, including the progress bar
        theme_bad = {'bgcolor': '#FFF0F0','title_color': 'red','content_color': 'red','icon_color': 'red', 'icon': 'fa fa-times-circle'}
        theme_neutral = {'bgcolor': '#f9f9f9','title_color': 'orange','content_color': 'orange','icon_color': 'orange', 'icon': 'fa fa-question-circle'}
        theme_good = {'bgcolor': '#EFF8F7','title_color': 'green','content_color': 'green','icon_color': 'green', 'icon': 'fa fa-check-circle'}
            # filter df by depot

        def calPicks(df):
                    count_SAP_open = df[df['AllSSCCLabelsPrinted']==0]['SapOrderNumber'].nunique()
                    count_SAP_done = df[df['AllSSCCLabelsPrinted']==1]['SapOrderNumber'].nunique()
                    done__mastercase = df[df['AllSSCCLabelsPrinted']==0]['Picks Karton'].sum()       
                    done_outer = df[df['AllSSCCLabelsPrinted']==0]['Picks Stangen'].sum()
                    done_pallet = df[df['AllSSCCLabelsPrinted']==0]['Picks Paletten'].sum()                       
                    open_mastercase = df[df['AllSSCCLabelsPrinted']==1]['Picks Karton'].sum()
                    open_outer = df[df['AllSSCCLabelsPrinted']==1]['Picks Stangen'].sum()
                    open_pallet = df[df['AllSSCCLabelsPrinted']==1]['Picks Paletten'].sum()                     
                    sum_picks = df['Picks Gesamt'].sum()   
                    sum_done = df[df['AllSSCCLabelsPrinted']==1]['Picks Gesamt'].sum()    
                    return count_SAP_open, count_SAP_done, done__mastercase, done_outer, done_pallet, open_mastercase, open_outer, open_pallet, sum_picks, sum_done
        count_SAP_open, count_SAP_done, done__mastercase, done_outer, done_pallet, open_mastercase, open_outer, open_pallet, sum_pick,sum_done = calPicks(df)
        
        open_inPercent = round((sum_pick - sum_done) / sum_pick * 100, 2)
                
        if is_after_deadline == True:
            sel_theme = theme_bad
        else:
            sel_theme = theme_good

        
        #to int
        content = f'Karton 🔜 ✓: {sum_done.astype(str)} : {sum_pick - sum_done}' # need   

        
        card = hc.info_card(
            title=f'{sum_pick.astype(str)}',
            content= "",#content ,  # Fügen Sie hier ein Komma hinzu
            theme_override=sel_theme,
            bar_value=open_inPercent
        )
        card2 = hc.info_card(
            title='Stangen',
            content= content ,  # Fügen Sie hier ein Komma hinzu
            theme_override=sel_theme,
            bar_value=open_inPercent
        )
        
    
    def new_kennzahlen(df):
        
        def calPicks(df):
            count_SAP_open = df[df['AllSSCCLabelsPrinted']==0]['SapOrderNumber'].nunique()
            count_SAP_done = df[df['AllSSCCLabelsPrinted']==1]['SapOrderNumber'].nunique()
            done__mastercase = df[df['AllSSCCLabelsPrinted']==0]['Picks Karton'].sum()       
            done_outer = df[df['AllSSCCLabelsPrinted']==0]['Picks Stangen'].sum()
            done_pallet = df[df['AllSSCCLabelsPrinted']==0]['Picks Paletten'].sum()                       
            open_mastercase = df[df['AllSSCCLabelsPrinted']==1]['Picks Karton'].sum()
            open_outer = df[df['AllSSCCLabelsPrinted']==1]['Picks Stangen'].sum()
            open_pallet = df[df['AllSSCCLabelsPrinted']==1]['Picks Paletten'].sum()                    
            df_offen = df[df['AllSSCCLabelsPrinted']==0]['Picks Gesamt'].sum()
            df_fertig = df[df['AllSSCCLabelsPrinted']==1]['Picks Gesamt'].sum()   
            sum_picks = df['Picks Gesamt'].sum()   
            sum_done = df[df['AllSSCCLabelsPrinted']==1]['Picks Gesamt'].sum()    
            return count_SAP_open, count_SAP_done, done__mastercase, done_outer, done_pallet, open_mastercase, open_outer, open_pallet, df_offen, df_fertig, sum_picks, sum_done
        count_SAP_open, count_SAP_done, done__mastercase, done_outer, done_pallet, open_mastercase, open_outer, open_pallet, df_offen, df_fertig, sum_picks, sum_done = calPicks(df)
            
        icon_path_mastercase = 'Data/appData/ico/mastercase_favicon.ico'
        icon_path_outer = 'Data/appData/ico/favicon_outer.ico'
        icon_path_pallet = 'Data/appData/ico/pallet_favicon.ico'   
        icon_path_Delivery = 'Data/appData/ico/delivery-note.ico' 
                
        labels = ['Karton', 'Stangen', 'Paletten']

        def type_progress_png(progress, total, type: str):
            # Lade das Bild
            if type == 'Mastercase':
                img = Image.open(icon_path_mastercase)
            elif type == 'Outer':
                img = Image.open(icon_path_outer)
            elif type == 'Pallet':
                img = Image.open(icon_path_pallet)
            elif type == 'Delivery':
                img = Image.open(icon_path_Delivery)
            # Berechne den Prozentsatz des Fortschritts
            percentage = (progress / total) * 100

            # Erstelle eine Figur mit transparentem Hintergrund
            fig, ax = plt.subplots(figsize=(35, 11))
            fig.patch.set_alpha(0)

            # Erstelle die Fortschrittsleiste
            ax.barh([''], [percentage], color='#50af47')#50af47'
            ax.barh([''], [100-percentage], left=[percentage], color='#4D4D4D')

            # Setze Grenzen und Labels
            ax.set_xlim(0, 100)
            ax.set_xticks([])
            ax.set_yticks([])
            ax.set_frame_on(False)

            # Füge den Fortschrittstext hinzu
            plt.text(0, 0, f'{progress} von {total} ({percentage:.0f}%)', ha='left', va='center', color='white', fontsize=205, fontdict={'family': 'Montserrat', 'weight': 'bold'})

            # Konvertiere das Diagramm in ein NumPy-Array
            fig.canvas.draw()
            progress_bar_np = np.array(fig.canvas.renderer._renderer)
            plt.close()

            # Bestimme, wo die Fortschrittsleiste auf dem Bild platziert werden soll
            img_width, img_height = img.size
            bar_height = progress_bar_np.shape[0]
            bar_width = progress_bar_np.shape[1]
            x_offset = 160  # Setze diesen Wert auf 133, um den Balken bei Pixel 133 beginnen zu lassen
            y_offset = img_height - bar_height - (img_height // 4)

            # Füge die Fortschrittsleiste zum Bild hinzu
            final_img = img.copy()
            final_img.paste(Image.fromarray(progress_bar_np), (x_offset, y_offset), Image.fromarray(progress_bar_np))

            # Speichere das finale Bild
            return final_img
        img_truck = type_progress_png(done_pallet+open_pallet, done_pallet, 'Pallet')
        st.image(img_truck, use_column_width=True)
        
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

        # Erstelle Balkendiagramm
        fig = px.bar(dfAggregated, x='PlannedDate', y='Picks Gesamt', color='DeliveryDepot', barmode='group',
                    title='LKW Pro Depot', height=600, text='label')

        # Update trace colors
        colors = ['#0e2b63', '#004f9f', '#ef7d00', '#ffbb00']
        for color, depot in zip(colors, depots):
            fig.update_traces(marker_color=color, selector=dict(DeliveryDepot=depot))

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

    def figTachoDiagramm(df, delivery_depot):
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


        fig = go.Figure(go.Indicator(
            domain = {'x': [0, 1], 'y': [0, 1]},
            value = completion_rate,
            mode = "gauge+number+delta",
            title = {'text': f"{delivery_depot} Ziel (%)"},
            delta = {'reference': 100},
            number = {'suffix': "%"},
            gauge = {
                'axis': {
                    'range': [0, 100],
                    'tickangle': -90,
                    'tickvals': [],  # Keine Ticks anzeigen
                    'ticktext': []   # Keine Texte für Ticks anzeigen
                },
                'steps': [{'range': [0, 100], 'color': "#0F2B63"}],

            }
        ))
        
        # Text neben den Symbolen x recht y oben
        fig.add_annotation(x=0.5  , y=1.2, text=f"{sum_picks}", showarrow=False, font=dict(size=20))
        fig.add_annotation(x=0, y=-0.2, text=f"{done_All}", showarrow=False, font=dict(size=20))
        fig.add_annotation(x=1, y=-0.2, text=f"{open_ALL}", showarrow=False, font=dict(size=20))
        fig.update_layout(
        font_family="Montserrat", font_color="#0F2B63",
                        height=330)
        title = {
            'text': f"{delivery_depot}",
            # Stellen Sie sicher, dass der Titel-Text hier steht
            'y':0.9,  # Positionierung des Titels, kann angepasst werden
            'x':0.5,  # Zentriert den Titel, kann angepasst werden
            'xanchor': 'center',  # Sorgt dafür, dass der Titel zentriert ist
            'yanchor': 'top'  # Positioniert den Titel oben
        }
        fig.update_layout(title=title, showlegend=False, font_family="Montserrat", font_color="#0F2B63", title_font_family="Montserrat", title_font_color="#0F2B63", title_font_size=25)


        st.plotly_chart(fig, use_container_width=True,config={'displayModeBar': False})
        
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
            col1, col2,col3,col4 = st.columns([0.3,0.1,0.4,0.2])
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
    
            # if img_type == 'Mastercase':
            #     img_type = img_mastercase
            #     col1, col2 = st.columns([0.3, 0.4])
            #     with col2:
            #         st.image(img_type, width=32)
            #     with col1:
            #         annotated_text('',annotation(str(done_value),'', "#50af47", font_family="Montserrat"),'  / ',annotation(str(open_value),'', "#ef7d00", font_family="Montserrat"))
                  
            # elif img_type == 'Pallet':
            #     img_type = img_pallet
            #     col1, col2 = st.columns([0.3, 0.4])
            #     with col2:
            #         st.image(img_type, width=32)
            #     with col1:
            #         #green
            #         annotated_text('',annotation(str(done_value),'', "#50af47", font_family="Montserrat"),'  / ',annotation(str(open_value),'', "#ef7d00", font_family="Montserrat"))

            # elif img_type == 'Delivery':
            #     img_type = img_Delivery
            #     col1, col2, = st.columns([0.3, 0.4])
            #     with col2:
            #         st.image(img_type, width=32)
            #     with col1:
            #         #green
            #         annotated_text('',annotation(str(done_value),'', "#50af47", font_family="Montserrat"),'   / ',annotation(str(open_value),'', "#ef7d00", font_family="Montserrat"))
               
            # elif img_type == 'Sum':
            #     img_type = icon_path_Sum
            #     col1, col2  = st.columns([0.3, 0.4])
            #     with col2:
            #         st.image(img_type, width=32)
            #     with col1:
            #         #green
            #         annotated_text('',annotation(str(done_value),'', "#50af47", font_family="Montserrat"),'   / ',annotation(str(open_value),'', "#ef7d00", font_family="Montserrat"))
        
        masterCase_Outer_Pal_Icoons('Delivery' ,done_DN, open_DN)
        masterCase_Outer_Pal_Icoons('Outer' ,done_outer, open_outer)
        masterCase_Outer_Pal_Icoons('Mastercase' ,open_mastercase, done_mastercase)
        masterCase_Outer_Pal_Icoons('Pallet' ,open_pallet, done_pallet)
        
        

    def figUebermitteltInDeadline(df):        
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
        sar.st_autorefresh(interval=48000, debounce=True)
        colhead1, colhead2 ,colhead3, colhead4 = st.columns(4)
        with colhead2:
            lastUpdate = read_table('prod_KundenbestellungenUpdateTime')
            lastUpdateDate = lastUpdate['time'].iloc[0]
            st.write('Letztes Update:')
            st.write(lastUpdateDate)
        with colhead1:
            sel_date = datetime.date.today()  
            sel_date = st.date_input('Datum', sel_date)   
            dfOr = LIVE.loadDF(sel_date,sel_date) 
    
        with colhead4:                
            LIVE.wetter()
        img_strip = Image.open('Data/img/strip.png')   
        img_strip = img_strip.resize((1000, 15))     

        st.image(img_strip, use_column_width=True, caption='',)      
          

        col33 ,col34, col35, col36, col37 = st.columns(5)
        with col33:
            LIVE.figTachoDiagramm(dfOr,'Gesamt')
        with col34:
            LIVE.figTachoDiagramm(dfOr,'KNSTR')
        with col35:
            LIVE.figTachoDiagramm(dfOr,'KNLEJ')
        with col36:
            LIVE.figTachoDiagramm(dfOr,'KNBFE')
        with col37:
            LIVE.figTachoDiagramm(dfOr,'KNHAJ')
        #LIVE.columnsKennzahlen(dfOr)
        #st.write('Keine Daten vorhanden')
        try:
            with st.popover('Auftragsdetails in Timeline',help='Details zu den Aufträgen', use_container_width=True, ):
                    LIVE.timeline(dfOr)         
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
            st.write('Keine Daten vorhanden')
        try:
            LIVE.fig_trucks_Org(dfOr)
        except:
            LIVE.fig_trucks_Org(dfOr)
        try:
            LIVE.fig_Status_nach_Katergorie(dfOr)
        except:
            st.write('Keine Daten vorhanden')
        try:
            LIVE.figPicksBy_SAP_Order_CS_PAL(dfOr) 
        except:
            st.write('Keine Daten vorhanden')





