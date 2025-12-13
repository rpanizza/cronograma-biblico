import uuid
import math
from datetime import datetime

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
ADMIN_PASS = "R$Masterkey01"  # Em produção, usar hash + secrets
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

def exec_sql(sql: str, params: tuple = ()):
    client = get_client()
    return client.execute(sql, params)

def init_db():
    # schema version
    exec_sql("""
        CREATE TABLE IF NOT EXISTS meta (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        );
    """)
    exec_sql("""
        INSERT OR IGNORE INTO meta (key, value) VALUES ('schema_version', ?);
    """, (SCHEMA_VERSION,))

    # years
    exec_sql("""
    CREATE TABLE IF NOT EXISTS years (
        id TEXT PRIMARY KEY,
        year INTEGER UNIQUE NOT NULL,
        created_at TEXT NOT NULL
    );
    """)
    # events
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
    # subevents
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
    # descriptions
    exec_sql("""
    CREATE TABLE IF NOT EXISTS descriptions (
        id TEXT PRIMARY KEY,
        parent_type TEXT NOT NULL CHECK (parent_type IN ('event','subevent')),
        parent_id TEXT NOT NULL,
        text TEXT NOT NULL,
        created_at TEXT NOT NULL
    );
    """)
    # prophecies
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
    # analyses
    exec_sql("""
    CREATE TABLE IF NOT EXISTS analyses (
        id TEXT PRIMARY KEY,
        parent_type TEXT NOT NULL CHECK (parent_type IN ('event','subevent')),
        parent_id TEXT NOT NULL,
        text TEXT NOT NULL,
        created_at TEXT NOT NULL
    );
    """)
    # índices
    exec_sql("CREATE INDEX IF NOT EXISTS idx_events_year ON events(year_id);")
    exec_sql("CREATE INDEX IF NOT EXISTS idx_subevents_event ON subevents(event_id);")
    exec_sql("CREATE INDEX IF NOT EXISTS idx_desc_parent ON descriptions(parent_id, parent_type);")
    exec_sql("CREATE INDEX IF NOT EXISTS idx_prop_parent ON prophecies(parent_id, parent_type);")
    exec_sql("CREATE INDEX IF NOT EXISTS idx_analy_parent ON analyses(parent_id, parent_type);")


# ---------------------------
# CRUD
# ---------------------------
def add_year(year: int):
    yid = new_id()
    exec_sql("INSERT INTO years (id, year, created_at) VALUES (?, ?, ?);", (yid, year, now_iso()))
    return yid

def get_years():
    res = exec_sql("SELECT id, year FROM years ORDER BY year ASC;")
    return [{"id": r["id"], "year": r["year"]} for r in res.rows]

def add_event(year_id: str, title: str, summary: str = None, start_date: str = None, end_date: str = None):
    eid = new_id()
    exec_sql("""
        INSERT INTO events (id, year_id, title, summary, start_date, end_date, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?);
    """, (eid, year_id, title, summary, start_date, end_date, now_iso()))
    return eid

def get_events_by_year(year_id: str):
    res = exec_sql("""
        SELECT id, title, summary, start_date, end_date
        FROM events WHERE year_id = ?
        ORDER BY created_at ASC;
    """, (year_id,))
    return [{"id": r["id"], "title": r["title"], "summary": r["summary"], "start_date": r["start_date"], "end_date": r["end_date"]} for r in res.rows]

def add_subevent(event_id: str, title: str, summary: str = None, start_date: str = None, end_date: str = None):
    sid = new_id()
    exec_sql("""
        INSERT INTO subevents (id, event_id, title, summary, start_date, end_date, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?);
    """, (sid, event_id, title, summary, start_date, end_date, now_iso()))
    return sid

def get_subevents(event_id: str):
    res = exec_sql("""
        SELECT id, title, summary, start_date, end_date
        FROM subevents WHERE event_id = ?
        ORDER BY created_at ASC;
    """, (event_id,))
    return [{"id": r["id"], "title": r["title"], "summary": r["summary"], "start_date": r["start_date"], "end_date": r["end_date"]} for r in res.rows]

def add_description(parent_type: str, parent_id: str, text: str):
    did = new_id()
    exec_sql("""
        INSERT INTO descriptions (id, parent_type, parent_id, text, created_at)
        VALUES (?, ?, ?, ?, ?);
    """, (did, parent_type, parent_id, text, now_iso()))
    return did

def get_descriptions(parent_type: str, parent_id: str):
    res = exec_sql("""
        SELECT id, text FROM descriptions
        WHERE parent_type = ? AND parent_id = ?
        ORDER BY created_at ASC;
    """, (parent_type, parent_id))
    return [{"id": r["id"], "text": r["text"]} for r in res.rows]

