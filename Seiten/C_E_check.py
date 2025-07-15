from pandas.testing import assert_frame_equal
import pandas as pd
import numpy as np
from PIL import Image
import re
import streamlit as st
import json
import uuid
from Data_Class.MMSQL_connection import read_Table, save_Table_append, save_Table
import hydralit_components as hc

import chardet
import streamlit as st
import io


@st.dialog("ACHTUNG")
def vote(item):
    st.error(f"Achtung Mengenfehler!!")


def check_upload(df_sap:pd.DataFrame, df_dbh: pd.DataFrame, check_aktive:bool = True):
    '''Diese Funktion prüft ob die Spaltennamen und dtypes der neuen Dateien mit den alten übereinstimmen
    Args:
    df_sap: pd.DataFrame
    df_dbh: pd.DataFrame
    check_aktive: bool
    Rerturns exceptions if the columns and dtypes are not the same
    Returns:
    df_sap: pd.DataFrame
    df_dbh: pd.DataFrame '''
    if check_aktive:
        
        with open('Data/appData/check_uploads/C_E_check_data_upload.json', 'r') as f:
            data = json.load(f)

        # prüfe ob die Spaltennamen und dtypes der neuen Dateien mit den alten übereinstimmen
        sap_cols = df_sap.columns.tolist()
        dbh_cols = df_dbh.columns.tolist()
        sap_dtypes = df_sap.dtypes.astype(str).tolist()
        dbh_dtypes = df_dbh.dtypes.astype(str).tolist()

        # Ermittle die Unterschiede
        diff_sap_cols = list(set(data['sap']) - set(sap_cols))
        diff_dbh_cols = list(set(data['dbh']) - set(dbh_cols))
        diff_sap_dtypes = [i for i, j in zip(data['sap_dtypes'], sap_dtypes) if i != j]
        diff_dbh_dtypes = [i for i, j in zip(data['dbh_dtypes'], dbh_dtypes) if i != j]

        if diff_sap_cols or diff_dbh_cols or diff_sap_dtypes or diff_dbh_dtypes:
            st.warning('Die Spaltennamen und dtypes stimmen nicht mit den alten überein')
            if diff_sap_cols:
                st.warning(f'Unterschiedliche Spalten in SAP:{diff_sap_cols}')
            if diff_dbh_cols:
                st.warning(f'Unterschiedliche Spalten in DBH:{diff_dbh_cols}')
            if diff_sap_dtypes:
                st.warning(f'Unterschiedliche dtypes in SAP:{diff_sap_dtypes}')
            if diff_dbh_dtypes:
                st.warning(f'Unterschiedliche dtypes in DBH:{diff_dbh_dtypes}')
        else:
            return df_sap, df_dbh
    else:
        return df_sap, df_dbh        

def normalize_number(value):
    if isinstance(value, str):
        # Entfernen Sie Tausendertrennzeichen und ersetzen Sie Komma durch Punkt
        return float(value.replace('.', '').replace(',', '.'))
    return value

