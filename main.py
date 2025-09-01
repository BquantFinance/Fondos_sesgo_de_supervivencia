import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import numpy as np
import re
import yfinance as yf

# Page configuration
st.set_page_config(
    page_title="Análisis Fondos CNMV - Sesgo de Supervivencia",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Modern, minimalist CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }
    
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        background-attachment: fixed;
    }
    
    .main {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 20px;
        padding: 2rem;
        margin: 1rem;
        backdrop-filter: blur(10px);
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
    }
    
    /* Metrics with glassmorphism */
    [data-testid="metric-container"] {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.9) 0%, rgba(255, 255, 255, 0.7) 100%);
        padding: 1.5rem;
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.8);
        box-shadow: 0 8px 32px rgba(31, 38, 135, 0.15);
        backdrop-filter: blur(10px);
        transition: transform 0.3s ease;
    }
    
    [data-testid="metric-container"]:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 40px rgba(31, 38, 135, 0.2);
    }
    
    [data-testid="metric-container"] [data-testid="metric-label"] {
        color: #64748b;
        font-size: 0.875rem;
        font-weight: 500;
        letter-spacing: 0.5px;
        text-transform: uppercase;
    }
    
    [data-testid="metric-container"] [data-testid="metric-value"] {
        color: #1e293b;
        font-size: 2rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    [data-testid="metric-container"] [data-testid="metric-delta"] {
        color: #64748b;
        font-size: 0.875rem;
    }
    
    /* Headers */
    h1 {
        color: #1e293b;
        font-weight: 700;
        font-size: 2.5rem;
        letter-spacing: -1px;
        margin-bottom: 0.5rem;
    }
    
    h2 {
        color: #334155;
        font-weight: 600;
        font-size: 1.75rem;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    
    h3 {
        color: #475569;
        font-weight: 500;
        font-size: 1.25rem;
    }
    
    /* Search input styling */
    .stTextInput > div > div > input {
        background: white;
        border: 2px solid #e2e8f0;
        border-radius: 12px;
        padding: 0.75rem 1rem;
        font-size: 1rem;
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* Select box styling */
    .stSelectbox > div > div {
        background: white;
        border-radius: 12px;
        border: 2px solid #e2e8f0;
    }
    
    /* Dataframe styling */
    [data-testid="stDataFrame"] {
        background: white;
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
    }
    
    .dataframe {
        font-size: 14px;
        border: none !important;
    }
    
    .dataframe thead tr th {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        font-size: 0.75rem !important;
        letter-spacing: 0.5px !important;
        padding: 1rem !important;
    }
    
    .dataframe tbody tr:hover {
        background: #f8fafc !important;
    }
    
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        background: rgba(255, 255, 255, 0.5);
        border-radius: 16px;
        padding: 0.5rem;
        gap: 0.5rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 12px;
        color: #64748b;
        font-weight: 500;
        padding: 0.75rem 1.5rem;
        transition: all 0.3s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(255, 255, 255, 0.5);
    }
    
    .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
        background: white;
        color: #667eea;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.15);
    }
    
    /* Author box */
    .author-box {
        background: white;
        padding: 1rem 2rem;
        border-radius: 16px;
        margin: 1.5rem 0;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        font-size: 0.9rem;
        color: #64748b;
    }
    
    .author-box a {
        color: #667eea;
        text-decoration: none;
        font-weight: 600;
        transition: color 0.3s ease;
    }
    
    .author-box a:hover {
        color: #764ba2;
    }
    
    /* Info boxes */
    .info-box {
        background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
        border-left: 4px solid #667eea;
        padding: 1rem 1.5rem;
        margin: 1rem 0;
        border-radius: 8px;
        color: #334155;
    }
    
    .warning-box {
        background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
        border-left: 4px solid #ef4444;
        padding: 1rem 1.5rem;
        margin: 1rem 0;
        border-radius: 8px;
        color: #991b1b;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: white;
        padding-top: 2rem;
    }
    
    [data-testid="stSidebar"] .element-container {
        padding: 0 1rem;
    }
    
    /* Radio buttons */
    .stRadio > label {
        color: #334155;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    
    /* Plotly charts background */
    .js-plotly-plot {
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
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
        border-color: #667eea;
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

# Load S&P 500 data
@st.cache_data
def load_sp500_data():
    try:
        sp500 = yf.download('^GSPC', start='2004-01-01', end='2025-12-31', progress=False, multi_level_index=False)
        sp500 = sp500[['Close']]
        sp500.columns = ['SP500']
        sp500['Returns'] = sp500['SP500'].pct_change() * 100
        return sp500
    except:
        return pd.DataFrame()

# Load main data
df = load_and_process_data()

# Calculate key metrics
births = df[df['status'] == 'NUEVAS_INSCRIPCIONES']
deaths = df[df['status'] == 'BAJAS']

total_births = len(births)
total_deaths = len(deaths)
mortality_rate = (total_deaths / total_births * 100) if total_births > 0 else 0
net_change = total_births - total_deaths

# Title
st.markdown("# 🔍 Búsqueda y Análisis de Fondos Españoles")
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
        delta="registrados",
        help="Total de fondos creados 2004-2025"
    )

with col2:
    st.metric(
        label="Liquidados",
        value=f"{total_deaths:,}",
        delta=f"{mortality_rate:.0f}% mortalidad",
        help="Fondos dados de baja"
    )

with col3:
    st.metric(
        label="Activos",
        value=f"{total_births - total_deaths:,}",
        delta="estimados",
        help="Fondos potencialmente activos"
    )

with col4:
    st.metric(
        label="Sesgo",
        value=f"{abs(net_change):,}",
        delta="fondos ocultos",
        delta_color="inverse",
        help="Fondos que desaparecen de las estadísticas"
    )

# Main tabs
tabs = ["🔍 **Búsqueda de Fondos**", "📊 **Análisis Temporal**", "📈 **Impacto del Sesgo**"]
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
        
        # Include all columns including Depositaria
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

# Tab 2: Temporal Analysis
with tab_list[1]:
    st.markdown("### Evolución Temporal del Sesgo")
    
    # Prepare yearly data
    yearly_stats = df.groupby(['year', 'status']).size().unstack(fill_value=0)
    yearly_stats = yearly_stats.rename(columns={
        'NUEVAS_INSCRIPCIONES': 'Altas',
        'BAJAS': 'Bajas'
    })
    yearly_stats['Cambio_Neto'] = yearly_stats['Altas'] - yearly_stats['Bajas']
    yearly_stats = yearly_stats.reset_index()
    
    # Create beautiful gradient chart
    fig = go.Figure()
    
    # Births
    fig.add_trace(go.Bar(
        x=yearly_stats['year'],
        y=yearly_stats['Altas'],
        name='Altas',
        marker=dict(
            color=yearly_stats['Altas'],
            colorscale='Viridis',
            line=dict(width=0)
        ),
        text=yearly_stats['Altas'],
        textposition='outside',
        hovertemplate='<b>%{x}</b><br>Altas: %{y}<extra></extra>'
    ))
    
    # Deaths
    fig.add_trace(go.Bar(
        x=yearly_stats['year'],
        y=-yearly_stats['Bajas'],
        name='Bajas',
        marker=dict(
            color=yearly_stats['Bajas'],
            colorscale='Reds',
            line=dict(width=0)
        ),
        text=yearly_stats['Bajas'],
        textposition='outside',
        hovertemplate='<b>%{x}</b><br>Bajas: %{y}<extra></extra>'
    ))
    
    # Net change line
    fig.add_trace(go.Scatter(
        x=yearly_stats['year'],
        y=yearly_stats['Cambio_Neto'],
        name='Balance Neto',
        line=dict(color='#667eea', width=3),
        mode='lines+markers',
        marker=dict(size=10, color='#667eea', line=dict(width=2, color='white')),
        hovertemplate='<b>%{x}</b><br>Balance: %{y:+}<extra></extra>'
    ))
    
    fig.update_layout(
        xaxis_title="",
        yaxis_title="Número de Fondos",
        hovermode='x unified',
        height=500,
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family='Inter', color='#334155'),
        barmode='relative',
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5,
            bgcolor='rgba(255,255,255,0.8)',
            borderwidth=0
        )
    )
    
    fig.add_hline(y=0, line_color="#e2e8f0", line_width=2)
    fig.update_xaxes(gridcolor='#f1f5f9', showgrid=False, zeroline=False)
    fig.update_yaxes(gridcolor='#f1f5f9', showgrid=True, zeroline=False)
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Period analysis
    st.markdown("### Análisis por Períodos")
    
    periods = {
        "Pre-Crisis (2004-2008)": (2004, 2008),
        "Crisis Financiera (2009-2015)": (2009, 2015),
        "Recuperación (2016-2019)": (2016, 2019),
        "Era COVID (2020-2025)": (2020, 2025)
    }
    
    period_stats = []
    for period_name, (start_year, end_year) in periods.items():
        period_data = yearly_stats[(yearly_stats['year'] >= start_year) & (yearly_stats['year'] <= end_year)]
        if len(period_data) > 0:
            total_births_period = period_data['Altas'].sum()
            total_deaths_period = period_data['Bajas'].sum()
            net_change_period = total_births_period - total_deaths_period
            mortality_rate_period = (total_deaths_period / total_births_period * 100) if total_births_period > 0 else 0
            
            period_stats.append({
                'Período': period_name,
                'Altas': total_births_period,
                'Bajas': total_deaths_period,
                'Balance': net_change_period,
                'Mortalidad (%)': f"{mortality_rate_period:.1f}"
            })
    
    period_df = pd.DataFrame(period_stats)
    
    st.dataframe(
        period_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Período": st.column_config.TextColumn("Período", width="medium"),
            "Altas": st.column_config.NumberColumn("Altas", format="%d"),
            "Bajas": st.column_config.NumberColumn("Bajas", format="%d"),
            "Balance": st.column_config.NumberColumn("Balance", format="%d"),
            "Mortalidad (%)": st.column_config.TextColumn("Mortalidad (%)")
        }
    )

