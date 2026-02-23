import streamlit as st
import streamlit.components.v1 as components
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


_THREE_JS_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>CNMV Fund Network · 3D</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    background: #000;
    overflow: hidden;
    font-family: 'SF Mono', 'Fira Code', 'Consolas', monospace;
    color: #e8e4df;
  }
  canvas { display: block; }

  /* Tooltip */
  #tooltip {
    position: fixed;
    pointer-events: none;
    background: rgba(8,8,8,0.92);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 10px;
    padding: 14px 18px;
    font-size: 12px;
    line-height: 1.6;
    max-width: 320px;
    opacity: 0;
    transition: opacity 0.2s ease;
    backdrop-filter: blur(16px);
    z-index: 100;
    box-shadow: 0 12px 40px rgba(0,0,0,0.6);
  }
  #tooltip.visible { opacity: 1; }
  #tooltip .tt-name {
    font-size: 14px;
    font-weight: 600;
    margin-bottom: 4px;
    letter-spacing: 0.5px;
  }
  #tooltip .tt-type {
    font-size: 10px;
    text-transform: uppercase;
    letter-spacing: 2px;
    margin-bottom: 8px;
    opacity: 0.6;
  }
  #tooltip .tt-stat {
    font-size: 11px;
    opacity: 0.75;
  }
  .gestora-color { color: #e2a44e; }
  .depositaria-color { color: #6ec4a7; }

  /* HUD */
  #hud {
    position: fixed;
    top: 24px;
    left: 28px;
    z-index: 50;
  }
  #hud h1 {
    font-family: 'Georgia', serif;
    font-size: 22px;
    font-weight: 400;
    letter-spacing: 0.5px;
    color: #e8e4df;
    margin-bottom: 4px;
  }
  #hud .subtitle {
    font-size: 10px;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: rgba(255,255,255,0.3);
  }

  /* Legend */
  #legend {
    position: fixed;
    bottom: 28px;
    left: 28px;
    z-index: 50;
    display: flex;
    gap: 20px;
    font-size: 11px;
    letter-spacing: 0.5px;
  }
  .legend-item {
    display: flex;
    align-items: center;
    gap: 8px;
    opacity: 0.5;
  }
  .legend-dot {
    width: 10px;
    height: 10px;
    border-radius: 50%;
  }
  .legend-dot.gestora { background: #e2a44e; box-shadow: 0 0 12px #e2a44e88; }
  .legend-dot.depositaria { background: #6ec4a7; box-shadow: 0 0 12px #6ec4a788; }

  /* Stats */
  #stats {
    position: fixed;
    top: 24px;
    right: 28px;
    z-index: 50;
    text-align: right;
    font-size: 10px;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    color: rgba(255,255,255,0.25);
    line-height: 2;
  }
  #stats span { color: rgba(255,255,255,0.6); font-weight: 600; }

  /* Controls hint */
  #controls-hint {
    position: fixed;
    bottom: 28px;
    right: 28px;
    z-index: 50;
    font-size: 10px;
    letter-spacing: 1px;
    color: rgba(255,255,255,0.15);
    text-align: right;
    line-height: 2;
  }
</style>
</head>
<body>

<div id="tooltip">
  <div class="tt-name"></div>
  <div class="tt-type"></div>
  <div class="tt-stat"></div>
</div>

<div id="hud">
  <h1>Red Financiera CNMV</h1>
  <div class="subtitle">Gestoras · Depositarias · 2004 — 2025</div>
</div>

<div id="stats">
  Nodos <span id="stat-nodes">0</span><br>
  Vínculos <span id="stat-edges">0</span><br>
  Fondos <span id="stat-funds">0</span>
</div>

<div id="legend">
  <div class="legend-item"><div class="legend-dot gestora"></div> Gestoras</div>
  <div class="legend-item"><div class="legend-dot depositaria"></div> Depositarias</div>
</div>

<div id="controls-hint">
  Arrastrar para rotar<br>
  Scroll para zoom<br>
  Click en nodo para fijar
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
// ═══════════════════════════════════════════════════════════════════════
// DATA
// ═══════════════════════════════════════════════════════════════════════

