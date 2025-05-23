import streamlit as st
import pandas as pd
import plotly.express as px
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
import datetime

@st.cache_data
def load_data():
    # Daten laden
    df_kunde = pd.read_excel(
        "/Users/martinwolf/Library/CloudStorage/OneDrive-BAT/ONEDRIVE MARTIN_/Auswertungen/Abrechnung DE/Kosten_Übersicht_Kunde.xlsx"
    )
    # Entferne LFTYP mit den werten ZLKE und ZLKS
    df_kunde = df_kunde[~df_kunde['LFART'].isin(['ZLKE', 'ZLKS'])]
    df_merged = pd.read_parquet('df_kunde.parquet')
    # Eingelesene CSV als einzige Datenquelle nutzen
    # Hier können Sie Ihre Daten laden
    
    return df_kunde, df_merged
def depot_mapping(df):
    # Mapping der Werke auf aussagekräftige Depotnamen
    depot_mapping = {
        'DE30': 'BAT Bayreuth',
        'DE52': 'K+N München',
        'DE53': 'K+N Berlin',
        'DE54': 'K+N Hamburg',
        'DE55': 'K+N Hannover',
        'DE56': 'K+N Duisburg',
        'DE57': 'K+N Leipzig',
        'DE58': 'K+N Mainz',
        'DE59': 'K+N Stuttgart',
        'DE11': 'LOG-IN Hegnabrunn',
        'DE19': 'Arvato Harsewinkel',
    }
    df['Depotname'] = df['WERKS'].map(depot_mapping)
    df['Depotname'] = df['Depotname'].fillna(df['WERKS'])

    # Zusätzliches Mapping für sprechende Spaltennamen
    depot_clarity_names = {
        'DE30': 'Bayreuth (BAT)',
        'DE52': 'München (K+N)',
        'DE53': 'Berlin (K+N)',
        'DE54': 'Hamburg (K+N)',
        'DE55': 'Hannover (K+N)',
        'DE56': 'Duisburg (K+N)',
        'DE57': 'Leipzig (K+N)',
        'DE58': 'Mainz (K+N)',
        'DE59': 'Stuttgart (K+N)',
        'DE11': 'Hegnabrunn (LOG-IN)',
        'DE19': 'Harsewinkel (Arvato)',
    }
    df['Depot_Klarname'] = df['WERKS'].map(depot_clarity_names).fillna(df['WERKS'])

    # Icon/Logo Mapping
    werks_logos = {
        'DE30': "Data/img/Domestic_LOGO.png",
        'DE52': "Data/img/kn_logo.png",
        'DE53': "Data/img/kn_logo.png",
        'DE54': "Data/img/kn_logo.png",
        'DE55': "Data/img/kn_logo.png",
        'DE56': "Data/img/kn_logo.png",
        'DE57': "Data/img/kn_logo.png",
        'DE58': "Data/img/kn_logo.png",
        'DE59': "Data/img/kn_logo.png",
        'DE11': "Data/img/logo_login_spedition.png",
        'DE19': "Data/img/arvato.png"
    }
    df['Depot_Logo'] = df['WERKS'].map(werks_logos).fillna("")

    depot_colors = {
        'DE30': '#0e2b63',  # darkBlue
        'DE52': '#004f9f',  # MidBlue
        'DE53': '#004f9f',
        'DE54': '#004f9f',
        'DE55': '#004f9f',
        'DE56': '#004f9f',
        'DE57': '#004f9f',
        'DE58': '#004f9f',
        'DE59': '#004f9f',
        'DE11': '#ef7d00',  # Orange
        'DE19': '#5a328a',  # Purple
    }
    df['Depot_Color'] = df['WERKS'].map(depot_colors).fillna("#999999")
    return df

