import streamlit as st
import pandas as pd
import json
import os
import base64
import io
from sqlalchemy import text
from sqlalchemy.pool import NullPool

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────
LOGO_DIR = os.path.join(os.path.dirname(__file__), "IPL LOGOS")
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

st.set_page_config(
    page_title="IPL 2026 Mock Auction Dashboard",
    layout="wide",
    page_icon=os.path.join(LOGO_DIR, "IPL.png") if os.path.exists(os.path.join(LOGO_DIR, "IPL.png")) else "🏏"
)

# ─────────────────────────────────────────────
# TEAM COLOURS & LOGOS
# ─────────────────────────────────────────────
TEAM_COLORS = {
    # bg = official fill, text = on-bg text, accent = always readable on dark dashboard
    "CSK":  {"bg": "#FFFF00", "text": "#073763", "accent": "#FFD700"},
    "DC":   {"bg": "#0076CF", "text": "#C00000", "accent": "#38BDF8"},
    "GT":   {"bg": "#1B2133", "text": "#E1C674", "accent": "#E1C674"},  # bg too dark → use gold
    "KKR":  {"bg": "#3A225D", "text": "#FFE599", "accent": "#C084FC"},  # bg too dark → use light purple
    "LSG":  {"bg": "#A21728", "text": "#FFFFFF", "accent": "#F87171"},  # brighten the red
    "MI":   {"bg": "#1155CC", "text": "#F1C232", "accent": "#60A5FA"},  # lighten the blue
    "PBKS": {"bg": "#FF0000", "text": "#FFFFFF", "accent": "#FF6B6B"},
    "RCB":  {"bg": "#CC0000", "text": "#FFFF00", "accent": "#FBBF24"},  # dark red → use amber
    "RR":   {"bg": "#FF6699", "text": "#073763", "accent": "#F472B6"},
    "SRH":  {"bg": "#FF9900", "text": "#000000", "accent": "#FB923C"},
    "UNSOLD": {"bg": "#FFFFFF", "text": "#FFFFFF", "accent": "#FFFFFF"},
}

TEAM_NAMES = {
    "CSK":  "Chennai Super Kings",
    "DC":   "Delhi Capitals",
    "GT":   "Gujarat Titans",
    "KKR":  "Kolkata Knight Riders",
    "LSG":  "Lucknow Super Giants",
    "MI":   "Mumbai Indians",
    "PBKS": "Punjab Kings",
    "RCB":  "Royal Challengers Bengaluru",
    "RR":   "Rajasthan Royals",
    "SRH":  "Sunrisers Hyderabad",
    "UNSOLD": "Unsold",
}


@st.cache_data
def get_logo_b64(team: str) -> str:
    path = os.path.join(LOGO_DIR, f"{team}.png")
    if os.path.exists(path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return ""

# ─────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────
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
    font-weight: 600 !important;
}

