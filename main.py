import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import networkx as nx
import numpy as np
import re
from collections import Counter
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# ─────────────────────────────────────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="CNMV Fund Observatory · Sesgo de Supervivencia",
    page_icon="◉",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─────────────────────────────────────────────────────────────────────────────
# THEME — Refined dark with amber/warm accent
# ─────────────────────────────────────────────────────────────────────────────

COLORS = {
    'bg':          '#0a0a0a',
    'surface':     '#141414',
    'surface2':    '#1a1a1a',
    'border':      'rgba(255,255,255,0.06)',
    'text':        '#e8e4df',
    'text_muted':  '#8a8580',
    'accent':      '#e2a44e',      # warm amber
    'accent2':     '#c2785c',      # terracotta
    'accent3':     '#7c9885',      # muted sage
    'green':       '#5fa87a',
    'red':         '#c75d5d',
    'purple':      '#9b8ec4',
    'blue':        '#6b9bc3',
}

PLOTLY_LAYOUT = dict(
    plot_bgcolor=COLORS['bg'],
    paper_bgcolor=COLORS['bg'],
    font=dict(family='DM Sans, sans-serif', color=COLORS['text'], size=12),
    hoverlabel=dict(
        bgcolor='rgba(20,20,20,0.95)',
        font_size=12,
        font_family='DM Sans, sans-serif',
        bordercolor='rgba(255,255,255,0.1)'
    ),
    margin=dict(t=60, b=40, l=50, r=30),
)

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700&family=DM+Mono:wght@400;500&family=Playfair+Display:ital,wght@0,600;0,700;1,600&display=swap');

    :root {{
        --bg: {COLORS['bg']};
        --surface: {COLORS['surface']};
        --accent: {COLORS['accent']};
        --accent2: {COLORS['accent2']};
        --text: {COLORS['text']};
        --muted: {COLORS['text_muted']};
    }}

    .stApp {{ background: var(--bg); }}
    .main {{ background: var(--bg); }}

    * {{ font-family: 'DM Sans', sans-serif; }}

    /* ── Metrics ── */
    [data-testid="metric-container"] {{
        background: var(--surface);
        padding: 1.4rem 1.6rem;
        border-radius: 14px;
        border: 1px solid rgba(255,255,255,0.04);
        transition: border-color 0.3s ease;
    }}
    [data-testid="metric-container"]:hover {{
        border-color: rgba(226,164,78,0.25);
    }}
    [data-testid="metric-container"] [data-testid="metric-label"] {{
        color: var(--muted);
        font-size: 0.7rem;
        font-weight: 500;
        letter-spacing: 1.5px;
        text-transform: uppercase;
    }}
    [data-testid="metric-container"] [data-testid="metric-value"] {{
        color: var(--text);
        font-family: 'DM Mono', monospace;
        font-size: 1.8rem;
        font-weight: 500;
    }}
    [data-testid="metric-container"] [data-testid="metric-delta"] {{
        color: var(--muted);
        font-size: 0.8rem;
    }}

    /* ── Headers ── */
    h1 {{
        font-family: 'Playfair Display', serif !important;
        color: var(--text) !important;
        font-weight: 700 !important;
        font-size: 2.4rem !important;
        letter-spacing: -0.5px !important;
    }}
    h2 {{
        font-family: 'Playfair Display', serif !important;
        color: var(--text) !important;
        font-weight: 600 !important;
        font-size: 1.6rem !important;
    }}
    h3 {{
        color: {COLORS['text_muted']} !important;
        font-weight: 500 !important;
        font-size: 1rem !important;
        letter-spacing: 0.5px !important;
    }}

    /* ── Tabs ── */
    .stTabs [data-baseweb="tab-list"] {{
        background: transparent;
        gap: 0;
        border-bottom: 1px solid rgba(255,255,255,0.06);
        padding: 0;
    }}
    .stTabs [data-baseweb="tab"] {{
        background: transparent;
        border-radius: 0;
        color: var(--muted);
        font-weight: 500;
        font-size: 0.85rem;
        letter-spacing: 0.5px;
        padding: 0.8rem 1.6rem;
        border-bottom: 2px solid transparent;
        transition: all 0.3s ease;
    }}
    .stTabs [data-baseweb="tab"]:hover {{
        color: var(--text);
    }}
    .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {{
        background: transparent;
        color: var(--accent);
        border-bottom: 2px solid var(--accent);
    }}
    .stTabs [data-baseweb="tab-highlight"] {{
        display: none;
    }}

    /* ── Inputs ── */
    .stTextInput > div > div > input,
    .stSelectbox > div > div {{
        background: var(--surface) !important;
        border: 1px solid rgba(255,255,255,0.06) !important;
        border-radius: 10px !important;
        color: var(--text) !important;
    }}
    .stTextInput > div > div > input:focus {{
        border-color: var(--accent) !important;
        box-shadow: 0 0 0 2px rgba(226,164,78,0.15) !important;
    }}
    .stTextInput > div > div > input::placeholder {{ color: var(--muted) !important; }}
    label {{ color: var(--muted) !important; font-size: 0.75rem !important; letter-spacing: 0.5px; text-transform: uppercase; }}

    /* ── DataFrames ── */
    [data-testid="stDataFrame"] {{
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid rgba(255,255,255,0.04);
    }}

    /* ── Misc ── */
    .stMarkdown hr {{ border-color: rgba(255,255,255,0.06); margin: 2rem 0; }}
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    .block-container {{ padding-top: 2rem; max-width: 1300px; }}
    
    /* ── Custom components ── */
    .hero-stat {{
        font-family: 'DM Mono', monospace;
        font-size: 3.2rem;
        font-weight: 500;
        line-height: 1;
    }}
    .hero-label {{
        font-size: 0.7rem;
        letter-spacing: 2px;
        text-transform: uppercase;
        color: var(--muted);
        margin-top: 0.4rem;
    }}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# DATA LOADING — Fixed CSV parsing
