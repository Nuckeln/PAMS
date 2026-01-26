import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pgeocode
import os
import ssl
import datetime
import re

# --- FIX: SSL Zertifikatsfehler umgehen ---
ssl._create_default_https_context = ssl._create_unverified_context

# --- Dummy Import Simulation ---
try:
    from Data_Class.SynapseReader import SynapseReader
except ImportError:
    SynapseReader = None

# Seiten-Konfiguration
st.set_page_config(page_title="Last Mile Analytics", layout="wide", page_icon="🚚")

# --- Globale Konstanten ---
DEPOT_NAME_MAPPING = {
    "BE5": "Bielefeld",
    "BF5": "Bielefeld",
    "ECH": "DE52 - München",
    "GNM": "DE53 - Berlin",
    "GRE": "Bielefeld",
    "HA5": "DE55 - Sehnde",
    "HH5": "DE54 - Hamburg",
    "HRO": "DE54 - Hamburg",
    "KIE": "DE54 - Hamburg",
    "LE5": "DE57 - Schkeuditz",
    "MA5": "Mainz",
    "MU5": "DE52 - München",
    "NU5": "DE52 - München",
    "PTD": "DE53 - Berlin",
    "Rheine": "DE56 - Duisburg",
    "ROW": "DE54 - Hamburg",
    "ST5": "DE59 - Gärtringen",
    "STB": "DE52 - München",
    "STW": "DE52 - München"
}


# --- 1. Helper Funktionen & Mapping (NEU ANGEPASST) ---

def check_punctuality(row):
    """
    Prüft Pünktlichkeit basierend auf Anlieferzeit-Fenster (z.B. '06:00 - 14:00')
    und tatsächlicher STARTSTANDZEIT.
    """
    # 1. Nur gelieferte Sendungen betrachten?
    if str(row.get('ZEBRAXXSTATUSCODE')) != '8021':
        return None 

    window = str(row.get('Anlieferzeit', ''))
    
    # 2. Kein Fenster -> Pünktlich
    if not window or window.lower() in ['nan', 'nat', 'none', '']:
        return True
        
    # 3. Tatsächliche Zeit
    arrival = row.get('STARTSTANDZEIT')
    if pd.isna(arrival):
        return None # Unbekannt
        
    arrival_time = arrival.time()
    
    # 4. Fenster parsen
    # Formate: "06:00 - 14:00", "6-14", "06:00-14:00"
    match = re.search(r'(\d{1,2}:?\d{0,2})\s*-\s*(\d{1,2}:?\d{0,2})', window)
    if match:
        start_str, end_str = match.groups()
        
        def parse_time(t_str):
            if ':' in t_str:
                return pd.to_datetime(t_str, format='%H:%M').time()
            else:
                return pd.to_datetime(t_str, format='%H').time()
        
        try:
            start_time = parse_time(start_str)
            end_time = parse_time(end_str)
            
            return start_time <= arrival_time <= end_time
        except:
            return None # Parsing Fehler
            
    return True

def get_status_category(row):
    """
    Exaktes Mapping nach Kundenvorgabe
    """
    code = str(row['ZEBRAXXSTATUSCODE'])
    
    # --- GRÜN: Erfolg ---
    if code == '8021':
        return "Erfolgreich zugestellt", "#2ca02c" # Sattgrün
        
    # --- BLAU: Unterwegs / Aktiv ---
    elif code == '8010':
        return "In Zustellung (bei Fahrer)", "#1f77b4" # Kräftiges Blau
        
    # --- HELLBLAU: Geplant / Noch im Depot ---
    elif code == '8001':
        return "Geplant / Papierprozess", "#aec7e8" # Helles Blau
        
    # --- ROT: Kritisch / Probleme ---
    elif code in ['8023', '8025', '8041']:
        # 8023: AV Kunde
        # 8025: Nicht übergeben (Streik etc)
        # 8041: Rücklauf im Depot
        return "Problem / Retoure", "#d62728" # Rot
        
    # --- GRAU: Storniert / Gelöscht ---
    elif code in ['8009', '8026', '8027']:
        return "Storniert / Gelöscht", "#7f7f7f" # Grau

    # Fallback
    return "Unbekannter Status", "#bcbd22"

