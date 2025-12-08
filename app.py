import streamlit as st
import pandas as pd
from datetime import datetime
import uuid # Biblioteca para gerar IDs únicos universais

# --- CONFIGURAÇÃO DA PÁGINA E CSS ---

st.set_page_config(
    page_title="Cronograma Profético Bíblico",
    page_icon="📜",
    layout="wide"
)

def timeline_css():
    st.markdown("""
        <style>
        .timeline-line {
            border-left: 3px dotted #A9A9A9;
            padding-left: 10px;
            margin-left: 10px;
            min-height: 40px;
        }
        .line-hoje {
            border-left: 3px dotted #FFD700;
            padding-left: 10px;
            margin-left: 10px;
            min-height: 40px;
        }
        .dot-event {
            font-size: 15px;
            color: #A9A9A9;
            margin-right: 5px;
            display: inline-block;
        }
        .dot-hoje {
            font-size: 18px;
            color: #FFD700;
            margin-right: 5px;
            display: inline-block;
        }
        .event-title {
            font-size: 1.25em;
            font-weight: bold;
        }
        .streamlit-expanderHeader {
            padding: 0;
            padding-left: 10px;
            margin-bottom: -10px;
            font-size: 1.1em;
            color: #6c757d;
        }
        </style>
    """, unsafe_allow_html=True)

timeline_css() 

ADMIN_PASSWORD = "R$Masterkey01" 

# --- NOVA ESTRUTURA DE DADOS (HIERÁRQUICA E COM IDs) ---

# Função auxiliar para criar novos itens facilmente
def criar_item(tipo, dados, subitens=None, id_personalizado=None):
    return {
        "id": id_personalizado if id_personalizado else str(uuid.uuid4()),
        "tipo": tipo, # 'secao', 'evento', 'fato'
        "dados": dados, # Dicionário com os campos específicos (titulo, data, analise, etc)
        "subitens": subitens if subitens else []
    }

DADOS_INICIAIS = [
    criar_item("secao", {"titulo": "I. OS PRIMEIROS TEMPLOS E O EXÍLIO"}, [
        criar_item("evento", {"data": "959 a.C.", "titulo": "A Dedicação do Primeiro Templo"}, [
            criar_item("fato", {
                "profeta": "Livros dos Reis e Crônicas (c. 560–430 a.C.)",
                "escritura": "'Assim se concluiu toda a obra que o rei Salomão fez...'",
                "analise": "O Templo de Salomão levou sete anos. A Glória (Shekinah) desceu."
            })
        ]),
        criar_item("evento", {"data": "586 a.C.", "titulo": "A Destruição do Primeiro Templo"}, [
            criar_item("fato", {
                "profeta": "Jeremias e Ezequiel (c. 627–571 a.C.)",
                "escritura": "'Queimaram a Casa de Deus...'",
                "analise": "Destruição pela Babilônia, devido à idolatria."
            })
        ])
    ]),
    criar_item("secao", {"titulo": "IV. O TEMPO DOS GENTIOS"}, [
        criar_item("evento", {"data": "2024", "titulo": "A Guerra em Gaza"}, [
            criar_item("fato", {
                "profeta": "Sofonias (c. 640–621 a.C.)",
                "escritura": "'Porque Gaza será desamparada...'",
                "analise": "Os recentes conflitos intensificam a instabilidade."
            })
        ])
    ]),
    criar_item("secao", {"titulo": "VI. EVENTOS FUTUROS"}, [
        criar_item("evento", {"data": "Futuro Iminente", "titulo": "A Destruição de Damasco"}, [
            criar_item("fato", {
                "profeta": "Isaías (c. 740–700 a.C.)",
                "escritura": "'Eis que Damasco será tirada...'",
                "analise": "Previsão de destruição completa."
            })
        ])
    ])
]

# Inicializa Session State
if 'cronograma_v2' not in st.session_state:
    st.session_state.cronograma_v2 = DADOS_INICIAIS
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'admin_tab_selected' not in st.session_state:
    st.session_state.admin_tab_selected = 0
if 'target_parent_id' not in st.session_state:
    st.session_state.target_parent_id = None

# --- HELPERS (Funções de Busca Recursiva) ---

def buscar_item_por_id(lista_itens, target_id):
    """Busca recursivamente um item pelo ID em toda a árvore."""
    for item in lista_itens:
        if item['id'] == target_id:
            return item
        # Busca nos subitens
        resultado = buscar_item_por_id(item['subitens'], target_id)
        if resultado:
            return resultado
    return None

def listar_opcoes_pais(lista_itens, nivel=0):
    """Gera uma lista plana para o Selectbox: (ID, Label, Tipo)."""
    opcoes = []
    for item in lista_itens:
        # Define o rótulo baseado no tipo
        if item['tipo'] == 'secao':
            label = f"📂 {item['dados']['titulo']}"
        elif item['tipo'] == 'evento':
            label = f"🗓️ {item['dados'].get('data', '')} | {item['dados']['titulo']}"
        else:
            continue # Não permitimos adicionar filhos a 'fatos' (por enquanto)
            
        opcoes.append({"id": item['id'], "label": label, "tipo": item['tipo']})
        
        # Recursão para pegar filhos que também podem ser pais (ex: Eventos são filhos de Seções, mas pais de Fatos)
        opcoes.extend(listar_opcoes_pais(item['subitens'], nivel + 1))
    return opcoes