# ─────────────────────────────────────────────────────────────────────────────

@st.cache_data(show_spinner=False)
def load_data():
    """Parse the CNMV CSV with its tricky quoting format."""
    with open('cnmv_funds_data_FINAL.csv', 'r', encoding='utf-8-sig') as f:
        lines = f.readlines()

    header = lines[0].strip()
    cleaned = [header]
    for line in lines[1:]:
        line = line.strip()
        if line.startswith('"') and line.endswith('"'):
            line = line[1:-1]
            line = line.replace('""', '"')
        cleaned.append(line)

    import io
    df = pd.read_csv(io.StringIO('\n'.join(cleaned)))

    # Extract end date from bulletin filename
    def _extract_date(filename):
        m = re.search(r'(\d{2})-(\d{2})-(\d{4})_al_(\d{2})-(\d{2})-(\d{4})', str(filename))
        if m:
            return pd.to_datetime(f"{m.group(6)}-{m.group(5)}-{m.group(4)}")
        m = re.search(r'(\d{2})-(\d{2})-(\d{4})', str(filename))
        if m:
            return pd.to_datetime(f"{m.group(3)}-{m.group(2)}-{m.group(1)}")
        return None

    df['date'] = df['file'].apply(_extract_date)
    df = df.dropna(subset=['date'])
    df['year'] = df['date'].dt.year
    df = df.drop_duplicates(subset=['N_Registro', 'status', 'date'])

    return df


@st.cache_data(show_spinner=False)
def build_lifecycle(_df):
    """Build fund lifecycle table from raw events."""
    births = _df[_df['status'] == 'NUEVAS_INSCRIPCIONES']
    deaths = _df[_df['status'] == 'BAJAS']

    unique = births[births['N_Registro'].notna()].groupby('N_Registro').agg(
        Nombre=('Nombre', 'first'),
        Fecha_Alta=('date', 'min'),
        Gestora=('Gestora', 'first'),
        Depositaria=('Depositaria', 'first'),
    ).reset_index()

    death_dates = deaths[deaths['N_Registro'].notna()].groupby('N_Registro')['date'].min().reset_index()
    death_dates.columns = ['N_Registro', 'Fecha_Baja']

    lc = unique.merge(death_dates, on='N_Registro', how='left')
    lc['Vida_Anos'] = ((lc['Fecha_Baja'] - lc['Fecha_Alta']).dt.days / 365.25).round(1)

    # Clean: remove negative lives and >50yr outliers
    lc = lc[(lc['Vida_Anos'].isna()) | ((lc['Vida_Anos'] >= 0) & (lc['Vida_Anos'] <= 50))]

    lc['Activo'] = lc['Fecha_Baja'].isna()
    lc['Año_Alta'] = lc['Fecha_Alta'].dt.year
    lc['Año_Baja'] = lc['Fecha_Baja'].dt.year

    return lc


@st.cache_data(show_spinner=False)
def build_network_data(_df):
    """Build Gestora–Depositaria network from fund relationships."""
    valid = _df[_df['Gestora'].notna() & _df['Depositaria'].notna()].copy()

    # Shorten names for display
    def _short(name, max_len=35):
        name = str(name)
        # Remove common suffixes
        for suffix in [', S.G.I.I.C., S.A.', ', S.A., SGIIC', ', S.A., S.G.I.I.C.', 
                       ', SGIIC, S.A.', ', SGIIC', ', S.A.', ', S.A']:
            name = name.replace(suffix, '')
        return name[:max_len] + '…' if len(name) > max_len else name

    # Edge data: each unique fund is one edge
    edges = valid.drop_duplicates(subset=['N_Registro']).groupby(
        ['Gestora', 'Depositaria']
    ).agg(
        weight=('N_Registro', 'count'),
        funds=('Nombre', lambda x: list(x)[:5])
    ).reset_index()

    edges['Gestora_short'] = edges['Gestora'].apply(_short)
    edges['Depositaria_short'] = edges['Depositaria'].apply(_short)

    # Node sizes
    gestora_sizes = edges.groupby('Gestora_short')['weight'].sum().to_dict()
    depositaria_sizes = edges.groupby('Depositaria_short')['weight'].sum().to_dict()

    return edges, gestora_sizes, depositaria_sizes


# ─────────────────────────────────────────────────────────────────────────────
# LOAD
# ─────────────────────────────────────────────────────────────────────────────

with st.spinner('Cargando datos CNMV…'):
    df = load_data()
    lifecycle = build_lifecycle(df)
    net_edges, gestora_sizes, depositaria_sizes = build_network_data(df)

births_df = df[df['status'] == 'NUEVAS_INSCRIPCIONES']
deaths_df = df[df['status'] == 'BAJAS']
total_births = len(births_df)
total_deaths = len(deaths_df)
active_count = lifecycle['Activo'].sum()
mortality_pct = total_deaths / total_births * 100 if total_births > 0 else 0
date_range_str = f"{df['date'].min().strftime('%b %Y')} — {df['date'].max().strftime('%b %Y')}"


# ─────────────────────────────────────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────────────────────────────────────

st.markdown(f"""
<div style="margin-bottom: 0.5rem;">
    <h1 style="margin-bottom: 0.2rem;">Observatorio de Fondos CNMV</h1>
    <p style="color: {COLORS['text_muted']}; font-size: 0.95rem; margin: 0;">
        Sesgo de supervivencia en la industria española de fondos de inversión · {date_range_str}
    </p>
</div>
""", unsafe_allow_html=True)