# Extrahierte Funktion für Tab 1
def render_kosten_nach_depot(df_kunde):
    AgGrid(df_kunde)
    # Dynamischer Datumsfilter: Monat / Woche / Jahr
    gran = st.radio(
        "Filtern nach:",
        ["Monat", "Woche", "Jahr"],
        horizontal=True
    )
    if gran == "Monat":
        monate = sorted(
            df_kunde['JahrMonat'].dt.to_period('M').astype(str).unique(),
            reverse=True
        )
        sel = st.selectbox("Wähle Monat:", monate)
        start = pd.to_datetime(f"{sel}-01")
        end = start + pd.offsets.MonthEnd()
    elif gran == "Woche":
        # Kalenderwochen über ISO-Kalender bestimmen
        iso = df_kunde['JahrMonat'].dt.isocalendar()[['year', 'week']].drop_duplicates()
        iso = iso.sort_values(['year', 'week'], ascending=[False, False])
        labels = iso.apply(lambda r: f"{r['year']}-W{int(r['week']):02d}", axis=1).tolist()
        sel = st.selectbox("Wähle Kalenderwoche:", labels)
        year_str, week_str = sel.split('-W')
        year = int(year_str)
        week = int(week_str)
        # Berechne Start/End als pandas Timestamps
        start_date = datetime.date.fromisocalendar(year, week, 1)
        end_date = start_date + datetime.timedelta(days=6)
        start = pd.to_datetime(start_date)
        end = pd.to_datetime(end_date)
    else:  # Jahr
        jahre = sorted(
            df_kunde['JahrMonat'].dt.year.astype(str).unique(),
            reverse=True
        )
        sel = st.selectbox("Wähle Jahr:", jahre)
        start = pd.to_datetime(f"{sel}-01-01")
        end = pd.to_datetime(f"{sel}-12-31")
    # Daten filtern nach ausgewähltem Zeitraum
    df_q = df_kunde[(df_kunde['JahrMonat'] >= start) & (df_kunde['JahrMonat'] <= end)]
    # Gestapeltes Flächendiagramm je Werk über Zeit
    if gran == "Monat":
        df_ts = df_kunde.groupby(['JahrMonat', 'WERKS'], as_index=False).agg({
            'Kosten_LM': 'sum', 'Pickkosten': 'sum'
        })
        df_ts['Gesamtkosten'] = df_ts['Kosten_LM'] + df_ts['Pickkosten']
        df_ts = df_ts.sort_values('JahrMonat')
        fig = px.area(
            df_ts,
            x='JahrMonat', y='Gesamtkosten', color='WERKS',
            labels={'Gesamtkosten': 'Kosten (€)', 'JahrMonat': 'Monat'},
            title='Gesamtkosten im Zeitverlauf (Monatlich)'
        )
        # Annotation für den letzten Monat
        last = df_ts['JahrMonat'].max()
        total_last = df_ts[df_ts['JahrMonat'] == last]['Gesamtkosten'].sum()
        fig.add_annotation(
            x=last, y=total_last,
            text=f"€{total_last:,.0f}",
            showarrow=False, yshift=10
        )
    elif gran == "Jahr":
        df_ts = df_kunde.assign(Jahr=df_kunde['JahrMonat'].dt.year) \
            .groupby(['Jahr', 'WERKS'], as_index=False) \
            .agg({'Kosten_LM': 'sum', 'Pickkosten': 'sum'})
        df_ts['Gesamtkosten'] = df_ts['Kosten_LM'] + df_ts['Pickkosten']
        df_ts = df_ts.sort_values('Jahr')
        fig = px.area(
            df_ts,
            x='Jahr', y='Gesamtkosten', color='WERKS',
            labels={'Gesamtkosten': 'Kosten (€)', 'Jahr': 'Jahr'},
            title='Gesamtkosten im Zeitverlauf (Jährlich)'
        )
        # Annotation für das letzte Jahr
        last_year = df_ts['Jahr'].max()
        total_last_year = df_ts[df_ts['Jahr'] == last_year]['Gesamtkosten'].sum()
        fig.add_annotation(
            x=last_year, y=total_last_year,
            text=f"€{total_last_year:,.0f}",
            showarrow=False, yshift=10
        )
    else:
        st.info("Wöchentliche Zeitreihe derzeit nicht möglich")
        fig = None

    if fig is not None:
        fig.update_yaxes(tickformat="€,.0f")
        st.plotly_chart(fig, use_container_width=True)

    # Detailauswertung je Depot (Sunburst)
    st.markdown("### Detailauswertung je Depot")
    depots = df_q['WERKS'].unique()
    cols = st.columns(4)
    for i, depot in enumerate(depots):
        with cols[i % 4]:
            df_depot = df_q[df_q['WERKS'] == depot]
            # Header mit Logo, Depotname und Gesamtkosten
            depot_name = df_depot['Depot_Klarname'].iloc[0]
            logo_path = df_depot['Depot_Logo'].iloc[0]
            total_kosten = df_depot['Kosten_LM'].sum() + df_depot['Pickkosten'].sum()
            header_cols = st.columns([1, 2])
            with header_cols[0]:
                if logo_path:
                    st.image(logo_path)
            with header_cols[1]:
                st.markdown(f"### {depot_name}")
                st.markdown(f"**Gesamtkosten:** €{total_kosten:,.0f}")

            # Detaillierte Kostenaufteilung: Last Mile vs. Pickkosten
            kosten_summe = df_depot.groupby('LFART_Types')[['Kosten_LM', 'Pickkosten']].sum().reset_index()
            df_melt = kosten_summe.melt(
                id_vars=['LFART_Types'],
                value_vars=['Kosten_LM', 'Pickkosten'],
                var_name='Kostenart',
                value_name='Betrag'
            )
            df_melt = df_melt[df_melt['Betrag'] > 0]

            if not df_melt.empty:
                fig_detail = px.sunburst(
                    df_melt,
                    path=['LFART_Types', 'Kostenart'],
                    values='Betrag',
                    color='Betrag',
                    color_continuous_scale='Blues',
                    title=''
                )
                fig_detail.update_traces(texttemplate='%{label}<br>€ %{value:,.0f}')
                st.plotly_chart(fig_detail, use_container_width=True)
            else:
                st.info("Keine Daten")

