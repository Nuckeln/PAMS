import streamlit as st
import pandas as pd
import plotly.express as px
import os
import pyarrow.compute as pc
from datetime import datetime, timedelta, timezone

try:
    from Data_Class.SynapseReader import SynapseReader
except ImportError:
    SynapseReader = None

# --- CONFIGURATION & LOGOS ---
LOGO_MAP = {
    'DIET': 'Data/img/DIET_LOGO.png',
    'LEAF': 'Data/img/LEAF_LOGO.png',
    'EXPORT': 'Data/img/outbound.png', 
    'DOMESTIC': 'Data/img/Domestic_LOGO.png',
    'C&F': 'Data/img/C&F_LOGO.png',
    'KN': 'Data/img/kuehne-nagel-logo-blue.png',
    'Bayreuth': 'Data/img/logo_login_spedition.png'
}

# KN Location Mapping
KN_MAPPING = {
    'DE52': 'München', 'MU5': 'München', 'NU5': 'München', 'STB': 'München', 'STW': 'München', 'ECH': 'München',
    'DE54': 'Hamburg', 'HH5': 'Hamburg', 'HRO': 'Hamburg', 'KIE': 'Hamburg', 'ROW': 'Hamburg',
    'MA5': 'Mainz',
    'DE53': 'Berlin', 'GNM': 'Berlin', 'PTD': 'Berlin',
    'DE55': 'Sehnde', 'HA5': 'Sehnde',
    'DE56': 'Duisburg', 'Rheine': 'Duisburg',
    'DE57': 'Schkeuditz', 'LE5': 'Schkeuditz',
    'DE59': 'Gärtringen', 'ST5': 'Gärtringen',
    'BE5': 'Bielefeld', 'BF5': 'Bielefeld', 'GRE': 'Bielefeld'
}

# --- HELPER FUNCTIONS ---
def get_kn_location_name(plant_code):
    """
    Maps Plant/Depot codes to City names for KN.
    """
    return KN_MAPPING.get(str(plant_code), str(plant_code))

@st.cache_data(ttl=3600)
def load_data():
    """
    Loads Inventory and Config data from Synapse/Delta Lake using SynapseReader.
    Cached for performance (TTL 1 hour).
    """
    if not SynapseReader:
        st.error("SynapseReader not available.")
        return pd.DataFrame(), pd.DataFrame()

    try:
        # 1. Calculate Date Threshold (Last 45 Days to be safe for 30 day history)
        days_back = 45
        threshold_date = datetime.now(timezone.utc) - timedelta(days=days_back)
        
        # PyArrow Filter for push-down predicate
        pa_filter = pc.field("CreationTimestamp") >= threshold_date
        
        # 1. Load Inventory (StockInventoryGermany)
        df_inv = SynapseReader.load_delta('gold/StockInventoryGermany/', as_pandas=True, filters=pa_filter)
        
        # 2. Load Config (StockConfigGermany) - usually smaller, load full or filter if needed
        df_conf = SynapseReader.load_delta('gold/StockConfigGermany/', as_pandas=True)
        
        return df_inv, df_conf
        
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame(), pd.DataFrame()

def process_data(df_inv, df_conf):
    """
    Pre-processes dataframes: ensures date columns, standardized types, and mapped columns.
    """
    if df_inv.empty:
        return df_inv, df_conf

    # Ensure CreationTimestamp is datetime
    if 'CreationTimestamp' in df_inv.columns:
        df_inv['CreationTimestamp'] = pd.to_datetime(df_inv['CreationTimestamp'], errors='coerce')
        # Normalize to Date (Day) for grouping
        df_inv['Date'] = df_inv['CreationTimestamp'].dt.normalize()
    
    # Ensure numeric columns for calculation
    for col in ['MengeVerkaufseinheit']:
        if col in df_inv.columns:
            df_inv[col] = pd.to_numeric(df_inv[col], errors='coerce').fillna(0)
    
    # Map KN Locations (StandortGeografisch -> StandortName)
    if 'StandortGeografisch' in df_inv.columns:
        df_inv['StandortName'] = df_inv['StandortGeografisch'].apply(get_kn_location_name)
    else:
        df_inv['StandortName'] = 'Unknown'

    # Config Data processing
    if not df_conf.empty:
        for col in ['MaxKapazitaetLagerzone']:
            if col in df_conf.columns:
                df_conf[col] = pd.to_numeric(df_conf[col], errors='coerce').fillna(0)
        
        # Also map Config locations
        if 'StandortGeografisch' in df_conf.columns:
            df_conf['StandortName'] = df_conf['StandortGeografisch'].apply(get_kn_location_name)
        else:
             df_conf['StandortName'] = 'Unknown'

    return df_inv, df_conf

