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
    "BE5": "Berlin",
    "BF5": "Bielefeld",
    "ECH": "München",
    "GNM": "Berlin",
    "GRE": "Bielefeld",
    "HA5": "Hannover",
    "HH5": "Hamburg",
    "HRO": "Hamburg",
    "KIE": "Hamburg",
    "LE5": "Schkeuditz",
    "MA5": "Mainz",
    "RH5": "Duisburg",
    "MU5": "München",
    "NU5": "München",
    "PTD": "Berlin",
    "Rheine": "Duisburg",
    "ROW": "Hamburg",
    "ST5": "Gärtringen",
    "STB": "München",
    "STW": "München"
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
    code = str(row.get('ZEBRAXXSTATUSCODE', ''))
    if code == '8021':
        return "Geliefert", "#2ca02c"  # Grün
    else:
        return "Nicht geliefert", "#d62728"  # Rot



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
    # Ensure PLZ is string and 5 chars (leading zeros)
    df['PLZ'] = df['PLZ'].astype(str).str.zfill(5)
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

def plot_fancy_map(df, depot_name_mapping):
    if df.empty or 'latitude' not in df.columns:
        st.warning("Keine Geodaten verfügbar.")
        return go.Figure()

    df_map = df.copy()
    
    # Sicherstellen, dass die Status-Spalten existieren (falls Cache-Probleme vorliegen)
    if 'Status_Text' not in df_map.columns:
        df_map[['Status_Text', 'Color']] = df_map.apply(lambda row: pd.Series(get_status_category(row)), axis=1)

    # Depot Mapping
    df_map['DEPOT_NAME_DISPLAY'] = df_map['ZUSTELLENDESDEPOT'].map(depot_name_mapping).fillna(df_map['ZUSTELLENDESDEPOT'])

    depot_locations = {
        "Bielefeld": {"depot_lat": 52.0302, "depot_lon": 8.5325},
        "München": {"depot_lat": 48.1351, "depot_lon": 11.5820},
        "Berlin": {"depot_lat": 52.5200, "depot_lon": 13.4050},
        "Hamburg": {"depot_lat": 53.5511, "depot_lon": 9.9937},
        "Hannover": {"depot_lat": 52.3759, "depot_lon": 9.7320},
        "Duisburg": {"depot_lat": 51.4325, "depot_lon": 6.7623},
        "Schkeuditz": {"depot_lat": 51.3936, "depot_lon": 12.2230},
        "Gärtringen": {"depot_lat": 48.6410, "depot_lon": 8.8988},
        "Mainz": {"depot_lat": 49.9929, "depot_lon": 8.2473}
    }
    
    depot_centers = pd.DataFrame.from_dict(depot_locations, orient='index').reset_index()
    depot_centers.rename(columns={'index': 'DEPOT_NAME_DISPLAY'}, inplace=True)
    df_map = df_map.merge(depot_centers, on='DEPOT_NAME_DISPLAY', how='left')
    df_map = df_map.dropna(subset=['latitude', 'longitude', 'depot_lat', 'depot_lon'])

    fig = go.Figure()

    # Wir nutzen die tatsächlichen Werte, die in der Spalte vorkommen
    available_statuses = df_map['Status_Text'].unique()

    for status in available_statuses:
        subset = df_map[df_map['Status_Text'] == status]
        color = subset['Color'].iloc[0]
        
        # A. Linien
        lats, lons = [], []
        for _, row in subset.iterrows():
            lats.extend([row['depot_lat'], row['latitude'], None])
            lons.extend([row['depot_lon'], row['longitude'], None])
        
        fig.add_trace(go.Scattermapbox(
            mode="lines",
            lon=lons, lat=lats,
            line=dict(width=1, color=color),
            opacity=0.4, 
            name=f"Route {status}",
            showlegend=False,
            legendgroup=status
        ))

        # B. Kunden Punkte
        fig.add_trace(go.Scattermapbox(
            mode="markers",
            lon=subset['longitude'],
            lat=subset['latitude'],
            marker=dict(size=8, color=color),
            text=subset['NAME'] + "<br>Status: " + status,
            name=status,
            legendgroup=status
        ))

    # C. Depots (Immer Schwarz)
    active_depots = depot_centers[depot_centers['DEPOT_NAME_DISPLAY'].isin(df_map['DEPOT_NAME_DISPLAY'].unique())]
    fig.add_trace(go.Scattermapbox(
        mode="markers+text",
        lon=active_depots['depot_lon'],
        lat=active_depots['depot_lat'],
        marker=dict(size=14, color='black'),
        text=active_depots['DEPOT_NAME_DISPLAY'],
        textposition="top center",
        name="Depots"
    ))

    fig.update_layout(
        mapbox_style="carto-positron",
        mapbox_zoom=5.6,
        mapbox_center={"lat": 51.1657, "lon": 10.4515},
        margin={"r":0,"t":0,"l":0,"b":0},
        height=800,
        #legend=dict(bgcolor="rgba(255,255,255,0.7)")
    )
    #legende ausblenden 
    fig.update_layout(showlegend=False)
    return fig


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
            st.subheader("🏢 Depot Übersicht")
            
            # --- FIX: STRIKTES MAPPING FÜR DEPOT-KARTEN ---
            df_display = df.copy()
            # Mappen OHNE fillna(), damit unbekannte Depots zu NaN werden
            df_display['ZUSTELLENDESDEPOT_NAME'] = df_display['ZUSTELLENDESDEPOT'].map(DEPOT_NAME_MAPPING)
            
            # Alle Zeilen löschen, die keinem der 9 Hauptdepots zugeordnet werden konnten
            df_display = df_display.dropna(subset=['ZUSTELLENDESDEPOT_NAME'])
            
            # Jetzt erhalten wir maximal 9 Depots
            depots = sorted(df_display['ZUSTELLENDESDEPOT_NAME'].unique())
            
            if depots:
                # Wir erstellen 2 Spalten für die Depot-Karten (kompakteres Layout)
                col_d1, col_d2 = st.columns(2)

                for i, depot_name in enumerate(depots):
                    current_col = col_d1 if i % 2 == 0 else col_d2
                    
                    with current_col:
                        depot_df = df_display[df_display['ZUSTELLENDESDEPOT_NAME'] == depot_name]
                        total = len(depot_df)
                        delivered = len(depot_df[depot_df['ZEBRAXXSTATUSCODE'].astype(str) == '8021'])
                        
                        # Pünktlichkeit berechnen
                        delivered_df = depot_df[depot_df['ZEBRAXXSTATUSCODE'].astype(str) == '8021']
                        punctual_count = len(delivered_df[delivered_df['Is_Punctual'] == True])
                        punctuality_rate = (punctual_count / delivered * 100) if delivered > 0 else 0

                        # Gesamtwartezeit in Minuten
                        total_wait_min = depot_df['Wartezeit_min'].sum()
                        
                        with st.container(border=True):
                            # Titelzeile mit kleinem Icon
                            logo_col, title_col = st.columns([1, 4])
                            # Falls du das Kühne+Nagel Logo hast, wird es hier angezeigt, sonst Text
                            kn_logo_path = "Data/img/kuehne-nagel-logo-blue.png"
                            if os.path.exists(kn_logo_path):
                                logo_col.image(kn_logo_path, width=30)
                            
                            title_col.markdown(f"**{depot_name}**")

                            # 1. Status Text
                            st.caption(f"{delivered} von {total} zugestellt")
                            
                            # 2. Fortschrittsbalken
                            progress_value = (delivered / total) if total > 0 else 0
                            st.progress(progress_value)
                                
                            # 3. KPIs klein darunter
                            c_wait, c_punc = st.columns(2)
                            c_wait.write(f"⏳ {total_wait_min:.0f} min")
                            c_punc.write(f"⏱️ {punctuality_rate:.0f}%")

            else:
                st.info("Keine passenden Depot-Daten für das ausgewählte Datum.")


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
            st.dataframe(df, width='content')

if __name__ == "__main__":
    app()