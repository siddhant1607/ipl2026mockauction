import streamlit as st
import pandas as pd
import json
import os
import io
import re
from .db import get_app_state, set_app_state

@st.cache_data
def load_mvp_points():
    """Load player points list from database or mvp.json."""
    db_data = get_app_state("mvp")
    if db_data is not None:
        return db_data
        
    try:
        with open("data/mvp.json") as f:
            return json.load(f)
    except Exception:
        return []

@st.cache_data
def load_squads():
    """Load team rosters from database or squads.json."""
    db_data = get_app_state("squads")
    if db_data is not None:
        return db_data
        
    try:
        with open("data/squads.json") as f:
            return json.load(f)
    except Exception:
        return {}

@st.cache_data
def load_data():
    """Construct the master DataFrame dynamically by merging MVP points and Squads."""
    """Construct the master DataFrame dynamically by merging MVP points and Squads."""
    mvp_list = load_mvp_points()
    full_squads = load_squads()
    
    # Extract offsets if they exist
    offsets = full_squads.get("__offsets__", {})
    # Filter out metadata keys for squad mapping
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
        
        team = PLAYER_TO_TEAM.get(name.lower(), "Unsold")
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
            team = PLAYER_TO_TEAM.get(name.lower(), "Unsold")
            master_rows.append({
                "player": name,
                "team": team,
                "impact": offset,
                "raw_impact": 0.0,
                "offset": offset
            })
    
    return pd.DataFrame(master_rows)

@st.cache_data
def load_lineups():
    db_data = get_app_state("lineups")
    if db_data is not None:
        return db_data
        
    path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "lineups.json")
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return {}

def save_lineups(lineups: dict):
    set_app_state("lineups", lineups)
    
    # Still write to local file as immediate backup
    path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "lineups.json")
    try:
        with open(path, "w") as f:
            json.dump(lineups, f, indent=2)
    except Exception:
        pass

def process_excel(file_bytes: bytes, squads: dict) -> tuple[list, list]:
    """Process uploaded Excel bytes → returns (mvp_rows, unmatched_players)."""
    # Filter out metadata for team mapping
    squads_only = {k: v for k, v in squads.items() if k != "__offsets__"}
    
    PLAYER_TO_TEAM = {
        p.lower(): team
        for team, players in squads_only.items()
        for p in players
    }

    if file_bytes:
        raw = pd.read_excel(io.BytesIO(file_bytes))
        raw.columns = [c.lower().strip() for c in raw.columns]
    else:
        return [], []

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
        team = PLAYER_TO_TEAM.get(name.lower(), "Unsold")
        if team == "Unsold":
            unmatched.append(name)

    return mvp_rows, unmatched

def process_text(text_content: str, squads: dict) -> tuple[list, list]:
    """Process pasted text → returns (mvp_rows, unmatched_players)."""
    # Filter out metadata for team mapping
    squads_only = {k: v for k, v in squads.items() if k != "__offsets__"}
    
    PLAYER_TO_TEAM = {
        p.lower(): team
        for team, players in squads_only.items()
        for p in players
    }

    lines = [line.strip() for line in text_content.splitlines()]
    mvp_rows = []
    
    # Regex to identify stats lines: starts with numeric impact, impact/mat, and match count
    # E.g., "190.6 95.3 2" or "21.2 21.2 1" or "-0.6 -0.6 1"
    stats_pattern = re.compile(r'^[\-\d\.]+\s+[\-\d\.]+\s+\d+')

    for i in range(len(lines)):
        line = lines[i]
        if stats_pattern.match(line):
            try:
                parts = line.split()
                impact = float(parts[0])
                
                # Based on the structure:
                # i-1: Team
                # i-2: Player Name
                if i >= 2:
                    team_candidate = lines[i-1]
                    player_candidate = lines[i-2]
                    
                    # Robustness: if player_candidate is empty (due to gap) or a rank digit, try one more up
                    if (not player_candidate or player_candidate.isdigit()) and i >= 3:
                        player_candidate = lines[i-3]
                    
                    if player_candidate and team_candidate:
                        # Sometimes Team and Player names are actually valid text
                        # We want to exclude cases where team_candidate might be part of previous player's stats
                        if stats_pattern.match(team_candidate) or stats_pattern.match(player_candidate):
                            continue
                            
                        # Further check: skip if player_candidate looks like a rank number
                        if player_candidate.isdigit():
                            continue

                        mvp_rows.append({
                            "player": player_candidate.strip(),
                            "impact": impact
                        })
            except (ValueError, IndexError):
                continue

    unmatched = []
    for row in mvp_rows:
        name = row["player"]
        team = PLAYER_TO_TEAM.get(name.lower(), "Unsold")
        if team == "Unsold":
            unmatched.append(name)

    return mvp_rows, unmatched

def get_player_stats_dict(df: pd.DataFrame) -> dict:
    """Returns a dictionary mapping player name (lowercase) to their stats for O(1) lookup."""
    return {
        row["player"].lower(): {
            "player": row["player"],
            "team": row["team"],
            "impact": row["impact"],
            "offset": row["offset"]
        }
        for _, row in df.iterrows()
    }