const GRAPH_DATA = __GRAPH_DATA_PLACEHOLDER__;

// ═══════════════════════════════════════════════════════════════════════
// SETUP
// ═══════════════════════════════════════════════════════════════════════

const W = window.innerWidth, H = window.innerHeight;

const scene = new THREE.Scene();
scene.fog = new THREE.FogExp2(0x000000, 0.0012);

const camera = new THREE.PerspectiveCamera(60, W / H, 1, 10000);
camera.position.set(0, 0, 500);

const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
renderer.setSize(W, H);
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.2;
document.body.appendChild(renderer.domElement);

// ═══════════════════════════════════════════════════════════════════════
// GLOW TEXTURE GENERATOR
// ═══════════════════════════════════════════════════════════════════════

function createGlowTexture(color, size) {
  const c = document.createElement('canvas');
  c.width = c.height = size;
  const ctx = c.getContext('2d');
  const g = ctx.createRadialGradient(size/2, size/2, 0, size/2, size/2, size/2);
  g.addColorStop(0.0, color);
  g.addColorStop(0.15, color);
  g.addColorStop(0.4, color.replace('1)', '0.3)'));
  g.addColorStop(0.7, color.replace('1)', '0.06)'));
  g.addColorStop(1.0, 'rgba(0,0,0,0)');
  ctx.fillStyle = g;
  ctx.fillRect(0, 0, size, size);
  const tex = new THREE.CanvasTexture(c);
  tex.needsUpdate = true;
  return tex;
}

const glowTexGestora = createGlowTexture('rgba(226,164,78,1)', 128);
const glowTexDepositaria = createGlowTexture('rgba(110,196,167,1)', 128);
const glowTexWhite = createGlowTexture('rgba(255,255,255,1)', 64);

// ═══════════════════════════════════════════════════════════════════════
// BUILD GRAPH
// ═══════════════════════════════════════════════════════════════════════

const nodes = GRAPH_DATA.nodes;
const edges = GRAPH_DATA.edges;

// Create node map
const nodeMap = {};
nodes.forEach((n, i) => {
  nodeMap[n.id] = i;
  // Random initial position in sphere
  const phi = Math.random() * Math.PI * 2;
  const theta = Math.acos(2 * Math.random() - 1);
  const r = 150 + Math.random() * 200;
  n.x = r * Math.sin(theta) * Math.cos(phi);
  n.y = r * Math.sin(theta) * Math.sin(phi);
  n.z = r * Math.cos(theta);
  n.vx = 0; n.vy = 0; n.vz = 0;
  n.connections = 0;
});

// Count connections
edges.forEach(e => {
  const si = nodeMap[e.source];
  const ti = nodeMap[e.target];
  if (si !== undefined) nodes[si].connections += e.weight;
  if (ti !== undefined) nodes[ti].connections += e.weight;
});

const maxWeight = Math.max(...nodes.map(n => n.weight));
const totalFunds = edges.reduce((s, e) => s + e.weight, 0);

// Update HUD
document.getElementById('stat-nodes').textContent = nodes.length;
document.getElementById('stat-edges').textContent = edges.length;
document.getElementById('stat-funds').textContent = totalFunds;

// ═══════════════════════════════════════════════════════════════════════
// 3D FORCE SIMULATION
// ═══════════════════════════════════════════════════════════════════════