@st.cache_data
def load_and_prep_data():
    if SynapseReader:
        df = SynapseReader.load_delta("silver/Logistics/Germany/Supplychain/LastMile/DDN/thirdparty_kn_ddn_bat_statusreporting/", as_pandas=True)
        df_kunden = pd.read_csv('Data/Kundenuebersicht_DSV_Hamburg.csv', sep=';')
        # Filter StatusDB = Aktiv or aktiv 
        df_kunden = df_kunden[df_kunden['Status DB'].isin(['Aktiv', 'aktiv'])]
    
        df_kunden = df_kunden.drop_duplicates(subset=['Customer#'], keep='last')
        #rename Customer# to KUNDENNUMMER
        df_kunden = df_kunden.rename(columns={'Customer#': 'KUNDENNUMMER'})

    else:
        # Dummy DataFrame für den Fall, dass SynapseReader nicht verfügbar ist
        df = pd.DataFrame()
        df_kunden = pd.DataFrame()

    # --- DATEN MERGE FÜR PÜNKTLICHKEIT ---
    if not df.empty and not df_kunden.empty:
         # Normalize IDs (Strip leading zeros)
        df['KUNDENNUMMER_norm'] = df['KUNDENNUMMER'].astype(str).str.lstrip('0')
        df_kunden['KUNDENNUMMER_norm'] = df_kunden['KUNDENNUMMER'].astype(str).str.lstrip('0')
        
        # Merge Anlieferzeit
        # Wir nehmen nur Anlieferzeit mit rüber
        if 'Anlieferzeit' in df_kunden.columns:
            df = df.merge(df_kunden[['KUNDENNUMMER_norm', 'Anlieferzeit']], on='KUNDENNUMMER_norm', how='left')

    # Geocoding
    nomi = pgeocode.Nominatim('de')
    plz_locations = df['PLZ'].unique()
    geo_data = nomi.query_postal_code(plz_locations.astype(str))
    
    geo_map = geo_data[['postal_code', 'latitude', 'longitude']].rename(columns={'postal_code': 'PLZ'})
    df['PLZ'] = df['PLZ'].astype(str)
    df = df.merge(geo_map, on='PLZ', how='left')

    # Datum
    df['LIEFERTERMIN'] = pd.to_datetime(df['LIEFERTERMIN'], errors='coerce')

    # --- NEU: Wartezeit ---
    for col in ['STARTSTANDZEIT', 'ENDESTANDZEIT']:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')

    if 'STARTSTANDZEIT' in df.columns and 'ENDESTANDZEIT' in df.columns:
        df['Wartezeit'] = df['ENDESTANDZEIT'] - df['STARTSTANDZEIT']
        # Nur positive Wartezeiten berücksichtigen
        df['Wartezeit'] = df['Wartezeit'].apply(lambda x: x if x.total_seconds() > 0 else pd.NaT)
        df['Wartezeit_min'] = df['Wartezeit'].dt.total_seconds() / 60
    else:
        # Fallback-Spalten erstellen, wenn sie nicht da sind
        df['Wartezeit_min'] = 0

    # Status Mapping (BRAUCHT TIME FÜR CHECK)
    df['Is_Punctual'] = df.apply(check_punctuality, axis=1)
    df[['Status_Text', 'Color']] = df.apply(lambda row: pd.Series(get_status_category(row)), axis=1)
    
    return df, df_kunden

# --- 2. Visualisierung: Die Map (ZOOM FIX) ---

