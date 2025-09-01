import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import numpy as np
import re

# Page configuration
st.set_page_config(
    page_title="Análisis Sesgo de Supervivencia - Fondos CNMV",
    page_icon="💀",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Dark dramatic styling
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(180deg, #0e1117 0%, #1a1f2e 100%);
    }
    
    /* Metrics styling */
    [data-testid="metric-container"] {
        background: linear-gradient(135deg, rgba(220, 38, 38, 0.1) 0%, rgba(127, 29, 29, 0.2) 100%);
        padding: 1.2rem;
        border-radius: 12px;
        border: 1px solid rgba(220, 38, 38, 0.3);
        backdrop-filter: blur(10px);
    }
    
    [data-testid="metric-container"] [data-testid="metric-label"] {
        color: #fca5a5;
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    [data-testid="metric-container"] [data-testid="metric-value"] {
        color: #fef2f2;
        font-size: 2rem;
        font-weight: 700;
    }
    
    /* Headers */
    h1 {
        background: linear-gradient(135deg, #dc2626 0%, #991b1b 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        font-size: 2.8rem;
        text-align: center;
        margin-bottom: 0.5rem;
        letter-spacing: -1px;
    }
    
    h2 {
        color: #f1f5f9;
        font-weight: 600;
        margin-top: 2rem;
        margin-bottom: 1rem;
        font-size: 1.8rem;
    }
    
    h3 {
        color: #e2e8f0;
        font-weight: 500;
    }
    
    .author-box {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        padding: 0.8rem 1.5rem;
        border-radius: 12px;
        margin: 1rem 0 2rem 0;
        text-align: center;
        font-size: 0.95rem;
        border: 1px solid #475569;
    }
    
    .author-box a {
        color: #60a5fa;
        text-decoration: none;
        font-weight: 600;
    }
    
    .author-box a:hover {
        color: #93bbfc;
        text-decoration: underline;
    }
    
    .death-ticker {
        background: linear-gradient(90deg, rgba(220, 38, 38, 0.2) 0%, rgba(127, 29, 29, 0.1) 100%);
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        border-left: 4px solid #dc2626;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.8; }
        100% { opacity: 1; }
    }
    
    .insight-box {
        background: rgba(30, 41, 59, 0.5);
        border: 1px solid #334155;
        padding: 1.2rem;
        border-radius: 12px;
        margin: 1rem 0;
        backdrop-filter: blur(10px);
    }
    
    /* Sidebar simplification */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1f2e 0%, #0e1117 100%);
        padding-top: 2rem;
    }
    
    [data-testid="stSidebar"] .element-container {
        margin-bottom: 1rem;
    }
    
    .stRadio > label {
        color: #cbd5e1;
        font-weight: 600;
        font-size: 1.1rem;
        margin-bottom: 1rem;
    }
    
    /* Warning box */
    .warning-box {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.2) 0%, rgba(185, 28, 28, 0.1) 100%);
        border: 2px solid #dc2626;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 2rem 0;
        text-align: center;
        animation: shake 0.5s;
    }
    
    @keyframes shake {
        0%, 100% { transform: translateX(0); }
        25% { transform: translateX(-5px); }
        75% { transform: translateX(5px); }
    }
    
    /* Hide some default Streamlit elements for cleaner look */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Title and author
st.markdown("# 💀 El Cementerio de Fondos Españoles")
st.markdown("""
<div class="author-box">
    <strong>Análisis del Sesgo de Supervivencia en Fondos de Inversión</strong><br>
    Por <a href="https://twitter.com/Gsnchez" target="_blank">@Gsnchez</a> | 
    <a href="https://bquantfinance.com" target="_blank">bquantfinance.com</a> | 
    Datos: CNMV 2004-2025
</div>
""", unsafe_allow_html=True)

# Load and process data
@st.cache_data
def load_and_process_data():
    df = pd.read_csv('cnmv_funds_data_RAW_final_multipage.csv')
    
    # Extract date from filename
    def extract_date_from_filename(filename):
        match = re.search(r'(\d{2})-(\d{2})-(\d{4})_al_(\d{2})-(\d{2})-(\d{4})', filename)
        if match:
            end_date = pd.to_datetime(f"{match.group(6)}-{match.group(5)}-{match.group(4)}", format='%Y-%m-%d')
            return end_date
        return None
    
    # Add date columns
    df['date'] = df['file'].apply(extract_date_from_filename)
    df = df.dropna(subset=['date'])
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month
    df['year_month'] = df['date'].dt.to_period('M')
    
    return df

