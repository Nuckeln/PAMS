import streamlit as st
import pandas as pd

class Int_to_Textbox:

    def erst_Textb_int(anzahl_boxen: int, label: str, text: str, key: str):
        '''Erstellt eine Textbox mit einem Label und einem Key anhand der Anzahl der Boxen
        Arguments:
        anzahl_boxen  – Anzahl der Textboxen
        label   – Label der Textbox
        text     – Inhalte der Textbox werden bei einem ; getrennt z.B. "Text1;Text2;Text3"
        key     – Key der Textbox
        Returns:
        Gibt eine Liste mit den Werten der Textboxen zurück
        '''
        # Split the comma-separated string into a list
        input_list = text.split(';')

        # Fill up the input list with empty strings if necessary
        input_list += [''] * (anzahl_boxen - len(input_list))

        entry_values = []
        for i in range(anzahl_boxen):
            # Add the index to the label and key to make them unique
            unique_label = label +" "+ str(i + 1) + ':'
            unique_key = key + str(i + 1)
            value = st.text_input(unique_label, key=unique_key, value=input_list[i])
            entry_values.append(value)

        return entry_values


                        
    # def checkboxes_in_Col(df,cols:int,key):

    #     input_list = df[cols].unique().tolist()
    #     input_list.sort()
    #     entry_values = []
    #     for i in range(len(input_list)):
    #         unique_label = input_list[i]
    #         unique_key = key + str(i + 1)
    #         value = st.checkbox(unique_label, key=unique_key)
    #         entry_values.append(value)
    #     return entry_values

                        

    def checkboxes_in_Col(df, cols,select_all, key):
        '''Erstellt Checkboxen mit einem Label und einem Key anhand der Anzahl der rows in der Spalte
        Arguments:
        df  – Dataframe
        cols   – Welche der Spalten des Dataframes soll angezeigt werden
        key     – Key der Checkbox
        select_all – Boolean (TRUE/FALSE) ob alle Checkboxen ausgewählt werden sollen 
        Returns:
        Gibt eine Liste mit den Werten der Checkboxen zurück
        '''
        # prüfe ob df eine Liste oder DataFrame ist
        if type(df) == list:
            df = pd.DataFrame(df)
            # column name = cols
        input_list = df[cols].unique().tolist()
        
        input_list_count = len(input_list) // 4  # Anzahl der Elemente in jeder Spalte

        # round up if the division is not exact
        if len(input_list) % 4 != 0:
            input_list_count += 1

        col1, col2, col3, col4 = st.columns(4)

        columns = [col1, col2, col3, col4]  # Liste der Spalten

        # st.write(f"Total unique items: {len(input_list)}")
        # st.write(f"Items per column: {input_list_count}")

        #select_all = st.button("Alles auswählen")

        input_list.sort()
        
        selected_labels = []  # Array zum Speichern der Labels der ausgewählten Checkboxen

        for i in range(len(input_list)):
            unique_label = input_list[i]
            unique_key = key + str(i + 1)
            
            # Wähle die entsprechende Spalte aus
            current_col = columns[i // input_list_count]
            
            # Setze den Wert der Checkbox basierend auf dem "Alles auswählen" Button
            default_value = select_all
            
            # Erstelle die Checkbox in der aktuellen Spalte
            value = current_col.checkbox(unique_label, value=default_value, key=unique_key)
            
            # Wenn die Checkbox ausgewählt ist, füge ihr Label dem selected_labels Array hinzu
            if value:
                selected_labels.append(unique_label)

        return selected_labels  # Rückgabe der ausgewählten Labels