def plot_fancy_map(df, depot_name_mapping):
    if df.empty or 'latitude' not in df.columns:
        st.warning("Keine Geodaten verfügbar.")
        return go.Figure()

    # Depot Zentren berechnen
    depot_centers = df.groupby('ZUSTELLENDESDEPOT')[['latitude', 'longitude']].mean().reset_index()
    depot_centers.rename(columns={'latitude': 'depot_lat', 'longitude': 'depot_lon'}, inplace=True)
    
    # Map depot codes to names for display
    depot_centers['DEPOT_NAME_DISPLAY'] = depot_centers['ZUSTELLENDESDEPOT'].map(depot_name_mapping).fillna(depot_centers['ZUSTELLENDESDEPOT'])
    
    df_map = df.merge(depot_centers, on='ZUSTELLENDESDEPOT', how='left')

    fig = go.Figure()

    # A. Linien (Spider)
    for status, color in df_map[['Status_Text', 'Color']].drop_duplicates().values:
        subset = df_map[df_map['Status_Text'] == status]
        lats = []
        lons = []
        for _, row in subset.iterrows():
            lats.append(row['depot_lat'])
            lats.append(row['latitude'])
            lats.append(None)
            lons.append(row['depot_lon'])
            lons.append(row['longitude'])
            lons.append(None)
        
        fig.add_trace(go.Scattermapbox(
            mode="lines",
            lon=lons,
            lat=lats,
            line=dict(width=1, color=color),
            opacity=0.5, # Etwas sichtbarer gemacht
            name=f"Route ({status})",
            hoverinfo='skip'
        ))

    # B. Kunden Punkte
    fig.add_trace(go.Scattermapbox(
        mode="markers",
        lon=df_map['longitude'],
        lat=df_map['latitude'],
        marker=dict(size=9, color=df_map['Color']),
        text=df_map['NAME'] + "<br>" + df_map['Status_Text'],
        name="Kunden"
    ))

    # C. Depots
    fig.add_trace(go.Scattermapbox(
        mode="markers+text",
        lon=depot_centers['depot_lon'],
        lat=depot_centers['depot_lat'],
        marker=dict(size=18, color='black', symbol='circle'), # Etwas größer
        text=depot_centers['DEPOT_NAME_DISPLAY'],
        textposition="top center",
        name="Depots"
    ))

    # --- MAP OPTIMIERUNG ---
    fig.update_layout(
        mapbox_style="carto-positron",
        mapbox_zoom=5.8, # <-- HIER: Zoom erhöht (näher ran)
        mapbox_center={"lat": 51.1657, "lon": 10.4515}, # Geometrisches Zentrum DE
        margin={"r":0,"t":0,"l":0,"b":0},
        height=800,
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01, bgcolor="rgba(255,255,255,0.8)")
    )
    
    return fig

# --- 3. Haupt-App ---

