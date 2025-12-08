import streamlit as st
import json
import os
import uuid 

# --- CONFIGURAÇÃO INICIAL E VERSÕES ---
st.set_page_config(
    page_title="App Cronograma Profético 2.0", 
    layout="centered", 
    initial_sidebar_state="auto"
)

# Versão do Aplicativo (App) - Inicialização do Projeto 2.0 com Login
VERSAO_APP = "2.0.0" 
# Versão do Conteúdo (Cronologia) - Inicial
VERSAO_CONTEUDO = "26.0101.1" 

# Configurações de Acesso
ARQUIVO_DADOS = 'cronograma_v2.json'
SENHA_CORRETA = "R$Masterkey01" # Senha de Admin

# --- FUNÇÕES DE DADOS (SIMPLIFICADAS PARA V2) ---

def carregar_dados():
    """Carrega dados ou retorna a estrutura padrão inicial."""
    dados_padrao = {
        "titulo": "📜 Cronograma Profético Dinâmico (V2)",
        "eventos": [],
        "config": {
            "versao_app": VERSAO_APP,
            "versao_conteudo": VERSAO_CONTEUDO,
            "titulo_projeto": "App Cronograma Profético 2.0"
        }
    }
    if not os.path.exists(ARQUIVO_DADOS):
        return dados_padrao
    with open(ARQUIVO_DADOS, 'r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return dados_padrao

def salvar_dados(dados):
    """Salva a estrutura completa de dados."""
    with open(ARQUIVO_DADOS, 'w', encoding='utf-8') as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)

# --- ESTADOS INICIAIS ---

if 'is_admin' not in st.session_state: st.session_state['is_admin'] = False
if 'admin_pass_input' not in st.session_state: st.session_state['admin_pass_input'] = ""
if 'status_message' not in st.session_state: st.session_state['status_message'] = None


# --- FUNÇÕES DE LAYOUT ---

def display_status():
    """Exibe mensagens de status (sucesso/falha) se houver."""
    if st.session_state.get('status_message'):
        tipo, mensagem = st.session_state['status_message']
        if tipo == 'success':
            st.success(mensagem)
        elif tipo == 'error':
            st.error(mensagem)
        elif tipo == 'warning':
            st.warning(mensagem)
        st.session_state['status_message'] = None 

# --- LOGIN E LOGOUT ---

def handle_login(password_attempt):
    """Processa a tentativa de login."""
    if password_attempt == SENHA_CORRETA:
        st.session_state.is_admin = True
        st.session_state['status_message'] = ('success', "✅ Login de administrador bem-sucedido!")
    else:
        st.session_state.is_admin = False
        st.session_state['status_message'] = ('error', "⚠️ Senha incorreta. Acesso negado.")
    st.rerun()

def handle_logout():
    """Processa o logout."""
    st.session_state.is_admin = False
    st.session_state.admin_pass_input = ""
    st.session_state['status_message'] = ('warning', "🚪 Sessão encerrada. Você saiu da área de administrador.")
    st.rerun()

# --- INTERFACE: ÁREA DO ADMIN (DASHBOARD) ---

def admin_dashboard():
    """Conteúdo exclusivo para o administrador."""
    
    st.header("🔑 Painel de Administração - Dashboard")
    st.success("Bem-vindo de volta! Aqui você controlará a criação e edição do cronograma.")
    
    st.divider()
    
    st.subheader("Configurações do Projeto")
    dados_app = carregar_dados()
    st.write(f"**Título Atual:** {dados_app['config']['titulo_projeto']}")
    st.write(f"**Versão do App:** {dados_app['config']['versao_app']}")
    st.write(f"**Versão do Conteúdo:** {dados_app['config']['versao_conteudo']}")
    
    # Próxima etapa: Adicionar ferramentas de edição aqui
    
# --- INTERFACE: ÁREA PÚBLICA (CRONOGRAMA) ---

def main_app():
    """Conteúdo visível para todos os usuários."""
    
    dados_app = carregar_dados()
    
    st.title(dados_app.get("titulo", "App Cronograma Profético 2.0"))

    st.markdown("---")
    st.header("🖼️ Pré-Visualização do Cronograma")
    st.info("Este conteúdo será o cronograma final. No momento, está vazio. Use o Painel de Administração para adicionar eventos.")
    
    # Rodapé da Aplicação
    st.markdown("---")
    st.caption(f"App v{VERSAO_APP} | Conteúdo v{VERSAO_CONTEUDO}")

# --- BARRA LATERAL (LOGIN) ---

with st.sidebar:
    st.header("⚙️ Ferramentas e Acesso")
    
    if st.session_state.is_admin:
        st.success("✅ Logado como Administrador")
        st.button("🚪 Sair", on_click=handle_logout, key='logout_btn_sidebar')
    else:
        st.subheader("Login de Administrador")
        
        with st.form("login_form"):
            password_input = st.text_input("Senha", type="password", key='login_pass_input')
            submitted = st.form_submit_button("Entrar")
            
            if submitted:
                handle_login(password_input)

# --- EXECUÇÃO PRINCIPAL ---

display_status()

if st.session_state.is_admin:
    admin_dashboard()
else:
    main_app()
