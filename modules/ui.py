import streamlit as st
import pandas as pd
import json
import os
from .config import TEAM_COLORS, TEAM_NAMES
from .utils import get_logo_b64, reorder_lineup, clear_lineup_callback
from .data import load_lineups, save_lineups, process_excel, set_app_state

def render_leaderboard(df, squads):
    st.markdown("<div class='section-title'>🏆 Squad Points Standings</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-sub'>Ranked by total ESPNCricinfo MVP points</div>", unsafe_allow_html=True)

    team_totals = (
        df[df["team"] != "Unsold"]
        .groupby("team")["impact"]
        .sum()
        .sort_values(ascending=False)
        .reset_index()
    )

    # Ensure all teams from squads appear even with 0 points
    for team_key in squads:
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

def render_players_tab(df):
    st.markdown("<div class='section-title'>📊 Player Performance</div>", unsafe_allow_html=True)

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

    df_sorted = df.sort_values(by="impact", ascending=False).reset_index(drop=True)
    df_sorted["Rank"] = df_sorted.index + 1
    
    filtered = df_sorted.copy()
    if search:
        filtered = filtered[filtered["player"].str.contains(search, case=False, na=False, regex=False)]
    
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
    
    if "premium_ui_players" not in st.session_state:
        st.session_state.premium_ui_players = True

    if st.session_state.premium_ui_players:
        if "player_limit" not in st.session_state:
            st.session_state.player_limit = 25
        
        display_list = filtered.head(st.session_state.player_limit)

        if display_list.empty:
            st.info("No players found matching your criteria.")
        else:
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
                
                if offset > 0:
                    off_color, off_prefix = "#4ade80", "+"
                elif offset < 0:
                    off_color, off_prefix = "#f87171", "" 
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
    else:
        # Classical UI (Dataframe)
        display_df = filtered[["Rank", "player", "team", "impact", "offset"]].copy()
        display_df.columns = ["Rank", "Player", "Team", "Points", "Adjustment"]
        st.dataframe(
            display_df,
            width="stretch",
            hide_index=True,
            column_config={
                "Points": st.column_config.NumberColumn(format="%.1f"),
                "Adjustment": st.column_config.NumberColumn(format="%.1f")
            }
        )

    st.markdown("---")
    st.toggle("✨ Premium UI Cards (Turn off for stable performance)", key="premium_ui_players", help="Disable this if the app is slow or crashing.")