def detaillierte_datenprüfung(df_sap, df_dbh, round_on:bool = True):
#def detaillierte_datenprüfung(df_sap, df_dbh, round_on):
    df_dbh['Rohmasse'] = pd.to_numeric(df_dbh['Rohmasse'], errors='coerce')
    df_sap['Gross Weight'] = pd.to_numeric(df_sap['Gross Weight'], errors='coerce')
    with st.expander('Inhalt der Dokumente anzeigen', expanded=False):
        st.dataframe(df_sap)
        st.dataframe(df_dbh)
    dn_sap = df_sap['Delivery Number'].tolist()
    #entferne duplikate
    dn_sap = list(dict.fromkeys(dn_sap))
    # Konvertiere die Spalte 'Vorgangsnummer' in einen String
    #df
    #df_dbh['Vorgangsnummer'] = df_dbh['Vorgangsnummer'].astype(str)
    df_dbh['Bezugsnummer'] = df_dbh['Bezugsnummer'].astype(str)
    # Erstelle einen regulären Ausdruck, um 10-stellige Zahlen zu finden
    regex = r'(\d{10})'
    # Erstelle eine leere Liste, um die gefundenen Zahlen zu speichern
    dn_DBH_list = []
    # Durchlaufe jede Zeile in der Spalte 'Vorgangsnummer'
    for vorgangsnummer in df_dbh['Bezugsnummer']:
        # Finde alle Übereinstimmungen des regulären Ausdrucks in der aktuellen Zeile
        matches = re.findall(regex, vorgangsnummer)
        # Füge die gefundenen Zahlen zur Liste hinzu
        dn_DBH_list.extend(matches)
    # Entferne Duplikate
    dn_DBH_list = list(dict.fromkeys(dn_DBH_list))
    # both to int
    dn_sap = [int(i) for i in dn_sap]
    dn_DBH_list = [int(i) for i in dn_DBH_list]
    missing_dn = [dn for dn in dn_sap if dn not in dn_DBH_list]
    # aggriegere dfdbh nach Warennummer und summiere  Menge , Rohmasse , Eigenmasse
    df_dbh_agg = df_dbh.groupby('Warennummer').agg({'Menge':'sum','Rohmasse':'sum','Eigenmasse':'sum'}).reset_index()
    # first 8 digts of df_sap['Commodity Code']
    df_sap['Commodity Code'] = df_sap['Commodity Code'].astype(str)
    df_sap['Commodity Code'] = df_sap['Commodity Code'].str[:8]
    #to int
    df_sap['Commodity Code'] = df_sap['Commodity Code'].astype(int)
    # Aggregiere df_sap nach Commodity Code und summiere Quantity, Gross Weight, Net Weight
    df_sap_agg = df_sap.groupby('Commodity Code').agg({'Quantity':'sum','Gross Weight':'sum','Net Weight':'sum'}).reset_index()
    #read columns names of df_sap_agg
    col_names_sap = df_sap_agg.columns
    #change col names of df_dbh_agg to col_names_sap
    df_dbh_agg.columns = col_names_sap
    # Erstelle eine Ausgabe DataFrame
    diff_table = pd.DataFrame(columns=['Spalte', 'Index',])
    # prüfe ob die SapOrderNumber




    def truncate_float_columns(dataframe, decimals, exclude_columns=[]):
        factor = 10 ** decimals
        for column in dataframe.columns:
            if dataframe[column].dtype == float and column not in exclude_columns:
                dataframe[column] = np.trunc(dataframe[column] * factor) / factor
        return dataframe

    # Falls round_on True ist, runde die Float-Spalten außer "Quantity" auf 2 Nachkommastellen
    if round_on:
        df_sap_agg = truncate_float_columns(df_sap_agg, 2, exclude_columns=['Quantity'])
        #df_dbh_agg = truncate_float_columns(df_dbh_agg, 2, exclude_columns=['Quantity'])



# NUR QUANITTY nicht mehr runden 

    df1 = df_dbh_agg
    df2 = df_sap_agg    
    
        # Normalisiere die numerischen Spalten
    for df in [df1, df2]:
        for col in ['Quantity', 'Gross Weight', 'Net Weight']:
            if col in df.columns:
                df[col] = df[col].apply(normalize_number)
    
    
    
    # Prüfe zuerst Spaltennamen und Datentypen
    if set(df1.columns) != set(df2.columns):
        missing_in_df1 = set(df2.columns) - set(df1.columns)
        missing_in_df2 = set(df1.columns) - set(df2.columns)
        new_row = pd.DataFrame({
            'Spalte': ['Missing Columns'],
            'Index': ['-'],
            'Wert in DBH Dokument': [list(missing_in_df2)],
            'Wert in SAP Dokument': [list(missing_in_df1)]
        })
        diff_table = pd.concat([diff_table, new_row], ignore_index=True)

    # Vergleiche die Werte in den Spalten
    for column in set(df1.columns).intersection(df2.columns):
        for index, (value1, value2) in enumerate(zip(df1[column], df2[column])):
            if pd.isna(value1) and pd.isna(value2):
                continue  # Beide Werte sind NaN, kein Unterschied
            # Prüfe auf numerische Werte und vergleiche mit Toleranz
            if isinstance(value1, (float, int)) and isinstance(value2, (float, int)):
                if not np.isclose(value1, value2, atol=1e-2):
                    new_row = pd.DataFrame({
                        'Spalte': [column],
                        'Index_in_Commodity_Code': [index],
                        'DBH Dokument': [value1],
                        'SAP Dokument': [value2]
                    })
                    diff_table = pd.concat([diff_table, new_row], ignore_index=True)
            else:
                if value1 != value2:
                    new_row = pd.DataFrame({
                        'Spalte': [column],
                        'Index_in_Commodity_Code': [index],
                        'DBH Dokument': [value1],
                        'SAP Dokument': [value2]
                    })
                    diff_table = pd.concat([diff_table, new_row], ignore_index=True)

        # suche nach dem Commodity Code in df_sap_agg anhand der Index_in_Commodity_Code in diff_table
    # füge die Spalte Commodity Code in diff_table hinzu
    try:    
        df_sap_agg['IndexStelle']= df_sap_agg.index
        # sverweis auf df_sap_agg suche nach Commodity Code in df_sap_agg anhand der Index_in_Commodity_Code in diff_table
        diff_table['Commodity Code'] = diff_table['Index_in_Commodity_Code'].map(df_sap_agg.set_index('IndexStelle')['Commodity Code'])
        #sotiere spalten nach Commodity Code, Spalte SAP Dokument und DBH Dokument drope den rest
        diff_table = diff_table[['Commodity Code','Spalte','DBH Dokument','SAP Dokument']]
        #konverzt all to string
        diff_table = diff_table.astype(str)
    
    except KeyError:
        pass
    #st.data_editor(diff_table)
    return diff_table, missing_dn, dn_DBH_list, dn_sap