function simulate(iterations) {
  const alpha = 0.3;
  const repulsion = 8000;
  const attraction = 0.0004;
  const damping = 0.85;
  const centerGravity = 0.002;

  for (let iter = 0; iter < iterations; iter++) {
    // Repulsion between all nodes
    for (let i = 0; i < nodes.length; i++) {
      for (let j = i + 1; j < nodes.length; j++) {
        const dx = nodes[i].x - nodes[j].x;
        const dy = nodes[i].y - nodes[j].y;
        const dz = nodes[i].z - nodes[j].z;
        let dist = Math.sqrt(dx*dx + dy*dy + dz*dz) + 1;
        const force = repulsion / (dist * dist);
        const fx = dx / dist * force;
        const fy = dy / dist * force;
        const fz = dz / dist * force;
        nodes[i].vx += fx * alpha;
        nodes[i].vy += fy * alpha;
        nodes[i].vz += fz * alpha;
        nodes[j].vx -= fx * alpha;
        nodes[j].vy -= fy * alpha;
        nodes[j].vz -= fz * alpha;
      }
    }

    // Attraction along edges
    edges.forEach(e => {
      const si = nodeMap[e.source];
      const ti = nodeMap[e.target];
      if (si === undefined || ti === undefined) return;
      const s = nodes[si], t = nodes[ti];
      const dx = t.x - s.x;
      const dy = t.y - s.y;
      const dz = t.z - s.z;
      const dist = Math.sqrt(dx*dx + dy*dy + dz*dz) + 1;
      const force = dist * attraction * Math.sqrt(e.weight);
      const fx = dx / dist * force;
      const fy = dy / dist * force;
      const fz = dz / dist * force;
      s.vx += fx * alpha;
      s.vy += fy * alpha;
      s.vz += fz * alpha;
      t.vx -= fx * alpha;
      t.vy -= fy * alpha;
      t.vz -= fz * alpha;
    });

    // Center gravity + apply velocities
    for (let i = 0; i < nodes.length; i++) {
      nodes[i].vx -= nodes[i].x * centerGravity;
      nodes[i].vy -= nodes[i].y * centerGravity;
      nodes[i].vz -= nodes[i].z * centerGravity;
      nodes[i].vx *= damping;
      nodes[i].vy *= damping;
      nodes[i].vz *= damping;
      nodes[i].x += nodes[i].vx;
      nodes[i].y += nodes[i].vy;
      nodes[i].z += nodes[i].vz;
    }
  }
}

// Run simulation
simulate(300);

// ═══════════════════════════════════════════════════════════════════════
// CREATE 3D OBJECTS
// ═══════════════════════════════════════════════════════════════════════

const nodeGroup = new THREE.Group();
const edgeGroup = new THREE.Group();
const glowGroup = new THREE.Group();
const particleGroup = new THREE.Group();

scene.add(edgeGroup);
scene.add(glowGroup);
scene.add(nodeGroup);
scene.add(particleGroup);

// ── Edges ──
const edgeMeshes = [];
edges.forEach(e => {
  const si = nodeMap[e.source];
  const ti = nodeMap[e.target];
  if (si === undefined || ti === undefined) return;
  const s = nodes[si], t = nodes[ti];

  const points = [
    new THREE.Vector3(s.x, s.y, s.z),
    new THREE.Vector3(t.x, t.y, t.z)
  ];
  const geom = new THREE.BufferGeometry().setFromPoints(points);
  const normW = e.weight / 120;
  const opacity = 0.04 + normW * 0.25;

  // Determine color by dominant node type
  const isGestoraDominant = (nodes[si].type === 'gestora');
  const baseColor = isGestoraDominant ? new THREE.Color(0xe2a44e) : new THREE.Color(0x6ec4a7);
  const edgeColor = baseColor.clone().lerp(new THREE.Color(0x333333), 0.5);

  const mat = new THREE.LineBasicMaterial({
    color: edgeColor,
    transparent: true,
    opacity: opacity,
    blending: THREE.AdditiveBlending,
    depthWrite: false
  });
  const line = new THREE.Line(geom, mat);
  line.userData = { sourceIdx: si, targetIdx: ti, weight: e.weight, baseOpacity: opacity };
  edgeGroup.add(line);
  edgeMeshes.push(line);
});

// ── Nodes (core spheres) ──
const nodeMeshes = [];
const gestoraColor = new THREE.Color(0xe2a44e);
const depositariaColor = new THREE.Color(0x6ec4a7);