def add_prophecy(parent_type: str, parent_id: str, reference: str, text: str):
    pid = new_id()
    exec_sql("""
        INSERT INTO prophecies (id, parent_type, parent_id, reference, text, created_at)
        VALUES (?, ?, ?, ?, ?, ?);
    """, (pid, parent_type, parent_id, reference, text, now_iso()))
    return pid

def get_prophecies(parent_type: str, parent_id: str):
    res = exec_sql("""
        SELECT id, reference, text FROM prophecies
        WHERE parent_type = ? AND parent_id = ?
        ORDER BY created_at ASC;
    """, (parent_type, parent_id))
    return [{"id": r["id"], "reference": r["reference"], "text": r["text"]} for r in res.rows]

def add_analysis(parent_type: str, parent_id: str, text: str):
    aid = new_id()
    exec_sql("""
        INSERT INTO analyses (id, parent_type, parent_id, text, created_at)
        VALUES (?, ?, ?, ?, ?);
    """, (aid, parent_type, parent_id, text, now_iso()))
    return aid

def get_analyses(parent_type: str, parent_id: str):
    res = exec_sql("""
        SELECT id, text FROM analyses
        WHERE parent_type = ? AND parent_id = ?
        ORDER BY created_at ASC;
    """, (parent_type, parent_id))
    return [{"id": r["id"], "text": r["text"]} for r in res.rows]


# ---------------------------
# Gemini
# ---------------------------
def setup_gemini():
    api_key = st.secrets.get("GOOGLE_API_KEY", "")
    if GEMINI_AVAILABLE and api_key:
        genai.configure(api_key=api_key)
        return True
    return False

def call_gemini(prompt: str, context: dict = None, model_name: str = "gemini-1.5-flash"):
    if not GEMINI_AVAILABLE:
        return "Gemini SDK não está disponível (instale google-generativeai)."
    if not setup_gemini():
        return "Chave de API do Gemini ausente em st.secrets (GOOGLE_API_KEY)."
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
# UI: Session and login
# ---------------------------
def ensure_session():
    if "is_admin" not in st.session_state:
        st.session_state.is_admin = False
    if "admin_user" not in st.session_state:
        st.session_state.admin_user = None
    if "admin_pw" not in st.session_state:
        st.session_state.admin_pw = ""
    if "login_msg" not in st.session_state:
        st.session_state.login_msg = ""

def validate_login():
    user = st.session_state.get("admin_user")
    pw = st.session_state.get("admin_pw")
    if user == ADMIN_USER and pw == ADMIN_PASS:
        st.session_state.is_admin = True
        st.session_state.login_msg = "Login realizado com sucesso."
    else:
        st.session_state.is_admin = False
        st.session_state.login_msg = "Usuário ou senha inválidos."

def logoff():
    st.session_state.is_admin = False
    st.session_state.admin_user = None
    st.session_state.admin_pw = ""
    st.session_state.login_msg = "Sessão encerrada."


# ---------------------------
# UI: Circular timeline
# ---------------------------
def render_circular_timeline(years):
    if not years:
        st.info("Nenhum ano cadastrado ainda.")
        return

    n = len(years)
    # ângulos 0..180 graus para criar uma curva ascendente
    angles = [i * (180 / max(n - 1, 1)) for i in range(n)]
    radius = 1.0
    xs = [radius * -1 * math.cos(math.radians(a)) for a in angles]
    ys = [radius * math.sin(math.radians(a)) for a in angles]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=xs, y=ys,
        mode="lines+markers",
        line=dict(color="#6C63FF", width=2),
        marker=dict(size=12, color="#00ADB5"),
        text=[str(y["year"]) for y in years],
        hovertemplate="Ano: %{text}<extra></extra>"
    ))

    fig.update_layout(
        showlegend=False,
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        margin=dict(l=10, r=10, t=10, b=10),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        height=240,
    )
    st.plotly_chart(fig, use_container_width=True)


