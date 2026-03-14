import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings('ignore')

# ═══════════════════════════════════════════════════════════════
# PAGE CONFIG
# ═══════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="H-Factor",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ═══════════════════════════════════════════════════════════════
# DESIGN SYSTEM  ── Obsidian Terminal aesthetic
# ═══════════════════════════════════════════════════════════════
THEME = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:ital,wght@0,400;0,700;1,400&family=Outfit:wght@300;400;500;600;700;800;900&display=swap');

/* ══════════════════════════════════════════
   BASE & RESET
══════════════════════════════════════════ */
*, *::before, *::after { box-sizing: border-box; }
html, body, [class*="css"] { font-family: 'Outfit', sans-serif; }
.stApp { background: #080b12; }
section[data-testid="stSidebar"] {
    background: #0c1018 !important;
    border-right: 1px solid #1a2035;
}
.block-container {
    padding: 1.5rem 2rem 3rem 2rem !important;
    max-width: 1600px;
}

/* ── Scrollbar */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: #0c1018; }
::-webkit-scrollbar-thumb { background: #1e3a5f; border-radius: 4px; }

/* ══════════════════════════════════════════
   COMPANY OVERVIEW TEXT — JUSTIFIED
══════════════════════════════════════════ */
.company-overview-box {
    background: #0c1018;
    border: 1px solid #151f30;
    border-radius: 14px;
    padding: 24px 28px;
    margin-bottom: 16px;
}
.company-overview-box p,
.company-overview-box .overview-text {
    font-size: 14px;
    line-height: 1.85;
    color: #9ab4cc;
    text-align: justify;
    text-justify: inter-word;
    hyphens: auto;
    -webkit-hyphens: auto;
    -ms-hyphens: auto;
    word-break: break-word;
    margin: 0;
}

/* ══════════════════════════════════════════
   HERO HEADER
══════════════════════════════════════════ */
.hf-hero {
    position: relative;
    padding: 28px 32px 24px;
    margin-bottom: 8px;
    background: linear-gradient(135deg, #0c1525 0%, #0f1e38 50%, #0a1628 100%);
    border: 1px solid #1a3050;
    border-radius: 20px;
    overflow: hidden;
}
.hf-hero::before {
    content: '';
    position: absolute;
    top: -60px; right: -60px;
    width: 240px; height: 240px;
    background: radial-gradient(circle, rgba(0,168,255,0.08) 0%, transparent 70%);
    border-radius: 50%;
    pointer-events: none;
}
.hf-hero::after {
    content: '';
    position: absolute;
    bottom: -40px; left: 20%;
    width: 160px; height: 160px;
    background: radial-gradient(circle, rgba(99,102,241,0.06) 0%, transparent 70%);
    border-radius: 50%;
    pointer-events: none;
}
.hf-logo {
    font-family: 'Space Mono', monospace;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 6px;
    text-transform: uppercase;
    color: #00a8ff;
    margin-bottom: 4px;
    opacity: 0.9;
}
.hf-company-name {
    font-size: clamp(22px, 3vw, 36px);
    font-weight: 800;
    color: #f0f6ff;
    line-height: 1.15;
    letter-spacing: -0.5px;
    margin-bottom: 6px;
    word-break: break-word;
}
.hf-ticker-badge {
    display: inline-block;
    font-family: 'Space Mono', monospace;
    font-size: 12px;
    font-weight: 700;
    color: #00a8ff;
    background: rgba(0,168,255,0.1);
    border: 1px solid rgba(0,168,255,0.25);
    border-radius: 6px;
    padding: 3px 10px;
    margin-right: 8px;
    margin-bottom: 4px;
    white-space: nowrap;
}
.hf-price {
    font-size: clamp(20px, 2.5vw, 28px);
    font-weight: 800;
}
.hf-meta {
    font-size: 13px;
    color: #5a7a9a;
    margin-top: 8px;
    letter-spacing: 0.3px;
    word-break: break-word;
}
.hf-meta span { color: #7a9ab8; }

/* ══════════════════════════════════════════
   KPI STRIP — responsive wrapping
══════════════════════════════════════════ */
.kpi-strip {
    display: flex;
    flex-wrap: wrap;
    gap: 1px;
    background: #1a2035;
    border: 1px solid #1a2035;
    border-radius: 14px;
    overflow: hidden;
    margin: 16px 0;
}
.kpi-item {
    flex: 1 1 100px;
    background: #0c1018;
    padding: 14px 16px;
    transition: background 0.2s;
    min-width: 80px;
}
.kpi-item:hover { background: #111928; }
.kpi-label {
    font-family: 'Space Mono', monospace;
    font-size: 9px;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: #3a5a7a;
    margin-bottom: 6px;
    white-space: nowrap;
}
.kpi-value {
    font-size: clamp(16px, 2vw, 22px);
    font-weight: 700;
    color: #e8f4ff;
    line-height: 1;
    word-break: break-all;
}
.kpi-sub { font-size: 10px; color: #3a6a9a; margin-top: 4px; }

/* ══════════════════════════════════════════
   VERDICT BANNER — stacks on mobile
══════════════════════════════════════════ */
.verdict-banner {
    border-radius: 16px;
    padding: 24px 28px;
    margin: 20px 0;
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 20px;
    position: relative;
    overflow: hidden;
}
.verdict-banner::before {
    content: '';
    position: absolute;
    inset: 0;
    opacity: 0.04;
    background-size: 40px 40px;
    background-image:
        repeating-linear-gradient(0deg,#fff 0,#fff 1px,transparent 1px,transparent 40px),
        repeating-linear-gradient(90deg,#fff 0,#fff 1px,transparent 1px,transparent 40px);
    pointer-events: none;
}
.verdict-undervalued { background: linear-gradient(135deg,#041a0e,#062a16); border: 1.5px solid #16a34a; }
.verdict-overvalued  { background: linear-gradient(135deg,#1a0404,#2a0808); border: 1.5px solid #dc2626; }
.verdict-fair        { background: linear-gradient(135deg,#1a1204,#2a1e08); border: 1.5px solid #d97706; }
.verdict-icon { font-size: clamp(36px, 5vw, 52px); line-height: 1; flex-shrink: 0; }
.verdict-main { flex: 1; min-width: 160px; }
.verdict-label {
    font-family: 'Space Mono', monospace;
    font-size: 10px;
    letter-spacing: 4px;
    text-transform: uppercase;
    opacity: 0.6;
    margin-bottom: 4px;
}
.verdict-text {
    font-size: clamp(28px, 4vw, 42px);
    font-weight: 900;
    letter-spacing: -1px;
    line-height: 1;
}
.verdict-sub { font-size: 13px; color: #5a7a9a; margin-top: 6px; }
.verdict-stats { margin-left: auto; text-align: right; flex-shrink: 0; }
.verdict-score-big {
    font-size: clamp(40px, 5vw, 56px);
    font-weight: 900;
    letter-spacing: -2px;
    line-height: 1;
}
.verdict-score-label {
    font-family: 'Space Mono', monospace;
    font-size: 9px;
    letter-spacing: 2px;
    color: #3a5a7a;
    text-transform: uppercase;
}
.verdict-confidence { font-size: 13px; color: #5a7a9a; margin-top: 4px; }

/* ══════════════════════════════════════════
   SECTION TITLES
══════════════════════════════════════════ */
.section-title {
    font-family: 'Space Mono', monospace;
    font-size: 10px;
    letter-spacing: 4px;
    text-transform: uppercase;
    color: #00a8ff;
    margin: 28px 0 14px;
    display: flex;
    align-items: center;
    gap: 12px;
}
.section-title::after {
    content: '';
    flex: 1;
    height: 1px;
    background: linear-gradient(90deg, #1a3050, transparent);
}

/* ══════════════════════════════════════════
   METRIC CARDS — fluid responsive grid
══════════════════════════════════════════ */
.mc-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(130px, 1fr));
    gap: 10px;
}
.mc {
    background: #0c1018;
    border: 1px solid #151f30;
    border-radius: 12px;
    padding: 14px 16px;
    position: relative;
    overflow: hidden;
    transition: border-color 0.2s, transform 0.2s;
}
.mc:hover { border-color: #1e3a5f; transform: translateY(-1px); }
.mc::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: var(--mc-accent, linear-gradient(90deg, #00a8ff, #6366f1));
    opacity: 0.6;
}
.mc-label {
    font-family: 'Space Mono', monospace;
    font-size: 9px;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    color: #3a5a7a;
    margin-bottom: 6px;
    white-space: normal;
    word-break: break-word;
    line-height: 1.4;
}
.mc-value {
    font-size: clamp(12px, 1.6vw, 17px);
    font-weight: 700;
    color: #e8f4ff;
    line-height: 1.35;
    white-space: normal;
    word-break: break-word;
    overflow-wrap: break-word;
    max-width: 100%;
    display: block;
}
/* Numeric values — keep on one line, scale down if needed */
.mc-value.num {
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    font-size: clamp(11px, 1.5vw, 17px);
}
.mc-value.green  { color: #22c55e; }
.mc-value.red    { color: #ef4444; }
.mc-value.amber  { color: #f59e0b; }
.mc-value.blue   { color: #38bdf8; }

/* ══════════════════════════════════════════
   SCORE PILLS — wrap on small screens
══════════════════════════════════════════ */
.score-row {
    display: flex;
    gap: 8px;
    align-items: stretch;
    flex-wrap: wrap;
    margin: 12px 0;
}
.score-pill {
    flex: 1 1 80px;
    min-width: 80px;
    background: #0c1018;
    border: 1px solid #151f30;
    border-radius: 12px;
    padding: 12px 10px;
    text-align: center;
}
.score-pill-label {
    font-family: 'Space Mono', monospace;
    font-size: 8px;
    letter-spacing: 1px;
    text-transform: uppercase;
    color: #3a5a7a;
    margin-bottom: 6px;
    word-break: break-word;
}
.score-pill-value { font-size: clamp(22px, 3vw, 28px); font-weight: 900; letter-spacing: -1px; }
.score-pill-bar { height: 3px; border-radius: 2px; margin-top: 8px; background: #1a2035; overflow: hidden; }
.score-pill-fill { height: 100%; border-radius: 2px; }

/* ══════════════════════════════════════════
   TARGET CARDS — wrap on mobile
══════════════════════════════════════════ */
.target-row {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    margin-top: 8px;
}
.target-card {
    flex: 1 1 110px;
    min-width: 100px;
    background: #0c1018;
    border: 1px solid #151f30;
    border-radius: 12px;
    padding: 14px 12px;
    text-align: center;
}
.target-card-method {
    font-family: 'Space Mono', monospace;
    font-size: 8px;
    letter-spacing: 1px;
    text-transform: uppercase;
    color: #3a5a7a;
    margin-bottom: 8px;
    word-break: break-word;
}
.target-card-price {
    font-size: clamp(16px, 2vw, 22px);
    font-weight: 800;
    color: #e8f4ff;
    margin-bottom: 4px;
    word-break: break-all;
}
.target-card-upside { font-size: 12px; font-weight: 700; }

/* ══════════════════════════════════════════
   DCF PANEL
══════════════════════════════════════════ */
.dcf-panel {
    background: #0c1018;
    border: 1px solid #1a2a4a;
    border-radius: 16px;
    padding: 20px 24px;
    margin: 12px 0;
}
.dcf-panel-title {
    font-family: 'Space Mono', monospace;
    font-size: 10px;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: #00a8ff;
    margin-bottom: 16px;
    padding-bottom: 12px;
    border-bottom: 1px solid #1a2a4a;
}
.dcf-config-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
    gap: 16px;
}

/* ══════════════════════════════════════════
   SENSITIVITY TABLE — horizontal scroll on mobile
══════════════════════════════════════════ */
.sens-wrapper {
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
    border-radius: 12px;
}
.sens-table { width: 100%; border-collapse: collapse; font-size: 12px; min-width: 480px; }
.sens-table th {
    font-family: 'Space Mono', monospace;
    font-size: 9px;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    color: #3a5a7a;
    padding: 8px 10px;
    text-align: center;
    border-bottom: 1px solid #1a2a4a;
    white-space: nowrap;
}
.sens-table td {
    padding: 7px 10px;
    text-align: center;
    border: 1px solid #1a2a4a;
    font-family: 'Space Mono', monospace;
    font-size: 11px;
    color: #e8f4ff;
    white-space: nowrap;
}
.sens-table .cell-current { background: rgba(0,168,255,0.1); color: #00a8ff; font-weight: 700; }
.sens-high  { background: rgba(34,197,94,0.08);  color: #22c55e; }
.sens-mid   { background: rgba(245,158,11,0.08); color: #f59e0b; }
.sens-low   { background: rgba(239,68,68,0.08);  color: #ef4444; }

/* ══════════════════════════════════════════
   SIDEBAR
══════════════════════════════════════════ */
.sidebar-brand {
    font-family: 'Space Mono', monospace;
    font-size: 18px;
    font-weight: 700;
    color: #00a8ff;
    letter-spacing: 2px;
    margin-bottom: 2px;
}
.sidebar-tagline { font-size: 11px; color: #3a5a7a; margin-bottom: 20px; letter-spacing: 0.5px; }
.sidebar-section {
    font-family: 'Space Mono', monospace;
    font-size: 9px;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: #1e3a5f;
    margin: 20px 0 10px;
}

/* ══════════════════════════════════════════
   STREAMLIT COMPONENT OVERRIDES
══════════════════════════════════════════ */
.stButton > button {
    background: linear-gradient(135deg, #0a3a6a, #0e4a8a) !important;
    color: #e8f4ff !important;
    border: 1px solid #1a5aa0 !important;
    border-radius: 10px !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 11px !important;
    letter-spacing: 2px !important;
    text-transform: uppercase !important;
    padding: 10px 16px !important;
    transition: all 0.2s !important;
    width: 100%;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #0d4a80, #1260b0) !important;
    border-color: #2a7ad0 !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 20px rgba(0,168,255,0.15) !important;
}
.stSlider > div > div > div { background: #00a8ff !important; }
.stSlider > div > div > div > div { background: #00a8ff !important; }
div[data-testid="stNumberInput"] input,
div[data-testid="stTextInput"] input {
    background: #0c1320 !important;
    border: 1px solid #1a3050 !important;
    border-radius: 8px !important;
    color: #e8f4ff !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 13px !important;
}
div[data-testid="stNumberInput"] input:focus,
div[data-testid="stTextInput"] input:focus {
    border-color: #00a8ff !important;
    box-shadow: 0 0 0 2px rgba(0,168,255,0.1) !important;
}
.stSelectbox > div > div {
    background: #0c1320 !important;
    border: 1px solid #1a3050 !important;
    color: #e8f4ff !important;
}
.stCheckbox > label > span { color: #7a9ab8 !important; }
.stTabs [data-baseweb="tab-list"] {
    background: #0c1018 !important;
    border-bottom: 1px solid #1a2035 !important;
    gap: 0 !important;
    flex-wrap: wrap !important;
}
.stTabs [data-baseweb="tab"] {
    font-family: 'Space Mono', monospace !important;
    font-size: 9px !important;
    letter-spacing: 1.5px !important;
    text-transform: uppercase !important;
    color: #3a5a7a !important;
    padding: 10px 14px !important;
    border-bottom: 2px solid transparent !important;
    white-space: nowrap !important;
}
.stTabs [aria-selected="true"] {
    color: #00a8ff !important;
    border-bottom: 2px solid #00a8ff !important;
    background: transparent !important;
}
div[data-testid="metric-container"] {
    background: #0c1018 !important;
    border: 1px solid #151f30 !important;
    border-radius: 10px !important;
    padding: 12px 14px !important;
}
div[data-testid="metric-container"] label {
    color: #3a5a7a !important;
    font-size: 11px !important;
}
div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
    color: #e8f4ff !important;
    font-size: clamp(16px, 2vw, 20px) !important;
    font-weight: 700 !important;
}
.stExpander {
    background: #0c1018 !important;
    border: 1px solid #1a2035 !important;
    border-radius: 12px !important;
}
.stExpander > div { background: #0c1018 !important; }
hr { border-color: #1a2035 !important; }
p, li { color: #7a9ab8 !important; }
h1, h2, h3 { color: #e8f4ff !important; }
label { color: #5a7a9a !important; font-size: 12px !important; }
.stMarkdown { color: #7a9ab8; }
.element-container .stAlert {
    background: #0c1018 !important;
    border-color: #1a3050 !important;
}

/* ══════════════════════════════════════════
   RESPONSIVE BREAKPOINTS
══════════════════════════════════════════ */

/* Tablet (≤ 1024px) */
@media (max-width: 1024px) {
    .block-container { padding: 1rem 1.25rem 2rem !important; }
    .hf-hero { padding: 22px 24px 20px; }
    .verdict-banner { padding: 20px 22px; gap: 16px; }
    .kpi-item { padding: 12px 14px; }
    .mc-grid { grid-template-columns: repeat(auto-fill, minmax(110px, 1fr)); }
    .dcf-config-grid { grid-template-columns: repeat(auto-fill, minmax(130px, 1fr)); }
}

/* Mobile (≤ 768px) */
@media (max-width: 768px) {
    .block-container { padding: 0.75rem 0.75rem 2rem !important; }
    .hf-hero { padding: 18px 18px 16px; border-radius: 14px; }
    .hf-company-name { font-size: 22px; }
    .kpi-strip { border-radius: 10px; }
    .kpi-item { flex: 1 1 80px; padding: 10px 12px; }
    .kpi-value { font-size: 16px; }
    .verdict-banner { padding: 16px 18px; border-radius: 12px; }
    .verdict-text { font-size: 26px; }
    .verdict-score-big { font-size: 38px; }
    .verdict-stats { width: 100%; text-align: left; margin-left: 0; }
    .score-pill { flex: 1 1 60px; min-width: 60px; padding: 10px 8px; }
    .score-pill-value { font-size: 22px; }
    .mc-grid { grid-template-columns: repeat(auto-fill, minmax(100px, 1fr)); gap: 8px; }
    .mc { padding: 12px 12px; border-radius: 10px; }
    .mc-value { font-size: 15px; }
    .target-card { flex: 1 1 90px; min-width: 85px; padding: 10px 8px; }
    .target-card-price { font-size: 16px; }
    .dcf-panel { padding: 16px 18px; }
    .dcf-config-grid { grid-template-columns: 1fr 1fr; gap: 12px; }
    .sens-table { font-size: 10px; }
    .sens-table td, .sens-table th { padding: 5px 7px; }
    .stTabs [data-baseweb="tab"] { padding: 8px 10px !important; font-size: 8px !important; }
    .company-overview-box { padding: 16px 18px; border-radius: 10px; }
    .company-overview-box .overview-text { font-size: 13px; }
}

/* Small mobile (≤ 480px) */
@media (max-width: 480px) {
    .kpi-item { flex: 1 1 70px; }
    .kpi-label { font-size: 8px; letter-spacing: 1px; }
    .kpi-value { font-size: 14px; }
    .verdict-icon { font-size: 32px; }
    .verdict-text { font-size: 22px; }
    .verdict-score-big { font-size: 32px; }
    .score-pill { flex: 1 1 50px; min-width: 50px; }
    .score-pill-label { font-size: 7px; }
    .mc-grid { grid-template-columns: repeat(auto-fill, minmax(90px, 1fr)); }
    .dcf-config-grid { grid-template-columns: 1fr; }
    .target-card { flex: 1 1 80px; }
}
</style>
"""
st.markdown(THEME, unsafe_allow_html=True)




# ═══════════════════════════════════════════════════════════════
# DATA LAYER
# ═══════════════════════════════════════════════════════════════
@st.cache_data(ttl=21600, show_spinner=False)  # 6 hours cache
def fetch_stock_data(ticker: str):
    """
    Fetch all stock data using a 3-layer session strategy:

    Layer A — curl_cffi (BEST): impersonates Chrome at HTTP/2 + TLS fingerprint
              level. Yahoo Finance cannot distinguish this from a real browser.
              This is the official yfinance recommendation for cloud deployments.

    Layer B — requests-cache: standard requests with disk cache + User-Agent
              rotation. Reduces repeat calls, works when curl_cffi unavailable.

    Layer C — plain yf.Ticker: bare fallback with no session customisation.

    Plus: empty-response detection (Yahoo returns {} silently when blocking),
    exponential backoff, fast_info + Search fallbacks for partial data.
    """
    import time, random

    RATE_LIMIT_KEYS = [
        '429', 'rate', 'too many', 'connection',
        'timeout', 'remote', 'chunked', 'proxy', 'forbidden', '403'
    ]

    def _is_valid_info(d):
        """Yahoo returns empty {} when blocking — detect it."""
        if not d or not isinstance(d, dict):
            return False
        return any(k in d for k in [
            'currentPrice', 'regularMarketPrice', 'previousClose',
            'open', 'bid', 'ask', 'marketCap', 'trailingPE'
        ])

    def _make_session():
        """
        Build the best available session in priority order.
        curl_cffi impersonates Chrome at TLS level — most effective against
        Yahoo Finance IP blocking on shared cloud servers like Streamlit Cloud.
        """
        # Priority 1: curl_cffi — browser-level impersonation
        try:
            from curl_cffi import requests as cffi_requests
            session = cffi_requests.Session(impersonate="chrome120")
            return session, "curl_cffi"
        except ImportError:
            pass

        # Priority 2: requests-cache — reduces repeat calls to Yahoo
        try:
            import requests_cache
            session = requests_cache.CachedSession(
                cache_name='/tmp/yfinance_cache',
                expire_after=21600,   # match our Streamlit cache TTL
                allowable_methods=['GET'],
            )
            USER_AGENTS = [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) "
                "Gecko/20100101 Firefox/125.0",
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            ]
            session.headers.update({'User-Agent': random.choice(USER_AGENTS)})
            return session, "requests_cache"
        except ImportError:
            pass

        # Priority 3: plain requests with User-Agent
        try:
            import requests as req_plain
            session = req_plain.Session()
            session.headers.update({
                'User-Agent': (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
                )
            })
            return session, "requests"
        except Exception:
            pass

        return None, "none"

    def _fetch_info_with_retry(s, max_retries=4):
        """
        Retry on both exceptions AND empty responses.
        Yahoo returns {} silently when blocking — _is_valid_info detects this.
        """
        for attempt in range(max_retries):
            try:
                data = s.info
                if _is_valid_info(data):
                    return data
                wait = 3 * (2 ** attempt)   # 3s → 6s → 12s → 24s
                time.sleep(wait)
            except Exception as e:
                err_str = str(e).lower()
                if any(k in err_str for k in RATE_LIMIT_KEYS):
                    time.sleep(3 * (2 ** attempt))
                else:
                    raise e
        return {}

    def _fetch_with_retry(fn, max_retries=3, base_delay=2):
        """Generic retry for history, financials, cashflow etc."""
        last_err = None
        for attempt in range(max_retries):
            try:
                return fn()
            except Exception as e:
                last_err = e
                if any(k in str(e).lower() for k in RATE_LIMIT_KEYS):
                    time.sleep(base_delay * (2 ** attempt))
                else:
                    raise e
        if last_err:
            raise last_err
        return None

    # ── Build session using best available library
    session, session_type = _make_session()
    try:
        s = yf.Ticker(ticker, session=session) if session else yf.Ticker(ticker)
    except Exception:
        s = yf.Ticker(ticker)

    # ── Fetch info (most important, most frequently blocked)
    info = _fetch_info_with_retry(s)

    # ── If info still empty, try fast_info + Search as fallback
    if not _is_valid_info(info):
        fallback = {}

        # Layer 1: fast_info — different endpoint, often works when .info blocked
        try:
            fi = s.fast_info
            fallback.update({
                'currentPrice':      getattr(fi, 'last_price', None),
                'regularMarketPrice':getattr(fi, 'last_price', None),
                'marketCap':         getattr(fi, 'market_cap', None),
                'currency':          getattr(fi, 'currency', 'USD'),
                'exchange':          getattr(fi, 'exchange', None),
                'fiftyTwoWeekHigh':  getattr(fi, 'year_high', None),
                'fiftyTwoWeekLow':   getattr(fi, 'year_low', None),
                'previousClose':     getattr(fi, 'previous_close', None),
            })
        except Exception:
            pass

        # Layer 2: yf.Search — fetches company metadata from a different endpoint
        # This gives us longName, sector, industry, exchange even when .info blocked
        try:
            search_result = yf.Search(ticker, max_results=1)
            quotes = search_result.quotes if hasattr(search_result, 'quotes') else []
            if quotes:
                q = quotes[0]
                # Only fill fields not already in fallback
                if not fallback.get('longName'):
                    fallback['longName']  = q.get('longname') or q.get('shortname')
                if not fallback.get('exchange'):
                    fallback['exchange']  = q.get('exchange')
                if not fallback.get('sector'):
                    fallback['sector']    = q.get('sector')
                if not fallback.get('industry'):
                    fallback['industry']  = q.get('industry')
                # typeDisp gives us "Equity", "ETF" etc
                fallback['quoteType']     = q.get('quoteType', '')
        except Exception:
            pass

        # Merge with any partial info already fetched, remove None values
        if info and isinstance(info, dict):
            fallback.update({k: v for k, v in info.items() if v is not None})
        info = {k: v for k, v in fallback.items() if v is not None}

    # ── Fetch remaining data with stagger
    time.sleep(0.5)
    hist          = _fetch_with_retry(lambda: s.history(period="2y"))
    time.sleep(0.5)
    financials    = _fetch_with_retry(lambda: s.financials)
    time.sleep(0.5)
    balance_sheet = _fetch_with_retry(lambda: s.balance_sheet)
    time.sleep(0.5)
    cashflow      = _fetch_with_retry(lambda: s.cashflow)

    return info, hist, financials, balance_sheet, cashflow


# ═══════════════════════════════════════════════════════════════
# UTILITIES
# ═══════════════════════════════════════════════════════════════
def safe_get(d, k, default=None):
    """Safely extract a value from a dict.
    Returns default for None dict, None value, N/A, inf, NaN.
    Does NOT filter 0.0 — zero is a valid financial value.
    """
    if d is None:                        # ← guard: dict itself is None
        return default
    if not isinstance(d, dict):          # ← guard: not even a dict
        return default
    v = d.get(k, default)
    if v is None or v == "N/A":
        return default
    try:
        f = float(v)
        if f != f:  # NaN check
            return default
        if abs(f) == float('inf'):
            return default
        return v
    except (TypeError, ValueError):
        return v  # non-numeric strings (country, exchange) are valid

def fmt(val, pct=False, x=False, dec=2, default="—"):
    if val is None: return default
    try:
        if pct: return f"{val*100:.{dec}f}%"
        if x:   return f"{val:.{dec}f}x"
        return f"{val:.{dec}f}"
    except: return default

CURRENCY_SYMBOLS = {
    "USD":"$","EUR":"€","GBP":"£","JPY":"¥","CNY":"¥","INR":"₹","KRW":"₩",
    "BRL":"R$","CAD":"C$","AUD":"A$","HKD":"HK$","SGD":"S$","CHF":"CHF ",
    "SEK":"kr ","NOK":"kr ","DKK":"kr ","MXN":"MX$","ZAR":"R","RUB":"₽",
    "TRY":"₺","NZD":"NZ$","TWD":"NT$","THB":"฿","IDR":"Rp ","MYR":"RM ",
    "PHP":"₱","SAR":"SR ","AED":"AED ","ILS":"₪","PLN":"zł ","CZK":"Kč ",
    "HUF":"Ft ","CLP":"CLP$","COP":"COP$","PEN":"S/.","ARS":"AR$","EGP":"E£",
    "NGN":"₦","PKR":"Rs ","BDT":"৳","VND":"₫","UAH":"₴","QAR":"QR ",
    "KWD":"KD ","BHD":"BD ",
}

def get_currency(info):
    if not info or not isinstance(info, dict):
        return 'USD', '$'
    code = (info.get('currency') or 'USD').upper()
    return code, CURRENCY_SYMBOLS.get(code, f"{code} ")

def fp(val, sym, dec=2, default="—"):
    if val is None: return default
    try: return f"{sym}{val:,.{dec}f}"
    except: return default

def fmt_cap(v, sym):
    if v is None: return "—"
    if v >= 1e12: return f"{sym}{v/1e12:.2f}T"
    if v >= 1e9:  return f"{sym}{v/1e9:.2f}B"
    if v >= 1e6:  return f"{sym}{v/1e6:.2f}M"
    return f"{sym}{v:.0f}"

def fmt_fcf(v, sym):
    if v is None: return "—"
    av = abs(v)
    if av >= 1e9: return f"{sym}{v/1e9:.2f}B"
    if av >= 1e6: return f"{sym}{v/1e6:.2f}M"
    return f"{sym}{v:.0f}"

def fmt_fiscal_year(raw) -> str:
    """
    Convert Yahoo Finance raw fiscal-year/quarter field to human-readable string.
    Handles: "2024-03-31 00:00:00", "2024-03-31", unix timestamps, None.
    """
    if raw is None or raw == "N/A" or raw == "—":
        return "—"
    from datetime import datetime, timezone
    dt = None
    if isinstance(raw, str):
        # Try each format against the full string (not truncated)
        clean = raw.split(".")[0].strip()   # strip microseconds if any
        for fmt_str in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%Y-%m-%dT%H:%M:%S"):
            try:
                dt = datetime.strptime(clean, fmt_str)
                break
            except ValueError:
                continue
    if dt is None:
        # Try unix timestamp (integer or float)
        try:
            dt = datetime.fromtimestamp(float(raw), tz=timezone.utc)
        except (ValueError, TypeError, OSError):
            return str(raw)
    if dt is None:
        return str(raw)
    month_name = dt.strftime("%B %Y")
    m = dt.month
    quarter = "Q1" if m <= 3 else "Q2" if m <= 6 else "Q3" if m <= 9 else "Q4"
    return f"{month_name}  ({quarter})"


def fmt_website(url) -> str:
    """Strip protocol for clean display."""
    if not url: return "—"
    return str(url).replace("https://","").replace("http://","").replace("www.","").rstrip("/")


def color_class(val, good_high=True, lo=0, hi=0.1):
    if val is None: return ""
    if good_high: return "green" if val >= hi else ("amber" if val >= lo else "red")
    else:         return "green" if val <= lo else ("amber" if val <= hi else "red")

def upside_color(u):
    if u is None: return "#5a7a9a"
    return "#22c55e" if u > 5 else ("#ef4444" if u < -5 else "#f59e0b")


# ═══════════════════════════════════════════════════════════════
# METRICS
# ═══════════════════════════════════════════════════════════════
def calculate_metrics(info, cashflow):
    if info is None or not isinstance(info, dict):
        info = {}   # use empty dict so safe_get returns defaults
    m = {}
    keys = [
        ('pe','trailingPE'),('forward_pe','forwardPE'),('pb','priceToBook'),
        ('ps','priceToSalesTrailing12Months'),('ev_ebitda','enterpriseToEbitda'),
        ('peg','pegRatio'),('gross_margin','grossMargins'),('op_margin','operatingMargins'),
        ('net_margin','profitMargins'),('roe','returnOnEquity'),('roa','returnOnAssets'),
        ('rev_growth','revenueGrowth'),('earn_growth','earningsGrowth'),
        ('current_ratio','currentRatio'),('quick_ratio','quickRatio'),
        ('de_ratio','debtToEquity'),('div_yield','dividendYield'),
        ('payout_ratio','payoutRatio'),('target_mean','targetMeanPrice'),
        ('target_high','targetHighPrice'),('target_low','targetLowPrice'),
        ('analyst_count','numberOfAnalystOpinions'),('rec_mean','recommendationMean'),
        ('beta','beta'),('forward_eps','forwardEps'),('book_value','bookValue'),
        ('52w_high','fiftyTwoWeekHigh'),('52w_low','fiftyTwoWeekLow'),
        ('avg_volume','averageVolume'),('market_cap','marketCap'),
    ]
    for k, yk in keys:
        m[k] = safe_get(info, yk)
    m['current_price'] = safe_get(info,'currentPrice') or safe_get(info,'regularMarketPrice')
    try:
        fcf_vals = []
        for col in cashflow.columns[:4]:
            ocf   = cashflow.loc['Operating Cash Flow', col] if 'Operating Cash Flow' in cashflow.index else None
            capex = cashflow.loc['Capital Expenditure',  col] if 'Capital Expenditure'  in cashflow.index else 0
            if ocf: fcf_vals.append(ocf + (capex or 0))
        m['base_fcf'] = np.mean(fcf_vals[:2]) if len(fcf_vals) >= 2 else (fcf_vals[0] if fcf_vals else None)
        mktcap = m.get('market_cap')
        m['fcf_yield'] = fcf_vals[0] / mktcap if (fcf_vals and mktcap) else None
    except:
        m['base_fcf'] = None; m['fcf_yield'] = None
    return m


# ═══════════════════════════════════════════════════════════════
# SCORING
# ═══════════════════════════════════════════════════════════════
def score_metrics(m):
    """
    Score each fundamental dimension 0-100.
    Uses a sentinel of None (not 50) for missing data so real scores of ~50
    are not accidentally filtered. Falls back to neutral 50 only when ALL
    metrics in a category are missing.
    """
    def sr(v, lo, mid, hi, inv=True):
        """Returns None if data missing, else a score 12-95."""
        if v is None:
            return None
        try:
            fv = float(v)
        except (TypeError, ValueError):
            return None
        if inv:   # lower value = better (e.g. P/E, D/E)
            if fv <= lo:  return 95
            elif fv <= mid: return 72
            elif fv <= hi:  return 42
            else:           return 12
        else:     # higher value = better (e.g. margins, ROE)
            if fv >= hi:  return 95
            elif fv >= mid: return 72
            elif fv >= lo:  return 42
            else:           return 12

    def avg(scores):
        valid = [s for s in scores if s is not None]
        return np.mean(valid) if valid else 50.0  # neutral fallback

    # Valuation: lower ratio = better
    V = avg([
        sr(m.get('pe'),         10, 20, 35),
        sr(m.get('forward_pe'), 10, 18, 30),
        sr(m.get('pb'),          1,  3,  6),
        sr(m.get('ps'),          1,  4, 10),
        sr(m.get('ev_ebitda'),   8, 15, 25),
        sr(m.get('peg'),         0,  1,  2),
    ])

    # Profitability: higher = better
    P = avg([
        sr(m.get('gross_margin'), 0.20, 0.40, 0.60, inv=False),
        sr(m.get('net_margin'),   0.05, 0.15, 0.25, inv=False),
        sr(m.get('roe'),          0.05, 0.15, 0.30, inv=False),
    ])

    # Growth: higher = better
    G = avg([
        sr(m.get('rev_growth'),  0.03, 0.10, 0.20, inv=False),
        sr(m.get('earn_growth'), 0.03, 0.10, 0.20, inv=False),
    ])

    # Financial health: current_ratio higher=better, de_ratio lower=better
    H = avg([
        sr(m.get('current_ratio'), 1.0, 1.5, 3.0, inv=False),
        sr(m.get('de_ratio'),      0.5, 1.5, 3.0, inv=True),
    ])

    C = V*0.40 + P*0.30 + G*0.20 + H*0.10
    return {'valuation':V, 'profitability':P, 'growth':G, 'health':H, 'composite':C}


# ═══════════════════════════════════════════════════════════════
# DCF MODEL  (accepts user-defined assumptions)
# ═══════════════════════════════════════════════════════════════
def dcf_valuation(info, cashflow, params: dict):
    try:
        shares = safe_get(info, 'sharesOutstanding')
        cp     = safe_get(info,'currentPrice') or safe_get(info,'regularMarketPrice')
        if not shares: return None

        base_fcf = params['base_fcf']
        if base_fcf is None or base_fcf <= 0: return None

        # Sanity check: FCF/MarketCap > 100% is almost certainly a data artefact
        # (common for banks/financials where yfinance OCF includes loan activity).
        # In such cases we still compute but flag it — the user must override.
        mktcap = safe_get(info, 'marketCap')
        if mktcap and base_fcf / mktcap > 1.0:
            # FCF implausibly large — likely a financial sector data issue.
            # We continue but the user should override Base FCF in the sidebar.
            pass  # don't block, let sidebar override handle it

        g1          = params['growth_rate_1'] / 100
        g2          = params['growth_rate_2'] / 100
        terminal_g  = params['terminal_growth'] / 100
        wacc        = params['wacc'] / 100

        if wacc <= terminal_g: wacc = terminal_g + 0.02

        projected = []
        # Phase 1: years 1–5
        for yr in range(1, 6):
            projected.append(base_fcf * (1 + g1) ** yr)
        # Phase 2: years 6–10
        for yr in range(1, 6):
            projected.append(projected[-1] * (1 + g2))

        pv_fcf = sum(fcf / (1 + wacc)**(i+1) for i, fcf in enumerate(projected))
        tv     = projected[-1] * (1 + terminal_g) / (wacc - terminal_g)
        pv_tv  = tv / (1 + wacc)**10

        net_debt  = (safe_get(info,'totalDebt',0) or 0) - (safe_get(info,'totalCash',0) or 0)
        intrinsic = (pv_fcf + pv_tv - net_debt) / shares
        # Margin of Safety: positive = stock cheap vs intrinsic, negative = stock expensive
        # Denominator is cp (current price) — the reference point for the investor
        mos = (intrinsic - cp) / cp * 100 if (intrinsic and cp and cp > 0) else None

        return {
            'intrinsic_value': intrinsic,
            'current_price': cp,
            'wacc': wacc,
            'g1': g1, 'g2': g2,
            'terminal_g': terminal_g,
            'base_fcf': base_fcf,
            'pv_fcf': pv_fcf,
            'pv_tv': pv_tv,
            'projected': projected,
            'margin_of_safety': mos,
        }
    except Exception as e:
        return None


# ═══════════════════════════════════════════════════════════════
# SENSITIVITY MATRIX
# ═══════════════════════════════════════════════════════════════
def build_sensitivity(info, cashflow, base_params, cp, sym):
    wacc_range   = [base_params['wacc']-2, base_params['wacc']-1, base_params['wacc'],
                    base_params['wacc']+1, base_params['wacc']+2]
    growth_range = [base_params['growth_rate_1']-5, base_params['growth_rate_1']-2.5,
                    base_params['growth_rate_1'],
                    base_params['growth_rate_1']+2.5, base_params['growth_rate_1']+5]

    table = []
    for w in wacc_range:
        row = []
        for g in growth_range:
            p = {**base_params, 'wacc': w, 'growth_rate_1': g}
            r = dcf_valuation(info, cashflow, p)
            val = r['intrinsic_value'] if r else None
            row.append(val)
        table.append(row)
    return table, wacc_range, growth_range


# ═══════════════════════════════════════════════════════════════
# VERDICT
# ═══════════════════════════════════════════════════════════════
def get_verdict(scores, dcf, m):
    """
    Multi-signal verdict engine.

    Signal weights (revised):
      Ratio Score  : max 3 pts  (broad fundamental quality)
      DCF MoS      : max 5 pts  (valuation vs intrinsic — highest weight,
                                  scaled by magnitude for extreme readings)
      Analyst target: max 2 pts  (consensus opinion)

    DCF dominates because it directly answers "is the stock cheap/expensive"
    and should not be overridden by a good score composite alone.
    """
    v = {'undervalued': 0, 'fair': 0, 'overvalued': 0}

    # ── Signal 1: Fundamental ratio composite score (0–100 → 0–3 pts)
    c = scores['composite']
    if c >= 70:
        v['undervalued'] += 3
    elif c >= 55:
        v['undervalued'] += 1
        v['fair'] += 1
    elif c >= 45:
        v['fair'] += 2
    elif c >= 30:
        v['overvalued'] += 1
        v['fair'] += 1
    else:
        v['overvalued'] += 3

    # ── Signal 2: DCF Margin of Safety (0–5 pts, magnitude-scaled)
    if dcf and dcf.get('margin_of_safety') is not None:
        mos = dcf['margin_of_safety']
        if mos >= 40:
            v['undervalued'] += 5        # very cheap: >40% below intrinsic
        elif mos >= 20:
            v['undervalued'] += 4        # comfortable margin of safety
        elif mos >= 5:
            v['undervalued'] += 2        # slight undervaluation
            v['fair'] += 1
        elif mos >= -5:
            v['fair'] += 3               # roughly fairly valued
        elif mos >= -20:
            v['overvalued'] += 2         # moderately overvalued
            v['fair'] += 1
        elif mos >= -40:
            v['overvalued'] += 4         # significantly overvalued
        else:
            v['overvalued'] += 5         # severely overvalued: >40% above intrinsic

    # ── Signal 3: Analyst consensus price target (0–2 pts)
    cp_val = m.get('current_price')
    tgt    = m.get('target_mean')
    if cp_val and tgt and cp_val > 0:
        up = (tgt - cp_val) / cp_val * 100
        if up >= 20:
            v['undervalued'] += 2
        elif up >= 10:
            v['undervalued'] += 1
        elif up >= -5:
            v['fair'] += 2
        elif up >= -15:
            v['overvalued'] += 1
        else:
            v['overvalued'] += 2

    total = sum(v.values())
    if total == 0:
        return 'fair', 50

    final = max(v, key=v.get)

    # Break ties explicitly: prefer the signal with the strongest single evidence
    max_val = v[final]
    tied = [k for k, val in v.items() if val == max_val]
    if len(tied) > 1:
        # Tiebreak: DCF MoS is the most objective signal
        if dcf and dcf.get('margin_of_safety') is not None:
            mos = dcf['margin_of_safety']
            if mos > 5:   final = 'undervalued'
            elif mos < -5: final = 'overvalued'
            else:          final = 'fair'

    conf = v[final] / total * 100
    return final, conf


# ═══════════════════════════════════════════════════════════════
# TARGETS
# ═══════════════════════════════════════════════════════════════
def calc_targets(info, m, dcf):
    t = {}
    if m.get('target_low'):  t['Bear\nAnalyst Low']  = m['target_low']
    if m.get('target_mean'): t['Base\nAnalyst Mean'] = m['target_mean']
    if m.get('target_high'): t['Bull\nAnalyst High'] = m['target_high']
    if dcf and dcf.get('intrinsic_value'): t['DCF\nIntrinsic'] = dcf['intrinsic_value']
    fwd = m.get('forward_eps')
    if fwd and fwd > 0: t['Fair PE\n20× FWD EPS'] = 20 * fwd
    bv = m.get('book_value')
    if bv and bv > 0: t['P/B\n1.5× Book'] = 1.5 * bv
    return t


# ═══════════════════════════════════════════════════════════════
# RENDER HELPERS
# ═══════════════════════════════════════════════════════════════
def section(title, icon=""):
    st.markdown(f'<div class="section-title">{icon}&nbsp; {title}</div>', unsafe_allow_html=True)

def mc_row(items, sym=None):
    """items: list of (label, value, color_class_or_none)
    Automatically detects numeric/short codes vs long text:
      - Short codes & numbers  → .num  (single line, ellipsis)
      - Long text (sector etc) → wrap  (wraps cleanly)
    """
    import re as _re
    def _is_numeric(v):
        # Numeric: contains digits with optional currency/percent signs
        # Also treat short exchange codes (NSE, BSE, NYSE < 6 chars) as numeric
        v = str(v).strip()
        if v == '—': return True
        if len(v) <= 6 and _re.match(r'^[A-Z0-9.]+$', v): return True   # codes
        if _re.search(r'\d', v): return True                             # has digits
        return False

    html = '<div class="mc-grid">'
    for label, value, cc in items:
        accent = {
            'green':'linear-gradient(90deg,#22c55e,#16a34a)',
            'red':'linear-gradient(90deg,#ef4444,#dc2626)',
            'amber':'linear-gradient(90deg,#f59e0b,#d97706)',
            'blue':'linear-gradient(90deg,#00a8ff,#6366f1)',
            None:'linear-gradient(90deg,#1a3050,#1e3a6a)',
        }.get(cc, 'linear-gradient(90deg,#1a3050,#1e3a6a)')
        color_style = f' {cc}' if cc else ''
        # Choose value display class
        val_str = str(value) if value is not None else '—'
        val_class = 'num' if _is_numeric(val_str) else 'wrap'
        full_class = f'mc-value {val_class}{color_style}'
        html += (
            f'<div class="mc" style="--mc-accent:{accent}" title="{val_str}">'
            f'<div class="mc-label">{label}</div>'
            f'<div class="{full_class}">{val_str}</div>'
            f'</div>'
        )
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)

def score_pills(scores):
    items = [
        ("Overall",       scores['composite']),
        ("Valuation",     scores['valuation']),
        ("Profitability", scores['profitability']),
        ("Growth",        scores['growth']),
        ("Fin. Health",   scores['health']),
    ]
    html = '<div class="score-row">'
    for label, score in items:
        if score >= 65:   sc, fc = '#22c55e', 'rgba(34,197,94,0.08)'
        elif score >= 45: sc, fc = '#f59e0b', 'rgba(245,158,11,0.08)'
        else:             sc, fc = '#ef4444', 'rgba(239,68,68,0.08)'
        html += f"""
        <div class="score-pill" style="background:{fc}; border-color:{sc}33;">
            <div class="score-pill-label">{label}</div>
            <div class="score-pill-value" style="color:{sc};">{score:.0f}</div>
            <div class="score-pill-bar">
                <div class="score-pill-fill" style="width:{min(score,100):.0f}%; background:{sc};"></div>
            </div>
        </div>"""
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════
def main():

    # ── SIDEBAR ─────────────────────────────────────────────
    with st.sidebar:
        st.markdown('<div class="sidebar-brand">⚡ H-FACTOR</div>', unsafe_allow_html=True)
        st.markdown('<div class="sidebar-tagline">Fundamental Analysis Agent</div>', unsafe_allow_html=True)
        st.divider()

        st.markdown('<div class="sidebar-section">Stock Search</div>', unsafe_allow_html=True)

        # ── Search mode toggle
        search_mode = st.radio(
            "search_mode", ["🔤 Ticker Symbol", "🔍 Company Name"],
            horizontal=True, label_visibility="collapsed",
            key="search_mode"
        )

        ticker_input = ""
        analyze_btn  = False

        if search_mode == "🔤 Ticker Symbol":
            ticker_input = st.text_input(
                "Ticker", placeholder="AAPL · RELIANCE.NS · TSLA",
                label_visibility="collapsed", key="ticker_direct"
            ).upper().strip()
            analyze_btn = st.button("⚡  Analyze", use_container_width=True, key="btn_direct")

        else:
            # Free-style company name search
            search_query = st.text_input(
                "Company Name", placeholder="e.g. HDFC Bank, Apple, Infosys…",
                label_visibility="collapsed", key="search_query"
            ).strip()

            search_results = []
            if search_query and len(search_query) >= 2:
                try:
                    results = yf.Search(search_query, max_results=8)
                    quotes  = results.quotes if hasattr(results, 'quotes') else []
                    search_results = [
                        q for q in quotes
                        if q.get('symbol') and q.get('shortname') or q.get('longname')
                    ]
                except Exception:
                    search_results = []

            if search_results:
                options = {
                    f"{q.get('shortname') or q.get('longname','Unknown')} [{q['symbol']}]  ·  {q.get('exchange','')}": q['symbol']
                    for q in search_results
                }
                chosen_label = st.selectbox(
                    "Select security", list(options.keys()),
                    label_visibility="collapsed", key="search_select"
                )
                ticker_input = options[chosen_label]
                st.caption(f"Ticker: **{ticker_input}**")
                analyze_btn = st.button("⚡  Analyze", use_container_width=True, key="btn_search")
            elif search_query and len(search_query) >= 2:
                st.caption("No results found — try a different name or switch to Ticker mode.")

        st.markdown('<div class="sidebar-section">Display</div>', unsafe_allow_html=True)
        show_dcf    = st.checkbox("DCF Analysis", True)
        show_charts = st.checkbox("Price Charts",  True)
        show_sens   = st.checkbox("Sensitivity Matrix", True)

        st.divider()

        # ── DCF CUSTOMIZATION PANEL
        st.markdown('<div class="sidebar-section">DCF Assumptions</div>', unsafe_allow_html=True)

        with st.expander("⚙️ Customize DCF Model", expanded=False):
            st.caption("Override auto-detected values to fine-tune the model.")

            # We'll store dcf_params in session state and populate defaults after data loads
            # These widgets use keys so they're stable
            st.markdown("**Phase 1 Growth (Yr 1–5)**")
            dcf_g1 = st.slider("Growth Rate %", 1.0, 40.0,
                               st.session_state.get('dcf_g1_default', 12.0),
                               0.5, key="dcf_g1",
                               help="Expected annual FCF growth for the first 5 years")

            st.markdown("**Phase 2 Growth (Yr 6–10)**")
            dcf_g2 = st.slider("Slow Growth Rate %", 0.5, 25.0,
                               st.session_state.get('dcf_g2_default', 6.0),
                               0.5, key="dcf_g2",
                               help="Growth decelerates in years 6–10")

            st.markdown("**Terminal Growth Rate**")
            dcf_tg = st.slider("Terminal Growth %", 1.0, 5.0,
                               st.session_state.get('dcf_tg_default', 3.0),
                               0.25, key="dcf_tg",
                               help="Perpetual growth rate after year 10 (usually ~GDP growth)")

            st.markdown("**Discount Rate (WACC)**")
            dcf_wacc = st.slider("WACC %", 5.0, 20.0,
                                 st.session_state.get('dcf_wacc_default', 9.0),
                                 0.25, key="dcf_wacc",
                                 help="Weighted Average Cost of Capital")

            st.markdown("**Base Free Cash Flow**")
            dcf_fcf_override = st.number_input(
                "Base FCF (leave 0 for auto)",
                min_value=0.0, value=0.0, step=1e6,
                format="%.0f", key="dcf_fcf_manual",
                help="Set manually in the stock's local currency. 0 = use auto-calculated value."
            )

            st.markdown("**Risk-Free Rate**")
            dcf_rfr = st.slider("Risk-Free Rate %", 1.0, 8.0,
                                st.session_state.get('dcf_rfr_default', 4.5),
                                0.25, key="dcf_rfr",
                                help="Typically the 10-year government bond yield")

        st.divider()
        st.caption("Data · Yahoo Finance (free, ~15 min delay)\nFor education only — not financial advice.")

    # ── APP HEADER ──────────────────────────────────────────
    if not analyze_btn and 'ticker' not in st.session_state:

        # ── Hero banner (no single-quotes inside style attrs)
        st.markdown(
            '<div class="hf-hero">'
            '<div class="hf-logo">&#9889; H-Factor &middot; Fundamental Analysis Agent</div>'
            '<div class="hf-company-name">Know What Any<br/>Stock Is Worth.</div>'
            '<div class="hf-meta">'
            'Multi-model valuation engine &middot; DCF &middot; Ratio Scoring &middot; Analyst Consensus &middot; '
            '<span>40+ currencies</span> &middot; Free data via Yahoo Finance'
            '</div></div>',
            unsafe_allow_html=True
        )

        # ── How-To section header
        st.markdown(
            '<div style="font-family:monospace;font-size:10px;letter-spacing:4px;'
            'text-transform:uppercase;color:#00a8ff;margin:24px 0 14px;">'
            'How To Use H-Factor</div>',
            unsafe_allow_html=True
        )

        # ── 6 step cards — built in Python to avoid quote conflicts
        MONO = "font-family:monospace;font-size:9px;letter-spacing:2px;text-transform:uppercase;"
        CARD = "background:#0c1018;border:1px solid #151f30;border-radius:12px;padding:18px 20px;"
        BODY = "font-size:13px;color:#7a9ab8;line-height:1.7;"
        HL   = "color:#e8f4ff;font-weight:700;"
        CODE = "color:#00a8ff;"
        BLUE = "color:#00a8ff;"
        AMBR = "color:#f59e0b;"

        steps = [
            ("1&#65039;&#8419;", BLUE, "Search a Stock",
             f'Use the sidebar on the left. Choose <b style="{HL}">&#128292; Ticker Symbol</b> '
             f'if you know the code (e.g. <code style="{CODE}">AAPL</code>, '
             f'<code style="{CODE}">RELIANCE.NS</code>) &mdash; or switch to '
             f'<b style="{HL}">&#128269; Company Name</b> to search by name (e.g. "HDFC Bank", "Apple").'),

            ("2&#65039;&#8419;", BLUE, "Hit Analyze",
             f'Click <b style="{HL}">&#9889; Analyze</b>. The agent fetches live data from Yahoo Finance '
             f'&mdash; financials, cash flows, analyst targets &mdash; and runs all models automatically. '
             f'Takes 3&ndash;10 seconds.'),

            ("3&#65039;&#8419;", BLUE, "Read the Verdict",
             f'The banner shows <b style="color:#22c55e;">UNDERVALUED</b>, '
             f'<b style="color:#f59e0b;">FAIRLY VALUED</b>, or '
             f'<b style="color:#ef4444;">OVERVALUED</b> with a confidence % '
             f'and composite score out of 100.'),

            ("4&#65039;&#8419;", BLUE, "Explore the Tabs",
             f'Five tabs give you the full picture:<br/>'
             f'<b style="{HL}">Scores &amp; Targets</b> &middot; prices &amp; analyst views<br/>'
             f'<b style="{HL}">Fundamentals</b> &middot; all financial ratios<br/>'
             f'<b style="{HL}">DCF Model</b> &middot; intrinsic value &amp; sensitivity<br/>'
             f'<b style="{HL}">Price Chart</b> &middot; 2Y candles + Bollinger bands<br/>'
             f'<b style="{HL}">Overview</b> &middot; company info &amp; key facts'),

            ("5&#65039;&#8419;", BLUE, "Tune the DCF",
             f'Open <b style="{HL}">&#9881;&#65039; Customize DCF Model</b> in the sidebar '
             f'to override growth rates, WACC, and terminal rate. The model and verdict update instantly. '
             f'Use the <b style="{HL}">Sensitivity Matrix</b> to see intrinsic value across scenarios.'),

            ("&#9888;&#65039;", AMBR, "Important Note",
             f'H-Factor is an <b style="{HL}">educational research tool</b>, not financial advice. '
             f'Data is from Yahoo Finance (~15 min delayed). '
             f'Always consult a qualified financial advisor before making investment decisions.'),
        ]

        grid_html = '<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:12px;">'
        for icon, icon_color, title, body in steps:
            grid_html += (
                f'<div style="{CARD}">'
                f'<div style="font-size:22px;margin-bottom:8px;">{icon}</div>'
                f'<div style="{MONO}color:{icon_color[6:-1]};margin-bottom:6px;">{title}</div>'
                f'<div style="{BODY}">{body}</div>'
                f'</div>'
            )
        grid_html += '</div>'
        st.markdown(grid_html, unsafe_allow_html=True)

        # ── Ticker reference table
        BADGE = ("background:#111928;border:1px solid #1a3050;border-radius:6px;"
                 "padding:4px 10px;font-family:monospace;font-size:11px;color:#7a9ab8;"
                 "display:inline-block;margin:3px 0;")
        exchanges = [
            ("&#127482;&#127480;", "US",         "AAPL &middot; MSFT &middot; TSLA"),
            ("&#127470;&#127475;", "India NSE",  "RELIANCE.NS &middot; TCS.NS"),
            ("&#127470;&#127475;", "India BSE",  "RELIANCE.BO &middot; TCS.BO"),
            ("&#127468;&#127463;", "UK",         "LLOY.L &middot; HSBA.L"),
            ("&#127465;&#127466;", "Germany",    "BMW.DE &middot; SAP.DE"),
            ("&#127471;&#127477;", "Japan",      "7203.T &middot; 6758.T"),
            ("&#127464;&#127475;", "China/HK",   "BABA &middot; 0700.HK"),
        ]
        ref_html = (
            '<div style="background:#0c1018;border:1px solid #151f30;border-radius:12px;'
            'padding:16px 20px;margin:16px 0;">'
            '<div style="font-family:monospace;font-size:9px;letter-spacing:3px;'
            'text-transform:uppercase;color:#00a8ff;margin-bottom:12px;">'
            'Ticker Symbol Quick Reference</div>'
            '<div style="display:flex;flex-wrap:wrap;gap:8px;">'
        )
        for flag, exch, tickers in exchanges:
            ref_html += (
                f'<span style="{BADGE}">'
                f'{flag} {exch} &nbsp;<code style="color:#00a8ff;">{tickers}</code>'
                f'</span>'
            )
        ref_html += (
            f'<span style="{BADGE}">&#128161; Tip: use Company Name mode if you don\'t know the ticker</span>'
            '</div></div>'
        )
        st.markdown(ref_html, unsafe_allow_html=True)

        # ── Demo buttons
        st.markdown(
            '<div style="font-family:monospace;font-size:9px;letter-spacing:3px;'
            'text-transform:uppercase;color:#3a5a7a;margin:12px 0 8px;">Try a demo stock</div>',
            unsafe_allow_html=True
        )
        cols = st.columns(8)
        demos = ["AAPL", "MSFT", "GOOGL", "NVDA", "TSLA", "RELIANCE.NS", "HDFCBANK.NS", "INFY.NS"]
        for i, t in enumerate(demos):
            if cols[i].button(t, use_container_width=True):
                st.session_state['ticker'] = t
                st.rerun()
        return

    if analyze_btn:
        st.session_state['ticker'] = ticker_input
        # Only clear cache if it's a different ticker than last time
        # Avoids unnecessary Yahoo Finance API calls for same ticker
        if st.session_state.get('last_fetched') != ticker_input:
            fetch_stock_data.clear()
            st.session_state['last_fetched'] = ticker_input

    ticker = st.session_state.get('ticker', ticker_input)

    # ── FETCH ────────────────────────────────────────────────
    with st.spinner(f"Fetching data for {ticker}… (retrying if rate limited)"):
        try:
            info, hist, financials, balance_sheet, cashflow = fetch_stock_data(ticker)
        except Exception as e:
            err_str = str(e).lower()
            if any(k in err_str for k in ['429', 'rate', 'too many']):
                st.error(
                    "⚠️ Yahoo Finance is rate limiting requests right now. "
                    "This is temporary and usually resolves in 1–2 minutes. "
                    "Please wait a moment and try again."
                )
                st.info(
                    "💡 **Tips to reduce rate limiting:**\n"
                    "- Wait 60–90 seconds before retrying\n"
                    "- Avoid analyzing many different stocks in quick succession\n"
                    "- The same stock won't trigger this — it's cached for 6 hours"
                )
            else:
                st.error(f"Data fetch failed: {e}")
            return

    # ── Validate info before any .get() calls
    if not info or not isinstance(info, dict) or not any(
        k in info for k in ['currentPrice','regularMarketPrice','previousClose','marketCap']
    ):
        st.error(
            f"⚠️ Could not load data for **{ticker}**. "
            f"Yahoo Finance may be temporarily blocking requests from this server. "
            f"This usually resolves on its own."
        )
        st.info(
            '💡 **What to try:**\n'
            '- Wait 2-3 minutes and click Analyze again\n'
            '- The data is cached for 6 hours once loaded successfully\n'
            '- If this persists, try analyzing a different stock first, '
            'then come back to this one'
        )
        st.warning(
            f"If you believe **{ticker}** is a valid ticker, "
            f"this is a Yahoo Finance server-side block — not a ticker error. "
            f"TCS.NS, RELIANCE.NS, HDFCBANK.NS are all valid examples that "
            f"may temporarily fail on shared cloud servers."
        )
        return

    cp = safe_get(info, 'currentPrice') or safe_get(info, 'regularMarketPrice')
    if not cp:
        st.error(f"Could not get current price for **{ticker}**. "
                 f"The market may be closed or the ticker may be delisted.")
        return

    currency_code, SYM = get_currency(info)
    m = calculate_metrics(info, cashflow)
    scores = score_metrics(m)

    # ── POPULATE DCF DEFAULTS (only first time for this ticker)
    beta = safe_get(info,'beta', 1.0) or 1.0
    rfr  = st.session_state.get('dcf_rfr', 4.5)
    auto_wacc = round(max(7.0, min(rfr + beta * 5.5, 18.0)), 2)
    auto_g1   = round(min(max((safe_get(info,'earningsGrowth') or 0.10) * 100, 3.0), 35.0), 1)
    auto_g2   = round(auto_g1 * 0.5, 1)

    if 'last_ticker' not in st.session_state or st.session_state['last_ticker'] != ticker:
        st.session_state['last_ticker'] = ticker
        st.session_state['dcf_wacc_default'] = auto_wacc
        st.session_state['dcf_g1_default']   = auto_g1
        st.session_state['dcf_g2_default']   = auto_g2
        st.session_state['dcf_tg_default']   = 3.0
        st.session_state['dcf_rfr_default']  = rfr

    # Build DCF params from sidebar widgets
    manual_fcf = st.session_state.get('dcf_fcf_manual', 0.0)
    dcf_params = {
        'growth_rate_1':  st.session_state.get('dcf_g1', auto_g1),
        'growth_rate_2':  st.session_state.get('dcf_g2', auto_g2),
        'terminal_growth':st.session_state.get('dcf_tg', 3.0),
        'wacc':           st.session_state.get('dcf_wacc', auto_wacc),
        'base_fcf':       manual_fcf if manual_fcf > 0 else m.get('base_fcf'),
    }

    dcf = dcf_valuation(info, cashflow, dcf_params) if show_dcf else None
    verdict, confidence = get_verdict(scores, dcf, m)
    targets = calc_targets(info, m, dcf)

    _i       = info if (info and isinstance(info, dict)) else {}
    company  = _i.get('longName') or _i.get('shortName') or ticker
    sector   = _i.get('sector')   or ''
    industry = _i.get('industry') or ''
    country  = _i.get('country')  or ''
    mktcap   = safe_get(info, 'marketCap')
    wk52_h   = m.get('52w_high')
    wk52_l   = m.get('52w_low')
    pct_from_high = ((cp - wk52_h) / wk52_h * 100) if wk52_h else None

    # ── HERO HEADER ─────────────────────────────────────────
    vc_hex = {'undervalued':'#22c55e','overvalued':'#ef4444','fair':'#f59e0b'}[verdict]
    change  = safe_get(info,'regularMarketChangePercent') or safe_get(info,'currentPrice')
    ch_str  = f"{change:+.2f}%" if isinstance(change, float) and abs(change) < 100 else ""

    st.markdown(f"""
    <div class="hf-hero">
        <div class="hf-logo">⚡ H-Factor · {currency_code}</div>
        <div class="hf-company-name">{company}</div>
        <div style="margin:8px 0;">
            <span class="hf-ticker-badge">{ticker}</span>
            <span style="font-size:28px;font-weight:800;color:{vc_hex};">{fp(cp,SYM)}</span>
            {"<span style='font-size:14px;color:#5a7a9a;margin-left:8px;'>"+ch_str+"</span>" if ch_str else ""}
        </div>
        <div class="hf-meta">
            {f'<span>{sector}</span> &middot; ' if sector else ''}
            {f'<span>{industry}</span> &middot; ' if industry else ''}
            {f'<span>{country}</span> &middot; ' if country else ''}
            Mkt Cap <span>{fmt_cap(mktcap,SYM)}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── KPI STRIP ───────────────────────────────────────────
    pe   = m.get('pe')
    fpe  = m.get('forward_pe')
    peg  = m.get('peg')
    beta_v = safe_get(info,'beta')
    vol  = safe_get(info,'averageVolume')
    vol_str = f"{vol/1e6:.1f}M" if vol and vol >= 1e6 else (f"{vol/1e3:.0f}K" if vol else "—")

    st.markdown(f"""
    <div class="kpi-strip">
        <div class="kpi-item">
            <div class="kpi-label">P/E (TTM)</div>
            <div class="kpi-value">{fmt(pe,x=True)}</div>
        </div>
        <div class="kpi-item">
            <div class="kpi-label">Fwd P/E</div>
            <div class="kpi-value">{fmt(fpe,x=True)}</div>
        </div>
        <div class="kpi-item">
            <div class="kpi-label">PEG</div>
            <div class="kpi-value">{fmt(peg)}</div>
        </div>
        <div class="kpi-item">
            <div class="kpi-label">Beta</div>
            <div class="kpi-value">{fmt(beta_v)}</div>
        </div>
        <div class="kpi-item">
            <div class="kpi-label">52W High</div>
            <div class="kpi-value">{fp(wk52_h,SYM)}</div>
            <div class="kpi-sub">{f'{pct_from_high:+.1f}% from high' if pct_from_high else ''}</div>
        </div>
        <div class="kpi-item">
            <div class="kpi-label">52W Low</div>
            <div class="kpi-value">{fp(wk52_l,SYM)}</div>
        </div>
        <div class="kpi-item">
            <div class="kpi-label">Avg Volume</div>
            <div class="kpi-value">{vol_str}</div>
        </div>
        <div class="kpi-item">
            <div class="kpi-label">Div Yield</div>
            <div class="kpi-value">{fmt(m.get('div_yield'),pct=True)}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── VERDICT BANNER ──────────────────────────────────────
    em_map = {'undervalued':'📈','overvalued':'📉','fair':'⚖️'}
    label_map = {'undervalued':'UNDERVALUED','overvalued':'OVERVALUED','fair':'FAIRLY VALUED'}
    sub_map = {
        'undervalued': 'Trading below estimated intrinsic value — potential buying opportunity',
        'overvalued':  'Trading above estimated intrinsic value — exercise caution',
        'fair':        'Trading near estimated fair value — limited upside or downside',
    }
    mos = dcf.get('margin_of_safety') if dcf else None
    mos_str = f"Margin of Safety: <b style='color:{vc_hex};'>{mos:+.1f}%</b> &nbsp;|&nbsp; " if mos is not None else ""

    st.markdown(f"""
    <div class="verdict-banner verdict-{verdict}">
        <div class="verdict-icon">{em_map[verdict]}</div>
        <div class="verdict-main">
            <div class="verdict-label">H-Factor Verdict</div>
            <div class="verdict-text" style="color:{vc_hex};">{label_map[verdict]}</div>
            <div class="verdict-sub">{sub_map[verdict]}</div>
        </div>
        <div class="verdict-stats">
            <div class="verdict-score-big" style="color:{vc_hex};">{scores['composite']:.0f}</div>
            <div class="verdict-score-label">Composite Score</div>
            <div class="verdict-confidence">
                {mos_str}Confidence <b>{confidence:.0f}%</b>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ═══════════════════════════════════════════════════════
    # TABS
    # ═══════════════════════════════════════════════════════
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "SCORES & TARGETS", "FUNDAMENTALS", "DCF MODEL", "PRICE CHART", "OVERVIEW"
    ])

    # ── TAB 1: SCORES & TARGETS ─────────────────────────────
    with tab1:
        section("Scoring Breakdown", "📊")
        score_pills(scores)

        section("Price Targets", "🎯")
        if targets:
            # Bar chart
            tl = [k.replace('\n',' ') for k in targets]
            tv = list(targets.values())
            bc = ['#22c55e' if v > cp*1.1 else ('#ef4444' if v < cp*0.9 else '#f59e0b') for v in tv]

            fig_t = go.Figure(go.Bar(
                x=tl, y=tv, marker_color=bc,
                text=[fp(v,SYM) for v in tv],
                textposition='outside', textfont=dict(size=12, color='#e8f4ff'),
                marker_line_width=0,
            ))
            if cp:
                fig_t.add_hline(y=cp, line_dash='dot', line_color='#00a8ff', line_width=1.5,
                                annotation_text=f"  Current {fp(cp,SYM)}",
                                annotation_font=dict(color='#00a8ff', size=12))
            fig_t.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(12,16,24,1)',
                height=260, margin=dict(l=0,r=40,t=20,b=0),
                showlegend=False, font=dict(color='#7a9ab8', family='Space Mono'),
                xaxis=dict(showgrid=False, color='#3a5a7a'),
                yaxis=dict(showgrid=True, gridcolor='#151f30', color='#3a5a7a',
                           title=f"Price ({currency_code})"),
            )
            st.plotly_chart(fig_t, use_container_width=True)

            # Target cards row
            html = '<div class="target-row">'
            for name, val in targets.items():
                upside = (val - cp) / cp * 100 if cp else None
                uc = upside_color(upside)
                html += f"""
                <div class="target-card">
                    <div class="target-card-method">{name.replace(chr(10),' ')}</div>
                    <div class="target-card-price">{fp(val,SYM)}</div>
                    <div class="target-card-upside" style="color:{uc};">
                        {f'{upside:+.1f}%' if upside is not None else '—'}
                    </div>
                </div>"""
            html += '</div>'
            st.markdown(html, unsafe_allow_html=True)

        # Analyst consensus
        section("Analyst Consensus", "🧑‍💼")
        rec = m.get('rec_mean')
        rec_labels = {1:"Strong Buy",2:"Buy",3:"Hold",4:"Sell",5:"Strong Sell"}
        rec_colors = {1:"#22c55e",2:"#86efac",3:"#f59e0b",4:"#f87171",5:"#ef4444"}
        rl = rec_labels.get(round(rec),'Hold') if rec else "—"
        rc = rec_colors.get(round(rec),'#f59e0b') if rec else '#5a7a9a'

        mc_row([
            ("# Analysts",   str(m.get('analyst_count') or '—'), None),
            ("Mean Target",  fp(m.get('target_mean'),SYM),        'blue'),
            ("Bull Target",  fp(m.get('target_high'),SYM),        'green'),
            ("Bear Target",  fp(m.get('target_low'), SYM),        'red'),
            ("Rating",       rl,                                   None),
        ], SYM)

        if rec:
            st.markdown(f"**Consensus:** <span style='color:{rc};font-weight:700;font-size:16px;'>{rl}</span> &nbsp;<span style='color:#3a5a7a;font-size:13px;'>({rec:.1f}/5.0)</span>", unsafe_allow_html=True)

    # ── TAB 2: FUNDAMENTALS ─────────────────────────────────
    with tab2:
        section("Valuation Ratios", "💰")
        mc_row([
            ("P/E (TTM)",    fmt(m['pe'],x=True),        color_class(m['pe'],False,10,25)),
            ("Forward P/E",  fmt(m['forward_pe'],x=True), color_class(m['forward_pe'],False,10,22)),
            ("Price/Book",   fmt(m['pb'],x=True),         color_class(m['pb'],False,1,5)),
            ("Price/Sales",  fmt(m['ps'],x=True),         color_class(m['ps'],False,1,8)),
            ("EV/EBITDA",    fmt(m['ev_ebitda'],x=True),  color_class(m['ev_ebitda'],False,8,20)),
            ("PEG Ratio",    fmt(m['peg']),                color_class(m['peg'],False,0,2)),
        ])

        section("Profitability & Returns", "📈")
        mc_row([
            ("Gross Margin",    fmt(m['gross_margin'],pct=True),  color_class(m['gross_margin'],True,0.2,0.4)),
            ("Oper. Margin",    fmt(m['op_margin'],pct=True),     color_class(m['op_margin'],True,0.05,0.15)),
            ("Net Margin",      fmt(m['net_margin'],pct=True),    color_class(m['net_margin'],True,0.05,0.15)),
            ("ROE",             fmt(m['roe'],pct=True),           color_class(m['roe'],True,0.05,0.15)),
            ("ROA",             fmt(m['roa'],pct=True),           color_class(m['roa'],True,0.02,0.08)),
            ("FCF Yield",       fmt(m['fcf_yield'],pct=True),     color_class(m['fcf_yield'],True,0.02,0.05)),
        ])

        section("Growth", "🚀")
        mc_row([
            ("Revenue Growth (YoY)",  fmt(m['rev_growth'],pct=True),  color_class(m['rev_growth'],True,0.03,0.15)),
            ("Earnings Growth (YoY)", fmt(m['earn_growth'],pct=True), color_class(m['earn_growth'],True,0.03,0.15)),
            ("Fwd EPS",               fp(m.get('forward_eps'),SYM),    'blue'),
            ("Book Value/Share",      fp(m.get('book_value'),SYM),     None),
        ])

        section("Financial Health", "🏦")
        mc_row([
            ("Current Ratio",  fmt(m['current_ratio']),           color_class(m['current_ratio'],True,1.0,2.0)),
            ("Quick Ratio",    fmt(m['quick_ratio']),             color_class(m['quick_ratio'],True,0.8,1.5)),
            ("Debt / Equity",  fmt(m['de_ratio']),                color_class(m['de_ratio'],False,0.5,2.0)),
            ("Beta",           fmt(safe_get(info,'beta')),         None),
            ("Payout Ratio",   fmt(m.get('payout_ratio'),pct=True),None),
            ("Div Yield",      fmt(m.get('div_yield'),pct=True),   'amber' if m.get('div_yield') else None),
        ])

    # ── TAB 3: DCF MODEL ────────────────────────────────────
    with tab3:
        if not show_dcf:
            st.info("Enable DCF Analysis in the sidebar to see this section.")
        elif not dcf:
            st.warning("⚠️ DCF could not be computed — Base FCF is unavailable or negative. Try overriding the Base FCF value in the sidebar.")
        else:
            # Results
            mos = dcf.get('margin_of_safety')
            mos_color = '#22c55e' if mos and mos > 20 else ('#f59e0b' if mos and mos > 0 else '#ef4444')

            section("DCF Results", "🔬")
            mc_row([
                ("Intrinsic Value",   fp(dcf['intrinsic_value'],SYM), 'blue'),
                ("Current Price",     fp(dcf['current_price'],SYM),   None),
                ("Margin of Safety",  f"{mos:+.1f}%" if mos is not None else "—", 'green' if (mos and mos>20) else ('amber' if (mos and mos>0) else 'red')),
                ("PV of FCFs",        fmt_fcf(dcf['pv_fcf'],SYM),    None),
                ("PV Terminal Value", fmt_fcf(dcf['pv_tv'],SYM),     None),
                ("WACC Applied",      fmt(dcf['wacc'],pct=True),      None),
            ])

            # Assumptions recap
            section("Active Model Assumptions", "⚙️")
            st.markdown(f"""
            <div class="dcf-panel">
                <div class="dcf-panel-title">DCF Configuration</div>
                <div class="dcf-config-grid">
                    <div>
                        <div class="mc-label">Base FCF</div>
                        <div class="mc-value blue">{fmt_fcf(dcf['base_fcf'],SYM)}</div>
                    </div>
                    <div>
                        <div class="mc-label">Phase 1 Growth (Yr 1–5)</div>
                        <div class="mc-value blue">{dcf['g1']*100:.1f}%</div>
                    </div>
                    <div>
                        <div class="mc-label">Phase 2 Growth (Yr 6–10)</div>
                        <div class="mc-value blue">{dcf['g2']*100:.1f}%</div>
                    </div>
                    <div>
                        <div class="mc-label">Terminal Growth</div>
                        <div class="mc-value blue">{dcf['terminal_g']*100:.2f}%</div>
                    </div>
                    <div>
                        <div class="mc-label">WACC</div>
                        <div class="mc-value blue">{dcf['wacc']*100:.2f}%</div>
                    </div>
                    <div>
                        <div class="mc-label">Projection Horizon</div>
                        <div class="mc-value blue">10 Years</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # FCF Waterfall chart
            section("10-Year FCF Projection", "📊")
            years = [f"Yr {i}" for i in range(1, 11)]
            proj  = dcf['projected']
            phase_colors = ['#00a8ff']*5 + ['#6366f1']*5

            fig_fcf = go.Figure()
            fig_fcf.add_trace(go.Bar(
                x=years, y=[v/1e9 for v in proj],
                marker_color=phase_colors, marker_line_width=0,
                text=[fmt_fcf(v,SYM) for v in proj],
                textposition='outside', textfont=dict(size=10, color='#7a9ab8'),
            ))
            fig_fcf.add_shape(type="line",x0=-0.5,x1=4.5,y0=0,y1=0,
                              line=dict(color='#1a3050',dash='dot',width=1))
            fig_fcf.add_annotation(x=2,y=max(proj)/1e9*1.05,
                                   text="Phase 1: High Growth",
                                   font=dict(color='#00a8ff',size=10,family='Space Mono'),
                                   showarrow=False)
            fig_fcf.add_annotation(x=7,y=max(proj)/1e9*1.05,
                                   text="Phase 2: Slow Growth",
                                   font=dict(color='#6366f1',size=10,family='Space Mono'),
                                   showarrow=False)
            fig_fcf.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(12,16,24,1)',
                height=300, margin=dict(l=0,r=0,t=30,b=0),
                showlegend=False, font=dict(color='#7a9ab8', family='Space Mono'),
                xaxis=dict(showgrid=False, color='#3a5a7a'),
                yaxis=dict(showgrid=True, gridcolor='#151f30', color='#3a5a7a',
                           title=f"FCF ({currency_code}B)"),
            )
            st.plotly_chart(fig_fcf, use_container_width=True)

            # Sensitivity matrix
            if show_sens and dcf:
                section("Sensitivity Analysis", "🔭")
                st.caption("Intrinsic value across different WACC and Growth Rate combinations. Your current inputs are highlighted in blue.")
                try:
                    table, wacc_range, growth_range = build_sensitivity(info, cashflow, dcf_params, cp, SYM)

                    header = "<tr><th>WACC \\ Growth</th>" + "".join(f"<th>{g:.1f}%</th>" for g in growth_range) + "</tr>"
                    rows_html = ""
                    for i, w in enumerate(wacc_range):
                        row_html = f"<tr><td style='color:#00a8ff;font-family:Space Mono;'>{w:.1f}%</td>"
                        for j, val in enumerate(table[i]):
                            is_current = (abs(w - dcf_params['wacc']) < 0.1 and abs(growth_range[j] - dcf_params['growth_rate_1']) < 0.2)
                            if val is None:
                                cell_content, cell_class = "—", ""
                            else:
                                cell_content = fp(val, SYM)
                                upside_v = (val - cp) / cp * 100 if cp else 0
                                cell_class = "sens-high" if upside_v > 20 else ("sens-low" if upside_v < -10 else "sens-mid")
                                if is_current: cell_class = "cell-current"
                            row_html += f"<td class='{cell_class}'>{cell_content}</td>"
                        row_html += "</tr>"
                        rows_html += row_html

                    st.markdown(f"""
                    <div class="dcf-panel">
                    <div class="sens-wrapper">
                        <table class="sens-table">
                            <thead>{header}</thead>
                            <tbody>{rows_html}</tbody>
                        </table>
                    </div>
                        <div style="margin-top:12px;font-size:11px;color:#3a5a7a;font-family:Space Mono;">
                            🟢 >+20% upside &nbsp;&nbsp; 🟡 mixed &nbsp;&nbsp; 🔴 >-10% downside &nbsp;&nbsp; 🔵 current inputs
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                except Exception as e:
                    st.warning(f"Sensitivity matrix failed: {e}")

    # ── TAB 4: PRICE CHART ──────────────────────────────────
    with tab4:
        if not show_charts or hist.empty:
            st.info("Enable Price Charts in the sidebar.")
        else:
            section("Price History (2Y)", "📉")
            period_opts = {"6 Months":"6mo","1 Year":"1y","2 Years":"2y","5 Years":"5y"}
            chosen = st.select_slider("Period", list(period_opts.keys()), "2 Years")
            p = period_opts[chosen]

            @st.cache_data(ttl=21600, show_spinner=False)
            def get_hist(t, per):
                import time
                for attempt in range(3):
                    try:
                        return yf.Ticker(t).history(period=per)
                    except Exception as e:
                        if attempt < 2:
                            time.sleep(2 * (2 ** attempt))
                        else:
                            raise e
            h = get_hist(ticker, p)

            fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                                row_heights=[0.72,0.28], vertical_spacing=0.02)
            fig.add_trace(go.Candlestick(
                x=h.index, open=h['Open'], high=h['High'], low=h['Low'], close=h['Close'],
                increasing_line_color='#22c55e', decreasing_line_color='#ef4444',
                increasing_fillcolor='rgba(34,197,94,0.3)', decreasing_fillcolor='rgba(239,68,68,0.3)',
                name='OHLC', line_width=1,
            ), row=1, col=1)

            ma20  = h['Close'].rolling(20).mean()
            ma50  = h['Close'].rolling(50).mean()
            ma200 = h['Close'].rolling(200).mean()
            fig.add_trace(go.Scatter(x=h.index,y=ma20, line=dict(color='#38bdf8',width=1),name='MA20',opacity=0.8),row=1,col=1)
            fig.add_trace(go.Scatter(x=h.index,y=ma50, line=dict(color='#f59e0b',width=1.5),name='MA50'),row=1,col=1)
            fig.add_trace(go.Scatter(x=h.index,y=ma200,line=dict(color='#a78bfa',width=1.5),name='MA200'),row=1,col=1)

            # Bollinger bands
            std20 = h['Close'].rolling(20).std()
            bb_upper = ma20 + 2*std20
            bb_lower = ma20 - 2*std20
            fig.add_trace(go.Scatter(x=h.index,y=bb_upper,line=dict(color='rgba(56,189,248,0.2)',width=1),name='BB Upper',showlegend=False),row=1,col=1)
            fig.add_trace(go.Scatter(x=h.index,y=bb_lower,line=dict(color='rgba(56,189,248,0.2)',width=1),fill='tonexty',fillcolor='rgba(56,189,248,0.03)',name='BB Lower',showlegend=False),row=1,col=1)

            vol_colors = ['rgba(34,197,94,0.5)' if c>=o else 'rgba(239,68,68,0.5)' for c,o in zip(h['Close'],h['Open'])]
            fig.add_trace(go.Bar(x=h.index,y=h['Volume'],marker_color=vol_colors,name='Volume',showlegend=False),row=2,col=1)

            # DCF intrinsic value line
            if dcf and dcf.get('intrinsic_value'):
                fig.add_hline(y=dcf['intrinsic_value'], line_dash='dash',
                              line_color='rgba(0,168,255,0.5)', line_width=1,
                              annotation_text=f"  DCF {fp(dcf['intrinsic_value'],SYM)}",
                              annotation_font=dict(color='#00a8ff',size=10), row=1, col=1)

            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(12,16,24,1)',
                height=520, margin=dict(l=0,r=0,t=10,b=0),
                xaxis_rangeslider_visible=False,
                legend=dict(orientation='h',y=1.04,font=dict(size=11,color='#7a9ab8')),
                font=dict(color='#7a9ab8',family='Space Mono'),
            )
            fig.update_xaxes(showgrid=False, color='#3a5a7a', zeroline=False)
            fig.update_yaxes(showgrid=True, gridcolor='#151f30', color='#3a5a7a', zeroline=False)
            st.plotly_chart(fig, use_container_width=True)

            # Score radar
            section("Score Radar", "🕸️")
            cats = ['Valuation','Profitability','Growth','Health']
            vals = [scores['valuation'],scores['profitability'],scores['growth'],scores['health']]
            vv   = vals + [vals[0]]
            cc   = cats + [cats[0]]
            fig_r = go.Figure(go.Scatterpolar(
                r=vv, theta=cc, fill='toself',
                fillcolor='rgba(0,168,255,0.08)',
                line=dict(color='#00a8ff',width=2),
            ))
            fig_r.update_layout(
                polar=dict(
                    radialaxis=dict(visible=True,range=[0,100],tickfont=dict(color='#3a5a7a',size=9,family='Space Mono'),gridcolor='#151f30',linecolor='#1a2035'),
                    angularaxis=dict(tickfont=dict(color='#7a9ab8',size=12),linecolor='#1a2035'),
                    bgcolor='rgba(12,16,24,1)'
                ),
                paper_bgcolor='rgba(0,0,0,0)',
                height=300, margin=dict(l=40,r=40,t=20,b=20),
                showlegend=False, font=dict(color='#7a9ab8')
            )
            st.plotly_chart(fig_r, use_container_width=True)

    # ── TAB 5: OVERVIEW ─────────────────────────────────────
    with tab5:
        _info = info if (info and isinstance(info, dict)) else {}
        summary = _info.get('longBusinessSummary','')
        if summary:
            section("Company Overview", "🏢")
            st.markdown(f'''
            <div class="company-overview-box">
                <div class="overview-text">{summary}</div>
            </div>''', unsafe_allow_html=True)

        section("Key Information", "📋")
        left, right = st.columns(2)

        raw_fy      = _info.get('mostRecentQuarter') or _info.get('lastFiscalYearEnd')
        fy_str      = fmt_fiscal_year(raw_fy)
        website_str = fmt_website(_info.get('website'))
        emp         = _info.get('fullTimeEmployees')
        emp_str     = f"{emp:,}" if emp else '—'

        with left:
            mc_row([
                ("Exchange",    _info.get('exchange','—'),  None),
                ("Country",     _info.get('country','—'),   None),
                ("Currency",    currency_code,                'blue'),
                ("Employees",   emp_str,                      None),
            ])
        with right:
            mc_row([
                ("Website",             website_str,                     None),
                ("IPO Date",            _info.get('ipoExpectedDate','—'), None),
                ("Most Recent Quarter", fy_str,                          'amber'),
                ("Sector",              _info.get('sector','—'),         None),
            ])

    # ── FOOTER ──────────────────────────────────────────────
    st.markdown("---")

    # ── Stats engine: Supabase (cloud) with JSON fallback (local)
    # Entire block wrapped — stats failure must NEVER crash the app
    import json, os

    # ── Detect if Supabase secrets are available
    def _get_supabase():
        """Returns supabase client if secrets configured, else None.
        Uses key-based access instead of .get() — more reliable across
        all Streamlit versions and avoids AttributeError on st.secrets.
        """
        try:
            # Access secrets via key lookup — raises KeyError if missing
            url = st.secrets["SUPABASE_URL"]
            key = st.secrets["SUPABASE_KEY"]
            if not url or not key:
                return None
            from supabase import create_client
            return create_client(str(url), str(key))
        except KeyError:
            # Secrets not configured — running locally without secrets
            return None
        except Exception:
            # Any other error (import fail, network, etc.) — degrade gracefully
            return None

    # ── Supabase stats functions
    def _supabase_load(client):
        try:
            r = client.table("hfactor_stats").select("visits,hearts").eq("id", 1).execute()
            if r.data:
                return {"visits": r.data[0]["visits"], "hearts": r.data[0]["hearts"]}
        except Exception:
            pass
        return {"visits": 0, "hearts": 0}

    def _supabase_increment(client, field):
        """Atomic increment using Supabase RPC to avoid race conditions."""
        try:
            # Use raw SQL via rpc for atomic update
            client.rpc("increment_stat", {"field_name": field}).execute()
            return True
        except Exception:
            # Fallback: read-modify-write (non-atomic but acceptable at small scale)
            try:
                r = client.table("hfactor_stats").select(field).eq("id", 1).execute()
                current = r.data[0][field] if r.data else 0
                client.table("hfactor_stats").update(
                    {field: current + 1}
                ).eq("id", 1).execute()
                return True
            except Exception:
                return False

    def _supabase_log(client, ticker, currency, verdict, country):
        """Log each analysis event for usage analytics."""
        try:
            client.table("hfactor_usage_log").insert({
                "ticker": ticker,
                "currency": currency,
                "verdict": verdict,
                "country": country,
            }).execute()
        except Exception:
            pass

    # ── Local JSON fallback (for running on your own machine)
    # Safe path for local stats file — works on both local and cloud
    # Falls back to current working directory if __file__ is unavailable
    try:
        _base_dir = os.path.dirname(os.path.abspath(__file__))
    except (NameError, OSError):
        _base_dir = os.getcwd()
    STATS_FILE = os.path.join(_base_dir, '.hfactor_stats.json')

    def _local_load():
        try:
            with open(STATS_FILE) as f:
                return json.load(f)
        except Exception:
            return {"visits": 0, "hearts": 0}

    def _local_save(d):
        try:
            with open(STATS_FILE, "w") as f:
                json.dump(d, f)
        except Exception:
            pass

    def _local_increment(field):
        d = _local_load()
        d[field] = d.get(field, 0) + 1
        _local_save(d)

    # ── Unified interface — auto-selects backend
    try:
        _sb = _get_supabase()
    except Exception:
        _sb = None
    _using_supabase = _sb is not None

    def load_stats():
        if _using_supabase:
            return _supabase_load(_sb)
        return _local_load()

    def increment_stat(field):
        if _using_supabase:
            _supabase_increment(_sb, field)
        else:
            _local_increment(field)

    # ── Count visit once per browser session
    try:
        if "visit_counted" not in st.session_state:
            st.session_state["visit_counted"] = True
            increment_stat("visits")
        stats  = load_stats()
        visits = stats.get("visits", 0)
        hearts = stats.get("hearts", 0)
    except Exception:
        visits = 0
        hearts = 0

    # ── Log this analysis event (once per ticker per session)
    try:
        if _using_supabase and _sb is not None:
            log_key = f"logged_{ticker}"
            if log_key not in st.session_state:
                st.session_state[log_key] = True
                _supabase_log(_sb, ticker, currency_code, verdict,
                              info.get("country", "Unknown"))
    except Exception:
        pass

    # ── Heart reaction (once per session)
    if "user_hearted" not in st.session_state:
        st.session_state["user_hearted"] = False

    footer_left, footer_mid, footer_right = st.columns([3, 2, 3])

    with footer_mid:
        heart_label = "❤️ Thanks!" if st.session_state["user_hearted"] else "🤍 Love this app?"
        if st.button(heart_label, key="heart_btn", use_container_width=True):
            if not st.session_state["user_hearted"]:
                st.session_state["user_hearted"] = True
                try:
                    increment_stat("hearts")
                    stats  = load_stats()
                    hearts = stats.get("hearts", 0)
                except Exception:
                    pass
                st.rerun()

    with footer_left:
        backend_badge = (
            '<span style="font-size:9px;color:#0a3a1a;background:#0d2a14;'
            'border:1px solid #1a5a30;border-radius:4px;padding:1px 6px;'
            'margin-left:8px;">&#9729; cloud</span>'
            if _using_supabase else
            '<span style="font-size:9px;color:#1a3a5a;background:#0a1828;'
            'border:1px solid #1a3050;border-radius:4px;padding:1px 6px;'
            'margin-left:8px;">&#128187; local</span>'
        )
        st.markdown(
            f'<div style="font-family:monospace;font-size:10px;color:#1e3a5f;'
            f'letter-spacing:2px;padding-top:10px;">'
            f'&#9889; H-FACTOR &middot; FUNDAMENTAL ANALYSIS AGENT'
            f'{backend_badge}</div>',
            unsafe_allow_html=True
        )

    with footer_right:
        st.markdown(
            f'<div style="text-align:right;padding-top:8px;">'
            f'<span style="font-size:12px;color:#1e3a5f;margin-right:16px;">'
            f'&#128065; {visits:,} visits</span>'
            f'<span style="font-size:12px;color:#c0392b;">'
            f'&#10084; {hearts:,} reactions</span>'
            f'</div>',
            unsafe_allow_html=True
        )

    st.markdown(
        '<div style="text-align:center;font-size:11px;color:#1a2a3a;margin-top:4px;">'
        'Data: Yahoo Finance &middot; Educational Use Only &middot; Not Financial Advice'
        '</div>',
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
