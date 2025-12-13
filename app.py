import uuid
import math
from datetime import datetime
import asyncio

import streamlit as st
import plotly.graph_objects as go

# LibSQL/Turso (SQLite online)
try:
    from libsql_client import create_client
    DB_AVAILABLE = True
except Exception:
    DB_AVAILABLE = False

# Gemini
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except Exception:
    GEMINI_AVAILABLE = False


APP_TITLE = "Estudo Bíblico — Linha do Tempo Circular"
ADMIN_USER = "admin"
ADMIN_PASS = "R$Masterkey01"
SCHEMA_VERSION = "v1"


# ---------------------------
# Helpers
# ---------------------------
def new_id() -> str:
    return str(uuid.uuid4())

def now_iso() -> str:
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"

def safe_int(val, default=None):
    try:
        return int(val)
    except Exception:
        return default


# ---------------------------
# DB: Turso/libSQL client
# ---------------------------
def get_client():
    if not DB_AVAILABLE:
        raise RuntimeError("Biblioteca libsql-client não está instalada.")
    db_url = st.secrets.get("TURSO_DATABASE_URL", "")
    db_token = st.secrets.get("TURSO_AUTH_TOKEN", "")
    if not db_url or not db_token:
        raise RuntimeError("Configure TURSO_DATABASE_URL e TURSO_AUTH_TOKEN em st.secrets.")
    return create_client(url=db_url, auth_token=db_token)

# ✅ Correção aplicada aqui
def exec_sql(sql: str, params: tuple = ()):
    client = get_client()
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    if loop.is_running():
        # Se já houver loop ativo (caso raro), cria tarefa
        future = asyncio.ensure_future(client.execute(sql, params))
        return loop.run_until_complete(future)
    else:
        return loop.run_until_complete(client.execute(sql, params))


def init_db():
    exec_sql("""
        CREATE TABLE IF NOT EXISTS meta (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        );
    """)
    exec_sql("""
        INSERT OR IGNORE INTO meta (key, value) VALUES ('schema_version', ?);
    """, (SCHEMA_VERSION,))

    exec_sql("""
    CREATE TABLE IF NOT EXISTS years (
        id TEXT PRIMARY KEY,
        year INTEGER UNIQUE NOT NULL,
        created_at TEXT NOT NULL
    );
    """)
    exec_sql("""
    CREATE TABLE IF NOT EXISTS events (
        id TEXT PRIMARY KEY,
        year_id TEXT NOT NULL,
        title TEXT NOT NULL,
        summary TEXT,
        start_date TEXT,
        end_date TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY (year_id) REFERENCES years (id) ON DELETE CASCADE
    );
    """)
    exec_sql("""
    CREATE TABLE IF NOT EXISTS subevents (
        id TEXT PRIMARY KEY,
        event_id TEXT NOT NULL,
        title TEXT NOT NULL,
        summary TEXT,
        start_date TEXT,
        end_date TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY (event_id) REFERENCES events (id) ON DELETE CASCADE
    );
    """)
    exec_sql("""
    CREATE TABLE IF NOT EXISTS descriptions (
        id TEXT PRIMARY KEY,
        parent_type TEXT NOT NULL CHECK (parent_type IN ('event','subevent')),
        parent_id TEXT NOT NULL,
        text TEXT NOT NULL,
        created_at TEXT NOT NULL
    );
    """)
    exec_sql("""
    CREATE TABLE IF NOT EXISTS prophecies (
        id TEXT PRIMARY KEY,
        parent_type TEXT NOT NULL CHECK (parent_type IN ('event','subevent')),
        parent_id TEXT NOT NULL,
        reference TEXT,
        text TEXT NOT NULL,
        created_at TEXT NOT NULL
    );
    """)
    exec_sql("""
    CREATE TABLE IF NOT EXISTS analyses (
        id TEXT PRIMARY KEY,
        parent_type TEXT NOT NULL CHECK (parent_type IN ('event','subevent')),
        parent_id TEXT NOT NULL,
        text TEXT NOT NULL,
        created_at TEXT NOT NULL
    );
    """)
    exec_sql("CREATE INDEX IF NOT EXISTS idx_events_year ON events(year_id);")
    exec_sql("CREATE INDEX IF NOT EXISTS idx_subevents_event ON subevents(event_id);")
    exec_sql("CREATE INDEX IF NOT EXISTS idx_desc_parent ON descriptions(parent_id, parent_type);")
    exec_sql("CREATE INDEX IF NOT EXISTS idx_prop_parent ON prophecies(parent_id, parent_type);")
    exec_sql("CREATE INDEX IF NOT EXISTS idx_analy_parent ON analyses(parent_id, parent_type);")


