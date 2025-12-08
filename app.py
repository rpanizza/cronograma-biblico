# app.py
import streamlit as st
import pandas as pd
# Importação do Google Generative AI (para uso futuro)
from google import genai 

# --- Configuração Inicial e Estilo Customizado (Timeline) ---
st.set_page_config(
    page_title="Cronograma Profético Bíblico",
    page_icon="📜",
    layout="wide"
)

# Injeção de CSS para simular a aparência de uma "Timeline" vertical
st.markdown("""
    <style>
    /* Estilos globais */
    .stApp {
        background-color: #f4f4f9; 
    }
    h1 {
        color: #3f51b5; /* Azul Profundo */
    }
    
    /* Estrutura da Timeline */
    .timeline {
        position: relative;
        margin-top: 30px;
        padding-left: 50px;
    }

    /* A linha vertical central (pseudo-elemento) */
    .timeline::before {
        content: '';
        position: absolute;
        top: 0;
        bottom: 0;
        left: 20px; 
        width: 4px;
        background-color: #3f51b5;
        border-radius: 2px;
    }
    
    /* Item da Timeline */
    .timeline-item {
        margin-bottom: 40px;
        position: relative;
    }

    /* O círculo que marca o evento */
    .timeline-item::before {
        content: '';
        position: absolute;
        width: 16px;
        height: 16px;
        background-color: #ff9800;
        border: 4px solid #f4f4f9;
        border-radius: 50%;
        left: -38px; 
        top: 0;
        z-index: 1;
    }
    
    .timeline-date {
        font-weight: bold;
        color: #3f51b5;
        margin-bottom: 5px;
    }
    
    .timeline-content {
        background-color: white;
        padding: 15px;
        border-radius: 8px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True)


# --- Dados de Exemplo (simulando a busca no banco de dados) ---
# Em um app real, você leria isso de um arquivo ou BD.
data = {
    'date': ['0 (Criação)', 'c. 2000 A.C.', 'c. 1446 A.C.', 'c. 0', 'Futuro'],
    'title': ['O Princípio', 'Aliança Abraâmica', 'Êxodo do Egito', 'O Cristo', 'A Nova Terra'],
    'description': [
        '**Gênesis 1:1**. Deus cria os céus e a terra e estabelece o tempo.',
        '**Gênesis 12:1-3**. Chamado de Abrão e a promessa de uma grande nação.',
        '**Livro de Êxodo**. Libertação do povo de Israel da escravidão no Egito.',
        '**Mateus 1:18**. Nascimento, vida, morte e ressurreição de Jesus Cristo.',
        '**Apocalipse 21:1**. A consumação da história e a morada eterna.'
    ]
}
events_df = pd.DataFrame(data)

# --- Função da Dashboard (Visualização Pública) ---
def show_dashboard(events):
    
    st.title("📜 Cronograma Profético Bíblico")

    # Layout dos botões na barra lateral
    st.sidebar.header("Ações")
    
    # Botão de Login
    if st.sidebar.button("🔑 Login Administrador"):
        st.session_state.page = 'login' 
        st.experimental_rerun()
    
    # Botão de Compartilhar
    if st.sidebar.button("🔗 Compartilhar Link"):
        st.sidebar.info("Link de compartilhamento em breve!")

    # --- Visualização da Timeline ---
    st.subheader("A Linha do Tempo da Profecia")
    
    # Injeta o contêiner da timeline e itera sobre os eventos
    st.markdown('<div class="timeline">', unsafe_allow_html=True)
    
    for index, event in events.iterrows():
        html_item = f"""
        <div class="timeline-item">
            <div class="timeline-date">{event['date']}</div>
            <div class="timeline-content">
                <h3 class="timeline-title">{event['title']}</h3>
                <p class="timeline-description">{event['description']}</p>
            </div>
        </div>
        """
        st.markdown(html_item, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # Diagrama da timeline vertical
    # 


# --- Função de Login ---
def show_login():
    st.title("🔑 Login Administrador")
    
    # Formulário de Login
    with st.form("login_form"):
        username = st.text_input("Usuário")
        password = st.text_input("Senha", type="password")
        submitted = st.form_submit_button("Entrar")
        
        if submitted:
            # --- Lógica de Autenticação ---
            # OBS: Altere 'admin' e '123' para as credenciais reais de produção!
            if username == "admin" and password == "123": 
                st.session_state.logged_in = True
                st.session_state.page = 'admin'
                st.success("Login bem-sucedido! Redirecionando...")
                st.experimental_rerun()
            else:
                st.error("Usuário ou senha inválidos.")
    
    if st.button("Voltar para Dashboard"):
        st.session_state.page = 'dashboard'
        st.experimental_rerun()

# --- Função do Painel Admin (Edição de Conteúdo) ---
def show_admin_panel():
    st.title("⚙️ Painel de Administração - Edição de Eventos")
    
    st.subheader("Ferramentas de Gerenciamento (CRUD)")
    st.info("Aqui será implementado o sistema para **Adicionar**, **Editar** e **Excluir** eventos da linha do tempo.")
    
    # --- Seção Futura: Integração Gemini ---
    st.subheader("Assistente de Conteúdo (Gemini)")
    st.warning("Para usar o Gemini, você precisará de uma chave de API (`os.environ['GEMINI_API_KEY']`).")
    
    if st.button("Gerar Resumo do Novo Evento com IA"):
        # EXEMPLO DE USO FUTURO:
        try:
            # client = genai.Client()
            # prompt = "Gere uma descrição concisa e fiel sobre o evento 'A Parábola do Semeador' (Mateus 13:1-9), usando apenas referências bíblicas."
            # response = client.models.generate_content(prompt)
            # st.markdown(f"**Resultado do Gemini:**\n\n{response.text}")
            st.success("A chamada à API do Gemini está pronta para ser implementada aqui!")
        except Exception as e:
            st.error(f"Erro ao tentar usar a API do Gemini: {e}")
    
    # Botão de Logout
    if st.button("Logout"):
        del st.session_state.logged_in
        st.session_state.page = 'dashboard'
        st.experimental_rerun()

# --- Controle de Páginas (Roteamento Principal) ---

# Inicializa o estado da sessão (se não existir)
if 'page' not in st.session_state:
    st.session_state.page = 'dashboard'

# Roteamento baseado no estado
if st.session_state.page == 'dashboard':
    show_dashboard(events_df)
elif st.session_state.page == 'login':
    show_login()
elif st.session_state.page == 'admin' and st.session_state.get('logged_in'):
    show_admin_panel()
else:
    # Caso de segurança: se o estado estiver corrompido, volta para o dashboard
    st.session_state.page = 'dashboard'
    st.experimental_rerun()