nodes.forEach((n, i) => {
  const isGestora = n.type === 'gestora';
  const radius = isGestora
    ? 1.5 + (n.weight / maxWeight) * 5
    : 2 + (n.weight / maxWeight) * 7;

  const geom = new THREE.SphereGeometry(radius, 24, 24);
  const color = isGestora ? gestoraColor : depositariaColor;
  const mat = new THREE.MeshBasicMaterial({
    color: color,
    transparent: true,
    opacity: 0.9,
  });
  const mesh = new THREE.Mesh(geom, mat);
  mesh.position.set(n.x, n.y, n.z);
  mesh.userData = { nodeIndex: i, baseRadius: radius };
  nodeGroup.add(mesh);
  nodeMeshes.push(mesh);

  // ── Glow sprite ──
  const glowSize = radius * (isGestora ? 10 : 12);
  const spriteMat = new THREE.SpriteMaterial({
    map: isGestora ? glowTexGestora : glowTexDepositaria,
    transparent: true,
    opacity: 0.15 + (n.weight / maxWeight) * 0.35,
    blending: THREE.AdditiveBlending,
    depthWrite: false,
  });
  const sprite = new THREE.Sprite(spriteMat);
  sprite.position.set(n.x, n.y, n.z);
  sprite.scale.set(glowSize, glowSize, 1);
  sprite.userData = { nodeIndex: i };
  glowGroup.add(sprite);
});

// ── Flowing particles along edges ──
const NUM_PARTICLES = 600;
const particlePositions = new Float32Array(NUM_PARTICLES * 3);
const particleColors = new Float32Array(NUM_PARTICLES * 3);
const particleSpeeds = new Float32Array(NUM_PARTICLES);
const particleEdgeMap = new Uint16Array(NUM_PARTICLES);
const particleProgress = new Float32Array(NUM_PARTICLES);

const validEdges = edges.filter(e => nodeMap[e.source] !== undefined && nodeMap[e.target] !== undefined);

for (let i = 0; i < NUM_PARTICLES; i++) {
  const edgeIdx = Math.floor(Math.random() * validEdges.length);
  particleEdgeMap[i] = edgeIdx;
  particleProgress[i] = Math.random();
  particleSpeeds[i] = 0.0008 + Math.random() * 0.003;

  const e = validEdges[edgeIdx];
  const s = nodes[nodeMap[e.source]];
  const t = nodes[nodeMap[e.target]];
  const p = particleProgress[i];
  particlePositions[i*3]   = s.x + (t.x - s.x) * p;
  particlePositions[i*3+1] = s.y + (t.y - s.y) * p;
  particlePositions[i*3+2] = s.z + (t.z - s.z) * p;

  // Color based on source type
  const srcNode = nodes[nodeMap[e.source]];
  if (srcNode.type === 'gestora') {
    particleColors[i*3]   = 0.886; // #e2a44e
    particleColors[i*3+1] = 0.643;
    particleColors[i*3+2] = 0.306;
  } else {
    particleColors[i*3]   = 0.431; // #6ec4a7
    particleColors[i*3+1] = 0.769;
    particleColors[i*3+2] = 0.655;
  }
}

const particleGeom = new THREE.BufferGeometry();
particleGeom.setAttribute('position', new THREE.BufferAttribute(particlePositions, 3));
particleGeom.setAttribute('color', new THREE.BufferAttribute(particleColors, 3));

const particleMat = new THREE.PointsMaterial({
  size: 2.2,
  map: glowTexWhite,
  transparent: true,
  opacity: 0.7,
  blending: THREE.AdditiveBlending,
  depthWrite: false,
  vertexColors: true,
  sizeAttenuation: true,
});

const particleMesh = new THREE.Points(particleGeom, particleMat);
particleGroup.add(particleMesh);

// ── Background stars ──
const starCount = 2000;
const starGeom = new THREE.BufferGeometry();
const starPos = new Float32Array(starCount * 3);
for (let i = 0; i < starCount; i++) {
  starPos[i*3]   = (Math.random() - 0.5) * 4000;
  starPos[i*3+1] = (Math.random() - 0.5) * 4000;
  starPos[i*3+2] = (Math.random() - 0.5) * 4000;
}
starGeom.setAttribute('position', new THREE.BufferAttribute(starPos, 3));
const starMat = new THREE.PointsMaterial({
  size: 0.8,
  color: 0x444444,
  transparent: true,
  opacity: 0.5,
  blending: THREE.AdditiveBlending,
  depthWrite: false,
  sizeAttenuation: true,
});
scene.add(new THREE.Points(starGeom, starMat));