def render_top_kunden(df_kunde):
    top10 = df_kunde.groupby("NAME1")["Gesamtkosten"].sum().nlargest(10).index.tolist()
    df_top = df_kunde[df_kunde["NAME1"].isin(top10)]
    df_plot = df_top.groupby(["JahrMonat", "NAME1"], as_index=False).agg({
        "Kosten_LM": "sum", "Pickkosten": "sum"
    })
    df_plot["Gesamtkosten"] = df_plot["Kosten_LM"] + df_plot["Pickkosten"]
    df_long = df_plot.melt(id_vars=["JahrMonat", "NAME1"], value_vars=["Kosten_LM", "Pickkosten"],
                           var_name="Kostenart", value_name="Betrag")
    df_long["Monat"] = df_long["JahrMonat"].dt.strftime("%Y-%m")

    fig = px.bar(df_long, x="Monat", y="Betrag", color="Kostenart",
                 facet_col="NAME1", facet_col_wrap=2, text_auto='.0f',
                 labels={"Betrag": "Kosten (€)"}, title="Kostenentwicklung – Top 10 Kunden")
    fig.update_layout(height=800)
    fig.update_yaxes(tickformat="€,.0f")
    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    st.plotly_chart(fig, use_container_width=True)

def render_zeitverlauf(df_kunde):
    df_sum = df_kunde.groupby("JahrMonat", as_index=False).agg({
        "Kosten_LM": "sum", "Pickkosten": "sum"
    })
    df_sum["Gesamtkosten"] = df_sum["Kosten_LM"] + df_sum["Pickkosten"]
    fig = px.line(df_sum, x="JahrMonat", y=["Kosten_LM", "Pickkosten", "Gesamtkosten"],
                  markers=True, labels={"value": "Kosten (€)", "variable": "Kostenart"},
                  title="Gesamtkosten im Zeitverlauf")
    fig.update_layout()
    fig.update_yaxes(tickformat="€,.0f")
    st.plotly_chart(fig, use_container_width=True)
    
