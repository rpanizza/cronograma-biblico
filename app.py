# app.py
import streamlit as st
import pandas as pd
import json
import os
# Importação do Google Generative AI (para uso futuro)
# from google import genai 

# Nome do arquivo onde os eventos serão salvos
DATA_FILE = 'events.json'

# --- 1. Funções de Persistência de Dados (JSON) ---

def load_events():
    """Carrega os eventos do arquivo JSON. Se o arquivo não existir, retorna dados de exemplo."""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            st.error("Erro ao ler o arquivo events.json. Carregando dados de exemplo.")
            return get_sample_data()
    else:
        # Se não existe, cria o arquivo com dados de exemplo e salva.
        sample_data = get_sample_data()
        save_events(sample_data)
        return sample_data

def save_events(events):
    """Salva a lista de eventos no arquivo JSON."""
    try:
        # Garante que a lista de eventos não é None antes de salvar
        if events is None:
            events = [] 
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(events, f, ensure_ascii=False, indent=4)
    except Exception as e:
        st.error(f"Erro ao salvar dados no JSON: {e}")

def get_sample_data():
    """Retorna dados iniciais de exemplo (Timeline Profética Bíblica)."""
    return [
        {'id': 1, 'date': '0 (Criação)', 'title': 'O Princípio', 'description': '**Gênesis 1:1**. Deus cria os céus e a terra e estabelece o tempo.', 'type': 'Passado'},
        {'id': 2, 'date': 'c. 2000 A.C.', 'title': 'Aliança Abraâmica', 'description': '**Gênesis 12:1-3**. Chamado de Abrão e a promessa de uma grande nação.', 'type': 'Passado'},
        {'id': 3, 'date': 'c. 0', 'title': 'O Cristo', 'description': '**Mateus 1:18**. Nascimento, vida, morte e ressurreição de Jesus Cristo.', 'type': 'Passado'},
        {'id': 4, 'date': 'Futuro Próximo', 'title': 'A Segunda Vinda', 'description': '**Apocalipse 19:11-16**. Retorno triunfal de Cristo.', 'type': 'Futuro'},
        {'id': 5, 'date': 'Eternidade', 'title': 'A Nova Terra', 'description': '**Apocalipse 21:1**. A consumação da história e a morada eterna.', 'type': 'Futuro'}
    ]

# --- 2. Configuração Inicial e Estilo Customizado ---

st.set_page_config(
    page_title="Cronograma Profético Bíblico",
    page_icon="📜",
    layout="wide"
)

# Injeção de CSS para simular a aparência de uma "Timeline" vertical
st.markdown("""
    <style>
    /* Estilos globais */
    .stApp { background-color: #f4f4f9; }
    h1 { color: #3f51b5; }
    
    /* Estrutura da Timeline */
    .timeline {
        position: relative;
        margin-top: 30px;
        padding-left: 50px;
    }

    /* A linha vertical central */
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


# --- 3. Função da Dashboard (Visualização Pública) ---

def show_dashboard():
    
    events = load_events()
    events_df = pd.DataFrame(events)

    st.title("📜 Cronograma Profético Bíblico")

    # Layout dos Botões no Canto Superior Direito
    col_spacer, col_login, col_share = st.columns([12, 1.5, 1]) 
    
    with col_login:
        if st.button("🔑 Login", key='login_button'):
            st.session_state.page = 'login' 
            st.experimental_rerun()
            
    with col_share:
        if st.button("🔗", key='share_button'):
            st.toast("Link de compartilhamento copiado para a área de transferência! (Simulado)")
            
    st.markdown("---") # Separador
    
    # --- Visualização da Timeline ---
    st.subheader("A Linha do Tempo da Profecia")
    
    st.markdown('<div class="timeline">', unsafe_allow_html=True)
    
    # Ordena os eventos pela data (simulando ordem cronológica)
    # Nota: A ordem cronológica correta pode exigir um campo de ordenação numérico escondido.
    for index, event in events_df.iterrows():
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


# --- 4. Função de Login ---

def show_login():
    st.title("🔑 Login Administrador")
    
    with st.form("login_form"):
        username = st.text_input("Usuário")
        password = st.text_input("Senha", type="password")
        submitted = st.form_submit_button("Entrar")
        
        if submitted:
            # Autenticação: ALVO ÚNICO - MUITO INSEGURO, APENAS PARA TESTE!
            if username == os.environ.get('ADMIN_USER', 'admin') and \
               password == os.environ.get('ADMIN_PASSWORD', '123'):
                st.session_state.logged_in = True
                st.session_state.page = 'admin'
                st.success("Login bem-sucedido! Redirecionando...")
                st.experimental_rerun()
            else:
                st.error("Usuário ou senha inválidos.")
    
    if st.button("Voltar para Dashboard"):
        st.session_state.page = 'dashboard'
        st.experimental_rerun()

# --- 5. Função do Painel Admin (CRUD) ---

def show_admin_panel():
    st.title("⚙️ Painel de Administração - Edição de Eventos")
    events = load_events()
    
    if st.button("Logout"):
        del st.session_state.logged_in
        st.session_state.page = 'dashboard'
        st.experimental_rerun()

    st.markdown("---")

    # --- A. ADICIONAR NOVO EVENTO (CREATE) ---
    st.subheader("➕ Adicionar Novo Evento")
    
    with st.form("add_event_form", clear_on_submit=True):
        new_title = st.text_input("Título do Evento (Ex: Segunda Vinda)", key='new_title')
        new_date = st.text_input("Data/Período (Ex: Futuro Próximo)", key='new_date')
        new_description = st.text_area("Descrição (com Referência Bíblica, Ex: **Apocalipse 19**)", key='new_description')
        
        submitted = st.form_submit_button("Salvar Novo Evento")
        
        if submitted:
            if new_title and new_date and new_description:
                # Gera um ID simples (em produção, usar UUID)
                new_id = max(e['id'] for e in events) + 1 if events else 1
                
                new_event = {
                    'id': new_id,
                    'title': new_title,
                    'date': new_date,
                    'description': new_description,
                    'type': 'Novo' # Classificação inicial
                }
                
                events.append(new_event)
                save_events(events)
                # LINHA CORRIGIDA AQUI: A f-string está completa e fechada
                st.success(f"Evento '{new_title}' adicionado com sucesso!")
                st.experimental_rerun()
            else:
                st.error("Por favor, preencha todos os campos para adicionar o evento.")
    
    st.markdown("---")
    
    # --- B. LISTAR/EDITAR/EXCLUIR EVENTOS (READ/UPDATE/DELETE) ---
    st.subheader("📋 Eventos Atuais")
    
    if events:
        events_df = pd.DataFrame(events)
        # Exibe a tabela para visualização e edição
        st.dataframe(events_df, use_container_width=True)
        
        # Placeholder para as funcionalidades de edição e exclusão
        st.info("Funcionalidades de Edição e Exclusão serão implementadas abaixo da tabela.")

    else:
        st.warning("Nenhum evento cadastrado.")


# --- 6. Controle de Páginas (Roteamento Principal) ---

# Inicializa o estado da sessão (se não existir)
if 'page' not in st.session_state:
    st.session_state.page = 'dashboard'

# Roteamento baseado no estado
if st.session_state.page == 'dashboard':
    show_dashboard()
elif st.session_state.page == 'login':
    show_login()
elif st.session_state.page == 'admin' and st.session_state.get('logged_in'):
    show_admin_panel()
else:
    # Caso de segurança: se o estado estiver corrompido, volta para o dashboard
    st.session_state.page = 'dashboard'
    st.experimental_rerun()
