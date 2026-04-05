import streamlit as st
import pandas as pd
import os

# Import our modular components
from modules.config import TEAM_COLORS, TEAM_NAMES
from modules.styles import inject_custom_css
from modules.db import run_migration
from modules.data import load_squads, load_data, load_lineups, get_player_stats_dict
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
    page_icon="IPL LOGOS/IPL.png"
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
player_stats = get_player_stats_dict(df)

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
# NAVIGATION (Lazy Tabs)
# ─────────────────────────────────────────────
tab_options = [
    "🏆 Leaderboard", "📊 Players", "🏏 Teams", "⭐ Playing XIs",
    "📋 XI Leaderboard", "🚫 Unsold", "🔄 Update Data", "👥 Edit Squads", "✏️ Edit Lineups"
]

# Use segmented_control for a premium, performant, and lazy-loading tab experience
selected_tab = st.segmented_control(
    "Navigation",
    options=tab_options,
    default="🏆 Leaderboard",
    label_visibility="collapsed"
)

st.markdown("<div style='margin-bottom: 24px;'></div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# TAB RENDERING (Only runs the active tab)
# ─────────────────────────────────────────────
if selected_tab == "🏆 Leaderboard":
    render_leaderboard(df, SQUADS)
elif selected_tab == "📊 Players":
    render_players_tab(df)
elif selected_tab == "🏏 Teams":
    render_teams_tab(df, SQUADS, player_stats)
elif selected_tab == "⭐ Playing XIs":
    render_playing_xi_tab(df, SQUADS, player_stats)
elif selected_tab == "📋 XI Leaderboard":
    render_xi_leaderboard_tab(df, SQUADS, player_stats)
elif selected_tab == "🚫 Unsold":
    render_unsold_tab(df)
elif selected_tab == "🔄 Update Data":
    render_update_data_tab(SQUADS)
elif selected_tab == "👥 Edit Squads":
    render_edit_squads_tab(FULL_SQUADS)
elif selected_tab == "✏️ Edit Lineups":
    render_edit_lineups_tab(SQUADS, df, player_stats)
