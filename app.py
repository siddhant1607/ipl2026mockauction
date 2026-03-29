import streamlit as st
import pandas as pd
import json

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────
st.set_page_config(page_title="IPL 2026 Fantasy Dashboard", layout="wide")

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


df = load_data()
SQUADS = load_squads()

# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
st.title("🏏 IPL 2026 Fantasy Dashboard")

if st.button("🔄 Refresh"):
    st.cache_data.clear()
    st.rerun()

if df.empty:
    st.warning("No data found. Run update workflow.")
    st.stop()

# ─────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "🏆 Leaderboard",
    "📊 Players",
    "🏏 Teams",
    "🚫 Unsold"
])

# ─────────────────────────────────────────────
# 🏆 LEADERBOARD
# ─────────────────────────────────────────────
with tab1:
    st.markdown("## 🏆 Fantasy League Standings")

    team_df = (
        df[df["team"] != "Unsold"]
        .groupby("team")["impact"]
        .sum()
        .sort_values(ascending=False)
        .reset_index()
    )

    team_df["Rank"] = team_df.index + 1

    top_score = team_df.iloc[0]["impact"]
    team_df["Gap"] = (top_score - team_df["impact"]).round(2)

    display = team_df[["Rank", "team", "impact", "Gap"]]
    display.columns = ["Rank", "Team", "Points", "Gap"]

    st.dataframe(display, width="stretch", hide_index=True)

# ─────────────────────────────────────────────
# 📊 PLAYERS
# ─────────────────────────────────────────────
with tab2:
    st.markdown("## 📊 Player Performance")

    top = df.sort_values(by="impact", ascending=False).iloc[0]
    st.subheader(f"🔥 MVP Leader: {top['player']} — {top['impact']:.2f} pts")

    search = st.text_input("Search player")

    filtered = df[df["player"].str.contains(search, case=False)] if search else df

    filtered = filtered.sort_values(by="impact", ascending=False).reset_index(drop=True)
    filtered["Rank"] = filtered.index + 1

    display = filtered[["Rank", "player", "team", "impact"]]
    display.columns = ["Rank", "Player", "Team", "Points"]

    st.dataframe(display, width="stretch")

# ─────────────────────────────────────────────
# 🏏 TEAMS
# ─────────────────────────────────────────────
with tab3:
    st.markdown("## 🏏 Team Breakdown")

    team = st.selectbox("Select Team", list(SQUADS.keys()))
    players = SQUADS[team]

    rows = []
    for p in players:
        match = df[df["player"].str.contains(p, case=False)]
        pts = match.iloc[0]["impact"] if not match.empty else 0

        rows.append({"Player": p, "Points": pts})

    team_df = pd.DataFrame(rows).sort_values(by="Points", ascending=False)

    st.dataframe(team_df, width="stretch")
    st.metric("Total Points", int(team_df["Points"].sum()))

# ─────────────────────────────────────────────
# 🚫 UNSOLD
# ─────────────────────────────────────────────
with tab4:
    st.markdown("## 🚫 Unsold Players")

    unsold_df = df[df["team"] == "Unsold"].copy()

    search_unsold = st.text_input("Search Unsold Players")

    if search_unsold:
        unsold_df = unsold_df[
            unsold_df["player"].str.contains(search_unsold, case=False)
        ]

    unsold_df = unsold_df.sort_values(by="impact", ascending=False).reset_index(drop=True)
    unsold_df["Rank"] = unsold_df.index + 1

    display_unsold = unsold_df[["Rank", "player", "impact"]]
    display_unsold.columns = ["Rank", "Player", "Points"]

    st.dataframe(display_unsold, width="stretch")
