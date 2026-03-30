import streamlit as st
import pandas as pd
import json
import os
import base64
import io

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="IPL 2026 Fantasy Dashboard",
    layout="wide",
    page_icon="🏏"
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
}

LOGO_DIR = os.path.join(os.path.dirname(__file__), "IPL LOGOS")

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
    font-family: 'Poppins', sans-serif;
    font-size: 2rem;
    font-weight: 800;
    background: linear-gradient(135deg, #63b3ed, #f6ad55, #fc8181);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0;
}
.page-header p {
    color: #94a3b8;
    margin: 4px 0 0 0;
    font-size: 0.85rem;
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
    background: linear-gradient(135deg, #3b82f6, #6366f1) !important;
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
    opacity: 0.65;
    font-weight: 400;
}
.lb-points {
    font-family: 'Poppins', sans-serif;
    font-weight: 700;
    font-size: 1rem;
}
.lb-gap {
    font-size: 0.78rem;
    opacity: 0.6;
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
    opacity: 0.7;
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
    color: #475569;
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
    background: rgba(30,41,59,0.8) !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    border-radius: 10px !important;
    color: #e2e8f0 !important;
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
    background: linear-gradient(135deg, #7c3aed, #dc2626, #ea580c);
    border-radius: 14px;
    padding: 20px 28px;
    display: flex;
    align-items: center;
    gap: 16px;
    margin-bottom: 20px;
    box-shadow: 0 8px 32px rgba(124,58,237,0.3);
}
.mvp-title {
    font-family: 'Poppins', sans-serif;
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: rgba(255,255,255,0.7);
}
.mvp-name {
    font-family: 'Poppins', sans-serif;
    font-size: 1.4rem;
    font-weight: 800;
    color: #fff;
}
.mvp-pts {
    font-size: 0.9rem;
    color: rgba(255,255,255,0.75);
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# LOAD DATA
# ─────────────────────────────────────────────
@st.cache_data
def load_data():
    try:
        return pd.read_json("master.json")
    except Exception as e:
        st.error("Error loading master.json")
        st.exception(e)
        return pd.DataFrame()


@st.cache_data
def load_squads():
    try:
        with open("squads.json") as f:
            return json.load(f)
    except Exception as e:
        st.error("Error loading squads.json")
        st.exception(e)
        return {}


def load_lineups():
    path = os.path.join(os.path.dirname(__file__), "lineups.json")
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return {}


def save_lineups(lineups: dict):
    path = os.path.join(os.path.dirname(__file__), "lineups.json")
    with open(path, "w") as f:
        json.dump(lineups, f, indent=2)


def process_excel(file_bytes: bytes, squads: dict) -> tuple[list, list, list]:
    """Process uploaded Excel bytes → returns (mvp_rows, master_rows, unmatched_players)."""
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

    master_rows = []
    unmatched = []
    for row in mvp_rows:
        name = row["player"]
        team = PLAYER_TO_TEAM.get(name.lower(), "Unsold")
        if team == "Unsold":
            unmatched.append(name)
        master_rows.append({"player": name, "team": team, "impact": row["impact"]})

    return mvp_rows, master_rows, unmatched


df = load_data()
SQUADS = load_squads()

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
            <h1>🏏 IPL 2026 Fantasy Dashboard</h1>
            <p>Mock Auction • Fantasy Points Tracker</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

col_r1, col_r2 = st.columns([1, 8])
with col_r2:
    if st.button("🔄 Refresh Data"):
        st.cache_data.clear()
        st.rerun()

# ─────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "🏆 Leaderboard",
    "📊 Players",
    "🏏 Teams",
    "⭐ Playing XIs",
    "📋 XI Leaderboard",
    "🚫 Unsold",
    "🔄 Update Data",
])

# ─────────────────────────────────────────────
# 🏆 LEADERBOARD
# ─────────────────────────────────────────────
with tab1:
    st.markdown("<div class='section-title'>🏆 Fantasy League Standings</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-sub'>Ranked by total fantasy impact points</div>", unsafe_allow_html=True)

    team_totals = (
        df[df["team"] != "Unsold"]
        .groupby("team")["impact"]
        .sum()
        .sort_values(ascending=False)
        .reset_index()
    )

    top_score = team_totals.iloc[0]["impact"]

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
                <span style="color:#e2e8f0">{full_name}</span><br>
                <span class="lb-abbr" style="color:{colors['accent']}">{team}</span>
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
with tab2:
    st.markdown("<div class='section-title'>📊 Player Performance</div>", unsafe_allow_html=True)

    top = df.sort_values(by="impact", ascending=False).iloc[0]
    top_team_colors = TEAM_COLORS.get(top["team"], {"bg": "#7c3aed", "text": "#fff"})
    top_logo_b64 = get_logo_b64(top["team"])
    top_logo_html = (
        f'<img style="width:48px;height:48px;object-fit:contain;border-radius:8px;background:rgba(255,255,255,0.1);padding:4px" src="data:image/png;base64,{top_logo_b64}" />'
        if top_logo_b64 else ""
    )
    st.markdown(f"""
    <div class="mvp-banner">
        {top_logo_html}
        <div>
            <div class="mvp-title">🔥 MVP Leader</div>
            <div class="mvp-name">{top['player']}</div>
            <div class="mvp-pts">{top['team']} · {top['impact']:.2f} fantasy points</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    search = st.text_input("🔍 Search player", placeholder="Type a player name…")
    filtered = df[df["player"].str.contains(search, case=False, na=False)] if search else df
    filtered = filtered.sort_values(by="impact", ascending=False).reset_index(drop=True)
    filtered["Rank"] = filtered.index + 1

    display = filtered[["Rank", "player", "team", "impact"]].copy()
    display.columns = ["Rank", "Player", "Team", "Points"]

    st.dataframe(display, width="stretch", hide_index=True)

# ─────────────────────────────────────────────
# 🏏 TEAMS
# ─────────────────────────────────────────────
with tab3:
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
            <div class="team-header-name" style="color:{colors['accent']}">{team}</div>
            <div class="team-header-full" style="color:#94a3b8">{full_name}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Build player data
    rows = []
    for p in players:
        match = df[df["player"].str.contains(p, case=False, na=False)]
        pts = match.iloc[0]["impact"] if not match.empty else 0.0
        rows.append({"Player": p, "Points": pts})

    team_df = pd.DataFrame(rows).sort_values(by="Points", ascending=False).reset_index(drop=True)
    team_df["Rank"] = team_df.index + 1

    # Render custom player rows
    total_pts = team_df["Points"].sum()

    for _, r in team_df.iterrows():
        pts = r["Points"]
        pts_color = colors["accent"] if pts > 0 else ("#ef4444" if pts < 0 else "#64748b")
        st.markdown(f"""
        <div class="player-row">
            <span class="player-rank-num">#{int(r['Rank'])}</span>
            <span class="player-name">{r['Player']}</span>
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
with tab4:
    st.markdown("<div class='section-title'>⭐ Playing XIs</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-sub'>View selected playing lineups for each team</div>", unsafe_allow_html=True)

    lineups = load_lineups()

    # ── Edit Lineup (password-protected) ──
    with st.expander("✏️ Edit Lineup", expanded=False):
        pwd = st.text_input("Enter admin password", type="password", key="xi_pwd")
        correct_pwd = st.secrets.get("lineup_password", "ipl2026")  # fallback for dev
        if pwd == correct_pwd:
            st.success("✅ Access granted — editing mode enabled")
            edit_team = st.selectbox(
                "Team to edit",
                list(SQUADS.keys()),
                format_func=lambda t: f"{t} — {TEAM_NAMES.get(t, t)}",
                key="edit_team_sel"
            )
            squad_options = SQUADS[edit_team]
            current_xi = lineups.get(edit_team, [])
            xi_size = st.radio("Lineup size", [11, 12, 13], horizontal=True, key="xi_size_radio")

            selected_xi = st.multiselect(
                f"Select {xi_size} players for {edit_team}",
                options=squad_options,
                default=[p for p in current_xi if p in squad_options],
                key="xi_multiselect"
            )

            if len(selected_xi) > xi_size:
                st.warning(f"⚠️ You have selected {len(selected_xi)} players — max is {xi_size}")
            elif len(selected_xi) < xi_size:
                st.info(f"ℹ️ Select {xi_size - len(selected_xi)} more player(s)")
            else:
                if st.button(f"💾 Save {edit_team} Playing {xi_size}", key="save_xi_btn"):
                    lineups[edit_team] = selected_xi
                    save_lineups(lineups)
                    st.success(f"✅ {edit_team} lineup saved!")
                    st.rerun()
        elif pwd:
            st.error("❌ Incorrect password")

    # ── Display all team lineups ──
    teams_with_xi = [t for t in SQUADS if t in lineups and lineups[t]]
    teams_without = [t for t in SQUADS if t not in lineups or not lineups[t]]

    if not teams_with_xi:
        st.info("No lineups set yet. Use **Edit Lineup** above to add your first playing XI.")
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
                        for p in xi:
                            match = df[df["player"].str.contains(p, case=False, na=False)]
                            pts = match.iloc[0]["impact"] if not match.empty else 0.0
                            xi_total += pts
                            pts_color = c["accent"] if pts > 0 else ("#ef4444" if pts < 0 else "#94a3b8")
                            xi_rows_html += f"""
                            <div class="lineup-player">
                                <span style="color:#cbd5e1">{p}</span>
                                <span style="font-weight:700;color:{pts_color}">{pts:.1f}</span>
                            </div>"""

                        xi_rows_html += f"""
                        <div class="lineup-total" style="border-top:1px solid {c['accent']}44;margin-top:6px;">
                            <span style="color:#e2e8f0">Total ({len(xi)})</span>
                            <span style="color:{c['accent']}">{xi_total:.1f} pts</span>
                        </div>"""
                    else:
                        xi_rows_html = "<div style='color:#475569;font-size:0.82rem;padding:8px'>No lineup set</div>"

                    st.markdown(f"""
                    <div class="lineup-card" style="background:linear-gradient(135deg,{c['accent']}12,{c['accent']}06);border-color:{c['accent']}33;">
                        <div style="display:flex;align-items:center;gap:12px;margin-bottom:14px;border-bottom:1px solid {c['accent']}33;padding-bottom:12px;">
                            {logo_html}
                            <div>
                                <div style="font-family:'Poppins',sans-serif;font-weight:700;font-size:1rem;color:{c['accent']}">{team_key}</div>
                                <div style="font-size:0.72rem;color:#64748b">{TEAM_NAMES.get(team_key,'')}</div>
                            </div>
                        </div>
                        {xi_rows_html}
                    </div>
                    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
# 📋 XI LEADERBOARD
# ─────────────────────────────────────────────
with tab5:
    st.markdown("<div class='section-title'>📋 Playing XI Leaderboard</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-sub'>Fantasy standings based on playing lineups only</div>", unsafe_allow_html=True)

    lineups = load_lineups()
    xi_standings = []

    for team_key, squad in SQUADS.items():
        xi = lineups.get(team_key, [])
        if not xi:
            continue
        total = 0.0
        for p in xi:
            match = df[df["player"].str.contains(p, case=False, na=False)]
            if not match.empty:
                total += match.iloc[0]["impact"]
        xi_standings.append({"team": team_key, "points": total, "size": len(xi)})

    if not xi_standings:
        st.info("No lineups have been set yet. Go to the **⭐ Playing XIs** tab to configure lineups.")
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
                    <span style="color:#e2e8f0">{TEAM_NAMES.get(team_key, team_key)}</span><br>
                    <span class="lb-abbr" style="color:{c['accent']}">{team_key} · Playing {item['size']}</span>
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
with tab6:
    st.markdown("<div class='section-title'>🚫 Unsold Players</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-sub'>Players not acquired in the mock auction</div>", unsafe_allow_html=True)

    unsold_df = df[df["team"] == "Unsold"].copy()
    search_unsold = st.text_input("🔍 Search", placeholder="Filter unsold players…", key="unsold_search")

    if search_unsold:
        unsold_df = unsold_df[unsold_df["player"].str.contains(search_unsold, case=False, na=False)]

    unsold_df = unsold_df.sort_values(by="impact", ascending=False).reset_index(drop=True)
    unsold_df["Rank"] = unsold_df.index + 1

    display_unsold = unsold_df[["Rank", "player", "impact"]].copy()
    display_unsold.columns = ["Rank", "Player", "Points"]

    st.dataframe(display_unsold, width="stretch", hide_index=True)

# ─────────────────────────────────────────────
# 🔄 UPDATE DATA
# ─────────────────────────────────────────────
with tab7:
    st.markdown("<div class='section-title'>🔄 Update Data</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-sub'>Upload a new MVP Excel sheet to regenerate mvp.json and master.json</div>", unsafe_allow_html=True)

    # ── Password gate ──
    upd_pwd = st.text_input("🔐 Admin password", type="password", key="update_pwd")
    correct_pwd = st.secrets.get("lineup_password", "ipl2026")

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
                    mvp_rows, master_rows, unmatched = process_excel(file_bytes, SQUADS)

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
                    matched = len(master_rows) - len(unmatched)
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-value" style="color:#48bb78">{matched}</div>
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

                # Top 10 preview table
                preview_df = pd.DataFrame(master_rows).head(15)
                preview_df.index = range(1, len(preview_df) + 1)
                preview_df.columns = ["Player", "Team", "Points"]
                st.markdown("<div style='color:#94a3b8;font-size:0.8rem;margin-bottom:6px'>Top 15 preview (sorted by original order):</div>", unsafe_allow_html=True)
                st.dataframe(preview_df, width="stretch", hide_index=False)

                # Unmatched warning
                if unmatched:
                    st.warning(f"⚠️ **{len(unmatched)} player(s) not found in any squad** — they'll be marked Unsold:\n" + ", ".join(unmatched))

                st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

                # ── Save button ──
                base_dir = os.path.dirname(__file__)
                if st.button("💾 Save & Update Dashboard", type="primary", key="save_update_btn"):
                    with st.spinner("Writing files…"):
                        # Save mvp.json
                        with open(os.path.join(base_dir, "mvp.json"), "w") as f:
                            json.dump(mvp_rows, f, indent=2)

                        # Save master.json
                        with open(os.path.join(base_dir, "master.json"), "w") as f:
                            json.dump(master_rows, f, indent=2)

                        # Also overwrite the local MVP.xlsx with the uploaded version
                        with open(os.path.join(base_dir, "MVP.xlsx"), "wb") as f:
                            f.write(file_bytes)

                    st.success(f"✅ Done! mvp.json ({len(mvp_rows)} players) and master.json updated.")
                    st.info("Click **🔄 Refresh Data** at the top to reload the dashboard with updated data.")

                    # Clear cache so next rerun picks up new data
                    st.cache_data.clear()

            except KeyError as e:
                st.error(f"❌ Column not found in Excel: {e}\n\nMake sure the sheet has **'Player'** and **'Total Impact'** columns.")
            except Exception as e:
                st.error(f"❌ Failed to parse Excel: {e}")
                st.exception(e)
        else:
            st.markdown("""
            <div style="border: 2px dashed rgba(99,102,241,0.3); border-radius: 12px; padding: 32px;
                        text-align: center; color: #475569; margin-top: 8px;">
                <div style="font-size:2rem;margin-bottom:8px">📂</div>
                <div style="font-weight:600;color:#94a3b8">Drop your MVP.xlsx here</div>
                <div style="font-size:0.8rem;margin-top:4px">or use the uploader above</div>
            </div>
            """, unsafe_allow_html=True)
