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
    
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
        background-color: #1e1e2e;
        padding: 0.5rem;
        border-radius: 12px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding-left: 20px;
        padding-right: 20px;
        background-color: transparent;
        border-radius: 8px;
        color: #94a3b8;
        font-weight: 500;
    }
    
    .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        color: white;
    }
    
    /* DataFrame styling */
    [data-testid="stDataFrame"] {
        background: #1e1e2e;
        border: 1px solid #334155;
        border-radius: 8px;
    }
    
    .dataframe {
        font-size: 14px;
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
    
    /* Custom stats cards */
    .stats-card {
        background: linear-gradient(135deg, #1e1e2e 0%, #2d2d44 100%);
        padding: 1rem;
        border-radius: 12px;
        border: 1px solid rgba(99, 102, 241, 0.3);
        margin: 0.5rem 0;
        transition: transform 0.2s;
    }
    
    .stats-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(99, 102, 241, 0.2);
    }
    
    .highlight-period {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.2) 0%, rgba(139, 92, 246, 0.2) 100%);
        border: 2px solid #6366f1;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
    
    /* Select boxes and inputs */
    .stSelectbox > div > div {
        background-color: #1e293b;
        border: 1px solid #475569;
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

# ============= SIDEBAR PARA FILTROS =============
st.sidebar.markdown("## 🎯 Seleccionar Período")

# Obtener años disponibles
years = sorted(df_all['Año'].unique())
selected_year = st.sidebar.selectbox(
    "📅 **Año**",
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
    "📆 **Mes**",
    ["Todo el año"] + [month_names.get(m, str(m)) for m in months_in_year],
    index=0
)

# Convertir mes seleccionado a número
if selected_month != "Todo el año":
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

# Calcular estadísticas
births_count = len(period_births)
deaths_count = len(period_deaths)
mergers_count = len(period_mergers)
net_change = births_count - deaths_count - mergers_count

# Opciones de visualización en sidebar
st.sidebar.markdown("---")
st.sidebar.markdown("## 📊 Opciones de Visualización")
show_full_analysis = st.sidebar.checkbox("Mostrar análisis completo", value=True)
show_historical = st.sidebar.checkbox("Mostrar evolución histórica", value=True)

# ============= SECCIÓN PRINCIPAL: FONDOS DEL PERÍODO =============
st.markdown(f'<div class="highlight-period"><h2 style="margin-top:0;">📋 Fondos del Período: {period_label}</h2></div>', unsafe_allow_html=True)

# Métricas del período en la parte superior
col1, col2, col3, col4 = st.columns(4)

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
        delta="Balance del período",
        delta_color="normal" if net_change >= 0 else "inverse"
    )

# Tabs para mostrar los fondos
tab1, tab2, tab3 = st.tabs(["🌱 **Altas**", "💀 **Bajas**", "🔄 **Fusiones**"])

with tab1:
    if len(period_births) > 0:
        st.markdown(f"<div class='stats-card'><strong>{len(period_births)}</strong> nuevos fondos registrados en {period_label}</div>", unsafe_allow_html=True)
        
        # Preparar datos para mostrar
        display_births = period_births[['Denominacion', 'Nº_Registro', 'Fecha']].copy()
        display_births = display_births.rename(columns={
            'Denominacion': 'Nombre del Fondo',
            'Nº_Registro': 'Nº Registro',
            'Fecha': 'Fecha Alta'
        })
        display_births = display_births.sort_values('Fecha Alta', ascending=False)
        
        # Mostrar DataFrame con estilo
        st.dataframe(
            display_births,
            use_container_width=True,
            height=400,
            hide_index=True,
            column_config={
                "Nombre del Fondo": st.column_config.TextColumn(
                    "Nombre del Fondo",
                    width="large",
                ),
                "Nº Registro": st.column_config.TextColumn(
                    "Nº Registro",
                    width="small",
                ),
                "Fecha Alta": st.column_config.DateColumn(
                    "Fecha Alta",
                    format="DD/MM/YYYY",
                    width="small",
                )
            }
        )
    else:
        st.info(f"📭 No hay altas registradas en {period_label}")

