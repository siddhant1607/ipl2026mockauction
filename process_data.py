import pandas as pd
import json
import difflib

# ─────────────────────────────────────────────
# LOAD SQUADS
# ─────────────────────────────────────────────
with open("squads.json") as f:
    squads = json.load(f)

PLAYER_TO_TEAM = {
    p.lower(): team
    for team, players in squads.items()
    for p in players
}

def find_team(name):
    if not isinstance(name, str):
        return "Unsold"

    n = name.lower().strip()

    if n in PLAYER_TO_TEAM:
        return PLAYER_TO_TEAM[n]

    match = difflib.get_close_matches(n, PLAYER_TO_TEAM.keys(), n=1, cutoff=0.6)
    return PLAYER_TO_TEAM[match[0]] if match else "Unsold"

# ─────────────────────────────────────────────
# READ EXCEL
# ─────────────────────────────────────────────
df = pd.read_excel("MVP.xlsx")

df.columns = [c.lower().strip() for c in df.columns]

# ─────────────────────────────────────────────
# PARSE STRUCTURE
# ─────────────────────────────────────────────
rows = []
current_impact = None

for _, row in df.iterrows():
    player_val = row.get("player")
    impact_val = row.get("total impact")

    # Case 1: rank row (player is number like 1,2,3)
    if isinstance(player_val, (int, float)) and not pd.isna(impact_val):
        current_impact = float(impact_val)

    # Case 2: actual player row
    elif isinstance(player_val, str) and player_val.strip():
        rows.append({
            "player": player_val.strip(),
            "impact": current_impact if current_impact is not None else 0
        })

# ─────────────────────────────────────────────
# CREATE MVP JSON
# ─────────────────────────────────────────────
with open("mvp.json", "w") as f:
    json.dump(rows, f, indent=2)

print("✅ mvp.json created")

# ─────────────────────────────────────────────
# CREATE MASTER JSON
# ─────────────────────────────────────────────
master = []

for row in rows:
    player = row["player"]
    impact = row["impact"]

    team = find_team(player)

    master.append({
        "player": player,
        "team": team,
        "impact": impact
    })

with open("master.json", "w") as f:
    json.dump(master, f, indent=2)

print("✅ master.json created")

# ─────────────────────────────────────────────
# DEBUG
# ─────────────────────────────────────────────
unknown = [p["player"] for p in master if p["team"] == "Unsold"]

if unknown:
    print("\n⚠️ Unsold players:")
    for p in unknown:
        print("-", p)
else:
    print("\n✅ All players matched")