import streamlit as st

def inject_custom_css():
    st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Poppins:wght@600;700;800;900&display=swap');

/* ── Base & Reset ── */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* ── Main background ── */
.stApp {
    background: linear-gradient(135deg, #0a0e1a 0%, #111827 50%, #0f172a 100%);
    min-height: 100vh;
}

/* ── Hide Streamlit branding ── */
#MainMenu, footer, header { visibility: hidden; }

/* ── Page header ── */
.page-header {
    background: linear-gradient(135deg, #1e293b 0%, #1a2744 100%);
    border: 1px solid rgba(99,179,237,0.15);
    border-radius: 16px;
    padding: 24px 32px;
    margin-bottom: 24px;
    display: flex;
    align-items: center;
    gap: 16px;
    box-shadow: 0 8px 32px rgba(0,0,0,0.4);
}
.page-header h1 {
    margin: 0;
    font-size: 2.22rem;
    background: linear-gradient(135deg, #fbbf24, #f59e0b);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 800;
}
.page-header p {
    margin: 8px 0 0 0;
    color: #94a3b8;
    font-size: 0.95rem;
    opacity: 0.9;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: rgba(30,41,59,0.8);
    border-radius: 12px;
    padding: 4px;
    gap: 4px;
    border: 1px solid rgba(255,255,255,0.08);
    backdrop-filter: blur(12px);
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px;
    color: #94a3b8;
    font-weight: 500;
    font-size: 0.88rem;
    padding: 8px 16px;
    transition: all 0.2s ease;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #1e40af, #1e3a8a) !important;
    color: #fff !important;
    font-weight: 600;
}

/* ── Section headers ── */
.section-title {
    font-family: 'Poppins', sans-serif;
    font-size: 1.5rem;
    font-weight: 700;
    color: #e2e8f0;
    margin-bottom: 4px;
}
.section-sub {
    color: #64748b;
    font-size: 0.82rem;
    margin-bottom: 20px;
}

/* ── Cards ── */
.card {
    background: rgba(30,41,59,0.7);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 14px;
    padding: 20px 24px;
    margin-bottom: 16px;
    backdrop-filter: blur(8px);
    box-shadow: 0 4px 24px rgba(0,0,0,0.3);
}

/* ── Metric cards ── */
.metric-card {
    background: linear-gradient(135deg, rgba(59,130,246,0.15), rgba(99,102,241,0.1));
    border: 1px solid rgba(99,102,241,0.25);
    border-radius: 12px;
    padding: 16px 20px;
    text-align: center;
}
.metric-value {
    font-family: 'Poppins', sans-serif;
    font-size: 2rem;
    font-weight: 800;
    color: #63b3ed;
    line-height: 1;
}
.metric-label {
    color: #64748b;
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-top: 4px;
}

/* ── Team badge pill ── */
.team-badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.05em;
}

/* ── Leaderboard row ── */
.lb-row {
    display: flex;
    align-items: center;
    gap: 14px;
    padding: 12px 16px;
    border-radius: 10px;
    margin-bottom: 8px;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
    border: 1px solid rgba(255,255,255,0.06);
}
.lb-row:hover {
    transform: translateX(4px);
    box-shadow: 0 4px 20px rgba(0,0,0,0.3);
}
.lb-rank {
    font-family: 'Poppins', sans-serif;
    font-size: 1.1rem;
    font-weight: 800;
    min-width: 28px;
    text-align: center;
}
.lb-logo {
    width: 40px;
    height: 40px;
    object-fit: contain;
    border-radius: 6px;
    background: rgba(255,255,255,0.08);
    padding: 3px;
}
.lb-team-name {
    flex: 1;
    font-weight: 600;
    font-size: 0.95rem;
}
.lb-abbr {
    font-size: 0.72rem;
    color: rgba(226, 232, 240, 0.7);
    font-weight: 400;
}
.lb-points {
    font-family: 'Poppins', sans-serif;
    font-weight: 700;
    font-size: 1rem;
}
.lb-gap {
    font-size: 0.78rem;
    color: rgba(226, 232, 240, 0.6);
    min-width: 60px;
    text-align: right;
}

/* ── Team header card ── */
.team-header {
    display: flex;
    align-items: center;
    gap: 20px;
    padding: 20px 28px;
    border-radius: 16px;
    margin-bottom: 20px;
    border: 1px solid rgba(255,255,255,0.1);
    box-shadow: 0 8px 32px rgba(0,0,0,0.4);
}
.team-header-name {
    font-family: 'Poppins', sans-serif;
    font-size: 1.6rem;
    font-weight: 800;
    line-height: 1.1;
}
.team-header-full {
    font-size: 0.85rem;
    color: rgba(226, 232, 240, 0.75);
    margin-top: 2px;
}

/* ── Player table ── */
.player-row {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 10px 16px;
    border-radius: 8px;
    margin-bottom: 6px;
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.05);
    transition: background 0.15s ease;
}
.player-row:hover {
    background: rgba(255,255,255,0.07);
}
.player-rank-num {
    font-size: 0.75rem;
    font-weight: 700;
    color: #94a3b8;
    min-width: 20px;
    text-align: center;
}
.player-name {
    flex: 1;
    font-weight: 500;
    font-size: 0.9rem;
    color: #e2e8f0;
}
.player-pts {
    font-family: 'Poppins', sans-serif;
    font-weight: 700;
    font-size: 0.95rem;
}

/* ── Refresh button ── */
.stButton > button {
    background: linear-gradient(135deg, #3b82f6, #6366f1);
    color: white;
    border: none;
    border-radius: 8px;
    padding: 8px 20px;
    font-weight: 600;
    font-size: 0.85rem;
    transition: all 0.2s ease;
    box-shadow: 0 4px 12px rgba(59,130,246,0.3);
}
.stButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 6px 20px rgba(59,130,246,0.4);
}

/* ── Selectbox ── */
.stSelectbox > div > div {
    background: rgba(30,41,59,0.8) !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    border-radius: 10px !important;
    color: #e2e8f0 !important;
}

/* ── Search input ── */
.stTextInput > div > div > input {
    background: rgba(30,41,59,0.8) !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    border-radius: 10px !important;
    color: #e2e8f0 !important;
}
.stTextInput > div > div > input::placeholder {
    color: #64748b !important;
    opacity: 1 !important;
}
/* Also target the label text above inputs */
.stTextInput label, .stSelectbox label, .stMultiSelect label,
.stFileUploader label, .stRadio label p {
    color: #94a3b8 !important;
}

/* ── Multiselect ── */
.stMultiSelect > div > div {
    background: rgba(30,41,59,0.8) !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    border-radius: 10px !important;
}

/* ── DataFrames ── */
.stDataFrame {
    border-radius: 12px;
    overflow: hidden;
    border: 1px solid rgba(255,255,255,0.07);
}

/* ── Password input ── */
.stTextInput input[type="password"] {
    background: rgba(30,41,51,0.9) !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    border-radius: 10px !important;
    color: #e2e8f0 !important;
}
/* Force password eye icon container to be dark */
.stTextInput [data-testid="stBaseButton-secondary"] {
    background-color: transparent !important;
    color: #94a3b8 !important;
    border: none !important;
}
.stTextInput div[data-baseweb="input"] {
    background-color: rgba(30,41,51,0.9) !important;
}

/* ── Expanders ── */
[data-testid="stExpander"] {
    background: rgba(30,41,59,0.7) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 12px !important;
}
[data-testid="stExpander"] summary {
    color: #e2e8f0 !important;
    font-weight: 600 !important;
}
[data-testid="stExpander"] summary:hover {
    color: #3b82f6 !important;
}
[data-testid="stExpander"] > div[role="region"] {
    background-color: transparent !important;
    color: #e2e8f0 !important;
}

/* ── DataFrames ── */
[data-testid="stDataFrame"] {
    background-color: #1a1e2e !important;
    border-radius: 12px !important;
}
/* This targets the underlying grid container if visible */
[data-testid="stDataFrame"] > div {
    background-color: #1a1e2e !important;
}

/* ── Lineup card ── */
.lineup-card {
    border-radius: 14px;
    padding: 20px;
    border: 2px solid rgba(255,255,255,0.1);
    margin-bottom: 16px;
}
.lineup-player {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 12px;
    border-radius: 6px;
    margin-bottom: 4px;
    background: rgba(0,0,0,0.15);
    font-size: 0.88rem;
}
.lineup-total {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 10px 12px;
    border-radius: 6px;
    font-weight: 700;
    font-size: 1rem;
    margin-top: 8px;
    background: rgba(0,0,0,0.25);
}

/* ── XI Leaderboard ── */
.xi-lb-row {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 14px 18px;
    border-radius: 10px;
    margin-bottom: 8px;
    border: 1px solid rgba(255,255,255,0.06);
    transition: transform 0.2s ease;
}
.xi-lb-row:hover { transform: translateX(4px); }

/* ── MVP banner ── */
.mvp-banner {
    border-radius: 14px;
    padding: 20px 28px;
    display: flex;
    align-items: center;
    gap: 16px;
    margin-bottom: 20px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.2);
}
.mvp-title {
    font-family: 'Poppins', sans-serif;
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.12em;
}
.mvp-name {
    font-family: 'Poppins', sans-serif;
    font-size: 1.4rem;
    font-weight: 800;
    color: #fff;
}
.mvp-pts {
    font-size: 0.9rem;
    color: rgba(226, 232, 240, 0.75);
}