// ═══════════════════════════════════════════════════════════════════════
// CAMERA CONTROLS (manual orbit)
// ═══════════════════════════════════════════════════════════════════════

let cameraTheta = 0, cameraPhi = Math.PI / 2, cameraRadius = 500;
let targetTheta = 0, targetPhi = Math.PI / 2, targetRadius = 500;
let isDragging = false, lastMouseX = 0, lastMouseY = 0;
let autoRotate = true;
let focusedNode = null;

function updateCamera() {
  cameraTheta += (targetTheta - cameraTheta) * 0.08;
  cameraPhi += (targetPhi - cameraPhi) * 0.08;
  cameraRadius += (targetRadius - cameraRadius) * 0.08;

  cameraPhi = Math.max(0.1, Math.min(Math.PI - 0.1, cameraPhi));
  cameraRadius = Math.max(100, Math.min(1500, cameraRadius));

  camera.position.x = cameraRadius * Math.sin(cameraPhi) * Math.cos(cameraTheta);
  camera.position.y = cameraRadius * Math.cos(cameraPhi);
  camera.position.z = cameraRadius * Math.sin(cameraPhi) * Math.sin(cameraTheta);
  camera.lookAt(0, 0, 0);
}

renderer.domElement.addEventListener('mousedown', e => {
  isDragging = true;
  lastMouseX = e.clientX;
  lastMouseY = e.clientY;
  autoRotate = false;
});

renderer.domElement.addEventListener('mousemove', e => {
  if (isDragging) {
    const dx = e.clientX - lastMouseX;
    const dy = e.clientY - lastMouseY;
    targetTheta -= dx * 0.005;
    targetPhi -= dy * 0.005;
    lastMouseX = e.clientX;
    lastMouseY = e.clientY;
  }
});

renderer.domElement.addEventListener('mouseup', () => {
  isDragging = false;
  setTimeout(() => { autoRotate = true; }, 3000);
});

renderer.domElement.addEventListener('wheel', e => {
  targetRadius += e.deltaY * 0.5;
  e.preventDefault();
}, { passive: false });

// Touch support
renderer.domElement.addEventListener('touchstart', e => {
  if (e.touches.length === 1) {
    isDragging = true;
    lastMouseX = e.touches[0].clientX;
    lastMouseY = e.touches[0].clientY;
    autoRotate = false;
  }
}, { passive: true });

renderer.domElement.addEventListener('touchmove', e => {
  if (isDragging && e.touches.length === 1) {
    const dx = e.touches[0].clientX - lastMouseX;
    const dy = e.touches[0].clientY - lastMouseY;
    targetTheta -= dx * 0.005;
    targetPhi -= dy * 0.005;
    lastMouseX = e.touches[0].clientX;
    lastMouseY = e.touches[0].clientY;
  }
}, { passive: true });

renderer.domElement.addEventListener('touchend', () => {
  isDragging = false;
  setTimeout(() => { autoRotate = true; }, 3000);
});

// ═══════════════════════════════════════════════════════════════════════
// RAYCASTING / HOVER
// ═══════════════════════════════════════════════════════════════════════

const raycaster = new THREE.Raycaster();
raycaster.params.Points = { threshold: 5 };
const mouse = new THREE.Vector2();
let hoveredNode = null;
const tooltip = document.getElementById('tooltip');

