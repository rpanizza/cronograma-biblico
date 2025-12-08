# app.py
import streamlit as st
import pandas as pd
import os 
# Importação do Google Generative AI (para uso futuro)
# from google import genai 

# --- 1. Configuração Inicial e Estilo Customizado (Timeline) ---

st.set_page_config(
    page_title="Cronograma Profético Bíblico",
    page_icon="📜",
    layout="wide" # Ocupa toda a largura da tela
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

# --- 2. Dados de Exemplo (Hardcoded) ---
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


# --- 3. Função da Dashboard (Visualização Pública) ---

def show_dashboard(events):
    
    st.title("📜 Cronograma Profético Bíblico")

    # Layout dos Botões no Canto Superior Direito (usando colunas)
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
    
    # Renderiza os eventos
    for index, event in events.iterrows():
        # INÍCIO DA CORREÇÃO: Envolvendo a atribuição em parênteses
        html_item = (
            f"""
            <div class="timeline-item">
                <div class="timeline-date">{event['date']}</div>
                <div class="timeline-content">
                    <h3 class="timeline-title">{event['title']}</h3>
                    <p class="timeline-description">{event['description']}</p>
                </div>
            </div>
            """
        )
        # FIM DA CORREÇÃO
        st.markdown(html_item, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)


# --- 4. Função de Login ---

def show_login():
    st.title("🔑 Login Administrador")
    
    with st.form("login_form"):
        username = st.text_input("Usuário")
        password = st.text_input("Senha", type="password")
        submitted = st.form_submit_button
