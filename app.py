import streamlit as st
import pandas as pd
from datetime import datetime
import hashlib 

# --- CONFIGURAÇÃO DA PÁGINA E CSS CUSTOMIZADO ---

st.set_page_config(
    page_title="Cronograma Profético Bíblico",
    page_icon="📜",
    layout="wide"
)

# Estilos CSS (Cor Cinza e Tamanho do Ponto Reduzido)
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
        /* Expander na área pública (Manter o visual padrão simples) */
        .st-emotion-cache-19a6x5k { /* Classe específica do header do expander Streamlit */
            padding: 0;
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
                "fatos": [ # Fato 1
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
                "fatos": [ # Fato 1
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
    """Renderiza o título do evento e o Expander de Detalhes na mesma linha."""
    
    # 1. Colunas para alinhar visualmente: Ponto/Linha, Título/Data, e Expander/Botão
    col_dot, col_title, col_expand = st.columns([0.05, 0.70, 0.25])
    
    with col_dot:
        st.markdown('<div class="dot-event">⚪</div>', unsafe_allow_html=True)
        if show_line:
            st.markdown('<div class="timeline-line"></div>', unsafe_allow_html=True)
            
    with col_title:
        # Título do evento principal
        st.markdown(f'<p class="event-title">{evento["data_principal"]} | {evento["titulo_evento"]}</p>', unsafe_allow_html=True)
    
    with col_expand:
        # Expander de Detalhes no final da linha do evento (Sem key - mantendo o modelo funcional original)
        with st.expander("Detalhes (Fatos, Profecias, Análises)"):
            if st.session_state.logged_in:
                st.info("Logado: Você pode adicionar novos fatos aqui.")
                
            for fato in evento['fatos']:
                exibir_fato(fato)
                
            # Botão para o administrador adicionar novos fatos
            if st.session_state.logged_in:
                # O administrador adiciona o fato pelo formulário na Área Admin
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
    
    # Itera pelas Seções (I, II, III...)
    for secao_data in st.session_state.cronograma:
        secao = secao_data['secao']
        st.header(secao)
        st.markdown("---")
        
        is_future_section = secao.startswith('VI.') or secao.startswith('VII.') or secao.startswith('VIII.')

        # Insere o marcador HOJE antes da primeira seção de eventos futuros
        if is_future_section and not hoje_inserido:
            exibir_marcador_hoje()
            hoje_inserido = True
            st.header(secao) # Repete o cabeçalho para a seção futura
            st.markdown("---")
        
        # Itera pelos Eventos dentro da Seção
        for i, evento in enumerate(secao_data['eventos']):
            show_line = i < len(secao_data['eventos']) - 1 # Mostra a linha, exceto no último evento da seção
            exibir_evento(evento, show_line)
            st.markdown("<br>") # Espaçamento entre eventos

    # Caso não haja seções futuras, insere HOJE no final
    if not hoje_inserido:
          exibir_marcador_hoje()


# --- FUNÇÕES DE ADMINISTRAÇÃO (Alteradas) ---

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

def get_all_events_options():
    """Retorna uma lista de rótulos de eventos E IDs para o selectbox."""
    events = []
    for secao in st.session_state.cronograma:
        for i_evento, evento in enumerate(secao['eventos']):
            # Gera um ID determinístico para uso interno
            unique_str = f"{secao['secao']}-{evento['data_principal']}-{evento['titulo_evento']}"
            evento_id = hashlib.sha1(unique_str.encode('utf-8')).hexdigest()
            events.append({"id": evento_id, "label": f"[{secao['secao']}] {evento['data_principal']} | {evento['titulo_evento']}"})
    return events


def admin_adicionar_fato(target_event_id=None):
    """Página unificada para estudos e adição de fatos/eventos (Tab 1)."""
    
    st.subheader("🤖 Ambiente de Estudo com Gemini")
    st.info("Use este campo para interagir com o Gemini 3 Pro para formatar escrituras fielmente e validar/revisar análises antes de adicionar um Fato.")
    
    # Campo de Prompt do Gemini
    prompt = st.text_area("Insira o texto da profecia/análise para o Gemini revisar ou formatar:", key="gemini_prompt", height=150)
    
    if st.button("Analisar com Gemini (Integração Futura)", disabled=True):
        st.warning("Integração da API Gemini ainda pendente.")

    st.divider()

    st.subheader("➕ Adicionar Novo Fato a um Evento Existente")
    
    events_options = get_all_events_options()
    
    default_index = 0
    selected_event_id = None
    if target_event_id and events_options:
        try:
            # Tenta encontrar o índice do evento de destino
            for i, opt in enumerate(events_options):
                if opt['id'] == target_event_id:
                    default_index = i
                    break
        except Exception:
            pass
    
    # Selectbox para escolher o Evento Pai
    selected_event_label = st.selectbox(
        "Selecione o Evento Pai onde o Fato será adicionado:",
        options=[opt['label'] for opt in events_options],
        index=default_index,
        key="select_parent_event"
    )
    
    # Obtém o ID do evento selecionado
    if events_options:
        selected_event_id = events_options[default_index]['id'] if not selected_event_label else next((opt['id'] for opt in events_options if opt['label'] == selected_event_label), None)


    with st.form("form_novo_fato", clear_on_submit=True):
        st.markdown("**Novo Fato (Profecia/Análise/Histórico)**")
        novo_data_profeta = st.text_input("Profeta/Fonte/Data Específica do Fato", key="input_fato_profeta")
        
        # Conforme a instrução de ser fiel às escrituras, o campo Escritura é essencial.
        nova_escritura = st.text_area("📖 Escrituras (ARA) - Fiel às palavras", key="input_fato_escritura")
        nova_analise = st.text_area("🌍 Análise (Como este fato se encaixa na profecia/evento)", key="input_fato_analise")
        
        submit_button = st.form_submit_button("Salvar Novo Fato")
        
        if submit_button:
            if selected_event_id and novo_data_profeta and (nova_escritura or nova_analise):
                novo_fato = {
                    "data_profeta": novo_data_profeta,
                    "escritura_ara": nova_escritura,
                    "analise": nova_analise
                }
                
                # Procura o evento pelo ID e anexa o novo fato
                found = False
                for secao in st.session_state.cronograma:
                    for evento in secao['eventos']:
                        # Gera o ID para comparação
                        current_unique_str = f"{secao['secao']}-{evento['data_principal']}-{evento['titulo_evento']}"
                        current_event_id = hashlib.sha1(current_unique_str.encode('utf-8')).hexdigest()
                        
                        if current_event_id == selected_event_id:
                            evento['fatos'].append(novo_fato)
                            found = True
                            break
                    if found: break
                
                if found:
                    st.success(f"Novo Fato adicionado com sucesso ao evento: '{evento['titulo_evento']}'!")
                    st.session_state.target_event_id = None # Limpa o target
                    st.rerun() 
                else:
                    st.error("Erro ao encontrar o evento pai.")
            else:
                st.error("Preencha o Profeta/Fonte e ao menos a Escritura ou a Análise.")

# --- FUNÇÃO DE GERENCIAMENTO EM FORMATO DE ÁRVORE ---

def admin_exibir_estrutura():
    """Gerenciar a estrutura usando expansão por clique (Tree View) (Tab 2)."""
    st.subheader("📝 Gerenciar Estrutura de Seções e Eventos")
    st.info("Clique para expandir as seções e eventos. Use o botão `+ Fato` para adicionar fatos rapidamente ao evento.")
    st.warning("⚠️ Para adição de novas Seções ou Eventos principais, ainda é recomendado o uso da Tab 'JSON'.")

    for i_secao, secao_data in enumerate(st.session_state.cronograma):
        secao = secao_data['secao']
        
        # Chave garantidamente única para o Expander da Seção
        secao_key = f"sec_exp_{hashlib.sha1(secao.encode('utf-8')).hexdigest()}"
        
        # Expander da Seção
        with st.expander(label=f"📂 **{secao}** ({len(secao_data['eventos'])} Eventos)", expanded=False, key=secao_key):
            
            for i_evento, evento in enumerate(secao_data['eventos']):
                
                # Cria o ID do evento de forma determinística
                unique_str = f"{secao}-{evento['data_principal']}-{evento['titulo_evento']}"
                evento_id = hashlib.sha1(unique_str.encode('utf-8')).hexdigest()
                
                # Expander do Evento
                evento_key = f"evt_exp_{evento_id}"
                
                # Usamos colunas para alinhar o expander e o botão de atalho
                col_title, col_button = st.columns([0.8, 0.2])
                
                with col_title:
                    # Rótulo do Expander do Evento
                    label_evento = f"🗓️ {evento['data_principal']} | {evento['titulo_evento']} ({len(evento['fatos'])} Fatos)"
                    
                    # Usa o Expander para o evento (com key única)
                    with st.expander(label=label_evento, expanded=False, key=evento_key):
                        st.caption("Fatos Contidos:")
                        
                        # Exibe os fatos contidos
                        for i_fato, fato in enumerate(evento['fatos']):
                            st.markdown(f"**⚪ Fato {i_fato+1}:** {fato['data_profeta']}")
                            st.markdown(f" > *Escritura:* {fato['escritura_ara'][:80].strip()}...")
                        
                        st.markdown("---")
                        # st.button(f"Excluir Evento '{evento['titulo_evento']}'", key=f"del_evt_{evento_id}", disabled=True)
                
                with col_button:
                    # Botão de atalho para adicionar fato
                    if st.button(f"➕ Fato", key=f"add_fato_{evento_id}"):
                        # Redireciona para a Tab de Adição e define o evento alvo
                        st.session_state.admin_tab_selected = 0 
                        st.session_state.target_event_id = evento_id
                        st.rerun()

# --- FUNÇÃO PRINCIPAL ADMIN ---
def admin_page():
    """Página de administração principal com abas reestruturadas."""
    st.title("🔑 Área Administrativa")
    st.markdown("Gerencie o cronograma de eventos proféticos.")
    st.divider()
    
    tabs = ["➕ Estudo e Adição de Fatos/Eventos", "📝 Gerenciar Estrutura (Árvore)", "📄 Gerenciar Estrutura Bruta (JSON)"]
    
    # Usa o estado para manter a aba selecionada após o reruns
    selected_tab_index = st.session_state.admin_tab_selected
    
    # Cria as abas. Nota: Streamlit manipula as abas diretamente no frontend.
    tabs_list = st.tabs(tabs)
    
    # Verifica qual aba foi clicada e atualiza o estado
    # Este é um método simplificado de detecção de mudança de aba, mais robusto seria usar callbacks.
    # No entanto, vamos confiar no st.tabs simples e no reruns:

    if st.session_state.admin_tab_selected == 0:
        with tabs_list[0]:
            # Tab 1: Estudo e Adição (Unificada)
            target_id = st.session_state.get('target_event_id', None)
            admin_adicionar_fato(target_id)
            # Limpa o target_event_id após a exibição/uso (apenas se não estiver sendo usado ativamente)
            # A limpeza é feita dentro de admin_adicionar_fato para ser mais controlada.
            
    elif st.session_state.admin_tab_selected == 1:
        with tabs_list[1]:
            # Tab 2: Gerenciar Estrutura (Árvore)
            admin_exibir_estrutura()

    elif st.session_state.admin_tab_selected == 2:
        with tabs_list[2]:
            # Tab 3: Gerenciar Estrutura Bruta (JSON)
            st.subheader("📄 Gerenciar Estrutura Bruta (JSON)")
            st.info("Use esta aba para inspeção de dados, backup ou edição manual avançada.")
            st.json(st.session_state.cronograma, expanded=False)

    # Lógica de atualização de aba (se o usuário clicar em uma nova aba)
    # Streamlit lida com isso automaticamente na maioria dos casos com st.tabs, 
    # mas o índice inicial deve ser definido corretamente.
    
    # Se o usuário clicar no botão '+' e mudar o 'admin_tab_selected' para 0, o rerun garante a transição.
    

# --- FLUXO PRINCIPAL DO APLICATIVO ---

login_sidebar()

if st.session_state.logged_in:
    admin_page()
else:
    exibir_cronograma()
