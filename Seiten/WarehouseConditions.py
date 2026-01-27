import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import timedelta, datetime
from Data_Class.SynapseReader import SynapseReader

def create_simple_line_chart(df, data_col, time_col, title, color, unit, limits=None):
    if df.empty or df[data_col].isnull().all():
        return go.Figure().update_layout(title=f"{title} (Keine Daten)")
    
    fig = go.Figure()

    # Daten hinzufügen
    fig.add_trace(go.Scatter(
        x=df[time_col], 
        y=df[data_col],
        mode='lines', 
        name=title,
        line=dict(color=color, width=2)
    ))

    # Y-Achsen-Bereich bestimmen
    y_min_data = df[data_col].min()
    y_max_data = df[data_col].max()
    padding = (y_max_data - y_min_data) * 0.1 if (y_max_data - y_min_data) > 0 else 1 # 10% padding

    plot_y_min = y_min_data - padding
    plot_y_max = y_max_data + padding

    if limits:
        lower_bound, upper_bound = limits
        # Sorge dafür, dass die Limits im Plot sichtbar sind
        plot_y_min = min(plot_y_min, lower_bound - padding)
        plot_y_max = max(plot_y_max, upper_bound + padding)

        # --- Farbige Bereiche für Grenzwerte ---
        x_min_plot, x_max_plot = df[time_col].min(), df[time_col].max()

        # Grüner Bereich (OK)
        fig.add_shape(type="rect", xref="x", yref="y", x0=x_min_plot, y0=lower_bound, x1=x_max_plot, y1=upper_bound,
                      fillcolor="lightgreen", opacity=0.3, layer="below", line_width=0)
        
        # Roter Bereich (zu niedrig)
        fig.add_shape(type="rect", xref="x", yref="y", x0=x_min_plot, y0=plot_y_min, x1=x_max_plot, y1=lower_bound,
                      fillcolor="lightcoral", opacity=0.3, layer="below", line_width=0)

        # Roter Bereich (zu hoch)
        fig.add_shape(type="rect", xref="x", yref="y", x0=x_min_plot, y0=upper_bound, x1=x_max_plot, y1=plot_y_max,
                      fillcolor="lightcoral", opacity=0.3, layer="below", line_width=0)

    fig.update_layout(
        title=dict(text=title, font=dict(size=14)),
        margin=dict(l=10, r=10, t=40, b=10),
        height=250, 
        yaxis=dict(title=unit, showgrid=True, gridcolor='lightgrey', range=[plot_y_min, plot_y_max]),
        xaxis=dict(showgrid=False),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(255,255,255,0.5)',
        hovermode="x unified"
    )
    return fig

