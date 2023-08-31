import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, DataReturnMode


class sel_DataFrameAG:


    def AG_Select_Grid(df: pd.DataFrame, height_value: int,keyname:str) -> str:
            '''
            Erstellt ein AG-Grid und gibt von der ausgewählten Zeile den wert aus der Row[1] als string.
            
            Arguments:
            df  – muss ein Datenframe sein
            
            hohe   – Bitte den wert festlegen wie hoch das Grid sein soll
            
            keyname     – Bitte einen eindeutigen Namen vergeben

            Returns:
            gibt ein str zurück
            '''

            # GridOptionsBuilder erstellen und Row-Selection aktivieren
            gob = GridOptionsBuilder.from_dataframe(df)
            gob.configure_selection('single', use_checkbox=False)
            grid_options = gob.build()
            #df drop index

            # AG-Grid in Streamlit erstellen
            response = AgGrid(
                df,
                gridOptions=grid_options,
                height=height_value,
                width='100%',
                data_return_mode=DataReturnMode.AS_INPUT,
                update_mode=GridUpdateMode.MODEL_CHANGED,
                fit_columns_on_grid_load=True,
                allow_unsafe_jscode=True,
                key=keyname,
            )
            #hide index


            # Wert aus Spalte 0 der ausgewählten Zeile ausgeben
            if response['selected_rows']:
                selected_row = response['selected_rows'][0]
                col_name = df.columns[3]  # Name der Spalte 0
                return (f"{selected_row[col_name]}")

        # Hauptfunktion