renderer.domElement.addEventListener('mousemove', e => {
  mouse.x = (e.clientX / W) * 2 - 1;
  mouse.y = -(e.clientY / H) * 2 + 1;

  raycaster.setFromCamera(mouse, camera);
  const intersects = raycaster.intersectObjects(nodeMeshes);

  if (intersects.length > 0) {
    const mesh = intersects[0].object;
    const idx = mesh.userData.nodeIndex;
    const n = nodes[idx];

    if (hoveredNode !== idx) {
      hoveredNode = idx;
      highlightNode(idx);
    }

    // Tooltip
    const tt = tooltip;
    tt.querySelector('.tt-name').textContent = n.id;
    tt.querySelector('.tt-name').className = 'tt-name ' + (n.type === 'gestora' ? 'gestora-color' : 'depositaria-color');
    tt.querySelector('.tt-type').textContent = n.type === 'gestora' ? '● Gestora' : '◆ Depositaria';
    tt.querySelector('.tt-stat').innerHTML = `${n.weight} fondos · ${n.connections} conexiones ponderadas`;
    tt.classList.add('visible');

    const offsetX = e.clientX + 20;
    const offsetY = e.clientY - 10;
    tt.style.left = Math.min(offsetX, W - 340) + 'px';
    tt.style.top = Math.min(offsetY, H - 100) + 'px';

    document.body.style.cursor = 'pointer';
  } else {
    if (hoveredNode !== null) {
      unhighlightAll();
      hoveredNode = null;
    }
    tooltip.classList.remove('visible');
    document.body.style.cursor = 'default';
  }
});

renderer.domElement.addEventListener('click', e => {
  raycaster.setFromCamera(mouse, camera);
  const intersects = raycaster.intersectObjects(nodeMeshes);
  if (intersects.length > 0) {
    const idx = intersects[0].object.userData.nodeIndex;
    focusOnNode(idx);
  }
});

function highlightNode(idx) {
  // Dim everything
  nodeMeshes.forEach((m, i) => {
    if (i === idx) {
      m.material.opacity = 1;
      m.scale.setScalar(1.4);
    } else {
      m.material.opacity = 0.12;
      m.scale.setScalar(1);
    }
  });

  glowGroup.children.forEach((s, i) => {
    if (i === idx) {
      s.material.opacity = 0.8;
    } else {
      s.material.opacity = 0.02;
    }
  });

  // Highlight connected edges and nodes
  const connectedNodes = new Set();
  edgeMeshes.forEach(line => {
    const { sourceIdx, targetIdx, baseOpacity } = line.userData;
    if (sourceIdx === idx || targetIdx === idx) {
      line.material.opacity = Math.min(baseOpacity * 6, 0.8);
      connectedNodes.add(sourceIdx === idx ? targetIdx : sourceIdx);
    } else {
      line.material.opacity = 0.01;
    }
  });

  // Bring back connected nodes
  connectedNodes.forEach(ci => {
    nodeMeshes[ci].material.opacity = 0.7;
    nodeMeshes[ci].scale.setScalar(1.1);
    if (glowGroup.children[ci]) {
      glowGroup.children[ci].material.opacity = 0.3;
    }
  });
}

function unhighlightAll() {
  nodeMeshes.forEach((m, i) => {
    m.material.opacity = 0.9;
    m.scale.setScalar(1);
  });
  glowGroup.children.forEach((s, i) => {
    const n = nodes[i];
    if (n) {
      s.material.opacity = 0.15 + (n.weight / maxWeight) * 0.35;
    }
  });
  edgeMeshes.forEach(line => {
    line.material.opacity = line.userData.baseOpacity;
  });
}

function focusOnNode(idx) {
  const n = nodes[idx];
  // Move camera to look at this node from nearby
  const dist = 200;
  const dx = n.x, dy = n.y, dz = n.z;
  const r = Math.sqrt(dx*dx + dy*dy + dz*dz);
  if (r > 1) {
    targetTheta = Math.atan2(dz, dx);
    targetPhi = Math.acos(dy / r);
    targetRadius = r + dist;
  }
}

// ═══════════════════════════════════════════════════════════════════════
// ANIMATION LOOP
// ═══════════════════════════════════════════════════════════════════════

let time = 0;

