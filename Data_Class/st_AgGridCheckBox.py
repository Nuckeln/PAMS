import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, DataReturnMode
import uuid



def createAGgrid_withCheckbox(df:pd.DataFrame,hoehe:int,keyname:str):
    '''
    Erstellt ein AG-Grid mit Checkboxen und gibt die ausgewählten Zeilen als JSON zurück.
    
    Arguments:
    df  – muss ein Datenframe sein
    
    hohe   – Bitte den wert festlegen wie hoch das Grid sein soll
    
    keyname     – Bitte einen eindeutigen Namen vergeben

    Returns:
    gibt ein JSON zurück

    Kann so in ein Arry gepackt werden 

    ret_value = AGGridCheckBox.createAGgrid_withCheckbox(df)
    transportnummern = []
    for item in ret_value:
        transportnummern.append(item['Transportnummer'])
    '''
    df['Auswahl'] = False

    column_defs = [
        {
            'field': 'Auswahl',
            'checkboxSelection': True,
            'headerCheckboxSelection': True,
            'width': 75,
            'cellRenderer': """
                function(params) {
                    var input = document.createElement('input');
                    input.type = 'checkbox';
                    input.checked = params.value;
                    input.addEventListener('change', function() {
                        params.node.setDataValue(params.colDef.field, this.checked);
                        params.api.dispatchEvent({type: 'cellValueChanged', api: params.api, node: params.node, data: params.data, column: params.column, colDef: params.colDef, newValue: this.checked});
                    });
                    return input;
                }
            """,
        }
    ]

    for col in df.columns:
        if col != 'Auswahl':
            column_defs.append({'field': col})

    gob = GridOptionsBuilder.from_dataframe(df)
    grid_options = gob.build()
    grid_options['columnDefs'] = column_defs
    grid_options['rowSelection'] = 'multiple'
    grid_options['enableCellChangeFlash'] = True

    response = {}

    response.update(AgGrid(
        df,
        gridOptions=grid_options,
        height=hoehe,
        width='100%',
        fit_columns_on_grid_load=True,
            data_return_mode=DataReturnMode.AS_INPUT,
            update_mode=GridUpdateMode.MODEL_CHANGED,
        key='grid',
    ))  
    #drop auswahl
    return response.get('selected_rows')
