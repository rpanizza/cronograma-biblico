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
        /* CSS Idêntico ao anterior que funcionava bem */
        .timeline-line { border-left: 3px dotted #A9A9A9; padding-left: 10px; margin-left: 10px; min-height: 40px; }
        .line-hoje { border-left: 3px dotted #FFD700; padding-left: 10px; margin-left: 10px; min-height: 40px; }
        .dot-event { font-size: 15px; color: #A9A9A9; margin-right: 5px; display: inline-block; }
        .dot-hoje { font-size: 18px; color: #FFD700; margin-right: 5px; display: inline-block; }
        .event-title { font-size: 1.25em; font-weight: bold; }
        .streamlit-expanderHeader { padding: 0; padding-left: 10px; margin-bottom: -10px; font-size: 1.1em; color: #6c757d; }
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
    
    # Como o st.tabs padrão não sincroniza perfeitamente com variaveis de estado sem rerun,
    # forçamos a renderização do conteúdo da aba clicada manualmente pelo usuário:
    with tabs[1]:
        if st.session_state.admin_tab_selected != 1: # Se o usuário clicou na tab visualmente
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
            if st.button("Entrar"): # Simplificado para teste rápido, pode por senha dps
                 st.session_state.logged_in = True
                 st.rerun()

# --- APP START ---
login_sidebar()

if st.session_state.logged_in:
    admin_page()
else:
    exibir_cronograma()

"""
-------------------------------------------------------------------------
{import streamlit as st
import pandas as pd
from datetime import datetime
import hashlib 

# --- CONFIGURAÇÃO DA PÁGINA E CSS CUSTOMIZADO ---

st.set_page_config(
    page_title="Cronograma Profético Bíblico",
    page_icon="📜",
    layout="wide"
)

# Estilos CSS
def timeline_css():
    st.markdown("""
        <style>
        /* Linha Pontilhada - Cinza Escuro */
        .timeline-line {
            border-left: 3px dotted #A9A9A9; /* Cinza */
            padding-left: 10px; 
            margin-left: 10px; 
            min-height: 40px; 
        }
        /* Linha do marcador HOJE - Cinza */
        .line-hoje {
            border-left: 3px dotted #FFD700; /* Amarelo para contraste */
            padding-left: 10px; 
            margin-left: 10px; 
            min-height: 40px; 
        }
        /* Ponto do Evento - Cinza e Menor */
        .dot-event {
            font-size: 15px; /* Menor */
            color: #A9A9A9; /* Cinza */
            margin-right: 5px;
            display: inline-block;
        }
        /* Ponto HOJE - Amarelo */
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
        /* Expander na área pública */
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

# Chave de acesso administrativa
ADMIN_PASSWORD = "R$Masterkey01" 

# --- MODELO DE DADOS ---

DADOS_INICIAIS = [
    {
        "secao": "I. OS PRIMEIROS TEMPLOS E O EXÍLIO",
        "eventos": [
            {
                "data_principal": "959 a.C.",
                "titulo_evento": "A Dedicação do Primeiro Templo",
                "fatos": [ 
                    {
                        "data_profeta": "Livros dos Reis e Crônicas (c. 560–430 a.C.)",
                        "escritura_ara": "'Assim se concluiu toda a obra que o rei Salomão fez para a Casa do SENHOR. Então, Salomão trouxe as coisas que Davi...' (1 Reis 7:51)",
                        "analise": "O Templo de Salomão levou sete anos. A Glória (Shekinah) de Deus desceu em forma de nuvem."
                    }
                ]
            },
            {
                "data_principal": "586 a.C.",
                "titulo_evento": "A Destruição do Primeiro Templo e Início do Exílio",
                "fatos": [ 
                    {
                        "data_profeta": "Jeremias e Ezequiel (c. 627–571 a.C.)",
                        "escritura_ara": "'Queimaram a Casa de Deus, derribaram os muros de Jerusalém...' (2 Crônicas 36:19)",
                        "analise": "Destruição pela Babilônia, devido à idolatria. Início do Cativeiro Babilônico de 70 anos."
                    }
                ]
            }
        ]
    },
    {
        "secao": "IV. O TEMPO DOS GENTIOS",
        "eventos": [
            {
                "data_principal": "70 d.C.",
                "titulo_evento": "A Destruição do Segundo Templo",
                "fatos": [
                    {
                        "data_profeta": "Jesus Cristo (Mateus 24:2)",
                        "escritura_ara": "'...não ficará aqui pedra sobre pedra que não seja derribada.' (Mateus 24:2)",
                        "analise": "Cumprido pelo General Tito e o exército romano, marcando a Diáspora."
                    }
                ]
            },
            {
                "data_principal": "2024",
                "titulo_evento": "A Guerra em Gaza e o Passo para o Pacto Final",
                "fatos": [
                    {
                        "data_profeta": "Sofonias (c. 640–621 a.C.)",
                        "escritura_ara": "'Porque Gaza será desamparada, e Ascalom, assolada...' (Sofonias 2:4)",
                        "analise": "Os recentes conflitos intensificam a instabilidade na região, pavimentando o caminho para um futuro pacto de sete anos (Daniel 9:27)."
                    },
                     {
                        "data_profeta": "Evento Secundário Relevante (2024)",
                        "escritura_ara": "Não aplicável (Fato Histórico)",
                        "analise": "Morte do líder da Síria (exemplo). Documenta fatos históricos menores que cumprem a profecia a longo prazo (como a destruição de Damasco)."
                    }
                ]
            }
        ]
    },
    {
        "secao": "VI. EVENTOS FUTUROS",
        "eventos": [
             {
                "data_principal": "Futuro Iminente",
                "titulo_evento": "A Destruição de Damasco (Síria)",
                "fatos": [
                    {
                        "data_profeta": "Isaías (c. 740–700 a.C.)",
                        "escritura_ara": "'Eis que Damasco será tirada, para deixar de ser cidade, e será um montão de ruínas.' (Isaías 17:1)",
                        "analise": "Previsão de destruição completa. Sua concretização seria o último grande evento regional antes da Grande Tribulação."
                    }
                ]
            }
        ]
    }
]


# Inicializa o Session State
if 'cronograma' not in st.session_state:
    st.session_state.cronograma = DADOS_INICIAIS
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
# Novo estado para controlar a aba admin selecionada e o evento de destino para o botão '+'
if 'admin_tab_selected' not in st.session_state:
    st.session_state.admin_tab_selected = 0
if 'target_event_id' not in st.session_state:
    st.session_state.target_event_id = None 


# --- FUNÇÕES DE EXIBIÇÃO (Visão Pública) ---

def exibir_fato(fato):
    """Renderiza um fato profético/histórico dentro do Expander Detalhes."""
    st.markdown(f"**📅 Profeta/Fonte:** {fato['data_profeta']}")
    
    with st.container(border=True):
        st.markdown("**📖 Escrituras (ARA):**")
        st.markdown(f"*{fato['escritura_ara']}*")
        st.markdown("**🌍 Análise:**")
        st.markdown(fato['analise'])
    st.markdown("---") # Separador entre fatos

def exibir_evento(evento, show_line=True):
    """Renderiza o título do evento e o Expander de Detalhes na mesma linha, agora com chave única e label de seta."""
    
    # ----------------------------------------------------
    # CHAVE ÚNICA DETERMINÍSTICA PARA EVITAR CONFLITOS
    # ----------------------------------------------------
    unique_str = f"{evento['data_principal']}-{evento['titulo_evento']}"
    expander_key = f"pub_exp_{hashlib.sha1(unique_str.encode('utf-8')).hexdigest()}"
    # ----------------------------------------------------
    
    col_dot, col_title, col_expand = st.columns([0.05, 0.70, 0.25])
    
    with col_dot:
        st.markdown('<div class="dot-event">⚪</div>', unsafe_allow_html=True)
        if show_line:
            st.markdown('<div class="timeline-line"></div>', unsafe_allow_html=True)
            
    with col_title:
        st.markdown(f'<p class="event-title">{evento["data_principal"]} | {evento["titulo_evento"]}</p>', unsafe_allow_html=True)
    
    with col_expand:
        with st.expander(label="▶️", expanded=False, key=expander_key):
            st.subheader("Fatos, Profecias e Análises Correlacionadas")
            
            if st.session_state.logged_in:
                st.info("Logado: Você pode adicionar novos fatos aqui.")
                
            for fato in evento['fatos']:
                exibir_fato(fato)
                
            if st.session_state.logged_in:
                st.markdown(f"**Atenção Admin:** Use a aba 'Adicionar Fato' na Área Administrativa para adicionar novos itens ao evento **'{evento['titulo_evento']}'**.")


def exibir_marcador_hoje():
    """Insere o marcador 'HOJE' na timeline."""
    col_dot, col_content, _ = st.columns([0.05, 0.70, 0.25])
    
    with col_dot:
        st.markdown('<div class="dot-hoje">⭐</div>', unsafe_allow_html=True)
        st.markdown('<div class="line-hoje"></div>', unsafe_allow_html=True)
            
    with col_content:
        st.markdown(f'<p class="event-title">📍 **HOJE ({datetime.now().year})**</p>', unsafe_allow_html=True)
        st.info("A partir deste ponto, o relógio profético está em fase de preparação para os eventos futuros.")


def exibir_cronograma():
    """Renderiza o cronograma completo."""
    st.title("📜 Cronograma Profético Bíblico")
    st.markdown("Uma timeline organizada por eventos principais, profecias e análises correlacionadas.")
    st.divider()

    hoje_inserido = False
    
    for secao_data in st.session_state.cronograma:
        secao = secao_data['secao']
        st.header(secao)
        st.markdown("---")
        
        is_future_section = secao.startswith('VI.') or secao.startswith('VII.') or secao.startswith('VIII.')

        if is_future_section and not hoje_inserido:
            exibir_marcador_hoje()
            hoje_inserido = True
            st.header(secao)
            st.markdown("---")
        
        for i, evento in enumerate(secao_data['eventos']):
            show_line = i < len(secao_data['eventos']) - 1 
            exibir_evento(evento, show_line)
            st.markdown("<br>") 

    if not hoje_inserido:
          exibir_marcador_hoje()


# --- FUNÇÕES DE ADMINISTRAÇÃO ---

def get_all_events_options():
    """Retorna uma lista de rótulos de eventos E IDs para o selectbox."""
    events = []
    for secao in st.session_state.cronograma:
        for evento in secao['eventos']:
            # Gera um ID determinístico para uso interno
            unique_str = f"{secao['secao']}-{evento['data_principal']}-{evento['titulo_evento']}"
            evento_id = hashlib.sha1(unique_str.encode('utf-8')).hexdigest()
            events.append({"id": evento_id, "label": f"[{secao['secao']}] {evento['data_principal']} | {evento['titulo_evento']}"})
    return events


def admin_adicionar_fato_evento(target_event_id=None):
    """
    Página unificada para estudos e adição de Eventos ou Fatos.
    Agora permite escolher se o item é um novo Evento Pai ou um Fato filho.
    """
    
    st.subheader("🤖 Ambiente de Estudo com Gemini")
    st.info("Use este campo para interagir com o Gemini 3 Pro para formatar escrituras fielmente e validar/revisar análises antes de adicionar.")
    
    prompt = st.text_area("Insira o texto da profecia/análise para o Gemini revisar ou formatar:", key="gemini_prompt", height=100)
    
    if st.button("Analisar com Gemini (Integração Futura)", disabled=True):
        st.warning("Integração da API Gemini ainda pendente.")

    st.divider()

    st.subheader("➕ Adicionar Novo Item ao Cronograma")
    
    # --- CHECKBOX PARA HABILITAR/DESABILITAR VINCULAÇÃO ---
    # Se marcado: Adiciona Fato a um Pai existente.
    # Se desmarcado: Cria um novo Evento Pai.
    vincular_existente = st.checkbox("Vincular a um Evento Pai existente? (Adicionar sub-fato)", value=True if target_event_id else False)

    events_options = get_all_events_options()
    
    selected_event_id = None
    
    # Lógica de interface baseada na checkbox
    if vincular_existente:
        # --- MODO: ADICIONAR FATO (FILHO) ---
        default_index = 0
        if target_event_id and events_options:
            try:
                for i, opt in enumerate(events_options):
                    if opt['id'] == target_event_id:
                        default_index = i
                        break
            except Exception:
                pass
        
        selected_event_label = st.selectbox(
            "Selecione o Evento Pai onde o Fato será adicionado:",
            options=[opt['label'] for opt in events_options],
            index=default_index,
            key="select_parent_event"
        )
        
        if events_options and selected_event_label:
            selected_event_id = next((opt['id'] for opt in events_options if opt['label'] == selected_event_label), None)
            
        st.caption("Preencha abaixo os detalhes do fato (profecia, análise, etc).")

    else:
        # --- MODO: CRIAR NOVO EVENTO (PAI) ---
        st.markdown("### 🆕 Criando Novo Evento Principal")
        col_new_sec, col_new_date = st.columns([0.7, 0.3])
        novo_evento_secao = col_new_sec.text_input("Seção (Ex: VII. A GRANDE TRIBULAÇÃO)", placeholder="Seção existente ou nova")
        novo_evento_data = col_new_date.text_input("Data do Evento", placeholder="Ex: 2030")
        novo_evento_titulo = st.text_input("Título do Novo Evento", placeholder="Ex: O Início dos Juízos")
        
        st.caption("Preencha abaixo o primeiro fato/análise deste novo evento.")

    with st.form("form_novo_item", clear_on_submit=True):
        st.markdown("**Conteúdo do Fato/Profecia/Análise**")
        novo_data_profeta = st.text_input("Profeta/Fonte/Data Específica", key="input_fato_profeta", placeholder="Ex: Isaías (c. 700 a.C.)")
        nova_escritura = st.text_area("📖 Escrituras (ARA) - Fiel às palavras", key="input_fato_escritura")
        nova_analise = st.text_area("🌍 Análise (Como este fato se encaixa na profecia/evento)", key="input_fato_analise")
        
        submit_button = st.form_submit_button("Salvar Item")
        
        if submit_button:
            # Dados do Fato (Comum para ambos os casos)
            if not (novo_data_profeta and (nova_escritura or nova_analise)):
                st.error("Preencha o Profeta/Fonte e ao menos a Escritura ou a Análise.")
            else:
                novo_fato = {
                    "data_profeta": novo_data_profeta,
                    "escritura_ara": nova_escritura,
                    "analise": nova_analise
                }

                if vincular_existente:
                    # --- SALVAR COMO FILHO ---
                    if selected_event_id:
                        found = False
                        for secao in st.session_state.cronograma:
                            for evento in secao['eventos']:
                                current_unique_str = f"{secao['secao']}-{evento['data_principal']}-{evento['titulo_evento']}"
                                current_event_id = hashlib.sha1(current_unique_str.encode('utf-8')).hexdigest()
                                
                                if current_event_id == selected_event_id:
                                    evento['fatos'].append(novo_fato)
                                    found = True
                                    break
                            if found: break
                        
                        if found:
                            st.success(f"Novo Fato adicionado com sucesso ao evento existente!")
                            st.session_state.target_event_id = None
                            st.rerun()
                        else:
                            st.error("Erro ao encontrar o evento pai selecionado.")
                    else:
                        st.error("Selecione um evento pai.")
                
                else:
                    # --- SALVAR COMO NOVO EVENTO PAI ---
                    if novo_evento_secao and novo_evento_data and novo_evento_titulo:
                        # Cria estrutura do novo evento
                        novo_evento_struct = {
                            "data_principal": novo_evento_data,
                            "titulo_evento": novo_evento_titulo,
                            "fatos": [novo_fato] # Adiciona o fato inicial
                        }
                        
                        # Verifica se a seção já existe
                        secao_existe = False
                        for secao in st.session_state.cronograma:
                            if secao['secao'] == novo_evento_secao:
                                secao['eventos'].append(novo_evento_struct)
                                secao_existe = True
                                break
                        
                        # Se seção não existe, cria nova seção
                        if not secao_existe:
                            nova_secao_struct = {
                                "secao": novo_evento_secao,
                                "eventos": [novo_evento_struct]
                            }
                            st.session_state.cronograma.append(nova_secao_struct)
                        
                        st.success(f"Novo Evento '{novo_evento_titulo}' criado com sucesso!")
                        st.rerun()
                    else:
                        st.error("Para criar um novo evento pai, preencha Seção, Data e Título.")


def admin_exibir_estrutura():
    """Gerenciar a estrutura usando expansão por clique (Tree View)."""
    st.subheader("📝 Gerenciar Estrutura de Seções e Eventos")
    st.info("Clique para expandir as seções e eventos. Use o botão `+ Fato` para adicionar sub-fatos.")

    for i_secao, secao_data in enumerate(st.session_state.cronograma):
        secao = secao_data['secao']
        secao_key = f"sec_exp_{hashlib.sha1(secao.encode('utf-8')).hexdigest()}"
        
        with st.expander(label=f"📂 **{secao}** ({len(secao_data['eventos'])} Eventos)", expanded=False, key=secao_key):
            for i_evento, evento in enumerate(secao_data['eventos']):
                unique_str = f"{secao}-{evento['data_principal']}-{evento['titulo_evento']}"
                evento_id = hashlib.sha1(unique_str.encode('utf-8')).hexdigest()
                evento_key = f"evt_exp_{evento_id}"
                
                col_title, col_button = st.columns([0.8, 0.2])
                with col_title:
                    label_evento = f"🗓️ {evento['data_principal']} | {evento['titulo_evento']} ({len(evento['fatos'])} Fatos)"
                    with st.expander(label=label_evento, expanded=False, key=evento_key):
                        st.caption("Fatos Contidos:")
                        for i_fato, fato in enumerate(evento['fatos']):
                            st.markdown(f"**⚪ Fato {i_fato+1}:** {fato['data_profeta']}")
                            st.markdown(f" > *Escritura:* {fato['escritura_ara'][:80].strip()}...")
                        st.markdown("---")
                
                with col_button:
                    if st.button(f"➕ Fato", key=f"add_fato_{evento_id}"):
                        st.session_state.admin_tab_selected = 0 
                        st.session_state.target_event_id = evento_id
                        st.rerun()

def admin_page():
    """Página de administração principal."""
    st.title("🔑 Área Administrativa")
    st.markdown("Gerencie o cronograma de eventos proféticos.")
    st.divider()
    
    tabs = ["➕ Estudo e Adição (Fatos/Eventos)", "📝 Gerenciar Estrutura", "📄 JSON Bruto"]
    
    selected_tab_index = st.session_state.admin_tab_selected
    tabs_list = st.tabs(tabs)
    
    # Renderização Condicional baseada na aba
    if st.session_state.admin_tab_selected == 0:
        with tabs_list[0]:
            target_id = st.session_state.get('target_event_id', None)
            admin_adicionar_fato_evento(target_id)
            if 'target_event_id' in st.session_state and st.session_state.target_event_id is not None:
                 st.session_state.target_event_id = None 

    elif st.session_state.admin_tab_selected == 1:
        with tabs_list[1]:
            admin_exibir_estrutura()

    elif st.session_state.admin_tab_selected == 2:
        with tabs_list[2]:
            st.subheader("📄 Gerenciar Estrutura Bruta (JSON)")
            st.json(st.session_state.cronograma, expanded=False)

    # Detecção manual de clique na aba não é perfeita sem callbacks complexos em Streamlit puro,
    # mas o estado 'admin_tab_selected' controla qual conteúdo é renderizado primariamente
    # se a navegação vier dos botões internos. Se o usuário clicar nas tabs, o Streamlit
    # gerencia a visualização, mas as variáveis de estado podem não sincronizar imediatamente
    # sem um componente customizado. Para este uso, focar na navegação interna (botões) é mais seguro.

def login_sidebar():
    """Função para o login na barra lateral."""
    if st.session_state.logged_in:
        st.sidebar.success("Logado como Administrador!")
        if st.sidebar.button("Logout"):
            st.session_state.logged_in = False
            st.rerun()
    else:
        st.sidebar.header("🔑 Área Administrativa")
        password = st.sidebar.text_input("Senha", type="password")
        if st.sidebar.button("Entrar"):
            if password == ADMIN_PASSWORD:
                st.session_state.logged_in = True
                st.sidebar.success("Login bem-sucedido!")
                st.rerun()
            else:
                st.sidebar.error("Senha incorreta.")

# --- FLUXO PRINCIPAL DO APLICATIVO ---

login_sidebar()

if st.session_state.logged_in:
    admin_page()
else:
    exibir_cronograma()
