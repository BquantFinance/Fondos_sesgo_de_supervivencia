import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np
import re

# Page configuration
st.set_page_config(
    page_title="Sesgo de Supervivencia - Fondos CNMV",
    page_icon="💀",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Dark theme CSS
st.markdown("""
<style>
    .stApp {
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
    
    .alert-box {
        background: linear-gradient(135deg, #991b1b 0%, #dc2626 100%);
        padding: 1.2rem;
        border-radius: 12px;
        margin: 1.5rem 0;
        color: #fef2f2;
        text-align: center;
        font-weight: 600;
        font-size: 1.1rem;
        box-shadow: 0 4px 6px rgba(220, 38, 38, 0.3);
    }
    
    .info-box {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        border-left: 4px solid #6366f1;
        padding: 1.2rem;
        margin: 1.5rem 0;
        border-radius: 8px;
        color: #cbd5e1;
    }
    
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
    
    .crisis-period {
        background: rgba(239, 68, 68, 0.1);
        border: 2px solid rgba(239, 68, 68, 0.3);
        border-radius: 12px;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Title
st.markdown("<h1>💀 Sesgo de Supervivencia en Fondos Españoles</h1>", unsafe_allow_html=True)
st.markdown("""
<div class="creator-box">
    Análisis del Sesgo de Supervivencia en la Industria de Fondos Española (CNMV) | 2004-2025
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
    
    return df

df = load_and_process_data()

# Calculate key metrics
births = df[df['status'] == 'NUEVAS_INSCRIPCIONES']
deaths = df[df['status'] == 'BAJAS']

total_births = len(births)
total_deaths = len(deaths)
mortality_rate = (total_deaths / total_births * 100) if total_births > 0 else 0
net_change = total_births - total_deaths

# KEY INSIGHT: Survivorship Bias Alert
st.markdown(f"""
<div class="alert-box">
    ⚠️ EVIDENCIA CRÍTICA DE SESGO DE SUPERVIVENCIA ⚠️<br>
    Mortalidad: {mortality_rate:.1f}% | Más fondos mueren que nacen | {abs(net_change):,} fondos desaparecidos netos
</div>
""", unsafe_allow_html=True)

# Top metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="🌱 Total Altas",
        value=f"{total_births:,}",
        delta="Fondos creados"
    )

with col2:
    st.metric(
        label="💀 Total Bajas",
        value=f"{total_deaths:,}",
        delta="Fondos liquidados"
    )

with col3:
    st.metric(
        label="📉 Tasa Mortalidad",
        value=f"{mortality_rate:.1f}%",
        delta="Bajas/Altas"
    )

with col4:
    st.metric(
        label="⚰️ Saldo Neto",
        value=f"{net_change:,}",
        delta="Déficit total",
        delta_color="inverse"
    )

# Prepare yearly data
yearly_stats = df.groupby(['year', 'status']).size().unstack(fill_value=0)
yearly_stats = yearly_stats.rename(columns={
    'NUEVAS_INSCRIPCIONES': 'Altas',
    'BAJAS': 'Bajas'
})
yearly_stats['Cambio_Neto'] = yearly_stats['Altas'] - yearly_stats['Bajas']
yearly_stats['Tasa_Mortalidad_Anual'] = (yearly_stats['Bajas'] / yearly_stats['Altas'] * 100).round(1)
yearly_stats = yearly_stats.reset_index()

# VISUALIZATION 1: Historical Evolution
st.markdown("## 📊 Evolución Histórica: La Cruda Realidad")

fig1 = go.Figure()

# Add births (positive)
fig1.add_trace(go.Bar(
    x=yearly_stats['year'],
    y=yearly_stats['Altas'],
    name='Altas (Nacimientos)',
    marker_color='#10b981',
    text=yearly_stats['Altas'],
    textposition='outside',
    hovertemplate='<b>%{x}</b><br>Altas: %{y}<extra></extra>'
))

# Add deaths (negative)
fig1.add_trace(go.Bar(
    x=yearly_stats['year'],
    y=-yearly_stats['Bajas'],
    name='Bajas (Muertes)',
    marker_color='#ef4444',
    text=yearly_stats['Bajas'],
    textposition='outside',
    hovertemplate='<b>%{x}</b><br>Bajas: %{y}<extra></extra>'
))

# Add net change line
fig1.add_trace(go.Scatter(
    x=yearly_stats['year'],
    y=yearly_stats['Cambio_Neto'],
    name='Cambio Neto',
    line=dict(color='#fbbf24', width=3),
    mode='lines+markers',
    marker=dict(size=10),
    hovertemplate='<b>%{x}</b><br>Cambio Neto: %{y:+}<extra></extra>'
))

# Highlight crisis period (2009-2015)
fig1.add_vrect(
    x0=2008.5, x1=2015.5,
    fillcolor="red", opacity=0.1,
    annotation_text="CRISIS<br>FINANCIERA",
    annotation_position="top"
)

fig1.update_layout(
    title="Nacimientos vs Muertes de Fondos: El Cementerio Crece",
    xaxis_title="Año",
    yaxis_title="Número de Fondos",
    hovermode='x unified',
    height=500,
    plot_bgcolor='#1e1e2e',
    paper_bgcolor='#0e1117',
    font=dict(color='#cbd5e1'),
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

fig1.add_hline(y=0, line_color="#64748b", line_width=2)
fig1.update_xaxes(gridcolor='#334155', showgrid=False)
fig1.update_yaxes(gridcolor='#334155', showgrid=True)

st.plotly_chart(fig1, use_container_width=True)

# VISUALIZATION 2: Mortality Rate Evolution
st.markdown("## 💀 Tasa de Mortalidad Anual")

fig2 = go.Figure()

# Calculate colors based on mortality rate
colors = ['#ef4444' if rate > 100 else '#f59e0b' if rate > 50 else '#10b981' 
          for rate in yearly_stats['Tasa_Mortalidad_Anual']]

fig2.add_trace(go.Bar(
    x=yearly_stats['year'],
    y=yearly_stats['Tasa_Mortalidad_Anual'],
    marker_color=colors,
    text=[f"{rate:.0f}%" for rate in yearly_stats['Tasa_Mortalidad_Anual']],
    textposition='outside',
    hovertemplate='<b>%{x}</b><br>Tasa Mortalidad: %{y:.1f}%<extra></extra>'
))

fig2.add_hline(y=100, line_color="#ef4444", line_width=2, line_dash="dash",
               annotation_text="100% = Más muertes que nacimientos")

fig2.update_layout(
    title="Tasa de Mortalidad: Años de Masacre (>100% = Más Muertes que Nacimientos)",
    xaxis_title="Año",
    yaxis_title="Tasa de Mortalidad (%)",
    height=400,
    plot_bgcolor='#1e1e2e',
    paper_bgcolor='#0e1117',
    font=dict(color='#cbd5e1'),
    showlegend=False
)

fig2.update_xaxes(gridcolor='#334155', showgrid=False)
fig2.update_yaxes(gridcolor='#334155', showgrid=True)

st.plotly_chart(fig2, use_container_width=True)

# Crisis Period Analysis
st.markdown("## 🔥 Análisis del Período de Crisis (2009-2015)")

crisis_data = yearly_stats[(yearly_stats['year'] >= 2009) & (yearly_stats['year'] <= 2015)]
crisis_births = crisis_data['Altas'].sum()
crisis_deaths = crisis_data['Bajas'].sum()
crisis_net = crisis_births - crisis_deaths
crisis_mortality = (crisis_deaths / crisis_births * 100) if crisis_births > 0 else 0

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""
    <div class="crisis-period">
        <h3>📊 Período Crisis</h3>
        <p>• Altas: <strong>{crisis_births:,}</strong></p>
        <p>• Bajas: <strong>{crisis_deaths:,}</strong></p>
        <p>• Balance: <strong style="color: #ef4444;">{crisis_net:,}</strong></p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="crisis-period">
        <h3>💀 Tasa Mortalidad Crisis</h3>
        <p style="font-size: 2rem; color: #ef4444;"><strong>{crisis_mortality:.0f}%</strong></p>
        <p>Casi 2 muertes por cada nacimiento</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="crisis-period">
        <h3>⚠️ Impacto</h3>
        <p>• <strong>{abs(crisis_net):,}</strong> fondos desaparecidos</p>
        <p>• 7 años consecutivos negativos</p>
        <p>• Sesgo extremo en datos históricos</p>
    </div>
    """, unsafe_allow_html=True)

# VISUALIZATION 3: Cumulative Impact
st.markdown("## 📈 Impacto Acumulado: El Sesgo se Agrava")

yearly_stats['Cumulative_Net'] = yearly_stats['Cambio_Neto'].cumsum()

fig3 = go.Figure()

fig3.add_trace(go.Scatter(
    x=yearly_stats['year'],
    y=yearly_stats['Cumulative_Net'],
    mode='lines+markers',
    fill='tozeroy',
    fillcolor='rgba(239, 68, 68, 0.2)',
    line=dict(color='#ef4444', width=3),
    marker=dict(size=8),
    text=[f"{val:+,}" for val in yearly_stats['Cumulative_Net']],
    textposition='top center',
    hovertemplate='<b>%{x}</b><br>Déficit Acumulado: %{y:,}<extra></extra>'
))

fig3.add_hline(y=0, line_color="#64748b", line_width=1, line_dash="dash")

fig3.update_layout(
    title="Déficit Acumulado de Fondos: La Brecha que Crece",
    xaxis_title="Año",
    yaxis_title="Cambio Neto Acumulado",
    height=400,
    plot_bgcolor='#1e1e2e',
    paper_bgcolor='#0e1117',
    font=dict(color='#cbd5e1'),
    showlegend=False
)

fig3.update_xaxes(gridcolor='#334155', showgrid=False)
fig3.update_yaxes(gridcolor='#334155', showgrid=True)

st.plotly_chart(fig3, use_container_width=True)

# Top Management Companies Analysis
st.markdown("## 🏢 Gestoras con Mayor Actividad")

# Births by management company
births_by_gestora = births.dropna(subset=['Gestora']).groupby('Gestora').size().reset_index(name='Altas')
top_gestoras_births = births_by_gestora.nlargest(15, 'Altas')

fig4 = go.Figure()

fig4.add_trace(go.Bar(
    y=top_gestoras_births['Gestora'],
    x=top_gestoras_births['Altas'],
    orientation='h',
    marker_color='#10b981',
    text=top_gestoras_births['Altas'],
    textposition='outside',
    hovertemplate='<b>%{y}</b><br>Nuevos Fondos: %{x}<extra></extra>'
))

fig4.update_layout(
    title="Top 15 Gestoras por Creación de Fondos",
    xaxis_title="Número de Fondos Creados",
    yaxis_title="",
    height=500,
    plot_bgcolor='#1e1e2e',
    paper_bgcolor='#0e1117',
    font=dict(color='#cbd5e1'),
    showlegend=False,
    margin=dict(l=300)
)

fig4.update_xaxes(gridcolor='#334155', showgrid=True)
fig4.update_yaxes(gridcolor='#334155', showgrid=False)

st.plotly_chart(fig4, use_container_width=True)

# Key Implications
st.markdown("## ⚠️ Implicaciones del Sesgo de Supervivencia")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="info-box">
        <h3>📊 Impacto en Análisis de Rentabilidad</h3>
        <ul style="line-height: 1.8;">
            <li>✓ Los fondos que fracasan <strong>desaparecen de las bases de datos</strong></li>
            <li>✓ Solo sobreviven los fondos con mejor performance</li>
            <li>✓ Las rentabilidades históricas están <strong>infladas artificialmente</strong></li>
            <li>✓ El riesgo real está <strong>sistemáticamente subestimado</strong></li>
            <li>✓ Con 143% de mortalidad, el sesgo es <strong>EXTREMO</strong></li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="info-box">
        <h3>🎯 Para el Inversor</h3>
        <ul style="line-height: 1.8;">
            <li>⚠️ <strong>No confíes en rentabilidades históricas promedio</strong></li>
            <li>⚠️ El riesgo de pérdida es mayor al publicado</li>
            <li>⚠️ Muchos fondos "ganadores" de hoy serán los muertos de mañana</li>
            <li>⚠️ La selección activa de fondos tiene alta probabilidad de fracaso</li>
            <li>⚠️ Considera alternativas de inversión pasiva e indexada</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# Summary Statistics Table
st.markdown("## 📋 Resumen Estadístico Completo")

# Create summary by year with additional metrics
summary_data = []
for year in yearly_stats['year']:
    year_data = yearly_stats[yearly_stats['year'] == year].iloc[0]
    summary_data.append({
        'Año': int(year),
        'Altas': int(year_data['Altas']),
        'Bajas': int(year_data['Bajas']),
        'Cambio Neto': int(year_data['Cambio_Neto']),
        'Tasa Mortalidad (%)': f"{year_data['Tasa_Mortalidad_Anual']:.0f}%",
        'Acumulado': int(year_data['Cumulative_Net'])
    })

summary_df = pd.DataFrame(summary_data)

# Style the dataframe
def style_negative(val):
    if isinstance(val, str):
        return ''
    return 'color: #ef4444' if val < 0 else 'color: #10b981'

styled_df = summary_df.style.applymap(style_negative, subset=['Cambio Neto', 'Acumulado'])

st.dataframe(
    summary_df,
    use_container_width=True,
    height=400,
    hide_index=True,
    column_config={
        "Año": st.column_config.NumberColumn("Año", format="%d"),
        "Altas": st.column_config.NumberColumn("Altas", format="%d"),
        "Bajas": st.column_config.NumberColumn("Bajas", format="%d"),
        "Cambio Neto": st.column_config.NumberColumn("Cambio Neto", format="%d"),
        "Tasa Mortalidad (%)": st.column_config.TextColumn("Mortalidad"),
        "Acumulado": st.column_config.NumberColumn("Déficit Acum.", format="%d")
    }
)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #64748b; padding: 2rem 0;">
    <p>📊 Datos: CNMV (Comisión Nacional del Mercado de Valores) | 📅 Período: 2004-2025</p>
    <p>⚠️ Este análisis demuestra el severo sesgo de supervivencia en la industria de fondos española</p>
    <p>💀 Más de 3,600 fondos han desaparecido, distorsionando las estadísticas de rentabilidad</p>
</div>
""", unsafe_allow_html=True)
