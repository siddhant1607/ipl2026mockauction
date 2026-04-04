import streamlit as st
import pandas as pd
import os

# Import our modular components
from modules.config import TEAM_COLORS, TEAM_NAMES
from modules.styles import inject_custom_css
from modules.db import run_migration
from modules.data import load_squads, load_data, load_lineups
from modules.ui import (
    render_leaderboard, render_players_tab, render_teams_tab,
    render_playing_xi_tab, render_xi_leaderboard_tab, render_unsold_tab,
    render_update_data_tab, render_edit_squads_tab, render_edit_lineups_tab
)

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="IPL 2026 Mock Auction Dashboard",
    layout="wide",
    page_icon="🏏"
)

# ─────────────────────────────────────────────
# INITIALIZATION
# ─────────────────────────────────────────────
inject_custom_css()
run_migration()

# Load base data
FULL_SQUADS = load_squads()
SQUADS = {k: v for k, v in FULL_SQUADS.items() if k != "__offsets__"}
df = load_data()

# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
col_h1, col_h2 = st.columns([1, 8])
with col_h2:
    st.markdown("""
    <div class="page-header">
        <div>
            <h1>🏏 IPL 2026 Mock Auction Dashboard</h1>
            <p>IPL 2026 Mock Auction • QCC Live</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Styling for Refresh Button
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
# TABS
# ─────────────────────────────────────────────
tabs = st.tabs([
    "🏆 Leaderboard", "📊 Players", "🏏 Teams", "⭐ Playing XIs",
    "📋 XI Leaderboard", "🚫 Unsold", "🔄 Update Data", "👥 Edit Squads", "✏️ Edit Lineups"
])

tab_renders = [
    lambda: render_leaderboard(df, SQUADS),
    lambda: render_players_tab(df),
    lambda: render_teams_tab(df, SQUADS),
    lambda: render_playing_xi_tab(df, SQUADS),
    lambda: render_xi_leaderboard_tab(df, SQUADS),
    lambda: render_unsold_tab(df),
    lambda: render_update_data_tab(SQUADS),
    lambda: render_edit_squads_tab(FULL_SQUADS),
    lambda: render_edit_lineups_tab(SQUADS, df)
]

for tab, render_func in zip(tabs, tab_renders):
    with tab:
        render_func()
