import streamlit as st
import requests
import pandas as pd
import difflib

# ─────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────
st.set_page_config(page_title="IPL 2026 Fantasy Dashboard", layout="wide")

# ─────────────────────────────────────────────────────────────
# SQUADS
# ─────────────────────────────────────────────────────────────
SQUADS = {
    "PBKS": ["Vaibhav Suryavanshi","Mitchell Marsh","Abdul Samad","Ryan Rickelton",
             "Nitish Rana","Shimron Hetmyer","Karun Nair","Mitchell Santner",
             "Mitchell Owen","Marco Jansen","Yuzvendra Chahal","Jofra Archer",
             "Harpreet Brar","Umran Malik","Tushar Deshpande","Akash Deep",
             "Vignesh Puthur","Zeeshan Ansari"],

    "CSK": ["KL Rahul","Ayush Mhatre","Venkatesh Iyer","Sanju Samson",
            "Ajinkya Rahane","Kartik Sharma","Urvil Patel","Mohammed Siraj",
            "Xavier Bartlett","Matt Henry","Akeal Hosein","Ravi Bishnoi",
            "Jaydev Unadkat","Mayank Markande","Rahul Chahar","Mayank Yadav",
            "Mangesh Yadav","Rashid Khan","Jamie Overton","Washington Sundar",
            "Ravindra Jadeja"],

    "KKR": ["Aniket Verma","Shashank Singh","Naman Dhir","Devdutt Padikkal",
            "Robin Minz","Jasprit Bumrah","Josh Hazlewood","Adam Milne",
            "Khaleel Ahmed","Shivam Mavi","Sunil Narine","Corbin Bosch",
            "Romario Shepherd","Matthew Short","Josh Inglis","MS Dhoni"],

    "RCB": ["Shubham Dubey","Prashant Veer","Nitish Kumar Reddy","Shahrukh Khan",
            "Rachin Ravindra","Azmatullah Omarzai","Swapnil Singh","Jos Buttler",
            "Phil Salt","Nicholas Pooran","Prabhsimran Singh","Varun Chakravarthy",
            "Trent Boult","Deepak Chahar","Mohsin Khan","Anshul Kamboj",
            "Rasikh Salam","Nandre Burger"],

    "SRH": ["Mitchell Starc","Sai Sudharsan","Quinton de Kock","Mohammed Shami",
            "Tilak Varma","T Natarajan","Kuldeep Sen","Lungi Ngidi",
            "Sarfaraz Khan","Manish Pandey","Nehal Wadhera","Glenn Phillips",
            "Abhishek Sharma","Tim Seifert","David Miller","Sherfane Rutherford",
            "Anukul Roy","Kanishk Chauhan","Rahul Tewatia","Shivang Kumar"],

    "DC": ["Sameer Rizvi","Pathum Nissanka","Ashutosh Sharma","Prithvi Shaw",
           "Cameron Green","Shivam Dube","Axar Patel","Aquib Nabi",
           "Brydon Carse","Tristan Stubbs","Angkrish Raghuvanshi",
           "Kumar Kushagra","Vishnu Vinod","Kuldeep Yadav","Kagiso Rabada",
           "Blessing Muzarabani","Allah Ghazanfar","Kartik Tyagi",
           "Ashok Sharma","Yudhvir Singh"],

    "GT": ["Virat Kohli","Ruturaj Gaikwad","Ishan Kishan","Ramandeep Singh",
           "Rovman Powell","Jason Holder","Riyan Parag","Will Jacks",
           "Arshad Khan","Harshit Rana","Prasidh Krishna","Lockie Ferguson",
           "Matheesha Pathirana","Pat Cummins","Eshan Malinga",
           "Ashwani Kumar","Gurjanpreet Singh"],

    "LSG": ["Shubman Gill","Rohit Sharma","Rishabh Pant","Rajat Patidar",
            "Tejaswi Singh","Jitesh Sharma","Krunal Pandya","Vipraj Nigam",
            "Harshit Rana","Vaibhav Arora","Jacob Duffy","Bhuvneshwar Kumar",
            "Nuwan Thushara","Tom Banton","Rahul Tripathi","Manav Suthar"],

    "RR": ["Suryakumar Yadav","Yashasvi Jaiswal","Rinku Singh","Devdutt Padikkal",
           "Ayush Badoni","Smaran Ravichandran","Salil Arora","Donovan Ferreira",
           "Finn Allen","Liam Livingstone","Shahbaz Ahmed","Cooper Connolly",
           "Suryansh Shedge","Mukesh Kumar","Harshal Patel","Adam Milne",
           "Sandeep Sharma","M Siddharth","Digvesh Rathi","Suyash Sharma",
           "Sai Kishore"],

    "MI": ["Heinrich Klaasen","David Miller","Travis Head","Priyansh Arya",
           "Anuj Rawat","Dhruv Jurel","Abhishek Porel","Arshdeep Singh",
           "Noor Ahmad","Wanindu Hasaranga","Avesh Khan","Hardik Pandya",
           "Dasun Shanaka","Marcus Stoinis","Aiden Markram","Shardul Thakur"]
}