def app():
    # --- Daten Laden ---
    @st.cache_data(ttl=7700)
    def load_synapse_datasets():
        try:
            environmental_data = SynapseReader.load_delta("gold/EnvironmentalData/", as_pandas=True)
            violations_data = SynapseReader.load_delta("gold/StockViolationGermany/", as_pandas=True)
        except Exception as e:
            st.error(f"Fehler beim Laden der Synapse-Daten: {e}")
            return pd.DataFrame(), pd.DataFrame()
        return environmental_data, violations_data

    # Lade die CSV separat, damit sie nicht gecached wird und live bearbeitet werden kann
    try:
        #conditions_df = SynapseReader.read_csv_from_blob('raw/Logistics/Masterdata/ProductCategory_Thresholds.csv')
        conditions_df = pd.read_csv('Data/appData/Bedingungen.csv')
    except Exception as e:
        st.error(f"Fehler beim Laden der 'Bedingungen.csv': {e}")
        conditions_df = pd.DataFrame() # Fallback

    env_df, viol_df = load_synapse_datasets()


    if env_df.empty:
        st.warning("Keine Umgebungsdaten verfügbar.")
        return
    if conditions_df.empty:
        st.warning("Keine Bedingungsdaten (Bedingungen.csv) verfügbar.")
        return

    # --- Vorverarbeitung & Zeitzonen-Fix ---
    env_df['Messzeitpunkt'] = pd.to_datetime(env_df['Messzeitpunkt'], utc=True).dt.tz_localize(None)
    if env_df['Messwert'].dtype == object:
        env_df['Messwert'] = env_df['Messwert'].str.replace(',', '.').astype(float)
    
    if not viol_df.empty:
        viol_df['ViolationDate'] = pd.to_datetime(viol_df['ViolationDate'], utc=True).dt.tz_localize(None)

    # --- Globale Filter im Header ---
    st.header("Globale Filter")
    col1, col2 = st.columns(2)

    with col1:
        # Verwende die (potenziell bearbeitete) conditions_df für die Optionen
        global_product_category = st.selectbox(
            "Produktkategorie für Grenzwerte:",
            options=conditions_df['Product Category'].unique()
        )

    with col2:
        min_env_date = env_df['Messzeitpunkt'].min().date()
        max_env_date = env_df['Messzeitpunkt'].max().date()
        
        selected_date_range = st.date_input(
            "Zeitraum auswählen:",
            value=(max_env_date - timedelta(days=14), max_env_date),
            min_value=min_env_date,
            max_value=max_env_date,
        )
    
    # --- Expander zum Bearbeiten der Bedingungen ---
    with st.expander("Bedingungen anpassen"):
        st.info("Hier können die Bedingungen für die Produktkategorien bearbeitet werden. Änderungen werden erst nach dem Klick auf 'Speichern' übernommen.")
        
        with st.form(key="conditions_form"):
            edited_df = st.data_editor(
                conditions_df,
                num_rows="dynamic",
                width='stretch'
            )
            
            submitted = st.form_submit_button("Änderungen speichern")
            
            if submitted:
                try:
                    # Der Rückgabewert von st.data_editor in einem Formular ist das bearbeitete DataFrame
                    #edited_df.to_csv('Bedingungen.csv', index=False)
                    st.success("Die Bedingungen wurden erfolgreich in 'Bedingungen.csv' gespeichert!")
                    st.experimental_rerun()
                except Exception as e:
                    st.error(f"Fehler beim Speichern der Datei: {e}")

    if len(selected_date_range) != 2:
        st.warning("Bitte einen Start- und Enddatum auswählen.")
        return

    start_date, end_date = selected_date_range
    start_datetime = datetime.combine(start_date, datetime.min.time())
    end_datetime = datetime.combine(end_date, datetime.max.time())
    # --- Filter anwenden ---
    mask = (env_df['Messzeitpunkt'] >= start_datetime) & (env_df['Messzeitpunkt'] <= end_datetime)
    df_filtered = env_df.loc[mask].copy()

    if df_filtered.empty:
        st.warning(f"Keine Daten im ausgewählten Zeitraum ({start_date.strftime('%Y-%m-%d')} bis {end_date.strftime('%Y-%m-%d')}) gefunden.")
        return

    st.divider()

    # --- Grenzwerte aus der globalen Auswahl holen ---
    # Verwende die potenziell bearbeitete, aber neu geladene conditions_df
    if global_product_category not in conditions_df['Product Category'].unique():
        st.warning(f"Die ausgewählte Kategorie '{global_product_category}' existiert nicht mehr. Bitte eine neue auswählen.")
        st.stop()
        
    selected_condition = conditions_df[conditions_df['Product Category'] == global_product_category].iloc[0]
    temp_limits = (selected_condition['Temp LL (°C)'], selected_condition['Temp UL (°C)'])
    hum_limits = (selected_condition['RH LL (%)'], selected_condition['RH UL (%)'])

    # --- Visualisierung pro Bereich ---
    grouped = df_filtered.groupby(['StandortGeografisch', 'Lagerhalle'])

    for (standort, Lagerhalle), group_view in grouped:

        group = group_view.copy()
        
        st.subheader(f"📍 {standort} - {Lagerhalle}")
        st.write(f"Anzahl Messpunkte: {group['StorageHash'].nunique()} | Zeitraum: {group['Messzeitpunkt'].min().strftime('%Y-%m-%d')} bis {group['Messzeitpunkt'].max().strftime('%Y-%m-%d')}")
        st.write(f"Fachbereiche: {', '.join(group['Fachbereich'].unique())}")
        
        # Daten trennen
        temp_data = group[group['Typ'] == 'Temperatur'].sort_values('Messzeitpunkt')
        hum_data = group[group['Typ'] == 'Feuchte'].sort_values('Messzeitpunkt')
        
        # --- TÄGLICHER MEDIAN ---
        if not temp_data.empty:
            temp_data_median = temp_data.set_index('Messzeitpunkt').resample('D')['Messwert'].median().reset_index()
        else:
            temp_data_median = pd.DataFrame(columns=['Messzeitpunkt', 'Messwert'])

        if not hum_data.empty:
            hum_data_median = hum_data.set_index('Messzeitpunkt').resample('D')['Messwert'].median().reset_index()
        else:
            hum_data_median = pd.DataFrame(columns=['Messzeitpunkt', 'Messwert'])

        # Layout: 2 Spalten für die Kurven
        col_temp, col_hum = st.columns(2)
        
        with col_temp:
            fig_t = create_simple_line_chart(temp_data_median, 'Messwert', 'Messzeitpunkt', "Temperatur (Tagesmedian)", "#d62728", "°C", temp_limits)
            st.plotly_chart(fig_t, width='stretch')
            
        with col_hum:
            fig_h = create_simple_line_chart(hum_data_median, 'Messwert', 'Messzeitpunkt', "Luftfeuchtigkeit (Tagesmedian)", "#1f77b4", "%rF", hum_limits)
            st.plotly_chart(fig_h, width='stretch')

        # --- Violations anzeigen ---
        if not viol_df.empty:
            # Violation-Filterung an den globalen Zeitbereich anpassen
            viol_mask = (viol_df['ViolationDate'] >= start_datetime) & (viol_df['ViolationDate'] <= end_datetime)
            recent_violations = viol_df[viol_mask]
            
            area_hashes = group['StorageHash'].unique()
            area_violations = recent_violations[recent_violations['StorageHash'].isin(area_hashes)]
            
            if not area_violations.empty:
                expander_title = f"⚠️ {len(area_violations)} Bestands-Verstöße in diesem Bereich ({start_date.strftime('%Y-%m-%d')} bis {end_date.strftime('%Y-%m-%d')})"
                with st.expander(expander_title, expanded=False):
                    st.dataframe(
                        area_violations[['Artikelnummer', 'Artikelbeschreibung', 'ViolationReason', 'ExceededValue', 'LimitValue', 'ViolationDate']],
                        width='stretch',
                        hide_index=True
                    )
        with st.expander("Rohdaten dieser Bereichsanalyse anzeigen", expanded=False):
            st.dataframe(group.sort_values('Messzeitpunkt'), width='stretch')
        st.markdown("---")

if __name__ == "__main__":
    app()