import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np
import re

# Page configuration
st.set_page_config(
    page_title="Análisis Sesgo de Supervivencia",
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
tab1, tab2, tab3, tab4 = st.tabs(["📈 **Análisis Temporal**", "📋 **Datos Transaccionales**", "🏢 **Análisis por Gestoras**", "🔍 **Búsqueda de Fondos**"])

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
    st.markdown("### 📋 Datos Transaccionales de Fondos")
    
    # Combine births and deaths into a single transactional view
    # Prepare births data
    births_trans = births[['date', 'Nombre', 'N_Registro', 'Gestora', 'Depositaria']].copy()
    births_trans['Tipo_Operacion'] = '🌱 Alta'
    births_trans['Color_Tag'] = 'success'
    
    # Prepare deaths data
    deaths_trans = deaths[['date', 'Nombre', 'N_Registro', 'Gestora', 'Depositaria']].copy()
    deaths_trans['Tipo_Operacion'] = '💀 Baja'
    deaths_trans['Color_Tag'] = 'danger'
    
    # Combine both
    transactions_df = pd.concat([births_trans, deaths_trans], ignore_index=True)
    transactions_df = transactions_df.sort_values('date', ascending=False)
    
    # Add year and month for filtering
    transactions_df['year'] = transactions_df['date'].dt.year
    transactions_df['month'] = transactions_df['date'].dt.month
    transactions_df['month_name'] = transactions_df['date'].dt.strftime('%B')
    
    # Apply filters from sidebar
    filtered_trans = transactions_df[transactions_df['year'].isin(selected_years)]
    
    # Apply month filter
    reverse_months_esp = {
        'Enero': 'January', 'Febrero': 'February', 'Marzo': 'March', 'Abril': 'April',
        'Mayo': 'May', 'Junio': 'June', 'Julio': 'July', 'Agosto': 'August',
        'Septiembre': 'September', 'Octubre': 'October', 'Noviembre': 'November', 'Diciembre': 'December'
    }
    selected_months_eng_trans = [reverse_months_esp.get(m, m) for m in selected_months]
    filtered_trans = filtered_trans[filtered_trans['month_name'].isin(selected_months_eng_trans)]
    
    # Apply status filter
    if status_filter == 'Solo Altas':
        filtered_trans = filtered_trans[filtered_trans['Tipo_Operacion'] == '🌱 Alta']
    elif status_filter == 'Solo Bajas':
        filtered_trans = filtered_trans[filtered_trans['Tipo_Operacion'] == '💀 Baja']
    
    # Additional filters for transactional data
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        search_trans = st.text_input(
            "🔍 Buscar en transacciones",
            placeholder="Nombre del fondo, gestora o nº registro...",
            key="search_trans"
        )
    
    with col2:
        # Date range selector
        date_range = st.selectbox(
            "Período",
            options=['Todo', 'Último mes', 'Últimos 3 meses', 'Último año', 'Últimos 5 años'],
            index=0,
            key="date_range_trans"
        )
    
    with col3:
        # Sort order
        sort_order = st.selectbox(
            "Ordenar por",
            options=['Fecha (más reciente)', 'Fecha (más antiguo)', 'Nombre A-Z', 'Nombre Z-A'],
            index=0,
            key="sort_trans"
        )
    
    # Apply search filter
    if search_trans:
        mask = (
            filtered_trans['Nombre'].str.contains(search_trans.upper(), case=False, na=False) |
            filtered_trans['Gestora'].str.contains(search_trans.upper(), case=False, na=False) |
            filtered_trans['N_Registro'].astype(str).str.contains(search_trans, na=False)
        )
        filtered_trans = filtered_trans[mask]
    
    # Apply date range filter
    if date_range != 'Todo':
        from datetime import datetime, timedelta
        today = datetime.now()
        if date_range == 'Último mes':
            cutoff_date = today - timedelta(days=30)
        elif date_range == 'Últimos 3 meses':
            cutoff_date = today - timedelta(days=90)
        elif date_range == 'Último año':
            cutoff_date = today - timedelta(days=365)
        elif date_range == 'Últimos 5 años':
            cutoff_date = today - timedelta(days=1825)
        
        filtered_trans = filtered_trans[filtered_trans['date'] >= cutoff_date]
    
    # Apply sorting
    if sort_order == 'Fecha (más reciente)':
        filtered_trans = filtered_trans.sort_values('date', ascending=False)
    elif sort_order == 'Fecha (más antiguo)':
        filtered_trans = filtered_trans.sort_values('date', ascending=True)
    elif sort_order == 'Nombre A-Z':
        filtered_trans = filtered_trans.sort_values('Nombre', ascending=True)
    elif sort_order == 'Nombre Z-A':
        filtered_trans = filtered_trans.sort_values('Nombre', ascending=False)
    
    # Display summary statistics
    col1, col2, col3, col4 = st.columns(4)
    
    total_transactions = len(filtered_trans)
    total_altas = len(filtered_trans[filtered_trans['Tipo_Operacion'] == '🌱 Alta'])
    total_bajas = len(filtered_trans[filtered_trans['Tipo_Operacion'] == '💀 Baja'])
    
    with col1:
        st.metric("Total Transacciones", f"{total_transactions:,}")
    
    with col2:
        st.metric("Altas", f"{total_altas:,}",
                  delta=f"{(total_altas/total_transactions*100):.1f}%" if total_transactions > 0 else "0%")
    
    with col3:
        st.metric("Bajas", f"{total_bajas:,}",
                  delta=f"{(total_bajas/total_transactions*100):.1f}%" if total_transactions > 0 else "0%")
    
    with col4:
        balance_trans = total_altas - total_bajas
        st.metric("Balance", f"{balance_trans:+,}",
                  delta="Positivo" if balance_trans > 0 else "Negativo" if balance_trans < 0 else "Neutro")
    
    # Display transactional data
    st.markdown("#### Detalle de Transacciones")
    
    if len(filtered_trans) > 0:
        # Prepare display dataframe
        display_trans = filtered_trans[['date', 'Tipo_Operacion', 'Nombre', 'N_Registro', 'Gestora', 'Depositaria']].copy()
        display_trans['date'] = display_trans['date'].dt.strftime('%Y-%m-%d')
        display_trans = display_trans.rename(columns={
            'date': 'Fecha',
            'Tipo_Operacion': 'Operación',
            'N_Registro': 'Nº Registro'
        })
        
        # Clean N_Registro column (remove NaN and convert to int where possible)
        display_trans['Nº Registro'] = display_trans['Nº Registro'].apply(
            lambda x: int(x) if pd.notna(x) else ''
        )
        
        st.dataframe(
            display_trans,
            use_container_width=True,
            height=600,
            hide_index=True,
            column_config={
                "Fecha": st.column_config.TextColumn("Fecha", width="small"),
                "Operación": st.column_config.TextColumn("Operación", width="small"),
                "Nombre": st.column_config.TextColumn("Nombre del Fondo", width="large"),
                "Nº Registro": st.column_config.TextColumn("Nº Registro", width="small"),
                "Gestora": st.column_config.TextColumn("Gestora", width="medium"),
                "Depositaria": st.column_config.TextColumn("Depositaria", width="medium")
            }
        )
        
        # Recent activity summary
        st.markdown("#### 📊 Actividad Reciente")
        
        # Group by month for recent activity
        recent_months = filtered_trans.copy()
        recent_months['year_month'] = recent_months['date'].dt.to_period('M')
        monthly_activity = recent_months.groupby(['year_month', 'Tipo_Operacion']).size().unstack(fill_value=0)
        monthly_activity = monthly_activity.tail(12)  # Last 12 months
        
        if len(monthly_activity) > 0:
            # Create activity chart
            fig_activity = go.Figure()
            
            if '🌱 Alta' in monthly_activity.columns:
                fig_activity.add_trace(go.Bar(
                    x=monthly_activity.index.astype(str),
                    y=monthly_activity['🌱 Alta'],
                    name='Altas',
                    marker_color='#22c55e'
                ))
            
            if '💀 Baja' in monthly_activity.columns:
                fig_activity.add_trace(go.Bar(
                    x=monthly_activity.index.astype(str),
                    y=monthly_activity['💀 Baja'],
                    name='Bajas',
                    marker_color='#dc2626'
                ))
            
            fig_activity.update_layout(
                title="Actividad Mensual (Últimos 12 meses)",
                xaxis_title="Mes",
                yaxis_title="Número de Operaciones",
                height=300,
                plot_bgcolor='#1a1f2e',
                paper_bgcolor='#0e1117',
                font=dict(color='#cbd5e1', size=12),
                showlegend=True,
                barmode='group',
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="center",
                    x=0.5
                )
            )
            
            fig_activity.update_xaxes(gridcolor='#334155', showgrid=False)
            fig_activity.update_yaxes(gridcolor='#334155', showgrid=True)
            
            st.plotly_chart(fig_activity, use_container_width=True)
        
        # Download button
        csv_trans = display_trans.to_csv(index=False)
        st.download_button(
            label="📥 Descargar transacciones en CSV",
            data=csv_trans,
            file_name='transacciones_fondos.csv',
            mime='text/csv',
        )
    else:
        st.info("No se encontraron transacciones con los criterios especificados.")

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