# Tab 3: Impact Analysis
with tab_list[2]:
    st.markdown("### El Impacto Real del Sesgo de Supervivencia")
    
    # Load S&P 500 for comparison
    sp500_data = load_sp500_data()
    
    if not sp500_data.empty:
        # Calculate monthly stats
        monthly_stats = df.groupby(['year', 'month', 'status']).size().unstack(fill_value=0)
        monthly_stats = monthly_stats.rename(columns={
            'NUEVAS_INSCRIPCIONES': 'Altas',
            'BAJAS': 'Bajas'
        })
        monthly_stats['Mortalidad'] = (monthly_stats['Bajas'] / monthly_stats['Altas'] * 100).fillna(0)
        monthly_stats = monthly_stats.reset_index()
        monthly_stats['date'] = pd.to_datetime(monthly_stats[['year', 'month']].assign(day=1))
        
        # Create comparison chart
        fig2 = make_subplots(
            rows=2, cols=1,
            row_heights=[0.6, 0.4],
            vertical_spacing=0.1,
            subplot_titles=('S&P 500 vs Mortalidad de Fondos', 'Correlación Temporal')
        )
        
        # S&P 500
        fig2.add_trace(
            go.Scatter(
                x=sp500_data.index,
                y=sp500_data['SP500'],
                name='S&P 500',
                fill='tozeroy',
                fillcolor='rgba(102, 126, 234, 0.1)',
                line=dict(color='#667eea', width=2),
                hovertemplate='S&P 500: $%{y:,.0f}<extra></extra>'
            ),
            row=1, col=1
        )
        
        # Mortality overlay
        fig2.add_trace(
            go.Scatter(
                x=monthly_stats['date'],
                y=monthly_stats['Mortalidad'],
                name='Mortalidad (%)',
                yaxis='y2',
                line=dict(color='#ef4444', width=2),
                hovertemplate='Mortalidad: %{y:.1f}%<extra></extra>'
            ),
            row=2, col=1
        )
        
        fig2.update_layout(
            height=600,
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(family='Inter', color='#334155'),
            hovermode='x unified',
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.1,
                xanchor="center",
                x=0.5
            )
        )
        
        fig2.update_xaxes(gridcolor='#f1f5f9', showgrid=False)
        fig2.update_yaxes(gridcolor='#f1f5f9', showgrid=True)
        
        st.plotly_chart(fig2, use_container_width=True)
    
    # Impact explanation
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="info-box">
            <h4>📊 Impacto en Rentabilidades</h4>
            <ul style="line-height: 1.8;">
                <li>Los fondos liquidados desaparecen de las estadísticas</li>
                <li>Solo sobreviven los fondos con mejor performance</li>
                <li>Las rentabilidades históricas están infladas artificialmente</li>
                <li>El riesgo real está sistemáticamente subestimado</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="warning-box">
            <h4>⚠️ Para el Inversor</h4>
            <ul style="line-height: 1.8;">
                <li>No confíes solo en rentabilidades históricas promedio</li>
                <li>El riesgo de pérdida es mayor al publicado</li>
                <li>Muchos fondos "ganadores" de hoy serán los muertos de mañana</li>
                <li>Considera alternativas de inversión pasiva e indexada</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #64748b; padding: 2rem 0; font-size: 0.875rem;">
    <p>Este análisis demuestra el severo sesgo de supervivencia en la industria de fondos española.</p>
    <p>Con una tasa de mortalidad del {:.0f}%, las estadísticas publicadas no reflejan la realidad completa.</p>
    <p style="margin-top: 1rem;">
        <a href="https://twitter.com/Gsnchez" target="_blank" style="color: #667eea;">@Gsnchez</a> • 
        <a href="https://bquantfinance.com" target="_blank" style="color: #667eea;">bquantfinance.com</a>
    </p>
</div>
""".format(mortality_rate), unsafe_allow_html=True)
