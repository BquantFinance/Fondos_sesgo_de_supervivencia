import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import numpy as np
import re
import yfinance as yf
import pandas_datareader.data as wb

# Page configuration
st.set_page_config(
    page_title="Análisis Fondos CNMV - Sesgo de Supervivencia",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Ultra-modern CSS with animations and effects
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&display=swap');
    
    * {
        font-family: 'Space Grotesk', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }
    
    /* Animated gradient background */
    .stApp {
        background: linear-gradient(-45deg, #0a0a0a, #1a0f2e, #0f172a, #18181b);
        background-size: 400% 400%;
        animation: gradientShift 15s ease infinite;
    }
    
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    .main {
        background: transparent;
        padding: 0;
    }
    
    /* Neon glow metrics */
    [data-testid="metric-container"] {
        background: rgba(15, 15, 15, 0.6);
        backdrop-filter: blur(20px) saturate(200%);
        -webkit-backdrop-filter: blur(20px) saturate(200%);
        padding: 1.5rem;
        border-radius: 20px;
        border: 1px solid rgba(139, 92, 246, 0.2);
        box-shadow: 
            0 0 40px rgba(139, 92, 246, 0.1),
            inset 0 0 20px rgba(139, 92, 246, 0.05),
            0 10px 40px rgba(0, 0, 0, 0.5);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    [data-testid="metric-container"]::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(139, 92, 246, 0.3), transparent);
        transition: left 0.5s;
    }
    
    [data-testid="metric-container"]:hover::before {
        left: 100%;
    }
    
    [data-testid="metric-container"]:hover {
        transform: translateY(-5px) scale(1.02);
        border: 1px solid rgba(139, 92, 246, 0.5);
        box-shadow: 
            0 0 60px rgba(139, 92, 246, 0.3),
            inset 0 0 30px rgba(139, 92, 246, 0.1),
            0 20px 60px rgba(0, 0, 0, 0.7);
    }
    
    [data-testid="metric-container"] [data-testid="metric-label"] {
        color: #94a3b8;
        font-size: 0.7rem;
        font-weight: 600;
        letter-spacing: 2px;
        text-transform: uppercase;
        opacity: 0.9;
    }
    
    [data-testid="metric-container"] [data-testid="metric-value"] {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #8b5cf6 0%, #ec4899 50%, #06b6d4 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: textGradient 3s ease infinite;
        text-shadow: 0 0 40px rgba(139, 92, 246, 0.5);
    }
    
    @keyframes textGradient {
        0%, 100% { filter: hue-rotate(0deg); }
        50% { filter: hue-rotate(30deg); }
    }
    
    [data-testid="metric-container"] [data-testid="metric-delta"] {
        color: #64748b;
        font-size: 0.875rem;
        opacity: 0.8;
        font-weight: 500;
    }
    
    /* Glowing headers */
    h1 {
        color: #f1f5f9;
        font-weight: 800;
        font-size: 3rem;
        letter-spacing: -1px;
        margin-bottom: 0.5rem;
        text-shadow: 
            0 0 20px rgba(139, 92, 246, 0.5),
            0 0 40px rgba(139, 92, 246, 0.3);
        animation: pulse 2s ease-in-out infinite;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.9; }
    }
    
    h2 {
        color: #e2e8f0;
        font-weight: 600;
        font-size: 1.75rem;
        margin-top: 2rem;
        margin-bottom: 1rem;
        text-shadow: 0 0 10px rgba(139, 92, 246, 0.3);
    }
    
    h3 {
        color: #cbd5e1;
        font-weight: 500;
        font-size: 1.25rem;
        text-shadow: 0 0 5px rgba(139, 92, 246, 0.2);
    }
    
    /* Futuristic search input */
    .stTextInput > div > div > input {
        background: rgba(15, 15, 15, 0.8);
        border: 2px solid transparent;
        border-radius: 16px;
        padding: 1rem 1.5rem;
        font-size: 1rem;
        color: #f1f5f9;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        background-image: linear-gradient(rgba(15, 15, 15, 0.8), rgba(15, 15, 15, 0.8)),
                          linear-gradient(90deg, #8b5cf6, #ec4899, #06b6d4);
        background-origin: border-box;
        background-clip: padding-box, border-box;
    }
    
    .stTextInput > div > div > input:focus {
        box-shadow: 
            0 0 0 4px rgba(139, 92, 246, 0.1),
            0 0 30px rgba(139, 92, 246, 0.3),
            inset 0 0 20px rgba(139, 92, 246, 0.05);
        transform: translateY(-2px);
    }
    
    .stTextInput > div > div > input::placeholder {
        color: #64748b;
    }
    
    /* Holographic select box */
    .stSelectbox > div > div {
        background: rgba(15, 15, 15, 0.8);
        border-radius: 16px;
        border: 2px solid rgba(139, 92, 246, 0.2);
        color: #f1f5f9;
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
    }
    
    .stSelectbox > div > div:hover {
        border-color: rgba(139, 92, 246, 0.5);
        box-shadow: 0 0 20px rgba(139, 92, 246, 0.2);
    }
    
    /* Futuristic dataframe */
    [data-testid="stDataFrame"] {
        background: rgba(15, 15, 15, 0.6);
        border-radius: 20px;
        overflow: hidden;
        border: 1px solid rgba(139, 92, 246, 0.1);
        backdrop-filter: blur(10px);
        box-shadow: 
            0 0 40px rgba(139, 92, 246, 0.05),
            0 10px 40px rgba(0, 0, 0, 0.5);
    }
    
    .dataframe {
        font-size: 14px;
        border: none !important;
    }
    
    .dataframe thead tr th {
        background: linear-gradient(135deg, #8b5cf6 0%, #ec4899 100%) !important;
        color: white !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        font-size: 0.7rem !important;
        letter-spacing: 1.5px !important;
        padding: 1rem !important;
        border: none !important;
        text-shadow: 0 0 10px rgba(0, 0, 0, 0.5);
    }
    
    .dataframe tbody tr {
        background: rgba(15, 15, 15, 0.6) !important;
        border-bottom: 1px solid rgba(139, 92, 246, 0.05) !important;
        transition: all 0.3s ease !important;
    }
    
    .dataframe tbody tr:hover {
        background: linear-gradient(90deg, 
            rgba(139, 92, 246, 0.1) 0%, 
            rgba(236, 72, 153, 0.1) 50%, 
            rgba(6, 182, 212, 0.1) 100%) !important;
        transform: scale(1.01);
        box-shadow: 0 0 20px rgba(139, 92, 246, 0.2);
    }
    
    .dataframe tbody tr td {
        color: #e2e8f0 !important;
        border: none !important;
        padding: 0.75rem !important;
    }
    
    /* Animated tabs */
    .stTabs [data-baseweb="tab-list"] {
        background: rgba(15, 15, 15, 0.6);
        border-radius: 20px;
        padding: 0.5rem;
        gap: 0.5rem;
        border: 1px solid rgba(139, 92, 246, 0.1);
        backdrop-filter: blur(10px);
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 16px;
        color: #94a3b8;
        font-weight: 600;
        padding: 0.75rem 1.5rem;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    .stTabs [data-baseweb="tab"]::before {
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        width: 0;
        height: 0;
        border-radius: 50%;
        background: radial-gradient(circle, rgba(139, 92, 246, 0.3), transparent);
        transition: width 0.3s, height 0.3s, top 0.3s, left 0.3s;
    }
    
    .stTabs [data-baseweb="tab"]:hover::before {
        width: 100%;
        height: 100%;
        top: 0;
        left: 0;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        color: #e2e8f0;
        transform: translateY(-2px);
    }
    
    .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
        background: linear-gradient(135deg, #8b5cf6 0%, #ec4899 100%);
        color: white;
        box-shadow: 
            0 0 20px rgba(139, 92, 246, 0.4),
            0 4px 12px rgba(0, 0, 0, 0.3);
        animation: tabGlow 2s ease infinite;
    }
    
    @keyframes tabGlow {
        0%, 100% { box-shadow: 0 0 20px rgba(139, 92, 246, 0.4), 0 4px 12px rgba(0, 0, 0, 0.3); }
        50% { box-shadow: 0 0 30px rgba(139, 92, 246, 0.6), 0 4px 12px rgba(0, 0, 0, 0.3); }
    }
    
    /* Holographic author box */
    .author-box {
        background: linear-gradient(135deg, 
            rgba(139, 92, 246, 0.1) 0%, 
            rgba(236, 72, 153, 0.1) 50%, 
            rgba(6, 182, 212, 0.1) 100%);
        padding: 1rem 2rem;
        border-radius: 20px;
        margin: 1.5rem 0;
        text-align: center;
        border: 1px solid transparent;
        background-origin: border-box;
        background-clip: padding-box, border-box;
        font-size: 0.9rem;
        color: #94a3b8;
        position: relative;
        overflow: hidden;
        animation: holographic 3s ease infinite;
    }
    
    @keyframes holographic {
        0%, 100% { 
            background: linear-gradient(135deg, 
                rgba(139, 92, 246, 0.1) 0%, 
                rgba(236, 72, 153, 0.1) 50%, 
                rgba(6, 182, 212, 0.1) 100%);
        }
        50% { 
            background: linear-gradient(135deg, 
                rgba(6, 182, 212, 0.1) 0%, 
                rgba(139, 92, 246, 0.1) 50%, 
                rgba(236, 72, 153, 0.1) 100%);
        }
    }
    
    .author-box a {
        color: #c7d2fe;
        text-decoration: none;
        font-weight: 600;
        transition: all 0.3s ease;
        text-shadow: 0 0 10px rgba(139, 92, 246, 0.5);
    }
    
    .author-box a:hover {
        color: #e0e7ff;
        text-shadow: 0 0 20px rgba(139, 92, 246, 0.8);
    }
    
    /* Glowing info boxes */
    .info-box {
        background: rgba(99, 102, 241, 0.05);
        border-left: 4px solid;
        border-image: linear-gradient(180deg, #8b5cf6, #ec4899) 1;
        padding: 1rem 1.5rem;
        margin: 1rem 0;
        border-radius: 12px;
        color: #e2e8f0;
        backdrop-filter: blur(10px);
        position: relative;
        overflow: hidden;
    }
    
    .info-box::before {
        content: '';
        position: absolute;
        top: -2px;
        left: -2px;
        right: -2px;
        bottom: -2px;
        background: linear-gradient(45deg, #8b5cf6, #ec4899, #06b6d4, #8b5cf6);
        border-radius: 12px;
        opacity: 0;
        z-index: -1;
        transition: opacity 0.3s;
        animation: rotate 3s linear infinite;
    }
    
    .info-box:hover::before {
        opacity: 0.5;
    }
    
    @keyframes rotate {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
    
    .warning-box {
        background: rgba(239, 68, 68, 0.05);
        border-left: 4px solid #ef4444;
        padding: 1rem 1.5rem;
        margin: 1rem 0;
        border-radius: 12px;
        color: #fca5a5;
        backdrop-filter: blur(10px);
        animation: warningPulse 2s ease infinite;
    }
    
    @keyframes warningPulse {
        0%, 100% { box-shadow: 0 0 20px rgba(239, 68, 68, 0.2); }
        50% { box-shadow: 0 0 30px rgba(239, 68, 68, 0.4); }
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: rgba(15, 15, 15, 0.9);
        backdrop-filter: blur(20px);
        padding-top: 2rem;
        border-right: 1px solid rgba(139, 92, 246, 0.1);
    }
    
    /* Plotly charts */
    .js-plotly-plot {
        border-radius: 20px;
        overflow: hidden;
        border: 1px solid rgba(139, 92, 246, 0.1);
        box-shadow: 0 0 40px rgba(139, 92, 246, 0.05);
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Smooth scrolling */
    html {
        scroll-behavior: smooth;
    }
    
    /* Loading animation */
    .stSpinner > div {
        border-color: #8b5cf6;
    }
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(15, 15, 15, 0.5);
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, #8b5cf6, #ec4899);
        border-radius: 5px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(180deg, #a78bfa, #f9a8d4);
    }
</style>
""", unsafe_allow_html=True)

# Load and process data
@st.cache_data
def load_and_process_data():
    df = pd.read_csv('cnmv_funds_data_RAW_final_multipage.csv')
    
    def extract_date_from_filename(filename):
        match = re.search(r'(\d{2})-(\d{2})-(\d{4})_al_(\d{2})-(\d{2})-(\d{4})', filename)
        if match:
            end_date = pd.to_datetime(f"{match.group(6)}-{match.group(5)}-{match.group(4)}", format='%Y-%m-%d')
            return end_date
        return None
    
    df['date'] = df['file'].apply(extract_date_from_filename)
    df = df.dropna(subset=['date'])
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month
    df['year_month'] = df['date'].dt.to_period('M')
    
    return df

# Load macro data
@st.cache_data
def load_macro_data():
    try:
        start_date = '2004-01-01'
        end_date = '2025-12-31'
        
        indicators = {
            'LRHUTTTTESM156S': 'Spain_Unemployment',
            'VIXCLS': 'VIX',
            'DGS10': 'US_10Y_Bond'
        }
        
        macro_data = pd.DataFrame()
        for fred_code, name in indicators.items():
            try:
                series = wb.DataReader(fred_code, 'fred', start_date, end_date)
                series.columns = [name]
                if macro_data.empty:
                    macro_data = series
                else:
                    macro_data = macro_data.join(series, how='outer')
            except:
                continue
        
        macro_data = macro_data.ffill()
        return macro_data
    except:
        return pd.DataFrame()

# Load S&P 500 data
@st.cache_data
def load_sp500_data():
    try:
        sp500 = yf.download('^GSPC', start='2004-01-01', end='2025-12-31', progress=False, multi_level_index=False)
        sp500 = sp500[['Close', 'Volume']]
        sp500.columns = ['SP500', 'Volume']
        sp500['Returns'] = sp500['SP500'].pct_change() * 100
        sp500['MA50'] = sp500['SP500'].rolling(window=50).mean()
        sp500['MA200'] = sp500['SP500'].rolling(window=200).mean()
        return sp500
    except:
        return pd.DataFrame()

# Load main data
df = load_and_process_data()
macro_data = load_macro_data()
sp500_data = load_sp500_data()

# Calculate key metrics
births = df[df['status'] == 'NUEVAS_INSCRIPCIONES']
deaths = df[df['status'] == 'BAJAS']

total_births = len(births)
total_deaths = len(deaths)
mortality_rate = (total_deaths / total_births * 100) if total_births > 0 else 0
net_change = total_births - total_deaths

# Title with gradient animation
st.markdown("# 💎 Análisis de Fondos Españoles - Sesgo de Supervivencia")
st.markdown("""
<div class="author-box">
    <strong>Análisis del Sesgo de Supervivencia en Fondos de Inversión</strong><br>
    Por <a href="https://twitter.com/Gsnchez" target="_blank">@Gsnchez</a> • 
    <a href="https://bquantfinance.com" target="_blank">bquantfinance.com</a> • 
    Datos CNMV 2004-2025
</div>
""", unsafe_allow_html=True)

# Key metrics with enhanced styling
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="Total Fondos",
        value=f"{total_births:,}",
        delta="registrados"
    )

with col2:
    st.metric(
        label="Liquidados",
        value=f"{total_deaths:,}",
        delta=f"{mortality_rate:.0f}% mortalidad"
    )

with col3:
    st.metric(
        label="Activos",
        value=f"{total_births - total_deaths:,}",
        delta="estimados"
    )

with col4:
    st.metric(
        label="Sesgo",
        value=f"{abs(net_change):,}",
        delta="fondos ocultos",
        delta_color="inverse"
    )

# Main tabs
tabs = ["🔍 **Búsqueda de Fondos**", "🌊 **Ciclo Económico**", "📊 **Análisis Temporal**"]
tab_list = st.tabs(tabs)

# Tab 1: Fund Search
with tab_list[0]:
    st.markdown("### Búsqueda y Ciclo de Vida de Fondos")
    
    # Process lifecycle data
    births_lifecycle = births[births['N_Registro'].notna()].copy()
    deaths_lifecycle = deaths[deaths['N_Registro'].notna()].copy()
    
    unique_funds = births_lifecycle.groupby('N_Registro').agg({
        'Nombre': 'first',
        'date': 'min',
        'Gestora': 'first',
        'Depositaria': 'first'
    }).reset_index()
    unique_funds.columns = ['N_Registro', 'Nombre', 'Fecha_Alta', 'Gestora', 'Depositaria']
    
    death_dates = deaths_lifecycle.groupby('N_Registro')['date'].min().reset_index()
    death_dates.columns = ['N_Registro', 'Fecha_Baja']
    
    fund_lifecycle = unique_funds.merge(death_dates, on='N_Registro', how='left')
    fund_lifecycle['Vida_Anos'] = ((fund_lifecycle['Fecha_Baja'] - fund_lifecycle['Fecha_Alta']).dt.days / 365.25).round(1)
    fund_lifecycle['Estado_Actual'] = fund_lifecycle['Fecha_Baja'].apply(lambda x: '✅ Activo' if pd.isna(x) else '💀 Liquidado')
    
    # Search interface
    col1, col2 = st.columns([3, 1])
    
    with col1:
        search_term = st.text_input(
            "",
            placeholder="🔍 Buscar por nombre o número de registro...",
            help="Ej: CAIXASABADELL o 3043"
        )
    
    with col2:
        status_search = st.selectbox(
            "",
            options=['Todos', 'Activos', 'Liquidados'],
            index=0
        )
    
    # Apply filters
    filtered_lifecycle = fund_lifecycle.copy()
    
    if search_term:
        mask = (
            filtered_lifecycle['Nombre'].str.contains(search_term.upper(), case=False, na=False) |
            filtered_lifecycle['N_Registro'].astype(str).str.contains(search_term, na=False)
        )
        filtered_lifecycle = filtered_lifecycle[mask]
    
    if status_search == 'Activos':
        filtered_lifecycle = filtered_lifecycle[filtered_lifecycle['Fecha_Baja'].isna()]
    elif status_search == 'Liquidados':
        filtered_lifecycle = filtered_lifecycle[filtered_lifecycle['Fecha_Baja'].notna()]
    
    # Statistics
    total_in_search = len(filtered_lifecycle)
    active_in_search = len(filtered_lifecycle[filtered_lifecycle['Fecha_Baja'].isna()])
    liquidated_in_search = len(filtered_lifecycle[filtered_lifecycle['Fecha_Baja'].notna()])
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Fondos", f"{total_in_search:,}")
    
    with col2:
        st.metric("Activos", f"{active_in_search:,}", 
                  delta=f"{(active_in_search/total_in_search*100):.1f}%" if total_in_search > 0 else "0%")
    
    with col3:
        st.metric("Liquidados", f"{liquidated_in_search:,}",
                  delta=f"{(liquidated_in_search/total_in_search*100):.1f}%" if total_in_search > 0 else "0%")
    
    # Display results
    if total_in_search > 0:
        display_lifecycle = filtered_lifecycle.copy()
        display_lifecycle['N_Registro'] = display_lifecycle['N_Registro'].astype(int)
        display_lifecycle = display_lifecycle.sort_values('Fecha_Alta', ascending=False)
        
        display_lifecycle['Fecha_Alta'] = display_lifecycle['Fecha_Alta'].dt.strftime('%Y-%m-%d')
        display_lifecycle['Fecha_Baja'] = display_lifecycle['Fecha_Baja'].dt.strftime('%Y-%m-%d')
        
        display_cols = ['N_Registro', 'Nombre', 'Fecha_Alta', 'Fecha_Baja', 'Vida_Anos', 'Estado_Actual', 'Gestora', 'Depositaria']
        
        st.dataframe(
            display_lifecycle[display_cols],
            use_container_width=True,
            height=500,
            hide_index=True,
            column_config={
                "N_Registro": st.column_config.NumberColumn("Nº Registro", width="small"),
                "Nombre": st.column_config.TextColumn("Nombre del Fondo", width="large"),
                "Fecha_Alta": st.column_config.TextColumn("Fecha Alta", width="small"),
                "Fecha_Baja": st.column_config.TextColumn("Fecha Baja", width="small"),
                "Vida_Anos": st.column_config.NumberColumn("Vida (años)", format="%.1f", width="small"),
                "Estado_Actual": st.column_config.TextColumn("Estado", width="small"),
                "Gestora": st.column_config.TextColumn("Gestora", width="medium"),
                "Depositaria": st.column_config.TextColumn("Depositaria", width="medium")
            }
        )

# Tab 2: Economic Cycle with stunning visuals
with tab_list[1]:
    st.markdown("### 🌊 Mortalidad de Fondos y Ciclo Económico")
    
    # Prepare monthly data
    monthly_stats = df.groupby(['year', 'month', 'status']).size().unstack(fill_value=0)
    monthly_stats = monthly_stats.rename(columns={
        'NUEVAS_INSCRIPCIONES': 'Altas',
        'BAJAS': 'Bajas'
    })
    monthly_stats['Mortalidad'] = (monthly_stats['Bajas'] / monthly_stats['Altas'] * 100).fillna(0)
    monthly_stats['Balance'] = monthly_stats['Altas'] - monthly_stats['Bajas']
    monthly_stats = monthly_stats.reset_index()
    monthly_stats['date'] = pd.to_datetime(monthly_stats[['year', 'month']].assign(day=1))
    
    if not sp500_data.empty:
        # Create stunning 3D surface plot
        fig = go.Figure()
        
        # Add S&P 500 with gradient fill
        fig.add_trace(go.Scatter(
            x=sp500_data.index,
            y=sp500_data['SP500'],
            name='S&P 500',
            mode='lines',
            line=dict(width=0),
            fill='tozeroy',
            fillcolor='rgba(99, 102, 241, 0.3)',
            hovertemplate='S&P 500: $%{y:,.0f}<extra></extra>'
        ))
        
        # Add gradient line on top
        fig.add_trace(go.Scatter(
            x=sp500_data.index,
            y=sp500_data['SP500'],
            name='S&P 500',
            mode='lines',
            line=dict(
                width=3,
                color=sp500_data['SP500'],
                colorscale='Viridis',
                showscale=False
            ),
            showlegend=False,
            hovertemplate='S&P 500: $%{y:,.0f}<extra></extra>'
        ))
        
        # Add moving averages with glow effect
        fig.add_trace(go.Scatter(
            x=sp500_data.index,
            y=sp500_data['MA200'],
            name='MA 200',
            mode='lines',
            line=dict(color='#06b6d4', width=2, dash='dot'),
            opacity=0.7,
            hovertemplate='MA 200: $%{y:,.0f}<extra></extra>'
        ))
        
        # Create secondary y-axis for mortality spikes
        fig.add_trace(go.Bar(
            x=monthly_stats['date'],
            y=monthly_stats['Mortalidad'],
            name='Mortalidad (%)',
            yaxis='y2',
            marker=dict(
                color=monthly_stats['Mortalidad'],
                colorscale=[
                    [0, 'rgba(34, 197, 94, 0.4)'],
                    [0.5, 'rgba(251, 191, 36, 0.4)'],
                    [1, 'rgba(239, 68, 68, 0.8)']
                ],
                line=dict(width=0)
            ),
            hovertemplate='Mortalidad: %{y:.1f}%<extra></extra>'
        ))
        
        # Add crisis periods as gradient overlays
        crisis_periods = [
            {"name": "Crisis Financiera", "start": "2008-09-01", "end": "2009-06-01", "color": "rgba(239, 68, 68, 0.15)"},
            {"name": "Crisis Deuda EU", "start": "2011-08-01", "end": "2012-07-01", "color": "rgba(251, 191, 36, 0.15)"},
            {"name": "COVID-19", "start": "2020-02-01", "end": "2020-05-01", "color": "rgba(139, 92, 246, 0.15)"}
        ]
        
        for period in crisis_periods:
            fig.add_vrect(
                x0=period["start"],
                x1=period["end"],
                fillcolor=period["color"],
                layer="below",
                line_width=0,
                annotation_text=period["name"],
                annotation_position="top",
                annotation_font_color="#e2e8f0",
                annotation_font_size=10
            )
        
        # Update layout with dark theme and effects
        fig.update_layout(
            title={
                'text': 'S&P 500 vs Mortalidad de Fondos',
                'font': {'size': 24, 'color': '#e2e8f0', 'family': 'Space Grotesk'}
            },
            height=600,
            plot_bgcolor='rgba(15, 15, 15, 0.8)',
            paper_bgcolor='transparent',
            font=dict(family='Space Grotesk', color='#e2e8f0', size=12),
            hovermode='x unified',
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="top",
                y=1.1,
                xanchor="center",
                x=0.5,
                bgcolor='rgba(15, 15, 15, 0.8)',
                bordercolor='rgba(139, 92, 246, 0.3)',
                borderwidth=1,
                font=dict(size=11)
            ),
            xaxis=dict(
                gridcolor='rgba(139, 92, 246, 0.1)',
                showgrid=True,
                zeroline=False,
                tickfont=dict(size=10)
            ),
            yaxis=dict(
                title="S&P 500 Index",
                gridcolor='rgba(139, 92, 246, 0.1)',
                showgrid=True,
                zeroline=False,
                tickfont=dict(size=10)
            ),
            yaxis2=dict(
                title="Mortalidad (%)",
                overlaying='y',
                side='right',
                gridcolor='rgba(139, 92, 246, 0.05)',
                tickfont=dict(size=10)
            ),
            hoverlabel=dict(
                bgcolor='rgba(15, 15, 15, 0.9)',
                bordercolor='rgba(139, 92, 246, 0.5)',
                font=dict(color='#e2e8f0', size=12)
            )
        )
        
        # Add range slider with custom styling
        fig.update_xaxes(
            rangeslider=dict(
                visible=True,
                bgcolor='rgba(15, 15, 15, 0.6)',
                bordercolor='rgba(139, 92, 246, 0.3)',
                borderwidth=1,
                thickness=0.05
            )
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
    # Correlation Matrix with heatmap
    if not macro_data.empty:
        st.markdown("### 🔮 Matriz de Correlaciones")
        
        # Merge data for correlations
        monthly_macro = macro_data.resample('M').mean()
        correlation_data = monthly_stats.set_index('date').join(monthly_macro, how='inner')
        
        # Calculate correlation matrix
        corr_cols = ['Altas', 'Bajas', 'Mortalidad'] + [col for col in monthly_macro.columns if col in correlation_data.columns]
        if len(corr_cols) > 3:
            corr_matrix = correlation_data[corr_cols].corr()
            
            # Create beautiful heatmap
            fig_corr = go.Figure(data=go.Heatmap(
                z=corr_matrix.values,
                x=corr_matrix.columns,
                y=corr_matrix.columns,
                colorscale=[
                    [0, 'rgb(15, 15, 15)'],
                    [0.25, 'rgb(99, 102, 241)'],
                    [0.5, 'rgb(139, 92, 246)'],
                    [0.75, 'rgb(236, 72, 153)'],
                    [1, 'rgb(251, 191, 36)']
                ],
                text=corr_matrix.values.round(2),
                texttemplate='%{text}',
                textfont={"size": 12, "color": "white"},
                colorbar=dict(
                    title="Correlación",
                    titlefont=dict(color='#e2e8f0'),
                    tickfont=dict(color='#e2e8f0'),
                    bgcolor='rgba(15, 15, 15, 0.8)',
                    bordercolor='rgba(139, 92, 246, 0.3)',
                    borderwidth=1
                ),
                hovertemplate='%{x} vs %{y}<br>Correlación: %{z:.3f}<extra></extra>'
            ))
            
            fig_corr.update_layout(
                height=500,
                plot_bgcolor='rgba(15, 15, 15, 0.8)',
                paper_bgcolor='transparent',
                font=dict(family='Space Grotesk', color='#e2e8f0'),
                xaxis=dict(tickangle=45, tickfont=dict(size=11)),
                yaxis=dict(tickfont=dict(size=11)),
                hoverlabel=dict(
                    bgcolor='rgba(15, 15, 15, 0.9)',
                    bordercolor='rgba(139, 92, 246, 0.5)',
                    font=dict(color='#e2e8f0')
                )
            )
            
            st.plotly_chart(fig_corr, use_container_width=True)

# Tab 3: Temporal Analysis with advanced charts
with tab_list[2]:
    st.markdown("### 📊 Evolución Temporal del Sesgo")
    
    # Prepare yearly data
    yearly_stats = df.groupby(['year', 'status']).size().unstack(fill_value=0)
    yearly_stats = yearly_stats.rename(columns={
        'NUEVAS_INSCRIPCIONES': 'Altas',
        'BAJAS': 'Bajas'
    })
    yearly_stats['Cambio_Neto'] = yearly_stats['Altas'] - yearly_stats['Bajas']
    yearly_stats = yearly_stats.reset_index()
    
    # Create advanced 3D chart
    fig = go.Figure()
    
    # Add 3D-like bars for births
    for i, row in yearly_stats.iterrows():
        fig.add_trace(go.Bar(
            x=[row['year']],
            y=[row['Altas']],
            name='Altas' if i == 0 else '',
            marker=dict(
                color='rgba(34, 197, 94, 0.8)',
                line=dict(color='rgba(34, 197, 94, 1)', width=2)
            ),
            text=row['Altas'],
            textposition='outside',
            textfont=dict(color='#22c55e', size=14, family='Space Grotesk Bold'),
            hovertemplate=f'<b>{row["year"]}</b><br>Altas: {row["Altas"]}<extra></extra>',
            showlegend=(i == 0)
        ))
    
    # Add 3D-like bars for deaths
    for i, row in yearly_stats.iterrows():
        fig.add_trace(go.Bar(
            x=[row['year']],
            y=[-row['Bajas']],
            name='Bajas' if i == 0 else '',
            marker=dict(
                color='rgba(239, 68, 68, 0.8)',
                line=dict(color='rgba(239, 68, 68, 1)', width=2)
            ),
            text=row['Bajas'],
            textposition='outside',
            textfont=dict(color='#ef4444', size=14, family='Space Grotesk Bold'),
            hovertemplate=f'<b>{row["year"]}</b><br>Bajas: {row["Bajas"]}<extra></extra>',
            showlegend=(i == 0)
        ))
    
    # Add animated net change line
    fig.add_trace(go.Scatter(
        x=yearly_stats['year'],
        y=yearly_stats['Cambio_Neto'],
        name='Balance Neto',
        mode='lines+markers',
        line=dict(
            color='#fbbf24',
            width=4,
            shape='spline'
        ),
        marker=dict(
            size=12,
            color='#fbbf24',
            line=dict(width=3, color='rgba(15, 15, 15, 0.8)'),
            symbol='diamond'
        ),
        hovertemplate='<b>%{x}</b><br>Balance: %{y:+}<extra></extra>'
    ))
    
    # Add zero line with glow
    fig.add_hline(
        y=0,
        line_color='rgba(139, 92, 246, 0.5)',
        line_width=2,
        line_dash="dot",
        annotation_text="Equilibrio",
        annotation_position="right",
        annotation_font_color='#8b5cf6'
    )
    
    # Update layout with stunning effects
    fig.update_layout(
        title={
            'text': 'Evolución de Altas vs Bajas (2004-2025)',
            'font': {'size': 24, 'color': '#e2e8f0', 'family': 'Space Grotesk'}
        },
        xaxis_title="",
        yaxis_title="Número de Fondos",
        hovermode='x unified',
        height=600,
        plot_bgcolor='rgba(15, 15, 15, 0.8)',
        paper_bgcolor='transparent',
        font=dict(family='Space Grotesk', color='#e2e8f0'),
        barmode='relative',
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.05,
            xanchor="center",
            x=0.5,
            bgcolor='rgba(15, 15, 15, 0.8)',
            bordercolor='rgba(139, 92, 246, 0.3)',
            borderwidth=1,
            font=dict(size=12)
        ),
        xaxis=dict(
            gridcolor='rgba(139, 92, 246, 0.05)',
            showgrid=False,
            zeroline=False,
            tickfont=dict(size=11)
        ),
        yaxis=dict(
            gridcolor='rgba(139, 92, 246, 0.1)',
            showgrid=True,
            zeroline=False,
            tickfont=dict(size=11)
        ),
        hoverlabel=dict(
            bgcolor='rgba(15, 15, 15, 0.9)',
            bordercolor='rgba(139, 92, 246, 0.5)',
            font=dict(color='#e2e8f0', size=12)
        ),
        updatemenus=[
            dict(
                type="buttons",
                direction="left",
                buttons=list([
                    dict(
                        args=[{"visible": [True] * len(fig.data)}],
                        label="Todo",
                        method="update"
                    ),
                    dict(
                        args=[{"visible": [True if i < len(yearly_stats) * 2 else False for i in range(len(fig.data))]}],
                        label="Solo Barras",
                        method="update"
                    ),
                    dict(
                        args=[{"visible": [False if i < len(yearly_stats) * 2 else True for i in range(len(fig.data))]}],
                        label="Solo Línea",
                        method="update"
                    ),
                ]),
                pad={"r": 10, "t": 10},
                showactive=True,
                x=0.0,
                xanchor="left",
                y=1.15,
                yanchor="top",
                bgcolor='rgba(15, 15, 15, 0.8)',
                bordercolor='rgba(139, 92, 246, 0.3)',
                borderwidth=1,
                font=dict(color='#e2e8f0', size=11)
            ),
        ]
    )
    
    st.plotly_chart(fig, use_container_width=True)

# Footer
st.markdown("---")
st.markdown(f"""
<div style="text-align: center; color: #64748b; padding: 2rem 0; font-size: 0.875rem;">
    <p style="font-size: 1rem; color: #94a3b8;">Este análisis demuestra el severo sesgo de supervivencia en la industria de fondos española.</p>
    <p style="font-size: 1.2rem; color: #e2e8f0; font-weight: 600; text-shadow: 0 0 20px rgba(139, 92, 246, 0.5);">
        Tasa de mortalidad: {mortality_rate:.0f}%
    </p>
    <p style="margin-top: 1.5rem;">
        <a href="https://twitter.com/Gsnchez" target="_blank" style="color: #c7d2fe; text-shadow: 0 0 10px rgba(139, 92, 246, 0.5);">@Gsnchez</a> • 
        <a href="https://bquantfinance.com" target="_blank" style="color: #c7d2fe; text-shadow: 0 0 10px rgba(139, 92, 246, 0.5);">bquantfinance.com</a>
    </p>
</div>
""", unsafe_allow_html=True)