with tab4:
    st.markdown("### 🔍 Búsqueda y Ciclo de Vida de Fondos")
    
    # Create a comprehensive fund lifecycle dataframe
    # Get all unique funds with their birth dates
    births_lifecycle = births[['Nombre', 'N_Registro', 'date', 'Gestora', 'Depositaria']].copy()
    births_lifecycle = births_lifecycle.rename(columns={'date': 'Fecha_Alta'})
    births_lifecycle['Estado'] = 'Alta'
    
    # Get all unique funds with their death dates
    deaths_lifecycle = deaths[['Nombre', 'N_Registro', 'date']].copy()
    deaths_lifecycle = deaths_lifecycle.rename(columns={'date': 'Fecha_Baja'})
    deaths_lifecycle['Estado'] = 'Baja'
    
    # Merge to create lifecycle view
    # First, get unique funds from births
    unique_funds = births_lifecycle.groupby('N_Registro').agg({
        'Nombre': 'first',
        'Fecha_Alta': 'min',
        'Gestora': 'first',
        'Depositaria': 'first'
    }).reset_index()
    
    # Then add death dates if they exist
    death_dates = deaths_lifecycle.groupby('N_Registro').agg({
        'Fecha_Baja': 'min'
    }).reset_index()
    
    fund_lifecycle = unique_funds.merge(death_dates, on='N_Registro', how='left')
    
    # Calculate lifespan
    fund_lifecycle['Vida_Dias'] = (fund_lifecycle['Fecha_Baja'] - fund_lifecycle['Fecha_Alta']).dt.days
    fund_lifecycle['Vida_Anos'] = (fund_lifecycle['Vida_Dias'] / 365.25).round(1)
    fund_lifecycle['Estado_Actual'] = fund_lifecycle['Fecha_Baja'].apply(lambda x: '💀 Liquidado' if pd.notna(x) else '✅ Activo')
    
    # Search options
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
    
    # Filter based on search
    filtered_lifecycle = fund_lifecycle.copy()
    
    if search_term:
        # Search in both name and registry number
        mask = (
            filtered_lifecycle['Nombre'].str.contains(search_term.upper(), case=False, na=False) |
            filtered_lifecycle['N_Registro'].astype(str).str.contains(search_term, na=False)
        )
        filtered_lifecycle = filtered_lifecycle[mask]
    
    if status_search == 'Activos':
        filtered_lifecycle = filtered_lifecycle[filtered_lifecycle['Fecha_Baja'].isna()]
    elif status_search == 'Liquidados':
        filtered_lifecycle = filtered_lifecycle[filtered_lifecycle['Fecha_Baja'].notna()]
    
    # Display statistics
    col1, col2, col3, col4 = st.columns(4)
    
    total_in_search = len(filtered_lifecycle)
    active_in_search = len(filtered_lifecycle[filtered_lifecycle['Fecha_Baja'].isna()])
    liquidated_in_search = len(filtered_lifecycle[filtered_lifecycle['Fecha_Baja'].notna()])
    
    with col1:
        st.metric("Total Fondos", f"{total_in_search:,}")
    
    with col2:
        st.metric("Activos", f"{active_in_search:,}", 
                  delta=f"{(active_in_search/total_in_search*100):.1f}%" if total_in_search > 0 else "0%")
    
    with col3:
        st.metric("Liquidados", f"{liquidated_in_search:,}",
                  delta=f"{(liquidated_in_search/total_in_search*100):.1f}%" if total_in_search > 0 else "0%")
    
    with col4:
        avg_lifespan = filtered_lifecycle[filtered_lifecycle['Vida_Anos'].notna()]['Vida_Anos'].mean()
        st.metric("Vida Media (años)", f"{avg_lifespan:.1f}" if pd.notna(avg_lifespan) else "N/A")
    
    # Display the lifecycle table
    st.markdown("#### Detalle de Fondos")
    
    # Prepare display dataframe
    display_lifecycle = filtered_lifecycle[['N_Registro', 'Nombre', 'Fecha_Alta', 'Fecha_Baja', 
                                           'Vida_Anos', 'Estado_Actual', 'Gestora', 'Depositaria']].copy()
    
    # Sort by registry number or date
    display_lifecycle = display_lifecycle.sort_values('Fecha_Alta', ascending=False)
    
    # Format dates for display
    display_lifecycle['Fecha_Alta'] = display_lifecycle['Fecha_Alta'].dt.strftime('%Y-%m-%d')
    display_lifecycle['Fecha_Baja'] = display_lifecycle['Fecha_Baja'].dt.strftime('%Y-%m-%d')
    
    st.dataframe(
        display_lifecycle,
        use_container_width=True,
        height=600,
        hide_index=True,
        column_config={
            "N_Registro": st.column_config.NumberColumn("Nº Registro", format="%d", width="small"),
            "Nombre": st.column_config.TextColumn("Nombre del Fondo", width="large"),
            "Fecha_Alta": st.column_config.TextColumn("Fecha Alta", width="small"),
            "Fecha_Baja": st.column_config.TextColumn("Fecha Baja", width="small"),
            "Vida_Anos": st.column_config.NumberColumn("Vida (años)", format="%.1f", width="small"),
            "Estado_Actual": st.column_config.TextColumn("Estado", width="small"),
            "Gestora": st.column_config.TextColumn("Gestora", width="medium"),
            "Depositaria": st.column_config.TextColumn("Depositaria", width="medium")
        }
    )
    
    # Lifespan distribution for liquidated funds
    if liquidated_in_search > 0:
        st.markdown("#### Distribución de Vida de Fondos Liquidados")
        
        liquidated_funds = filtered_lifecycle[filtered_lifecycle['Fecha_Baja'].notna()].copy()
        
        # Create histogram of lifespans
        fig_lifespan = go.Figure()
        
        fig_lifespan.add_trace(go.Histogram(
            x=liquidated_funds['Vida_Anos'],
            nbinsx=30,
            marker_color='#dc2626',
            opacity=0.7,
            hovertemplate='<b>Vida: %{x:.1f} años</b><br>Número de fondos: %{y}<extra></extra>'
        ))
        
        fig_lifespan.update_layout(
            xaxis_title="Vida del Fondo (años)",
            yaxis_title="Número de Fondos",
            height=350,
            plot_bgcolor='#1a1f2e',
            paper_bgcolor='#0e1117',
            font=dict(color='#cbd5e1', size=12),
            showlegend=False,
            bargap=0.1
        )
        
        fig_lifespan.update_xaxes(gridcolor='#334155', showgrid=True)
        fig_lifespan.update_yaxes(gridcolor='#334155', showgrid=True)
        
        st.plotly_chart(fig_lifespan, use_container_width=True)
        
        # Statistics about lifespan
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <div class="info-box">
                <h4>⏱️ Estadísticas de Vida</h4>
                <p>• Vida mínima: <strong>{liquidated_funds['Vida_Anos'].min():.1f} años</strong></p>
                <p>• Vida máxima: <strong>{liquidated_funds['Vida_Anos'].max():.1f} años</strong></p>
                <p>• Vida mediana: <strong>{liquidated_funds['Vida_Anos'].median():.1f} años</strong></p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            short_lived = len(liquidated_funds[liquidated_funds['Vida_Anos'] < 5])
            medium_lived = len(liquidated_funds[(liquidated_funds['Vida_Anos'] >= 5) & (liquidated_funds['Vida_Anos'] < 10)])
            long_lived = len(liquidated_funds[liquidated_funds['Vida_Anos'] >= 10])
            
            st.markdown(f"""
            <div class="info-box">
                <h4>📊 Distribución por Duración</h4>
                <p>• Menos de 5 años: <strong>{short_lived} ({short_lived/liquidated_in_search*100:.1f}%)</strong></p>
                <p>• Entre 5-10 años: <strong>{medium_lived} ({medium_lived/liquidated_in_search*100:.1f}%)</strong></p>
                <p>• Más de 10 años: <strong>{long_lived} ({long_lived/liquidated_in_search*100:.1f}%)</strong></p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            # Find funds that died quickly (less than 2 years)
            quick_deaths = len(liquidated_funds[liquidated_funds['Vida_Anos'] < 2])
            
            st.markdown(f"""
            <div class="info-box">
                <h4>⚠️ Muertes Prematuras</h4>
                <p>• Fondos liquidados en menos de 2 años: <strong>{quick_deaths}</strong></p>
                <p>• Porcentaje del total: <strong>{quick_deaths/liquidated_in_search*100:.1f}%</strong></p>
                <p>• Evidencia clara de sesgo de supervivencia</p>
            </div>
            """, unsafe_allow_html=True)

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
