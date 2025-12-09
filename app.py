import streamlit as st
import sqlite3
import uuid
import requests

# ==============================
# CONFIGURAÇÕES DO APP
# ==============================
st.set_page_config(page_title="Estudo Bíblico Profético", layout="wide")

# ==============================
# BANCO DE DADOS
# ==============================
def init_db():
    conn = sqlite3.connect("timeline.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS eventos (
            id TEXT PRIMARY KEY,
            ano TEXT,
            titulo TEXT,
            descricao TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS profecias (
            id TEXT PRIMARY KEY,
            evento_id TEXT,
            texto TEXT,
            FOREIGN KEY(evento_id) REFERENCES eventos(id)
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS analises (
            id TEXT PRIMARY KEY,
            evento_id TEXT,
            texto TEXT,
            FOREIGN KEY(evento_id) REFERENCES eventos(id)
        )
    """)
    conn.commit()
    conn.close()

def add_evento(ano, titulo, descricao, profecias, analises):
    conn = sqlite3.connect("timeline.db")
    c = conn.cursor()
    evento_id = str(uuid.uuid4())
    c.execute("INSERT INTO eventos VALUES (?, ?, ?, ?)", (evento_id, ano, titulo, descricao))
    for p in profecias:
        c.execute("INSERT INTO profecias VALUES (?, ?, ?)", (str(uuid.uuid4()), evento_id, p))
    for a in analises:
        c.execute("INSERT INTO analises VALUES (?, ?, ?)", (str(uuid.uuid4()), evento_id, a))
    conn.commit()
    conn.close()

def get_eventos():
    conn = sqlite3.connect("timeline.db")
    c = conn.cursor()
    c.execute("SELECT * FROM eventos ORDER BY ano")
    eventos = c.fetchall()
    result = []
    for e in eventos:
        evento_id, ano, titulo, descricao = e
        c.execute("SELECT texto FROM profecias WHERE evento_id=?", (evento_id,))
        profecias = [row[0] for row in c.fetchall()]
        c.execute("SELECT texto FROM analises WHERE evento_id=?", (evento_id,))
        analises = [row[0] for row in c.fetchall()]
        result.append({
            "id": evento_id,
            "ano": ano,
            "titulo": titulo,
            "descricao": descricao,
            "profecias": profecias,
            "analises": analises
        })
    conn.close()
    return result

# ==============================
# LOGIN
# ==============================
def login():
    st.sidebar.title("Login do Administrador")
    user = st.sidebar.text_input("Usuário")
    password = st.sidebar.text_input("Senha", type="password")
    if st.sidebar.button("Entrar"):
        if user == "admin" and password == "1234":
            st.session_state["auth"] = True
        else:
            st.sidebar.error("Usuário ou senha inválidos")

# ==============================
# GEMINI INTEGRAÇÃO
# ==============================
def gemini_query(prompt, token):
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"
    headers = {"Authorization": f"Bearer {token}"}
    body = {"contents": [{"parts": [{"text": prompt}]}]}
    response = requests.post(url, headers=headers, json=body)
    if response.status_code == 200:
        return response.json()["candidates"][0]["content"]["parts"][0]["text"]
    else:
        return f"Erro: {response.text}"

# ==============================
# INTERFACE PRINCIPAL
# ==============================
def main():
    init_db()

    if "auth" not in st.session_state:
        st.session_state["auth"] = False

    if not st.session_state["auth"]:
        login()
        return

    st.title("📖 Estudo Bíblico Profético")

    # Timeline
    st.subheader("Timeline Profética")
    eventos = get_eventos()
    for e in eventos:
        st.markdown(f"### 📅 {e['ano']}")
        st.markdown(f"- **Evento:** {e['titulo']} (ID: {e['id']})")
        if e["descricao"]:
            st.write(f"Descrição: {e['descricao']}")
        if e["profecias"]:
            st.write(f"Profecias: {', '.join(e['profecias'])}")
        if e["analises"]:
            st.write(f"Análises: {', '.join(e['analises'])}")

    # Área de administração
    st.subheader("Gerenciar Cronograma")
    ano = st.text_input("Ano do evento")
    titulo = st.text_input("Título do evento")
    descricao = st.text_area("Descrição")
    profecias = st.text_area("Profecias (separadas por vírgula)")
    analises = st.text_area("Análises (separadas por vírgula)")

    if st.button("Adicionar Evento"):
        add_evento(
            ano,
            titulo,
            descricao,
            [p.strip() for p in profecias.split(",") if p.strip()],
            [a.strip() for a in analises.split(",") if a.strip()]
        )
        st.success("Evento adicionado com sucesso!")

    # Integração com Gemini
    st.subheader("Estudo com Gemini")
    token = st.text_input("Token Gemini", type="password")
    prompt = st.text_area("Digite seu estudo/prompt")
    if st.button("Enviar ao Gemini") and token and prompt:
        resposta = gemini_query(prompt, token)
        st.markdown("### 📜 Resposta do Gemini")
        st.write(resposta)

if __name__ == "__main__":
    main()