def get_filtered_metrics(category, df_inv, df_conf, latest_date):
    """
    Calculates metrics for a specific category based on the defined rules.
    Returns:
        current_stock (float/int),
        capacity (float/int),
        history_df (DataFrame),
        current_df_filtered (DataFrame)
    """
    
    # --- 1. Define Filters ---
    
    # Inventory Filters (Boolean Masks)
    mask_inv = None
    metric_type = 'count' # or 'sum_unit'
    
    # Config Filters (Boolean Masks)
    mask_conf = None
    
    # Logic Switch
    if category == 'DIET':
        # StockInventory
        mask_inv = (df_inv['Fachbereich'] == 'DIET') & (df_inv['Lagerzone'] == 'Blocklager')
        metric_type = 'sum_unit'
        # StockConfig
        if not df_conf.empty:
            mask_conf = (df_conf['Fachbereich'] == 'DIET') & (df_conf['Lagerzone'] == 'Blocklager')
            
    elif category == 'LEAF':
        mask_inv = (df_inv['Fachbereich'] == 'LEAF') & (df_inv['Lagerzone'] == 'Blocklager')
        metric_type = 'sum_unit'
        if not df_conf.empty:
            mask_conf = (df_conf['Fachbereich'] == 'LEAF') & (df_conf['Lagerzone'] == 'Blocklager')

    elif category == 'C&F':
        mask_inv = (df_inv['Fachbereich'] == 'C&F') & (df_inv['Lagerzone'] == 'Regallager')
        metric_type = 'count'
        if not df_conf.empty:
            mask_conf = (df_conf['Fachbereich'] == 'C&F') & (df_conf['Lagerzone'] == 'Regallager')

    elif category == 'EXPORT':
        # Fachbereich = Finished Goods Export
        # Lagerzone = Hochregallager OR Regallager OR Blocklager
        mask_inv = (df_inv['Fachbereich'] == 'Finished Goods Export') & \
                   (df_inv['Lagerzone'].isin(['Hochregallager', 'Regallager', 'Blocklager']))
        metric_type = 'count'
        if not df_conf.empty:
            mask_conf = (df_conf['Fachbereich'] == 'Finished Goods Export') & \
                        (df_conf['Lagerzone'].isin(['Hochregallager', 'Regallager', 'Blocklager']))

    elif category == 'DOMESTIC':
        # Fachbereich = Domestic Deutschland
        # Lagerzone = Blocklager OR Regallager
        # StandortGeografisch = Bayreuth
        mask_inv = (df_inv['Fachbereich'] == 'Domestic Deutschland') & \
                   (df_inv['Lagerzone'].isin(['Blocklager', 'Regallager'])) & \
                   (df_inv['StandortGeografisch'] == 'Bayreuth')
        metric_type = 'count'
        if not df_conf.empty:
            mask_conf = (df_conf['Fachbereich'] == 'Domestic Deutschland') & \
                        (df_conf['StandortGeografisch'] == 'Bayreuth') & \
                        (df_conf['Lagerzone'].isin(['Blocklager', 'Regallager']))

    elif category in ['München', 'Hamburg', 'Mainz', 'Duisburg', 'Berlin']: # KN Depots
        # Uses Mapped Name column 'StandortName'
        mask_inv = (df_inv['Fachbereich'] == 'Domestic Deutschland') & \
                   (df_inv['Lagerzone'] == 'Paletten Zone') & \
                   (df_inv['StandortName'] == category)
        metric_type = 'count'
        
        if not df_conf.empty:
            mask_conf = (df_conf['Fachbereich'] == 'Domestic Deutschland') & \
                        (df_conf['Lagerzone'] == 'Paletten Zone') & \
                        (df_conf['StandortName'] == category)
            
    else:
        return 0, 0, pd.DataFrame(), pd.DataFrame()

    # --- 2. Calculate Inventory Metrics ---
    
    # Filter full inventory history
    df_inv_filtered = df_inv[mask_inv].copy() if not df_inv.empty else pd.DataFrame()
    
    # Calculate Daily Stats (History)
    if not df_inv_filtered.empty:
        if metric_type == 'sum_unit':
            history = df_inv_filtered.groupby('Date')['MengeVerkaufseinheit'].sum().reset_index(name='Value')
        else: # count rows
            history = df_inv_filtered.groupby('Date').size().reset_index(name='Value')
    else:
        history = pd.DataFrame(columns=['Date', 'Value'])

    # Current Stock Value (latest available date in dataset)
    current_val = 0
    df_current_filtered = pd.DataFrame()
    
    if not df_inv_filtered.empty:
        df_current_filtered = df_inv_filtered[df_inv_filtered['Date'] == latest_date]
        
        if metric_type == 'sum_unit':
            current_val = df_current_filtered['MengeVerkaufseinheit'].sum()
        else:
            current_val = len(df_current_filtered)
            
    # --- 3. Calculate Capacity ---
    capacity_val = 0
    if mask_conf is not None and not df_conf.empty:
        df_conf_filtered = df_conf[mask_conf]
        if not df_conf_filtered.empty:
            # Remove duplicates from Sensor_ID
            if 'Sensor_ID' in df_conf_filtered.columns:
                df_conf_dedup = df_conf_filtered.drop_duplicates(subset=['Sensor_ID'])
                capacity_val = df_conf_dedup['MaxKapazitaetLagerzone'].sum()
            else:
                capacity_val = df_conf_filtered['MaxKapazitaetLagerzone'].sum()

    return current_val, capacity_val, history, df_current_filtered