with tab2:
    if len(period_deaths) > 0:
        st.markdown(f"<div class='stats-card'><strong>{len(period_deaths)}</strong> fondos liquidados en {period_label}</div>", unsafe_allow_html=True)
        
        display_deaths = period_deaths[['Denominacion', 'Nº_Registro', 'Fecha']].copy()
        display_deaths = display_deaths.rename(columns={
            'Denominacion': 'Nombre del Fondo',
            'Nº_Registro': 'Nº Registro',
            'Fecha': 'Fecha Baja'
        })
        display_deaths = display_deaths.sort_values('Fecha Baja', ascending=False)
        
        st.dataframe(
            display_deaths,
            use_container_width=True,
            height=400,
            hide_index=True,
            column_config={
                "Nombre del Fondo": st.column_config.TextColumn(
                    "Nombre del Fondo",
                    width="large",
                ),
                "Nº Registro": st.column_config.TextColumn(
                    "Nº Registro",
                    width="small",
                ),
                "Fecha Baja": st.column_config.DateColumn(
                    "Fecha Baja",
                    format="DD/MM/YYYY",
                    width="small",
                )
            }
        )
    else:
        st.info(f"📭 No hay bajas registradas en {period_label}")

with tab3:
    if len(period_mergers) > 0:
        st.markdown(f"<div class='stats-card'><strong>{len(period_mergers)}</strong> fondos fusionados en {period_label}</div>", unsafe_allow_html=True)
        
        display_mergers = period_mergers[['Denominacion', 'Nº_Registro', 'Fecha']].copy()
        display_mergers = display_mergers.rename(columns={
            'Denominacion': 'Nombre del Fondo',
            'Nº_Registro': 'Nº Registro',
            'Fecha': 'Fecha Fusión'
        })
        display_mergers = display_mergers.sort_values('Fecha Fusión', ascending=False)
        
        st.dataframe(
            display_mergers,
            use_container_width=True,
            height=400,
            hide_index=True,
            column_config={
                "Nombre del Fondo": st.column_config.TextColumn(
                    "Nombre del Fondo",
                    width="large",
                ),
                "Nº Registro": st.column_config.TextColumn(
                    "Nº Registro",
                    width="small",
                ),
                "Fecha Fusión": st.column_config.DateColumn(
                    "Fecha Fusión",
                    format="DD/MM/YYYY",
                    width="small",
                )
            }
        )
    else:
        st.info(f"📭 No hay fusiones registradas en {period_label}")

# ============= ANÁLISIS DETALLADO (si está activado) =============
if show_full_analysis:
    # Detalle mensual del año seleccionado
    st.markdown(f"## 📅 Distribución Mensual - {selected_year}")
    
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
    monthly_data['Cambio_Neto'] = monthly_data['Altas'] - monthly_data['Bajas'] - monthly_data['Fusiones']
    
    # Gráfico mensual
    fig_monthly = go.Figure()
    
    fig_monthly.add_trace(go.Bar(
        x=monthly_data['Mes_Nombre'],
        y=monthly_data['Altas'],
        name='Altas',
        marker_color='#10b981',
        text=monthly_data['Altas'].astype(int),
        textposition='auto',
        hovertemplate='<b>%{x}</b><br>Altas: %{y}<extra></extra>'
    ))
    
    fig_monthly.add_trace(go.Bar(
        x=monthly_data['Mes_Nombre'],
        y=monthly_data['Bajas'],
        name='Bajas',
        marker_color='#ef4444',
        text=monthly_data['Bajas'].astype(int),
        textposition='auto',
        hovertemplate='<b>%{x}</b><br>Bajas: %{y}<extra></extra>'
    ))
    
    fig_monthly.add_trace(go.Bar(
        x=monthly_data['Mes_Nombre'],
        y=monthly_data['Fusiones'],
        name='Fusiones',
        marker_color='#f59e0b',
        text=monthly_data['Fusiones'].astype(int),
        textposition='auto',
        hovertemplate='<b>%{x}</b><br>Fusiones: %{y}<extra></extra>'
    ))
    
    # Resaltar mes seleccionado si aplica
    if month_num:
        month_idx = month_num - 1
        fig_monthly.add_vrect(
            x0=month_idx - 0.4,
            x1=month_idx + 0.4,
            fillcolor="#6366f1",
            opacity=0.2,
            line_width=2,
            line_color="#6366f1",
        )
    
    fig_monthly.update_layout(
        xaxis_title="",
        yaxis_title="Número de Fondos",
        height=400,
        plot_bgcolor='#1e1e2e',
        paper_bgcolor='#0e1117',
        font=dict(color='#cbd5e1'),
        barmode='group',
        hovermode='x unified',
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5
        )
    )
    
    fig_monthly.update_xaxes(gridcolor='#334155', showgrid=False)
    fig_monthly.update_yaxes(gridcolor='#334155', showgrid=True)
    
    st.plotly_chart(fig_monthly, use_container_width=True)