# --- VISÃO PÚBLICA (Leitor) ---

def render_fato(item_fato):
    d = item_fato['dados']
    st.markdown(f"**📅 Profeta/Fonte:** {d.get('profeta', '')}")
    with st.container(border=True):
        st.markdown("**📖 Escrituras (ARA):**")
        st.markdown(f"*{d.get('escritura', '')}*")
        st.markdown("**🌍 Análise:**")
        st.markdown(d.get('analise', ''))
    st.markdown("---")

def render_evento(item_evento, show_line=True):
    d = item_evento['dados']
    # Layout visual
    col_dot, col_title, col_expand = st.columns([0.05, 0.70, 0.25])
    
    with col_dot:
        st.markdown('<div class="dot-event">⚪</div>', unsafe_allow_html=True)
        if show_line:
            st.markdown('<div class="timeline-line"></div>', unsafe_allow_html=True)
            
    with col_title:
        st.markdown(f'<p class="event-title">{d.get("data", "")} | {d.get("titulo", "")}</p>', unsafe_allow_html=True)
    
    with col_expand:
        # Expander único e seguro
        key_expander = f"pub_exp_{item_evento['id']}"
        with st.expander(label="▶️", expanded=False, key=key_expander):
            st.subheader("Fatos e Análises")
            for sub in item_evento['subitens']:
                if sub['tipo'] == 'fato':
                    render_fato(sub)
            
            if st.session_state.logged_in:
                st.caption(f"Admin ID: {item_evento['id']}")

def render_marcador_hoje():
    col_dot, col_content, _ = st.columns([0.05, 0.70, 0.25])
    with col_dot:
        st.markdown('<div class="dot-hoje">⭐</div>', unsafe_allow_html=True)
        st.markdown('<div class="line-hoje"></div>', unsafe_allow_html=True)
    with col_content:
        st.markdown(f'<p class="event-title">📍 **HOJE ({datetime.now().year})**</p>', unsafe_allow_html=True)

def exibir_cronograma():
    st.title("📜 Cronograma Profético Bíblico")
    st.markdown("Timeline estruturada por eventos e sub-eventos.")
    st.divider()

    hoje_inserido = False

    # Nível 1: Seções
    for item_secao in st.session_state.cronograma_v2:
        if item_secao['tipo'] == 'secao':
            titulo_secao = item_secao['dados']['titulo']
            
            # Lógica do HOJE
            is_future = "FUTURO" in titulo_secao.upper() or "VII." in titulo_secao or "VI." in titulo_secao
            if is_future and not hoje_inserido:
                render_marcador_hoje()
                hoje_inserido = True
            
            st.header(titulo_secao)
            st.markdown("---")

            # Nível 2: Eventos
            eventos = [sub for sub in item_secao['subitens'] if sub['tipo'] == 'evento']
            for i, item_evento in enumerate(eventos):
                show_line = i < len(eventos) - 1
                render_evento(item_evento, show_line)
                st.markdown("<br>")
    
    if not hoje_inserido:
        render_marcador_hoje()

# --- ÁREA ADMINISTRATIVA ---

