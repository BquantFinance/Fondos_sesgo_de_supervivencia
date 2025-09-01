import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np
import re

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
    
    /* Metrics styling */
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
    
    /* Headers */
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
    
    .summary-box {
        background: #1a1f2e;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        border: 1px solid #334155;
    }
    
    /* Tables */
    .dataframe {
        font-size: 13px;
    }
    
    /* Sidebar */
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
    
    # Extract date from filename
    def extract_date_from_filename(filename):
        match = re.search(r'(\d{2})-(\d{2})-(\d{4})_al_(\d{2})-(\d{2})-(\d{4})', filename)
        if match:
            # Use end date of bulletin period
            end_date = pd.to_datetime(f"{match.group(6)}-{match.group(5)}-{match.group(4)}", format='%Y-%m-%d')
            return end_date
        return None
    
    # Add date columns
    df['date'] = df['file'].apply(extract_date_from_filename)
    df = df.dropna(subset=['date'])
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month
    df['year_month'] = df['date'].dt.to_period('M')
    df['month_name'] = df['date'].dt.strftime('%B')
    
    # Translate status for better readability
    df['status_esp'] = df['status'].map({
        'NUEVAS_INSCRIPCIONES': 'Altas',
        'BAJAS': 'Bajas'
    })
    
    return df

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

# Year filter with "Todos los años" option
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

# Month filter with "Todos los meses" option
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
show_monthly_detail = st.sidebar.checkbox("Mostrar detalle mensual", value=True)
show_gestoras = st.sidebar.checkbox("Mostrar análisis por gestoras", value=True)
show_raw_data = st.sidebar.checkbox("Mostrar datos brutos", value=False)

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

# Important note about mortality rate
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

# Tabs for different views
tab1, tab2, tab3 = st.tabs(["📈 **Análisis Temporal**", "📋 **Tabla Detallada**", "🏢 **Análisis por Gestoras**"])

with tab1:
    # Historical Evolution Chart
    st.markdown("### Evolución Histórica de Altas y Bajas")
    
    fig1 = go.Figure()
    
    # Add births
    fig1.add_trace(go.Bar(
        x=yearly_stats['year'],
        y=yearly_stats['Altas'],
        name='Altas',
        marker_color='#22c55e',
        text=yearly_stats['Altas'],
        textposition='outside',
        hovertemplate='<b>%{x}</b><br>Altas: %{y}<extra></extra>'
    ))
    
    # Add deaths
    fig1.add_trace(go.Bar(
        x=yearly_stats['year'],
        y=-yearly_stats['Bajas'],
        name='Bajas',
        marker_color='#dc2626',
        text=yearly_stats['Bajas'],
        textposition='outside',
        hovertemplate='<b>%{x}</b><br>Bajas: %{y}<extra></extra>'
    ))
    
    # Add net change line
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
    
    # Mortality Rate Evolution
    st.markdown("### Evolución de la Tasa de Mortalidad Anual")
    
    fig2 = go.Figure()
    
    # Prepare colors based on rate
    colors = ['#dc2626' if rate > 100 else '#f59e0b' if rate > 50 else '#22c55e' 
              for rate in yearly_stats['Tasa_Mortalidad']]
    
    fig2.add_trace(go.Bar(
        x=yearly_stats['year'],
        y=yearly_stats['Tasa_Mortalidad'],
        marker_color=colors,
        text=[f"{rate:.0f}%" for rate in yearly_stats['Tasa_Mortalidad']],
        textposition='outside',
        hovertemplate='<b>%{x}</b><br>Tasa de Mortalidad: %{y:.1f}%<extra></extra>'
    ))
    
    fig2.add_hline(y=100, line_color="#dc2626", line_width=1.5, line_dash="dash",
                   annotation_text="100% (Equilibrio)")
    
    fig2.update_layout(
        xaxis_title="Año",
        yaxis_title="Tasa de Mortalidad (%)",
        height=350,
        plot_bgcolor='#1a1f2e',
        paper_bgcolor='#0e1117',
        font=dict(color='#cbd5e1', size=12),
        showlegend=False
    )
    
    fig2.update_xaxes(gridcolor='#334155', showgrid=False)
    fig2.update_yaxes(gridcolor='#334155', showgrid=True)
    
    st.plotly_chart(fig2, use_container_width=True)
    
    # Cumulative Impact
    st.markdown("### Impacto Acumulado")
    
    yearly_stats['Cumulative_Net'] = yearly_stats['Cambio_Neto'].cumsum()
    
    fig3 = go.Figure()
    
    fig3.add_trace(go.Scatter(
        x=yearly_stats['year'],
        y=yearly_stats['Cumulative_Net'],
        mode='lines+markers',
        fill='tozeroy',
        fillcolor='rgba(220, 38, 38, 0.1)',
        line=dict(color='#dc2626', width=2.5),
        marker=dict(size=7),
        hovertemplate='<b>%{x}</b><br>Balance Acumulado: %{y:,}<extra></extra>'
    ))
    
    fig3.add_hline(y=0, line_color="#64748b", line_width=1, line_dash="dash")
    
    fig3.update_layout(
        xaxis_title="Año",
        yaxis_title="Cambio Neto Acumulado",
        height=350,
        plot_bgcolor='#1a1f2e',
        paper_bgcolor='#0e1117',
        font=dict(color='#cbd5e1', size=12),
        showlegend=False
    )
    
    fig3.update_xaxes(gridcolor='#334155', showgrid=False)
    fig3.update_yaxes(gridcolor='#334155', showgrid=True)
    
    st.plotly_chart(fig3, use_container_width=True)

