import streamlit as st
import json
import uuid
import requests

# ==============================
# CONFIGURAÇÕES DO APP
# ==============================
st.set_page_config(page_title="Estudo Bíblico Profético", layout="wide")

# Função para carregar dados
def load_data():
    try:
        with open("data.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

# Função para salvar dados
def save_data(data):
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# ==============================
# LOGIN
# ==============================
def login():
    st.sidebar.title("Login do Administrador")
    user = st.sidebar.text_input("Usuário")
    password = st.sidebar.text_input("Senha", type="password")
    if st.sidebar.button("Entrar"):
        if user == "admin" and password == "1234":  # exemplo simples
            st.session_state["auth"] = True
        else:
            st.sidebar.error("Usuário ou senha inválidos")

# ==============================
# GEMINI INTEGRAÇÃO
# ==============================
def gemini_query(prompt, token):
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"
    headers = {"Authorization": f"Bearer {token}"}
    body = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    response = requests.post(url, headers=headers, json=body)
    if response.status_code == 200:
        return response.json()["candidates"][0]["content"]["parts"][0]["text"]
    else:
        return f"Erro: {response.text}"

# ==============================
# INTERFACE PRINCIPAL
# ==============================
def main():
    if "auth" not in st.session_state:
        st.session_state["auth"] = False

    if not st.session_state["auth"]:
        login()
        return

    st.title("📖 Estudo Bíblico Profético")
    data = load_data()

    # Timeline
    st.subheader("Timeline Profética")
    for ano, eventos in sorted(data.items()):
        st.markdown(f"### 📅 {ano}")
        for evento in eventos:
            st.markdown(f"- **Evento:** {evento['titulo']} (ID: {evento['id']})")
            if "descricao" in evento:
                st.write(f"Descrição: {evento['descricao']}")
            if "profecias" in evento:
                st.write(f"Profecias: {', '.join(evento['profecias'])}")
            if "analises" in evento:
                st.write(f"Análises: {', '.join(evento['analises'])}")

    # Área de administração
    st.subheader("Gerenciar Cronograma")
    ano = st.text_input("Ano do evento")
    titulo = st.text_input("Título do evento")
    descricao = st.text_area("Descrição")
    profecias = st.text_area("Profecias (separadas por vírgula)")
    analises = st.text_area("Análises (separadas por vírgula)")

    if st.button("Adicionar Evento"):
        novo_evento = {
            "id": str(uuid.uuid4()),
            "titulo": titulo,
            "descricao": descricao,
            "profecias": [p.strip() for p in profecias.split(",") if p.strip()],
            "analises": [a.strip() for a in analises.split(",") if a.strip()]
        }
        if ano not in data:
            data[ano] = []
        data[ano].append(novo_evento)
        save_data(data)
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