/* ── Custom Navigation (Radio as Tabs) ── */
div[data-testid="stRadio"] > div {
    background: rgba(30,41,59,0.8);
    border-radius: 12px;
    padding: 4px;
    gap: 4px;
    border: 1px solid rgba(255,255,255,0.08);
    backdrop-filter: blur(12px);
    display: flex;
    flex-wrap: wrap;
}
div[data-testid="stRadio"] label {
    border-radius: 8px;
    color: #94a3b8 !important;
    font-weight: 500;
    font-size: 0.88rem;
    padding: 6px 14px;
    transition: all 0.2s ease;
    cursor: pointer;
    border: none !important;
    background: transparent !important;
}
div[data-testid="stRadio"] label:hover {
    background: rgba(255,255,255,0.05) !important;
    color: #fff !important;
}
/* Highlight selected tab */
div[data-testid="stRadio"] label:has(input:checked) {
    background: linear-gradient(135deg, #1e40af, #1e3a8a) !important;
    color: #fff !important;
    font-weight: 600 !important;
    box-shadow: 0 4px 12px rgba(30,64,175,0.3) !important;
}
div[data-testid="stRadio"] label[data-selected="true"] {
    background: linear-gradient(135deg, #1e40af, #1e3a8a) !important;
    color: #fff !important;
    font-weight: 600 !important;
    box-shadow: 0 4px 12px rgba(30,64,175,0.3) !important;
}
/* Hide the radio circles and headers */
div[data-testid="stRadio"] div[role="radiogroup"] > label > div:first-child {
    display: none !important;
}
div[data-testid="stRadio"] label[data-testid="stWidgetLabel"] {
    display: none !important;
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

# ─────────────────────────────────────────────
# DATABASE CONFIG & MIGRATION
# ─────────────────────────────────────────────
@st.cache_resource
def init_connection():
    if "neon_url" not in st.secrets:
        return None
    
    c = st.connection(
        "neon", 
        type="sql", 
        url=st.secrets["neon_url"],
        poolclass=NullPool
    )
    
    # Run migration/sync check ONLY ONCE during app startup
    try:
        with c.session as s:
            s.execute(text("""
                CREATE TABLE IF NOT EXISTS app_state (
                    key VARCHAR(50) PRIMARY KEY,
                    data JSONB
                );
            """))
            count = s.execute(text("SELECT COUNT(*) FROM app_state")).scalar()
            if count == 0:
                files = {
                    "squads": os.path.join(DATA_DIR, "squads.json"), 
                    "lineups": os.path.join(DATA_DIR, "lineups.json"), 
                    "master": os.path.join(DATA_DIR, "master.json"), 
                    "mvp": os.path.join(DATA_DIR, "mvp.json")
                }
                base = os.path.dirname(__file__)
                for k, fname in files.items():
                    fpath = os.path.join(base, fname)
                    if os.path.exists(fpath):
                        with open(fpath, "r") as f:
                            jdata = json.load(f)
                            s.execute(text("INSERT INTO app_state (key, data) VALUES (:k, CAST(:dat AS JSONB)) ON CONFLICT (key) DO UPDATE SET data = EXCLUDED.data;"), {"k": k, "dat": json.dumps(jdata)})
                s.commit()
            else:
                s.commit()
    except Exception as e:
        # We don't want to crash the whole app if DB is briefly unavailable
        pass
    return c

conn = init_connection()
USE_DATABASE = conn is not None

def set_app_state(key: str, data):
    if USE_DATABASE:
        with conn.session as s:
            s.execute(text("INSERT INTO app_state (key, data) VALUES (:k, CAST(:dat AS JSONB)) ON CONFLICT (key) DO UPDATE SET data = EXCLUDED.data;"), {"k": key, "dat": json.dumps(data)})
            s.commit()

def get_app_state(key: str):
    if USE_DATABASE:
        try:
            with conn.session as s:
                res = s.execute(text("SELECT data FROM app_state WHERE key = :k"), {"k": key}).fetchone()
                if res and res[0]:
                    return res[0]
        except Exception:
            return None
    return None


@st.cache_data(ttl=300)
def load_mvp_points():
    """Load player points list from database or mvp.json."""
    db_data = get_app_state("mvp")
    if db_data is not None:
        return db_data
        
    try:
        with open(os.path.join(DATA_DIR, "mvp.json"), "r") as f:
            return json.load(f)
    except Exception:
        return []


@st.cache_data(ttl=300)
def load_squads():
    """Load team rosters from database or squads.json."""
    db_data = get_app_state("squads")
    if db_data is not None:
        return db_data
        
    try:
        with open(os.path.join(DATA_DIR, "squads.json"), "r") as f:
            return json.load(f)
    except Exception:
        return {}


def load_data():
    """Construct the master DataFrame dynamically by merging MVP points and Squads."""
    mvp_list = load_mvp_points()
    full_squads = load_squads()
    
    # Extract offsets if they exist
    offsets = full_squads.get("__offsets__", {})
    # Filter out metaladata keys for squad mapping
    squads_only = {k: v for k, v in full_squads.items() if k != "__offsets__"}
    
    # Pre-map players to teams for fast lookup
    PLAYER_TO_TEAM = {
        p.lower(): team
        for team, players in squads_only.items()
        for p in players
    }
    
    processed_names = set()
    master_rows = []
    for item in mvp_list:
        name = item.get("player", "")
        raw_pts = item.get("impact", 0.0)
        offset = offsets.get(name, 0.0)
        adj_pts = raw_pts + offset
        
        team = PLAYER_TO_TEAM.get(name.lower(), "UNSOLD")
        master_rows.append({
            "player": name,
            "team": team,
            "impact": adj_pts,
            "raw_impact": raw_pts,
            "offset": offset
        })
        processed_names.add(name.lower())
        
    # Add any manual adjustments for players/entities not in the MVP list
    for name, offset in offsets.items():
        if name.lower() not in processed_names:
            team = PLAYER_TO_TEAM.get(name.lower(), "UNSOLD")
            master_rows.append({
                "player": name,
                "team": team,
                "impact": offset,
                "raw_impact": 0.0,
                "offset": offset
            })
    
    return pd.DataFrame(master_rows)


@st.cache_data(ttl=300)
def load_lineups():
    db_data = get_app_state("lineups")
    if db_data is not None:
        return db_data
        
    path = os.path.join(DATA_DIR, "lineups.json")
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return {}


def save_lineups(lineups: dict):
    set_app_state("lineups", lineups)
    # Bust the cache so the next read picks up changes
    load_lineups.clear()
    
    # Still write to local file as immediate backup
    path = os.path.join(DATA_DIR, "lineups.json")
    try:
        with open(path, "w") as f:
            json.dump(lineups, f, indent=2)
    except Exception:
        pass


def clear_lineup_callback(team_name, players):
    """Callback to safely clear session state for a team's lineup."""
    if "ordered_lineups" in st.session_state:
        st.session_state.ordered_lineups[team_name] = []
    for p in players:
        k = f"chk_{team_name}_{p}"
        if k in st.session_state:
            st.session_state[k] = False
    # Persist the cleared lineup to DB and file
    lineups = load_lineups()
    lineups[team_name] = []
    save_lineups(lineups)

def reorder_lineup(team_name, index, direction):
    """Helper to move a player up or down in the session state ordered list."""
    if "ordered_lineups" not in st.session_state:
        return
    xi = st.session_state.ordered_lineups[team_name][:] # copy
    if direction == "up" and index > 0:
        xi[index], xi[index-1] = xi[index-1], xi[index]
    elif direction == "down" and index < len(xi) - 1:
        xi[index], xi[index+1] = xi[index+1], xi[index]
    
    st.session_state.ordered_lineups[team_name] = xi


def process_excel(file_bytes: bytes, squads: dict) -> tuple[list, list]:
    """Process uploaded Excel bytes → returns (mvp_rows, unmatched_players)."""
    PLAYER_TO_TEAM = {
        p.lower(): team
        for team, players in squads.items()
        for p in players
    }

    raw = pd.read_excel(io.BytesIO(file_bytes))
    raw.columns = [c.lower().strip() for c in raw.columns]

    mvp_rows = []
    current_impact = None

    for _, row in raw.iterrows():
        player_val = row.get("player")
        impact_val = row.get("total impact")

        # Rank rows have a number in the player column
        if isinstance(player_val, (int, float)) and not pd.isna(impact_val):
            current_impact = float(impact_val)
        elif isinstance(player_val, str) and player_val.strip():
            mvp_rows.append({
                "player": player_val.strip(),
                "impact": current_impact if current_impact is not None else 0.0
            })

    unmatched = []
    for row in mvp_rows:
        name = row["player"]
        team = PLAYER_TO_TEAM.get(name.lower(), "UNSOLD")
        if team == "UNSOLD":
            unmatched.append(name)

    return mvp_rows, unmatched


FULL_SQUADS = load_squads()
SQUADS = {k: v for k, v in FULL_SQUADS.items() if k != "__offsets__"}
OFFSETS = FULL_SQUADS.get("__offsets__", {})
df = load_data()

# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
col_h1, col_h2 = st.columns([1, 8])
with col_h1:
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
with col_h2:
    st.markdown("""
    <div class="page-header">
        <div>
            <h1>🏏 IPL 2026 Mock Auction Dashboard</h1>
            <p>IPL 2026 Mock Auction • QCC Live</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

col_r1, col_r2 = st.columns([1, 8])
with col_r2:
    st.markdown("""
    <style>
    div.stButton > button:first-child {
        background: linear-gradient(135deg, #1e40af, #1e3a8a);
        color: white;
        border: none;
        padding: 10px 24px;
        border-radius: 8px;
        font-weight: 600;
    }
    div.stButton > button:first-child:hover {
        background: linear-gradient(135deg, #2563eb, #1e40af);
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)
    if st.button("🔄 Refresh Data"):
        st.cache_data.clear()
        st.rerun()

# ─────────────────────────────────────────────
# NAVIGATION (LAZY LOADING)
# ─────────────────────────────────────────────
tab_options = [
    "🏆 Leaderboard",
    "📊 Players",
    "🏏 Teams",
    "⭐ Playing XIs",
    "📋 XI Leaderboard",
    "🚫 Unsold",
    "🔄 Update Data",
    "👥 Edit Squads",
    "✏️ Edit Lineups",
]

# Create the navigation menu (styled like tabs)
active_tab = st.radio(
    "Navigation",
    options=tab_options,
    horizontal=True,
    label_visibility="collapsed"
)

# ─────────────────────────────────────────────
# 🏆 LEADERBOARD
# ─────────────────────────────────────────────
if active_tab == "🏆 Leaderboard":
    st.markdown("<div class='section-title'>🏆 Squad Points Standings</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-sub'>Ranked by total ESPNCricinfo MVP points</div>", unsafe_allow_html=True)

    team_totals = (
        df[df["team"] != "UNSOLD"]
        .groupby("team")["impact"]
        .sum()
        .sort_values(ascending=False)
        .reset_index()
    )

    # Ensure all teams from SQUADS appear even with 0 points
    for team_key in SQUADS:
        if team_key not in team_totals["team"].values:
            team_totals = pd.concat([team_totals, pd.DataFrame([{"team": team_key, "impact": 0.0}])], ignore_index=True)
    team_totals = team_totals.sort_values(by="impact", ascending=False).reset_index(drop=True)

    top_score = team_totals.iloc[0]["impact"] if not team_totals.empty else 0.0

    rank_icons = {1: "🥇", 2: "🥈", 3: "🥉"}

    for i, row in team_totals.iterrows():
        rank = i + 1
        team = row["team"]
        pts = row["impact"]
        gap = top_score - pts
        colors = TEAM_COLORS.get(team, {"bg": "#1e293b", "text": "#e2e8f0", "accent": "#60a5fa"})
        full_name = TEAM_NAMES.get(team, team)
        logo_b64 = get_logo_b64(team)
        logo_html = (
            f'<img class="lb-logo" src="data:image/png;base64,{logo_b64}" />'
            if logo_b64 else
            f'<div style="width:40px;height:40px;border-radius:6px;background:{colors["bg"]};display:flex;align-items:center;justify-content:center;font-weight:800;font-size:0.7rem;color:{colors["text"]}">{team}</div>'
        )
        rank_icon = rank_icons.get(rank, f"#{rank}")
        gap_display = f"−{gap:.1f}" if gap > 0 else "LEADER"

        st.markdown(f"""
        <div class="lb-row" style="background: linear-gradient(135deg, {colors['accent']}18, {colors['accent']}06);">
            <span class="lb-rank" style="color:{colors['accent']}">{rank_icon}</span>
            {logo_html}
            <div class="lb-team-name">
                <span style="color:{colors['accent']}; font-weight:700;">{full_name}</span><br>
                <span class="lb-abbr">{team}</span>
            </div>
            <div style="text-align:right">
                <div class="lb-points" style="color:{colors['accent']}">{pts:.1f} pts</div>
                <div class="lb-gap">{gap_display}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
# 📊 PLAYERS
# ─────────────────────────────────────────────
elif active_tab == "📊 Players":
    st.markdown("<div class='section-title'>📊 Player Performance</div>", unsafe_allow_html=True)
    
    # Get value from session state for lazy loading logic
    classical_ui = st.session_state.get("classic_players", False)

    if not df.empty:
        top = df.sort_values(by="impact", ascending=False).iloc[0]
        top_team_colors = TEAM_COLORS.get(top["team"], {"bg": "#1e293b", "text": "#fff", "accent": "#60a5fa"})
        top_logo_b64 = get_logo_b64(top["team"])
        top_logo_html = (
            f'<img style="width:48px;height:48px;object-fit:contain;border-radius:8px;background:rgba(255,255,255,0.1);padding:4px" src="data:image/png;base64,{top_logo_b64}" />'
            if top_logo_b64 else ""
        )
        st.markdown(f"""
        <div class="mvp-banner" style="background: linear-gradient(135deg, {top_team_colors['accent']}15, {top_team_colors['accent']}08); border: 1px solid {top_team_colors['accent']}33;">
            {top_logo_html}
            <div>
                <div class="mvp-title" style="color:{top_team_colors['accent']}">MVP Leader</div>
                <div class="mvp-name">{top['player']}</div>
                <div class="mvp-pts" style="color:#e2e8f0; opacity:0.8; font-size:0.85rem;">{top['team']} · {top['impact']:.1f} Impact points</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("No player data available yet. Upload MVP data to get started.")

    col_s1, col_s2 = st.columns([2, 1])
    with col_s1:
        search = st.text_input("🔍 Search player", placeholder="Type a player name…")
    with col_s2:
        sort_by = st.selectbox("Sort by", ["Points (High to Low)", "Points (Low to High)", "Name (A-Z)", "Team (A-Z)", "Adjustment (High to Low)", "Adjustment (Low to High)"])

    # ── Initial Sorting & Filter ──
    # Rank is always based on impact points across all players
    df_sorted = df.sort_values(by="impact", ascending=False).reset_index(drop=True)
    df_sorted["Rank"] = df_sorted.index + 1
    
    filtered = df_sorted.copy()
    if search:
        filtered = filtered[filtered["player"].str.contains(search, case=False, na=False, regex=False)]
    
    # ── Re-sort filtered results if requested ──
    if sort_by == "Points (Low to High)":
        filtered = filtered.sort_values(by="impact", ascending=True)
    elif sort_by == "Name (A-Z)":
        filtered = filtered.sort_values(by="player", ascending=True)
    elif sort_by == "Team (A-Z)":
        filtered = filtered.sort_values(by="team", ascending=True)
    elif sort_by == "Adjustment (High to Low)":
        filtered = filtered.sort_values(by="offset", ascending=False)
    elif sort_by == "Adjustment (Low to High)":
        filtered = filtered.sort_values(by="offset", ascending=True)
    # Default is the global Rank (Points desc)
    
    # ── Pagination ──
    if "player_limit" not in st.session_state:
        st.session_state.player_limit = 25
    
    display_list = filtered.head(st.session_state.player_limit)

    if classical_ui:
        # ── Classical UI (Full Dataframe) ──
        st.dataframe(
            filtered[["Rank", "player", "team", "impact", "offset"]],
            width="stretch",
            hide_index=True,
            column_config={
                "impact": st.column_config.NumberColumn("Points", format="%.1f"),
                "offset": st.column_config.NumberColumn("Adj", format="%.1f"),
                "player": "Name",
                "team": "Squad"
            }
        )
    else:
        # ── Premium UI (Cards) ──
        for _, row in display_list.iterrows():
            name = row["player"]
            team = row["team"]
            pts = row["impact"]
            offset = row["offset"]
            rank = row["Rank"]
            
            c = TEAM_COLORS.get(team, {"bg": "#1e293b", "text": "#e2e8f0", "accent": "#60a5fa"})
            logo_b64 = get_logo_b64(team)
            logo_html = (
                f'<img class="player-card-logo" src="data:image/png;base64,{logo_b64}" />'
                if logo_b64 else 
                f'<div class="player-card-logo" style="background:{c["bg"]}; display:flex; align-items:center; justify-content:center; color:{c["text"]}; font-size:1rem; font-weight:800;">{team[0]}</div>'
            )
            
            # Offset color logic
            if offset > 0:
                off_color, off_prefix = "#4ade80", "+"
            elif offset < 0:
                off_color, off_prefix = "#f87171", "" # negative sign included in offset
            else:
                off_color, off_prefix = "#64748b", ""
                
            st.markdown(f"""
            <div class="player-card" style="background: linear-gradient(135deg, {c['bg']}25, {c['bg']}08); border-color: {c['accent']}33;">
                <div class="player-card-logo-container">
                    <div class="player-card-rank">#{int(rank)}</div>
                    {logo_html}
                </div>
                <div class="player-card-info">
                    <div class="player-card-name">{name}</div>
                    <div class="player-card-team" style="color: {c['accent']}">{TEAM_NAMES.get(team, team)}</div>
                </div>
                <div class="player-card-metrics">
                    <div class="player-card-points" style="color: {c['accent']}">{pts:.1f}</div>
                    <div class="player-card-adjustment" style="color: {off_color}">Adj: {off_prefix}{offset:.1f}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        if len(filtered) > st.session_state.player_limit:
            if st.button(f"Load more ({len(filtered) - st.session_state.player_limit} remaining)", use_container_width=True):
                st.session_state.player_limit += 25
                st.rerun()

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
    st.checkbox("💾 Classical UI", value=classical_ui, key="classic_players", help="Use standard dataframes for better performance")

# ─────────────────────────────────────────────
# 🏏 TEAMS
# ─────────────────────────────────────────────
elif active_tab == "🏏 Teams":
    st.markdown("<div class='section-title'>🏏 Team Breakdown</div>", unsafe_allow_html=True)

    team = st.selectbox("Select Team", list(SQUADS.keys()), format_func=lambda t: f"{t} — {TEAM_NAMES.get(t, t)}")
    if not team or not SQUADS:
        st.info("No team data available.")
        st.stop()
    players = SQUADS[team]
    colors = TEAM_COLORS.get(team, {"bg": "#1e293b", "text": "#e2e8f0", "accent": "#60a5fa"})
    full_name = TEAM_NAMES.get(team, team)
    logo_b64 = get_logo_b64(team)
    logo_html = (
        f'<img style="width:72px;height:72px;object-fit:contain;border-radius:10px;background:rgba(255,255,255,0.08);padding:6px" src="data:image/png;base64,{logo_b64}" />'
        if logo_b64 else ""
    )

    # Team header card
    st.markdown(f"""
    <div class="team-header" style="background: linear-gradient(135deg, {colors['accent']}22, {colors['accent']}0a);">
        {logo_html}
        <div>
            <div class="team-header-name" style="color:{colors['accent']}">{full_name}</div>
            <div class="team-header-full" style="color:#94a3b8">{team}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Build player data
    rows = []
    for p in players:
        match = df[df["player"].str.contains(p, case=False, na=False, regex=False)]
        pts = match.iloc[0]["impact"] if not match.empty else 0.0
        rows.append({"Player": p, "Points": pts})

    team_df = pd.DataFrame(rows).sort_values(by="Points", ascending=False).reset_index(drop=True)
    team_df["Rank"] = team_df.index + 1

    # Render custom player rows
    total_pts = team_df["Points"].sum()

    for _, r in team_df.iterrows():
        pts = r["Points"]
        p_name = r["Player"]
        pts_color = colors["accent"] if pts > 0 else ("#ef4444" if pts < 0 else "#64748b")
        
        st.markdown(f"""
        <div class="player-row">
            <span class="player-rank-num">#{int(r['Rank'])}</span>
            <span class="player-name">{p_name}</span>
            <span class="player-pts" style="color:{pts_color}">{pts:.1f}</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style="display:flex;justify-content:space-between;align-items:center;padding:14px 16px;
        border-radius:10px;margin-top:8px;
        background: linear-gradient(135deg, {colors['accent']}22, {colors['accent']}0a);
        border: 1px solid {colors['accent']}44;">
        <span style="font-weight:700;color:#e2e8f0;font-size:0.9rem;">Total Squad Points</span>
        <span style="font-family:'Poppins',sans-serif;font-weight:800;font-size:1.2rem;color:{colors['accent']}">{total_pts:.1f} pts</span>
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
# ⭐ PLAYING XIs
# ─────────────────────────────────────────────
elif active_tab == "⭐ Playing XIs":
    st.markdown("<div class='section-title'>⭐ Playing XIs</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-sub'>View selected playing lineups for each team</div>", unsafe_allow_html=True)

    lineups = load_lineups()

    # ── Display all team lineups ──
    teams_with_xi = [t for t in SQUADS if t in lineups and lineups[t]]
    teams_without = [t for t in SQUADS if t not in lineups or not lineups[t]]

    if not teams_with_xi:
        st.info("No lineups set yet. Use the **✏️ Edit Lineups** tab to add your first playing XI.")
    else:
        cols_per_row = 2
        team_list = list(SQUADS.keys())
        for i in range(0, len(team_list), cols_per_row):
            cols = st.columns(cols_per_row)
            for j, team_key in enumerate(team_list[i:i + cols_per_row]):
                with cols[j]:
                    c = TEAM_COLORS.get(team_key, {"bg": "#1e293b", "text": "#e2e8f0", "accent": "#60a5fa"})
                    logo_b64 = get_logo_b64(team_key)
                    logo_html = (
                        f'<img style="width:44px;height:44px;object-fit:contain;border-radius:8px;background:rgba(255,255,255,0.08);padding:4px" src="data:image/png;base64,{logo_b64}" />'
                        if logo_b64 else ""
                    )
                    xi = lineups.get(team_key, [])
                    xi_total = 0.0
                    xi_rows_html = ""

                    if xi:
                        for idx, p in enumerate(xi):
                            match = df[df["player"].str.contains(p, case=False, na=False, regex=False)]
                            pts = match.iloc[0]["impact"] if not match.empty else 0.0
                            xi_total += pts
                            pts_color = c["accent"] if pts > 0 else ("#ef4444" if pts < 0 else "#94a3b8")
                            xi_rows_html += f'<div class="lineup-player"><span style="color:#e2e8f0;"><b style="color:{c["accent"]};margin-right:8px;">#{idx+1}</b> {p}</span><span style="font-weight:700;color:{pts_color}">{pts:.1f}</span></div>'

                        xi_rows_html += f'<div class="lineup-total" style="border-top:1px solid {c["accent"]}44;margin-top:6px;"><span style="color:#e2e8f0;">Total ({len(xi)})</span><span style="font-weight:700;color:{c["accent"]}">{xi_total:.1f} pts</span></div>'
                    else:
                        xi_rows_html = "<div style='color:#475569;font-size:0.82rem;padding:8px'>No lineup set</div>"

                    st.markdown(f"""
                    <div class="lineup-card" style="background:linear-gradient(135deg,{c['accent']}12,{c['accent']}06);border-color:{c['accent']}33;">
                        <div style="display:flex;align-items:center;gap:12px;margin-bottom:14px;border-bottom:1px solid {c['accent']}33;padding-bottom:12px;">
                            {logo_html}
                            <div>
                                <div style="font-family:'Poppins',sans-serif;font-weight:700;font-size:1rem;color:{c['accent']}">{TEAM_NAMES.get(team_key,'')}</div>
                                <div style="font-size:0.72rem;color:#64748b">{team_key}</div>
                            </div>
                        </div>
                        {xi_rows_html}
                    </div>
                    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
# 📋 XI LEADERBOARD
# ─────────────────────────────────────────────
elif active_tab == "📋 XI Leaderboard":
    st.markdown("<div class='section-title'>📋 Playing XI Leaderboard</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-sub'>Team Standings based on playing lineups only</div>", unsafe_allow_html=True)
    lineups = load_lineups()
    xi_standings = []

    for team_key, squad in SQUADS.items():
        xi = lineups.get(team_key, [])
        if not xi:
            continue
        total = 0.0
        for p in xi:
            match = df[df["player"].str.contains(p, case=False, na=False, regex=False)]
            if not match.empty:
                total += match.iloc[0]["impact"]
        xi_standings.append({"team": team_key, "points": total, "size": len(xi)})

    if not xi_standings:
        st.info("No lineups set yet. Use the **✏️ Edit Lineups** tab to add your first playing XI.")
    else:
        xi_standings.sort(key=lambda x: x["points"], reverse=True)
        top_xi = xi_standings[0]["points"]

        for i, item in enumerate(xi_standings):
            rank = i + 1
            team_key = item["team"]
            pts = item["points"]
            gap = top_xi - pts
            c = TEAM_COLORS.get(team_key, {"bg": "#1e293b", "text": "#e2e8f0", "accent": "#60a5fa"})
            logo_b64 = get_logo_b64(team_key)
            logo_html = (
                f'<img class="lb-logo" src="data:image/png;base64,{logo_b64}" />'
                if logo_b64 else
                f'<div style="width:40px;height:40px;border-radius:6px;background:{c["bg"]};display:flex;align-items:center;justify-content:center;font-weight:800;font-size:0.7rem;color:{c["text"]}">{team_key}</div>'
            )
            rank_icons_xi = {1: "🥇", 2: "🥈", 3: "🥉"}
            rank_icon = rank_icons_xi.get(rank, f"#{rank}")
            gap_display = f"−{gap:.1f}" if gap > 0 else "LEADER"

            st.markdown(f"""
            <div class="xi-lb-row" style="background: linear-gradient(135deg, {c['accent']}18, {c['accent']}06);">
                <span class="lb-rank" style="color:{c['accent']}">{rank_icon}</span>
                {logo_html}
                <div class="lb-team-name">
                    <span style="color:{c['accent']}; font-weight:700;">{TEAM_NAMES.get(team_key, team_key)}</span><br>
                    <span class="lb-abbr">{team_key} · Playing {item['size']}</span>
                </div>
                <div style="text-align:right">
                    <div class="lb-points" style="color:{c['accent']}">{pts:.1f} pts</div>
                    <div class="lb-gap">{gap_display}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # Teams with no lineup set
        missing = [t for t in SQUADS if t not in {x["team"] for x in xi_standings}]
        if missing:
            st.markdown("<div style='color:#475569;font-size:0.8rem;margin-top:12px'>⚠️ No lineup set: " + ", ".join(missing) + "</div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# 🚫 UNSOLD
# ─────────────────────────────────────────────
elif active_tab == "🚫 Unsold":
    st.markdown("<div class='section-title'>🚫 Unsold Players</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-sub'>Players not acquired in the mock auction</div>", unsafe_allow_html=True)

    # Get value from session state
    classical_ui_unsold = st.session_state.get("classic_unsold", False)

    unsold_df = df[df["team"] == "UNSOLD"].copy()
    
    col_u1, col_u2 = st.columns([2, 1])
    with col_u1:
        search_unsold = st.text_input("🔍 Search", placeholder="Filter unsold players…", key="unsold_search")
    with col_u2:
        sort_unsold = st.selectbox("Sort by", ["Points (High to Low)", "Points (Low to High)", "Name (A-Z)"], key="unsold_sort")

    if search_unsold:
        unsold_df = unsold_df[unsold_df["player"].str.contains(search_unsold, case=False, na=False, regex=False)]

    if sort_unsold == "Points (High to Low)":
        unsold_df = unsold_df.sort_values(by="impact", ascending=False)
    elif sort_unsold == "Points (Low to High)":
        unsold_df = unsold_df.sort_values(by="impact", ascending=True)
    elif sort_unsold == "Name (A-Z)":
        unsold_df = unsold_df.sort_values(by="player", ascending=True)

    unsold_df = unsold_df.reset_index(drop=True)
    unsold_df["Rank"] = unsold_df.index + 1

    # ── Pagination ──
    if "unsold_limit" not in st.session_state:
        st.session_state.unsold_limit = 25
    
    display_unsold = unsold_df.head(st.session_state.unsold_limit)

    if display_unsold.empty:
        st.info("No unsold players found.")
    else:
        if classical_ui_unsold:
            st.dataframe(
                display_unsold[["Rank", "player", "impact"]], 
                width="stretch", 
                hide_index=True,
                column_config={
                    "Rank": st.column_config.NumberColumn(format="%d"),
                    "player": "Player",
                    "impact": st.column_config.NumberColumn("Points", format="%.1f")
                }
            )
        else:
            for _, row in display_unsold.iterrows():
                name = row["player"]
                pts = row["impact"]
                rank = row["Rank"]
                
                # Use UNSOLD logo and white accent
                c = TEAM_COLORS.get("UNSOLD", {"bg": "#1e293b", "text": "#ffffff", "accent": "#ffffff"})
                logo_b64 = get_logo_b64("UNSOLD")
                logo_html = (
                    f'<img class="player-card-logo" src="data:image/png;base64,{logo_b64}" />'
                    if logo_b64 else 
                    f'<div class="player-card-logo" style="background:{c["bg"]}; display:flex; align-items:center; justify-content:center; color:{c["text"]}; font-size:1rem; font-weight:800;">U</div>'
                )
                
                st.markdown(f"""
                <div class="player-card" style="background: linear-gradient(135deg, {c['bg']}25, {c['bg']}08); border-color: {c['accent']}33;">
                    <div class="player-card-logo-container">
                        <div class="player-card-rank">#{int(rank)}</div>
                        {logo_html}
                    </div>
                    <div class="player-card-info">
                        <div class="player-card-name">{name}</div>
                        <div class="player-card-team" style="color: {c['accent']}">{TEAM_NAMES.get("UNSOLD", "Unsold")}</div>
                    </div>
                    <div class="player-card-metrics">
                        <div class="player-card-points" style="color: {c['accent']}">{pts:.1f}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
        st.checkbox("💾 Classical UI", value=classical_ui_unsold, key="classic_unsold", help="Use standard dataframes for better performance")

# ─────────────────────────────────────────────
# 🔄 UPDATE DATA
# ─────────────────────────────────────────────
elif active_tab == "🔄 Update Data":
    st.markdown("<div class='section-title'>🔄 Update Data</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-sub'>Upload a new MVP Excel sheet to regenerate mvp.json and master.json</div>", unsafe_allow_html=True)

    # ── Password gate ──
    upd_pwd = st.text_input("🔐 Enter Admin password", type="password", key="update_pwd")
    correct_pwd = st.secrets.get("admin_password")

    if not upd_pwd:
        st.markdown("""
        <div class="card" style="border-color:rgba(99,102,241,0.3)">
            <div style="color:#94a3b8;font-size:0.88rem;line-height:1.7">
                <b style="color:#e2e8f0">How it works:</b><br>
                1. Enter the admin password above<br>
                2. Upload your updated <code>MVP.xlsx</code> file<br>
                3. Preview the parsed data<br>
                4. Click <b>Save & Update</b> — mvp.json and master.json are regenerated instantly
            </div>
        </div>
        """, unsafe_allow_html=True)

        with st.expander("ℹ️ How to create MVP.xlsx"):
            st.markdown("""
            1. Go to the [ESPNCricinfo MVP Page](https://www.espncricinfo.com/series/ipl-2026-1510719/most-valuable-players).
            2. Copy the MVP table starting from the headers down to the required players.
            """)
            try:
                st.image("assets/img1.png", caption="Copying from ESPNCricinfo table")
            except Exception:
                pass
            
            st.markdown("""
            3. Paste it carefully into an empty Excel file so that it has the **Player** and **Total Impact** columns.
            4. Save it as `MVP.xlsx`.
            """)
            try:
                st.image("assets/img3.png", caption="Pasting into Excel")
            except Exception:
                pass

    elif upd_pwd != correct_pwd:
        st.error("❌ Incorrect password")

    else:
        st.success("✅ Access granted")
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

        uploaded = st.file_uploader(
            "Upload MVP.xlsx",
            type=["xlsx"],
            help="Must have 'Player' and 'Total Impact' columns in the same format as the current MVP.xlsx"
        )

        if uploaded is not None:
            file_bytes = uploaded.read()

            try:
                with st.spinner("Parsing Excel…"):
                    mvp_rows, unmatched = process_excel(file_bytes, SQUADS)

                # ── Preview ──
                st.markdown("<div class='section-title' style='font-size:1.1rem;margin-top:16px'>📋 Preview</div>", unsafe_allow_html=True)

                col_prev1, col_prev2, col_prev3 = st.columns(3)
                with col_prev1:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-value" style="color:#63b3ed">{len(mvp_rows)}</div>
                        <div class="metric-label">Players parsed</div>
                    </div>
                    """, unsafe_allow_html=True)
                with col_prev2:
                    matched_count = len(mvp_rows) - len(unmatched)
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-value" style="color:#48bb78">{matched_count}</div>
                        <div class="metric-label">Matched to squads</div>
                    </div>
                    """, unsafe_allow_html=True)
                with col_prev3:
                    unsold_color = "#f6ad55" if unmatched else "#48bb78"
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-value" style="color:{unsold_color}">{len(unmatched)}</div>
                        <div class="metric-label">Unsold / unmatched</div>
                    </div>
                    """, unsafe_allow_html=True)

                st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

                # Top 15 preview table (Calculate teams on the fly for preview)
                PLAYER_TO_TEAM_LOCAL = {p.lower(): t for t, players in SQUADS.items() for p in players}
                preview_list = []
                for row in mvp_rows[:15]:
                    name = row["player"]
                    preview_list.append({
                        "Player": name,
                        "Team": PLAYER_TO_TEAM_LOCAL.get(name.lower(), "Unsold"),
                        "Points": row["impact"]
                    })
                
                preview_df = pd.DataFrame(preview_list)
                preview_df.index = range(1, len(preview_df) + 1)
                st.markdown("<div style='color:#94a3b8;font-size:0.8rem;margin-bottom:6px'>Top 15 preview:</div>", unsafe_allow_html=True)
                st.dataframe(
                    preview_df, 
                    width="stretch", 
                    hide_index=False,
                    column_config={
                        "Points": st.column_config.NumberColumn(format="%.1f")
                    }
                )

                # Unmatched warning
                if unmatched:
                    st.warning(f"⚠️ **{len(unmatched)} player(s) not found in any squad** — they'll be marked Unsold:\n" + ", ".join(unmatched))

                st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

                # ── Save button ──
                if st.button("💾 Save & Update Dashboard", type="primary", key="save_update_btn"):
                    with st.spinner("Writing files…"):
                        # Save mvp.json
                        with open(os.path.join(DATA_DIR, "mvp.json"), "w") as f:
                            json.dump(mvp_rows, f, indent=2)
                        set_app_state("mvp", mvp_rows)

                        # Also overwrite the local MVP.xlsx with the uploaded version
                        with open(os.path.join(DATA_DIR, "MVP.xlsx"), "wb") as f:
                            f.write(file_bytes)

                    st.success(f"✅ Done! mvp.json ({len(mvp_rows)} players) updated.")
                    st.info("The dashboard now uses real-time merging of these points with your squads.")
                    
                    # Clear cache so next rerun picks up new data
                    st.cache_data.clear()
                    st.rerun()

                # ── Download buttons ──
                st.markdown("<div class='section-title' style='font-size:1.1rem;margin-top:24px'>📥 Download Data</div>", unsafe_allow_html=True)
                dl_col1, dl_col2 = st.columns(2)
                with dl_col1:
                    # Construct a temporary master list for download purposes
                    current_master = []
                    PLAYER_TO_TEAM_DL = {p.lower(): t for t, plist in SQUADS.items() for p in plist}
                    for row in mvp_rows:
                        name = row["player"]
                        current_master.append({
                            "player": name, 
                            "team": PLAYER_TO_TEAM_DL.get(name.lower(), "Unsold"), 
                            "impact": row["impact"]
                        })
                    
                    st.download_button(
                        label="📥 Download master.json (Live)",
                        data=json.dumps(current_master, indent=2),
                        file_name="master.json",
                        mime="application/json",
                        key="dl_master_btn"
                    )
                with dl_col2:
                    st.download_button(
                        label="📥 Download mvp.json",
                        data=json.dumps(mvp_rows, indent=2),
                        file_name="mvp.json",
                        mime="application/json",
                        key="dl_mvp_btn"
                    )

            except KeyError as e:
                st.error(f"❌ Column not found in Excel: {e}\n\nMake sure the sheet has **'Player'** and **'Total Impact'** columns.")
            except Exception as e:
                st.error(f"❌ Failed to parse Excel: {e}")
                st.exception(e)
            pass

# ─────────────────────────────────────────────
# 👥 EDIT SQUADS
# ─────────────────────────────────────────────
elif active_tab == "👥 Edit Squads":
    st.markdown("<div class='section-title'>👥 Edit Squads</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-sub'>Directly edit the squads.json file and add or remove players from teams</div>", unsafe_allow_html=True)

    # ── Password gate ──
    sq_pwd = st.text_input("🔐 Enter Admin password", type="password", key="squads_pwd")
    correct_pwd = st.secrets.get("admin_password")

    if not sq_pwd:
        st.info("Enter admin password to enable the squads editor.")
    elif sq_pwd != correct_pwd:
        st.error("❌ Incorrect password")
    else:
        st.success("✅ Access granted")
        squads_json_str = json.dumps(FULL_SQUADS, indent=4)
        
        edited_squads = st.text_area(
            "Squads JSON (including Adjustments)",
            value=squads_json_str,
            height=500,
            help="Ensure this is valid JSON. The format must be a dictionary where keys are team names and values are lists of player names. Special key '__offsets__' maps player names to point adjustments (positive to add, negative to deduct)."
        )
        
        if st.button("💾 Save Squads", type="primary", key="save_squads_btn"):
            try:
                parsed_squads = json.loads(edited_squads)
                
                # Basic validation
                all_player_names = []
                for team, players in parsed_squads.items():
                    if team == "__offsets__":
                        continue
                    if not isinstance(players, list):
                        raise ValueError(f"Value for team '{team}' must be a list of players.")
                    for p in players:
                        if p in all_player_names:
                            raise ValueError(f"Duplicate player: '{p}' appears in multiple squads.")
                        all_player_names.append(p)
                
                # Save to squads.json
                with open(os.path.join(DATA_DIR, "squads.json"), "w") as f:
                    json.dump(parsed_squads, f, indent=4)
                set_app_state("squads", parsed_squads)
                
                st.success("✅ Squads updated successfully!")
                st.info("Click **🔄 Refresh Data** at the top to reload the dashboard with updated squads.")
                st.cache_data.clear()
            
            except json.JSONDecodeError as e:
                st.error(f"❌ Invalid JSON format: {e}")
            except Exception as e:
                st.error(f"❌ Failed to parse or save squads: {e}")

        # ── Download button ──
        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
        st.download_button(
            label="📥 Download squads.json (with offsets)",
            data=json.dumps(FULL_SQUADS, indent=2),
            file_name="squads.json",
            mime="application/json",
            key="dl_squads_btn_with_off"
        )

# ─────────────────────────────────────────────
# ✏️ EDIT LINEUPS
# ─────────────────────────────────────────────
elif active_tab == "✏️ Edit Lineups":
    st.markdown("<div class='section-title'>✏️ Edit Playing Lineups</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-sub'>Select players and set batting order for each team</div>", unsafe_allow_html=True)

    lineups = load_lineups()

    # ── Admin password gate ──
    pwd = st.text_input("🔐 Enter Admin password", type="password", key="xi_pwd")
    correct_pwd = st.secrets.get("admin_password")
    
    if not pwd:
        st.info("Enter admin password to enable the lineup editor.")
    elif pwd != correct_pwd:
        st.error("❌ Incorrect password")
    else:
        st.success("✅ Access granted — editing mode enabled")
        edit_team = st.selectbox(
            "Team to edit",
            list(SQUADS.keys()),
            format_func=lambda t: f"{t} — {TEAM_NAMES.get(t, t)}",
            key="edit_team_sel"
        )
        squad_options = SQUADS[edit_team]
        current_xi = lineups.get(edit_team, [])
        xi_size = 13  # Max limit
        
        # Initialize session state for ordered lineups if not present
        if "ordered_lineups" not in st.session_state:
            st.session_state.ordered_lineups = {}
        if edit_team not in st.session_state.ordered_lineups:
            # Sync with pre-saved lineup for this team
            st.session_state.ordered_lineups[edit_team] = lineups.get(edit_team, [])

        # Get current ordered list from state
        current_ordered_xi = st.session_state.ordered_lineups[edit_team]

        # Ensure current_ordered_xi does not exceed max size (trim if needed)
        if len(current_ordered_xi) > xi_size:
            current_ordered_xi = current_ordered_xi[:xi_size]
            st.session_state.ordered_lineups[edit_team] = current_ordered_xi
            st.warning(f"⚠️ Pre-saved lineup was trimmed to {xi_size} to match current selection limit.")

        # Selection Grid
        st.markdown(f"<div style='margin-bottom:8px;font-weight:600;color:#94a3b8;'>Select players for {edit_team} (Batting order matches click order)</div>", unsafe_allow_html=True)
        
        player_data = []
        for p in squad_options:
            match = df[df["player"].str.contains(p, case=False, na=False, regex=False)]
            pts = match.iloc[0]["impact"] if not match.empty else 0.0
            player_data.append({"name": p, "pts": pts})
        
        # Sort players by points descending for convenience
        player_data.sort(key=lambda x: x["pts"], reverse=True)
        
        for i in range(0, len(player_data), 2):
            chk_cols = st.columns(2)
            for j in range(2):
                if i + j < len(player_data):
                    item = player_data[i + j]
                    pname = item["name"]
                    pts = item["pts"]
                    is_selected = pname in current_ordered_xi
                    
                    with chk_cols[j]:
                        val = st.checkbox(f"{pname} • {pts:.1f} pts", value=is_selected, key=f"chk_{edit_team}_{pname}")
                        
                        if val and not is_selected:
                            if len(current_ordered_xi) < xi_size:
                                current_ordered_xi.append(pname)
                                st.session_state.ordered_lineups[edit_team] = current_ordered_xi
                                st.rerun()
                            else:
                                st.error(f"⚠️ Cannot select more than {xi_size} players.")
                        elif not val and is_selected:
                            current_ordered_xi.remove(pname)
                            st.session_state.ordered_lineups[edit_team] = current_ordered_xi
                            st.rerun()

        selected_xi = current_ordered_xi

        # Live Preview of Order with Interactive Controls
        if selected_xi:
            st.markdown("<div style='margin-top:16px; margin-bottom:8px; font-weight:600; color:#94a3b8;'>Live Batting Order Preview (Reorder directly):</div>", unsafe_allow_html=True)
            
            selected_pts = 0.0
            for idx, pname in enumerate(selected_xi):
                # Find points for this player
                p_pts = next((p["pts"] for p in player_data if p["name"] == pname), 0.0)
                selected_pts += p_pts
                pts_color = "#60a5fa" if p_pts > 0 else ("#ef4444" if p_pts < 0 else "#94a3b8")
                
                # Create a row with player info and reorder buttons
                row_cols = st.columns([0.1, 0.7, 0.1, 0.1])
                with row_cols[0]:
                    st.markdown(f"<div style='margin-top:10px; color:#6366f1; font-weight:800;'>#{idx+1}</div>", unsafe_allow_html=True)
                with row_cols[1]:
                    st.markdown(f"""
                    <div style="background:rgba(255,255,255,0.05); padding:6px 12px; border-radius:6px; border:1px solid rgba(255,255,255,0.1); margin-top:2px;">
                        <span style="color:#e2e8f0; font-size:0.85rem;">{pname}</span>
                        <span style="color:{pts_color}; font-weight:700; font-size:0.75rem; float:right;">{p_pts:.1f} pts</span>
                    </div>
                    """, unsafe_allow_html=True)
                with row_cols[2]:
                    # Up button
                    if st.button("⬆️", key=f"up_{edit_team}_{pname}", use_container_width=True, disabled=(idx==0)):
                        reorder_lineup(edit_team, idx, "up")
                        st.rerun()
                with row_cols[3]:
                    # Down button
                    if st.button("⬇️", key=f"down_{edit_team}_{pname}", use_container_width=True, disabled=(idx==len(selected_xi)-1)):
                        reorder_lineup(edit_team, idx, "down")
                        st.rerun()
            
            # Display real-time total
            st.markdown(f"""
            <div style="background:rgba(99,102,241,0.1); border:1px solid rgba(99,102,241,0.3); border-radius:8px; padding:12px 16px; margin: 16px 0;">
                <span style="color:#94a3b8; font-size:0.9rem">Current Selection Total:</span> 
                <span style="color:#60a5fa; font-size:1.1rem; font-weight:700; margin-left:8px">{selected_pts:.1f} pts</span>
            </div>
            """, unsafe_allow_html=True)
        else:
            selected_pts = 0.0

        if len(selected_xi) > xi_size:
            st.warning(f"⚠️ You have selected {len(selected_xi)} players — absolute max is {xi_size}")
        else:
            col_btn1, col_btn2 = st.columns([1, 1])
            with col_btn1:
                if st.button(f"💾 Save {edit_team} Lineup ({len(selected_xi)})", key="save_xi_btn", use_container_width=True):
                    lineups[edit_team] = selected_xi
                    save_lineups(lineups)
                    # Also update session state so preview is consistent
                    st.session_state.ordered_lineups[edit_team] = selected_xi
                    st.success(f"✅ {edit_team} lineup saved!")
                    st.rerun()
            with col_btn2:
                st.button(
                    "🧹 Clear Lineup",
                    key="clear_xi_btn",
                    on_click=clear_lineup_callback,
                    args=(edit_team, squad_options),
                    use_container_width=True
                )
        with st.container():
            st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
            st.download_button(
                label="📥 Download lineups.json",
                data=json.dumps(lineups, indent=2),
                file_name="lineups.json",
                mime="application/json",
                key="dl_lineups_btn"
            )
