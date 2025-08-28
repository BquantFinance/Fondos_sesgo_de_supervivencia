import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np

# Configuración de página
st.set_page_config(
    page_title="Sesgo de Supervivencia - Fondos CNMV",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS para dark mode con paleta elegante
st.markdown("""
<style>
    /* Dark mode palette */
    .stApp {
        background-color: #0e1117;
    }
    
    .main {
        padding-top: 2rem;
        background-color: #0e1117;
    }
    
    /* Metrics styling */
    [data-testid="metric-container"] {
        background: linear-gradient(135deg, #1e1e2e 0%, #2d2d44 100%);
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
    
    [data-testid="metric-container"] [data-testid="metric-label"] {
        color: #94a3b8;
        font-size: 0.9rem;
        font-weight: 500;
    }
    
    [data-testid="metric-container"] [data-testid="metric-value"] {
        color: #f1f5f9;
        font-size: 2rem;
        font-weight: 600;
    }
    
    [data-testid="metric-container"] [data-testid="metric-delta"] {
        color: #64748b;
    }
    
    /* Headers */
    h1 {
        color: #f1f5f9;
        font-weight: 300;
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
        text-align: center;
    }
    
    h2 {
        color: #cbd5e1;
        font-weight: 400;
        margin-top: 2.5rem;
        margin-bottom: 1.5rem;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid #334155;
    }
    
    h3 {
        color: #e2e8f0;
        font-weight: 400;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background-color: #1e1e2e;
    }
    
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e1e2e 0%, #151521 100%);
        border-right: 1px solid #334155;
    }
    
    /* Info boxes */
    .creator-box {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        padding: 1rem;
        border-radius: 12px;
        margin: 1rem 0;
        text-align: center;
        box-shadow: 0 4px 6px rgba(99, 102, 241, 0.3);
    }
    
    .creator-box a {
        color: #f1f5f9;
        text-decoration: none;
        font-weight: 600;
    }
    
    .creator-box a:hover {
        text-decoration: underline;
    }
    
    .info-box {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        border-left: 4px solid #6366f1;
        padding: 1.2rem;
        margin: 1.5rem 0;
        border-radius: 8px;
        color: #cbd5e1;
    }
    
    .alert-box {
        background: linear-gradient(135deg, #991b1b 0%, #dc2626 100%);
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        color: #fef2f2;
        text-align: center;
        font-weight: 600;
    }
    
    .success-box {
        background: linear-gradient(135deg, #14532d 0%, #16a34a 100%);
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        color: #f0fdf4;
        text-align: center;
        font-weight: 600;
    }
    
    /* Select boxes and inputs */
    .stSelectbox > div > div {
        background-color: #1e293b;
        border: 1px solid #475569;
    }
    
    /* Custom gradient for positive/negative */
    .positive-gradient {
        background: linear-gradient(135deg, #059669 0%, #10b981 100%);
        padding: 0.5rem 1rem;
        border-radius: 6px;
        color: white;
        display: inline-block;
    }
    
    .negative-gradient {
        background: linear-gradient(135deg, #dc2626 0%, #ef4444 100%);
        padding: 0.5rem 1rem;
        border-radius: 6px;
        color: white;
        display: inline-block;
    }
</style>
""", unsafe_allow_html=True)

# Título y créditos
st.markdown("<h1>🌙 Sesgo de Supervivencia en Fondos Españoles</h1>", unsafe_allow_html=True)
st.markdown("""
<div class="creator-box">
    Creado por <a href="https://twitter.com/Gsnchez" target="_blank">@Gsnchez</a> | 
    <a href="https://bquantfinance.com" target="_blank">bquantfinance.com</a>
</div>
""", unsafe_allow_html=True)

# Cargar datos
@st.cache_data
def load_data():
    df_all = pd.read_excel('cnmv_fondos_20250828_172717.xlsx', sheet_name='Todos_Fondos')
    df_births = pd.read_excel('cnmv_fondos_20250828_172717.xlsx', sheet_name='NUEVAS INSCRIPCIONES')
    df_deaths = pd.read_excel('cnmv_fondos_20250828_172717.xlsx', sheet_name='BAJAS')
    
    for df in [df_all, df_births, df_deaths]:
        df['Fecha_Parsed'] = pd.to_datetime(df['Fecha_Parsed'])
        df['Year_Month'] = df['Fecha_Parsed'].dt.to_period('M')
    
    return df_all, df_births, df_deaths

df_all, df_births, df_deaths = load_data()

# Sidebar para filtros
st.sidebar.markdown("## 🎯 Filtros de Consulta")

# Obtener años disponibles
years = sorted(df_all['Año'].unique())
selected_year = st.sidebar.selectbox(
    "📅 Seleccionar Año",
    years,
    index=len(years)-2  # Penúltimo año por defecto
)

# Obtener meses para el año seleccionado
months_in_year = sorted(df_all[df_all['Año'] == selected_year]['Mes'].unique())
month_names = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
    5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
    9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
}