# Hero metrics row
c1, c2, c3, c4, c5 = st.columns(5)
with c1:
    st.metric("Registrados", f"{total_births:,}", f"{df['Gestora'].nunique()} gestoras")
with c2:
    st.metric("Liquidados", f"{total_deaths:,}", f"{mortality_pct:.0f}% mortalidad")
with c3:
    st.metric("Activos hoy", f"{active_count:,}", f"{active_count/total_births*100:.0f}% supervivencia")
with c4:
    med_life = lifecycle[lifecycle['Vida_Anos'].notna()]['Vida_Anos'].median()
    st.metric("Vida mediana", f"{med_life:.1f} años", "fondos liquidados")
with c5:
    st.metric("Depositarias", f"{df['Depositaria'].nunique()}", f"{len(net_edges)} vínculos")


# ─────────────────────────────────────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────────────────────────────────────

tab_network, tab_survival, tab_temporal, tab_explorer = st.tabs([
    "RED FINANCIERA", "SUPERVIVENCIA", "EVOLUCIÓN", "EXPLORADOR"
])


# ═════════════════════════════════════════════════════════════════════════════
# TAB 1 — NETWORK
# ═════════════════════════════════════════════════════════════════════════════

with tab_network:
    st.markdown("## Red Gestora — Depositaria")
    st.markdown(f"""
    <p style="color: {COLORS['text_muted']}; margin-top: -0.8rem; margin-bottom: 1.5rem;">
        Cada arista conecta una gestora con la depositaria que custodia sus fondos. 
        El grosor indica el número de fondos en esa relación. Los clusters revelan los ecosistemas financieros españoles.
    </p>
    """, unsafe_allow_html=True)

    # Controls
    nc1, nc2, nc3 = st.columns([1, 1, 2])
    with nc1:
        min_edge_weight = st.slider("Mín. fondos por vínculo", 1, 30, 3,
                                     help="Filtra relaciones con pocos fondos para simplificar el grafo")
    with nc2:
        layout_algo = st.selectbox("Layout", ['spring', 'kamada_kawai'], index=0)

    # Build networkx graph
    filtered_edges = net_edges[net_edges['weight'] >= min_edge_weight]

    G = nx.Graph()
    for _, row in filtered_edges.iterrows():
        g_node = f"G|{row['Gestora_short']}"
        d_node = f"D|{row['Depositaria_short']}"
        G.add_node(g_node, node_type='gestora', full_name=row['Gestora'],
                   size=gestora_sizes.get(row['Gestora_short'], 1))
        G.add_node(d_node, node_type='depositaria', full_name=row['Depositaria'],
                   size=depositaria_sizes.get(row['Depositaria_short'], 1))
        G.add_edge(g_node, d_node, weight=row['weight'],
                   funds=', '.join(row['funds'][:3]))

    if len(G.nodes()) > 0:
        # Layout
        if layout_algo == 'spring':
            pos = nx.spring_layout(G, k=2.5/np.sqrt(len(G.nodes())), iterations=80,
                                   weight='weight', seed=42)
        else:
            pos = nx.kamada_kawai_layout(G, weight='weight')

        # Separate node types
        gestora_nodes = [n for n, d in G.nodes(data=True) if d['node_type'] == 'gestora']
        dep_nodes = [n for n, d in G.nodes(data=True) if d['node_type'] == 'depositaria']

        # Build edge traces
        edge_x, edge_y = [], []
        edge_weights = []
        for u, v, d in G.edges(data=True):
            x0, y0 = pos[u]
            x1, y1 = pos[v]
            edge_x += [x0, x1, None]
            edge_y += [y0, y1, None]
            edge_weights.append(d['weight'])

        # Create multiple edge traces for varying width
        fig_net = go.Figure()

        # Draw edges with opacity based on weight
        max_w = max(edge_weights) if edge_weights else 1
        for u, v, d in G.edges(data=True):
            x0, y0 = pos[u]
            x1, y1 = pos[v]
            w = d['weight']
            norm_w = w / max_w
            fig_net.add_trace(go.Scatter(
                x=[x0, x1], y=[y0, y1],
                mode='lines',
                line=dict(
                    width=max(0.5, norm_w * 8),
                    color=f'rgba(226,164,78,{0.08 + norm_w * 0.35})'
                ),
                hoverinfo='text',
                text=f"{u.split('|')[1]} ↔ {v.split('|')[1]}<br>{w} fondos",
                showlegend=False
            ))

        # Gestora nodes
        g_x = [pos[n][0] for n in gestora_nodes]
        g_y = [pos[n][1] for n in gestora_nodes]
        g_sizes = [max(8, min(50, G.nodes[n]['size'] * 0.5)) for n in gestora_nodes]
        g_text = [f"<b>{n.split('|')[1]}</b><br>{G.nodes[n]['size']} fondos<br>Conexiones: {G.degree(n)}"
                  for n in gestora_nodes]
        g_labels = [n.split('|')[1] if G.nodes[n]['size'] > 20 else '' for n in gestora_nodes]

        fig_net.add_trace(go.Scatter(
            x=g_x, y=g_y,
            mode='markers+text',
            marker=dict(
                size=g_sizes,
                color=COLORS['accent'],
                line=dict(width=1.5, color='rgba(226,164,78,0.4)'),
                opacity=0.9,
            ),
            text=g_labels,
            textposition='top center',
            textfont=dict(size=8, color=COLORS['text_muted']),
            hovertext=g_text,
            hoverinfo='text',
            name='Gestoras'
        ))

        # Depositaria nodes
        d_x = [pos[n][0] for n in dep_nodes]
        d_y = [pos[n][1] for n in dep_nodes]
        d_sizes = [max(10, min(55, G.nodes[n]['size'] * 0.4)) for n in dep_nodes]
        d_text = [f"<b>{n.split('|')[1]}</b><br>{G.nodes[n]['size']} fondos custodiados<br>Conexiones: {G.degree(n)}"
                  for n in dep_nodes]
        d_labels = [n.split('|')[1] if G.nodes[n]['size'] > 30 else '' for n in dep_nodes]

        fig_net.add_trace(go.Scatter(
            x=d_x, y=d_y,
            mode='markers+text',
            marker=dict(
                size=d_sizes,
                color=COLORS['accent3'],
                symbol='diamond',
                line=dict(width=1.5, color='rgba(124,152,133,0.4)'),
                opacity=0.9,
            ),
            text=d_labels,
            textposition='bottom center',
            textfont=dict(size=8, color=COLORS['text_muted']),
            hovertext=d_text,
            hoverinfo='text',
            name='Depositarias'
        ))

        fig_net.update_layout(
            plot_bgcolor=COLORS['bg'],
            paper_bgcolor=COLORS['bg'],
            font=dict(family='DM Sans, sans-serif', color=COLORS['text'], size=12),
            hoverlabel=dict(
                bgcolor='rgba(20,20,20,0.95)', font_size=12,
                font_family='DM Sans, sans-serif', bordercolor='rgba(255,255,255,0.1)'
            ),
            margin=dict(t=40, b=20, l=20, r=20),
            height=700,
            showlegend=True,
            legend=dict(
                orientation='h', yanchor='top', y=1.05, xanchor='center', x=0.5,
                font=dict(size=12, color=COLORS['text']),
                bgcolor='rgba(0,0,0,0)',
            ),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, visible=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, visible=False),
            title=None,
        )

        st.plotly_chart(fig_net, use_container_width=True)

        # Network stats
        st.markdown("---")
        st.markdown("### Métricas de Red")
        nc1, nc2, nc3, nc4 = st.columns(4)

        with nc1:
            st.metric("Nodos", f"{len(G.nodes())}", f"{len(gestora_nodes)} gestoras · {len(dep_nodes)} depositarias")
        with nc2:
            st.metric("Vínculos", f"{len(G.edges())}", f"mín. {min_edge_weight} fondos")
        with nc3:
            if nx.is_connected(G):
                st.metric("Componentes", "1", "grafo conexo")
            else:
                n_comp = nx.number_connected_components(G)
                st.metric("Componentes", f"{n_comp}", "subgrafos aislados")
        with nc4:
            density = nx.density(G)
            st.metric("Densidad", f"{density:.3f}", "ratio de conexiones")

        # Top centrality
        st.markdown("### Nodos sistémicos")
        st.markdown(f"<p style='color:{COLORS['text_muted']}; margin-top:-0.7rem;'>Entidades con mayor centralidad de intermediación — potenciales puntos de fragilidad sistémica.</p>", unsafe_allow_html=True)

        betw = nx.betweenness_centrality(G, weight='weight')
        deg = nx.degree_centrality(G)

        top_betw = sorted(betw.items(), key=lambda x: -x[1])[:10]
        centrality_df = pd.DataFrame([{
            'Entidad': n.split('|')[1],
            'Tipo': 'Gestora' if n.startswith('G|') else 'Depositaria',
            'Betweenness': round(v, 4),
            'Degree': round(deg[n], 4),
            'Fondos': G.nodes[n]['size'],
            'Conexiones': G.degree(n)
        } for n, v in top_betw])

        st.dataframe(centrality_df, use_container_width=True, hide_index=True,
                     column_config={
                         'Betweenness': st.column_config.NumberColumn(format='%.4f'),
                         'Degree': st.column_config.NumberColumn(format='%.4f'),
                     })

    else:
        st.info("No hay suficientes datos para el grafo con este filtro. Reduce el mínimo de fondos.")


