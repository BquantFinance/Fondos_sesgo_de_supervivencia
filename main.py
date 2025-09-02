import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import numpy as np
import re
import yfinance as yf
import pandas_datareader.data as wb

# Page configuration
st.set_page_config(
    page_title="Análisis Fondos CNMV - Sesgo de Supervivencia",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Enhanced Dark Mode CSS with Premium Aesthetics
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600&display=swap');
    
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }
    
    /* Enhanced Dark Theme Base */
    .stApp {
        background: linear-gradient(180deg, #0a0a0a 0%, #0f0f0f 50%, #050505 100%);
        position: relative;
    }
    
    .stApp::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: 
            radial-gradient(circle at 20% 50%, rgba(120, 119, 198, 0.03) 0%, transparent 50%),
            radial-gradient(circle at 80% 80%, rgba(255, 119, 198, 0.03) 0%, transparent 50%),
            radial-gradient(circle at 40% 20%, rgba(120, 219, 255, 0.02) 0%, transparent 50%);
        pointer-events: none;
        z-index: 1;
    }
    
    .main {
        background: transparent;
        padding: 0;
        position: relative;
        z-index: 2;
    }
    
    /* Premium Glassmorphism Metrics */
    [data-testid="metric-container"] {
        background: linear-gradient(
            135deg,
            rgba(255, 255, 255, 0.03) 0%,
            rgba(255, 255, 255, 0.01) 100%
        );
        backdrop-filter: blur(20px) saturate(180%);
        -webkit-backdrop-filter: blur(20px) saturate(180%);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 20px;
        padding: 1.75rem;
        position: relative;
        overflow: hidden;
        box-shadow: 
            0 10px 40px rgba(0, 0, 0, 0.4),
            inset 0 1px 0 rgba(255, 255, 255, 0.1),
            inset 0 -1px 0 rgba(0, 0, 0, 0.2);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    [data-testid="metric-container"]::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 1px;
        background: linear-gradient(
            90deg,
            transparent 0%,
            rgba(255, 255, 255, 0.2) 50%,
            transparent 100%
        );
        opacity: 0;
        transition: opacity 0.3s ease;
    }
    
    [data-testid="metric-container"]:hover::before {
        opacity: 1;
    }
    
    [data-testid="metric-container"]:hover {
        transform: translateY(-4px) scale(1.02);
        border-color: rgba(147, 51, 234, 0.5);
        box-shadow: 
            0 20px 60px rgba(147, 51, 234, 0.2),
            inset 0 1px 0 rgba(255, 255, 255, 0.15),
            0 0 40px rgba(147, 51, 234, 0.1);
    }
    
    [data-testid="metric-container"] [data-testid="metric-label"] {
        color: #9ca3af;
        font-size: 0.7rem;
        font-weight: 600;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        margin-bottom: 0.5rem;
        opacity: 0.9;
    }
    
    [data-testid="metric-container"] [data-testid="metric-value"] {
        font-size: 2.25rem;
        font-weight: 800;
        background: linear-gradient(
            135deg,
            #a78bfa 0%,
            #ec4899 50%,
            #06b6d4 100%
        );
        background-size: 200% 200%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: gradient-shift 3s ease infinite;
        line-height: 1.1;
        margin: 0.5rem 0;
    }
    
    @keyframes gradient-shift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    [data-testid="metric-container"] [data-testid="metric-delta"] {
        background: rgba(147, 51, 234, 0.15);
        color: #a78bfa;
        padding: 0.25rem 0.75rem;
        border-radius: 100px;
        font-size: 0.75rem;
        font-weight: 600;
        display: inline-block;
        margin-top: 0.5rem;
        border: 1px solid rgba(147, 51, 234, 0.2);
    }
    
    /* Enhanced Typography */
    h1 {
        background: linear-gradient(135deg, #f9fafb 0%, #9ca3af 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 900;
        font-size: 3rem;
        letter-spacing: -2px;
        margin-bottom: 1rem;
        position: relative;
    }
    
    h1::after {
        content: '';
        position: absolute;
        bottom: -10px;
        left: 0;
        width: 60px;
        height: 4px;
        background: linear-gradient(90deg, #a78bfa 0%, #ec4899 100%);
        border-radius: 2px;
    }
    
    h2 {
        color: #e5e7eb;
        font-weight: 700;
        font-size: 1.875rem;
        margin-top: 2.5rem;
        margin-bottom: 1.25rem;
        letter-spacing: -0.5px;
    }
    
    h3 {
        color: #d1d5db;
        font-weight: 600;
        font-size: 1.375rem;
        margin: 1.5rem 0 1rem 0;
        position: relative;
        padding-left: 1rem;
    }
    
    h3::before {
        content: '';
        position: absolute;
        left: 0;
        top: 50%;
        transform: translateY(-50%);
        width: 4px;
        height: 20px;
        background: linear-gradient(180deg, #a78bfa 0%, #ec4899 100%);
        border-radius: 2px;
    }
    
    /* Premium Input Fields */
    .stTextInput > div > div > input {
        background: rgba(17, 24, 39, 0.7);
        border: 1px solid rgba(147, 51, 234, 0.2);
        border-radius: 16px;
        padding: 1rem 1.25rem;
        font-size: 0.95rem;
        color: #f3f4f6;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        backdrop-filter: blur(10px);
        box-shadow: 
            0 4px 20px rgba(0, 0, 0, 0.3),
            inset 0 1px 0 rgba(255, 255, 255, 0.05);
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #a78bfa;
        background: rgba(17, 24, 39, 0.9);
        box-shadow: 
            0 0 0 4px rgba(147, 51, 234, 0.15),
            0 4px 20px rgba(147, 51, 234, 0.2),
            inset 0 1px 0 rgba(255, 255, 255, 0.1);
        outline: none;
    }
    
    .stTextInput > div > div > input::placeholder {
        color: #6b7280;
        font-weight: 400;
    }
    
    /* Premium Select Box */
    .stSelectbox > div > div {
        background: rgba(17, 24, 39, 0.7);
        border-radius: 16px;
        border: 1px solid rgba(147, 51, 234, 0.2);
        color: #f3f4f6;
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
    }
    
    .stSelectbox > div > div:hover {
        border-color: rgba(147, 51, 234, 0.4);
        box-shadow: 0 4px 20px rgba(147, 51, 234, 0.15);
    }
    
    /* Enhanced Dataframe */
    [data-testid="stDataFrame"] {
        background: linear-gradient(
            135deg,
            rgba(17, 24, 39, 0.9) 0%,
            rgba(17, 24, 39, 0.7) 100%
        );
        border-radius: 20px;
        overflow: hidden;
        border: 1px solid rgba(147, 51, 234, 0.15);
        box-shadow: 
            0 10px 40px rgba(0, 0, 0, 0.4),
            inset 0 1px 0 rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
    }
    
    .dataframe thead tr th {
        background: linear-gradient(135deg, #7c3aed 0%, #ec4899 100%) !important;
        color: white !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        font-size: 0.7rem !important;
        letter-spacing: 1.5px !important;
        padding: 1.25rem 1rem !important;
        border: none !important;
        position: relative !important;
    }
    
    .dataframe tbody tr {
        background: rgba(17, 24, 39, 0.5) !important;
        border-bottom: 1px solid rgba(147, 51, 234, 0.1) !important;
        transition: all 0.2s ease !important;
    }
    
    .dataframe tbody tr:hover {
        background: linear-gradient(
            90deg,
            rgba(147, 51, 234, 0.15) 0%,
            rgba(147, 51, 234, 0.1) 100%
        ) !important;
        transform: translateX(4px);
    }
    
    .dataframe tbody tr td {
        color: #e5e7eb !important;
        border: none !important;
        padding: 1rem !important;
        font-size: 0.9rem !important;
        font-weight: 400 !important;
    }
    
    /* Premium Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background: linear-gradient(
            135deg,
            rgba(17, 24, 39, 0.7) 0%,
            rgba(17, 24, 39, 0.5) 100%
        );
        border-radius: 20px;
        padding: 0.5rem;
        gap: 0.5rem;
        border: 1px solid rgba(147, 51, 234, 0.15);
        backdrop-filter: blur(10px);
        box-shadow: 
            0 4px 20px rgba(0, 0, 0, 0.3),
            inset 0 1px 0 rgba(255, 255, 255, 0.05);
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 14px;
        color: #9ca3af;
        font-weight: 600;
        padding: 0.875rem 1.75rem;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    .stTabs [data-baseweb="tab"]::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(135deg, #7c3aed 0%, #ec4899 100%);
        opacity: 0;
        transition: opacity 0.3s ease;
        border-radius: 14px;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        color: #f3f4f6;
        transform: translateY(-2px);
    }
    
    .stTabs [data-baseweb="tab"]:hover::before {
        opacity: 0.1;
    }
    
    .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
        background: linear-gradient(135deg, #7c3aed 0%, #ec4899 100%);
        color: white;
        box-shadow: 
            0 8px 30px rgba(147, 51, 234, 0.35),
            inset 0 1px 0 rgba(255, 255, 255, 0.2);
        font-weight: 700;
    }
    
    .stTabs [data-baseweb="tab-list"] button[aria-selected="true"]::before {
        opacity: 0;
    }
    
    /* Premium Author Box */
    .author-box {
        background: linear-gradient(
            135deg,
            rgba(147, 51, 234, 0.1) 0%,
            rgba(236, 72, 153, 0.1) 100%
        );
        padding: 1.5rem 2.5rem;
        border-radius: 24px;
        margin: 2rem 0;
        text-align: center;
        border: 1px solid rgba(147, 51, 234, 0.2);
        font-size: 0.95rem;
        color: #d1d5db;
        backdrop-filter: blur(10px);
        box-shadow: 
            0 10px 40px rgba(147, 51, 234, 0.1),
            inset 0 1px 0 rgba(255, 255, 255, 0.05);
        position: relative;
        overflow: hidden;
    }
    
    .author-box::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(
            circle,
            rgba(147, 51, 234, 0.1) 0%,
            transparent 70%
        );
        animation: pulse 4s ease-in-out infinite;
    }
    
    @keyframes pulse {
        0%, 100% { transform: scale(1); opacity: 0.5; }
        50% { transform: scale(1.1); opacity: 0.3; }
    }
    
    .author-box strong {
        color: #f3f4f6;
        font-weight: 700;
        font-size: 1.1rem;
    }
    
    .author-box a {
        background: linear-gradient(135deg, #a78bfa 0%, #ec4899 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-decoration: none;
        font-weight: 700;
        transition: all 0.3s ease;
        position: relative;
    }
    
    .author-box a:hover {
        transform: translateY(-1px);
        filter: brightness(1.2);
    }
    
    /* Premium Info Boxes */
    .info-box {
        background: linear-gradient(
            135deg,
            rgba(99, 102, 241, 0.08) 0%,
            rgba(139, 92, 246, 0.08) 100%
        );
        border-left: 4px solid;
        border-image: linear-gradient(180deg, #7c3aed 0%, #ec4899 100%) 1;
        padding: 1.5rem 2rem;
        margin: 1.5rem 0;
        border-radius: 16px;
        color: #e5e7eb;
        backdrop-filter: blur(10px);
        box-shadow: 
            0 4px 20px rgba(0, 0, 0, 0.2),
            inset 0 1px 0 rgba(255, 255, 255, 0.03);
        position: relative;
        overflow: hidden;
    }
    
    .info-box h4 {
        color: #f3f4f6;
        margin: 0 0 0.75rem 0;
        font-size: 1.1rem;
        font-weight: 700;
    }
    
    .warning-box {
        background: linear-gradient(
            135deg,
            rgba(239, 68, 68, 0.08) 0%,
            rgba(239, 68, 68, 0.05) 100%
        );
        border-left: 4px solid #ef4444;
        padding: 1.5rem 2rem;
        margin: 1.5rem 0;
        border-radius: 16px;
        color: #fca5a5;
        backdrop-filter: blur(10px);
        box-shadow: 
            0 4px 20px rgba(239, 68, 68, 0.1),
            inset 0 1px 0 rgba(255, 255, 255, 0.03);
    }
    
    /* Premium Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #111827 0%, #0f172a 100%);
        padding-top: 2rem;
        border-right: 1px solid rgba(147, 51, 234, 0.1);
    }
    
    /* Radio Buttons */
    .stRadio > label {
        color: #f3f4f6;
        font-weight: 600;
        margin-bottom: 0.75rem;
        font-size: 0.95rem;
    }
    
    .stRadio div[role="radiogroup"] label {
        background: rgba(17, 24, 39, 0.5);
        padding: 0.75rem 1rem;
        border-radius: 12px;
        margin: 0.5rem 0;
        transition: all 0.3s ease;
        border: 1px solid transparent;
    }
    
    .stRadio div[role="radiogroup"] label:hover {
        background: rgba(147, 51, 234, 0.1);
        border-color: rgba(147, 51, 234, 0.3);
    }
    
    /* Plotly Charts Enhancement */
    .js-plotly-plot {
        border-radius: 20px;
        overflow: hidden;
        border: 1px solid rgba(147, 51, 234, 0.15);
        box-shadow: 
            0 10px 40px rgba(0, 0, 0, 0.3),
            inset 0 1px 0 rgba(255, 255, 255, 0.03);
        background: rgba(17, 24, 39, 0.5);
        backdrop-filter: blur(10px);
    }
    
    /* Hide Streamlit Elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Smooth scrolling with momentum */
    html {
        scroll-behavior: smooth;
        scroll-padding-top: 2rem;
    }
    
    /* Loading animation */
    .stSpinner > div {
        border-color: #7c3aed;
        border-top-color: #ec4899;
    }
    
    /* Economic Cycle Badges Enhanced */
    .cycle-badge {
        display: inline-block;
        padding: 0.5rem 1.25rem;
        border-radius: 100px;
        font-size: 0.7rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin: 0.25rem;
        position: relative;
        overflow: hidden;
        backdrop-filter: blur(10px);
    }
    
    .cycle-expansion {
        background: linear-gradient(135deg, rgba(34, 197, 94, 0.15) 0%, rgba(34, 197, 94, 0.1) 100%);
        color: #86efac;
        border: 1px solid rgba(34, 197, 94, 0.3);
        box-shadow: 0 4px 15px rgba(34, 197, 94, 0.2);
    }
    
    .cycle-crisis {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.15) 0%, rgba(239, 68, 68, 0.1) 100%);
        color: #fca5a5;
        border: 1px solid rgba(239, 68, 68, 0.3);
        box-shadow: 0 4px 15px rgba(239, 68, 68, 0.2);
    }
    
    .cycle-recovery {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.15) 0%, rgba(99, 102, 241, 0.1) 100%);
        color: #a5b4fc;
        border: 1px solid rgba(99, 102, 241, 0.3);
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.2);
    }
    
    /* Glow Effects */
    .glow-purple {
        box-shadow: 0 0 40px rgba(147, 51, 234, 0.3);
    }
    
    .glow-pink {
        box-shadow: 0 0 40px rgba(236, 72, 153, 0.3);
    }
    
    /* Custom Scrollbar */
    ::-webkit-scrollbar {
        width: 12px;
        height: 12px;
    }
    
    ::-webkit-scrollbar-track {
        background: #111827;
        border-radius: 6px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, #7c3aed 0%, #ec4899 100%);
        border-radius: 6px;
        border: 2px solid #111827;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(180deg, #8b5cf6 0%, #f472b6 100%);
    }
    
    /* Animations */
    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
    }
    
    @keyframes shimmer {
        0% { background-position: -200% center; }
        100% { background-position: 200% center; }
    }
    
    /* Footer Enhancement */
    .footer-content {
        background: linear-gradient(
            135deg,
            rgba(17, 24, 39, 0.9) 0%,
            rgba(17, 24, 39, 0.7) 100%
        );
        border-radius: 24px;
        padding: 3rem 2rem;
        text-align: center;
        border: 1px solid rgba(147, 51, 234, 0.15);
        backdrop-filter: blur(10px);
        box-shadow: 
            0 -10px 40px rgba(0, 0, 0, 0.3),
            inset 0 1px 0 rgba(255, 255, 255, 0.05);
        margin-top: 4rem;
    }
    
    .footer-content p {
        color: #9ca3af;
        font-size: 0.95rem;
        line-height: 1.8;
        margin: 0.5rem 0;
    }
    
    .footer-content a {
        background: linear-gradient(135deg, #a78bfa 0%, #ec4899 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 600;
        text-decoration: none;
        transition: all 0.3s ease;
    }
    
    .footer-content a:hover {
        filter: brightness(1.3);
    }
</style>
""", unsafe_allow_html=True)

# Load and process data
@st.cache_data
def load_and_process_data():
    df = pd.read_csv('cnmv_funds_data_FINAL.csv')
    
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

# Load macro data
@st.cache_data
def load_macro_data():
    try:
        start_date = '2004-01-01'
        end_date = '2025-12-31'
        
        indicators = {
            'LRHUTTTTESM156S': 'Spain_Unemployment',
            'VIXCLS': 'VIX',
            'DGS10': 'US_10Y_Bond'
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
        return macro_data
    except:
        return pd.DataFrame()

# Load S&P 500 data
@st.cache_data
def load_sp500_data():
    try:
        sp500 = yf.download('^GSPC', start='2004-01-01', end='2025-12-31', progress=False, multi_level_index=False)
        sp500 = sp500[['Close']]
        sp500.columns = ['SP500']
        sp500['Returns'] = sp500['SP500'].pct_change() * 100
        sp500['MA50'] = sp500['SP500'].rolling(window=50).mean()
        sp500['MA200'] = sp500['SP500'].rolling(window=200).mean()
        return sp500
    except:
        return pd.DataFrame()

# Load main data
df = load_and_process_data()
macro_data = load_macro_data()
sp500_data = load_sp500_data()

# Calculate key metrics
births = df[df['status'] == 'NUEVAS_INSCRIPCIONES']
deaths = df[df['status'] == 'BAJAS']

total_births = len(births)
total_deaths = len(deaths)
mortality_rate = (total_deaths / total_births * 100) if total_births > 0 else 0
net_change = total_births - total_deaths

# Title with gradient
st.markdown("# 📊 Análisis de Fondos Españoles - Sesgo de Supervivencia")
st.markdown("""
<div class="author-box">
    <strong>Análisis del Sesgo de Supervivencia en Fondos de Inversión</strong><br>
    <span style="margin-top: 0.5rem; display: block;">
        Por <a href="https://twitter.com/Gsnchez" target="_blank">@Gsnchez</a> • 
        <a href="https://bquantfinance.com" target="_blank">bquantfinance.com</a>
    </span>
    <span style="opacity: 0.7; font-size: 0.85rem; margin-top: 0.5rem; display: block;">
        📅 Datos CNMV 2004-2025 | 🔍 Análisis Exhaustivo
    </span>
</div>
""", unsafe_allow_html=True)

# Key metrics with enhanced styling
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="Total Fondos",
        value=f"{total_births:,}",
        delta="📈 Registrados"
    )

with col2:
    st.metric(
        label="Liquidados",
        value=f"{total_deaths:,}",
        delta=f"💀 {mortality_rate:.0f}% mortalidad"
    )

with col3:
    st.metric(
        label="Activos",
        value=f"{total_births - total_deaths:,}",
        delta="✅ Estimados"
    )

with col4:
    st.metric(
        label="Sesgo Oculto",
        value=f"{abs(net_change):,}",
        delta="⚠️ Fondos invisibles",
        delta_color="inverse"
    )

# Main tabs with icons
tabs = ["🔍 **Búsqueda de Fondos**", "📈 **Ciclo Económico**", "📊 **Análisis Temporal**"]
tab_list = st.tabs(tabs)

# Tab 1: Fund Search
with tab_list[0]:
    st.markdown("### 🔍 Búsqueda y Ciclo de Vida de Fondos")
    
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
    
    # Enhanced search interface
    col1, col2 = st.columns([3, 1])
    
    with col1:
        search_term = st.text_input(
            "",
            placeholder="🔍 Buscar por nombre o número de registro...",
            help="Introduce el nombre del fondo o su número de registro"
        )
    
    with col2:
        status_search = st.selectbox(
            "",
            options=['🌐 Todos', '✅ Activos', '💀 Liquidados'],
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
    
    status_map = {'🌐 Todos': 'Todos', '✅ Activos': 'Activos', '💀 Liquidados': 'Liquidados'}
    status_filter = status_map[status_search]
    
    if status_filter == 'Activos':
        filtered_lifecycle = filtered_lifecycle[filtered_lifecycle['Fecha_Baja'].isna()]
    elif status_filter == 'Liquidados':
        filtered_lifecycle = filtered_lifecycle[filtered_lifecycle['Fecha_Baja'].notna()]
    
    # Statistics with enhanced cards
    total_in_search = len(filtered_lifecycle)
    active_in_search = len(filtered_lifecycle[filtered_lifecycle['Fecha_Baja'].isna()])
    liquidated_in_search = len(filtered_lifecycle[filtered_lifecycle['Fecha_Baja'].notna()])
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("📊 Total Encontrados", f"{total_in_search:,}")
    
    with col2:
        st.metric("✅ Activos", f"{active_in_search:,}", 
                  delta=f"{(active_in_search/total_in_search*100):.1f}%" if total_in_search > 0 else "0%")
    
    with col3:
        st.metric("💀 Liquidados", f"{liquidated_in_search:,}",
                  delta=f"{(liquidated_in_search/total_in_search*100):.1f}%" if total_in_search > 0 else "0%")
    
    # Display results
    if total_in_search > 0:
        display_lifecycle = filtered_lifecycle.copy()
        display_lifecycle['N_Registro'] = display_lifecycle['N_Registro'].astype(int)
        display_lifecycle = display_lifecycle.sort_values('Fecha_Alta', ascending=False)
        
        display_lifecycle['Fecha_Alta'] = display_lifecycle['Fecha_Alta'].dt.strftime('%Y-%m-%d')
        display_lifecycle['Fecha_Baja'] = display_lifecycle['Fecha_Baja'].dt.strftime('%Y-%m-%d')
        
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
        st.info("🔍 No se encontraron fondos con los criterios especificados")

# Tab 2: Economic Cycle Analysis
with tab_list[1]:
    st.markdown("### 📈 Mortalidad de Fondos y Ciclo Económico")
    
    # Prepare monthly data
    monthly_stats = df.groupby(['year', 'month', 'status']).size().unstack(fill_value=0)
    monthly_stats = monthly_stats.rename(columns={
        'NUEVAS_INSCRIPCIONES': 'Altas',
        'BAJAS': 'Bajas'
    })
    monthly_stats['Mortalidad'] = (monthly_stats['Bajas'] / monthly_stats['Altas'] * 100).fillna(0)
    monthly_stats['Balance'] = monthly_stats['Altas'] - monthly_stats['Bajas']
    monthly_stats = monthly_stats.reset_index()
    monthly_stats['date'] = pd.to_datetime(monthly_stats[['year', 'month']].assign(day=1))
    
    # Enhanced macro visualization
    if not sp500_data.empty and not macro_data.empty:
        fig = make_subplots(
            rows=4, cols=1,
            row_heights=[0.3, 0.25, 0.25, 0.2],
            vertical_spacing=0.08,
            subplot_titles=(
                '<b>S&P 500 y Mortalidad de Fondos</b>',
                '<b>VIX - Índice de Volatilidad</b>',
                '<b>Desempleo España (%)</b>',
                '<b>Balance Neto de Fondos</b>'
            ),
            specs=[
                [{"secondary_y": True}],
                [{"secondary_y": False}],
                [{"secondary_y": False}],
                [{"secondary_y": False}]
            ]
        )
        
        # Panel 1: S&P 500 with gradient fill
        fig.add_trace(
            go.Scatter(
                x=sp500_data.index,
                y=sp500_data['SP500'],
                name='S&P 500',
                fill='tozeroy',
                fillcolor='rgba(147, 51, 234, 0.08)',
                line=dict(color='#a78bfa', width=2),
                hovertemplate='<b>S&P 500</b><br>$%{y:,.0f}<extra></extra>'
            ),
            row=1, col=1,
            secondary_y=False
        )
        
        # Add moving averages
        if 'MA50' in sp500_data.columns:
            fig.add_trace(
                go.Scatter(
                    x=sp500_data.index,
                    y=sp500_data['MA50'],
                    name='MA50',
                    line=dict(color='#ec4899', width=1, dash='dot'),
                    opacity=0.7,
                    hovertemplate='<b>MA50</b><br>$%{y:,.0f}<extra></extra>'
                ),
                row=1, col=1,
                secondary_y=False
            )
        
        fig.add_trace(
            go.Scatter(
                x=monthly_stats['date'],
                y=monthly_stats['Mortalidad'],
                name='Mortalidad (%)',
                line=dict(color='#ef4444', width=2.5),
                mode='lines+markers',
                marker=dict(size=4, color='#ef4444'),
                hovertemplate='<b>Mortalidad</b><br>%{y:.1f}%<extra></extra>'
            ),
            row=1, col=1,
            secondary_y=True
        )
        
        # Panel 2: VIX with gradient
        if 'VIX' in macro_data.columns:
            fig.add_trace(
                go.Scatter(
                    x=macro_data.index,
                    y=macro_data['VIX'],
                    name='VIX',
                    fill='tozeroy',
                    fillgradient=dict(
                        type="vertical",
                        colorscale=[[0, 'rgba(251, 191, 36, 0.1)'], [1, 'rgba(251, 191, 36, 0.3)']],
                    ),
                    line=dict(color='#fbbf24', width=2),
                    hovertemplate='<b>VIX</b><br>%{y:.1f}<extra></extra>'
                ),
                row=2, col=1
            )
            
            # Add VIX threshold line
            fig.add_hline(y=30, line_color='rgba(239, 68, 68, 0.5)', 
                         line_width=1, line_dash='dash', row=2, col=1)
        
        # Panel 3: Spanish Unemployment with gradient
        if 'Spain_Unemployment' in macro_data.columns:
            fig.add_trace(
                go.Scatter(
                    x=macro_data.index,
                    y=macro_data['Spain_Unemployment'],
                    name='Desempleo',
                    fill='tozeroy',
                    fillgradient=dict(
                        type="vertical",
                        colorscale=[[0, 'rgba(239, 68, 68, 0.1)'], [1, 'rgba(239, 68, 68, 0.25)']],
                    ),
                    line=dict(color='#dc2626', width=2),
                    hovertemplate='<b>Desempleo</b><br>%{y:.1f}%<extra></extra>'
                ),
                row=3, col=1
            )
        
        # Panel 4: Net Fund Balance with gradient bars
        colors = ['rgba(34, 197, 94, 0.8)' if x >= 0 else 'rgba(239, 68, 68, 0.8)' 
                 for x in monthly_stats['Balance']]
        
        fig.add_trace(
            go.Bar(
                x=monthly_stats['date'],
                y=monthly_stats['Balance'],
                name='Balance',
                marker=dict(
                    color=colors,
                    line=dict(color='rgba(255, 255, 255, 0.1)', width=1)
                ),
                hovertemplate='<b>Balance</b><br>%{y:+}<extra></extra>'
            ),
            row=4, col=1
        )
        
        # Enhanced crisis periods with labels
        crisis_periods = [
            {"name": "Crisis Financiera", "start": "2008-09-01", "end": "2009-06-01", "color": "rgba(239, 68, 68, 0.08)"},
            {"name": "Crisis Deuda EU", "start": "2011-08-01", "end": "2012-07-01", "color": "rgba(251, 191, 36, 0.08)"},
            {"name": "COVID-19", "start": "2020-02-01", "end": "2020-05-01", "color": "rgba(147, 51, 234, 0.08)"}
        ]
        
        for period in crisis_periods:
            for row in range(1, 5):
                fig.add_vrect(
                    x0=period["start"],
                    x1=period["end"],
                    fillcolor=period["color"],
                    layer="below",
                    line_width=0,
                    row=row, col=1
                )
        
        # Enhanced layout
        fig.update_layout(
            height=900,
            plot_bgcolor='rgba(17, 24, 39, 0.8)',
            paper_bgcolor='rgba(10, 10, 10, 0)',
            font=dict(family='Inter', color='#e5e7eb', size=12),
            hovermode='x unified',
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="top",
                y=1.02,
                xanchor="center",
                x=0.5,
                bgcolor='rgba(17, 24, 39, 0.8)',
                bordercolor='rgba(147, 51, 234, 0.2)',
                borderwidth=1,
                font=dict(size=11)
            ),
            margin=dict(t=80, b=40, l=60, r=40)
        )
        
        # Grid and axes styling
        fig.update_xaxes(
            gridcolor='rgba(147, 51, 234, 0.05)', 
            showgrid=True, 
            zeroline=False,
            tickfont=dict(size=10)
        )
        fig.update_yaxes(
            gridcolor='rgba(147, 51, 234, 0.05)', 
            showgrid=True, 
            zeroline=False,
            tickfont=dict(size=10)
        )
        
        # Update y-axis titles
        fig.update_yaxes(title_text="<b>S&P 500</b>", row=1, col=1, secondary_y=False)
        fig.update_yaxes(title_text="<b>Mortalidad (%)</b>", row=1, col=1, secondary_y=True)
        fig.update_yaxes(title_text="<b>VIX</b>", row=2, col=1)
        fig.update_yaxes(title_text="<b>Desempleo (%)</b>", row=3, col=1)
        fig.update_yaxes(title_text="<b>Balance</b>", row=4, col=1)
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Enhanced economic indicators
        st.markdown("### 💡 Indicadores Clave del Ciclo Económico")
        
        col1, col2, col3 = st.columns(3)
        
        # Calculate correlations
        if 'VIX' in macro_data.columns:
            monthly_vix = macro_data.resample('M')['VIX'].mean()
            correlation_data = monthly_stats.set_index('date').join(monthly_vix, how='inner')
            
            if len(correlation_data) > 10:
                vix_mortality_corr = correlation_data['Mortalidad'].corr(correlation_data['VIX'])
                
                with col1:
                    st.markdown(f"""
                    <div class="info-box">
                        <h4>📊 Correlación VIX-Mortalidad</h4>
                        <p style="font-size: 2.5rem; text-align: center; background: linear-gradient(135deg, #a78bfa 0%, #ec4899 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 800; margin: 1rem 0;">
                            {vix_mortality_corr:.3f}
                        </p>
                        <p style="text-align: center; opacity: 0.8; font-size: 0.9rem;">
                            Mayor volatilidad = Mayor mortalidad
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
        
        with col2:
            crisis_years = [2008, 2009, 2010, 2011, 2012, 2020]
            crisis_deaths = deaths[deaths['year'].isin(crisis_years)]
            crisis_mortality = (len(crisis_deaths) / len(deaths) * 100)
            
            st.markdown(f"""
            <div class="info-box">
                <h4>💀 Muertes en Crisis</h4>
                <p style="font-size: 2.5rem; text-align: center; background: linear-gradient(135deg, #ef4444 0%, #fbbf24 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 800; margin: 1rem 0;">
                    {crisis_mortality:.1f}%
                </p>
                <p style="text-align: center; opacity: 0.8; font-size: 0.9rem;">
                    Del total de liquidaciones
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            avg_life_crisis = fund_lifecycle[fund_lifecycle['Fecha_Alta'].notna() & fund_lifecycle['Fecha_Baja'].notna()]
            avg_life_crisis['Alta_Year'] = pd.to_datetime(avg_life_crisis['Fecha_Alta']).dt.year
            crisis_funds = avg_life_crisis[avg_life_crisis['Alta_Year'].isin(crisis_years)]
            
            if len(crisis_funds) > 0:
                avg_life = crisis_funds['Vida_Anos'].mean()
            else:
                avg_life = 0
            
            st.markdown(f"""
            <div class="info-box">
                <h4>⏱️ Vida Media en Crisis</h4>
                <p style="font-size: 2.5rem; text-align: center; background: linear-gradient(135deg, #fbbf24 0%, #22c55e 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 800; margin: 1rem 0;">
                    {avg_life:.1f} años
                </p>
                <p style="text-align: center; opacity: 0.8; font-size: 0.9rem;">
                    Fondos nacidos en crisis
                </p>
            </div>
            """, unsafe_allow_html=True)

# Tab 3: Temporal Analysis
with tab_list[2]:
    st.markdown("### 📊 Evolución Temporal del Sesgo")
    
    # Prepare yearly data
    yearly_stats = df.groupby(['year', 'status']).size().unstack(fill_value=0)
    yearly_stats = yearly_stats.rename(columns={
        'NUEVAS_INSCRIPCIONES': 'Altas',
        'BAJAS': 'Bajas'
    })
    yearly_stats['Cambio_Neto'] = yearly_stats['Altas'] - yearly_stats['Bajas']
    yearly_stats = yearly_stats.reset_index()
    
    # Enhanced temporal chart
    fig = go.Figure()
    
    # Births with gradient
    fig.add_trace(go.Bar(
        x=yearly_stats['year'],
        y=yearly_stats['Altas'],
        name='✅ Altas',
        marker=dict(
            color='rgba(34, 197, 94, 0.8)',
            line=dict(color='rgba(34, 197, 94, 1)', width=2)
        ),
        text=yearly_stats['Altas'],
        textposition='outside',
        textfont=dict(color='#22c55e', size=10, weight=600),
        hovertemplate='<b>%{x}</b><br>Altas: %{y}<extra></extra>'
    ))
    
    # Deaths with gradient
    fig.add_trace(go.Bar(
        x=yearly_stats['year'],
        y=-yearly_stats['Bajas'],
        name='💀 Bajas',
        marker=dict(
            color='rgba(239, 68, 68, 0.8)',
            line=dict(color='rgba(239, 68, 68, 1)', width=2)
        ),
        text=yearly_stats['Bajas'],
        textposition='outside',
        textfont=dict(color='#ef4444', size=10, weight=600),
        hovertemplate='<b>%{x}</b><br>Bajas: %{y}<extra></extra>'
    ))
    
    # Net change line with glow effect
    fig.add_trace(go.Scatter(
        x=yearly_stats['year'],
        y=yearly_stats['Cambio_Neto'],
        name='📈 Balance Neto',
        line=dict(color='#fbbf24', width=4),
        mode='lines+markers',
        marker=dict(
            size=12, 
            color='#fbbf24',
            line=dict(width=3, color='rgba(17, 24, 39, 0.8)'),
            symbol='diamond'
        ),
        hovertemplate='<b>%{x}</b><br>Balance: %{y:+}<extra></extra>'
    ))
    
    # Add a smoothed trend line
    from scipy.interpolate import make_interp_spline
    if len(yearly_stats) > 3:
        try:
            xnew = np.linspace(yearly_stats['year'].min(), yearly_stats['year'].max(), 300)
            spl = make_interp_spline(yearly_stats['year'], yearly_stats['Cambio_Neto'], k=3)
            smooth = spl(xnew)
            
            fig.add_trace(go.Scatter(
                x=xnew,
                y=smooth,
                name='📉 Tendencia',
                line=dict(color='rgba(147, 51, 234, 0.5)', width=2, dash='dash'),
                hovertemplate='<b>Tendencia</b><br>%{y:.0f}<extra></extra>'
            ))
        except:
            pass
    
    fig.update_layout(
        xaxis_title="",
        yaxis_title="<b>Número de Fondos</b>",
        hovermode='x unified',
        height=600,
        plot_bgcolor='rgba(17, 24, 39, 0.8)',
        paper_bgcolor='rgba(10, 10, 10, 0)',
        font=dict(family='Inter', color='#e5e7eb', size=12),
        barmode='relative',
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5,
            bgcolor='rgba(17, 24, 39, 0.9)',
            bordercolor='rgba(147, 51, 234, 0.3)',
            borderwidth=1,
            font=dict(size=11)
        ),
        margin=dict(t=80, b=60, l=60, r=40)
    )
    
    # Add zero line with glow
    fig.add_hline(
        y=0, 
        line_color='rgba(147, 51, 234, 0.5)', 
        line_width=2,
        line_dash='solid'
    )
    
    # Enhanced grid
    fig.update_xaxes(
        gridcolor='rgba(147, 51, 234, 0.05)', 
        showgrid=True, 
        zeroline=False,
        tickfont=dict(size=11)
    )
    fig.update_yaxes(
        gridcolor='rgba(147, 51, 234, 0.05)', 
        showgrid=True, 
        zeroline=False,
        tickfont=dict(size=11)
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Additional insights
    st.markdown("### 🎯 Insights Temporales")
    
    col1, col2, col3, col4 = st.columns(4)
    
    worst_year = yearly_stats.loc[yearly_stats['Bajas'].idxmax(), 'year']
    worst_deaths = yearly_stats.loc[yearly_stats['Bajas'].idxmax(), 'Bajas']
    
    best_year = yearly_stats.loc[yearly_stats['Altas'].idxmax(), 'year']
    best_births = yearly_stats.loc[yearly_stats['Altas'].idxmax(), 'Altas']
    
    with col1:
        st.markdown(f"""
        <div class="info-box" style="text-align: center;">
            <h4>📈 Mejor Año</h4>
            <p style="font-size: 2rem; font-weight: 800; color: #22c55e;">{best_year}</p>
            <p style="opacity: 0.8;">{best_births} altas</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="info-box" style="text-align: center;">
            <h4>📉 Peor Año</h4>
            <p style="font-size: 2rem; font-weight: 800; color: #ef4444;">{worst_year}</p>
            <p style="opacity: 0.8;">{worst_deaths} bajas</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        avg_yearly_births = yearly_stats['Altas'].mean()
        st.markdown(f"""
        <div class="info-box" style="text-align: center;">
            <h4>📊 Media Anual</h4>
            <p style="font-size: 2rem; font-weight: 800; color: #a78bfa;">{avg_yearly_births:.0f}</p>
            <p style="opacity: 0.8;">altas/año</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        total_net_change = yearly_stats['Cambio_Neto'].sum()
        st.markdown(f"""
        <div class="info-box" style="text-align: center;">
            <h4>🎯 Balance Total</h4>
            <p style="font-size: 2rem; font-weight: 800; color: #fbbf24;">{total_net_change:+,}</p>
            <p style="opacity: 0.8;">fondos netos</p>
        </div>
        """, unsafe_allow_html=True)

# Enhanced Footer
st.markdown("---")
st.markdown(f"""
<div class="footer-content">
    <p style="font-size: 1.1rem; color: #f3f4f6; margin-bottom: 1rem;">
        <strong>⚠️ Sesgo de Supervivencia Revelado</strong>
    </p>
    <p>Este análisis demuestra el severo sesgo de supervivencia en la industria de fondos española.</p>
    <p>Con una tasa de mortalidad del <span style="color: #ef4444; font-weight: 700;">{mortality_rate:.0f}%</span>, 
    las estadísticas publicadas no reflejan la realidad completa del mercado.</p>
    <p style="margin-top: 2rem;">
        <a href="https://twitter.com/Gsnchez" target="_blank">@Gsnchez</a> • 
        <a href="https://bquantfinance.com" target="_blank">bquantfinance.com</a><br>
        <span style="opacity: 0.6; font-size: 0.85rem;">Datos CNMV 2004-2025 | Última actualización: {datetime.now().strftime('%B %Y')}</span>
    </p>
</div>
""", unsafe_allow_html=True)
