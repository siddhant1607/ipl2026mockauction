import os

# ─────────────────────────────────────────────
# TEAM COLOURS & LOGOS
# ─────────────────────────────────────────────
TEAM_COLORS = {
    # bg = official fill, text = on-bg text, accent = always readable on dark dashboard
    "CSK":  {"bg": "#FFFF00", "text": "#073763", "accent": "#FFD700"},
    "DC":   {"bg": "#0076CF", "text": "#C00000", "accent": "#38BDF8"},
    "GT":   {"bg": "#1B2133", "text": "#E1C674", "accent": "#E1C674"},
    "KKR":  {"bg": "#3A225D", "text": "#FFE599", "accent": "#C084FC"},
    "LSG":  {"bg": "#A21728", "text": "#FFFFFF", "accent": "#F87171"},
    "MI":   {"bg": "#1155CC", "text": "#F1C232", "accent": "#60A5FA"},
    "PBKS": {"bg": "#FF0000", "text": "#FFFFFF", "accent": "#FF6B6B"},
    "RCB":  {"bg": "#CC0000", "text": "#FFFF00", "accent": "#FBBF24"},
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

LOGO_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "IPL LOGOS")