# ═════════════════════════════════════════════════════════════════════════════
# TAB 2 — SURVIVAL ANALYSIS
# ═════════════════════════════════════════════════════════════════════════════

with tab_survival:
    st.markdown("## Análisis de Supervivencia")
    st.markdown(f"""
    <p style="color: {COLORS['text_muted']}; margin-top: -0.8rem; margin-bottom: 1.5rem;">
        Curvas Kaplan-Meier por cohorte de lanzamiento. ¿Qué probabilidad tiene un fondo de sobrevivir 5, 10 o 15 años?
    </p>
    """, unsafe_allow_html=True)

    # ── Kaplan-Meier by cohort ──
    @st.cache_data
    def compute_km_curves(_lifecycle):
        """Compute Kaplan-Meier survival curves by 5-year cohort."""
        now = pd.Timestamp.now()
        lc = _lifecycle.copy()
        lc['duration'] = np.where(
            lc['Fecha_Baja'].notna(),
            (lc['Fecha_Baja'] - lc['Fecha_Alta']).dt.days / 365.25,
            (now - lc['Fecha_Alta']).dt.days / 365.25
        )
        lc['event'] = lc['Fecha_Baja'].notna().astype(int)
        lc['duration'] = lc['duration'].clip(lower=0)

        # Cohorts
        bins = [2003, 2008, 2013, 2018, 2025]
        labels = ['2004–2008', '2009–2013', '2014–2018', '2019–2025']
        lc['cohort'] = pd.cut(lc['Año_Alta'], bins=bins, labels=labels, right=True)

        curves = {}
        for cohort in labels:
            subset = lc[lc['cohort'] == cohort].copy()
            if len(subset) < 10:
                continue

            # Sort by duration
            times = sorted(subset['duration'].unique())
            n_at_risk = len(subset)
            survival = 1.0
            curve_t = [0]
            curve_s = [1.0]

            for t in times:
                events_at_t = len(subset[(subset['duration'] == t) & (subset['event'] == 1)])
                censored_at_t = len(subset[(subset['duration'] == t) & (subset['event'] == 0)])

                if n_at_risk > 0 and events_at_t > 0:
                    survival *= (1 - events_at_t / n_at_risk)

                curve_t.append(t)
                curve_s.append(survival)

                n_at_risk -= (events_at_t + censored_at_t)

            curves[cohort] = (curve_t, curve_s, len(subset))

        return curves

    km_curves = compute_km_curves(lifecycle)

    cohort_colors = {
        '2004–2008': COLORS['accent2'],
        '2009–2013': COLORS['accent'],
        '2014–2018': COLORS['blue'],
        '2019–2025': COLORS['accent3'],
    }

    fig_km = go.Figure()
    for cohort, (times, surv, n) in km_curves.items():
        color = cohort_colors.get(cohort, '#888')
        fig_km.add_trace(go.Scatter(
            x=times, y=[s * 100 for s in surv],
            mode='lines',
            name=f'{cohort} (n={n})',
            line=dict(color=color, width=2.5, shape='hv'),
            hovertemplate='<b>%{x:.1f} años</b><br>Supervivencia: %{y:.1f}%<extra>' + cohort + '</extra>'
        ))

    # Reference lines
    for pct in [50, 25]:
        fig_km.add_hline(y=pct, line_dash='dot',
                         line_color='rgba(255,255,255,0.1)',
                         annotation_text=f'{pct}%',
                         annotation_font_color=COLORS['text_muted'],
                         annotation_font_size=10)

    fig_km.update_layout(
        **PLOTLY_LAYOUT,
        height=500,
        title=dict(text='<b>Curvas de Supervivencia por Cohorte</b>',
                   font=dict(size=16, color=COLORS['text']), x=0, xanchor='left'),
        xaxis=dict(title='Años desde registro', range=[0, 21],
                   gridcolor='rgba(255,255,255,0.04)', tickfont=dict(color=COLORS['text_muted'])),
        yaxis=dict(title='Probabilidad de supervivencia (%)', range=[0, 105],
                   gridcolor='rgba(255,255,255,0.04)', tickfont=dict(color=COLORS['text_muted'])),
        legend=dict(
            bgcolor='rgba(0,0,0,0)',
            font=dict(color=COLORS['text'], size=11),
            yanchor='top', y=0.98, xanchor='right', x=0.98
        )
    )

    st.plotly_chart(fig_km, use_container_width=True)

    # ── Cohort stats table ──
    st.markdown("### Tabla de cohortes")

    cohort_stats = []
    now = pd.Timestamp.now()
    for cohort, (times, surv, n) in km_curves.items():
        # Find survival at specific timepoints
        def surv_at(target_yr):
            for i in range(len(times)-1, -1, -1):
                if times[i] <= target_yr:
                    return surv[i] * 100
            return 100.0

        subset = lifecycle[
            lifecycle['Año_Alta'].between(
                int(cohort.split('–')[0]),
                int(cohort.split('–')[1])
            )
        ]
        active_n = subset['Activo'].sum()
        dead_n = (~subset['Activo']).sum()
        med_vida = subset[subset['Vida_Anos'].notna()]['Vida_Anos'].median()

        cohort_stats.append({
            'Cohorte': cohort,
            'Fondos': n,
            'Activos': int(active_n),
            'Liquidados': int(dead_n),
            'Mortalidad %': round(dead_n / n * 100, 1) if n > 0 else 0,
            'Sup. 3 años %': round(surv_at(3), 1),
            'Sup. 5 años %': round(surv_at(5), 1),
            'Sup. 10 años %': round(surv_at(10), 1),
            'Vida mediana': round(med_vida, 1) if pd.notna(med_vida) else None,
        })

    st.dataframe(pd.DataFrame(cohort_stats), use_container_width=True, hide_index=True,
                 column_config={
                     'Mortalidad %': st.column_config.ProgressColumn(format='%.1f%%', min_value=0, max_value=100),
                     'Sup. 3 años %': st.column_config.ProgressColumn(format='%.1f%%', min_value=0, max_value=100),
                     'Sup. 5 años %': st.column_config.ProgressColumn(format='%.1f%%', min_value=0, max_value=100),
                     'Sup. 10 años %': st.column_config.ProgressColumn(format='%.1f%%', min_value=0, max_value=100),
                 })

    # ── Life distribution histogram ──
    st.markdown("---")
    st.markdown("### Distribución de vida de fondos liquidados")

    dead_funds = lifecycle[lifecycle['Vida_Anos'].notna() & (~lifecycle['Activo'])]

    fig_hist = go.Figure()
    fig_hist.add_trace(go.Histogram(
        x=dead_funds['Vida_Anos'],
        nbinsx=40,
        marker=dict(
            color=COLORS['accent2'],
            line=dict(color='rgba(0,0,0,0.3)', width=0.5),
            opacity=0.85,
        ),
        hovertemplate='<b>%{x:.1f} años</b><br>%{y} fondos<extra></extra>'
    ))

    # Add median line
    median_val = dead_funds['Vida_Anos'].median()
    fig_hist.add_vline(x=median_val, line_dash='dash', line_color=COLORS['accent'],
                       annotation_text=f'Mediana: {median_val:.1f} años',
                       annotation_font_color=COLORS['accent'],
                       annotation_font_size=11)

    fig_hist.update_layout(
        **PLOTLY_LAYOUT,
        height=400,
        title=dict(text='<b>¿Cuánto viven los fondos?</b>',
                   font=dict(size=16, color=COLORS['text']), x=0, xanchor='left'),
        xaxis=dict(title='Años de vida', gridcolor='rgba(255,255,255,0.04)',
                   tickfont=dict(color=COLORS['text_muted'])),
        yaxis=dict(title='Número de fondos', gridcolor='rgba(255,255,255,0.04)',
                   tickfont=dict(color=COLORS['text_muted'])),
        bargap=0.05,
    )

    st.plotly_chart(fig_hist, use_container_width=True)

    # Key insight metrics
    sc1, sc2, sc3, sc4 = st.columns(4)
    with sc1:
        infant = (dead_funds['Vida_Anos'] < 1).sum() / len(dead_funds) * 100
        st.metric("Mortalidad infantil", f"{infant:.0f}%", "mueren antes del 1er año")
    with sc2:
        y3 = (dead_funds['Vida_Anos'] < 3).sum() / len(dead_funds) * 100
        st.metric("< 3 años", f"{y3:.0f}%", "de los liquidados")
    with sc3:
        y5 = (dead_funds['Vida_Anos'] < 5).sum() / len(dead_funds) * 100
        st.metric("< 5 años", f"{y5:.0f}%", "de los liquidados")
    with sc4:
        q75 = dead_funds['Vida_Anos'].quantile(0.75)
        st.metric("Percentil 75", f"{q75:.1f} años", "vida máxima del 75%")