with tab2:
    st.markdown("### Tabla Detallada de Altas y Bajas")
    
    # Create detailed table
    if show_monthly_detail:
        # Monthly detail
        monthly_data = df.groupby(['year', 'month', 'status']).size().unstack(fill_value=0)
        monthly_data = monthly_data.rename(columns={
            'NUEVAS_INSCRIPCIONES': 'Altas',
            'BAJAS': 'Bajas'
        })
        monthly_data['Cambio_Neto'] = monthly_data['Altas'] - monthly_data['Bajas']
        monthly_data['Tasa_Mortalidad_%'] = (monthly_data['Bajas'] / monthly_data['Altas'] * 100).fillna(0).round(1)
        monthly_data = monthly_data.reset_index()
        
        # Add month names
        month_names_dict = {
            1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril',
            5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
            9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
        }
        monthly_data['Mes'] = monthly_data['month'].map(month_names_dict)
        monthly_data['Año'] = monthly_data['year']
        
        # Apply year filter
        monthly_data = monthly_data[monthly_data['year'].isin(selected_years)]
        
        # Store month number for sorting before reordering columns
        monthly_data['month_num'] = monthly_data['month']
        
        # Reorder columns for display
        display_monthly = monthly_data[['Año', 'Mes', 'Altas', 'Bajas', 'Cambio_Neto', 'Tasa_Mortalidad_%', 'month_num']].copy()
        
        # Display summary by year
        st.markdown("#### Resumen Anual")
        yearly_summary = display_monthly.groupby('Año').agg({
            'Altas': 'sum',
            'Bajas': 'sum',
            'Cambio_Neto': 'sum'
        }).reset_index()
        yearly_summary['Tasa_Mortalidad_%'] = (yearly_summary['Bajas'] / yearly_summary['Altas'] * 100).fillna(0).round(1)
        
        st.dataframe(
            yearly_summary,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Año": st.column_config.NumberColumn("Año", format="%d"),
                "Altas": st.column_config.NumberColumn("Altas", format="%d"),
                "Bajas": st.column_config.NumberColumn("Bajas", format="%d"),
                "Cambio_Neto": st.column_config.NumberColumn("Cambio Neto", format="%d"),
                "Tasa_Mortalidad_%": st.column_config.NumberColumn("Tasa Mortalidad (%)", format="%.1f")
            }
        )
        
        # Display monthly detail
        st.markdown("#### Detalle Mensual")
        
        # Sort by year (descending) and month (ascending)
        display_monthly = display_monthly.sort_values(['Año', 'month_num'], ascending=[False, True])
        # Remove the month_num column before displaying
        display_monthly = display_monthly.drop('month_num', axis=1)
        
        st.dataframe(
            display_monthly,
            use_container_width=True,
            height=600,
            hide_index=True,
            column_config={
                "Año": st.column_config.NumberColumn("Año", format="%d"),
                "Mes": st.column_config.TextColumn("Mes"),
                "Altas": st.column_config.NumberColumn("Altas", format="%d"),
                "Bajas": st.column_config.NumberColumn("Bajas", format="%d"),
                "Cambio_Neto": st.column_config.NumberColumn("Cambio Neto", format="%d"),
                "Tasa_Mortalidad_%": st.column_config.NumberColumn("Tasa Mortalidad (%)", format="%.1f")
            }
        )
        
        # Download button for the data
        csv = display_monthly.to_csv(index=False)
        st.download_button(
            label="📥 Descargar datos en CSV",
            data=csv,
            file_name='fondos_cnmv_detalle.csv',
            mime='text/csv',
        )
    else:
        # Yearly summary only
        st.dataframe(
            yearly_stats[['year', 'Altas', 'Bajas', 'Cambio_Neto', 'Tasa_Mortalidad']].rename(
                columns={'year': 'Año', 'Tasa_Mortalidad': 'Tasa_Mortalidad_%'}
            ),
            use_container_width=True,
            hide_index=True,
            column_config={
                "Año": st.column_config.NumberColumn("Año", format="%d"),
                "Altas": st.column_config.NumberColumn("Altas", format="%d"),
                "Bajas": st.column_config.NumberColumn("Bajas", format="%d"),
                "Cambio_Neto": st.column_config.NumberColumn("Cambio Neto", format="%d"),
                "Tasa_Mortalidad_%": st.column_config.NumberColumn("Tasa Mortalidad (%)", format="%.1f")
            }
        )