/* Global labels and secondary text */
label[data-testid="stWidgetLabel"], .stMarkdown p, .stMarkdown li {
    color: #e2e8f0 !important;
}
code {
    background-color: rgba(255,255,255,0.1) !important;
    color: #f6ad55 !important;
    padding: 2px 4px !important;
    border-radius: 4px !important;
}

/* ── Premium Player Card (Tab 2 Upgrade) ── */
.player-card {
    display: flex;
    align-items: center;
    gap: 16px;
    padding: 16px 20px;
    border-radius: 16px;
    margin-bottom: 12px;
    border: 1px solid rgba(255,255,255,0.08);
    position: relative;
    overflow: hidden;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.player-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(0,0,0,0.4);
}
.player-card-logo-container {
    position: relative;
    width: 64px;
    height: 64px;
    flex-shrink: 0;
}
.player-card-logo {
    width: 100%;
    height: 100%;
    object-fit: contain;
    border-radius: 50%;
    background: rgba(255,255,255,0.08);
    padding: 6px;
    border: 2px solid rgba(255,255,255,0.1);
}
.player-card-rank {
    position: absolute;
    top: -4px;
    left: -4px;
    background: #1e40af;
    color: white;
    font-size: 0.7rem;
    font-weight: 800;
    padding: 2px 6px;
    border-radius: 8px;
    border: 2px solid #0a0e1a;
    z-index: 2;
}
.player-card-info {
    flex: 1;
}
.player-card-name {
    font-family: 'Poppins', sans-serif;
    font-size: 1.15rem;
    font-weight: 700;
    color: #ffffff;
    line-height: 1.2;
}
.player-card-team {
    font-size: 0.82rem;
    font-weight: 600;
    margin-top: 2px;
}
.player-card-metrics {
    text-align: right;
}
.player-card-points {
    font-family: 'Poppins', sans-serif;
    font-size: 1.3rem;
    font-weight: 800;
    line-height: 1;
}
.player-card-adjustment {
    font-size: 0.78rem;
    font-weight: 700;
    margin-top: 4px;
}
</style>
""", unsafe_allow_html=True)