def admin_adicionar_item():
    """Formulário inteligente que se adapta baseado no Pai selecionado."""
    st.subheader("➕ Adicionar Novo Item")
    
    # 1. Escolha do Pai
    opcoes_pais = listar_opcoes_pais(st.session_state.cronograma_v2)
    
    # Checkbox para criar raiz (Nova Seção)
    criar_raiz = st.checkbox("Criar Nova Seção Principal (Sem pai)", value=False)
    
    parent_id_selecionado = None
    tipo_novo_item = "secao" # Default
    
    if not criar_raiz:
        # Tenta pré-selecionar se vier do botão '+'
        idx_padrao = 0
        if st.session_state.target_parent_id:
            for i, opt in enumerate(opcoes_pais):
                if opt['id'] == st.session_state.target_parent_id:
                    idx_padrao = i
                    break
        
        escolha = st.selectbox(
            "Selecione onde adicionar (Evento Pai ou Seção):", 
            options=opcoes_pais, 
            format_func=lambda x: x['label'],
            index=idx_padrao
        )
        
        if escolha:
            parent_id_selecionado = escolha['id']
            # Define o tipo do filho baseado no pai
            if escolha['tipo'] == 'secao':
                tipo_novo_item = "evento"
                st.info(f"Adicionando um **EVENTO** dentro da seção: {escolha['label']}")
            elif escolha['tipo'] == 'evento':
                tipo_novo_item = "fato"
                st.info(f"Adicionando um **FATO/ANÁLISE** dentro do evento: {escolha['label']}")
    else:
        st.info("Criando uma nova **SEÇÃO PRINCIPAL**.")

    st.divider()
    
    # 2. Formulário Dinâmico baseado no Tipo
    with st.form("form_add_generico", clear_on_submit=True):
        dados = {}
        
        if tipo_novo_item == "secao":
            dados['titulo'] = st.text_input("Título da Seção", placeholder="Ex: VIII. O NOVO CÉU")
            
        elif tipo_novo_item == "evento":
            col1, col2 = st.columns([0.3, 0.7])
            dados['data'] = col1.text_input("Data", placeholder="Ex: 2030")
            dados['titulo'] = col2.text_input("Título do Evento", placeholder="Ex: O Retorno")
            
        elif tipo_novo_item == "fato":
            dados['profeta'] = st.text_input("Fonte/Profeta", placeholder="Ex: João (Apocalipse)")
            dados['escritura'] = st.text_area("Escritura", placeholder="Texto fiel...")
            dados['analise'] = st.text_area("Análise", placeholder="Explicação...")
            
        submitted = st.form_submit_button("Salvar")
        
        if submitted:
            novo_item = criar_item(tipo_novo_item, dados)
            
            if criar_raiz:
                st.session_state.cronograma_v2.append(novo_item)
                st.success("Nova Seção criada!")
                st.rerun()
            elif parent_id_selecionado:
                pai = buscar_item_por_id(st.session_state.cronograma_v2, parent_id_selecionado)
                if pai:
                    pai['subitens'].append(novo_item)
                    st.success("Item adicionado com sucesso!")
                    st.session_state.target_parent_id = None # Limpa seleção
                    st.rerun()
                else:
                    st.error("Erro: Pai não encontrado.")

def admin_gerenciar_arvore():
    st.subheader("🌳 Estrutura do Cronograma")
    st.info("Visualização hierárquica. Use os botões '+' para adicionar filhos diretamente.")

    # Função recursiva para desenhar a árvore na admin
    def desenhar_no_admin(lista_itens, nivel=0):
        for item in lista_itens:
            tipo = item['tipo']
            dados = item['dados']
            
            # Formatação do Label
            if tipo == 'secao':
                icon = "📂"
                texto = dados['titulo']
            elif tipo == 'evento':
                icon = "🗓️"
                texto = f"{dados.get('data')} | {dados.get('titulo')}"
            else: # Fato
                icon = "⚪"
                texto = f"Fato: {dados.get('profeta')}..."
            
            # Renderização
            # Usamos colunas para indentação visual
            cols = st.columns([0.05 * nivel, 0.85 - (0.05*nivel), 0.1])
            
            with cols[1]:
                # Se não for fato, usa expander. Se for fato, apenas texto.
                if tipo != 'fato':
                    # Gera chave única para expander da árvore
                    tree_key = f"tree_exp_{item['id']}"
                    with st.expander(f"{icon} {texto}", expanded=False):
                        if item['subitens']:
                            desenhar_no_admin(item['subitens'], nivel + 1)
                        else:
                            st.caption("(Vazio)")
                else:
                    st.markdown(f"{icon} {texto}")
            
            with cols[2]:
                # Botão de adicionar filho (Só aparece para Seção e Evento)
                if tipo in ['secao', 'evento']:
                    if st.button("➕", key=f"add_btn_{item['id']}", help=f"Adicionar item em {texto}"):
                        st.session_state.admin_tab_selected = 0
                        st.session_state.target_parent_id = item['id']
                        st.rerun()

    desenhar_no_admin(st.session_state.cronograma_v2)

def admin_page():
    st.title("🔑 Área Administrativa V2")
    
    tabs = st.tabs(["➕ Adicionar Item", "🌳 Gerenciar Árvore", "📄 JSON"])
    
    # Controle de Aba via Botão
    if st.session_state.admin_tab_selected == 0:
        with tabs[0]:
            admin_adicionar_item()
    elif st.session_state.admin_tab_selected == 1:
        with tabs[1]:
             admin_gerenciar_arvore()
    
    # Hack para garantir que o conteúdo carregue se clicar na tab manualmente
    with tabs[1]:
        if st.session_state.admin_tab_selected != 1: 
             admin_gerenciar_arvore()
    with tabs[2]:
        st.json(st.session_state.cronograma_v2)

def login_sidebar():
    if st.session_state.logged_in:
        st.sidebar.success("Admin Logado")
        if st.sidebar.button("Sair"):
            st.session_state.logged_in = False
            st.rerun()
    else:
        with st.sidebar:
            st.header("Login")
            password = st.text_input("Senha", type="password")
            if st.button("Entrar"):
                if password == ADMIN_PASSWORD:
                    st.session_state.logged_in = True
                    st.rerun()
                else:
                    st.error("Senha Incorreta")

# --- APP START ---
login_sidebar()

if st.session_state.logged_in:
    admin_page()
else:
    exibir_cronograma()