# ============= EVOLUCIÓN HISTÓRICA (si está activada) =============
if show_historical:
    st.markdown("## 📈 Evolución Histórica Completa")
    
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
        opacity=0.9,
        hovertemplate='<b>%{x}</b><br>Altas: %{y}<extra></extra>'
    ))
    
    # Bajas (negativo)
    fig.add_trace(go.Bar(
        x=yearly_data['Año'],
        y=-yearly_data['Bajas'],
        name='Bajas',
        marker_color='#ef4444',
        opacity=0.9,
        hovertemplate='<b>%{x}</b><br>Bajas: %{y}<extra></extra>'
    ))
    
    # Fusiones (negativo)
    fig.add_trace(go.Bar(
        x=yearly_data['Año'],
        y=-yearly_data['Fusiones'],
        name='Fusiones',
        marker_color='#f59e0b',
        opacity=0.9,
        hovertemplate='<b>%{x}</b><br>Fusiones: %{y}<extra></extra>'
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
        hovertemplate='<b>%{x}</b><br>Cambio Neto: %{y:+}<extra></extra>'
    ))
    
    # Resaltar año seleccionado
    fig.add_vrect(
        x0=selected_year - 0.5,
        x1=selected_year + 0.5,
        fillcolor="#6366f1",
        opacity=0.1,
        line_width=0,
        annotation_text=f"{selected_year}",
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
            xanchor="center",
            x=0.5
        ),
        barmode='relative'
    )
    
    fig.update_xaxes(gridcolor='#334155', showgrid=True, zeroline=False)
    fig.update_yaxes(gridcolor='#334155', showgrid=True, zeroline=True, zerolinecolor='#64748b')
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Estadísticas acumuladas
    st.markdown("## 💎 Evidencia del Sesgo de Supervivencia")
    
    col1, col2, col3 = st.columns(3)
    
    total_births = len(df_births)
    total_deaths = len(df_deaths)
    total_mergers = df_all[df_all['Tipo_Operacion'] == 'FUSIÓN DE FONDOS DE INVERSIÓN'].shape[0]
    exit_rate = ((total_deaths + total_mergers) / total_births * 100)
    
    with col1:
        st.markdown(f"""
        <div class="info-box">
            <h3>📊 Totales Históricos</h3>
            <p>• Total Altas: <strong>{total_births:,}</strong></p>
            <p>• Total Bajas: <strong>{total_deaths:,}</strong></p>
            <p>• Total Fusiones: <strong>{total_mergers:,}</strong></p>
            <p>• Período: <strong>2004-2025</strong></p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="info-box">
            <h3>💀 Tasas de Salida</h3>
            <p>• Tasa de Mortalidad: <strong>{(total_deaths/total_births*100):.1f}%</strong></p>
            <p>• Tasa de Fusión: <strong>{(total_mergers/total_births*100):.1f}%</strong></p>
            <p>• <span style="color: #ef4444;">Tasa Total de Salida: <strong>{exit_rate:.1f}%</strong></span></p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="info-box">
            <h3>⚠️ Implicaciones</h3>
            <p>• Retornos <strong>sobrestimados</strong></p>
            <p>• Riesgo <strong>subestimado</strong></p>
            <p>• Bases de datos <strong>incompletas</strong></p>
            <p>• Performance <strong>sesgada</strong></p>
        </div>
        """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #64748b; padding: 2rem 0;">
    <p>📊 Datos: CNMV (Comisión Nacional del Mercado de Valores) | 📅 Período: 2004-2025</p>
    <p>
        Desarrollado por <a href="https://twitter.com/Gsnchez" target="_blank" style="color: #8b5cf6;">@Gsnchez</a> | 
        <a href="https://bquantfinance.com" target="_blank" style="color: #8b5cf6;">bquantfinance.com</a>
    </p>
</div>
""", unsafe_allow_html=True)