df = load_and_process_data()

# Simplified sidebar with preset periods
st.sidebar.markdown("## ⚙️ Control Panel")
st.sidebar.markdown("---")

# Period presets
period_preset = st.sidebar.radio(
    "📅 Período de Análisis",
    options=[
        "📊 Todo (2004-2025)",
        "💥 Crisis Financiera (2009-2015)",
        "🚀 Boom Pre-Crisis (2005-2007)",
        "📈 Recuperación (2016-2019)",
        "🦠 Era COVID (2020-2025)",
        "📆 Último Año"
    ],
    index=0
)

# Apply period filter
if "Todo" in period_preset:
    start_year, end_year = 2004, 2025
    period_label = "Período Completo (2004-2025)"
elif "Crisis" in period_preset:
    start_year, end_year = 2009, 2015
    period_label = "Crisis Financiera (2009-2015)"
elif "Boom" in period_preset:
    start_year, end_year = 2005, 2007
    period_label = "Boom Pre-Crisis (2005-2007)"
elif "Recuperación" in period_preset:
    start_year, end_year = 2016, 2019
    period_label = "Recuperación (2016-2019)"
elif "COVID" in period_preset:
    start_year, end_year = 2020, 2025
    period_label = "Era COVID (2020-2025)"
else:  # Último Año
    start_year = end_year = 2024
    period_label = "Último Año (2024)"

# Filter data
period_df = df[(df['year'] >= start_year) & (df['year'] <= end_year)]
births = period_df[period_df['status'] == 'NUEVAS_INSCRIPCIONES']
deaths = period_df[period_df['status'] == 'BAJAS']

