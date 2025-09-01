import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import numpy as np
import re
import pandas_datareader.data as wb
import yfinance as yf

# Page configuration
st.set_page_config(
    page_title="Análisis Sesgo de Supervivencia - Fondos CNMV",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional styling
st.markdown("""
<style>
    .stApp {
        background-color: #0e1117;
    }
    
    [data-testid="metric-container"] {
        background: linear-gradient(135deg, #1a1f2e 0%, #242b3d 100%);
        padding: 1.2rem;
        border-radius: 8px;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    [data-testid="metric-container"] [data-testid="metric-label"] {
        color: #94a3b8;
        font-size: 0.85rem;
        font-weight: 500;
    }
    
    [data-testid="metric-container"] [data-testid="metric-value"] {
        color: #f1f5f9;
        font-size: 1.8rem;
        font-weight: 600;
    }
    
    h1 {
        color: #f1f5f9;
        font-weight: 400;
        font-size: 2.2rem;
        margin-bottom: 0.5rem;
    }
    
    h2 {
        color: #cbd5e1;
        font-weight: 400;
        margin-top: 2rem;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid #334155;
    }
    
    h3 {
        color: #e2e8f0;
        font-weight: 400;
    }
    
    .author-box {
        background: linear-gradient(135deg, #4338ca 0%, #5b21b6 100%);
        padding: 0.8rem 1.5rem;
        border-radius: 8px;
        margin: 1rem 0 2rem 0;
        text-align: center;
        font-size: 0.95rem;
    }
    
    .author-box a {
        color: #f1f5f9;
        text-decoration: none;
        font-weight: 600;
    }
    
    .author-box a:hover {
        text-decoration: underline;
    }
    
    .info-box {
        background: #1a1f2e;
        border-left: 3px solid #4338ca;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 4px;
        color: #cbd5e1;
    }
    
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1f2e 0%, #0e1117 100%);
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
        background-color: transparent;
    }
    
    .stTabs [data-baseweb="tab"] {
        padding-left: 20px;
        padding-right: 20px;
        color: #94a3b8;
        font-weight: 500;
    }
    
    .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
        background: linear-gradient(135deg, #4338ca 0%, #5b21b6 100%);
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# Title and author
st.markdown("# 📊 Análisis del Sesgo de Supervivencia en Fondos de Inversión Españoles")
st.markdown("""
<div class="author-box">
    Creado por <a href="https://twitter.com/Gsnchez" target="_blank">@Gsnchez</a> | 
    <a href="https://bquantfinance.com" target="_blank">bquantfinance.com</a><br>
    Datos: CNMV (Comisión Nacional del Mercado de Valores) | Período: 2004-2025
</div>
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
    df['month_name'] = df['date'].dt.strftime('%B')
    
    df['status_esp'] = df['status'].map({
        'NUEVAS_INSCRIPCIONES': 'Altas',
        'BAJAS': 'Bajas'
    })
    
    return df

# Load macro data from FRED
@st.cache_data
def load_macro_data():
    try:
        start_date = '2004-01-01'
        end_date = '2025-12-31'
        
        indicators = {
            'IRLTLT01ESM156N': 'Spanish_10Y_Bond',
            'CLVMNACSCAB1GQES': 'Spain_GDP_Growth',
            'LRHUTTTTESM156S': 'Spain_Unemployment',
            'DEXESUS': 'EUR_USD',
            'VIXCLS': 'VIX',
            'DGS10': 'US_10Y_Bond',
            'FEDFUNDS': 'Fed_Rate',
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
        macro_data['year'] = macro_data.index.year
        macro_data['month'] = macro_data.index.month
        
        return macro_data
    
    except Exception as e:
        st.warning(f"Error loading macro data: {e}")
        return pd.DataFrame()

# Load S&P 500 data
@st.cache_data
def load_sp500_data():
    try:
        sp500 = yf.download('^GSPC', start='2004-01-01', end='2025-12-31', progress=False, multi_level_index=False)
        sp500 = sp500[['Close', 'Volume']]
        sp500.columns = ['SP500_Close', 'SP500_Volume']
        
        sp500['SP500_Returns'] = sp500['SP500_Close'].pct_change() * 100
        sp500['SP500_MA50'] = sp500['SP500_Close'].rolling(window=50).mean()
        sp500['SP500_MA200'] = sp500['SP500_Close'].rolling(window=200).mean()
        
        sp500['year'] = sp500.index.year
        sp500['month'] = sp500.index.month
        
        return sp500
    
    except Exception as e:
        st.warning(f"Error loading S&P 500 data: {e}")
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

# Sidebar filters
st.sidebar.markdown("## 🔍 Filtros de Análisis")
st.sidebar.markdown("---")

# Year filter
years_available = sorted(df['year'].unique())
year_filter_type = st.sidebar.radio(
    "Filtro de Años",
    options=['Todos los años', 'Selección personalizada'],
    index=0
)

if year_filter_type == 'Todos los años':
    selected_years = years_available
else:
    selected_years = st.sidebar.multiselect(
        "Seleccionar Años",
        options=years_available,
        default=years_available,
        help="Seleccione uno o varios años para analizar"
    )

# Month filter
months_order = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 
                'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
months_esp = {
    'January': 'Enero', 'February': 'Febrero', 'March': 'Marzo', 'April': 'Abril',
    'May': 'Mayo', 'June': 'Junio', 'July': 'Julio', 'August': 'Agosto',
    'September': 'Septiembre', 'October': 'Octubre', 'November': 'Noviembre', 'December': 'Diciembre'
}

month_filter_type = st.sidebar.radio(
    "Filtro de Meses",
    options=['Todos los meses', 'Selección personalizada'],
    index=0
)

if month_filter_type == 'Todos los meses':
    selected_months = months_order
else:
    selected_months = st.sidebar.multiselect(
        "Seleccionar Meses",
        options=months_order,
        default=months_order,
        help="Seleccione uno o varios meses"
    )

# Status filter
status_filter = st.sidebar.radio(
    "Tipo de Operación",
    options=['Ambas', 'Solo Altas', 'Solo Bajas'],
    index=0
)

# Apply filters
filtered_df = df[df['year'].isin(selected_years)]
reverse_months_esp = {v: k for k, v in months_esp.items()}
selected_months_eng = [reverse_months_esp.get(m, m) for m in selected_months]
filtered_df = filtered_df[filtered_df['month_name'].isin(selected_months_eng)]

if status_filter == 'Solo Altas':
    filtered_df = filtered_df[filtered_df['status'] == 'NUEVAS_INSCRIPCIONES']
elif status_filter == 'Solo Bajas':
    filtered_df = filtered_df[filtered_df['status'] == 'BAJAS']

# Display options
st.sidebar.markdown("---")
st.sidebar.markdown("## 📈 Opciones de Visualización")
show_macro_analysis = st.sidebar.checkbox("Mostrar análisis macro", value=True)

# Main metrics
st.markdown("## 📊 Resumen General del Período Completo")

# Show active filters
if year_filter_type != 'Todos los años' or month_filter_type != 'Todos los meses':
    filter_text = []
    if year_filter_type != 'Todos los años':
        filter_text.append(f"Años: {', '.join(map(str, selected_years))}")
    if month_filter_type != 'Todos los meses':
        filter_text.append(f"Meses: {', '.join(selected_months)}")
    st.info(f"**Filtros activos:** {' | '.join(filter_text)}")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="Total Altas",
        value=f"{total_births:,}",
        delta="Fondos creados",
        help="Total de fondos registrados en el período"
    )

with col2:
    st.metric(
        label="Total Bajas",
        value=f"{total_deaths:,}",
        delta="Fondos liquidados",
        help="Total de fondos dados de baja"
    )

with col3:
    st.metric(
        label="Tasa de Mortalidad",
        value=f"{mortality_rate:.1f}%",
        delta="Bajas/Altas",
        help="Porcentaje de bajas sobre altas. >100% significa más bajas que altas"
    )

with col4:
    st.metric(
        label="Balance Neto",
        value=f"{net_change:,}",
        delta="Altas - Bajas",
        delta_color="inverse" if net_change < 0 else "normal",
        help="Diferencia entre altas y bajas"
    )

# Note about mortality rate
if mortality_rate > 100:
    st.info(f"""
    📌 **Nota sobre la Tasa de Mortalidad:** Una tasa del {mortality_rate:.1f}% indica que por cada 100 fondos creados, 
    {int(mortality_rate)} fondos han sido liquidados. Esto evidencia un sesgo de supervivencia significativo en las bases de datos históricas.
    """)

# Prepare yearly data
yearly_stats = df.groupby(['year', 'status']).size().unstack(fill_value=0)
yearly_stats = yearly_stats.rename(columns={
    'NUEVAS_INSCRIPCIONES': 'Altas',
    'BAJAS': 'Bajas'
})
yearly_stats['Cambio_Neto'] = yearly_stats['Altas'] - yearly_stats['Bajas']
yearly_stats['Tasa_Mortalidad'] = (yearly_stats['Bajas'] / yearly_stats['Altas'] * 100).fillna(0).round(1)
yearly_stats = yearly_stats.reset_index()

# Tabs
tabs = ["📈 **Análisis Temporal**", "🔍 **Búsqueda de Fondos**", "🌍 **Análisis Macro**"]
tab_list = st.tabs(tabs)

# Tab 1: Temporal Analysis
with tab_list[0]:
    st.markdown("### Evolución Histórica de Altas y Bajas")
    
    fig1 = go.Figure()
    
    fig1.add_trace(go.Bar(
        x=yearly_stats['year'],
        y=yearly_stats['Altas'],
        name='Altas',
        marker_color='#22c55e',
        text=yearly_stats['Altas'],
        textposition='outside',
        hovertemplate='<b>%{x}</b><br>Altas: %{y}<extra></extra>'
    ))
    
    fig1.add_trace(go.Bar(
        x=yearly_stats['year'],
        y=-yearly_stats['Bajas'],
        name='Bajas',
        marker_color='#dc2626',
        text=yearly_stats['Bajas'],
        textposition='outside',
        hovertemplate='<b>%{x}</b><br>Bajas: %{y}<extra></extra>'
    ))
    
    fig1.add_trace(go.Scatter(
        x=yearly_stats['year'],
        y=yearly_stats['Cambio_Neto'],
        name='Cambio Neto',
        line=dict(color='#fbbf24', width=2.5),
        mode='lines+markers',
        marker=dict(size=8),
        hovertemplate='<b>%{x}</b><br>Cambio Neto: %{y:+}<extra></extra>'
    ))
    
    fig1.update_layout(
        xaxis_title="Año",
        yaxis_title="Número de Fondos",
        hovermode='x unified',
        height=450,
        plot_bgcolor='#1a1f2e',
        paper_bgcolor='#0e1117',
        font=dict(color='#cbd5e1', size=12),
        barmode='relative',
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5
        )
    )
    
    fig1.add_hline(y=0, line_color="#64748b", line_width=1)
    fig1.update_xaxes(gridcolor='#334155', showgrid=False)
    fig1.update_yaxes(gridcolor='#334155', showgrid=True)
    
    st.plotly_chart(fig1, use_container_width=True)

# Tab 2: Fund Search
with tab_list[1]:
    st.markdown("### 🔍 Búsqueda y Ciclo de Vida de Fondos")
    
    births_lifecycle = births[births['N_Registro'].notna()][['Nombre', 'N_Registro', 'date', 'Gestora', 'Depositaria']].copy()
    births_lifecycle = births_lifecycle.rename(columns={'date': 'Fecha_Alta'})
    
    deaths_lifecycle = deaths[deaths['N_Registro'].notna()][['Nombre', 'N_Registro', 'date']].copy()
    deaths_lifecycle = deaths_lifecycle.rename(columns={'date': 'Fecha_Baja'})
    
    unique_funds = births_lifecycle.groupby('N_Registro').agg({
        'Nombre': 'first',
        'Fecha_Alta': 'min',
        'Gestora': 'first',
        'Depositaria': 'first'
    }).reset_index()
    
    death_dates = deaths_lifecycle.groupby('N_Registro').agg({
        'Fecha_Baja': 'min'
    }).reset_index()
    
    fund_lifecycle = unique_funds.merge(death_dates, on='N_Registro', how='left')
    
    fund_lifecycle['Vida_Dias'] = (fund_lifecycle['Fecha_Baja'] - fund_lifecycle['Fecha_Alta']).dt.days
    fund_lifecycle['Vida_Anos'] = (fund_lifecycle['Vida_Dias'] / 365.25).round(1)
    fund_lifecycle['Estado_Actual'] = fund_lifecycle['Fecha_Baja'].apply(lambda x: '💀 Liquidado' if pd.notna(x) else '✅ Activo')
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        search_term = st.text_input(
            "🔍 Buscar fondo por nombre o número de registro",
            placeholder="Ej: CAIXASABADELL o 3043",
            help="Busque por nombre del fondo o número de registro CNMV"
        )
    
    with col2:
        status_search = st.selectbox(
            "Estado del fondo",
            options=['Todos', 'Activos', 'Liquidados'],
            index=0
        )
    
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
    
    if total_in_search > 0:
        display_lifecycle = filtered_lifecycle[['N_Registro', 'Nombre', 'Fecha_Alta', 'Fecha_Baja', 
                                               'Vida_Anos', 'Estado_Actual', 'Gestora']].copy()
        
        display_lifecycle['N_Registro'] = display_lifecycle['N_Registro'].astype(int)
        display_lifecycle = display_lifecycle.sort_values('Fecha_Alta', ascending=False)
        
        display_lifecycle['Fecha_Alta'] = display_lifecycle['Fecha_Alta'].dt.strftime('%Y-%m-%d')
        display_lifecycle['Fecha_Baja'] = display_lifecycle['Fecha_Baja'].dt.strftime('%Y-%m-%d')
        
        st.dataframe(
            display_lifecycle,
            use_container_width=True,
            height=400,
            hide_index=True
        )

# Tab 3: Macro Analysis
with tab_list[2]:
    st.markdown("### 🌍 Análisis del Ciclo Económico y Mortalidad de Fondos")
    
    if show_macro_analysis:
        macro_data = load_macro_data()
        sp500_data = load_sp500_data()
        
        if not sp500_data.empty or not macro_data.empty:
            st.markdown("### 📈 Vista Global: Mercados y Fondos")
            
            monthly_fund_stats = df.groupby(['year', 'month', 'status']).size().unstack(fill_value=0)
            monthly_fund_stats = monthly_fund_stats.rename(columns={
                'NUEVAS_INSCRIPCIONES': 'Altas',
                'BAJAS': 'Bajas'
            })
            monthly_fund_stats['Mortalidad'] = (monthly_fund_stats['Bajas'] / monthly_fund_stats['Altas'] * 100).fillna(0)
            monthly_fund_stats['Balance'] = monthly_fund_stats['Altas'] - monthly_fund_stats['Bajas']
            monthly_fund_stats = monthly_fund_stats.reset_index()
            monthly_fund_stats['date'] = pd.to_datetime(monthly_fund_stats[['year', 'month']].assign(day=1))
            
            fig_overview = make_subplots(
                rows=3, cols=1,
                row_heights=[0.5, 0.25, 0.25],
                vertical_spacing=0.05,
                subplot_titles=(
                    'S&P 500 y Fondos Españoles',
                    'Flujo Neto de Fondos',
                    'Tasa de Mortalidad'
                ),
                specs=[
                    [{"secondary_y": True}],
                    [{"secondary_y": False}],
                    [{"secondary_y": False}]
                ]
            )
            
            if not sp500_data.empty:
                fig_overview.add_trace(
                    go.Scatter(
                        x=sp500_data.index,
                        y=sp500_data['SP500_Close'],
                        name='S&P 500',
                        fill='tozeroy',
                        fillcolor='rgba(67, 56, 202, 0.1)',
                        line=dict(color='#4338ca', width=2),
                        hovertemplate='<b>S&P 500</b><br>%{x|%Y-%m-%d}<br>Close: $%{y:,.0f}<extra></extra>'
                    ),
                    row=1, col=1,
                    secondary_y=False
                )
            
            fig_overview.add_trace(
                go.Bar(
                    x=monthly_fund_stats['date'],
                    y=monthly_fund_stats['Altas'],
                    name='Altas',
                    marker_color='rgba(34, 197, 94, 0.6)',
                    yaxis='y2',
                    hovertemplate='<b>Altas</b><br>%{x|%Y-%m}<br>Fondos: %{y}<extra></extra>'
                ),
                row=1, col=1,
                secondary_y=True
            )
            
            fig_overview.add_trace(
                go.Bar(
                    x=monthly_fund_stats['date'],
                    y=-monthly_fund_stats['Bajas'],
                    name='Bajas',
                    marker_color='rgba(220, 38, 38, 0.6)',
                    yaxis='y2',
                    hovertemplate='<b>Bajas</b><br>%{x|%Y-%m}<br>Fondos: %{y}<extra></extra>'
                ),
                row=1, col=1,
                secondary_y=True
            )
            
            colors = ['#22c55e' if x >= 0 else '#dc2626' for x in monthly_fund_stats['Balance']]
            fig_overview.add_trace(
                go.Bar(
                    x=monthly_fund_stats['date'],
                    y=monthly_fund_stats['Balance'],
                    name='Balance Neto',
                    marker_color=colors,
                    hovertemplate='<b>Balance</b><br>%{x|%Y-%m}<br>Neto: %{y:+}<extra></extra>',
                    showlegend=False
                ),
                row=2, col=1
            )
            
            fig_overview.add_trace(
                go.Scatter(
                    x=monthly_fund_stats['date'],
                    y=monthly_fund_stats['Mortalidad'],
                    name='Tasa Mortalidad (%)',
                    line=dict(color='#dc2626', width=2),
                    hovertemplate='<b>Mortalidad</b><br>%{x|%Y-%m}<br>%{y:.1f}%<extra></extra>'
                ),
                row=3, col=1
            )
            
            crisis_periods = [
                {"name": "Crisis Financiera", "start": "2008-09-01", "end": "2009-06-01", "color": "rgba(220, 38, 38, 0.1)"},
                {"name": "Crisis Deuda EU", "start": "2011-08-01", "end": "2012-07-01", "color": "rgba(251, 191, 36, 0.1)"},
                {"name": "COVID-19", "start": "2020-02-01", "end": "2020-05-01", "color": "rgba(139, 92, 246, 0.1)"}
            ]
            
            # Add crisis periods as shapes instead of vrects for better subplot compatibility
            for period in crisis_periods:
                fig_overview.add_shape(
                    type="rect",
                    xref="x",
                    yref="paper",
                    x0=period["start"],
                    x1=period["end"],
                    y0=0,
                    y1=1,
                    fillcolor=period["color"],
                    layer="below",
                    line_width=0,
                    row=1, col=1
                )
                
                fig_overview.add_annotation(
                    x=period["start"],
                    y=1,
                    yref="paper",
                    text=period["name"],
                    showarrow=False,
                    row=1, col=1
                )
            
            fig_overview.update_yaxes(title_text="S&P 500 Index", row=1, col=1, secondary_y=False)
            fig_overview.update_yaxes(title_text="Número de Fondos", row=1, col=1, secondary_y=True)
            fig_overview.update_yaxes(title_text="Balance Neto", row=2, col=1)
            fig_overview.update_yaxes(title_text="Mortalidad (%)", row=3, col=1)
            
            fig_overview.update_layout(
                height=900,
                plot_bgcolor='#1a1f2e',
                paper_bgcolor='#0e1117',
                font=dict(color='#cbd5e1', size=11),
                hovermode='x unified',
                legend=dict(
                    orientation="h",
                    yanchor="top",
                    y=1.05,
                    xanchor="center",
                    x=0.5
                )
            )
            
            st.plotly_chart(fig_overview, key="overview_chart", use_container_width=True)
            
            if not sp500_data.empty:
                sp500_monthly = sp500_data.groupby(['year', 'month'])['SP500_Returns'].mean().reset_index()
                merged_for_corr = monthly_fund_stats.merge(
                    sp500_monthly,
                    on=['year', 'month'],
                    how='inner'
                )
                
                if len(merged_for_corr) > 10:
                    corr_sp500_mortality = merged_for_corr['Mortalidad'].corr(merged_for_corr['SP500_Returns'])
                    
                    st.markdown(f"""
                    <div class="info-box">
                        <h4>📊 Insights del Análisis</h4>
                        <ul style="line-height: 1.8;">
                            <li>Correlación S&P 500 Returns vs Mortalidad: <strong>{corr_sp500_mortality:.3f}</strong></li>
                            <li>Las crisis globales coinciden con picos de mortalidad</li>
                            <li>Los mercados alcistas no garantizan supervivencia de fondos locales</li>
                        </ul>
                    </div>
                    """, unsafe_allow_html=True)
    else:
        st.info("Active 'Mostrar análisis macro' en el panel lateral para ver el análisis del ciclo económico.")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #64748b; padding: 1.5rem 0; font-size: 14px;">
    <p><strong>Análisis del Sesgo de Supervivencia en Fondos de Inversión Españoles</strong></p>
    <p>Datos: CNMV | Período: 2004-2025</p>
    <p>Por <a href="https://twitter.com/Gsnchez" target="_blank" style="color: #4338ca;">@Gsnchez</a> | 
    <a href="https://bquantfinance.com" target="_blank" style="color: #4338ca;">bquantfinance.com</a></p>
</div>
""", unsafe_allow_html=True)