function animate() {
  requestAnimationFrame(animate);
  time += 0.016;

  // Auto rotation
  if (autoRotate) {
    targetTheta += 0.0008;
  }

  updateCamera();

  // Animate particles
  const posArr = particleGeom.attributes.position.array;
  for (let i = 0; i < NUM_PARTICLES; i++) {
    particleProgress[i] += particleSpeeds[i];
    if (particleProgress[i] > 1) {
      particleProgress[i] = 0;
      // Optionally reassign to different edge
      if (Math.random() < 0.3) {
        particleEdgeMap[i] = Math.floor(Math.random() * validEdges.length);
      }
    }

    const e = validEdges[particleEdgeMap[i]];
    const s = nodes[nodeMap[e.source]];
    const t = nodes[nodeMap[e.target]];
    const p = particleProgress[i];

    // Smooth step for nicer flow
    const sp = p * p * (3 - 2 * p);
    posArr[i*3]   = s.x + (t.x - s.x) * sp;
    posArr[i*3+1] = s.y + (t.y - s.y) * sp;
    posArr[i*3+2] = s.z + (t.z - s.z) * sp;
  }
  particleGeom.attributes.position.needsUpdate = true;

  // Gentle node pulse
  nodeMeshes.forEach((m, i) => {
    if (hoveredNode === null) {
      const pulse = 1 + Math.sin(time * 1.5 + i * 0.5) * 0.03;
      m.scale.setScalar(pulse);
    }
  });

  // Gentle glow pulse
  glowGroup.children.forEach((s, i) => {
    if (hoveredNode === null && nodes[i]) {
      const base = 0.15 + (nodes[i].weight / maxWeight) * 0.35;
      const pulse = base + Math.sin(time * 1.2 + i * 0.3) * 0.04;
      s.material.opacity = pulse;
    }
  });

  renderer.render(scene, camera);
}

animate();

// ═══════════════════════════════════════════════════════════════════════
// RESIZE
// ═══════════════════════════════════════════════════════════════════════

window.addEventListener('resize', () => {
  const w = window.innerWidth, h = window.innerHeight;
  camera.aspect = w / h;
  camera.updateProjectionMatrix();
  renderer.setSize(w, h);
});
</script>
</body>
</html>

"""

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

    # View mode selector
    nc0, nc1, nc2, nc3 = st.columns([1, 1, 1, 1])
    with nc0:
        view_mode = st.selectbox("Vista", ['3D Interactivo', '2D Analítico'], index=0,
                                  help="3D: Three.js inmersivo · 2D: Plotly con métricas de red")

    if view_mode == '3D Interactivo':
        # ── THREE.JS 3D VIEW ──
        with nc1:
            min_w_3d = st.slider("Mín. fondos", 1, 30, 2, key='3d_min',
                                  help="Filtra vínculos débiles")

        @st.cache_data
        def build_3d_html(_edges_df, min_weight):
            import json
            filt = _edges_df[_edges_df['weight'] >= min_weight]
            nodes_dict = {}
            for _, r in filt.iterrows():
                g = r['Gestora_short']
                d = r['Depositaria_short']
                if g not in nodes_dict:
                    nodes_dict[g] = {'id': g, 'type': 'gestora', 'weight': 0}
                if d not in nodes_dict:
                    nodes_dict[d] = {'id': d, 'type': 'depositaria', 'weight': 0}
                nodes_dict[g]['weight'] += r['weight']
                nodes_dict[d]['weight'] += r['weight']

            node_list = list(nodes_dict.values())
            edge_list = [{'source': r['Gestora_short'], 'target': r['Depositaria_short'],
                          'weight': int(r['weight'])} for _, r in filt.iterrows()]

            data_json = json.dumps({'nodes': node_list, 'edges': edge_list})

            html = _THREE_JS_TEMPLATE.replace('__GRAPH_DATA_PLACEHOLDER__', data_json)
            return html, len(node_list), len(edge_list)

        html_3d, n_nodes, n_edges = build_3d_html(net_edges, min_w_3d)
        components.html(html_3d, height=750, scrolling=False)

        st.caption(f"{n_nodes} nodos · {n_edges} vínculos · Arrastra para rotar, scroll para zoom, click en nodo para enfocar")

    else:
        # ── 2D PLOTLY VIEW ──
        # Controls
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