# ---------------------------
# UI: Year details
# ---------------------------
def render_year_details(year):
    events = get_events_by_year(year["id"])
    with st.expander(f"Ano {year['year']} — {len(events)} eventos", expanded=False):
        for ev in events:
            st.markdown(f"**ID do evento:** `{ev['id']}`")
            st.markdown(f"**Título:** {ev['title']}")
            if ev["summary"]:
                st.markdown(f"**Resumo:** {ev['summary']}")
            st.markdown(f"**Datas:** início: {ev['start_date'] or '-'} | fim: {ev['end_date'] or '-'}")

            subevents = get_subevents(ev["id"])
            if subevents:
                st.markdown("**Sub-eventos:**")
                for se in subevents:
                    st.markdown(f"- **ID:** `{se['id']}` — **{se['title']}**")
                    if se["summary"]:
                        st.markdown(f"  - {se['summary']}")
                    st.markdown(f"  - Datas: início: {se['start_date'] or '-'} | fim: {se['end_date'] or '-'}")

                    descs = get_descriptions("subevent", se["id"])
                    props = get_prophecies("subevent", se["id"])
                    anals = get_analyses("subevent", se["id"])
                    if descs:
                        st.markdown("  - **Descrições:**")
                        for d in descs:
                            st.markdown(f"    - `{d['id']}` — {d['text']}")
                    if props:
                        st.markdown("  - **Profecias:**")
                        for p in props:
                            st.markdown(f"    - `{p['id']}` — {p['reference'] or '-'}: {p['text']}")
                    if anals:
                        st.markdown("  - **Análises:**")
                        for a in anals:
                            st.markdown(f"    - `{a['id']}` — {a['text']}")

            ev_descs = get_descriptions("event", ev["id"])
            ev_props = get_prophecies("event", ev["id"])
            ev_anals = get_analyses("event", ev["id"])
            if ev_descs or ev_props or ev_anals:
                st.markdown("---")
            if ev_descs:
                st.markdown("**Descrições (evento):**")
                for d in ev_descs:
                    st.markdown(f"- `{d['id']}` — {d['text']}")
            if ev_props:
                st.markdown("**Profecias (evento):**")
                for p in ev_props:
                    st.markdown(f"- `{p['id']}` — {p['reference'] or '-'}: {p['text']}")
            if ev_anals:
                st.markdown("**Análises (evento):**")
                for a in ev_anals:
                    st.markdown(f"- `{a['id']}` — {a['text']}")


# ---------------------------
# UI: Admin panel
# ---------------------------
def admin_panel():
    st.subheader("Área do administrador")
    st.button("Logoff", on_click=logoff, type="secondary")

    st.markdown("### Gerenciar cronograma")

    # Add year
    st.markdown("#### Adicionar ano")
    col1, col2 = st.columns([2, 1])
    with col1:
        year_input = st.text_input("Ano", placeholder="Ex: 2025")
    with col2:
        if st.button("Salvar ano"):
            year_num = safe_int(year_input)
            if year_num is None:
                st.error("Ano inválido.")
            else:
                try:
                    yid = add_year(year_num)
                    st.success(f"Ano {year_num} salvo. ID: {yid}")
                except Exception as e:
                    st.error(f"Erro ao salvar ano: {e}")

    # Add event
    st.markdown("#### Adicionar evento")
    years = get_years()
    year_options = {f"{y['year']} ({y['id'][:8]})": y["id"] for y in years} if years else {}
    year_sel = st.selectbox("Ano do evento", options=list(year_options.keys()) or ["—"], index=0)
    ev_title = st.text_input("Título do evento", placeholder="Ex: Abertura do Selo")
    ev_summary = st.text_area("Resumo do evento", placeholder="Breve descrição...")
    ev_start = st.text_input("Data inicial (YYYY-MM-DD)", placeholder="Opcional")
    ev_end = st.text_input("Data final (YYYY-MM-DD)", placeholder="Opcional")
    if st.button("Salvar evento"):
        try:
            yid = year_options.get(year_sel)
            if not yid:
                st.error("Selecione um ano válido.")
            elif not ev_title.strip():
                st.error("Título do evento é obrigatório.")
            else:
                eid = add_event(yid, ev_title.strip(), ev_summary.strip() or None, ev_start.strip() or None, ev_end.strip() or None)
                st.success(f"Evento salvo. ID: {eid}")
        except Exception as e:
            st.error(f"Erro ao salvar evento: {e}")

    # Add sub-event
    st.markdown("#### Adicionar sub-evento")
    if years:
        evs_map = {}
        for y in years:
            evs = get_events_by_year(y["id"])
            for ev in evs:
                evs_map[f"{y['year']} — {ev['title']} ({ev['id'][:8]})"] = ev["id"]

        ev_sel = st.selectbox("Evento do sub-evento", options=list(evs_map.keys()) or ["—"])
        se_title = st.text_input("Título do sub-evento")
        se_summary = st.text_area("Resumo do sub-evento")
        se_start = st.text_input("Data inicial (YYYY-MM-DD)", placeholder="Opcional")
        se_end = st.text_input("Data final (YYYY-MM-DD)", placeholder="Opcional")
        if st.button("Salvar sub-evento"):
            try:
                evid = evs_map.get(ev_sel)
                if not evid:
                    st.error("Selecione um evento válido.")
                elif not se_title.strip():
                    st.error("Título do sub-evento é obrigatório.")
                else:
                    sid = add_subevent(evid, se_title.strip(), se_summary.strip() or None, se_start.strip() or None, se_end.strip() or None)
                    st.success(f"Sub-evento salvo. ID: {sid}")
            except Exception as e:
                st.error(f"Erro ao salvar sub-evento: {e}")
    else:
        st.info("Cadastre um ano e um evento antes de criar sub-eventos.")

    st.markdown("#### Adicionar conteúdo (descrições, profecias, análises)")
    target_type = st.selectbox("Tipo do alvo", options=["event", "subevent"])
    target_id = st.text_input("ID do alvo (copie da lista acima)")
    content_kind = st.selectbox("Tipo de conteúdo", options=["Descrição", "Profecia", "Análise"])
    if content_kind == "Profecia":
        ref = st.text_input("Referência bíblica (ex: Daniel 9:24-27)")
    else:
        ref = None
    content_text = st.text_area("Texto")
    if st.button("Salvar conteúdo"):
        try:
            if not target_id.strip():
                st.error("Forneça um ID de alvo válido.")
            elif not content_text.strip():
                st.error("Texto é obrigatório.")
            else:
                if content_kind == "Descrição":
                    cid = add_description(target_type, target_id.strip(), content_text.strip())
                elif content_kind == "Profecia":
                    cid = add_prophecy(target_type, target_id.strip(), ref.strip() if ref else None, content_text.strip())
                else:
                    cid = add_analysis(target_type, target_id.strip(), content_text.strip())
                st.success(f"Conteúdo salvo. ID: {cid}")
        except Exception as e:
            st.error(f"Erro ao salvar conteúdo: {e}")