def umrechnerZFG510000(SKU, Menge):
    #Menge to float
    Menge = float(Menge)
    # 10189719 
    master_data = read_Table('data_materialmaster-MaterialMasterUnitOfMeasures')
    master_data['MaterialNumber'] = master_data['MaterialNumber'].astype(str)
    master_data['MaterialNumber'] = master_data['MaterialNumber'].str.replace('0000000000', '')
    #Filter master_data for SKU and UnitOfMeasure == ZFG510000
    master_data = master_data[(master_data['MaterialNumber'] == SKU) & (master_data['UnitOfMeasure'] == 'KGM')]
    # Berechne Zollmenge = DenominatorToBaseUnitOfMeasure / NumeratorToBaseUnitOfMeasure * Menge
    #wenn erste Zeile leer dann 
    if not master_data.empty:    
        DenominatorToBaseUnitOfMeasure = master_data['DenominatorToBaseUnitOfMeasure'].values[0]
        NumeratorToBaseUnitOfMeasure = master_data['NumeratorToBaseUnitOfMeasure'].values[0]
        Zollmenge = DenominatorToBaseUnitOfMeasure / NumeratorToBaseUnitOfMeasure * Menge
        return Zollmenge, DenominatorToBaseUnitOfMeasure, NumeratorToBaseUnitOfMeasure
    else:
        pass

def recalculate_quantities(df_sap):
    # Kopiere den DataFrame, um die Originaldaten nicht zu verändern
    df = df_sap.copy()
    
    # Filtere die Zeilen, wo 'Material Group' gleich 'ZFG510000' ist
    mask = df['Material Group'] == 'ZFG510000'
    
    # Wende die Umrechnung nur auf die gefilterten Zeilen an
    df.loc[mask, 'Quantity'] = df.loc[mask].apply(
        lambda row: umrechnerZFG510000(str(row['SKU Number']), row['Quantity'])[0], 
        axis=1
    )
    
    return df

        
