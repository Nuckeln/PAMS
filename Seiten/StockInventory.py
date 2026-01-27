import streamlit as st
import pandas as pd
import plotly.express as px
import os
import pyarrow.compute as pc
from datetime import datetime, timedelta, timezone
from Data_Class.sql import SQL

try:
    from Data_Class.SynapseReader import SynapseReader
except ImportError:
    SynapseReader = None

# --- CONFIGURATION & LOGOS ---
# --- CONFIGURATION & LOGOS ---
LOGO_MAP = {
    'DIET': 'Data/img/DIET_LOGO.png',
    'LEAF': 'Data/img/LEAF_LOGO.png',
    'EXPORT': 'Data/img/LC_LOGO.png', 
    'DOMESTIC': 'Data/img/Domestic_LOGO.png',
    'C&F': 'Data/img/C&F_LOGO.png',
    'KN': 'Data/img/kuehne-nagel-logo-blue.png',
    'Bayreuth': 'Data/img/logo_login_spedition.png',
    'LOG-IN': 'Data/img/logo_login_spedition.png',
    'ARVATO': 'Data/img/arvato.png',
    # Individuelle KN Logos
    'Berlin': 'Data/img/KN_Berlin.py.png',
    'Duisburg': 'Data/img/KN_Dui.py.png',
    'Hamburg': 'Data/img/KN_Hamburg.py.png',
    'Mainz': 'Data/img/KN_mainz.py.png',
    'München': 'Data/img/KN_muc.py.png'
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

      
        dfStammdaten = SQL.read_table('data_materialmaster-MaterialMasterUnitOfMeasures', ['UnitOfMeasure', 'MaterialNumber','NumeratorToBaseUnitOfMeasure',
                                                                    'DenominatorToBaseUnitOfMeasure'],
                            )

        
        return df_inv, df_conf, dfStammdaten
        
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame(), pd.DataFrame()

def process_data(df_inv, df_conf, dfStammdaten):
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

    # Nur relevante Einheiten
    units = ['D97']
    dfStammdaten = dfStammdaten[dfStammdaten['UnitOfMeasure'].isin(units)].copy()

    # Neue Spalten berechnen (vektorisiert)
    dfStammdaten['Menge'] = dfStammdaten['NumeratorToBaseUnitOfMeasure'] / dfStammdaten['DenominatorToBaseUnitOfMeasure']

    df_inv['Artikelnummer'] = df_inv['Artikelnummer'].astype(str)
    
    df_inv = pd.merge(df_inv, dfStammdaten[['MaterialNumber', 'Menge']], left_on='Artikelnummer', right_on='MaterialNumber', how='left')
    # wenn in df_inv MengeVerkaufseinheit kleiner als 1 ist  und QuellSystem = Bayreuth SWISSLOG dann runde auf 1 auf
    mask_small = df_inv['MengeVerkaufseinheit'] < 1
    mask_bayreuth = df_inv['QuellSystem'] == 'Bayreuth SWISSLOG'
    df_inv.loc[mask_small & mask_bayreuth, 'MengeVerkaufseinheit'] = 1
    # wenn in df_inv MengeVerkaufseinheit 0 oder leer ist und QuellSystem = Bayreuth SWISSLOG dann MengeVerkaufseinheit = MenginTHoderKG / Menge
    mask_zero = (df_inv['MengeVerkaufseinheit'] == 0) | (df_inv['MengeVerkaufseinheit'].isna())
    mask_bayreuth = df_inv['QuellSystem'] == 'Bayreuth SWISSLOG'
    df_inv.loc[mask_zero & mask_bayreuth, 'MengeVerkaufseinheit'] = df_inv.loc[mask_zero & mask_bayreuth, 'MengeinTHoderKG'] / df_inv.loc[mask_zero & mask_bayreuth, 'Menge']

    return df_inv, df_conf


def get_filtered_metrics(category, df_inv, df_conf, latest_date):
    """
    Berechnet Bestände und Kapazitäten mit strikter Duplikat-Bereinigung 
    nach dem Filtern.
    """
    if df_inv.empty:
        return 0, 0, pd.DataFrame(), pd.DataFrame()

    # --- 1. Filter-Initialisierung ---
    m_inv = pd.Series(False, index=df_inv.index)
    m_conf = pd.Series(False, index=df_conf.index) if not df_conf.empty else None
    metric_type = 'count' # Standard: Paletten zählen

    # --- 2. Spezifische Filter-Regeln ---
    
    if category == 'DIET':
        m_inv = (df_inv['Fachbereich'] == 'DIET') & (df_inv['Lagerzone'] == 'Blocklager')
        metric_type = 'sum_unit'
        if m_conf is not None:
            m_conf = (df_conf['Fachbereich'] == 'DIET') & (df_conf['Lagerzone'] == 'Blocklager')

    elif category == 'LEAF':
        # Abfrage auf beide Schreibweisen zur Sicherheit
        target_fb = ['Leaf', 'LEAF']
        target_zones = ['Blocklager']

        m_inv = (df_inv['Fachbereich'].isin(target_fb)) & (df_inv['Lagerzone'].isin(target_zones))
        metric_type = 'sum_unit'
        if m_conf is not None:
            m_conf = (df_conf['Fachbereich'].isin(target_fb)) & (df_conf['Lagerzone'].isin(target_zones))

    elif category == 'C&F':
        m_inv = (df_inv['Fachbereich'] == 'C&F') & (df_inv['Lagerzone'] == 'Regallager')
        if m_conf is not None:
            m_conf = (df_conf['Fachbereich'] == 'C&F') & (df_conf['Lagerzone'] == 'Regallager')

    elif category == 'EXPORT':
            # Erweiterte Fachbereiche
            fbs = ['Finished Goods Export', 'WMS', "Domestic FG's"]
            # Definierte Zonen
            zones = ['Hochregallager', 'Regallager', 'Blocklager']
            
            # Filter für Inventory
            m_inv = (df_inv['Fachbereich'].isin(fbs)) & (df_inv['Lagerzone'].isin(zones))
            metric_type = 'sum_unit'
            
            # Filter für Config (Kapazität)
            if m_conf is not None:
                m_conf = (df_conf['Fachbereich'].isin(fbs)) & (df_conf['Lagerzone'].isin(zones))
    elif category == 'DOMESTIC':
        zones = ['Blocklager', 'Regallager']
        m_inv = (df_inv['Fachbereich'] == 'Domestic Deutschland') & \
                (df_inv['Lagerzone'].isin(zones)) & \
                (df_inv['StandortGeografisch'] == 'Bayreuth')
        if m_conf is not None:
            m_conf = (df_conf['Fachbereich'] == 'Domestic Deutschland') & \
                     (df_conf['StandortGeografisch'] == 'Bayreuth') & \
                     (df_conf['Lagerzone'].isin(zones))

    elif category in ['München', 'Hamburg', 'Mainz', 'Duisburg', 'Berlin']:
        m_inv = (df_inv['Fachbereich'] == 'Domestic Deutschland') & \
                (df_inv['Lagerzone'] == 'Paletten Zone') & \
                (df_inv['StandortName'] == category)
        if m_conf is not None:
            m_conf = (df_conf['Fachbereich'] == 'Domestic Deutschland') & \
                     (df_conf['Lagerzone'] == 'Paletten Zone') & \
                     (df_conf['StandortName'] == category)

    elif category == 'LOG-IN':
        m_inv = (df_inv['StandortGeografisch'] == 'Hegnabrunn') & (df_inv['Lagerzone'] == 'Lager Rack')
        if m_conf is not None:
            m_conf = (df_conf['StandortGeografisch'] == 'Hegnabrunn') & (df_conf['Lagerzone'] == 'Lager Rack')

    elif category == 'ARVATO':
        m_inv = (df_inv['StandortGeografisch'] == 'Elmshorn') & (df_inv['Lagerzone'] == 'Lager Rack')
        if m_conf is not None:
            m_conf = (df_conf['StandortGeografisch'] == 'Elmshorn') & (df_conf['Lagerzone'] == 'Lager Rack')

    # --- 3. Kapazitäts-Berechnung (Erst Filtern, dann Duplikate weg) ---
    capacity_val = 0
    if m_conf is not None and not df_conf.empty:
        df_c_filtered = df_conf[m_conf].copy()
        if not df_c_filtered.empty:
            # 1. Spalten sicherstellen und Numeric
            for col in ['MaxKapazitaetLagerzone', 'MaxKapazitaetHalle']:
                if col not in df_c_filtered.columns:
                    df_c_filtered[col] = 0
                else:
                    df_c_filtered[col] = pd.to_numeric(df_c_filtered[col], errors='coerce').fillna(0)

            # 2. Effektive Kapazität pro Zeile berechnen (Entweder Zone oder Halle)
            # Wir nehmen Zone, wenn > 0, sonst Halle.
            df_c_filtered['EffectiveCap'] = df_c_filtered.apply(
                lambda row: row['MaxKapazitaetLagerzone'] if row['MaxKapazitaetLagerzone'] > 0 else row['MaxKapazitaetHalle'],
                axis=1
            )

            # 3. Duplikate entfernen (Sensor-Level -> Storage Unit Level)
            # Nutzung von StorageHash wenn vorhanden, sonst Fallback auf Standort+Halle+Zone
            if 'StorageHash' in df_c_filtered.columns:
                df_c_unique = df_c_filtered.drop_duplicates(subset=['StorageHash'])
            else:
                # Fallback Key
                df_c_filtered['dedup_key'] = (
                    df_c_filtered['StandortGeografisch'].fillna('') + 
                    df_c_filtered['Lagerhalle'].fillna('') + 
                    df_c_filtered['Lagerzone'].fillna('') +
                    df_c_filtered['Fachbereich'].fillna('')
                )
                df_c_unique = df_c_filtered.drop_duplicates(subset=['dedup_key'])
            
            # 4. Summe bilden
            capacity_val = df_c_unique['EffectiveCap'].sum()

    # --- 4. Bestands-Berechnung ---
    df_inv_filtered = df_inv[m_inv].copy()
    if df_inv_filtered.empty:
        return 0, capacity_val, pd.DataFrame(columns=['Date', 'Value']), pd.DataFrame()

    # Historie (Summe oder Count)
    if metric_type == 'sum_unit':
        history = df_inv_filtered.groupby('Date')['MengeVerkaufseinheit'].sum().reset_index(name='Value')
    else:
        history = df_inv_filtered.groupby('Date').size().reset_index(name='Value')
    
    # Aktueller Tag
    df_curr = df_inv_filtered[df_inv_filtered['Date'] == latest_date]
    current_val = df_curr['MengeVerkaufseinheit'].sum() if metric_type == 'sum_unit' else len(df_curr)

    return current_val, capacity_val, history, df_curr


def render_tile(title, category_key, df_inv, df_conf, latest_date_norm):
    
    # Get Data
    current_val, capacity, history, df_details = get_filtered_metrics(category_key, df_inv, df_conf, latest_date_norm)
    
    # Determine Unit Label
    unit = "Karton" if category_key in ['DIET', 'LEAF'] else "Pal"
    
    with st.container(border=True):
        # --- ZEILE 1: LOGO (Linksbündig & Größer) ---
        logo_path = LOGO_MAP.get(category_key)
        if not logo_path:
            logo_path = LOGO_MAP.get('KN')
        
        # Spalten für linksbündige Ausrichtung (75% Breite für das Logo)
        log_col, _ = st.columns([3, 1]) 
        with log_col:
            if logo_path and os.path.exists(logo_path):
                st.image(logo_path, use_container_width=True)
            else:
                st.markdown(f"### {title}")

        # --- ZEILE 2: METRIKEN (Bestand & Auslastung/Kapazität) ---
        m1, m2 = st.columns(2)
        with m1:
            st.metric(label=f"Bestand ({unit})", value=f"{current_val:,.0f}")
            st.caption(f"Kapazität:")
        with m2:
            if capacity > 0:
                utilization = (current_val / capacity) * 100
                st.metric(label="Auslastung", value=f"{utilization:.1f}%")
                # Kapazität klein darunter für den vollen Überblick
                st.caption(f"{capacity:,.0f} {unit}")
            else:
                st.metric(label="Kapazität", value="n/a")

        # --- ZEILE 3: SPARKLINE (Historie) ---
        if not history.empty:
            fig = px.area(history, x='Date', y='Value')
            fig.update_layout(
                showlegend=False,
                margin=dict(l=0, r=0, t=5, b=5),
                height=50,
                xaxis=dict(visible=False),
                yaxis=dict(visible=False),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)'
            )
            fig.update_traces(
                line=dict(color='#0e2b63', width=2), 
                fillcolor='rgba(14, 43, 99, 0.1)'
            )
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        
        # --- ZEILE 4: DETAILS (Expander) ---
        with st.expander("🔎 Details"):
            if not df_details.empty:
                display_cols = ['Material', 'Artikeltext', 'Charge', 'MengeVerkaufseinheit', 'Lagerplatz']
                final_cols = [c for c in display_cols if c in df_details.columns]
                st.dataframe(df_details[final_cols], hide_index=True, use_container_width=True)
            else:
                st.info("Keine Detaildaten.")