selected_month = st.sidebar.selectbox(
    "📆 Seleccionar Mes",
    ["Todos"] + [month_names.get(m, str(m)) for m in months_in_year],
    index=0
)

# Convertir mes seleccionado a número
if selected_month != "Todos":
    month_num = [k for k, v in month_names.items() if v == selected_month][0] if selected_month in month_names.values() else int(selected_month)
else:
    month_num = None

# Filtrar datos según selección
if month_num:
    period_births = df_births[(df_births['Año'] == selected_year) & (df_births['Mes'] == month_num)]
    period_deaths = df_deaths[(df_deaths['Año'] == selected_year) & (df_deaths['Mes'] == month_num)]
    period_mergers = df_all[(df_all['Año'] == selected_year) & (df_all['Mes'] == month_num) & 
                            (df_all['Tipo_Operacion'] == 'FUSIÓN DE FONDOS DE INVERSIÓN')]
    period_label = f"{selected_month} {selected_year}"
else:
    period_births = df_births[df_births['Año'] == selected_year]
    period_deaths = df_deaths[df_deaths['Año'] == selected_year]
    period_mergers = df_all[(df_all['Año'] == selected_year) & 
                            (df_all['Tipo_Operacion'] == 'FUSIÓN DE FONDOS DE INVERSIÓN')]
    period_label = f"Año {selected_year}"

# Métricas del período seleccionado
st.markdown(f"## 📊 Resumen: {period_label}")

col1, col2, col3, col4 = st.columns(4)

births_count = len(period_births)
deaths_count = len(period_deaths)
mergers_count = len(period_mergers)
net_change = births_count - deaths_count - mergers_count

with col1:
    st.metric(
        label="🌱 Altas",
        value=f"{births_count}",
        delta="Nuevos fondos"
    )

with col2:
    st.metric(
        label="💀 Bajas",
        value=f"{deaths_count}",
        delta="Fondos liquidados"
    )

with col3:
    st.metric(
        label="🔄 Fusiones",
        value=f"{mergers_count}",
        delta="Fondos fusionados"
    )

with col4:
    st.metric(
        label="📈 Cambio Neto",
        value=f"{net_change:+}",
        delta="Altas - Bajas - Fusiones",
        delta_color="normal" if net_change >= 0 else "inverse"
    )

# Gráfico principal - Evolución histórica
st.markdown("## 📈 Evolución Histórica")

# Preparar datos anuales
yearly_births = df_births.groupby('Año').size().reset_index(name='Altas')
yearly_deaths = df_deaths.groupby('Año').size().reset_index(name='Bajas')
yearly_mergers = df_all[df_all['Tipo_Operacion'] == 'FUSIÓN DE FONDOS DE INVERSIÓN'].groupby('Año').size().reset_index(name='Fusiones')

yearly_data = pd.merge(yearly_births, yearly_deaths, on='Año', how='outer')
yearly_data = pd.merge(yearly_data, yearly_mergers, on='Año', how='outer')
yearly_data = yearly_data.fillna(0).sort_values('Año')

# Crear gráfico
fig = go.Figure()

# Altas (positivo)
fig.add_trace(go.Bar(
    x=yearly_data['Año'],
    y=yearly_data['Altas'],
    name='Altas',
    marker_color='#10b981',
    marker=dict(
        line=dict(width=0),
        pattern=dict(shape="")
    ),
    opacity=0.9,
    hovertemplate='<b>Altas</b><br>Año: %{x}<br>Fondos: %{y}<extra></extra>'
))

# Bajas (negativo)
fig.add_trace(go.Bar(
    x=yearly_data['Año'],
    y=-yearly_data['Bajas'],
    name='Bajas',
    marker_color='#ef4444',
    opacity=0.9,
    hovertemplate='<b>Bajas</b><br>Año: %{x}<br>Fondos: %{y}<extra></extra>'
))

