# Python Module
import streamlit as st
from streamlit_option_menu import option_menu # pip install streamlit-option-menu # CSS Style für Main Menu # https://icons.getbootstrap.com
import pandas as pd #Pip install pandas
import plotly_express as px #pip install plotly_expression
from P_Fehlverladungen import fehlverladungAnzeigen
#Eigene Klassen


# Zum Ausführen
#     streamlit run "/Users/martinwolf/Python/Superdepot Reporting/Test/App.py"

st.set_page_config(layout="wide", page_title="SuperDepot", page_icon=":bar_chart:")

fehlverladungAnzeigen()
#fehlverladungErfassen()



# def MitarbeiterPflegen(self):
#     dfMitarbeiter = pd.read_feather('/Users/martinwolf/Python/Superdepot Reporting/data/user.feather') 
#     with st.expander("Mitarbeiter Anlegen"):
#         with st.form(key='my_form', clear_on_submit=True):
#             col1, col2 = st.columns(2)
#             with col1:
#                 #id = dfMitarbeiter.index.max() + 1       
#                 name = st.text_input("Name",key='name')
#                 oneid = st.text_input("One ID",key='oneId')
#             with col2:
#                 funktion = st.selectbox('Funktion',["Operativ",'Administration','Management'],key='funktion')
#                 firma = st.selectbox("Unternehmen", ['BAT', 'LOG-IN'], key='firma')
#                 fachbereich = st.selectbox("Fachbereich", ['Super-Depot'],  key='fachbereich')
            
#             speichern = st.form_submit_button("Speichern")  
#             if speichern:
#                 #check user input  
#                 if name == "":
#                     st.error("Bitte Name eingeben")
#                 elif oneid == "":
#                     st.error("Bitte One ID eingeben")
#                 else:
#                     oneid = int(oneid)
#                     dfMitarbeiter = dfMitarbeiter.append({'Name':name,'One ID':oneid,'Funktion':funktion,'Unternehmen':firma,'Fachbereich':fachbereich},ignore_index=True)
#                     dfMitarbeiter.to_feather('/Users/martinwolf/Python/Superdepot Reporting/data/user.feather')
#                     st.success("Mitarbeiter wurde angelegt")

#     with st.expander("Mitarbeiter Löschen"):
#         with st.form(key='my_form2', clear_on_submit=True):
#             selMitarbeiter = st.selectbox("Mitarbeiter", dfMitarbeiter['Name'],key='selMitarbeiter')
#             löschen = st.form_submit_button("Löschen")
#             if löschen:
#                     dfMitarbeiter = dfMitarbeiter[dfMitarbeiter['Name'] != selMitarbeiter]
#                     dfMitarbeiter = dfMitarbeiter.reset_index(drop=True)
#                     dfMitarbeiter.to_feather('/Users/martinwolf/Python/Superdepot Reporting/data/user.feather')
            
#                 #st.experimental_rerun()
#     st.dataframe(dfMitarbeiter, use_container_width=True)
 




            
        
        # dfMiarbeiter = dfMiarbeiter.append({'MitarbeiterID': mitarbeiterID, 'MitarbeiterName': mitarbeiterName, 'MitarbeiterVorname': mitarbeiterVorname, 'MitarbeiterEmail': mitarbeiterEmail}, ignore_index=True)
        # dfMiarbeiter.to_feather('/Users/martinwolf/Python/Superdepot Reporting/data/user.feather')
        # st.write('Mitarbeiter angelegt')



# ----- Login -----
# if selected2 == "Live Status":
#     df = LoadData()
#     #df.index to date
#     df['Datum'] = pd.to_datetime(df.index)
#     st.dataframe(df)
#     fig = px.bar(df, x='Datum', y="Picks Gesamt", barmode="group")
#     st.plotly_chart(fig)
# elif selected2 == "Lagerbewegungen":
    #mitarbeiterAnlegen()