def app():
    
    # Load Data
    with st.spinner("Lade Bestandsdaten..."):
        df_inv_raw, df_conf_raw, dfStammdaten = load_data()
    if df_inv_raw.empty:
        st.warning("Keine Bestandsdaten gefunden. Bitte prüfen Sie die Quelle.")
        return

    # Process
    df_inv, df_conf = process_data(df_inv_raw, df_conf_raw, dfStammdaten)
    #st.dataframe(df_inv.head(200))
    
    # Determine Latest Date (Global)
    if 'Date' in df_inv.columns:
        latest_date = df_inv['Date'].max()
    else:
        st.error("Fehler: Datumsspalte konnte nicht ermittelt werden.")
        return

    # --- 1. BAYREUTH HUB ---
    #st.markdown("---")
    # Layout: 5 Columns
    cols = st.columns(5)
    
    cats = ['DIET', 'LEAF', 'C&F', 'EXPORT', 'DOMESTIC']
    
    for i, cat in enumerate(cats):
        with cols[i]:
            render_tile(cat, cat, df_inv, df_conf, latest_date)

    st.markdown("---")

    # --- 2. KÜHNE & NAGEL ---
    
    # Layout: 5 Columns
    cols_kn = st.columns(5)
    kn_cities = ['München', 'Hamburg', 'Mainz', 'Duisburg', 'Berlin']
    
    for i, city in enumerate(kn_cities):
        with cols_kn[i]:
            render_tile(city, city, df_inv, df_conf, latest_date)

    st.markdown("---")

    # --- 3. RRP Läger ---
    
    cols_rrp = st.columns(5)
    rrp_cats = ['LOG-IN', 'ARVATO']

    for i, cat in enumerate(rrp_cats):
        with cols_rrp[i]:
            render_tile(cat, cat, df_inv, df_conf, latest_date)


if __name__ == "__main__":
    app()