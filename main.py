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
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Dark mode aesthetic CSS
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
    
    /* Economic cycle badges */
    .cycle-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin: 0.25rem;
    }
    
    .cycle-expansion {
        background: rgba(34, 197, 94, 0.2);
        color: #86efac;
        border: 1px solid rgba(34, 197, 94, 0.3);
    }
    
    .cycle-crisis {
        background: rgba(239, 68, 68, 0.2);
        color: #fca5a5;
        border: 1px solid rgba(239, 68, 68, 0.3);
    }
    
    .cycle-recovery {
        background: rgba(99, 102, 241, 0.2);
        color: #a5b4fc;
        border: 1px solid rgba(99, 102, 241, 0.3);
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
        
        # Get Spanish unemployment and VIX
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
        sp500 = sp500[['Close']]
        sp500.columns = ['SP500']
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

# Title
st.markdown("# 📊 Análisis de Fondos Españoles - Sesgo de Supervivencia")
st.markdown("""
<div class="author-box">
    <strong>Análisis del Sesgo de Supervivencia en Fondos de Inversión</strong><br>
    Por <a href="https://twitter.com/Gsnchez" target="_blank">@Gsnchez</a> • 
    <a href="https://bquantfinance.com" target="_blank">bquantfinance.com</a> • 
    Datos CNMV 2004-2025
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
tabs = ["🔍 **Búsqueda de Fondos**", "📈 **Ciclo Económico**", "📊 **Análisis Temporal**"]
tab_list = st.tabs(tabs)

# Tab 1: Fund Search (PRIMARY)
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
    else:
        st.info("No se encontraron fondos con los criterios especificados")

# Tab 2: Economic Cycle Analysis
with tab_list[1]:
    st.markdown("### Mortalidad de Fondos y Ciclo Económico")
    
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
    
    # Create sophisticated macro analysis
    if not sp500_data.empty and not macro_data.empty:
        fig = make_subplots(
            rows=4, cols=1,
            row_heights=[0.3, 0.25, 0.25, 0.2],
            vertical_spacing=0.05,
            subplot_titles=(
                'S&P 500 y Mortalidad de Fondos',
                'VIX - Índice de Volatilidad',
                'Desempleo España (%)',
                'Balance Neto de Fondos'
            ),
            specs=[
                [{"secondary_y": True}],
                [{"secondary_y": False}],
                [{"secondary_y": False}],
                [{"secondary_y": False}]
            ]
        )
        
        # Panel 1: S&P 500 and Fund Mortality
        fig.add_trace(
            go.Scatter(
                x=sp500_data.index,
                y=sp500_data['SP500'],
                name='S&P 500',
                fill='tozeroy',
                fillcolor='rgba(99, 102, 241, 0.1)',
                line=dict(color='#6366f1', width=1.5),
                hovertemplate='S&P 500: $%{y:,.0f}<extra></extra>'
            ),
            row=1, col=1,
            secondary_y=False
        )
        
        fig.add_trace(
            go.Scatter(
                x=monthly_stats['date'],
                y=monthly_stats['Mortalidad'],
                name='Mortalidad (%)',
                line=dict(color='#ef4444', width=2),
                hovertemplate='Mortalidad: %{y:.1f}%<extra></extra>'
            ),
            row=1, col=1,
            secondary_y=True
        )
        
        # Panel 2: VIX
        if 'VIX' in macro_data.columns:
            fig.add_trace(
                go.Scatter(
                    x=macro_data.index,
                    y=macro_data['VIX'],
                    name='VIX',
                    fill='tozeroy',
                    fillcolor='rgba(251, 191, 36, 0.1)',
                    line=dict(color='#fbbf24', width=1.5),
                    hovertemplate='VIX: %{y:.1f}<extra></extra>'
                ),
                row=2, col=1
            )
        
        # Panel 3: Spanish Unemployment
        if 'Spain_Unemployment' in macro_data.columns:
            fig.add_trace(
                go.Scatter(
                    x=macro_data.index,
                    y=macro_data['Spain_Unemployment'],
                    name='Desempleo',
                    fill='tozeroy',
                    fillcolor='rgba(239, 68, 68, 0.1)',
                    line=dict(color='#dc2626', width=1.5),
                    hovertemplate='Desempleo: %{y:.1f}%<extra></extra>'
                ),
                row=3, col=1
            )
        
        # Panel 4: Net Fund Balance
        colors = ['#22c55e' if x >= 0 else '#ef4444' for x in monthly_stats['Balance']]
        fig.add_trace(
            go.Bar(
                x=monthly_stats['date'],
                y=monthly_stats['Balance'],
                name='Balance',
                marker_color=colors,
                hovertemplate='Balance: %{y:+}<extra></extra>'
            ),
            row=4, col=1
        )
        
        # Add crisis periods
        crisis_periods = [
            {"name": "Crisis Financiera", "start": "2008-09-01", "end": "2009-06-01"},
            {"name": "Crisis Deuda EU", "start": "2011-08-01", "end": "2012-07-01"},
            {"name": "COVID-19", "start": "2020-02-01", "end": "2020-05-01"}
        ]
        
        for period in crisis_periods:
            for row in range(1, 5):
                fig.add_vrect(
                    x0=period["start"],
                    x1=period["end"],
                    fillcolor="rgba(239, 68, 68, 0.05)",
                    layer="below",
                    line_width=0,
                    row=row, col=1
                )
        
        # Update layout
        fig.update_layout(
            height=800,
            plot_bgcolor='#1a1a1a',
            paper_bgcolor='#0f0f0f',
            font=dict(family='Inter', color='#e2e8f0', size=11),
            hovermode='x unified',
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="top",
                y=1.02,
                xanchor="center",
                x=0.5,
                bgcolor='rgba(26, 26, 26, 0.8)',
                bordercolor='#333',
                borderwidth=1
            )
        )
        
        fig.update_xaxes(gridcolor='#333', showgrid=False, zeroline=False)
        fig.update_yaxes(gridcolor='#333', showgrid=True, zeroline=False)
        
        # Update specific y-axes
        fig.update_yaxes(title_text="S&P 500", row=1, col=1, secondary_y=False)
        fig.update_yaxes(title_text="Mortalidad (%)", row=1, col=1, secondary_y=True)
        fig.update_yaxes(title_text="VIX", row=2, col=1)
        fig.update_yaxes(title_text="Desempleo (%)", row=3, col=1)
        fig.update_yaxes(title_text="Balance", row=4, col=1)
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Economic cycle indicators
        st.markdown("### Indicadores del Ciclo Económico")
        
        col1, col2, col3 = st.columns(3)
        
        # Calculate correlations
        if 'VIX' in macro_data.columns:
            # Merge data for correlation
            monthly_vix = macro_data.resample('M')['VIX'].mean()
            correlation_data = monthly_stats.set_index('date').join(monthly_vix, how='inner')
            
            if len(correlation_data) > 10:
                vix_mortality_corr = correlation_data['Mortalidad'].corr(correlation_data['VIX'])
                
                with col1:
                    st.markdown(f"""
                    <div class="info-box">
                        <h4>📊 Correlación VIX-Mortalidad</h4>
                        <p style="font-size: 2rem; text-align: center; color: #6366f1;">
                            {vix_mortality_corr:.3f}
                        </p>
                        <p style="text-align: center; opacity: 0.8;">
                            Mayor volatilidad = Mayor mortalidad
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
        
        with col2:
            crisis_years = [2008, 2009, 2010, 2011, 2012, 2020]
            crisis_deaths = deaths[deaths['year'].isin(crisis_years)]
            crisis_mortality = (len(crisis_deaths) / len(deaths) * 100)
            
            st.markdown(f"""
            <div class="info-box">
                <h4>💀 Muertes en Crisis</h4>
                <p style="font-size: 2rem; text-align: center; color: #ef4444;">
                    {crisis_mortality:.1f}%
                </p>
                <p style="text-align: center; opacity: 0.8;">
                    Del total de liquidaciones
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            avg_life_crisis = fund_lifecycle[fund_lifecycle['Fecha_Alta'].notna() & fund_lifecycle['Fecha_Baja'].notna()]
            avg_life_crisis['Alta_Year'] = pd.to_datetime(avg_life_crisis['Fecha_Alta']).dt.year
            crisis_funds = avg_life_crisis[avg_life_crisis['Alta_Year'].isin(crisis_years)]
            
            if len(crisis_funds) > 0:
                avg_life = crisis_funds['Vida_Anos'].mean()
            else:
                avg_life = 0
            
            st.markdown(f"""
            <div class="info-box">
                <h4>⏱️ Vida Media en Crisis</h4>
                <p style="font-size: 2rem; text-align: center; color: #fbbf24;">
                    {avg_life:.1f} años
                </p>
                <p style="text-align: center; opacity: 0.8;">
                    Fondos nacidos en crisis
                </p>
            </div>
            """, unsafe_allow_html=True)

# Tab 3: Temporal Analysis
with tab_list[2]:
    st.markdown("### Evolución Temporal del Sesgo")
    
    # Prepare yearly data
    yearly_stats = df.groupby(['year', 'status']).size().unstack(fill_value=0)
    yearly_stats = yearly_stats.rename(columns={
        'NUEVAS_INSCRIPCIONES': 'Altas',
        'BAJAS': 'Bajas'
    })
    yearly_stats['Cambio_Neto'] = yearly_stats['Altas'] - yearly_stats['Bajas']
    yearly_stats = yearly_stats.reset_index()
    
    # Create dark mode chart
    fig = go.Figure()
    
    # Births
    fig.add_trace(go.Bar(
        x=yearly_stats['year'],
        y=yearly_stats['Altas'],
        name='Altas',
        marker_color='#22c55e',
        text=yearly_stats['Altas'],
        textposition='outside',
        textfont=dict(color='#22c55e'),
        hovertemplate='<b>%{x}</b><br>Altas: %{y}<extra></extra>'
    ))
    
    # Deaths
    fig.add_trace(go.Bar(
        x=yearly_stats['year'],
        y=-yearly_stats['Bajas'],
        name='Bajas',
        marker_color='#ef4444',
        text=yearly_stats['Bajas'],
        textposition='outside',
        textfont=dict(color='#ef4444'),
        hovertemplate='<b>%{x}</b><br>Bajas: %{y}<extra></extra>'
    ))
    
    # Net change line
    fig.add_trace(go.Scatter(
        x=yearly_stats['year'],
        y=yearly_stats['Cambio_Neto'],
        name='Balance Neto',
        line=dict(color='#fbbf24', width=3),
        mode='lines+markers',
        marker=dict(size=10, color='#fbbf24', line=dict(width=2, color='#1a1a1a')),
        hovertemplate='<b>%{x}</b><br>Balance: %{y:+}<extra></extra>'
    ))
    
    fig.update_layout(
        xaxis_title="",
        yaxis_title="Número de Fondos",
        hovermode='x unified',
        height=500,
        plot_bgcolor='#1a1a1a',
        paper_bgcolor='#0f0f0f',
        font=dict(family='Inter', color='#e2e8f0'),
        barmode='relative',
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5,
            bgcolor='rgba(26, 26, 26, 0.8)',
            bordercolor='#333',
            borderwidth=1
        )
    )
    
    fig.add_hline(y=0, line_color='#666', line_width=1)
    fig.update_xaxes(gridcolor='#333', showgrid=False, zeroline=False)
    fig.update_yaxes(gridcolor='#333', showgrid=True, zeroline=False)
    
    st.plotly_chart(fig, use_container_width=True)

# Footer
st.markdown("---")
st.markdown(f"""
<div style="text-align: center; color: #64748b; padding: 2rem 0; font-size: 0.875rem;">
    <p>Este análisis demuestra el severo sesgo de supervivencia en la industria de fondos española.</p>
    <p>Con una tasa de mortalidad del {mortality_rate:.0f}%, las estadísticas publicadas no reflejan la realidad completa.</p>
    <p style="margin-top: 1rem;">
        <a href="https://twitter.com/Gsnchez" target="_blank" style="color: #a5b4fc;">@Gsnchez</a> • 
        <a href="https://bquantfinance.com" target="_blank" style="color: #a5b4fc;">bquantfinance.com</a>
    </p>
</div>
""", unsafe_allow_html=True)