# ---------------------------
# CRUD (igual ao anterior, usa exec_sql)
# ---------------------------
def add_year(year: int):
    yid = new_id()
    exec_sql("INSERT INTO years (id, year, created_at) VALUES (?, ?, ?);", (yid, year, now_iso()))
    return yid

def get_years():
    res = exec_sql("SELECT id, year FROM years ORDER BY year ASC;")
    return [{"id": r["id"], "year": r["year"]} for r in res.rows]

# ... (mantém todos os métodos add_event, get_events_by_year, add_subevent, etc. iguais ao código anterior, usando exec_sql)


# ---------------------------
# Gemini (igual ao anterior)
# ---------------------------
def setup_gemini():
    api_key = st.secrets.get("GOOGLE_API_KEY", "")
    if GEMINI_AVAILABLE and api_key:
        genai.configure(api_key=api_key)
        return True
    return False

def call_gemini(prompt: str, context: dict = None, model_name: str = "gemini-1.5-flash"):
    if not GEMINI_AVAILABLE:
        return "Gemini SDK não está disponível."
    if not setup_gemini():
        return "Chave de API do Gemini ausente em st.secrets."
    try:
        system_context = ""
        if context:
            system_context = f"""Contexto do estudo:
- Ano: {context.get('year')}
- Evento: {context.get('event_title')}
- Evento ID: {context.get('event_id')}
- Sub-evento: {context.get('subevent_title')}
- Sub-evento ID: {context.get('subevent_id')}
- Resumo: {context.get('summary') or '-'}
- Datas: início={context.get('start_date') or '-'}, fim={context.get('end_date') or '-'}
"""
        full_prompt = f"{system_context}\n\nPergunta/Estudo:\n{prompt}"
        model = genai.GenerativeModel(model_name)
        resp = model.generate_content(full_prompt)
        return resp.text or "Sem conteúdo retornado."
    except Exception as e:
        return f"Erro ao usar Gemini: {e}"


# ---------------------------
# Login, timeline, admin, etc.
# ---------------------------
# (mantém igual ao código anterior, sem mudanças)
# ---------------------------

def main():
    st.set_page_config(page_title=APP_TITLE, page_icon="📜", layout="wide")
    # login/session igual ao anterior
    ensure_session()

    # Sidebar login
    with st.sidebar:
        st.header("Login do administrador")
        st.text_input("Usuário", key="admin_user", placeholder="admin")
        st.text_input("Senha", key="admin_pw", type="password", placeholder="Digite e pressione Enter", on_change=validate_login)
        if st.session_state.login_msg:
            st.caption(st.session_state.login_msg)

    # Init DB
    try:
        init_db()
    except Exception as e:
        st.error(f"Falha ao inicializar banco (libSQL/Turso): {e}")
        st.stop()

    st.title(APP_TITLE)
    st.caption("Timeline circular com expansão de eventos e integração com Gemini.")

    years = get_years()
    render_circular_timeline(years)

    st.markdown("### Detalhes por ano")
    for y in years:
        render_year_details(y)

    st.markdown("---")
    gemini_study_section()

    st.markdown("---")
    if st.session_state.is_admin:
        admin_panel()
    else:
        st.info("Faça login para acessar a área do administrador.")


if __name__ == "__main__":
    main()