# Fusiones (negativo)
fig.add_trace(go.Bar(
    x=yearly_data['Año'],
    y=-yearly_data['Fusiones'],
    name='Fusiones',
    marker_color='#f59e0b',
    opacity=0.9,
    hovertemplate='<b>Fusiones</b><br>Año: %{x}<br>Fondos: %{y}<extra></extra>'
))

# Línea de cambio neto
yearly_data['Cambio_Neto'] = yearly_data['Altas'] - yearly_data['Bajas'] - yearly_data['Fusiones']
fig.add_trace(go.Scatter(
    x=yearly_data['Año'],
    y=yearly_data['Cambio_Neto'],
    name='Cambio Neto',
    line=dict(color='#8b5cf6', width=3),
    mode='lines+markers',
    marker=dict(size=8),
    hovertemplate='<b>Cambio Neto</b><br>Año: %{x}<br>Fondos: %{y:+}<extra></extra>'
))

# Resaltar año seleccionado
fig.add_vrect(
    x0=selected_year - 0.5,
    x1=selected_year + 0.5,
    fillcolor="#6366f1",
    opacity=0.1,
    line_width=0,
    annotation_text=f"Año {selected_year}",
    annotation_position="top"
)

fig.update_layout(
    title="Altas vs Bajas de Fondos (2004-2025)",
    xaxis_title="Año",
    yaxis_title="Número de Fondos",
    hovermode='x unified',
    height=500,
    plot_bgcolor='#1e1e2e',
    paper_bgcolor='#0e1117',
    font=dict(color='#cbd5e1', family='Arial, sans-serif'),
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1
    ),
    barmode='relative'
)

fig.update_xaxes(gridcolor='#334155', showgrid=True, zeroline=False)
fig.update_yaxes(gridcolor='#334155', showgrid=True, zeroline=True, zerolinecolor='#64748b')

st.plotly_chart(fig, use_container_width=True)

# Detalle mensual del año seleccionado
st.markdown(f"## 📅 Detalle Mensual - {selected_year}")

# Datos mensuales para el año seleccionado
monthly_births = df_births[df_births['Año'] == selected_year].groupby('Mes').size().reset_index(name='Altas')
monthly_deaths = df_deaths[df_deaths['Año'] == selected_year].groupby('Mes').size().reset_index(name='Bajas')
monthly_mergers = df_all[(df_all['Año'] == selected_year) & 
                         (df_all['Tipo_Operacion'] == 'FUSIÓN DE FONDOS DE INVERSIÓN')].groupby('Mes').size().reset_index(name='Fusiones')

# Merge mensual
monthly_data = pd.DataFrame({'Mes': range(1, 13)})
monthly_data = pd.merge(monthly_data, monthly_births, on='Mes', how='left')
monthly_data = pd.merge(monthly_data, monthly_deaths, on='Mes', how='left')
monthly_data = pd.merge(monthly_data, monthly_mergers, on='Mes', how='left')
monthly_data = monthly_data.fillna(0)
monthly_data['Mes_Nombre'] = monthly_data['Mes'].map(month_names)

# Gráfico mensual
fig_monthly = go.Figure()

fig_monthly.add_trace(go.Bar(
    x=monthly_data['Mes_Nombre'],
    y=monthly_data['Altas'],
    name='Altas',
    marker_color='#10b981',
    text=monthly_data['Altas'],
    textposition='auto',
))

fig_monthly.add_trace(go.Bar(
    x=monthly_data['Mes_Nombre'],
    y=monthly_data['Bajas'],
    name='Bajas',
    marker_color='#ef4444',
    text=monthly_data['Bajas'],
    textposition='auto',
))

fig_monthly.add_trace(go.Bar(
    x=monthly_data['Mes_Nombre'],
    y=monthly_data['Fusiones'],
    name='Fusiones',
    marker_color='#f59e0b',
    text=monthly_data['Fusiones'],
    textposition='auto',
))

fig_monthly.update_layout(
    title=f"Distribución Mensual - {selected_year}",
    xaxis_title="Mes",
    yaxis_title="Número de Fondos",
    height=400,
    plot_bgcolor='#1e1e2e',
    paper_bgcolor='#0e1117',
    font=dict(color='#cbd5e1'),
    barmode='group',
    hovermode='x unified'
)