def render_teams_tab(df, squads):
    st.markdown("<div class='section-title'>🏏 Team Breakdown</div>", unsafe_allow_html=True)

    team = st.selectbox("Select Team", list(squads.keys()), format_func=lambda t: f"{t} — {TEAM_NAMES.get(t, t)}")
    if not team or not squads:
        st.info("No team data available.")
        return
    players = squads[team]
    colors = TEAM_COLORS.get(team, {"bg": "#1e293b", "text": "#e2e8f0", "accent": "#60a5fa"})
    full_name = TEAM_NAMES.get(team, team)
    logo_b64 = get_logo_b64(team)
    logo_html = (
        f'<img style="width:72px;height:72px;object-fit:contain;border-radius:10px;background:rgba(255,255,255,0.08);padding:6px" src="data:image/png;base64,{logo_b64}" />'
        if logo_b64 else ""
    )

    st.markdown(f"""
    <div class="team-header" style="background: linear-gradient(135deg, {colors['accent']}22, {colors['accent']}0a);">
        {logo_html}
        <div>
            <div class="team-header-name" style="color:{colors['accent']}">{full_name}</div>
            <div class="team-header-full" style="color:#94a3b8">{team}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    rows = []
    for p in players:
        match = df[df["player"].str.contains(p, case=False, na=False, regex=False)]
        pts = match.iloc[0]["impact"] if not match.empty else 0.0
        rows.append({"Player": p, "Points": pts})

    team_df = pd.DataFrame(rows).sort_values(by="Points", ascending=False).reset_index(drop=True)
    team_df["Rank"] = team_df.index + 1
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

def render_playing_xi_tab(df, squads):
    st.markdown("<div class='section-title'>⭐ Playing XIs</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-sub'>View selected playing lineups for each team</div>", unsafe_allow_html=True)

    lineups = load_lineups()
    teams_with_xi = [t for t in squads if t in lineups and lineups[t]]

    if not teams_with_xi:
        st.info("No lineups set yet. Use the **✏️ Edit Lineups** tab to add your first playing XI.")
    else:
        cols_per_row = 2
        team_list = list(squads.keys())
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

def render_xi_leaderboard_tab(df, squads):
    st.markdown("<div class='section-title'>📋 Playing XI Leaderboard</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-sub'>Team Standings based on playing lineups only</div>", unsafe_allow_html=True)
    lineups = load_lineups()
    xi_standings = []

    for team_key, squad in squads.items():
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

        missing = [t for t in squads if t not in {x["team"] for x in xi_standings}]
        if missing:
            st.markdown("<div style='color:#475569;font-size:0.8rem;margin-top:12px'>⚠️ No lineup set: " + ", ".join(missing) + "</div>", unsafe_allow_html=True)

def render_unsold_tab(df):
    st.markdown("<div class='section-title'>🚫 Unsold Players</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-sub'>Players not acquired in the mock auction</div>", unsafe_allow_html=True)

    unsold_df = df[df["team"] == "Unsold"].copy()
    
    col_u1, col_u2 = st.columns([2, 1])
    with col_u1:
        search_unsold = st.text_input("🔍 Search", placeholder="Filter unsold players…", key="unsold_search")
    with col_u2:
        sort_unsold = st.selectbox("Sort by", ["Points (High to Low)", "Points (Low to High)", "Name (A-Z)"], key="unsold_sort")

    # ── Initial Rank ──
    # Rank for unsold is based on their points relative to other unsold players
    unsold_df = unsold_df.sort_values(by="impact", ascending=False).reset_index(drop=True)
    unsold_df["Rank"] = unsold_df.index + 1

    filtered = unsold_df.copy()
    if search_unsold:
        filtered = filtered[filtered["player"].str.contains(search_unsold, case=False, na=False, regex=False)]

    if sort_unsold == "Points (Low to High)":
        filtered = filtered.sort_values(by="impact", ascending=True)
    elif sort_unsold == "Name (A-Z)":
        filtered = filtered.sort_values(by="player", ascending=True)
    # Default is Points desc

    # ── Pagination ──
    if "premium_ui_unsold" not in st.session_state:
        st.session_state.premium_ui_unsold = True

    if st.session_state.premium_ui_unsold:
        if "unsold_limit" not in st.session_state:
            st.session_state.unsold_limit = 25
        
        display_list = filtered.head(st.session_state.unsold_limit)

        if display_list.empty:
            st.info("No unsold players found matching your criteria.")
        else:
            # Use config-based theme for unsold
            c = TEAM_COLORS["Unsold"]
            logo_b64 = get_logo_b64("UNSOLD")
            logo_html = (
                f'<img class="player-card-logo" src="data:image/png;base64,{logo_b64}" />'
                if logo_b64 else 
                f'<div class="player-card-logo" style="background:{c["bg"]}; display:flex; align-items:center; justify-content:center; color:{c["text"]}; font-size:1rem; font-weight:800;">UNSOLD</div>'
            )

            for _, row in display_list.iterrows():
                name = row["player"]
                pts = row["impact"]
                rank = row["Rank"]
                
                # Unsold players typically have 0 adjustment (offset)
                # but we can show it if it exists
                offset = row.get("offset", 0.0)
                if offset > 0:
                    off_color, off_prefix = "#4ade80", "+"
                elif offset < 0:
                    off_color, off_prefix = "#f87171", "" 
                else:
                    off_color, off_prefix = "#64748b", ""

                st.markdown(f"""
                <div class="player-card" style="background: linear-gradient(135deg, {c['accent']}18, {c['accent']}06); border-color: {c['accent']}33;">
                    <div class="player-card-logo-container">
                        <div class="player-card-rank" style="background:#475569; border-color:#0f172a;">#{int(rank)}</div>
                        {logo_html}
                    </div>
                    <div class="player-card-info">
                        <div class="player-card-name" style="color:{c['text']}">{name}</div>
                        <div class="player-card-team" style="color: {c['accent']}99">{TEAM_NAMES["Unsold"]}</div>
                    </div>
                    <div class="player-card-metrics">
                        <div class="player-card-points" style="color: {c['accent']}">{pts:.1f}</div>
                        <div class="player-card-adjustment" style="color: {off_color}">Adj: {off_prefix}{offset:.1f}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            if len(filtered) > st.session_state.unsold_limit:
                if st.button(f"Load more ({len(filtered) - st.session_state.unsold_limit} remaining)", use_container_width=True, key="unsold_load_more"):
                    st.session_state.unsold_limit += 25
                    st.rerun()
    else:
        # Classical UI (Dataframe)
        display_df = filtered[["Rank", "player", "impact", "offset"]].copy()
        display_df.columns = ["Rank", "Player", "Points", "Adjustment"]
        st.dataframe(
            display_df,
            width="stretch",
            hide_index=True,
            column_config={
                "Points": st.column_config.NumberColumn(format="%.1f"),
                "Adjustment": st.column_config.NumberColumn(format="%.1f")
            }
        )

    st.markdown("---")
    st.toggle("✨ Premium UI Cards (Turn off for stable performance)", key="premium_ui_unsold", help="Disable this if the app is slow or crashing.")

def render_update_data_tab(squads):
    st.markdown("<div class='section-title'>🔄 Update Data</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-sub'>Upload a new MVP Excel sheet to regenerate mvp.json and master.json</div>", unsafe_allow_html=True)

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
        uploaded = st.file_uploader("Upload MVP.xlsx", type=["xlsx"])

        if uploaded is not None:
            file_bytes = uploaded.read()
            try:
                with st.spinner("Parsing Excel…"):
                    mvp_rows, unmatched = process_excel(file_bytes, squads)

                st.markdown("<div class='section-title' style='font-size:1.1rem;margin-top:16px'>📋 Preview</div>", unsafe_allow_html=True)
                col_prev1, col_prev2, col_prev3 = st.columns(3)
                with col_prev1:
                    st.markdown(f'<div class="metric-card"><div class="metric-value">{len(mvp_rows)}</div><div class="metric-label">Players parsed</div></div>', unsafe_allow_html=True)
                with col_prev2:
                    matched_count = len(mvp_rows) - len(unmatched)
                    st.markdown(f'<div class="metric-card"><div class="metric-value" style="color:#48bb78">{matched_count}</div><div class="metric-label">Matched to squads</div></div>', unsafe_allow_html=True)
                with col_prev3:
                    st.markdown(f'<div class="metric-card"><div class="metric-value" style="color:#f6ad55">{len(unmatched)}</div><div class="metric-label">Unsold</div></div>', unsafe_allow_html=True)

                if st.button("💾 Save & Update Dashboard", type="primary"):
                    base_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
                    with open(os.path.join(base_dir, "mvp.json"), "w") as f:
                        json.dump(mvp_rows, f, indent=2)
                    set_app_state("mvp", mvp_rows)
                    with open(os.path.join(base_dir, "MVP.xlsx"), "wb") as f:
                        f.write(file_bytes)
                    st.success("✅ Updated!")
                    st.cache_data.clear()
                    st.rerun()

            except Exception as e:
                st.error(f"Error parsing Excel: {e}")

def render_edit_squads_tab(full_squads):
    st.markdown("<div class='section-title'>👥 Edit Squads</div>", unsafe_allow_html=True)
    sq_pwd = st.text_input("🔐 Enter Admin password", type="password", key="squads_pwd")
    correct_pwd = st.secrets.get("admin_password")

    if not sq_pwd:
        st.info("Enter admin password to enable the squads editor.")
    elif sq_pwd != correct_pwd:
        st.error("❌ Incorrect password")
    else:
        squads_json_str = json.dumps(full_squads, indent=4)
        edited_squads = st.text_area("Squads JSON", value=squads_json_str, height=500)
        
        if st.button("💾 Save Squads", type="primary"):
            try:
                parsed = json.loads(edited_squads)
                base_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
                with open(os.path.join(base_dir, "squads.json"), "w") as f:
                    json.dump(parsed, f, indent=4)
                set_app_state("squads", parsed)
                st.success("✅ Saved!")
                st.cache_data.clear()
                st.rerun()
            except Exception as e:
                st.error(f"Error saving: {e}")

def render_edit_lineups_tab(squads, df):
    st.markdown("<div class='section-title'>✏️ Edit Playing Lineups</div>", unsafe_allow_html=True)
    pwd = st.text_input("🔐 Enter Admin password", type="password", key="xi_pwd")
    correct_pwd = st.secrets.get("admin_password")
    
    if not pwd:
        st.info("Enter admin password.")
    elif pwd != correct_pwd:
        st.error("❌ Incorrect password")
    else:
        lineups = load_lineups()
        edit_team = st.selectbox("Team", list(squads.keys()), format_func=lambda t: f"{t} — {TEAM_NAMES.get(t, t)}")
        squad_options = squads[edit_team]
        
        if "ordered_lineups" not in st.session_state:
            st.session_state.ordered_lineups = {}
        if edit_team not in st.session_state.ordered_lineups:
            st.session_state.ordered_lineups[edit_team] = lineups.get(edit_team, [])

        current_ordered_xi = st.session_state.ordered_lineups[edit_team]
        
        player_data = []
        for p in squad_options:
            match = df[df["player"].str.contains(p, case=False, na=False, regex=False)]
            pts = match.iloc[0]["impact"] if not match.empty else 0.0
            player_data.append({"name": p, "pts": pts})
        
        player_data.sort(key=lambda x: x["pts"], reverse=True)
        
        for i in range(0, len(player_data), 2):
            cols = st.columns(2)
            for j in range(2):
                if i + j < len(player_data):
                    item = player_data[i + j]
                    pname = item["name"]
                    is_selected = pname in current_ordered_xi
                    if cols[j].checkbox(f"{pname} • {item['pts']:.1f}", value=is_selected, key=f"chk_{edit_team}_{pname}"):
                        if not is_selected:
                            current_ordered_xi.append(pname)
                            st.rerun()
                    elif is_selected:
                        current_ordered_xi.remove(pname)
                        st.rerun()

        if current_ordered_xi:
            for idx, pname in enumerate(current_ordered_xi):
                pts = next((p["pts"] for p in player_data if p["name"] == pname), 0.0)
                row = st.columns([0.1, 0.7, 0.1, 0.1])
                row[0].write(f"#{idx+1}")
                row[1].write(f"{pname} ({pts:.1f})")
                if row[2].button("⬆️", key=f"up_{idx}", disabled=(idx==0)):
                    reorder_lineup(edit_team, idx, "up")
                    st.rerun()
                if row[3].button("⬇️", key=f"down_{idx}", disabled=(idx==len(current_ordered_xi)-1)):
                    reorder_lineup(edit_team, idx, "down")
                    st.rerun()

            if st.button(f"💾 Save {edit_team} Lineup"):
                lineups[edit_team] = current_ordered_xi
                save_lineups(lineups)
                st.success("Saved!")
                st.rerun()
        
        if st.button("🗑️ Clear Lineup", type="secondary"):
            clear_lineup_callback(edit_team, squad_options)
            st.rerun()