# ---------------------------
# UI: Gemini study
# ---------------------------
def gemini_study_section():
    st.subheader("Estudo com Gemini (via prompt)")
    if not GEMINI_AVAILABLE:
        st.info("Instale 'google-generativeai' para usar Gemini.")
        return

    years = get_years()
    year_map = {str(y["year"]): y for y in years}
    year_pick = st.selectbox("Selecione ano (opcional)", options=["—"] + list(year_map.keys()))
    selected_year = year_map.get(year_pick)

    selected_event = None
    selected_subevent = None

    if selected_year:
        events = get_events_by_year(selected_year["id"])
        ev_map = {ev["title"]: ev for ev in events} if events else {}
        ev_pick = st.selectbox("Selecione evento (opcional)", options=["—"] + list(ev_map.keys()))
        selected_event = ev_map.get(ev_pick)

        if selected_event:
            subevents = get_subevents(selected_event["id"])
            se_map = {se["title"]: se for se in subevents} if subevents else {}
            se_pick = st.selectbox("Selecione sub-evento (opcional)", options=["—"] + list(se_map.keys()))
            selected_subevent = se_map.get(se_pick)

    prompt = st.text_area("Digite sua pergunta ou orientação de estudo", placeholder="Ex: Compare as profecias de Daniel com os eventos de 2025...")
    if st.button("Consultar Gemini"):
        context = {}
        if selected_year:
            context.update({"year": selected_year["year"]})
        if selected_event:
            context.update({
                "event_id": selected_event["id"],
                "event_title": selected_event["title"],
                "summary": selected_event["summary"],
                "start_date": selected_event["start_date"],
                "end_date": selected_event["end_date"]
            })
        if selected_subevent:
            context.update({
                "subevent_id": selected_subevent["id"],
                "subevent_title": selected_subevent["title"]
            })

        with st.spinner("Consultando Gemini..."):
            answer = call_gemini(prompt, context=context)
        st.markdown("#### Resposta do Gemini")
        st.write(answer)


# ---------------------------
# Main
# ---------------------------
def main():
    st.set_page_config(page_title=APP_TITLE, page_icon="📜", layout="wide")
    ensure_session()

    # Sidebar login
    with st.sidebar:
        st.header("Login do administrador")
        st.text_input("Usuário", key="admin_user", placeholder="admin")
        st.text_input("Senha", key="admin_pw", type="password", placeholder="Digite e pressione Enter", on_change=validate_login)
        if st.session_state.login_msg:
            st.caption(st.session_state.login_msg)

        st.markdown("---")
        st.caption("Pressione Enter na senha para validar sem clicar no botão.")

    # Init DB (online)
    try:
        init_db()
    except Exception as e:
        st.error(f"Falha ao inicializar banco (libSQL/Turso): {e}")
        st.stop()

    st.title(APP_TITLE)
    st.caption("Timeline circular com expansão de eventos, conteúdo detalhado e integração com Gemini (rodando 100% online).")

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