def main():

    col1, col2, col3, col4 = st.columns([3,1,1,1])
    with col1:
        st.markdown("""
            <style>
            @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@700&display=swap');
            </style>
            <h3 style='text-align: left; color: #0F2B63; font-family: Montserrat; font-weight: bold;'>{}</h3>
            """.format(f'Hi {st.session_state.username} 👋 Bitte lade deine Dokumente hoch.'), unsafe_allow_html=True)   
        
        with col2:
            pass
        with col3:
            round_on = st.toggle('Runde SAP', True)
        with col4:
            #st.write('1.12')
            sel_zeige_Daten = st.toggle('Zeige Prüfungen', False, disabled=True)

    with st.expander('Umrechner ZFG510000', expanded=False):
        with st.form(key='my_form'):
            col1, col2, col3= st.columns([1,1,3])
            with col1:
                sel_check_sku = st.text_input('Sku', key='search')
                cal_start = st.form_submit_button('Zeige umgerechnete Menge')
            with col2:
                sel_check_qty = st.number_input('Menge', key='menge')
            with col3:
                if cal_start:
                    if sel_check_sku == '' or sel_check_qty == '':
                        st.error('Keine Werte keine Kekse....')
                    elif not sel_check_sku.isdigit():
                        st.error('Du kannst mir die SKU Buchstabieren.... aber ich kann nur Zahlen lesen sry....')
                    
                    elif len(sel_check_sku) != 8:
                        st.error('8 Stellen hat so eine SKU......')
                    else:
                        try:  
                            ergebniss, numerator, denominator = umrechnerZFG510000(sel_check_sku, int(sel_check_qty))
                            st.success(f'Die umgerechnete Menge beträgt {ergebniss} KG')
                            st.write(f'SAP Stammdaten:  DenominatorToBaseUnitOfMeasure {denominator} / NumeratorToBaseUnitOfMeasure {numerator}')
                        except:
                            st.error('SKU hat keine daten zu UnitOfMeasure == KGM prüfe die SKU oder die Einheit in den Stammdaten.')
                            
                            
                            
                            
                            
    col1, col2 = st.columns(2)
    with col1:
        uploaded_file = st.file_uploader("Upload SAP File", type=['xlsx'])
    with col2:
        uploaded_file2 = st.file_uploader("Upload DBH File", type=['csv'])

    pd.set_option("display.precision", 2)
    img_strip = Image.open('Data/img/strip.png')   
    img_strip = img_strip.resize((1000, 15))  
    st.image(img_strip, use_column_width=True)
    if uploaded_file and uploaded_file2:
        try:
            df_sap = pd.read_excel(uploaded_file)
        except UnicodeDecodeError:
            st.error('Fehler beim lesen der SAP Datei')
        try:
            rawdata = uploaded_file2.getvalue()
            result = chardet.detect(rawdata)
            encoding = result['encoding']
            # Datei mit erkanntem Encoding einlesen
            df_dbh = pd.read_csv(io.StringIO(rawdata.decode(encoding)), sep=';')
        except Exception as e:
                st.error(f'Fehler beim Lesen der DBH Datei: {e}')
                st.stop()

        # Encoding automatisch erkennen
        rawdata = uploaded_file2.getvalue()
        result = chardet.detect(rawdata)
        encoding = result['encoding']

        # Datei mit erkanntem Encoding einlesen
        df_dbh = pd.read_csv(io.StringIO(rawdata.decode(encoding)), sep=';')



        if df_dbh.empty:
            st.error("Die DBH-Datei ist leer oder enthält keine Daten.")
            st.stop()
            
        if st.button('Daten Hochladen und prüfen'):
            with hc.HyLoader(f'',hc.Loaders.points_line):
            #   with st.container(border=True):
                    
                    if uploaded_file and uploaded_file2 not in [None]:
                        df_sap, df_dbh = check_upload(df_sap, df_dbh, check_aktive=False)
                        df_sap, df_dbh = check_upload(df_sap, df_dbh,check_aktive=False)
                        df_sap['Gross Weight'] = df_sap['Gross Weight'].astype(float)
                        df_dbh['Rohmasse'] = df_dbh['Rohmasse'].astype(float)
                        
                        df_sap = recalculate_quantities(df_sap)

                        diff_table, missing_dn, dn_DBH_list, dn_sap = detaillierte_datenprüfung(df_sap, df_dbh,round_on=round_on)

                        # erstelle einen string je Liste und Trenne mit ; 
                        if diff_table.empty and missing_dn == []:
                            st.success('Good Job 👍 Lieferscheine ☑️ Warengruppen ☑️  Mengen ☑️')
                            fehler_ja_nein = 'Nein'  
                        if missing_dn:
                            st.error('⛔️ Folgende Lieferscheine fehlen ⛔️')
                            st.write(missing_dn)
                            fehler_ja_nein = 'Ja'
                        if not diff_table.empty:
                            vote(diff_table)
                            st.error('⛔️ Fehler in den Mengen gefunden ⛔️')
                            fehler_ja_nein = 'Ja'
                            st.write(diff_table)
                        dn_DBH_list = ';'.join(map(str, dn_DBH_list))
                        missing_dn = ';'.join(map(str, missing_dn))
                        dn_sap = ';'.join(map(str, dn_sap))
                        diff_table = diff_table.to_dict(orient='records')
                        diff_table = ';'.join(map(str, diff_table))
                        df = pd.DataFrame({'Datum': [pd.Timestamp.now()], 'User': [st.session_state.username], 'UUID': [str(uuid.uuid4())], 'Fehler gefunden': fehler_ja_nein, 'Lieferscheine SAP': [dn_sap], 'Lieferscheine DBH': [dn_DBH_list], 'Fehlende Lieferscheine': [missing_dn], 'Fehlerhafte Mengen': [diff_table]})

if __name__ == '__main__':
    main()
    
