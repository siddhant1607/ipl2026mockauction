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
        df = pd.read_json("master.json")
        return df
    except FileNotFoundError:
        st.error("❌ master.json not found. Run data update workflow.")
        return pd.DataFrame()
    except Exception as e:
        st.error("❌ Error loading master.json")
        st.exception(e)
        return pd.DataFrame()


@st.cache_data
def load_squads():
    try:
        with open("squads.json") as f:
            return json.load(f)
    except FileNotFoundError:
        st.error("❌ squads.json not found.")
        return {}
    except Exception as e:
        st.error("❌ Error loading squads.json")
        st.exception(e)
        return {}


df = load_data()
SQUADS = load_squads()

# ─────────────────────────────────────────────
# UI HEADER
# ─────────────────────────────────────────────
st.title("🏏 IPL 2026 Fantasy Dashboard")

# Refresh button
if st.button("🔄 Refresh Data"):
    st.cache_data.clear()
    st.rerun()

# Stop if no data
if df.empty or not SQUADS:
    st.warning("No data available. Check files or run update.")
    st.stop()

# ─────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["🏆 Leaderboard", "📊 Players", "🏏 Teams"])

# ─────────────────────────────────────────────
# 🏆 Leaderboard
# ─────────────────────────────────────────────
with tab1:
    st.subheader("Team Standings")

    team_df = (
        df.groupby("team")["impact"]
        .sum()
        .sort_values(ascending=False)
        .reset_index()
    )

    st.dataframe(team_df, use_container_width=True)
    st.bar_chart(team_df.set_index("team"))

# ─────────────────────────────────────────────
# 📊 Players
# ─────────────────────────────────────────────
with tab2:
    st.subheader("Player Performance")

    search = st.text_input("🔍 Search player")

    filtered = (
        df[df["player"].str.contains(search, case=False)]
        if search
        else df
    )

    st.dataframe(filtered.sort_values(by="impact", ascending=False), use_container_width=True)

# ─────────────────────────────────────────────
# 🏏 Teams
# ─────────────────────────────────────────────
with tab3:
    st.subheader("Team Breakdown")

    team = st.selectbox("Select Team", list(SQUADS.keys()))
    players = SQUADS[team]

    rows = []
    for p in players:
        match = df[df["player"].str.contains(p, case=False)]
        pts = match.iloc[0]["impact"] if not match.empty else 0

        rows.append({
            "Player": p,
            "Points": pts
        })

    team_df = pd.DataFrame(rows).sort_values(by="Points", ascending=False)

    st.dataframe(team_df, use_container_width=True)

    total_points = int(team_df["Points"].sum())
    st.metric("Total Team Points", total_points)