with tab3:
    if show_gestoras:
        st.markdown("### Top Gestoras por Número de Fondos Registrados")
        
        # Analysis by management company (births)
        births_by_gestora = births.dropna(subset=['Gestora']).groupby('Gestora').size().reset_index(name='Altas')
        top_gestoras_births = births_by_gestora.nlargest(20, 'Altas')
        
        fig4 = go.Figure()
        
        fig4.add_trace(go.Bar(
            y=top_gestoras_births['Gestora'][::-1],
            x=top_gestoras_births['Altas'][::-1],
            orientation='h',
            marker_color='#4338ca',
            text=top_gestoras_births['Altas'][::-1],
            textposition='outside',
            hovertemplate='<b>%{y}</b><br>Fondos Registrados: %{x}<extra></extra>'
        ))
        
        fig4.update_layout(
            xaxis_title="Número de Fondos Registrados",
            yaxis_title="",
            height=600,
            plot_bgcolor='#1a1f2e',
            paper_bgcolor='#0e1117',
            font=dict(color='#cbd5e1', size=11),
            showlegend=False,
            margin=dict(l=350)
        )
        
        fig4.update_xaxes(gridcolor='#334155', showgrid=True)
        fig4.update_yaxes(gridcolor='#334155', showgrid=False, tickfont=dict(size=10))
        
        st.plotly_chart(fig4, use_container_width=True)
        
        # Table with gestoras data
        st.markdown("#### Detalle de Gestoras")
        
        gestora_summary = births_by_gestora.merge(
            deaths.dropna(subset=['Gestora']).groupby('Gestora').size().reset_index(name='Bajas'),
            on='Gestora',
            how='outer'
        ).fillna(0)
        
        gestora_summary['Balance'] = gestora_summary['Altas'] - gestora_summary['Bajas']
        gestora_summary['Tasa_Supervivencia_%'] = ((gestora_summary['Altas'] - gestora_summary['Bajas']) / gestora_summary['Altas'] * 100).fillna(0).round(1)
        gestora_summary = gestora_summary.sort_values('Altas', ascending=False).head(30)
        
        st.dataframe(
            gestora_summary,
            use_container_width=True,
            height=400,
            hide_index=True,
            column_config={
                "Gestora": st.column_config.TextColumn("Gestora", width="large"),
                "Altas": st.column_config.NumberColumn("Altas", format="%d"),
                "Bajas": st.column_config.NumberColumn("Bajas", format="%d"),
                "Balance": st.column_config.NumberColumn("Balance", format="%d"),
                "Tasa_Supervivencia_%": st.column_config.NumberColumn("Tasa Supervivencia (%)", format="%.1f")
            }
        )