# ─────────────────────────────────────────────────────────────
# PLAYER → TEAM MAP
# ─────────────────────────────────────────────────────────────
PLAYER_TO_TEAM = {
    p.lower(): team
    for team, players in SQUADS.items()
    for p in players
}

def find_team(name):
    n = name.lower()
    if n in PLAYER_TO_TEAM:
        return PLAYER_TO_TEAM[n]

    match = difflib.get_close_matches(n, PLAYER_TO_TEAM.keys(), n=1, cutoff=0.6)
    return PLAYER_TO_TEAM[match[0]] if match else "Unknown"

# ─────────────────────────────────────────────────────────────
# FETCH DATA (WITH DEBUG)
# ─────────────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def fetch_data():
    url = "https://www.espncricinfo.com/series/ipl-2026-1510719/most-valuable-players"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept-Language": "en-US,en;q=0.9",
    }

    try:
        st.write("🔍 Fetching HTML with headers...")

        response = requests.get(url, headers=headers, timeout=10)

        st.write("Status Code:", response.status_code)

        if response.status_code != 200:
            st.error("Blocked by Cricinfo (status not 200)")
            st.code(response.text[:500])
            return pd.DataFrame()

        html = response.text

        # 👇 Now pass HTML string (not URL)
        tables = pd.read_html(html)

        st.write(f"Tables found: {len(tables)}")

        if not tables:
            st.error("No tables found in HTML")
            return pd.DataFrame()

        df = tables[0]

        st.write("Columns:", df.columns.tolist())

        df.columns = [c.lower() for c in df.columns]

        if "total impact" in df.columns:
            df = df.rename(columns={"total impact": "impact"})
        elif "points" in df.columns:
            df = df.rename(columns={"points": "impact"})
        else:
            st.error("Impact column not found")
            st.dataframe(df.head())
            return pd.DataFrame()

        df = df[["player", "impact"]]
        df["team"] = df["player"].apply(find_team)

        return df

    except Exception as e:
        st.error("🔥 FULL ERROR BELOW")
        st.exception(e)
        return pd.DataFrame()
# ─────────────────────────────────────────────────────────────
# UI
# ─────────────────────────────────────────────────────────────
st.title("🏏 IPL 2026 Fantasy Dashboard")

df = fetch_data()

if df.empty:
    st.warning("No data fetched — check debug above")
    st.stop()

tab1, tab2, tab3 = st.tabs(["🏆 Leaderboard", "📊 Players", "🏏 Teams"])

# Leaderboard
with tab1:
    team_df = df.groupby("team")["impact"].sum().sort_values(ascending=False)
    st.dataframe(team_df)
    st.bar_chart(team_df)

# Players
with tab2:
    search = st.text_input("Search player")
    temp = df[df["player"].str.contains(search, case=False)] if search else df
    st.dataframe(temp)

# Teams
with tab3:
    team = st.selectbox("Select Team", list(SQUADS.keys()))
    players = SQUADS[team]

    rows = []
    for p in players:
        match = df[df["player"].str.contains(p, case=False)]
        pts = match.iloc[0]["impact"] if not match.empty else 0
        rows.append({"Player": p, "Points": pts})

    tdf = pd.DataFrame(rows)
    st.dataframe(tdf.sort_values(by="Points", ascending=False))
    st.metric("Total Points", int(tdf["Points"].sum()))