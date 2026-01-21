import pandas as pd
from Data_Class.SynapseReader import SynapseReader
import streamlit as st


@st.cache_data
def load_datasets():
    try:
        df_config = SynapseReader.load_delta("gold/StockConfigGermany//", as_pandas=True)
        df_vio = SynapseReader.load_delta("gold/StockViolationGermany/", as_pandas=True)
        df_inv = SynapseReader.load_delta("gold/StockInventoryGermany/", as_pandas=True)
    except Exception as e:
        st.error(f"Fehler beim Laden der Daten: {e}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
    return df_config, df_vio, df_inv
 
def app(): 
    # --- CSS FÜR KPI BOXEN ---
    st.markdown("""
    <style>
    .kpi-container {
        border-radius: 10px;
        padding: 15px;
        color: white;
        text-align: center;
        margin-bottom: 10px;
    }
    .kpi-title {
        font-size: 16px;
        font-weight: bold;
    }
    .kpi-value {
        font-size: 28px;
        font-weight: bold;
    }
    .kpi-blue { background-color: #2A628F; }
    .kpi-green { background-color: #4E8542; }
    .kpi-orange { background-color: #C57841; }
    .kpi-red { background-color: #AF3D3D; }
    </style>
    """, unsafe_allow_html=True)

    df_config, df_vio, df_inv = load_datasets()

    # --- DATENVERARBEITUNG (MERGE & CLEANING) ---
    df_merged = pd.merge(df_vio, df_inv, on='SSCCKVL', how='left')
    df_merged['ViolationDate_Temp'] = pd.to_datetime(df_merged['ViolationDate'])
    df_merged['Violation_Day_Only'] = df_merged['ViolationDate_Temp'].dt.date
    df_merged = df_merged.drop_duplicates(subset=['SSCCKVL', 'Violation_Day_Only'], keep='first')
    df_merged['Pallet in Stock'] = df_merged['StandortGeografisch'].apply(lambda x: 'No' if pd.isna(x) else 'Yes')
    def format_date_german(date_val):
        try: return pd.to_datetime(date_val).strftime('%d.%m.%y')
        except: return date_val
    date_cols = ['ViolationDate', 'WareneingangDatum', 'ShelfLife']
    for col in date_cols:
        if col in df_merged.columns:
            df_merged[col] = df_merged[col].apply(format_date_german)
            
    df_merged['ViolationDate_Temp_Filter'] = pd.to_datetime(df_merged['ViolationDate_Temp']).dt.date
    
    column_mapping = {
        'StandortGeografisch': 'Location', 'SSCCKVL': 'SSCCKVL', 'Artikelnummer': 'Materialnumber',
        'Materialgruppe': 'Materialgroup', 'Artikelbeschreibung': 'Item description', 'ViolationReason': 'Violation Reason',
        'ViolationDate': 'Violation Date', 'ExceededValue': 'Exeeded Value', 'LimitValue': 'Value Limit',
        'RemainingDays': 'RemainingDays', 'Fachbereich': 'Department', 'Lagerhalle': 'Warehouse',
        'Lagerzone': 'Storage Area', 'Stellplatz': 'Storage Bin', 'MengeinTHoderKG': 'Quantity in TH/KG',
        'MengeneinheitBaseUom': 'BaseUom', 'Endmarkt': 'End Market', 'WareneingangDatum': 'Goods Receipt Date',
        'ShelfLife': 'ShelfLife', 'Alert': 'Alert', 'Pallet in Stock': 'Pallet in Stock'
    }
    final_table = df_merged.rename(columns=column_mapping)
    
    target_columns = [
        'Location', 'SSCCKVL', 'Materialnumber', 'Materialgroup', 'Item description', 'Violation Reason', 
        'Violation Date', 'Exeeded Value', 'Value Limit', 'RemainingDays', 'Department', 'Warehouse', 
        'Storage Area', 'Storage Bin', 'Quantity in TH/KG', 'BaseUom', 'End Market', 'Goods Receipt Date', 
        'ShelfLife', 'Alert', 'Pallet in Stock', 'ViolationDate_Temp_Filter'
    ]
    available_cols = [c for c in target_columns if c in final_table.columns]
    final_table = final_table[available_cols]

    # --- SESSION STATE INITIALISIERUNG ---
    if 'filters_initialized' not in st.session_state:
        st.session_state.filters_initialized = True
        st.session_state.filters_reset = True # Force reset on first run


    def get_options(col_name):
        if col_name in final_table.columns:
            unique_vals = sorted(final_table[col_name].astype(str).unique().tolist())
            return ["Alle"] + unique_vals
        return ["Alle"]

    # Min/Max Datum für den Date-Picker
    min_date = final_table['ViolationDate_Temp_Filter'].min()
    max_date = final_table['ViolationDate_Temp_Filter'].max()

    # --- FILTER FORMULAR (UI) ---
    with st.form(key='filter_form'):
        
        # Filter zurücksetzen Logik
        if st.session_state.get('filters_reset', False):
            st.session_state.sel_loc = "Alle"
            st.session_state.sel_sscc = "Alle"
            st.session_state.sel_reason = "Alle"
            st.session_state.sel_start_date = min_date
            st.session_state.sel_end_date = max_date
            st.session_state.sel_days = "Alle"
            st.session_state.sel_dept = "Alle"
            st.session_state.sel_wh = "Alle"
            st.session_state.sel_area = "Alle"
            st.session_state.sel_bin = "Alle"
            st.session_state.sel_gr_date = "Alle"
            st.session_state.sel_mat_grp = "Alle"
            st.session_state.sel_end_mkt = "Alle"
            st.session_state.sel_shelf = "Alle"
            st.session_state.sel_alert = "Alle"
            st.session_state.sel_pallet = "Alle"
            st.session_state.filters_reset = False

        c1, c2, c3, c4, c5, c6, c7, c8 = st.columns(8)
        with c1: st.selectbox("Location", get_options('Location'), key="sel_loc")
        with c2: st.selectbox("SSCCKVL", get_options('SSCCKVL'), key="sel_sscc")
        with c3: st.selectbox("Violation Reason", get_options('Violation Reason'), key="sel_reason")
        with c4: st.date_input("Start date", min_value=min_date, max_value=max_date, key="sel_start_date")
        with c5: st.date_input("End date", min_value=min_date, max_value=max_date, key="sel_end_date")
        with c6: st.selectbox("RemainingDays", get_options('RemainingDays'), key="sel_days")
        with c7: st.selectbox("Department", get_options('Department'), key="sel_dept")
        with c8: st.selectbox("Warehouse", get_options('Warehouse'), key="sel_wh")

        c9, c10, c11, c12, c13, c14, c15, c16 = st.columns(8)
        with c9: st.selectbox("Storage Area", get_options('Storage Area'), key="sel_area")
        with c10: st.selectbox("Storage Bin", get_options('Storage Bin'), key="sel_bin")
        with c11: st.selectbox("Goods Receipt Date", get_options('Goods Receipt Date'), key="sel_gr_date")
        with c12: st.selectbox("Material Group", get_options('Materialgroup'), key="sel_mat_grp")
        with c13: st.selectbox("End Market", get_options('End Market'), key="sel_end_mkt")
        with c14: st.selectbox("ShelfLife", get_options('ShelfLife'), key="sel_shelf")
        with c15: st.selectbox("Alert", get_options('Alert'), key="sel_alert")
        with c16: st.selectbox("Pallet in Stock", get_options('Pallet in Stock'), key="sel_pallet")


        # Buttons in einer Reihe
        b1, b2 = st.columns(2)
        submitted = b1.form_submit_button("Filter anwenden", use_container_width=True)
        reset_pressed = b2.form_submit_button("Filter zurücksetzen", use_container_width=True)

        if reset_pressed:
            st.session_state.filters_reset = True
            st.experimental_rerun()

    # --- FILTER LOGIK ANWENDEN ---
    filtered_table = final_table.copy()

    # Datumsbereichsfilter immer anwenden, aber nur wenn die Keys existieren
    if 'sel_start_date' in st.session_state and 'sel_end_date' in st.session_state:
        filtered_table = filtered_table[(filtered_table['ViolationDate_Temp_Filter'] >= st.session_state.sel_start_date) & (filtered_table['ViolationDate_Temp_Filter'] <= st.session_state.sel_end_date)]

    # Andere Filter anwenden
    if st.session_state.get("sel_loc", "Alle") != "Alle": filtered_table = filtered_table[filtered_table['Location'].astype(str) == st.session_state.sel_loc]
    if st.session_state.get("sel_sscc", "Alle") != "Alle": filtered_table = filtered_table[filtered_table['SSCCKVL'].astype(str) == st.session_state.sel_sscc]
    if st.session_state.get("sel_reason", "Alle") != "Alle": filtered_table = filtered_table[filtered_table['Violation Reason'].astype(str) == st.session_state.sel_reason]
    if st.session_state.get("sel_days", "Alle") != "Alle": filtered_table = filtered_table[filtered_table['RemainingDays'].astype(str) == st.session_state.sel_days]
    if st.session_state.get("sel_dept", "Alle") != "Alle": filtered_table = filtered_table[filtered_table['Department'].astype(str) == st.session_state.sel_dept]
    if st.session_state.get("sel_wh", "Alle") != "Alle": filtered_table = filtered_table[filtered_table['Warehouse'].astype(str) == st.session_state.sel_wh]
    if st.session_state.get("sel_area", "Alle") != "Alle": filtered_table = filtered_table[filtered_table['Storage Area'].astype(str) == st.session_state.sel_area]
    if st.session_state.get("sel_bin", "Alle") != "Alle": filtered_table = filtered_table[filtered_table['Storage Bin'].astype(str) == st.session_state.sel_bin]
    if st.session_state.get("sel_gr_date", "Alle") != "Alle": filtered_table = filtered_table[filtered_table['Goods Receipt Date'].astype(str) == st.session_state.sel_gr_date]
    if st.session_state.get("sel_mat_grp", "Alle") != "Alle": filtered_table = filtered_table[filtered_table['Materialgroup'].astype(str) == st.session_state.sel_mat_grp]
    if st.session_state.get("sel_end_mkt", "Alle") != "Alle": filtered_table = filtered_table[filtered_table['End Market'].astype(str) == st.session_state.sel_end_mkt]
    if st.session_state.get("sel_shelf", "Alle") != "Alle": filtered_table = filtered_table[filtered_table['ShelfLife'].astype(str) == st.session_state.sel_shelf]
    if st.session_state.get("sel_alert", "Alle") != "Alle": filtered_table = filtered_table[filtered_table['Alert'].astype(str) == st.session_state.sel_alert]
    if st.session_state.get("sel_pallet", "Alle") != "Alle": filtered_table = filtered_table[filtered_table['Pallet in Stock'].astype(str) == st.session_state.sel_pallet]

    # --- KPI BERECHNUNG & ANZEIGE ---
    st.markdown("---") 

    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    with kpi1:
        st.markdown(f"""
        <div class="kpi-container kpi-blue">
            <div class="kpi-title">Pallets with Violations</div>
            <div class="kpi-value">{filtered_table['SSCCKVL'].nunique():,}</div>
        </div>
        """, unsafe_allow_html=True)
    with kpi2:
        st.markdown(f"""
        <div class="kpi-container kpi-green">
            <div class="kpi-title">Total Violations</div>
            <div class="kpi-value">{len(filtered_table):,}</div>
        </div>
        """, unsafe_allow_html=True)
    with kpi3:
        st.markdown(f"""
        <div class="kpi-container kpi-orange">
            <div class="kpi-title">Warehouses Affected</div>
            <div class="kpi-value">{filtered_table['Warehouse'].nunique():,}</div>
        </div>
        """, unsafe_allow_html=True)
    with kpi4:
         st.markdown(f"""
        <div class="kpi-container kpi-red">
            <div class="kpi-title">Departments Affected</div>
            <div class="kpi-value">{filtered_table['Department'].nunique():,}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")

    # --- ANZEIGE ---
    if 'Location' in filtered_table.columns and 'SSCCKVL' in filtered_table.columns:
        final_table_display = filtered_table.sort_values(by=['Location', 'SSCCKVL'])
    else:
        final_table_display = filtered_table

    if 'ViolationDate_Temp_Filter' in final_table_display.columns:
        final_table_display = final_table_display.drop(columns=['ViolationDate_Temp_Filter'])

    st.dataframe(final_table_display.head(10000), use_container_width=True)