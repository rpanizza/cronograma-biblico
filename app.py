import streamlit as st
import pandas as pd
from datetime import datetime

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
        </style>
    """, unsafe_allow_html=True)

timeline_css() 

# Chave de acesso administrativa
ADMIN_PASSWORD = "R$Masterkey01" 

# --- NOVO MODELO DE DADOS: LISTA DE SEÇÕES, CADA UMA COM LISTA DE EVENTOS E CADA EVENTO COM LISTA DE FATOS ---

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
    
# --- FUNÇÕES DE EXIBIÇÃO ---

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
        # Expander de Detalhes no final da linha do evento
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
    """Renderiza o cronograma completo, sem expander global."""
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


# --- ÁREA ADMINISTRATIVA ---

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

def admin_page():
    """Página de administração com a nova estrutura de dados."""
    st.title("🔑 Área Administrativa")
    st.markdown("Gerencie o cronograma (Seções, Eventos e Fatos) e utilize o ambiente de estudos.")
    st.divider()
    
    tab1, tab2, tab3 = st.tabs(["➕ Adicionar Fato/Evento", "📝 Gerenciar Estrutura", "🤖 Estudo com Gemini"])

    # Função utilitária para obter todos os eventos disponíveis (para o selectbox)
    def get_all_events():
        events = []
        for secao in st.session_state.cronograma:
            for evento in secao['eventos']:
                events.append(f"[{secao['secao']}] {evento['data_principal']} | {evento['titulo_evento']}")
        return events

    with tab1:
        st.subheader("Adicionar Novo Fato a um Evento Existente")
        st.info("Use esta opção para documentar uma nova profecia, uma análise atualizada ou um fato histórico relevante que se relaciona a um evento principal já cadastrado (Ex: Nova informação sobre a Destruição de Damasco).")

        # Seleciona o Evento Pai
        selected_event_label = st.selectbox(
            "Selecione o Evento Pai onde o Fato será adicionado:",
            options=get_all_events(),
            key="select_parent_event"
        )

        with st.form("form_novo_fato", clear_on_submit=True):
            st.markdown("**Novo Fato (Profecia/Análise/Histórico)**")
            novo_data_profeta = st.text_input("Profeta/Fonte/Data Específica do Fato (Ex: Líder Sírio Morto em 2024)", key="input_fato_profeta")
            nova_escritura = st.text_area("📖 Escrituras (ARA) - Fiel às palavras", key="input_fato_escritura")
            nova_analise = st.text_area("🌍 Análise (Como este fato se encaixa na profecia/evento)", key="input_fato_analise")
            
            submit_button = st.form_submit_button("Salvar Novo Fato")
            
            if submit_button and selected_event_label:
                if novo_data_profeta and (nova_escritura or nova_analise):
                    novo_fato = {
                        "data_profeta": novo_data_profeta,
                        "escritura_ara": nova_escritura,
                        "analise": nova_analise
                    }
                    
                    # Lógica para encontrar o evento selecionado e adicionar o fato
                    found = False
                    for secao in st.session_state.cronograma:
                        for evento in secao['eventos']:
                            current_label = f"[{secao['secao']}] {evento['data_principal']} | {evento['titulo_evento']}"
                            if current_label == selected_event_label:
                                evento['fatos'].append(novo_fato)
                                found = True
                                break
                        if found: break
                    
                    if found:
                        st.success(f"Novo Fato adicionado com sucesso ao evento: '{evento['titulo_evento']}'!")
                    else:
                        st.error("Erro ao encontrar o evento pai.")
                else:
                    st.error("Preencha o Profeta/Fonte e ao menos a Escritura ou a Análise.")
            elif submit_button:
                 st.error("Selecione um Evento Pai.")

    with tab2:
        st.subheader("Gerenciar a Estrutura (Seções e Eventos Principais)")
        st.info("Aqui você visualiza a estrutura de dados complexa. Para edição completa, o método mais fácil é converter para JSON, editar e carregar novamente, ou usar um banco de dados persistente.")
        
        # Exibe a estrutura completa como JSON (apenas para visualização de Admin)
        st.json(st.session_state.cronograma)
        
    with tab3:
        st.subheader("Ambiente de Estudo com I.A. (Gemini)")
        st.info("Use este espaço para interagir com o Gemini 3 Pro para revisar análises, formatar escrituras fielmente e gerar novos fatos, antes de adicioná-los usando a aba 'Adicionar Fato/Evento'.")
        # Placeholder para integração da Google AI
        st.markdown("Integração da API Gemini.")


# --- FLUXO PRINCIPAL DO APLICATIVO ---

login_sidebar()

if st.session_state.logged_in:
    admin_page()
else:
    exibir_cronograma()