def app():
    # Daten laden
    df_raw, df_Kunden = load_and_prep_data()
    
    if df_raw.empty:
        st.error("Keine Daten geladen.")
        return

    # Datepicker
    st.markdown("---")
    col_filter, _ = st.columns([1, 3])
    with col_filter:
        selected_date = st.date_input(
            "📅 Lieferdatum auswählen:",
            value=pd.Timestamp.now().date()
        )
    
    # Filterung
    df = df_raw[df_raw['LIEFERTERMIN'].dt.date == selected_date]
    # st.dataframe(df, width='content')  
    # st.dataframe(df_Kunden, width='content')

    # --- KPI BEREICH (Angepasst an neue Codes) ---
    total_orders = len(df)
    
    # 8021 = Erfolg
    delivered = len(df[df['ZEBRAXXSTATUSCODE'].astype(str) == '8021'])
    # 8001, 8010 = Offen / Unterwegs
    pending = len(df[df['ZEBRAXXSTATUSCODE'].astype(str).isin(['8001', '8010'])])
    
    # Pünktlichkeit KPI
    global_punctuality = 0
    if delivered > 0:
        punctual_count = len(df[(df['ZEBRAXXSTATUSCODE'].astype(str) == '8021') & (df['Is_Punctual'] == True)])
        global_punctuality = (punctual_count / delivered) * 100

    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric("📦 Gesamtaufträge", total_orders)
    
    quote = 0
    if total_orders > 0:
        quote = round(delivered/total_orders*100, 1)
        
    kpi2.metric("✅ Erfolgreich", delivered, delta=f"{quote}%")
    kpi3.metric("⏱️ Pünktlichkeit (Global)", f"{global_punctuality:.1f}%")
    kpi4.metric("⏳ Offen / Unterwegs", pending)

    st.markdown("---")

    # --- LAYOUT ---
    col_map, col_depots = st.columns([2, 1.5])

    with col_map:
        st.subheader("📍 Live Auslieferungs-Karte")
        if not df.empty:
            map_fig = plot_fancy_map(df, DEPOT_NAME_MAPPING)
            st.plotly_chart(map_fig, use_container_width=True)
        else:
            st.info(f"Keine Aufträge für den {selected_date} gefunden.")

    with col_depots:

        
        # Temporäre Spalte für die Anzeige erstellen
        df_display = df.copy()
        df_display['ZUSTELLENDESDEPOT_NAME'] = df_display['ZUSTELLENDESDEPOT'].map(DEPOT_NAME_MAPPING).fillna(df_display['ZUSTELLENDESDEPOT'])
        
        depots = sorted(df_display['ZUSTELLENDESDEPOT_NAME'].unique())
        
        if depots:
            col_d1, col_d2 = st.columns(2)

            for i, depot_name in enumerate(depots):
                current_col = col_d1 if i % 2 == 0 else col_d2
                
                with current_col:
                    depot_df = df_display[df_display['ZUSTELLENDESDEPOT_NAME'] == depot_name]
                    total = len(depot_df)
                    delivered = len(depot_df[depot_df['ZEBRAXXSTATUSCODE'].astype(str) == '8021'])
                    
                    # Pünktlichkeit berechnen
                    # Wir schauen nur auf Delivered Items
                    delivered_df = depot_df[depot_df['ZEBRAXXSTATUSCODE'].astype(str) == '8021']
                    punctual_count = len(delivered_df[delivered_df['Is_Punctual'] == True])
                    punctuality_rate = 0
                    if delivered > 0:
                        punctuality_rate = (punctual_count / delivered) * 100

                    # Gesamtwartezeit berechnen
                    total_wait_min = depot_df['Wartezeit_min'].sum()
                    
                    with st.container(border=True):
                        logo_col, title_col = st.columns([1, 4])
                        kn_logo_path = "Data/img/kuehne-nagel-logo-blue.png"
                        if os.path.exists(kn_logo_path):
                            logo_col.image(kn_logo_path, width=30)
                        
                        title_col.markdown(f"**{depot_name}**")

                        # 1. Text: Zugestellt
                        st.write(f"{delivered} von {total} zugestellt.")
                        
                        # 2. Balken (Status)
                        if total > 0:
                            progress_value = delivered / total
                            st.progress(progress_value)
                        else:
                            st.progress(0)
                            
                        # 3. Wartezeit & Pünktlichkeit
                        c_wait, c_punc = st.columns(2)
                        c_wait.write(f"⏳ Wartezeit: {total_wait_min:.0f} min")
                        c_punc.write(f"⏱️ Pünktlich: {punctuality_rate:.1f}%")

        else:
            st.info("Keine Depot-Daten für das ausgewählte Datum.")

    # --- Top Kunden Übersicht ---
    st.markdown("---")
    st.subheader("🏆 Top Kunden Status")
    st.markdown("Übersicht Key-Accounts")
    
    logo_map = {
        "EDEKA": "Data/img/Kundenlogos/EDEKA.png",
        "NETTO": "Data/img/Kundenlogos/NETTO.png",
        "REWE": "Data/img/Kundenlogos/REWE.png",
        "HALL": "Data/img/Kundenlogos/HALL.jpg"
    }

    if not df.empty:
        # Decide on number of columns based on number of logos
        cols = st.columns(len(logo_map))

        for idx, (key, path) in enumerate(logo_map.items()):
            with cols[idx]:
                with st.container(border=True):
                    if os.path.exists(path):
                        st.image(path, width='content')
                    else:
                        st.markdown(f"**{key}**")
                    
                    client_df = df[df['NAME'].str.contains(key, case=False, na=False)]
                    
                    if not client_df.empty:
                        cnt = len(client_df)
                        fails = len(client_df[client_df['ZEBRAXXSTATUSCODE'].astype(str).isin(['8023', '8041', '8025'])])
                        avg_wait_time = client_df['Wartezeit_min'].mean()
                        
                        # Pünktlichkeit Kunde
                        client_del = client_df[client_df['ZEBRAXXSTATUSCODE'].astype(str) == '8021']
                        client_punc_rate = 0
                        if len(client_del) > 0:
                            p_cnt = len(client_del[client_del['Is_Punctual'] == True])
                            client_punc_rate = (p_cnt / len(client_del)) * 100

                        st.metric("Aufträge", f"{cnt}")
                        
                        if fails > 0:
                            st.metric("Kritisch", f"{fails}", delta=f"{fails * -1}")
                        else:
                            st.metric("Kritisch", "0", delta="0")

                        if not pd.isna(avg_wait_time) and avg_wait_time > 0:
                            st.metric("Ø Wartezeit", f"{avg_wait_time:.0f} min")
                        else:
                            st.metric("Ø Wartezeit", "-")
                            
                        st.metric("Pünktlichkeit", f"{client_punc_rate:.1f}%")
                    else:
                        st.caption("Keine Aufträge")
    else:
        st.info("Keine Kundendaten für das ausgewählte Datum.")

    # Detail Tabelle
    st.markdown("---")
    with st.expander("📋 Detaillierte Datentabelle ansehen"):
        if not df.empty:
            df_display_table = df.sort_values(by='ZEBRAXXSTATUSCODE', ascending=False).copy()
            df_display_table['ZUSTELLENDESDEPOT'] = df_display_table['ZUSTELLENDESDEPOT'].map(DEPOT_NAME_MAPPING).fillna(df_display_table['ZUSTELLENDESDEPOT'])
            
            # Formatiere Zeitstempel für Anzeige
            for c in ['STARTSTANDZEIT', 'ENDESTANDZEIT']:
                if c in df_display_table.columns:
                     df_display_table[c] = df_display_table[c].dt.strftime('%H:%M')

            # Show detailed columns
            cols_to_show = [
                'ZUSTELLENDESDEPOT', 
                'LIEFERTERMIN', 
                'NAME', 
                'ORT', 
                'Anlieferzeit',      # Lieferfenster
                'STARTSTANDZEIT',    # Ankunft
                'ENDESTANDZEIT',     # Abfahrt
                'Wartezeit_min',     # Dauer
                'Is_Punctual',       # Pünktlich?
                'ZEBRAXXSTATUSCODE', 
                'Status_Text'
            ]
            
            # Spalten umbenennen für User
            rename_map = {
                'ZUSTELLENDESDEPOT': 'Depot',
                'LIEFERTERMIN': 'Datum',
                'NAME': 'Kunde',
                'ORT': 'Ort',
                'Anlieferzeit': 'Lieferfenster',
                'STARTSTANDZEIT': 'Ankunft',
                'ENDESTANDZEIT': 'Abfahrt',
                'Wartezeit_min': 'Wartezeit (Min)',
                'Is_Punctual': 'Pünktlich',
                'ZEBRAXXSTATUSCODE': 'Code',
                'Status_Text': 'Status'
            }
            
            # Filtere nur vorhandene Spalten
            existing_cols = [c for c in cols_to_show if c in df_display_table.columns]
            
            st.dataframe(
                df_display_table[existing_cols].rename(columns=rename_map),
                width='content'
            )

if __name__ == "__main__":
    app()