def render_tile(title, category_key, df_inv, df_conf, latest_date_norm):
    
    # Get Data
    current_val, capacity, history, df_details = get_filtered_metrics(category_key, df_inv, df_conf, latest_date_norm)
    
    # Determine Unit Label
    unit = "Karton" if category_key in ['DIET', 'LEAF'] else "Pal"
    
    with st.container(border=True):
        # Header / Logo
        col_logo, col_metric = st.columns([1, 2])
        
        with col_logo:
            logo_path = LOGO_MAP.get(category_key, LOGO_MAP.get('KN', None))
            # KN logic
            if category_key in ['München', 'Hamburg', 'Mainz', 'Duisburg', 'Berlin']:
                 logo_path = LOGO_MAP['KN']
            
            if logo_path and os.path.exists(logo_path):
                st.image(logo_path, use_container_width=True)
            else:
                st.write(f"**{title}**")

        with col_metric:
            st.metric(label=f"Bestand ({unit})", value=f"{current_val:,.0f}")
            if capacity > 0:
                utilization = (current_val / capacity) * 100
                st.caption(f"Kapazität: {capacity:,.0f} ({utilization:.1f}%)")
            else:
                st.caption("Kapazität: n/a")

        # Sparkline / Chart
        if not history.empty:
            fig = px.area(history, x='Date', y='Value')
            fig.update_layout(
                showlegend=False,
                margin=dict(l=0, r=0, t=10, b=0),
                height=80,
                xaxis=dict(visible=False),
                yaxis=dict(visible=False),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)'
            )
            fig.update_traces(line=dict(color='#0e2b63', width=2), fillcolor='rgba(14, 43, 99, 0.1)')
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        
        # Popup / Expander for Details
        with st.expander("🔎 Details anzeigen"):
            if not df_details.empty:
                st.caption(f"Gefilterte Daten für {latest_date_norm.date()}")
                # Select only relevant columns for display
                display_cols = ['Material', 'Artikeltext', 'Charge', 'MengeVerkaufseinheit', 'Lagerplatz', 'Lagerzone']
                final_cols = [c for c in display_cols if c in df_details.columns]
                if not final_cols: final_cols = df_details.columns 
                
                st.dataframe(df_details[final_cols], use_container_width=True, hide_index=True)
            else:
                st.info("Keine Daten für den aktuellen Filter vorhanden.")

def app():
    st.markdown("## 📦 Lagerbestands-Übersicht")
    
    # Load Data
    with st.spinner("Lade Bestandsdaten..."):
        df_inv_raw, df_conf_raw = load_data()
    
    if df_inv_raw.empty:
        st.warning("Keine Bestandsdaten gefunden. Bitte prüfen Sie die Quelle.")
        return

    # Process
    df_inv, df_conf = process_data(df_inv_raw, df_conf_raw)
    
    # Determine Latest Date (Global)
    if 'Date' in df_inv.columns:
        latest_date = df_inv['Date'].max()
        st.info(f"Datenstand: {latest_date.strftime('%d.%m.%Y')}")
    else:
        st.error("Fehler: Datumsspalte konnte nicht ermittelt werden.")
        return

    # --- 1. BAYREUTH HUB ---
    st.subheader("🏭 Bayreuth Hub")
    
    # Layout: 5 Columns
    cols = st.columns(5)
    
    cats = ['DIET', 'LEAF', 'C&F', 'EXPORT', 'DOMESTIC']
    
    for i, cat in enumerate(cats):
        with cols[i]:
            render_tile(cat, cat, df_inv, df_conf, latest_date)

    st.markdown("---")

    # --- 2. KÜHNE & NAGEL ---
    st.subheader("🚚 Kühne & Nagel Network")
    
    # Layout: 5 Columns
    cols_kn = st.columns(5)
    kn_cities = ['München', 'Hamburg', 'Mainz', 'Duisburg', 'Berlin']
    
    for i, city in enumerate(kn_cities):
        with cols_kn[i]:
            render_tile(city, city, df_inv, df_conf, latest_date)


if __name__ == "__main__":
    app()