# ═════════════════════════════════════════════════════════════════════════════
# TAB 3 — TEMPORAL EVOLUTION
# ═════════════════════════════════════════════════════════════════════════════

with tab_temporal:
    st.markdown("## Evolución temporal")
    st.markdown(f"""
    <p style="color: {COLORS['text_muted']}; margin-top: -0.8rem; margin-bottom: 1.5rem;">
        Altas y bajas de fondos a lo largo de dos décadas. Las zonas sombreadas marcan períodos de crisis.
    </p>
    """, unsafe_allow_html=True)

    tc1, tc2 = st.columns([1, 3])
    with tc1:
        granularity = st.selectbox("Granularidad", ['Anual', 'Trimestral', 'Mensual'], index=0)

    # Aggregate
    if granularity == 'Anual':
        ts = df.groupby(['year', 'status']).size().unstack(fill_value=0)
        ts.index = pd.to_datetime(ts.index.astype(str) + '-07-01')
    elif granularity == 'Trimestral':
        df_q = df.copy()
        df_q['q'] = df_q['date'].dt.to_period('Q')
        ts = df_q.groupby(['q', 'status']).size().unstack(fill_value=0)
        ts.index = ts.index.to_timestamp()
    else:
        df_m = df.copy()
        df_m['m'] = df_m['date'].dt.to_period('M')
        ts = df_m.groupby(['m', 'status']).size().unstack(fill_value=0)
        ts.index = ts.index.to_timestamp()

    ts = ts.rename(columns={'NUEVAS_INSCRIPCIONES': 'Altas', 'BAJAS': 'Bajas'})
    if 'Altas' not in ts.columns:
        ts['Altas'] = 0
    if 'Bajas' not in ts.columns:
        ts['Bajas'] = 0

    ts['Neto'] = ts['Altas'] - ts['Bajas']
    ts['Acumulado'] = ts['Neto'].cumsum()

    # Main chart: dual axis
    fig_ts = make_subplots(specs=[[{"secondary_y": True}]])

    fig_ts.add_trace(go.Bar(
        x=ts.index, y=ts['Altas'],
        name='Altas',
        marker=dict(color=COLORS['green'], opacity=0.85,
                    line=dict(width=0)),
        hovertemplate='<b>%{x|%Y-%m}</b><br>Altas: %{y}<extra></extra>'
    ), secondary_y=False)

    fig_ts.add_trace(go.Bar(
        x=ts.index, y=-ts['Bajas'],
        name='Bajas',
        marker=dict(color=COLORS['red'], opacity=0.85,
                    line=dict(width=0)),
        hovertemplate='<b>%{x|%Y-%m}</b><br>Bajas: %{y}<extra></extra>'
    ), secondary_y=False)

    fig_ts.add_trace(go.Scatter(
        x=ts.index, y=ts['Acumulado'],
        name='Acumulado neto',
        line=dict(color=COLORS['accent'], width=2.5),
        mode='lines',
        hovertemplate='<b>%{x|%Y-%m}</b><br>Acumulado: %{y:+,}<extra></extra>'
    ), secondary_y=True)

    # Crisis overlays
    crises = [
        ("Crisis financiera", "2008-01-01", "2009-12-31"),
        ("Crisis deuda EU", "2011-06-01", "2012-12-31"),
        ("COVID-19", "2020-02-01", "2020-09-30"),
    ]
    for label, s, e in crises:
        fig_ts.add_vrect(x0=s, x1=e, fillcolor="rgba(199,93,93,0.07)",
                         layer="below", line_width=0)
        fig_ts.add_annotation(
            x=pd.to_datetime(s) + (pd.to_datetime(e) - pd.to_datetime(s))/2,
            y=1.02, yref='paper', text=label, showarrow=False,
            font=dict(size=9, color='rgba(199,93,93,0.5)'))

    fig_ts.add_hline(y=0, line_color='rgba(255,255,255,0.1)', line_width=1)

    fig_ts.update_layout(
        **PLOTLY_LAYOUT,
        height=550,
        barmode='relative',
        title=dict(text='<b>Altas vs Bajas · Balance acumulado</b>',
                   font=dict(size=16, color=COLORS['text']), x=0, xanchor='left'),
        legend=dict(
            orientation='h', yanchor='top', y=1.12, xanchor='center', x=0.5,
            bgcolor='rgba(0,0,0,0)',
            font=dict(color=COLORS['text'], size=11),
        ),
        xaxis=dict(gridcolor='rgba(255,255,255,0.04)', tickfont=dict(color=COLORS['text_muted'])),
        yaxis=dict(title='Fondos por período', gridcolor='rgba(255,255,255,0.04)',
                   tickfont=dict(color=COLORS['text_muted'])),
        yaxis2=dict(title='Acumulado neto', gridcolor='rgba(255,255,255,0.04)',
                    tickfont=dict(color=COLORS['text_muted']),
                    showgrid=False),
    )

    st.plotly_chart(fig_ts, use_container_width=True)

    # Period stats
    st.markdown("---")
    mc1, mc2, mc3, mc4 = st.columns(4)
    with mc1:
        worst_idx = ts['Neto'].idxmin()
        st.metric("Peor período", f"{ts.loc[worst_idx, 'Neto']:+.0f}",
                  worst_idx.strftime('%Y-%m'))
    with mc2:
        best_idx = ts['Neto'].idxmax()
        st.metric("Mejor período", f"{ts.loc[best_idx, 'Neto']:+.0f}",
                  best_idx.strftime('%Y-%m'))
    with mc3:
        st.metric("Total altas", f"{ts['Altas'].sum():,.0f}")
    with mc4:
        st.metric("Total bajas", f"{ts['Bajas'].sum():,.0f}")

    # ── Concentration / HHI over time ──
    st.markdown("---")
    st.markdown("### Concentración del mercado (HHI)")
    st.markdown(f"<p style='color:{COLORS['text_muted']}; margin-top:-0.7rem;'>Índice Herfindahl-Hirschman de gestoras por año. Valores &gt; 1500 indican concentración moderada, &gt; 2500 alta.</p>", unsafe_allow_html=True)

    @st.cache_data
    def compute_hhi_over_time(_lifecycle):
        results = []
        for year in range(2005, 2026):
            # Funds active in this year
            active = _lifecycle[
                (_lifecycle['Fecha_Alta'].dt.year <= year) &
                ((_lifecycle['Fecha_Baja'].isna()) | (_lifecycle['Fecha_Baja'].dt.year >= year))
            ]
            if len(active) < 10:
                continue
            shares = active.groupby('Gestora').size() / len(active) * 100
            hhi = (shares ** 2).sum()
            top3 = shares.nlargest(3).sum()
            n_gestoras = len(shares)
            results.append({'Año': year, 'HHI': round(hhi, 0), 'Top 3 %': round(top3, 1),
                           'Gestoras activas': n_gestoras})
        return pd.DataFrame(results)

    hhi_df = compute_hhi_over_time(lifecycle)

    fig_hhi = make_subplots(specs=[[{"secondary_y": True}]])

    fig_hhi.add_trace(go.Bar(
        x=hhi_df['Año'], y=hhi_df['HHI'],
        name='HHI',
        marker=dict(
            color=[COLORS['accent'] if v > 1500 else COLORS['blue'] for v in hhi_df['HHI']],
            opacity=0.8
        ),
        hovertemplate='<b>%{x}</b><br>HHI: %{y:.0f}<extra></extra>'
    ), secondary_y=False)

    fig_hhi.add_trace(go.Scatter(
        x=hhi_df['Año'], y=hhi_df['Gestoras activas'],
        name='Gestoras activas',
        line=dict(color=COLORS['accent3'], width=2),
        mode='lines+markers',
        marker=dict(size=5),
        hovertemplate='<b>%{x}</b><br>%{y} gestoras<extra></extra>'
    ), secondary_y=True)

    # HHI threshold lines
    fig_hhi.add_hline(y=1500, line_dash='dot', line_color='rgba(255,255,255,0.15)',
                      annotation_text='Concentración moderada',
                      annotation_font_color=COLORS['text_muted'],
                      annotation_font_size=9, secondary_y=False)
    fig_hhi.add_hline(y=2500, line_dash='dot', line_color='rgba(255,255,255,0.15)',
                      annotation_text='Concentración alta',
                      annotation_font_color=COLORS['text_muted'],
                      annotation_font_size=9, secondary_y=False)

    fig_hhi.update_layout(
        **PLOTLY_LAYOUT,
        height=400,
        title=dict(text='<b>Concentración de gestoras (HHI) y número de actores</b>',
                   font=dict(size=16, color=COLORS['text']), x=0, xanchor='left'),
        legend=dict(
            orientation='h', yanchor='top', y=1.1, xanchor='center', x=0.5,
            bgcolor='rgba(0,0,0,0)', font=dict(color=COLORS['text'], size=11)),
        xaxis=dict(gridcolor='rgba(255,255,255,0.04)', tickfont=dict(color=COLORS['text_muted']),
                   dtick=2),
        yaxis=dict(title='HHI', gridcolor='rgba(255,255,255,0.04)',
                   tickfont=dict(color=COLORS['text_muted'])),
        yaxis2=dict(title='Gestoras activas', showgrid=False,
                    tickfont=dict(color=COLORS['text_muted'])),
    )

    st.plotly_chart(fig_hhi, use_container_width=True)


