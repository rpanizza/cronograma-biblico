import streamlit as st
import pandas as pd
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA E CSS CUSTOMIZADO ---

st.set_page_config(
    page_title="Cronograma Profético Bíblico",
    page_icon="📜",
    layout="wide"
)

# Estilos CSS (Cor Cinza, Ponto Menor e Estilo de Expander)
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
        /* Linha do marcador HOJE - Amarelo */
        .line-hoje {
            border-left: 3px dotted #FFD700; 
            padding-left: 10px; 
            margin-left: 10px; 
            min-height: 40px; 
        }
        /* Ponto do Evento - Cinza e Menor */
        .dot-event {
            font-size: 15px; 
            color: #A9A9A9; 
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
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        /* Ajuste do estilo do expander para ser mais discreto (seta) */
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

# --- DADOS INICIAIS (Modelo Aninhado) ---
# [ Mantendo o mesmo modelo de dados aninhado da versão anterior ]
DADOS_INICIAIS = [
    {
        "secao": "I. OS PRIMEIROS TEMPLOS E O EXÍLIO",
        "eventos": [
            {
                "id": "e_959ac", # ID único para gerenciamento
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
                "id": "e_586ac",
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
                "id": "e_2024_gaza",
                "data_principal": "2024",
                "titulo_evento": "A Guerra em Gaza e o Passo para o Pacto Final",
                "fatos": [
                    {
                        "data_profeta": "Sofonias (c. 640–621 a.C.)",
                        "escritura_ara": "'Porque Gaza será desamparada, e Ascalom, assolada...' (Sofonias 2:4)",
                        "analise": "Os recentes conflitos intensificam a instabilidade na região, pavimentando o caminho para um futuro pacto de sete anos."
                    },
                     {
                        "data_profeta": "Evento Secundário Relevante (2024)",
                        "escritura_ara": "Não aplicável (Fato Histórico)",
                        "analise": "Morte do líder da Síria (exemplo). Documenta fatos históricos menores que cumprem a profecia a longo prazo."
                    }
                ]
            }
        ]
    },
    {
        "secao": "VI. EVENTOS FUTUROS",
        "eventos": [
             {
                "id": "e_futuro_damasco",
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
if 'admin_tab_selected' not in st.session_state:
    st.session_state.admin_tab_selected = 0 # 0=Estudo, 1=Gerenciar, 2=JSON

# --- FUNÇÕES DE EXIBIÇÃO (Visão Pública) ---

def exibir_fato(fato):
    """Renderiza um fato profético/histórico."""
    st.markdown(f"**📅 Profeta/Fonte:** {fato['data_profeta']}")
    
    with st.container(border=True):
        st.markdown("**📖 Escrituras (ARA):**")
        st.markdown(f"*{fato['escritura_ara']}*")
        st.markdown("**🌍 Análise:**")
        st.markdown(fato['analise'])
    st.markdown("---") 

def exibir_evento(evento, show_line=True):
    """Renderiza o evento principal e o expander abaixo dele."""
    
    # Linha principal (Dot + Título/Data)
    col_dot, col_title = st.columns([0.03, 0.97])
    
    with col_dot:
        st.markdown('<div class="dot-event">⚪</div>', unsafe_allow_html=True)
        # Linha pontilhada vertical
        if show_line:
            st.markdown('<div class="timeline-line"></div>', unsafe_allow_html=True)
            
    with col_title:
        st.markdown(f'<p class="event-title">{evento["data_principal"]} | {evento["titulo_evento"]}</p>', unsafe_allow_html=True)
    
    # Expander de Detalhes (abaixo do evento, ocupando toda a largura)
    # Rótulo minimalista (somente a seta) para atender o pedido de 'caixa oculta'.
    with st.expander(label="▶️", expanded=False, key=f"pub_exp_{evento['id']}"):
        st.subheader("Detalhes: Fatos, Profecias e Análises Correlacionadas")
        for fato in evento['fatos']:
            exibir_fato(fato)


def exibir_marcador_hoje():
    """Insere o marcador 'HOJE' na timeline."""
    col_dot, col_content = st.columns([0.03, 0.97])
    
    with col_dot:
        st.markdown('<div class="dot-hoje">⭐</div>', unsafe_allow_html=True)
        st.markdown('<div class="line-hoje"></div>', unsafe_allow_html=True)
            
    with col_content:
        st.markdown(f'<p class="event-title">📍 **HOJE ({datetime.now().year})**</p>', unsafe_allow_html=True)
        st.info("A partir deste ponto, o relógio profético está em fase de preparação para os eventos futuros.")

def exibir_cronograma():
    """Renderiza o cronograma completo (Visão Pública)."""
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

def login_sidebar():
    """Função para o login na barra lateral."""
    # [ Código do login inalterado ]
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
    """Retorna uma lista de rótulos de eventos para o selectbox."""
    events = []
    for secao in st.session_state.cronograma:
        for evento in secao['eventos']:
            # Usando o ID para o valor e o rótulo para exibição
            events.append({"id": evento['id'], "label": f"[{secao['secao']}] {evento['data_principal']} | {evento['titulo_evento']}"})
    return events

def admin_adicionar_fato(target_event_id=None):
    """Página unificada para estudos e adição de fatos."""
    
    st.subheader("🤖 Ambiente de Estudo com Gemini")
    st.info("Use este campo para interagir com o Gemini 3 Pro para formatar escrituras fielmente e validar/revisar análises antes de adicionar um Fato.")
    
    # Área para o prompt do Gemini
    prompt = st.text_area("Insira o texto da profecia/análise para o Gemini revisar ou formatar:", key="gemini_prompt", height=150)
    
    # Placeholder para a integração futura do Gemini
    if st.button("Analisar com Gemini (Integração Futura)", disabled=True):
        st.warning("Integração da API Gemini ainda pendente. Use o prompt acima para preparar o texto para o formulário abaixo.")
        # Aqui seria onde o código real da Google AI seria inserido
        # st.code(f"A API Gemini retornaria a análise ou o texto formatado para o prompt: {prompt}")

    st.divider()

    st.subheader("➕ Adicionar Novo Fato a um Evento Existente")
    
    events_options = get_all_events_options()
    
    # Encontra o índice do evento selecionado se um ID foi passado (via botão '+')
    default_index = 0
    if target_event_id:
        try:
            default_index = next(i for i, opt in enumerate(events_options) if opt['id'] == target_event_id)
        except StopIteration:
            pass
            
    # Seleção do Evento Pai
    selected_event_label = st.selectbox(
        "Selecione o Evento Pai onde o Fato será adicionado:",
        options=[opt['label'] for opt in events_options],
        index=default_index,
        key="select_parent_event"
    )

    with st.form("form_novo_fato", clear_on_submit=True):
        st.markdown("**Novo Fato (Profecia/Análise/Histórico)**")
        novo_data_profeta = st.text_input("Profeta/Fonte/Data Específica do Fato", key="input_fato_profeta")
        nova_escritura = st.text_area("📖 Escrituras (ARA) - Fiel às palavras", key="input_fato_escritura")
        nova_analise = st.text_area("🌍 Análise (Como este fato se encaixa na profecia/evento)", key="input_fato_analise")
        
        submit_button = st.form_submit_button("Salvar Novo Fato")
        
        if submit_button:
            if novo_data_profeta and (nova_escritura or nova_analise):
                novo_fato = {
                    "data_profeta": novo_data_profeta,
                    "escritura_ara": nova_escritura,
                    "analise": nova_analise
                }
                
                # Lógica para encontrar o evento selecionado e adicionar o fato
                found = False
                selected_id = next(opt['id'] for opt in events_options if opt['label'] == selected_event_label)
                
                for secao in st.session_state.cronograma:
                    for evento in secao['eventos']:
                        if evento['id'] == selected_id:
                            evento['fatos'].append(novo_fato)
                            found = True
                            break
                    if found: break
                
                if found:
                    st.success(f"Novo Fato adicionado com sucesso ao evento: '{evento['titulo_evento']}'!")
                    st.rerun() # Recarrega para atualizar a interface
                else:
                    st.error("Erro ao encontrar o evento pai.")
            else:
                st.error("Preencha o Profeta/Fonte e ao menos a Escritura ou a Análise.")


def admin_exibir_estrutura():
    """Nova função para gerenciar a estrutura usando expansão por clique (Tree View)."""
    st.subheader("📝 Gerenciar Estrutura de Seções e Eventos")
    st.info("Clique para expandir as seções e eventos. Use o botão `+` para adicionar fatos rapidamente ao evento.")
    st.warning("⚠️ Edições (exclusão/modificação de texto) devem ser feitas na tab 'Gerenciar Estrutura Bruta' por enquanto, ou no `st.data_editor` da tab 'Gerenciar Estrutura Bruta'.")

    # Itera pelas Seções (Expanders de Nível 1)
    for i_secao, secao_data in enumerate(st.session_state.cronograma):
        secao = secao_data['secao']
        
        with st.expander(label=f"📂 **{secao}** ({len(secao_data['eventos'])} Eventos)", expanded=False):
            # Itera pelos Eventos (Expanders de Nível 2)
            for i_evento, evento in enumerate(secao_data['eventos']):
                
                # Expander do Evento
                with st.expander(label=f"🗓️ {evento['data_principal']} | {evento['titulo_evento']} ({len(evento['fatos'])} Fatos)", expanded=False):
                    
                    # Botão para Adicionar Fato Rápido
                    # O truque é mudar o estado da aba selecionada e passar o ID do evento
                    if st.button(f"+ Adicionar Fato a este Evento", key=f"add_fato_{evento['id']}"):
                        st.session_state.admin_tab_selected = 0 # Vai para a aba de estudos/adição
                        st.session_state.target_event_id = evento['id'] # Salva o ID do evento
                        st.rerun()
                        
                    st.markdown("---")
                    st.caption("Fatos Contidos:")
                    
                    # Itera pelos Fatos (Visualização simples)
                    for i_fato, fato in enumerate(evento['fatos']):
                        st.markdown(f"**⚪ Fato {i_fato+1}:** {fato['data_profeta']}")
                        st.markdown(f" > *Escritura:* {fato['escritura_ara'][:50]}...")
                    
                    st.markdown("---")


def admin_page():
    """Página de administração principal."""
    st.title("🔑 Área Administrativa")
    st.markdown("Gerencie o cronograma de eventos proféticos.")
    st.divider()
    
    # Definição das abas com controle de estado
    tabs = ["🤖 Estudo e Adição de Fatos", "📝 Gerenciar Estrutura (Árvore)", "📄 Gerenciar Estrutura Bruta (JSON)"]
    
    selected_tab = st.session_state.admin_tab_selected
    
    # Atualiza a aba selecionada se o usuário clicar
    selected_tab = st.tabs(tabs, selected_tab)[0]
    st.session_state.admin_tab_selected = tabs.index(selected_tab)
    
    # Lógica de renderização
    if selected_tab == tabs[0]:
        # Verifica se houve um redirecionamento do botão '+'
        target_id = st.session_state.get('target_event_id', None)
        admin_adicionar_fato(target_id)
        # Limpa o ID após o uso
        if 'target_event_id' in st.session_state:
            del st.session_state['target_event_id'] 

    elif selected_tab == tabs[1]:
        admin_exibir_estrutura()

    elif selected_tab == tabs[2]:
        st.subheader("📄 Gerenciar Estrutura Bruta (JSON)")
        st.info("Use esta aba apenas para **backup, edição em massa ou exclusão** complexa, copiando o código, editando e colando de volta, ou usando o `st.data_editor`.")
        
        # Converte a estrutura aninhada para JSON formatado
        json_data = st.json(st.session_state.cronograma, expanded=False)
        
        # Opção de edição manual (avançada)
        st.warning("Para editar ou excluir diretamente, recomendamos a Tab 2.")


# --- FLUXO PRINCIPAL DO APLICATIVO ---

login_sidebar()

if st.session_state.logged_in:
    admin_page()
else:
    exibir_cronograma()
