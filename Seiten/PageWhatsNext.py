import streamlit as st
import pandas as pd
import plotly.express as px
import os
import datetime

# --- CONFIGURATION & LOGOS ---
# Paths to your logos (adjusted for 4 areas)
LOGO_MAP = {
    'DIET': 'data/gold/PalletPrediction/img/diet_logo.png',
    'LEAF': 'data/gold/PalletPrediction/img/leaf_logo.png',
    'FMC': 'data/gold/PalletPrediction/img/LC_LOGO.png',
    'CASING & FLAVOR': 'data/gold/PalletPrediction/img/C&F_LOGO.png', # Shared logo
    'OTHER': 'data/gold/PalletPrediction/img/truck.png'
}

# Colors for the 4 areas
COLOR_MAP = {
    'DIET': '#0e2b63',            # Dark Blue
    'LEAF': '#50af47',            # Green
    'FMC': '#ef7d00',             # Orange
    'CASING & FLAVOR': '#E72482', # Pink/Magenta (Combined)
    'OTHER': 'grey'
}

def map_business_area(value):
    """
    Cleans and groups Business Areas into exactly 4 categories.
    """
    val_str = str(value).upper()
    
    if 'DIET' in val_str:
        return 'DIET'
    elif 'LEAF' in val_str:
        return 'LEAF'
    # Combine Casing and Flavor
    elif 'CASING' in val_str or 'FLAVOUR' in val_str or 'FLAVOR' in val_str:
        return 'CASING & FLAVOR'
    # Combine Finished Goods and Domestic
    elif 'FINISHED' in val_str or 'DOMESTIC' in val_str or 'BUILDING BLOCK' in val_str:
        return 'FMC'
    else:
        return 'OTHER'

def render_logistics_header():
    col1, col2 = st.columns([1, 8])
    with col1:
        if os.path.exists('data/gold/PalletPrediction/img/truck.png'):
            st.image('data/gold/PalletPrediction/img/truck.png', width=80)
        else:
            st.markdown("## 🚛")
    with col2:
        st.markdown("""
            <h2 style='color:#0F2B63; font-family:Montserrat; margin-bottom:0px; padding-top:10px;'>
                OUTBOUND PLANNING BOARD (Ex Bayreuth)
            </h2>
            <p style='color:grey; font-family:Montserrat; margin-top:0px;'>
                Internal factory delivery & availability check (4 business areas)
            </p>
        """, unsafe_allow_html=True)

def format_logistics_quantity(row):
    """
    Prioritizes logistic units for display.
    """
    def fmt(val): return f"{val:,.0f}" if val % 1 == 0 else f"{val:,.1f}"
    
    # 1. Pallet
    if row['Quantity_in_D97_Pallet'] > 0:
        return f"<b>{fmt(row['Quantity_in_D97_Pallet'])} Pal</b> <span style='color:grey; font-size:0.8em;'>({fmt(row['Order_Quantity'])} {row['Order_Unit']})</span>"
    # 2. Case
    elif row['Quantity_in_CS_Case'] > 0:
        return f"<b>{fmt(row['Quantity_in_CS_Case'])} Case</b> <span style='color:grey; font-size:0.8em;'>({fmt(row['Order_Quantity'])} {row['Order_Unit']})</span>"
    # Fallback
    else:
        return f"<b>{fmt(row['Order_Quantity'])} {row['Order_Unit']}</b>"

@st.cache_data
def load_data():
    file_path = '/daten.csv'
    
    if not os.path.exists(file_path):
        st.error(f"File not found: {file_path}")
        return pd.DataFrame()

    try:
        # Load CSV
        df = pd.read_csv(file_path, na_values=['NULL', 'null', '-'])
        
        # Rename columns to English
        rename_map = {
            'Bestell_Menge': 'Order_Quantity',
            'Freier_Bestand_DE06_Summe': 'Free_Stock_DE06_Sum',
            'Menge_in_D97_Palette': 'Quantity_in_D97_Pallet',
            'Menge_in_CS_Case': 'Quantity_in_CS_Case',
            'Bestell_Einheit': 'Order_Unit',
            'Empfangs_Werk': 'Receiving_Plant',
            'Artikeltext': 'Article_Text',
            'Ist_im_Lager_gepickt': 'Is_Picked_in_Warehouse',
            'Ist_Goods_Issue_gebucht': 'Is_Goods_Issue_Posted',
            'Lieferschein_Nummer': 'Delivery_Note_Number'
        }
        df = df.rename(columns=rename_map)

        # Parse date (German format: Day.Month.Year)
        df['LoadingDateExBayreuth'] = pd.to_datetime(df['LoadingDateExBayreuth'], format='%d.%m.%Y', errors='coerce')
        # Filter LoadingDateExBayreuth is not in the past
        today = pd.Timestamp.today().normalize()
        df = df[df['LoadingDateExBayreuth'] >= today]
        
        # Clean numbers
        num_cols = ['Order_Quantity', 'Free_Stock_DE06_Sum', 'Quantity_in_D97_Pallet', 'Quantity_in_CS_Case']
        for col in num_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            else:
                df[col] = 0

        # Load new fields as strings to avoid errors
        str_cols = ['Shippingconditions_Effective', 'Is_Picked_in_Warehouse', 'Is_Goods_Issue_Posted', 'Delivery_Note_Number', 'EBELN']
        for col in str_cols:
            if col in df.columns:
                df[col] = df[col].astype(str).fillna('N/A')
            else:
                df[col] = 'N/A'

        # Map Shippingconditions_Effective
        shipping_map = {'Z1': 'Road', 'Z2': 'Sea', 'Z3': 'Air'}
        df['Shippingconditions_Effective_Display'] = df['Shippingconditions_Effective'].map(shipping_map).fillna(df['Shippingconditions_Effective'])

        # 1. Clean Business Area (group into 4)
        df['Display_Area'] = df['Business_Area'].apply(map_business_area)
        
        # 2. Shortage Check (Stock < Demand)
        df['Stock_Bottleneck'] = df['Order_Quantity'] > df['Free_Stock_DE06_Sum']
        
        # 3. Format display string
        df['Display_Quantity'] = df.apply(format_logistics_quantity, axis=1)
        
        # Sort
        df = df.sort_values('LoadingDateExBayreuth')
        
        return df
        
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

