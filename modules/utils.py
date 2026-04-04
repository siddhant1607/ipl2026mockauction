import streamlit as st
import os
import base64
from .config import LOGO_DIR
from .data import load_lineups, save_lineups

@st.cache_data
def get_logo_b64(team: str) -> str:
    path = os.path.join(LOGO_DIR, f"{team}.png")
    if os.path.exists(path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return ""

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
