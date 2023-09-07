import streamlit as st



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


                    
def checkboxes_in_Col(df,cols:int,key):

    input_list = df[cols].unique().tolist()
    input_list.sort()
    entry_values = []
    for i in range(len(input_list)):
        unique_label = input_list[i]
        unique_key = key + str(i + 1)
        value = st.checkbox(unique_label, key=unique_key)
        entry_values.append(value)
    return entry_values