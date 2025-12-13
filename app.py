import streamlit as st
import sqlitecloud
import google.generativeai as genai

# Configurações
APP_TITLE = "Cronograma Bíblico"
DB_URL = st.secrets.get("SQLITECLOUD_URL")
GEMINI_KEY = st.secrets.get("GOOGLE_API_KEY")

# Conexão com SQLiteCloud
def get_conn():
    if not DB_URL:
        raise RuntimeError("SQLITECLOUD_URL não está configurado.")
    return sqlitecloud.connect(DB_URL)

# Teste de conexão
def test_db_connection():
    try:
        conn = get_conn()
        conn.close()
        return "✅ Conexão com SQLiteCloud OK."
    except Exception as e:
        return f"❌ Erro de conexão: {e}"

# Configura Gemini
def setup_gemini():
    if not GEMINI_KEY:
        return "❌ GOOGLE_API_KEY não configurado."
    try:
        genai.configure(api_key=GEMINI_KEY)
        return "✅ Gemini configurado."
    except Exception as e:
        return f"❌ Erro ao configurar Gemini: {e}"

# Consulta Gemini
def consultar_gemini(pergunta):
    try:
        modelo = genai.GenerativeModel("gemini-1.5-flash")
        resposta = modelo.generate_content(pergunta)
        return resposta.text
    except Exception as e:
        return f"❌ Erro ao consultar Gemini: {e}"

# Interface Streamlit
def main():
    st.set_page_config(page_title=APP_TITLE, page_icon="📜", layout="wide")
    st.title(APP_TITLE)
    st.caption("Aplicativo conectado ao SQLiteCloud e Gemini")

    with st.sidebar:
        st.subheader("🔧 Testes de conexão")
        if st.button("Testar banco"):
            st.info(test_db_connection())
        if st.button("Testar Gemini"):
            st.info(setup_gemini())

    st.subheader("📖 Estudo com Gemini")
    pergunta = st.text_area("Digite sua pergunta bíblica")
    if st.button("Consultar"):
        if pergunta.strip():
            resposta = consultar_gemini(pergunta.strip())
            st.markdown("### Resposta do Gemini")
            st.write(resposta)
        else:
            st.warning("Digite uma pergunta antes de consultar.")

if __name__ == "__main__":
    main()