def render_kundenanalyse(df_merged):
    st.header("👤 Kundenanalyse")
    # Filter-Elemente
    kunde = st.selectbox("Kunde auswählen", sorted(df_merged['NAME1'].unique()))
    start_date, end_date = st.date_input(
        "Zeitraum wählen",
        value=[df_merged['LFDAT'].min().date(), df_merged['LFDAT'].max().date()]
    )
    skus = st.multiselect("SKU auswählen", sorted(df_merged['MATNR'].unique()))
    produktarten = st.multiselect("Produktart auswählen", sorted(df_merged['MATKL'].dropna().unique()))

    # Daten filtern
    df_k = df_merged[df_merged['NAME1'] == kunde]
    df_k = df_k[(df_k['LFDAT'].dt.date >= start_date) & (df_k['LFDAT'].dt.date <= end_date)]
    if skus:
        df_k = df_k[df_k['MATNR'].isin(skus)]
    if produktarten:
        df_k = df_k[df_k['MATKL'].isin(produktarten)]

    # 1. Bestellprofil je SKU (Anzahl Lieferungen je MATNR)
    df_profile = df_k.groupby('MATNR').agg(
        Anzahl=('MATNR', 'count'),
        Durchschnitt_Menge=('LGMNG', 'mean')
    ).reset_index()
    fig1 = px.bar(
        df_profile, x='MATNR', y='Anzahl', text='Durchschnitt_Menge',
        labels={'Anzahl': 'Anzahl Lieferungen', 'Durchschnitt_Menge': 'Ø Menge'},
        title="Anzahl Lieferungen je SKU"
    )
    st.plotly_chart(fig1, use_container_width=True)

    # 2. Mengenverlauf über Zeit
    df_time = df_k.set_index('LFDAT').resample('M')['LGMNG'].sum().reset_index()
    fig2 = px.line(
        df_time, x='LFDAT', y='LGMNG',
        markers=True, title="Mengenverlauf (Monatlich)"
    )
    st.plotly_chart(fig2, use_container_width=True)

    # 3. Lieferintervall-Analyse
    df_k_sorted = df_k.sort_values('LFDAT')
    df_k_sorted['Intervall_Tage'] = df_k_sorted['LFDAT'].diff().dt.days
    fig3 = px.box(
        df_k_sorted, y='Intervall_Tage',
        title="Abstand zwischen Lieferungen (Tage)"
    )
    st.plotly_chart(fig3, use_container_width=True)
    st.metric("Median Lieferintervall (Tage)", int(df_k_sorted['Intervall_Tage'].median()))

    # 4. Heatmap Absatz pro SKU x Monat
    df_heat = df_k.copy()
    df_heat['Monat'] = df_heat['LFDAT'].dt.to_period('M').astype(str)
    df_heat = df_heat.groupby(['MATNR', 'Monat'])['LGMNG'].sum().reset_index()
    heat_data = df_heat.pivot(index='MATNR', columns='Monat', values='LGMNG').fillna(0)
    fig4 = px.imshow(
        heat_data, aspect='auto',
        labels={'x': 'Monat', 'y': 'SKU', 'color': 'Menge'},
        title="Absatz pro SKU und Monat"
    )
    st.plotly_chart(fig4, use_container_width=True)

    # 5. Lagenfaktor (Durchschnittliche Cases pro Paletten)
    df_lage = df_k.copy()
    df_lage['Lagenzahl'] = df_lage.apply(
        lambda row: row['Cases'] / row['Paletten'] if row['Paletten'] > 0 else None,
        axis=1
    )
    df_lage_summary = df_lage.groupby('Paletten').agg(
        Bestellungen=('LGMNG', 'count'),
        Ø_Cases_pro_Palette=('Lagenzahl', 'mean')
    ).reset_index()
    fig5 = px.bar(
        df_lage_summary, x='Paletten', y='Bestellungen',
        text='Ø_Cases_pro_Palette', labels={'Bestellungen': 'Anzahl Lieferungen', 'Ø_Cases_pro_Palette': 'Ø Cases/Palette'},
        title="Bestellungen je Palettenzahl"
    )
    st.plotly_chart(fig5, use_container_width=True)

    # 6. Wartezeiten nicht verfügbar
    st.info("Wartezeiten-Daten sind in der CSV nicht enthalten.")

def PageKostenreport():

    
    df_kunde, df_merged = load_data()
    st.subheader("📊 Logistikkosten-Analyse")

    df_kunde = depot_mapping(df_kunde)
    df_kunde['JahrMonat'] = pd.to_datetime(df_kunde['JahrMonat'], format="%Y%m")
    df_kunde['Gesamtkosten'] = df_kunde['Kosten_LM'] + df_kunde['Pickkosten']
    df_kunde['Quartal'] = df_kunde['JahrMonat'].dt.to_period("Q").astype(str)

    tab1, tab2, tab3, tab4 = st.tabs([
        "📦 Kosten nach Depot",
        "🏷️ Top Kunden",
        "📈 Zeitverlauf",
        "👤 Kundenanalyse"
    ])
    with tab1:
        render_kosten_nach_depot(df_kunde)
    # with tab2:
    #     render_top_kunden(df_kunde)
    # with tab3:
    #     render_zeitverlauf(df_kunde)
    # with tab4:
    #     render_kundenanalyse(df_merged)