# Show raw data if selected
if show_raw_data:
    st.markdown("---")
    st.markdown("## 📋 Datos Brutos")
    
    display_df = filtered_df[['date', 'year', 'month', 'status_esp', 'Nombre', 'N_Registro', 'Gestora', 'Depositaria']].copy()
    display_df['date'] = display_df['date'].dt.strftime('%Y-%m-%d')
    display_df = display_df.rename(columns={
        'date': 'Fecha',
        'year': 'Año',
        'month': 'Mes',
        'status_esp': 'Tipo',
        'N_Registro': 'Nº Registro'
    })
    
    st.dataframe(
        display_df,
        use_container_width=True,
        height=600,
        hide_index=True
    )

# Key insights section
st.markdown("---")
st.markdown("## 💡 Implicaciones del Sesgo de Supervivencia")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="info-box">
        <h4>📊 Impacto en el Análisis de Rentabilidad</h4>
        <ul style="line-height: 1.8; font-size: 14px;">
            <li>Los fondos con mal desempeño desaparecen de las bases de datos</li>
            <li>Las rentabilidades históricas promedio están sobrestimadas</li>
            <li>El riesgo real de la inversión en fondos está subestimado</li>
            <li>Los análisis de persistencia de rentabilidad están sesgados</li>
            <li>La comparación con índices de referencia no es equitativa</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="info-box">
        <h4>🎯 Consideraciones para el Inversor</h4>
        <ul style="line-height: 1.8; font-size: 14px;">
            <li>Evaluar con escepticismo las rentabilidades históricas publicadas</li>
            <li>Considerar el sesgo al analizar track records de gestoras</li>
            <li>Preferir análisis que incluyan fondos liquidados</li>
            <li>Valorar estrategias de inversión pasiva e indexada</li>
            <li>Diversificar para mitigar el riesgo de selección adversa</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# Period analysis
st.markdown("### 📈 Análisis por Períodos")

periods = {
    "Pre-Crisis (2004-2008)": (2004, 2008),
    "Crisis Financiera (2009-2015)": (2009, 2015),
    "Recuperación (2016-2019)": (2016, 2019),
    "Pandemia y Post (2020-2025)": (2020, 2025)
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
            'Cambio Neto': net_change_period,
            'Tasa Mortalidad (%)': f"{mortality_rate_period:.1f}"
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
        "Cambio Neto": st.column_config.NumberColumn("Cambio Neto", format="%d"),
        "Tasa Mortalidad (%)": st.column_config.TextColumn("Tasa Mortalidad (%)")
    }
)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #64748b; padding: 1.5rem 0; font-size: 14px;">
    <p><strong>Análisis del Sesgo de Supervivencia en Fondos de Inversión Españoles</strong></p>
    <p>Datos: CNMV (Comisión Nacional del Mercado de Valores) | Período: 2004-2025</p>
    <p>Desarrollado por <a href="https://twitter.com/Gsnchez" target="_blank" style="color: #4338ca;">@Gsnchez</a> | 
    <a href="https://bquantfinance.com" target="_blank" style="color: #4338ca;">bquantfinance.com</a></p>
    <p style="font-size: 12px; margin-top: 1rem;">
    Nota: Este análisis demuestra la importancia del sesgo de supervivencia en la evaluación de fondos de inversión. 
    Los datos históricos que excluyen fondos liquidados pueden sobrestimar significativamente las rentabilidades esperadas.
    </p>
</div>
""", unsafe_allow_html=True)
