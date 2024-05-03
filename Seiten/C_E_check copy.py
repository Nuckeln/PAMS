from pandas.testing import assert_frame_equal
import pandas as pd
import re
import streamlit as st
import json
from Data_Class.MMSQL_connection import read_Table, save_Table_append 

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

def datenprüfung(df_sap, df_dbh):
    st.data_editor(df_sap)
    st.data_editor(df_dbh)

    dn_sap = df_sap['Delivery Number'].tolist()
    #entferne duplikate
    dn_sap = list(dict.fromkeys(dn_sap))
    # Konvertiere die Spalte 'Vorgangsnummer' in einen String
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
    differences = None
    try:
        assert_frame_equal(df_dbh_agg, df_sap_agg)
    except AssertionError as e:
        differences = str(e)
    return differences, dn_DBH_list, dn_sap, missing_dn, df_dbh_agg, df_sap_agg
            
def formatiere_abweichungen(differences):
    if differences is None:
        return "Keine Abweichungen gefunden."
    error_messages = differences.split('\n')
    diff_table = pd.DataFrame(columns=['Spalte', 'Index', 'Wert Links', 'Wert Rechts'])
    st.write(error_messages)

    for line in error_messages:
        if 'values are different' in line:
            parts = line.split('[')
            if len(parts) < 4:
                continue  # Überspringe, falls die erwartete Struktur nicht vorhanden ist

            # Extrahiere die relevante Information
            col_info = line.split(' ')[1].strip()
            index_info = parts[1].split(']')[0]
            left_values = parts[2].split(']')[0].split(', ')
            right_values = parts[3].split(']')[0].split(', ')
            indices = index_info.split(', ')

            # Füge die Information in die Tabelle
            for idx, (left, right) in enumerate(zip(left_values, right_values)):
                diff_table = diff_table.append({
                    'Spalte': col_info,
                    'Index': indices[idx],
                    'Wert Links': left,
                    'Wert Rechts': right
                }, ignore_index=True)

    return diff_table

def umrechnerZFG510000(SKU, Menge):
    # 10189719 
    master_data = read_Table('data_materialmaster-MaterialMasterUnitOfMeasures')
    master_data['MaterialNumber'] = master_data['MaterialNumber'].astype(str)
    master_data['MaterialNumber'] = master_data['MaterialNumber'].str.replace('0000000000', '')
    #Filter master_data for SKU and UnitOfMeasure == ZFG510000
    master_data = master_data[(master_data['MaterialNumber'] == SKU) & (master_data['UnitOfMeasure'] == 'KGM')]
    # Berechne Zollmenge = DenominatorToBaseUnitOfMeasure / NumeratorToBaseUnitOfMeasure * Menge
    if not master_data.empty:        
        DenominatorToBaseUnitOfMeasure = master_data['DenominatorToBaseUnitOfMeasure'].values[0]
        NumeratorToBaseUnitOfMeasure = master_data['NumeratorToBaseUnitOfMeasure'].values[0]
        Zollmenge = DenominatorToBaseUnitOfMeasure / NumeratorToBaseUnitOfMeasure * Menge
        return Zollmenge
    else:
        return 'SKU nicht gefunden'
    
        
def main():
    st.warning('Dies ist noch in der Entwicklung und darf nicht für BAU verwendet werden')
    st.subheader('')
    
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@700&display=swap');
        </style>
        <h3 style='text-align: left; color: #0F2B63; font-family: Montserrat; font-weight: bold;'>{}</h3>
        """.format(f'Hi {st.session_state.username} 👋 Bitte lade deine Dokumente hoch.'), unsafe_allow_html=True)   
    with st.expander('Umrechner ZFG510000', expanded=False):
        with st.form(key='my_form'):
            col1, col2, col3= st.columns([1,1,3])
            with col1:
                sel_check_sku = st.text_input('Sku', key='search')
                cal = st.form_submit_button('Zeige umgerechnete Menge')
            with col2:
                sel_check_qty = st.text_input('Menge', key='menge')
            with col3:
                if cal:
                    if sel_check_sku == '' or sel_check_qty == '':
                        st.error('Bitte SKU und Menge eingeben')
                    else:
                        st.success(f'Die umgerechnete Menge beträgt {umrechnerZFG510000(sel_check_sku, int(sel_check_qty))} TH')
        
    col1, col2 = st.columns(2)
    with col1:
        uploaded_file = st.file_uploader("Upload SAP File", type=['xlsx'])
    with col2:
        uploaded_file2 = st.file_uploader("Upload DBH File", type=['csv'])
        
#### TESTBEDIENUNG ########
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        testversionladen = st.toggle('Testversionen laden', False)
        with col2:
            if testversionladen == True:
                test = st.slider('Testversion',1,3)
    if testversionladen:
        df_sap = pd.read_excel(f'Data/appData/testdatendbh/Test{test} SAP.xlsx')
        df_dbh = pd.read_csv(f'Data/appData/testdatendbh/Test{test}DBH.csv',sep=';')
        df_sap, df_dbh = check_upload(df_sap, df_dbh,check_aktive=False)
        differences, dn_DBH_list, dn_sap, missing_dn, df_dbh_agg, df_sap_agg = datenprüfung(df_sap, df_dbh)
        abw_table = formatiere_abweichungen(differences)
        #st.write(abw_table)           
                
                
    if uploaded_file and uploaded_file2:
        df_sap = pd.read_excel(uploaded_file)
        df_dbh = pd.read_csv(uploaded_file2,sep=';')
    if st.button('Daten Hochladen und prüfen'):
        if uploaded_file and uploaded_file2 not in [None]:
            df_sap, df_dbh = check_upload(df_sap, df_dbh, check_aktive=False)
            # Prüfe ob in df_sap Material Group ZFG510000 enthalten ist wenn ja berechne Zollmenge für jede Zeile
            if 'Material Group' in df_sap.columns:
                df_sap['Material Group'] = df_sap['Material Group'].astype(str)
                if 'ZFG510000' in df_sap['Material Group'].values:
                    st.warning('Material Group ZFG510000 gefunden und angepasst')
                    df_sap['Zollmenge'] = df_sap.apply(lambda row: umrechnerZFG510000(row['SKU'], row['Quantity']), axis=1)
            differences, dn_DBH_list, dn_sap, missing_dn, df_dbh_agg, df_sap_agg = datenprüfung(df_sap, df_dbh)
            abw_table = formatiere_abweichungen(differences)
           # st.write(abw_table)
    
    
if __name__ == '__main__':
    main()
    