# ═════════════════════════════════════════════════════════════════════════════
# TAB 4 — EXPLORER
# ═════════════════════════════════════════════════════════════════════════════

with tab_explorer:
    st.markdown("## Explorador de fondos")

    # Filters
    fc1, fc2, fc3 = st.columns([2, 1, 1])

    with fc1:
        search = st.text_input("Buscar por nombre o Nº registro",
                               placeholder="Ej: BBVA, Santander, 3043…")
    with fc2:
        status_filter = st.selectbox("Estado", ['Todos', 'Activos', 'Liquidados'])
    with fc3:
        gestora_list = ['Todas'] + sorted(lifecycle['Gestora'].dropna().unique().tolist())
        gestora_filter = st.selectbox("Gestora", gestora_list)

    # Apply filters
    result = lifecycle.copy()

    if search:
        mask = (
            result['Nombre'].str.contains(search.upper(), case=False, na=False) |
            result['N_Registro'].astype(str).str.contains(search, na=False)
        )
        result = result[mask]

    if status_filter == 'Activos':
        result = result[result['Activo']]
    elif status_filter == 'Liquidados':
        result = result[~result['Activo']]

    if gestora_filter != 'Todas':
        result = result[result['Gestora'] == gestora_filter]

    # Stats
    n_total = len(result)
    n_active = result['Activo'].sum()
    n_dead = n_total - n_active
    avg_life = result[result['Vida_Anos'].notna()]['Vida_Anos'].mean()

    ec1, ec2, ec3, ec4 = st.columns(4)
    with ec1:
        st.metric("Encontrados", f"{n_total:,}")
    with ec2:
        st.metric("Activos", f"{int(n_active):,}")
    with ec3:
        st.metric("Liquidados", f"{int(n_dead):,}")
    with ec4:
        st.metric("Vida media", f"{avg_life:.1f} años" if pd.notna(avg_life) else "—")

    if n_total > 0:
        display = result.copy()
        display['N_Registro'] = display['N_Registro'].astype(int)
        display = display.sort_values('Fecha_Alta', ascending=False)
        display['Estado'] = display['Activo'].map({True: '● Activo', False: '○ Liquidado'})
        display['Fecha_Alta_str'] = display['Fecha_Alta'].dt.strftime('%Y-%m-%d')
        display['Fecha_Baja_str'] = display['Fecha_Baja'].dt.strftime('%Y-%m-%d').fillna('—')

        show_cols = ['N_Registro', 'Nombre', 'Estado', 'Fecha_Alta_str', 'Fecha_Baja_str',
                     'Vida_Anos', 'Gestora', 'Depositaria']

        st.dataframe(
            display[show_cols],
            use_container_width=True,
            hide_index=True,
            height=500,
            column_config={
                'N_Registro': st.column_config.NumberColumn('Nº Reg', width='small'),
                'Nombre': st.column_config.TextColumn('Fondo', width='large'),
                'Estado': st.column_config.TextColumn('Estado', width='small'),
                'Fecha_Alta_str': st.column_config.TextColumn('Alta', width='small'),
                'Fecha_Baja_str': st.column_config.TextColumn('Baja', width='small'),
                'Vida_Anos': st.column_config.NumberColumn('Vida (años)', format='%.1f', width='small'),
                'Gestora': st.column_config.TextColumn('Gestora', width='medium'),
                'Depositaria': st.column_config.TextColumn('Depositaria', width='medium'),
            }
        )

        # Mortality by gestora for the current filter
        if n_total > 20:
            st.markdown("---")
            st.markdown("### Mortalidad por gestora")

            mort_by_g = result.groupby('Gestora').agg(
                Total=('N_Registro', 'count'),
                Liquidados=('Activo', lambda x: (~x).sum()),
                Vida_Media=('Vida_Anos', 'mean')
            ).round(1)
            mort_by_g['Mortalidad %'] = (mort_by_g['Liquidados'] / mort_by_g['Total'] * 100).round(1)
            mort_by_g = mort_by_g[mort_by_g['Total'] >= 3].sort_values('Total', ascending=False).head(15)

            fig_mort = go.Figure()
            fig_mort.add_trace(go.Bar(
                y=mort_by_g.index,
                x=mort_by_g['Total'],
                name='Total fondos',
                orientation='h',
                marker=dict(color=COLORS['blue'], opacity=0.4),
                hovertemplate='<b>%{y}</b><br>Total: %{x}<extra></extra>'
            ))
            fig_mort.add_trace(go.Bar(
                y=mort_by_g.index,
                x=mort_by_g['Liquidados'],
                name='Liquidados',
                orientation='h',
                marker=dict(color=COLORS['red'], opacity=0.8),
                hovertemplate='<b>%{y}</b><br>Liquidados: %{x}<extra></extra>'
            ))

            fig_mort.update_layout(
                **PLOTLY_LAYOUT,
                height=max(350, len(mort_by_g) * 30),
                barmode='overlay',
                title=dict(text='<b>Fondos totales vs liquidados por gestora</b>',
                           font=dict(size=14, color=COLORS['text']), x=0),
                yaxis=dict(autorange='reversed', tickfont=dict(size=10, color=COLORS['text_muted']),
                           gridcolor='rgba(255,255,255,0.04)'),
                xaxis=dict(title='Número de fondos', gridcolor='rgba(255,255,255,0.04)',
                           tickfont=dict(color=COLORS['text_muted'])),
                legend=dict(orientation='h', yanchor='top', y=1.08, xanchor='center', x=0.5,
                            bgcolor='rgba(0,0,0,0)', font=dict(color=COLORS['text'], size=11)),
            )
            st.plotly_chart(fig_mort, use_container_width=True)

    else:
        st.info("No se encontraron fondos con estos filtros.")


# ─────────────────────────────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────────────────────────────

st.markdown("---")
st.markdown(f"""
<div style="text-align: center; padding: 2rem 0 1rem;">
    <p style="color: {COLORS['text_muted']}; font-size: 0.85rem; margin: 0 0 0.5rem;">
        {total_deaths:,} fondos liquidados que ya no aparecen en los rankings publicados — eso es sesgo de supervivencia.
    </p>
    <p style="color: {COLORS['text_muted']}; font-size: 0.8rem; margin: 0;">
        <a href="https://twitter.com/Gsnchez" target="_blank" style="color: {COLORS['accent']}; text-decoration: none;">@Gsnchez</a> · 
        <a href="https://bquantfinance.com" target="_blank" style="color: {COLORS['accent']}; text-decoration: none;">bquantfinance.com</a> · 
        <a href="https://bquantfundlab.substack.com/" target="_blank" style="color: {COLORS['accent']}; text-decoration: none;">BQuant Fund Lab</a>
    </p>
</div>
""", unsafe_allow_html=True)
