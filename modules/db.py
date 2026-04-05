import streamlit as st
import json
from sqlalchemy import text

# ─────────────────────────────────────────────
# DATABASE CONFIG & MIGRATION
# ─────────────────────────────────────────────
USE_DATABASE = "neon_url" in st.secrets

def get_db_connection():
    if USE_DATABASE:
        return st.connection("neon", type="sql", url=st.secrets["neon_url"])
    return None

def init_db():
    if USE_DATABASE:
        conn = get_db_connection()
        try:
            with conn.session as s:
                s.execute(text("""
                    CREATE TABLE IF NOT EXISTS app_state (
                        key VARCHAR(50) PRIMARY KEY,
                        data JSONB
                    );
                """))
                s.commit()
        except Exception as e:
            st.error(f"Failed to initialize Neon DB: {e}")

def set_app_state(key: str, data):
    if USE_DATABASE:
        conn = get_db_connection()
        with conn.session as s:
            s.execute(text("INSERT INTO app_state (key, data) VALUES (:k, CAST(:dat AS JSONB)) ON CONFLICT (key) DO UPDATE SET data = EXCLUDED.data;"), {"k": key, "dat": json.dumps(data)})
            s.commit()

def get_app_state(key: str):
    if USE_DATABASE:
        conn = get_db_connection()
        try:
            with conn.session as s:
                res = s.execute(text("SELECT data FROM app_state WHERE key = :k"), {"k": key}).fetchone()
                if res and res[0]:
                    return res[0]
        except Exception:
            return None
    return None

def run_migration():
    if USE_DATABASE:
        if st.session_state.get("db_migrated"):
            return
            
        conn = get_db_connection()
        try:
            with conn.session as s:
                s.execute(text("""
                    CREATE TABLE IF NOT EXISTS app_state (
                        key VARCHAR(50) PRIMARY KEY,
                        data JSONB
                    );
                """))
                count = s.execute(text("SELECT COUNT(*) FROM app_state")).scalar()
                if count == 0:
                    st.info("🔄 Migrating local JSON files to your new Neon DB...")
                    files = {"squads": "squads.json", "lineups": "lineups.json", "master": "master.json", "mvp": "mvp.json"}
                    base = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
                    for k, fname in files.items():
                        fpath = os.path.join(base, fname)
                        if os.path.exists(fpath):
                            with open(fpath, "r") as f:
                                jdata = json.load(f)
                                s.execute(text("INSERT INTO app_state (key, data) VALUES (:k, CAST(:dat AS JSONB)) ON CONFLICT (key) DO UPDATE SET data = EXCLUDED.data;"), {"k": k, "dat": json.dumps(jdata)})
                    s.commit()
                else:
                    s.commit()
                st.session_state.db_migrated = True
        except Exception as e:
            st.error(f"Failed to synchronize with Neon DB: {e}")