def app():
    # CSS
    st.markdown("""
        <style>
        [data-testid="stMetric"] {
            background-color: #ffffff;
            border: 1px solid #e6e6e6;
            padding: 10px;
            border-radius: 5px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        }
        </style>
    """, unsafe_allow_html=True)
    
    df = load_data()
    if df.empty:
        return

    # --- TIMELINE ---
    st.markdown("##### 📅 Loading Plan (Timeline)")
    
    fig_timeline = px.scatter(
        df, 
        x='LoadingDateExBayreuth', 
        y='Display_Area',
        size='Order_Quantity', 
        color='Display_Area',
        color_discrete_map=COLOR_MAP,
        symbol='Stock_Bottleneck',
        opacity=0.8,
        hover_data={'Display_Quantity': False, 'Receiving_Plant': True, 'Article_Text': True},
        height=300
    )
    fig_timeline.update_layout(
        font_family="Montserrat",
        plot_bgcolor="white",
        yaxis_title=None,
        xaxis_title="Planned Loading Date",
        showlegend=False,
        margin=dict(t=10, b=10)
    )
    fig_timeline.update_xaxes(showgrid=True, gridcolor='#eee', tickformat="%d.%m")
    fig_timeline.update_yaxes(showgrid=True, gridcolor='#eee')
    
    st.plotly_chart(fig_timeline, use_container_width=True, config={'displayModeBar': False})

    st.markdown("---")
    
    # --- 4 TILES (GRID) ---
    target_areas = ['DIET', 'LEAF', 'FMC', 'CASING & FLAVOR']
    cols = st.columns(4)
    
    # Shipping pictograms
    shipping_icons = {'Road': '🚚', 'Sea': '🚢', 'Air': '✈️'}

    for i, area in enumerate(target_areas):
        with cols[i]:
            df_area = df[df['Display_Area'] == area].copy()
            
            # Header Info
            sum_pal = df_area['Quantity_in_D97_Pallet'].sum()
            sum_kg = df_area['Order_Quantity'].sum()
            
            if sum_pal > 0:
                header_main = f"{sum_pal:,.0f} Pal"
                header_sub = f"({sum_kg:,.0f} kg)"
            else:
                header_main = f"{sum_kg:,.0f} kg"
                header_sub = "Total"

            # TILE START
            with st.container(border=True):
                logo = LOGO_MAP.get(area)
                if os.path.exists(logo):
                    st.image(logo, use_column_width=True)
                else:
                    st.write("📦")
                
                st.divider()
                
                # List of next shipments (grouped by EBELN)
                if df_area.empty:
                    st.caption("No open orders")
                else:
                    # Group by Purchase Order (EBELN)
                    grouped = df_area.groupby('EBELN').agg(
                        LoadingDateExBayreuth=('LoadingDateExBayreuth', 'min'),
                        Receiving_Plant=('Receiving_Plant', 'first'),
                        Order_Quantity=('Order_Quantity', 'sum'),
                        Stock_Bottleneck=('Stock_Bottleneck', 'any'),
                        Shippingconditions_Effective_Display=('Shippingconditions_Effective_Display', 'first'),
                        Article_Text_Count=('Article_Text', 'count'),
                        Display_Quantity=('Display_Quantity', 'first') # This will be tricky, let's just show total items
                    ).reset_index().sort_values('LoadingDateExBayreuth')

                    for _, row in grouped.head(5).iterrows():
                        date = row['LoadingDateExBayreuth'].strftime('%d.%m')
                        plant = row['Receiving_Plant']
                        num_items = row['Article_Text_Count']
                        
                        # Status icon for stock
                        if row['Stock_Bottleneck']:
                            icon = "🔴"
                            style = "color:#E72482;" # Red/Pink on error
                        else:
                            icon = "🟢"
                            style = "color:black;"

                        shipping_icon = shipping_icons.get(row['Shippingconditions_Effective_Display'], '❓')
                        
                        st.markdown(
                            f"""
                            <div style='font-size:12px; margin-bottom:6px; border-bottom:1px solid #f0f0f0; padding-bottom:4px;'>
                                <div style='display:flex; justify-content:space-between;'>
                                    <span>{icon} <b>{date}</b> <span style='color:grey'>➜ {plant}</span></span>
                                    <span>{shipping_icon} {row['EBELN']}</span>
                                </div>
                                <div style='{style} margin-top:2px;'>
                                    <b>{num_items} {"items" if num_items > 1 else "item"}</b> in order
                                </div>
                            </div>
                            """, 
                            unsafe_allow_html=True
                        )
                    
                    if len(grouped) > 5:
                        st.caption(f"+ {len(grouped)-5} more orders")
    st.data_editor(df)

if __name__ == "__main__":
    #st.set_page_config(layout="wide", page_title="Outbound Board")
    app()