fig_monthly.update_xaxes(gridcolor='#334155', showgrid=False)
fig_monthly.update_yaxes(gridcolor='#334155', showgrid=True)

st.plotly_chart(fig_monthly, use_container_width=True)

# Estadísticas acumuladas
st.markdown("## 💎 Estadísticas Totales (2004-2025)")

col1, col2 = st.columns(2)

total_births = len(df_births)
total_deaths = len(df_deaths)
total_mergers = df_all[df_all['Tipo_Operacion'] == 'FUSIÓN DE FONDOS DE INVERSIÓN'].shape[0]
exit_rate = ((total_deaths + total_mergers) / total_births * 100)

with col1:
    st.markdown(f"""
    <div class="info-box">
        <h3>📊 Métricas de Supervivencia</h3>
        <p>• Total Altas: <strong>{total_births:,}</strong></p>
        <p>• Total Bajas: <strong>{total_deaths:,}</strong></p>
        <p>• Total Fusiones: <strong>{total_mergers:,}</strong></p>
        <p>• Tasa de Salida: <strong>{exit_rate:.1f}%</strong></p>
        <p>• Tasa de Mortalidad: <strong>{(total_deaths/total_births*100):.1f}%</strong></p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    # Calcular fondos activos estimados
    cumulative_net = (total_births - total_deaths - total_mergers)
    
    if cumulative_net < 0:
        status_class = "alert-box"
        status_text = f"⚠️ Mercado en Contracción: {abs(cumulative_net):,} fondos netos perdidos"
    else:
        status_class = "success-box"
        status_text = f"✅ Fondos Activos Estimados: {cumulative_net:,}"
    
    st.markdown(f"""
    <div class="info-box">
        <h3>🎯 Implicaciones del Sesgo</h3>
        <p>• Los retornos históricos <strong>excluyen fondos liquidados</strong></p>
        <p>• La rentabilidad real es <strong>inferior</strong> a la publicada</p>
        <p>• El riesgo está <strong>subestimado</strong> en las bases de datos</p>
        <p>• Efecto especialmente severo en <strong>crisis financieras</strong></p>
    </div>
    <div class="{status_class}">
        {status_text}
    </div>
    """, unsafe_allow_html=True)

# Lista de fondos del período (si hay)
if st.sidebar.checkbox("📋 Mostrar Lista de Fondos", value=False):
    st.markdown(f"## 📋 Fondos del Período: {period_label}")
    
    tab1, tab2, tab3 = st.tabs(["🌱 Altas", "💀 Bajas", "🔄 Fusiones"])
    
    with tab1:
        if len(period_births) > 0:
            st.dataframe(
                period_births[['Denominacion', 'Nº_Registro', 'Fecha']].rename(columns={
                    'Denominacion': 'Nombre del Fondo',
                    'Nº_Registro': 'Nº Registro',
                    'Fecha': 'Fecha Alta'
                }),
                use_container_width=True,
                height=400
            )
        else:
            st.info("No hay altas en este período")
    
    with tab2:
        if len(period_deaths) > 0:
            st.dataframe(
                period_deaths[['Denominacion', 'Nº_Registro', 'Fecha']].rename(columns={
                    'Denominacion': 'Nombre del Fondo',
                    'Nº_Registro': 'Nº Registro',
                    'Fecha': 'Fecha Baja'
                }),
                use_container_width=True,
                height=400
            )
        else:
            st.info("No hay bajas en este período")
    
    with tab3:
        if len(period_mergers) > 0:
            st.dataframe(
                period_mergers[['Denominacion', 'Nº_Registro', 'Fecha']].rename(columns={
                    'Denominacion': 'Nombre del Fondo',
                    'Nº_Registro': 'Nº Registro',
                    'Fecha': 'Fecha Fusión'
                }),
                use_container_width=True,
                height=400
            )
        else:
            st.info("No hay fusiones en este período")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #64748b; padding: 2rem 0;">
    <p>📊 Datos: CNMV (Comisión Nacional del Mercado de Valores)</p>
    <p>📅 Período analizado: 2004-2025 | 📄 Fuente: 1000+ boletines oficiales procesados</p>
    <p>
        Desarrollado por <a href="https://twitter.com/Gsnchez" target="_blank" style="color: #8b5cf6;">@Gsnchez</a> | 
        <a href="https://bquantfinance.com" target="_blank" style="color: #8b5cf6;">bquantfinance.com</a>
    </p>
</div>
""", unsafe_allow_html=True)
