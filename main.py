import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import numpy as np
import re
import warnings
warnings.filterwarnings('ignore')

# Page configuration
st.set_page_config(
    page_title="Análisis Fondos CNMV - Sesgo de Supervivencia",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Dark mode aesthetic CSS (keeping the same styles)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }
    
    .stApp {
        background: #0f0f0f;
    }
    
    .main {
        background: #0f0f0f;
        padding: 0;
    }
    
    /* Metrics with dark glassmorphism */
    [data-testid="metric-container"] {
        background: linear-gradient(135deg, rgba(30, 30, 30, 0.9) 0%, rgba(20, 20, 20, 0.9) 100%);
        padding: 1.5rem;
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.05);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
    }
    
    [data-testid="metric-container"]:hover {
        transform: translateY(-2px);
        border: 1px solid rgba(99, 102, 241, 0.3);
        box-shadow: 0 12px 40px rgba(99, 102, 241, 0.1);
    }
    
    [data-testid="metric-container"] [data-testid="metric-label"] {
        color: #94a3b8;
        font-size: 0.75rem;
        font-weight: 500;
        letter-spacing: 1px;
        text-transform: uppercase;
        opacity: 0.8;
    }
    
    [data-testid="metric-container"] [data-testid="metric-value"] {
        color: #f1f5f9;
        font-size: 2rem;
        font-weight: 700;
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    [data-testid="metric-container"] [data-testid="metric-delta"] {
        color: #64748b;
        font-size: 0.875rem;
        opacity: 0.7;
    }
    
    /* Headers */
    h1 {
        color: #f1f5f9;
        font-weight: 700;
        font-size: 2.5rem;
        letter-spacing: -1px;
        margin-bottom: 0.5rem;
    }
    
    h2 {
        color: #e2e8f0;
        font-weight: 600;
        font-size: 1.75rem;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    
    h3 {
        color: #cbd5e1;
        font-weight: 500;
        font-size: 1.25rem;
    }
    
    /* Search input styling */
    .stTextInput > div > div > input {
        background: rgba(30, 30, 30, 0.9);
        border: 1px solid rgba(99, 102, 241, 0.2);
        border-radius: 12px;
        padding: 0.75rem 1rem;
        font-size: 1rem;
        color: #f1f5f9;
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #6366f1;
        box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
        background: rgba(30, 30, 30, 1);
    }
    
    .stTextInput > div > div > input::placeholder {
        color: #64748b;
    }
    
    /* Select box styling */
    .stSelectbox > div > div {
        background: rgba(30, 30, 30, 0.9);
        border-radius: 12px;
        border: 1px solid rgba(99, 102, 241, 0.2);
        color: #f1f5f9;
    }
    
    /* Dataframe styling */
    [data-testid="stDataFrame"] {
        background: rgba(30, 30, 30, 0.9);
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid rgba(99, 102, 241, 0.1);
    }
    
    .dataframe {
        font-size: 14px;
        border: none !important;
    }
    
    .dataframe thead tr th {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%) !important;
        color: white !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        font-size: 0.75rem !important;
        letter-spacing: 1px !important;
        padding: 1rem !important;
        border: none !important;
    }
    
    .dataframe tbody tr {
        background: rgba(30, 30, 30, 0.9) !important;
        border-bottom: 1px solid rgba(255, 255, 255, 0.05) !important;
    }
    
    .dataframe tbody tr:hover {
        background: rgba(99, 102, 241, 0.1) !important;
    }
    
    .dataframe tbody tr td {
        color: #e2e8f0 !important;
        border: none !important;
        padding: 0.75rem !important;
    }
    
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        background: rgba(30, 30, 30, 0.5);
        border-radius: 16px;
        padding: 0.5rem;
        gap: 0.5rem;
        border: 1px solid rgba(99, 102, 241, 0.1);
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 12px;
        color: #94a3b8;
        font-weight: 500;
        padding: 0.75rem 1.5rem;
        transition: all 0.3s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(99, 102, 241, 0.1);
        color: #e2e8f0;
    }
    
    .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        color: white;
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.25);
    }
    
    /* Author box */
    .author-box {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%);
        padding: 1rem 2rem;
        border-radius: 16px;
        margin: 1.5rem 0;
        text-align: center;
        border: 1px solid rgba(99, 102, 241, 0.2);
        font-size: 0.9rem;
        color: #94a3b8;
    }
    
    .author-box a {
        color: #a5b4fc;
        text-decoration: none;
        font-weight: 600;
        transition: color 0.3s ease;
    }
    
    .author-box a:hover {
        color: #c7d2fe;
    }
    
    /* Info boxes */
    .info-box {
        background: rgba(99, 102, 241, 0.1);
        border-left: 4px solid #6366f1;
        padding: 1rem 1.5rem;
        margin: 1rem 0;
        border-radius: 8px;
        color: #e2e8f0;
    }
    
    .warning-box {
        background: rgba(239, 68, 68, 0.1);
        border-left: 4px solid #ef4444;
        padding: 1rem 1.5rem;
        margin: 1rem 0;
        border-radius: 8px;
        color: #fca5a5;
    }
    
    .data-quality-box {
        background: rgba(251, 191, 36, 0.1);
        border-left: 4px solid #fbbf24;
        padding: 1rem 1.5rem;
        margin: 1rem 0;
        border-radius: 8px;
        color: #fde047;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: #1a1a1a;
        padding-top: 2rem;
    }
    
    /* Radio buttons */
    .stRadio > label {
        color: #e2e8f0;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    
    /* Plotly charts background */
    .js-plotly-plot {
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid rgba(99, 102, 241, 0.1);
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
        border-color: #6366f1;
    }
</style>
""", unsafe_allow_html=True)

# Load and process data with data quality checks
@st.cache_data
def load_and_process_data():
    df = pd.read_csv('cnmv_funds_data_FINAL.csv')
    
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
    
    # Data quality: remove duplicates if any
    df = df.drop_duplicates(subset=['N_Registro', 'status', 'date'])
    
    return df

# Load main data
df = load_and_process_data()

# Process lifecycle data with enhanced data quality checks
@st.cache_data
def process_lifecycle_data(df):
    births = df[df['status'] == 'NUEVAS_INSCRIPCIONES']
    deaths = df[df['status'] == 'BAJAS']
    
    births_lifecycle = births[births['N_Registro'].notna()].copy()
    deaths_lifecycle = deaths[deaths['N_Registro'].notna()].copy()
    
    # Get unique funds with their first registration
    unique_funds = births_lifecycle.groupby('N_Registro').agg({
        'Nombre': 'first',
        'date': 'min',  # First registration date
        'Gestora': 'first',
        'Depositaria': 'first'
    }).reset_index()
    unique_funds.columns = ['N_Registro', 'Nombre', 'Fecha_Alta', 'Gestora', 'Depositaria']
    
    # Get death dates (first death date if multiple)
    death_dates = deaths_lifecycle.groupby('N_Registro')['date'].min().reset_index()
    death_dates.columns = ['N_Registro', 'Fecha_Baja']
    
    # Merge to create lifecycle
    fund_lifecycle = unique_funds.merge(death_dates, on='N_Registro', how='left')
    
    # Calculate life in years
    fund_lifecycle['Vida_Anos'] = ((fund_lifecycle['Fecha_Baja'] - fund_lifecycle['Fecha_Alta']).dt.days / 365.25).round(1)
    
    # DATA QUALITY CHECKS AND CLEANING
    initial_count = len(fund_lifecycle)
    
    # 1. Remove records where death date is before birth date (negative life)
    invalid_dates = fund_lifecycle['Vida_Anos'] < 0
    num_invalid_dates = invalid_dates.sum()
    
    # 2. Remove records with unreasonably long life (e.g., > 50 years)
    too_long_life = fund_lifecycle['Vida_Anos'] > 50
    num_too_long = too_long_life.sum()
    
    # 3. Keep track of removed records for reporting
    removed_records = fund_lifecycle[invalid_dates | too_long_life].copy()
    
    # 4. Clean the data
    fund_lifecycle = fund_lifecycle[~invalid_dates & ~too_long_life]
    
    # 5. Also remove funds with same birth and death date (0 days life) if suspicious
    zero_life = (fund_lifecycle['Vida_Anos'] == 0) & fund_lifecycle['Fecha_Baja'].notna()
    num_zero_life = zero_life.sum()
    
    # Optional: remove zero-life funds if they seem erroneous
    # fund_lifecycle = fund_lifecycle[~zero_life]
    
    # Add status column
    fund_lifecycle['Estado_Actual'] = fund_lifecycle['Fecha_Baja'].apply(lambda x: '✅ Activo' if pd.isna(x) else '💀 Liquidado')
    fund_lifecycle['Año_Alta'] = fund_lifecycle['Fecha_Alta'].dt.year
    fund_lifecycle['Año_Baja'] = fund_lifecycle['Fecha_Baja'].dt.year
    
    # Create data quality report
    quality_report = {
        'initial_count': initial_count,
        'invalid_dates': num_invalid_dates,
        'too_long_life': num_too_long,
        'zero_life': num_zero_life,
        'final_count': len(fund_lifecycle),
        'removed_records': removed_records
    }
    
    return fund_lifecycle, quality_report

# Process lifecycle data with quality checks
fund_lifecycle, quality_report = process_lifecycle_data(df)

# Calculate key metrics using cleaned data
births = df[df['status'] == 'NUEVAS_INSCRIPCIONES']
deaths = df[df['status'] == 'BAJAS']

total_births = len(births)
total_deaths = len(deaths)
mortality_rate = (total_deaths / total_births * 100) if total_births > 0 else 0
net_change = total_births - total_deaths

# Title
st.markdown("# 📊 Análisis de Fondos Españoles - Sesgo de Supervivencia")
st.markdown("""
<div class="author-box">
    <strong>Análisis del Sesgo de Supervivencia en Fondos de Inversión 11/2004 - 09/2025</strong><br>
    Por <a href="https://twitter.com/Gsnchez" target="_blank">@Gsnchez</a> • 
    <a href="https://bquantfinance.com" target="_blank">bquantfinance.com</a> • 
    Datos CNMV 2004-2025
</div>
""", unsafe_allow_html=True)

# Newsletter banner
st.markdown("""
<div style='background: rgba(99, 102, 241, 0.1); border: 1px solid rgba(99, 102, 241, 0.3); padding: 20px; border-radius: 12px; margin: 20px 0; text-align: center;'>
    <h3 style='color: #a5b4fc; margin: 0 0 10px 0;'>📬 BQuant Fund Lab Newsletter</h3>
    <p style='color: #94a3b8; margin: 0 0 15px 0;'>Análisis cuantitativo de fondos</p>
    <a href='https://bquantfundlab.substack.com/' target='_blank' style='background: #6366f1; color: white; padding: 10px 20px; border-radius: 8px; text-decoration: none; display: inline-block;'>Suscribirse →</a>
</div>
""", unsafe_allow_html=True)

# Key metrics at top
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
    # Use cleaned data for active count
    active_funds = len(fund_lifecycle[fund_lifecycle['Fecha_Baja'].isna()])
    st.metric(
        label="Activos",
        value=f"{active_funds:,}",
        delta="validados"
    )

with col4:
    st.metric(
        label="Sesgo",
        value=f"{abs(net_change):,}",
        delta="fondos ocultos",
        delta_color="inverse"
    )

# Main tabs
tabs = ["🔍 **Búsqueda de Fondos**", "📊 **Análisis Temporal**", "🔬 **Calidad de Datos**"]
tab_list = st.tabs(tabs)

# Tab 1: Fund Search (Enhanced)
with tab_list[0]:
    st.markdown("### Búsqueda y Ciclo de Vida de Fondos")
    
    # Enhanced search interface with multiple filters
    st.markdown("#### 🔍 Filtros de Búsqueda")
    
    # First row of filters
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        search_term = st.text_input(
            "Buscar por Nombre o Nº Registro",
            placeholder="Ej: CAIXASABADELL o 3043...",
            help="Búsqueda por nombre del fondo o número de registro"
        )
    
    with col2:
        status_search = st.selectbox(
            "Estado",
            options=['Todos', 'Activos', 'Liquidados'],
            index=0
        )
    
    with col3:
        # Get unique years for filter
        all_years = sorted(list(set(fund_lifecycle['Año_Alta'].dropna().astype(int).tolist() + 
                                  fund_lifecycle['Año_Baja'].dropna().astype(int).tolist())))
        
        year_range = st.select_slider(
            "Rango de Años",
            options=all_years,
            value=(min(all_years), max(all_years)),
            help="Filtra fondos activos en este período"
        )
    
    # Second row of filters
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        # Get unique Gestoras
        gestoras = ['Todas'] + sorted(fund_lifecycle['Gestora'].dropna().unique().tolist())
        selected_gestora = st.selectbox(
            "Gestora",
            options=gestoras,
            index=0
        )
    
    with col2:
        # Get unique Depositarias
        depositarias = ['Todas'] + sorted(fund_lifecycle['Depositaria'].dropna().unique().tolist())
        selected_depositaria = st.selectbox(
            "Depositaria",
            options=depositarias,
            index=0
        )
    
    with col3:
        vida_filter = st.select_slider(
            "Vida del Fondo (años)",
            options=['Todos', '< 1', '1-3', '3-5', '5-10', '> 10'],
            value='Todos',
            help="Filtra por duración de vida (solo liquidados)"
        )
    
    # Apply all filters
    filtered_lifecycle = fund_lifecycle.copy()
    
    # Text search filter
    if search_term:
        mask = (
            filtered_lifecycle['Nombre'].str.contains(search_term.upper(), case=False, na=False) |
            filtered_lifecycle['N_Registro'].astype(str).str.contains(search_term, na=False)
        )
        filtered_lifecycle = filtered_lifecycle[mask]
    
    # Status filter
    if status_search == 'Activos':
        filtered_lifecycle = filtered_lifecycle[filtered_lifecycle['Fecha_Baja'].isna()]
    elif status_search == 'Liquidados':
        filtered_lifecycle = filtered_lifecycle[filtered_lifecycle['Fecha_Baja'].notna()]
    
    # Year range filter
    mask = (
        (filtered_lifecycle['Año_Alta'] >= year_range[0]) & 
        (filtered_lifecycle['Año_Alta'] <= year_range[1])
    ) | (
        (filtered_lifecycle['Año_Baja'] >= year_range[0]) & 
        (filtered_lifecycle['Año_Baja'] <= year_range[1])
    )
    filtered_lifecycle = filtered_lifecycle[mask]
    
    # Gestora filter
    if selected_gestora != 'Todas':
        filtered_lifecycle = filtered_lifecycle[filtered_lifecycle['Gestora'] == selected_gestora]
    
    # Depositaria filter
    if selected_depositaria != 'Todas':
        filtered_lifecycle = filtered_lifecycle[filtered_lifecycle['Depositaria'] == selected_depositaria]
    
    # Life duration filter
    if vida_filter != 'Todos' and 'Vida_Anos' in filtered_lifecycle.columns:
        if vida_filter == '< 1':
            filtered_lifecycle = filtered_lifecycle[
                (filtered_lifecycle['Vida_Anos'] < 1) & filtered_lifecycle['Vida_Anos'].notna()
            ]
        elif vida_filter == '1-3':
            filtered_lifecycle = filtered_lifecycle[
                (filtered_lifecycle['Vida_Anos'] >= 1) & (filtered_lifecycle['Vida_Anos'] < 3)
            ]
        elif vida_filter == '3-5':
            filtered_lifecycle = filtered_lifecycle[
                (filtered_lifecycle['Vida_Anos'] >= 3) & (filtered_lifecycle['Vida_Anos'] < 5)
            ]
        elif vida_filter == '5-10':
            filtered_lifecycle = filtered_lifecycle[
                (filtered_lifecycle['Vida_Anos'] >= 5) & (filtered_lifecycle['Vida_Anos'] < 10)
            ]
        elif vida_filter == '> 10':
            filtered_lifecycle = filtered_lifecycle[
                filtered_lifecycle['Vida_Anos'] >= 10
            ]
    
    # Statistics summary
    total_in_search = len(filtered_lifecycle)
    active_in_search = len(filtered_lifecycle[filtered_lifecycle['Fecha_Baja'].isna()])
    liquidated_in_search = len(filtered_lifecycle[filtered_lifecycle['Fecha_Baja'].notna()])
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Fondos", f"{total_in_search:,}")
    
    with col2:
        st.metric("Activos", f"{active_in_search:,}", 
                  delta=f"{(active_in_search/total_in_search*100):.1f}%" if total_in_search > 0 else "0%")
    
    with col3:
        st.metric("Liquidados", f"{liquidated_in_search:,}",
                  delta=f"{(liquidated_in_search/total_in_search*100):.1f}%" if total_in_search > 0 else "0%")
    
    with col4:
        avg_vida = filtered_lifecycle[filtered_lifecycle['Vida_Anos'].notna()]['Vida_Anos'].mean()
        st.metric("Vida Media", f"{avg_vida:.1f} años" if not pd.isna(avg_vida) else "N/A")
    
    # Display results in table
    if total_in_search > 0:
        st.markdown(f"#### 📋 Resultados ({total_in_search:,} fondos encontrados)")
        
        display_lifecycle = filtered_lifecycle.copy()
        display_lifecycle['N_Registro'] = display_lifecycle['N_Registro'].astype(int)
        display_lifecycle = display_lifecycle.sort_values('Fecha_Alta', ascending=False)
        
        display_lifecycle['Fecha_Alta'] = display_lifecycle['Fecha_Alta'].dt.strftime('%Y-%m-%d')
        display_lifecycle['Fecha_Baja'] = display_lifecycle['Fecha_Baja'].dt.strftime('%Y-%m-%d')
        
        # Ensure no negative values are displayed
        display_lifecycle['Vida_Anos'] = display_lifecycle['Vida_Anos'].apply(
            lambda x: x if pd.isna(x) or x >= 0 else None
        )
        
        display_cols = ['N_Registro', 'Nombre', 'Fecha_Alta', 'Fecha_Baja', 'Vida_Anos', 'Estado_Actual', 'Gestora', 'Depositaria']
        
        st.dataframe(
            display_lifecycle[display_cols],
            use_container_width=True,
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
        
        # STATISTICS SECTION
        st.markdown("---")
        st.markdown("### 📊 Estadísticas Detalladas")
        
        # Create tabs for different statistics
        stat_tabs = st.tabs(["🏢 Por Gestora", "🏦 Por Depositaria", "📅 Por Años", "⚰️ Análisis de Mortalidad"])
        
        # Tab 1: Statistics by Gestora
        with stat_tabs[0]:
            col1, col2 = st.columns(2)
            
            with col1:
                # Top Gestoras by number of funds
                top_gestoras = filtered_lifecycle.groupby('Gestora').agg({
                    'N_Registro': 'count',
                    'Estado_Actual': lambda x: (x == '✅ Activo').sum(),
                    'Vida_Anos': 'mean'
                }).round(1)
                top_gestoras.columns = ['Total_Fondos', 'Activos', 'Vida_Media']
                top_gestoras['Liquidados'] = top_gestoras['Total_Fondos'] - top_gestoras['Activos']
                top_gestoras['Tasa_Mortalidad'] = (top_gestoras['Liquidados'] / top_gestoras['Total_Fondos'] * 100).round(1)
                top_gestoras = top_gestoras.sort_values('Total_Fondos', ascending=False).head(10)
                
                st.markdown("**🏆 Top 10 Gestoras por Número de Fondos**")
                st.dataframe(
                    top_gestoras,
                    use_container_width=True,
                    column_config={
                        "Total_Fondos": st.column_config.NumberColumn("Total", format="%d"),
                        "Activos": st.column_config.NumberColumn("Activos", format="%d"),
                        "Liquidados": st.column_config.NumberColumn("Liquidados", format="%d"),
                        "Vida_Media": st.column_config.NumberColumn("Vida Media (años)", format="%.1f"),
                        "Tasa_Mortalidad": st.column_config.NumberColumn("Mortalidad %", format="%.1f%%")
                    }
                )
            
            with col2:
                # Gestoras with highest mortality
                mortality_gestoras = filtered_lifecycle[filtered_lifecycle['Gestora'].notna()].groupby('Gestora').agg({
                    'N_Registro': 'count',
                    'Estado_Actual': lambda x: (x == '💀 Liquidado').sum()
                })
                mortality_gestoras.columns = ['Total', 'Liquidados']
                mortality_gestoras = mortality_gestoras[mortality_gestoras['Total'] >= 5]
                mortality_gestoras['Tasa_Mortalidad'] = (mortality_gestoras['Liquidados'] / mortality_gestoras['Total'] * 100).round(1)
                mortality_gestoras = mortality_gestoras.sort_values('Tasa_Mortalidad', ascending=False).head(10)
                
                st.markdown("**💀 Gestoras con Mayor Tasa de Mortalidad** *(mín. 5 fondos)*")
                st.dataframe(
                    mortality_gestoras,
                    use_container_width=True,
                    column_config={
                        "Total": st.column_config.NumberColumn("Total Fondos", format="%d"),
                        "Liquidados": st.column_config.NumberColumn("Liquidados", format="%d"),
                        "Tasa_Mortalidad": st.column_config.ProgressColumn(
                            "Mortalidad %",
                            format="%.1f%%",
                            min_value=0,
                            max_value=100
                        )
                    }
                )
        
        # Tab 2: Statistics by Depositaria
        with stat_tabs[1]:
            col1, col2 = st.columns(2)
            
            with col1:
                # Top Depositarias
                top_depositarias = filtered_lifecycle.groupby('Depositaria').agg({
                    'N_Registro': 'count',
                    'Estado_Actual': lambda x: (x == '✅ Activo').sum(),
                    'Vida_Anos': 'mean'
                }).round(1)
                top_depositarias.columns = ['Total_Fondos', 'Activos', 'Vida_Media']
                top_depositarias['Liquidados'] = top_depositarias['Total_Fondos'] - top_depositarias['Activos']
                top_depositarias = top_depositarias.sort_values('Total_Fondos', ascending=False).head(10)
                
                st.markdown("**🏆 Top 10 Depositarias por Número de Fondos**")
                st.dataframe(
                    top_depositarias,
                    use_container_width=True,
                    column_config={
                        "Total_Fondos": st.column_config.NumberColumn("Total", format="%d"),
                        "Activos": st.column_config.NumberColumn("Activos", format="%d"),
                        "Liquidados": st.column_config.NumberColumn("Liquidados", format="%d"),
                        "Vida_Media": st.column_config.NumberColumn("Vida Media (años)", format="%.1f")
                    }
                )
            
            with col2:
                # Market concentration
                total_funds = len(filtered_lifecycle)
                top5_depositarias = filtered_lifecycle.groupby('Depositaria')['N_Registro'].count().nlargest(5)
                concentration = (top5_depositarias.sum() / total_funds * 100)
                
                st.markdown("**📊 Concentración del Mercado**")
                st.metric("Top 5 Depositarias", f"{concentration:.1f}%", "del total de fondos")
                
                # Show concentration breakdown
                concentration_data = pd.DataFrame({
                    'Depositaria': top5_depositarias.index,
                    'Fondos': top5_depositarias.values,
                    'Porcentaje': (top5_depositarias.values / total_funds * 100).round(1)
                })
                st.dataframe(concentration_data, use_container_width=True, hide_index=True)
        
        # Tab 3: Statistics by Years
        with stat_tabs[2]:
            col1, col2 = st.columns(2)
            
            with col1:
                # Funds by year of creation
                yearly_creation = filtered_lifecycle.groupby('Año_Alta').agg({
                    'N_Registro': 'count',
                    'Estado_Actual': lambda x: (x == '✅ Activo').sum()
                })
                yearly_creation.columns = ['Creados', 'Aún_Activos']
                yearly_creation['Supervivencia_%'] = (yearly_creation['Aún_Activos'] / yearly_creation['Creados'] * 100).round(1)
                yearly_creation = yearly_creation.sort_index(ascending=False).head(10)
                
                st.markdown("**📅 Fondos por Año de Creación** *(últimos 10 años)*")
                st.dataframe(
                    yearly_creation,
                    use_container_width=True,
                    column_config={
                        "Creados": st.column_config.NumberColumn("Creados", format="%d"),
                        "Aún_Activos": st.column_config.NumberColumn("Aún Activos", format="%d"),
                        "Supervivencia_%": st.column_config.ProgressColumn(
                            "Supervivencia %",
                            format="%.1f%%",
                            min_value=0,
                            max_value=100
                        )
                    }
                )
            
            with col2:
                # Funds by year of closure
                yearly_closure = filtered_lifecycle[filtered_lifecycle['Año_Baja'].notna()].groupby('Año_Baja')['N_Registro'].count()
                yearly_closure = yearly_closure.sort_index(ascending=False).head(10)
                
                st.markdown("**⚰️ Liquidaciones por Año** *(últimos 10 años)*")
                yearly_closure_df = pd.DataFrame({
                    'Año': yearly_closure.index.astype(int),
                    'Liquidaciones': yearly_closure.values
                })
                
                # Add crisis indicator
                crisis_years = [2008, 2009, 2010, 2011, 2012, 2020]
                yearly_closure_df['Crisis'] = yearly_closure_df['Año'].apply(
                    lambda x: '🔴 Sí' if x in crisis_years else '🟢 No'
                )
                
                st.dataframe(
                    yearly_closure_df,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Año": st.column_config.NumberColumn("Año", format="%d"),
                        "Liquidaciones": st.column_config.NumberColumn("Liquidaciones", format="%d"),
                        "Crisis": st.column_config.TextColumn("Período Crisis")
                    }
                )
        
        # Tab 4: Mortality Analysis
        with stat_tabs[3]:
            col1, col2, col3 = st.columns(3)
            
            # Life duration distribution - only use valid positive values
            liquidated_funds = filtered_lifecycle[
                (filtered_lifecycle['Vida_Anos'].notna()) & 
                (filtered_lifecycle['Vida_Anos'] >= 0)
            ]
            
            with col1:
                st.markdown("**⏱️ Distribución de Vida de Fondos Liquidados**")
                if len(liquidated_funds) > 0:
                    life_bins = pd.cut(liquidated_funds['Vida_Anos'], 
                                     bins=[0, 1, 3, 5, 10, 100],
                                     labels=['< 1 año', '1-3 años', '3-5 años', '5-10 años', '> 10 años'])
                    life_dist = life_bins.value_counts().sort_index()
                    
                    life_dist_df = pd.DataFrame({
                        'Duración': life_dist.index,
                        'Fondos': life_dist.values,
                        'Porcentaje': (life_dist.values / life_dist.sum() * 100).round(1)
                    })
                    st.dataframe(life_dist_df, use_container_width=True, hide_index=True)
                else:
                    st.info("No hay datos de fondos liquidados con vida válida")
            
            with col2:
                st.markdown("**📈 Estadísticas de Supervivencia**")
                
                if len(liquidated_funds) > 0:
                    # Calculate survival stats
                    median_life = liquidated_funds['Vida_Anos'].median()
                    q1_life = liquidated_funds['Vida_Anos'].quantile(0.25)
                    q3_life = liquidated_funds['Vida_Anos'].quantile(0.75)
                    
                    st.metric("Mediana de Vida", f"{median_life:.1f} años")
                    st.metric("25% mueren antes de", f"{q1_life:.1f} años")
                    st.metric("75% mueren antes de", f"{q3_life:.1f} años")
                else:
                    st.info("No hay datos suficientes")
            
            with col3:
                st.markdown("**💡 Insights Clave**")
                
                if len(liquidated_funds) > 0:
                    # Calculate key insights
                    infant_mortality = len(liquidated_funds[liquidated_funds['Vida_Anos'] < 1]) / len(liquidated_funds) * 100
                    long_survivors = len(filtered_lifecycle[
                        (filtered_lifecycle['Vida_Anos'] > 10) | 
                        ((filtered_lifecycle['Fecha_Baja'].isna()) & 
                         ((pd.Timestamp.now() - filtered_lifecycle['Fecha_Alta']).dt.days / 365.25 > 10))
                    ]) / len(filtered_lifecycle) * 100
                    
                    st.info(f"""
                    **Mortalidad Infantil:** {infant_mortality:.1f}% de los fondos liquidados mueren en su primer año
                    
                    **Supervivientes a Largo Plazo:** Solo {long_survivors:.1f}% de los fondos superan los 10 años
                    
                    **Tasa de Mortalidad Global:** {(liquidated_in_search/total_in_search*100):.1f}% en la selección actual
                    """)
                else:
                    st.info("No hay datos suficientes para calcular insights")
    
    else:
        st.info("No se encontraron fondos con los criterios especificados. Prueba a ajustar los filtros.")

# Tab 2: Enhanced Temporal Analysis
with tab_list[1]:
    st.markdown("### 📈 Evolución Temporal del Sesgo de Supervivencia")
    
    # Time granularity selector
    col1, col2, col3, col4 = st.columns([1, 1, 1, 2])
    
    with col1:
        time_granularity = st.selectbox(
            "📅 Granularidad Temporal",
            options=['Semanal', 'Mensual', 'Trimestral', 'Anual'],
            index=3,
            help="Selecciona el período de agregación para el análisis"
        )
    
    with col2:
        chart_type = st.selectbox(
            "📊 Tipo de Gráfico",
            options=['Barras Apiladas', 'Líneas', 'Área', 'Cascada'],
            index=0,
            help="Selecciona el tipo de visualización"
        )
    
    with col3:
        show_moving_avg = st.checkbox(
            "📉 Media Móvil",
            value=True,
            help="Mostrar media móvil del balance neto"
        )
    
    with col4:
        if time_granularity != 'Anual':
            # Year selector for non-annual views
            available_years = sorted(df['year'].unique())
            selected_years = st.select_slider(
                "Rango de Años",
                options=available_years,
                value=(max(available_years)-5, max(available_years)),
                help="Selecciona el rango de años a visualizar"
            )
        else:
            selected_years = None
    
    # Prepare data based on granularity
    if time_granularity == 'Semanal':
        # Weekly aggregation
        df_temp = df.copy()
        df_temp['week'] = df_temp['date'].dt.to_period('W')
        
        if selected_years:
            df_temp = df_temp[(df_temp['year'] >= selected_years[0]) & (df_temp['year'] <= selected_years[1])]
        
        temporal_stats = df_temp.groupby(['week', 'status']).size().unstack(fill_value=0)
        temporal_stats.index = temporal_stats.index.to_timestamp()
        time_label = "Semana"
        ma_window = 4
        
    elif time_granularity == 'Mensual':
        # Monthly aggregation
        df_temp = df.copy()
        
        if selected_years:
            df_temp = df_temp[(df_temp['year'] >= selected_years[0]) & (df_temp['year'] <= selected_years[1])]
        
        temporal_stats = df_temp.groupby(['year_month', 'status']).size().unstack(fill_value=0)
        temporal_stats.index = temporal_stats.index.to_timestamp()
        time_label = "Mes"
        ma_window = 3
        
    elif time_granularity == 'Trimestral':
        # Quarterly aggregation
        df_temp = df.copy()
        df_temp['quarter'] = df_temp['date'].dt.to_period('Q')
        
        if selected_years:
            df_temp = df_temp[(df_temp['year'] >= selected_years[0]) & (df_temp['year'] <= selected_years[1])]
        
        temporal_stats = df_temp.groupby(['quarter', 'status']).size().unstack(fill_value=0)
        temporal_stats.index = temporal_stats.index.to_timestamp()
        time_label = "Trimestre"
        ma_window = 4
        
    else:  # Annual
        # Yearly aggregation
        temporal_stats = df.groupby(['year', 'status']).size().unstack(fill_value=0)
        temporal_stats.index = pd.to_datetime(temporal_stats.index.astype(str) + '-01-01')
        time_label = "Año"
        ma_window = 2
    
    # Rename columns for consistency
    if 'NUEVAS_INSCRIPCIONES' in temporal_stats.columns:
        temporal_stats = temporal_stats.rename(columns={
            'NUEVAS_INSCRIPCIONES': 'Altas',
            'BAJAS': 'Bajas'
        })
    
    # Calculate additional metrics
    temporal_stats['Balance_Neto'] = temporal_stats.get('Altas', 0) - temporal_stats.get('Bajas', 0)
    temporal_stats['Mortalidad_%'] = (temporal_stats.get('Bajas', 0) / temporal_stats.get('Altas', 1) * 100).fillna(0)
    temporal_stats['Acumulado'] = temporal_stats['Balance_Neto'].cumsum()
    
    # Calculate moving average if requested
    if show_moving_avg:
        temporal_stats['MA_Balance'] = temporal_stats['Balance_Neto'].rolling(window=ma_window, center=True).mean()
    
    # Create the main visualization
    fig = go.Figure()
    
    if chart_type == 'Barras Apiladas':
        # Stacked bar chart with gradient colors
        fig.add_trace(go.Bar(
            x=temporal_stats.index,
            y=temporal_stats.get('Altas', 0),
            name='🟢 Altas',
            marker=dict(
                color='rgba(34, 197, 94, 0.9)',
                line=dict(color='rgba(34, 197, 94, 1)', width=1)
            ),
            text=temporal_stats.get('Altas', 0),
            textposition='outside',
            textfont=dict(color='#22c55e', size=10),
            hovertemplate='<b>%{x|%Y-%m-%d}</b><br>Altas: %{y}<extra></extra>'
        ))
        
        fig.add_trace(go.Bar(
            x=temporal_stats.index,
            y=-temporal_stats.get('Bajas', 0),
            name='🔴 Bajas',
            marker=dict(
                color='rgba(239, 68, 68, 0.9)',
                line=dict(color='rgba(239, 68, 68, 1)', width=1)
            ),
            text=temporal_stats.get('Bajas', 0),
            textposition='outside',
            textfont=dict(color='#ef4444', size=10),
            hovertemplate='<b>%{x|%Y-%m-%d}</b><br>Bajas: %{y}<extra></extra>'
        ))
        
        # Add balance line
        fig.add_trace(go.Scatter(
            x=temporal_stats.index,
            y=temporal_stats['Balance_Neto'],
            name='⚡ Balance Neto',
            line=dict(color='#fbbf24', width=3, shape='spline'),
            mode='lines+markers',
            marker=dict(
                size=8,
                color='#fbbf24',
                line=dict(width=2, color='#1a1a1a'),
                symbol='diamond'
            ),
            hovertemplate='<b>%{x|%Y-%m-%d}</b><br>Balance: %{y:+}<extra></extra>'
        ))
        
    elif chart_type == 'Líneas':
        # Enhanced line chart
        fig.add_trace(go.Scatter(
            x=temporal_stats.index,
            y=temporal_stats.get('Altas', 0),
            name='🟢 Altas',
            line=dict(color='#22c55e', width=3, shape='spline'),
            mode='lines+markers',
            marker=dict(size=6, color='#22c55e'),
            fill='tozeroy',
            fillcolor='rgba(34, 197, 94, 0.1)',
            hovertemplate='<b>%{x|%Y-%m-%d}</b><br>Altas: %{y}<extra></extra>'
        ))
        
        fig.add_trace(go.Scatter(
            x=temporal_stats.index,
            y=temporal_stats.get('Bajas', 0),
            name='🔴 Bajas',
            line=dict(color='#ef4444', width=3, shape='spline'),
            mode='lines+markers',
            marker=dict(size=6, color='#ef4444'),
            fill='tozeroy',
            fillcolor='rgba(239, 68, 68, 0.1)',
            hovertemplate='<b>%{x|%Y-%m-%d}</b><br>Bajas: %{y}<extra></extra>'
        ))
        
        fig.add_trace(go.Scatter(
            x=temporal_stats.index,
            y=temporal_stats['Balance_Neto'],
            name='⚡ Balance',
            line=dict(color='#fbbf24', width=2, dash='dot'),
            mode='lines',
            hovertemplate='<b>%{x|%Y-%m-%d}</b><br>Balance: %{y:+}<extra></extra>'
        ))
        
    elif chart_type == 'Área':
        # Area chart with gradient
        fig.add_trace(go.Scatter(
            x=temporal_stats.index,
            y=temporal_stats.get('Altas', 0),
            name='🟢 Altas',
            stackgroup='one',
            fillcolor='rgba(34, 197, 94, 0.4)',
            line=dict(color='#22c55e', width=2),
            hovertemplate='<b>%{x|%Y-%m-%d}</b><br>Altas: %{y}<extra></extra>'
        ))
        
        fig.add_trace(go.Scatter(
            x=temporal_stats.index,
            y=-temporal_stats.get('Bajas', 0),
            name='🔴 Bajas',
            stackgroup='one',
            fillcolor='rgba(239, 68, 68, 0.4)',
            line=dict(color='#ef4444', width=2),
            hovertemplate='<b>%{x|%Y-%m-%d}</b><br>Bajas: %{y}<extra></extra>'
        ))
        
    else:  # Cascada (Waterfall)
        # Waterfall chart for cumulative effect
        fig.add_trace(go.Waterfall(
            x=temporal_stats.index,
            y=temporal_stats['Balance_Neto'],
            text=[f"{v:+}" for v in temporal_stats['Balance_Neto']],
            textposition="outside",
            connector={"line": {"color": "rgba(99, 102, 241, 0.3)", "width": 1}},
            increasing={"marker": {"color": "rgba(34, 197, 94, 0.8)"}},
            decreasing={"marker": {"color": "rgba(239, 68, 68, 0.8)"}},
            totals={"marker": {"color": "rgba(99, 102, 241, 0.8)"}},
            name="Balance Acumulado"
        ))
    
    # Add moving average if selected
    if show_moving_avg and 'MA_Balance' in temporal_stats.columns:
        fig.add_trace(go.Scatter(
            x=temporal_stats.index,
            y=temporal_stats['MA_Balance'],
            name=f'📊 Media Móvil ({ma_window} {time_label.lower()}s)',
            line=dict(color='#a78bfa', width=2, dash='dash'),
            mode='lines',
            opacity=0.7,
            hovertemplate='<b>%{x|%Y-%m-%d}</b><br>MA: %{y:.1f}<extra></extra>'
        ))
    
    # Add crisis period annotations
    crisis_periods = [
        {"name": "Crisis Financiera", "start": "2008-09-01", "end": "2009-06-01"},
        {"name": "Crisis Deuda EU", "start": "2011-08-01", "end": "2012-07-01"},
        {"name": "COVID-19", "start": "2020-02-01", "end": "2020-05-01"}
    ]
    
    for period in crisis_periods:
        # Only add if within the selected time range
        if temporal_stats.index[0] <= pd.to_datetime(period["end"]) and temporal_stats.index[-1] >= pd.to_datetime(period["start"]):
            fig.add_vrect(
                x0=period["start"],
                x1=period["end"],
                fillcolor="rgba(239, 68, 68, 0.08)",
                layer="below",
                line_width=0
            )
            
            # Add annotation separately
            fig.add_annotation(
                x=pd.to_datetime(period["start"]) + (pd.to_datetime(period["end"]) - pd.to_datetime(period["start"]))/2,
                y=1,
                yref="paper",
                text=period["name"],
                showarrow=False,
                font=dict(color="rgba(239, 68, 68, 0.5)", size=10),
                yanchor="bottom"
            )
    
    # Update layout with dark aesthetic
    fig.update_layout(
        title=dict(
            text=f"<b>Evolución {time_label} | Sesgo de Supervivencia</b><br><sup>Altas vs Bajas de Fondos</sup>",
            font=dict(size=20, color='#f1f5f9'),
            x=0.5,
            xanchor='center'
        ),
        xaxis=dict(
            title="",
            gridcolor='rgba(255, 255, 255, 0.05)',
            showgrid=True,
            zeroline=True,
            zerolinecolor='rgba(255, 255, 255, 0.1)',
            tickfont=dict(color='#94a3b8'),
            rangeslider=dict(
                visible=False
            ),
            type='date'
        ),
        yaxis=dict(
            title=f"Número de Fondos",
            gridcolor='rgba(255, 255, 255, 0.05)',
            showgrid=True,
            zeroline=True,
            zerolinecolor='rgba(255, 255, 255, 0.2)',
            tickfont=dict(color='#94a3b8')
        ),
        plot_bgcolor='#0f0f0f',
        paper_bgcolor='#0f0f0f',
        font=dict(family='Inter', color='#e2e8f0'),
        hovermode='x unified',
        hoverlabel=dict(
            bgcolor='rgba(26, 26, 26, 0.95)',
            font_size=12,
            font_family='Inter',
            bordercolor='#333'
        ),
        height=600,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="top",
            y=1.15,
            xanchor="center",
            x=0.5,
            bgcolor='rgba(26, 26, 26, 0.8)',
            bordercolor='rgba(99, 102, 241, 0.2)',
            borderwidth=1,
            font=dict(color='#e2e8f0', size=11)
        ),
        margin=dict(t=120, b=60, l=60, r=40),
        barmode='relative' if chart_type == 'Barras Apiladas' else None
    )
    
    # Add horizontal line at y=0
    fig.add_hline(
        y=0,
        line_color='rgba(255, 255, 255, 0.2)',
        line_width=1,
        line_dash="dash"
    )
    
    # Display the chart
    st.plotly_chart(fig, use_container_width=True)
    
    # Key Statistics Below Chart
    st.markdown("---")
    
    # Calculate period statistics
    col1, col2, col3, col4, col5 = st.columns(5)
    
    total_altas = temporal_stats.get('Altas', 0).sum()
    total_bajas = temporal_stats.get('Bajas', 0).sum()
    balance_total = total_altas - total_bajas
    avg_mortality = temporal_stats['Mortalidad_%'].mean()
    
    # Find worst period
    worst_period_idx = temporal_stats['Balance_Neto'].idxmin()
    worst_period_value = temporal_stats.loc[worst_period_idx, 'Balance_Neto']
    
    # Find best period
    best_period_idx = temporal_stats['Balance_Neto'].idxmax()
    best_period_value = temporal_stats.loc[best_period_idx, 'Balance_Neto']
    
    with col1:
        st.metric(
            f"Total Altas ({time_label}s: {len(temporal_stats)})",
            f"{total_altas:,}",
            f"Media: {(total_altas/len(temporal_stats)):.1f}"
        )
    
    with col2:
        st.metric(
            "Total Bajas",
            f"{total_bajas:,}",
            f"Media: {(total_bajas/len(temporal_stats)):.1f}"
        )
    
    with col3:
        st.metric(
            "Balance Total",
            f"{balance_total:+,}",
            f"{'Positivo' if balance_total > 0 else 'Negativo'}",
            delta_color="normal" if balance_total > 0 else "inverse"
        )
    
    with col4:
        st.metric(
            f"Peor {time_label}",
            f"{worst_period_value:+.0f}",
            f"{worst_period_idx.strftime('%Y-%m-%d')}",
            delta_color="inverse"
        )
    
    with col5:
        st.metric(
            f"Mejor {time_label}",
            f"{best_period_value:+.0f}",
            f"{best_period_idx.strftime('%Y-%m-%d')}"
        )

# Tab 3: Data Quality Report
with tab_list[2]:
    st.markdown("### 🔬 Reporte de Calidad de Datos")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📊 Resumen de Limpieza de Datos")
        
        quality_metrics = {
            "Registros Originales": quality_report['initial_count'],
            "Registros con Vida Negativa": quality_report['invalid_dates'],
            "Registros con Vida > 50 años": quality_report['too_long_life'],
            "Registros con Vida = 0 días": quality_report['zero_life'],
            "Registros Válidos Finales": quality_report['final_count'],
            "Tasa de Datos Válidos": f"{(quality_report['final_count']/quality_report['initial_count']*100):.1f}%"
        }
        
        for metric, value in quality_metrics.items():
            if isinstance(value, str):
                st.metric(metric, value)
            else:
                st.metric(metric, f"{value:,}")
    
    with col2:
        st.markdown("#### 🚨 Registros Problemáticos Eliminados")
        
        if len(quality_report['removed_records']) > 0:
            st.warning(f"Se eliminaron {len(quality_report['removed_records'])} registros con datos incorrectos")
            
            # Show sample of removed records
            if st.checkbox("Mostrar muestra de registros eliminados"):
                sample = quality_report['removed_records'].head(10)
                sample_display = sample[['N_Registro', 'Nombre', 'Fecha_Alta', 'Fecha_Baja', 'Vida_Anos']].copy()
                sample_display['Problema'] = sample_display['Vida_Anos'].apply(
                    lambda x: 'Vida negativa' if x < 0 else 'Vida excesiva (>50 años)' if x > 50 else 'Otro'
                )
                st.dataframe(sample_display, use_container_width=True, hide_index=True)
        else:
            st.success("No se detectaron registros problemáticos")
    
    # Data quality visualization
    st.markdown("---")
    st.markdown("#### 📈 Visualización de Calidad de Datos")
    
    # Create pie chart for data quality
    fig_quality = go.Figure(data=[go.Pie(
        labels=['Datos Válidos', 'Vida Negativa', 'Vida Excesiva', 'Otros'],
        values=[
            quality_report['final_count'],
            quality_report['invalid_dates'],
            quality_report['too_long_life'],
            quality_report['zero_life']
        ],
        hole=.3,
        marker=dict(colors=['#22c55e', '#ef4444', '#fbbf24', '#94a3b8'])
    )])
    
    fig_quality.update_layout(
        title="Distribución de Calidad de Datos",
        height=400,
        plot_bgcolor='#0f0f0f',
        paper_bgcolor='#0f0f0f',
        font=dict(family='Inter', color='#e2e8f0')
    )
    
    st.plotly_chart(fig_quality, use_container_width=True)
    
    # Data quality insights
    st.markdown("""
    <div class="info-box">
        <h4>💡 Recomendaciones de Calidad de Datos</h4>
        <ul style="margin-left: 1rem;">
            <li>Los registros con vida negativa indican errores en el registro de fechas</li>
            <li>Vidas superiores a 50 años son probablemente errores de digitación</li>
            <li>Es importante validar los datos fuente con la CNMV para estos casos</li>
            <li>La limpieza aplicada mejora la precisión del análisis de supervivencia</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown(f"""
<div style="text-align: center; color: #64748b; padding: 2rem 0; font-size: 0.875rem;">
    <p>Este análisis demuestra el severo sesgo de supervivencia en la industria de fondos española.</p>
    <p>Con una tasa de mortalidad del {mortality_rate:.0f}%, las estadísticas publicadas no reflejan la realidad completa.</p>
    <p>Datos limpios y validados para mayor precisión analítica.</p>
    <p style="margin-top: 1rem;">
        <a href="https://twitter.com/Gsnchez" target="_blank" style="color: #a5b4fc;">@Gsnchez</a> • 
        <a href="https://bquantfinance.com" target="_blank" style="color: #a5b4fc;">bquantfinance.com</a>
    </p>
</div>
""", unsafe_allow_html=True)