# View mode
view_mode = st.sidebar.radio(
    "🎯 Modo de Visualización",
    options=["📖 Historia", "🔍 Explorador", "📊 Análisis"],
    index=0,
    help="Historia: Narrativa guiada | Explorador: Gráficos interactivos | Análisis: Datos detallados"
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 📥 Descargas")
# Prepare download data
download_df = period_df[['date', 'status', 'Nombre', 'N_Registro', 'Gestora', 'Depositaria']].copy()
csv = download_df.to_csv(index=False)
st.sidebar.download_button(
    label="💾 Descargar Datos CSV",
    data=csv,
    file_name=f'fondos_cnmv_{start_year}_{end_year}.csv',
    mime='text/csv',
)

# Calculate key metrics
total_births = len(births)
total_deaths = len(deaths)
mortality_rate = (total_deaths / total_births * 100) if total_births > 0 else 0
net_change = total_births - total_deaths

# Death ticker
days_in_period = (period_df['date'].max() - period_df['date'].min()).days
if days_in_period > 0 and total_deaths > 0:
    death_frequency = days_in_period / total_deaths
    st.markdown(f"""
    <div class="death-ticker">
        ⚠️ <strong>En {period_label}: Un fondo muere cada {death_frequency:.1f} días</strong> | 
        {total_deaths:,} fondos liquidados | 
        Tasa de mortalidad: {mortality_rate:.1f}%
    </div>
    """, unsafe_allow_html=True)

# Main content based on view mode
if view_mode == "📖 Historia":
    # Story mode with dramatic narrative
    st.markdown("## 📖 La Historia de una Industria en Crisis")
    
    # Act 1: The Setup
    st.markdown("### Acto I: Las Cifras del Desastre")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("🌱 Nacimientos", f"{total_births:,}", 
                  help=f"Fondos creados en {period_label}")
    with col2:
        st.metric("💀 Muertes", f"{total_deaths:,}",
                  help=f"Fondos liquidados en {period_label}")
    with col3:
        st.metric("📉 Déficit", f"{net_change:,}",
                  delta="Más muertes que nacimientos" if net_change < 0 else "Balance positivo",
                  delta_color="inverse")
    with col4:
        st.metric("☠️ Mortalidad", f"{mortality_rate:.0f}%",
                  help="Bajas por cada 100 altas")
    
    # Waterfall chart showing the destruction
    st.markdown("### Acto II: La Cascada de Destrucción")
    
    # Prepare yearly data for waterfall
    yearly_data = []
    cumulative = 0
    
    for year in range(start_year, end_year + 1):
        year_births = len(df[(df['year'] == year) & (df['status'] == 'NUEVAS_INSCRIPCIONES')])
        year_deaths = len(df[(df['year'] == year) & (df['status'] == 'BAJAS')])
        year_net = year_births - year_deaths
        cumulative += year_net
        
        yearly_data.append({
            'year': str(year),
            'births': year_births,
            'deaths': year_deaths,
            'net': year_net,
            'cumulative': cumulative
        })
    
    yearly_df = pd.DataFrame(yearly_data)
    
    # Create waterfall chart
    fig_waterfall = go.Figure()
    
    # Add traces for each year
    for i, row in yearly_df.iterrows():
        if i == 0:
            base = 0
        else:
            base = yearly_df.iloc[i-1]['cumulative']
        
        color = '#10b981' if row['net'] >= 0 else '#dc2626'
        
        fig_waterfall.add_trace(go.Bar(
            x=[row['year']],
            y=[abs(row['net'])],
            base=base if row['net'] >= 0 else base + row['net'],
            marker_color=color,
            name=row['year'],
            text=f"{row['net']:+,}",
            textposition='outside',
            hovertemplate=f"<b>{row['year']}</b><br>Altas: {row['births']}<br>Bajas: {row['deaths']}<br>Neto: {row['net']:+,}<br>Acumulado: {row['cumulative']:+,}<extra></extra>",
            showlegend=False
        ))
    
    fig_waterfall.update_layout(
        title="Evolución Acumulada: Cada Barra es un Año de Pérdidas",
        xaxis_title="Año",
        yaxis_title="Fondos (Acumulado)",
        height=500,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#cbd5e1', size=12),
        hovermode='x unified'
    )
    
    fig_waterfall.add_hline(y=0, line_color="#ef4444", line_width=2, line_dash="dash")
    fig_waterfall.update_xaxes(gridcolor='#334155', showgrid=False)
    fig_waterfall.update_yaxes(gridcolor='#334155', showgrid=True)
    
    st.plotly_chart(fig_waterfall, use_container_width=True)
    
    # Survival funnel
    st.markdown("### Acto III: El Embudo de la Supervivencia")
    
    # Calculate survival rates for cohorts
    survival_periods = [1, 2, 5, 10, 15]
    survival_data = []
    
    for period in survival_periods:
        cutoff_year = 2025 - period
        cohort = df[(df['year'] <= cutoff_year) & (df['status'] == 'NUEVAS_INSCRIPCIONES')]
        cohort_ids = cohort['N_Registro'].dropna().unique()
        
        # Check how many are still alive
        dead = df[(df['status'] == 'BAJAS') & (df['N_Registro'].isin(cohort_ids))]
        alive = len(cohort_ids) - len(dead['N_Registro'].unique())
        survival_rate = (alive / len(cohort_ids) * 100) if len(cohort_ids) > 0 else 0
        
        survival_data.append({
            'Período': f"{period} años",
            'Total': len(cohort_ids),
            'Vivos': alive,
            'Muertos': len(dead['N_Registro'].unique()),
            'Tasa_Supervivencia': survival_rate
        })
    
    survival_df = pd.DataFrame(survival_data)
    
    # Create funnel chart
    fig_funnel = go.Figure()
    
    fig_funnel.add_trace(go.Funnel(
        y=survival_df['Período'],
        x=survival_df['Tasa_Supervivencia'],
        textinfo="value+percent initial",
        texttemplate='%{value:.1f}% supervivientes',
        marker=dict(
            color=survival_df['Tasa_Supervivencia'],
            colorscale=[[0, '#dc2626'], [0.5, '#f59e0b'], [1, '#10b981']],
            line=dict(width=2, color='#334155')
        ),
        hovertemplate='<b>Tras %{y}</b><br>Supervivencia: %{x:.1f}%<br>Total inicial: %{initial}<extra></extra>'
    ))
    
    fig_funnel.update_layout(
        title="Tasa de Supervivencia por Antigüedad",
        height=400,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#cbd5e1', size=12)
    )
    
    st.plotly_chart(fig_funnel, use_container_width=True)
    
    # Warning message
    st.markdown("""
    <div class="warning-box">
        <h3>⚠️ ALERTA: SESGO DE SUPERVIVENCIA EXTREMO</h3>
        <p style="font-size: 1.1rem; margin: 1rem 0;">
            Los datos históricos de rentabilidad <strong>excluyen los fondos liquidados</strong>, 
            creando una ilusión de rendimientos superiores. Con una tasa de mortalidad del 
            <strong>{:.0f}%</strong>, las rentabilidades publicadas están <strong>significativamente infladas</strong>.
        </p>
        <p style="font-size: 0.9rem; color: #fca5a5;">
            Este sesgo hace que el inversor medio sobrestime sistemáticamente las probabilidades de éxito en fondos activos.
        </p>
    </div>
    """.format(mortality_rate), unsafe_allow_html=True)

elif view_mode == "🔍 Explorador":
    # Explorer mode with interactive visualizations
    st.markdown("## 🔍 Explorador Interactivo")
    
    # Prepare data
    yearly_stats = df.groupby(['year', 'status']).size().unstack(fill_value=0)
    yearly_stats = yearly_stats.rename(columns={
        'NUEVAS_INSCRIPCIONES': 'Altas',
        'BAJAS': 'Bajas'
    })
    yearly_stats['Cambio_Neto'] = yearly_stats['Altas'] - yearly_stats['Bajas']
    yearly_stats['Tasa_Mortalidad'] = (yearly_stats['Bajas'] / yearly_stats['Altas'] * 100).fillna(0)
    yearly_stats = yearly_stats.reset_index()
    
    # Tab selection for different visualizations
    tab1, tab2, tab3, tab4 = st.tabs(["🌡️ **Mapa de Calor**", "📊 **Evolución Temporal**", 
                                       "🎯 **Análisis Gestoras**", "🔬 **Búsqueda Fondos**"])
    
    with tab1:
        # Mortality heatmap
        st.markdown("### 🌡️ Mapa de Calor de Mortalidad")
        
        # Prepare monthly data for heatmap
        monthly_stats = df.groupby(['year', 'month', 'status']).size().unstack(fill_value=0)
        monthly_stats = monthly_stats.rename(columns={
            'NUEVAS_INSCRIPCIONES': 'Altas',
            'BAJAS': 'Bajas'
        })
        monthly_stats['Mortalidad'] = (monthly_stats['Bajas'] / monthly_stats['Altas'] * 100).fillna(0)
        monthly_stats = monthly_stats.reset_index()
        
        # Pivot for heatmap
        heatmap_data = monthly_stats.pivot(index='month', columns='year', values='Mortalidad')
        
        # Create heatmap
        fig_heatmap = go.Figure(data=go.Heatmap(
            z=heatmap_data.values,
            x=heatmap_data.columns,
            y=['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 
               'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'],
            colorscale=[[0, '#10b981'], [0.5, '#f59e0b'], [1, '#dc2626']],
            colorbar=dict(title="Tasa de<br>Mortalidad (%)", titleside="right"),
            text=heatmap_data.values.round(0),
            texttemplate='%{text}%',
            textfont={"size": 10},
            hovertemplate='<b>%{x} - %{y}</b><br>Mortalidad: %{z:.1f}%<extra></extra>'
        ))
        
        fig_heatmap.update_layout(
            title="Intensidad de Mortalidad por Mes y Año (Rojo = Mayor Mortalidad)",
            xaxis_title="Año",
            yaxis_title="Mes",
            height=500,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#cbd5e1')
        )
        
        st.plotly_chart(fig_heatmap, use_container_width=True)
        
        # Insights
        worst_month = monthly_stats.loc[monthly_stats['Mortalidad'].idxmax()]
        st.markdown(f"""
        <div class="insight-box">
            <h4>💡 Insights del Mapa de Calor</h4>
            <ul>
                <li>Peor mes: <strong>{worst_month['month']}/{worst_month['year']}</strong> con {worst_month['Mortalidad']:.0f}% mortalidad</li>
                <li>Período crítico: <strong>2009-2015</strong> muestra consistentemente alta mortalidad</li>
                <li>Patrón estacional: Mayor mortalidad en meses de cierre fiscal</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with tab2:
        # Temporal evolution with multiple metrics
        st.markdown("### 📊 Evolución Temporal Multi-métrica")
        
        # Create subplots
        fig_temporal = make_subplots(
            rows=3, cols=1,
            subplot_titles=('Nacimientos vs Muertes', 'Tasa de Mortalidad (%)', 'Balance Acumulado'),
            vertical_spacing=0.1,
            row_heights=[0.4, 0.3, 0.3]
        )
        
        # Plot 1: Births vs Deaths
        fig_temporal.add_trace(
            go.Bar(x=yearly_stats['year'], y=yearly_stats['Altas'],
                   name='Nacimientos', marker_color='#10b981'),
            row=1, col=1
        )
        fig_temporal.add_trace(
            go.Bar(x=yearly_stats['year'], y=-yearly_stats['Bajas'],
                   name='Muertes', marker_color='#dc2626'),
            row=1, col=1
        )
        
        # Plot 2: Mortality Rate
        fig_temporal.add_trace(
            go.Scatter(x=yearly_stats['year'], y=yearly_stats['Tasa_Mortalidad'],
                      mode='lines+markers', name='Tasa Mortalidad',
                      line=dict(color='#f59e0b', width=3),
                      marker=dict(size=8)),
            row=2, col=1
        )
        fig_temporal.add_hline(y=100, line_dash="dash", line_color="#ef4444", 
                               annotation_text="100% = Equilibrio", row=2, col=1)
        
        # Plot 3: Cumulative Balance
        yearly_stats['Acumulado'] = yearly_stats['Cambio_Neto'].cumsum()
        fig_temporal.add_trace(
            go.Scatter(x=yearly_stats['year'], y=yearly_stats['Acumulado'],
                      mode='lines+markers', fill='tozeroy',
                      name='Balance Acumulado',
                      line=dict(color='#dc2626', width=3),
                      fillcolor='rgba(220, 38, 38, 0.2)'),
            row=3, col=1
        )
        
        fig_temporal.update_layout(
            height=800,
            showlegend=True,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#cbd5e1'),
            hovermode='x unified'
        )
        
        fig_temporal.update_xaxes(gridcolor='#334155', showgrid=False)
        fig_temporal.update_yaxes(gridcolor='#334155', showgrid=True)
        
        st.plotly_chart(fig_temporal, use_container_width=True)
    
    with tab3:
        # Management companies analysis
        st.markdown("### 🏢 Análisis por Gestoras")
        
        # Get births and deaths by gestora
        births_by_gestora = births.dropna(subset=['Gestora']).groupby('Gestora').size()
        deaths_by_gestora = deaths.dropna(subset=['Gestora']).groupby('Gestora').size()
        
        # Merge and calculate metrics
        gestora_stats = pd.DataFrame({
            'Altas': births_by_gestora,
            'Bajas': deaths_by_gestora
        }).fillna(0)
        
        gestora_stats['Total'] = gestora_stats['Altas'] + gestora_stats['Bajas']
        gestora_stats['Tasa_Mortalidad'] = (gestora_stats['Bajas'] / gestora_stats['Altas'] * 100).fillna(0)
        gestora_stats['Balance'] = gestora_stats['Altas'] - gestora_stats['Bajas']
        
        # Filter top gestoras by activity
        top_gestoras = gestora_stats.nlargest(20, 'Total')
        
        # Create bubble chart
        fig_bubble = go.Figure()
        
        fig_bubble.add_trace(go.Scatter(
            x=top_gestoras['Altas'],
            y=top_gestoras['Bajas'],
            mode='markers+text',
            marker=dict(
                size=top_gestoras['Total'] / 2,
                color=top_gestoras['Tasa_Mortalidad'],
                colorscale='RdYlGn_r',
                showscale=True,
                colorbar=dict(title="Mortalidad %"),
                line=dict(width=1, color='#334155')
            ),
            text=top_gestoras.index.str[:20],
            textposition="top center",
            hovertemplate='<b>%{text}</b><br>Altas: %{x}<br>Bajas: %{y}<br>Mortalidad: %{marker.color:.1f}%<extra></extra>'
        ))
        
        # Add diagonal line (equal births and deaths)
        max_val = max(top_gestoras['Altas'].max(), top_gestoras['Bajas'].max())
        fig_bubble.add_trace(go.Scatter(
            x=[0, max_val],
            y=[0, max_val],
            mode='lines',
            line=dict(color='#ef4444', width=2, dash='dash'),
            name='Línea de equilibrio',
            showlegend=True
        ))
        
        fig_bubble.update_layout(
            title="Gestoras: Nacimientos vs Muertes (Tamaño = Actividad Total)",
            xaxis_title="Fondos Creados",
            yaxis_title="Fondos Liquidados",
            height=600,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#cbd5e1')
        )
        
        fig_bubble.update_xaxes(gridcolor='#334155', showgrid=True)
        fig_bubble.update_yaxes(gridcolor='#334155', showgrid=True)
        
        st.plotly_chart(fig_bubble, use_container_width=True)
        
        # Worst performers table
        st.markdown("#### 💀 Gestoras con Mayor Mortalidad")
        worst_gestoras = gestora_stats[gestora_stats['Altas'] >= 10].nlargest(10, 'Tasa_Mortalidad')
        worst_display = worst_gestoras[['Altas', 'Bajas', 'Tasa_Mortalidad', 'Balance']].round(1)
        
        st.dataframe(
            worst_display,
            use_container_width=True,
            column_config={
                "Altas": st.column_config.NumberColumn("Altas", format="%d"),
                "Bajas": st.column_config.NumberColumn("Bajas", format="%d"),
                "Tasa_Mortalidad": st.column_config.NumberColumn("Mortalidad %", format="%.1f%%"),
                "Balance": st.column_config.NumberColumn("Balance", format="%d")
            }
        )
    
    with tab4:
        # Fund search and lifecycle
        st.markdown("### 🔬 Búsqueda y Ciclo de Vida de Fondos")
        
        # Search interface
        col1, col2 = st.columns([2, 1])
        with col1:
            search_term = st.text_input(
                "Buscar fondo",
                placeholder="Nombre o número de registro...",
                key="fund_search"
            )
        with col2:
            fund_status = st.selectbox(
                "Estado",
                ["Todos", "Activos", "Liquidados"],
                key="fund_status"
            )
        
        if search_term or fund_status != "Todos":
            # Create lifecycle dataframe
            births_search = births[births['N_Registro'].notna()].copy()
            deaths_search = deaths[deaths['N_Registro'].notna()].copy()
            
            # Get unique funds with birth dates
            fund_births = births_search.groupby('N_Registro').agg({
                'Nombre': 'first',
                'date': 'min',
                'Gestora': 'first'
            }).rename(columns={'date': 'Fecha_Alta'})
            
            # Get death dates
            fund_deaths = deaths_search.groupby('N_Registro')['date'].min().rename('Fecha_Baja')
            
            # Merge
            fund_lifecycle = fund_births.merge(fund_deaths, left_index=True, right_index=True, how='left')
            fund_lifecycle['Vida_Anos'] = ((fund_lifecycle['Fecha_Baja'] - fund_lifecycle['Fecha_Alta']).dt.days / 365.25).round(1)
            fund_lifecycle['Estado'] = fund_lifecycle['Fecha_Baja'].apply(lambda x: '💀 Liquidado' if pd.notna(x) else '✅ Activo')
            
            # Apply filters
            if search_term:
                mask = (
                    fund_lifecycle['Nombre'].str.contains(search_term.upper(), case=False, na=False) |
                    fund_lifecycle.index.astype(str).str.contains(search_term)
                )
                fund_lifecycle = fund_lifecycle[mask]
            
            if fund_status == "Activos":
                fund_lifecycle = fund_lifecycle[fund_lifecycle['Estado'] == '✅ Activo']
            elif fund_status == "Liquidados":
                fund_lifecycle = fund_lifecycle[fund_lifecycle['Estado'] == '💀 Liquidado']
            
            # Display results
            if len(fund_lifecycle) > 0:
                st.markdown(f"**Encontrados: {len(fund_lifecycle)} fondos**")
                
                display_lifecycle = fund_lifecycle.reset_index()[['N_Registro', 'Nombre', 'Fecha_Alta', 'Fecha_Baja', 'Vida_Anos', 'Estado', 'Gestora']]
                display_lifecycle['Fecha_Alta'] = display_lifecycle['Fecha_Alta'].dt.strftime('%Y-%m-%d')
                display_lifecycle['Fecha_Baja'] = display_lifecycle['Fecha_Baja'].dt.strftime('%Y-%m-%d')
                
                st.dataframe(
                    display_lifecycle,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "N_Registro": st.column_config.NumberColumn("Nº Registro", format="%d"),
                        "Nombre": st.column_config.TextColumn("Nombre del Fondo"),
                        "Fecha_Alta": st.column_config.TextColumn("Alta"),
                        "Fecha_Baja": st.column_config.TextColumn("Baja"),
                        "Vida_Anos": st.column_config.NumberColumn("Vida (años)", format="%.1f"),
                        "Estado": st.column_config.TextColumn("Estado"),
                        "Gestora": st.column_config.TextColumn("Gestora")
                    }
                )
            else:
                st.info("No se encontraron fondos con los criterios especificados")

else:  # Analysis mode
    st.markdown("## 📊 Análisis Detallado")
    
    # Complete statistics
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📈 Estadísticas del Período")
        st.markdown(f"""
        <div class="insight-box">
            <h4>Métricas Clave</h4>
            <ul style="line-height: 2;">
                <li>📅 Período: <strong>{period_label}</strong></li>
                <li>🌱 Total Altas: <strong>{total_births:,}</strong></li>
                <li>💀 Total Bajas: <strong>{total_deaths:,}</strong></li>
                <li>📉 Balance Neto: <strong>{net_change:+,}</strong></li>
                <li>☠️ Tasa de Mortalidad: <strong>{mortality_rate:.1f}%</strong></li>
                <li>📊 Promedio Anual de Bajas: <strong>{total_deaths/(end_year-start_year+1):.0f}</strong></li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("### ⚠️ Implicaciones del Sesgo")
        st.markdown(f"""
        <div class="insight-box">
            <h4>Impacto en Inversores</h4>
            <ul style="line-height: 2;">
                <li>📊 Rentabilidades históricas <strong>sobrestimadas</strong></li>
                <li>🎯 Riesgo real <strong>subestimado</strong></li>
                <li>📈 Supervivencia ≠ Calidad</li>
                <li>💰 Costes ocultos de liquidación</li>
                <li>🔄 Necesidad de diversificación</li>
                <li>📉 Preferir inversión pasiva/indexada</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # Detailed yearly table
    st.markdown("### 📋 Datos Anuales Detallados")
    
    yearly_detailed = []
    for year in range(start_year, end_year + 1):
        year_births = len(df[(df['year'] == year) & (df['status'] == 'NUEVAS_INSCRIPCIONES')])
        year_deaths = len(df[(df['year'] == year) & (df['status'] == 'BAJAS')])
        year_net = year_births - year_deaths
        year_mortality = (year_deaths / year_births * 100) if year_births > 0 else 0
        
        yearly_detailed.append({
            'Año': year,
            'Altas': year_births,
            'Bajas': year_deaths,
            'Balance': year_net,
            'Mortalidad %': year_mortality
        })
    
    yearly_detailed_df = pd.DataFrame(yearly_detailed)
    
    # Style the dataframe
    def style_negative(val):
        if isinstance(val, (int, float)) and val < 0:
            return 'color: #ef4444'
        return ''
    
    styled_df = yearly_detailed_df.style.applymap(style_negative, subset=['Balance'])
    
    st.dataframe(
        yearly_detailed_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Año": st.column_config.NumberColumn("Año", format="%d"),
            "Altas": st.column_config.NumberColumn("Altas", format="%d"),
            "Bajas": st.column_config.NumberColumn("Bajas", format="%d"),
            "Balance": st.column_config.NumberColumn("Balance", format="%d"),
            "Mortalidad %": st.column_config.NumberColumn("Mortalidad %", format="%.1f%%")
        }
    )
    
    # Cohort analysis
    st.markdown("### 🎯 Análisis de Cohortes")
    
    # Select cohort year
    cohort_year = st.selectbox(
        "Seleccionar año de nacimiento de la cohorte",
        options=list(range(2004, 2020)),
        index=0
    )
    
    # Get cohort funds
    cohort = df[(df['year'] == cohort_year) & (df['status'] == 'NUEVAS_INSCRIPCIONES')]
    cohort_ids = cohort['N_Registro'].dropna().unique()
    
    # Track survival over time
    survival_tracking = []
    for year in range(cohort_year, 2025):
        dead_by_year = df[(df['status'] == 'BAJAS') & 
                          (df['N_Registro'].isin(cohort_ids)) & 
                          (df['year'] <= year)]
        
        dead_count = len(dead_by_year['N_Registro'].unique())
        alive_count = len(cohort_ids) - dead_count
        survival_rate = (alive_count / len(cohort_ids) * 100) if len(cohort_ids) > 0 else 0
        
        survival_tracking.append({
            'Año': year,
            'Años_Transcurridos': year - cohort_year,
            'Vivos': alive_count,
            'Muertos': dead_count,
            'Tasa_Supervivencia': survival_rate
        })
    
    survival_tracking_df = pd.DataFrame(survival_tracking)
    
    # Plot survival curve
    fig_survival = go.Figure()
    
    fig_survival.add_trace(go.Scatter(
        x=survival_tracking_df['Años_Transcurridos'],
        y=survival_tracking_df['Tasa_Supervivencia'],
        mode='lines+markers',
        line=dict(color='#10b981', width=3),
        marker=dict(size=8),
        fill='tozeroy',
        fillcolor='rgba(16, 185, 129, 0.2)',
        name=f'Cohorte {cohort_year}',
        hovertemplate='<b>Año %{x} desde nacimiento</b><br>Supervivencia: %{y:.1f}%<extra></extra>'
    ))
    
    fig_survival.add_hline(y=50, line_dash="dash", line_color="#f59e0b",
                          annotation_text="50% supervivencia")
    
    fig_survival.update_layout(
        title=f"Curva de Supervivencia - Fondos Nacidos en {cohort_year}",
        xaxis_title="Años desde Nacimiento",
        yaxis_title="Tasa de Supervivencia (%)",
        height=400,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#cbd5e1'),
        showlegend=True
    )
    
    fig_survival.update_xaxes(gridcolor='#334155', showgrid=True)
    fig_survival.update_yaxes(gridcolor='#334155', showgrid=True, range=[0, 105])
    
    st.plotly_chart(fig_survival, use_container_width=True)
    
    # Cohort statistics
    if len(survival_tracking_df) > 0:
        final_survival = survival_tracking_df.iloc[-1]['Tasa_Supervivencia']
        half_life = survival_tracking_df[survival_tracking_df['Tasa_Supervivencia'] <= 50]
        half_life_years = half_life.iloc[0]['Años_Transcurridos'] if len(half_life) > 0 else "N/A"
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(f"Nacidos en {cohort_year}", f"{len(cohort_ids)} fondos")
        with col2:
            st.metric("Supervivencia Actual", f"{final_survival:.1f}%")
        with col3:
            st.metric("Vida Media (50% muertos)", f"{half_life_years} años" if half_life_years != "N/A" else "N/A")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #64748b; padding: 1.5rem 0; font-size: 13px;">
    <p><strong>El Cementerio de Fondos Españoles</strong></p>
    <p>Análisis del Sesgo de Supervivencia en la Industria de Fondos de Inversión</p>
    <p>Datos: CNMV (Comisión Nacional del Mercado de Valores) | Período: 2004-2025</p>
    <p>Por <a href="https://twitter.com/Gsnchez" target="_blank" style="color: #60a5fa;">@Gsnchez</a> | 
    <a href="https://bquantfinance.com" target="_blank" style="color: #60a5fa;">bquantfinance.com</a></p>
    <p style="margin-top: 1rem; font-size: 11px;">
    ⚠️ Este análisis demuestra el impacto del sesgo de supervivencia en las métricas de rentabilidad publicadas.
    Los fondos liquidados desaparecen de las estadísticas, inflando artificialmente los rendimientos históricos.
    </p>
</div>
""", unsafe_allow_html=True)
