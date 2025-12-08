import streamlit as st
import pandas as pd
import json
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA E CSS CUSTOMIZADO ---

st.set_page_config(
    page_title="Cronograma Profético Bíblico",
    page_icon="📜",
    layout="wide"
)

# Estilos CSS para a Timeline (Linha Pontilhada e Marcadores)
def timeline_css():
    st.markdown("""
        <style>
        /* Estilo para a linha pontilhada vertical - Cor: Verde escuro */
        .timeline-line {
            border-left: 3px dotted #4CAF50; 
            padding-left: 10px; 
            margin-left: 10px; 
            min-height: 40px; /* Altura mínima para o segmento de linha */
        }
        /* Estilo para o ponto 'Hoje' */
        .dot-hoje {
            font-size: 20px;
            color: #FFD700; /* Amarelo para destaque */
            margin-right: 5px;
            display: inline-block;
        }
        /* Estilo para a linha pontilhada do ponto 'Hoje' até o futuro */
        .line-hoje {
            border-left: 3px dotted #FFD700; 
            padding-left: 10px; 
            margin-left: 10px; 
            min-height: 40px; 
        }
        .event-title {
            font-size: 1.25em; /* Tamanho maior para o título do evento */
            font-weight: bold;
        }
        </style>
    """, unsafe_allow_html=True)

timeline_css() # Chama a função para injetar o CSS

# Chave de acesso administrativa
ADMIN_PASSWORD = "R$Masterkey01" 

# --- DADOS INICIAIS DO CRONOGRAMA ---

# Adicionado um conjunto mais representativo de dados
DADOS_INICIAIS = [
    {
        "secao": "I. OS PRIMEIROS TEMPLOS E O EXÍLIO",
        "data_evento": "959 a.C.",
        "titulo": "A Dedicação do Primeiro Templo",
        "data_profeta": "Livros dos Reis e Crônicas (Escrito c. 560–430 a.C.)",
        "escritura_ara": "'Assim se concluiu toda a obra que o rei Salomão fez para a Casa do SENHOR. Então, Salomão trouxe as coisas que Davi, seu pai, havia consagrado, a prata, o ouro e os utensílios, e os depositou nos tesouros da Casa do SENHOR.' (1 Reis 7:51)",
        "analise": "O Templo de Salomão, o Primeiro Templo, demorou sete anos para ser concluído."
    },
    {
        "secao": "I. OS PRIMEIROS TEMPLOS E O EXÍLIO",
        "data_evento": "586 a.C.",
        "titulo": "A Destruição do Primeiro Templo",
        "data_profeta": "Jeremias e Ezequiel (Escrito c. 627–571 a.C.)",
        "escritura_ara": "'Queimaram a Casa de Deus, derribaram os muros de Jerusalém, queimaram a fogo todos os seus palácios e destituíram todos os seus objetos de valor.' (2 Crônicas 36:19)",
        "analise": "A destruição foi executada pelo exército da Babilônia, dando início ao Cativeiro Babilônico."
    },
    {
        "secao": "II. A CONTAGEM MESSIÂNICA",
        "data_evento": "445 a.C.",
        "titulo": "O Início da Contagem das 70 Semanas",
        "data_profeta": "Daniel (Escrito c. 605–536 a.C.)",
        "escritura_ara": "'Sabe e entende: desde a saída da ordem para restaurar e para edificar Jerusalém, até ao Ungido, ao Príncipe, sete semanas e sessenta e duas semanas...' (Daniel 9:25)",
        "analise": "A contagem dos 483 anos proféticos (69 semanas de anos) começou com o decreto de Artaxerxes I, ativando o relógio profético de Daniel."
    },
    {
        "secao": "III. O CUMPRIMENTO DO MESSIAS",
        "data_evento": "32 d.C.",
        "titulo": "A Ressurreição e a Incorrupção",
        "data_profeta": "Davi (Salmos) (Escrito c. 1011–971 a.C.)",
        "escritura_ara": "'Pois não deixarás a minha alma na morte, nem permitirás que o teu Santo veja corrupção.' (Salmo 16:10)",
        "analise": "A Ressurreição é o fato histórico central que prova que Jesus é o Messias e que Seu corpo não sofreu corrupção na sepultura."
    },
    {
        "secao": "V. A RECONSTRUÇÃO DO RELÓGIO PROFÉTICO",
        "data_evento": "1948",
        "titulo": "Renascimento da Nação de Israel (Estado)",
        "data_profeta": "Isaías (Escrito c. 740–700 a.C.)",
        "escritura_ara": "'Acaso, pode uma terra nascer num só dia? Acaso, nasce uma nação de uma só vez? Mas, apenas Sião esteve de parto, já deu à luz seus filhos.' (Isaías 66:8)",
        "analise": "A Proclamação do Estado de Israel em 14 de maio de 1948 cumpriu a profecia de um nascimento nacional repentino."
    },
]

# Inicializa o Session State
if 'cronograma' not in st.session_state:
    st.session_state.cronograma = DADOS_INICIAIS
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    
# --- FUNÇÕES DE EXIBIÇÃO ---

def exibir_evento(evento, show_line=True):
    """Renderiza um único evento no formato de timeline com linha pontilhada."""
    
    # 1. Colunas para alinhar visualmente o dot e o conteúdo
    col_dot, col_content = st.columns([0.05, 0.95])
    
    with col_dot:
        # Ponto do evento (usando emoji para o ponto visual)
        st.markdown('<div class="timeline-dot">🟢</div>', unsafe_allow_html=True)
        # Linha pontilhada (somente se não for o último evento/separador)
        if show_line:
            st.markdown('<div class="timeline-line"></div>', unsafe_allow_html=True)
            
    with col_content:
        # Título do evento
        st.markdown(f'<p class="event-title">🗓️ {evento["data_evento"]} {evento["titulo"]}</p>', unsafe_allow_html=True)
        
        # Conteúdo detalhado dentro de um container
        with st.container(border=True):
            st.markdown(f"**📅 Profeta e Data:** {evento['data_profeta']}")
            
            # Expander para as Escrituras e Análise
            with st.expander("📖 **Escrituras (ARA)**"):
                # Garante fidelidade ao texto original, conforme seu pedido
                st.markdown(f"*{evento['escritura_ara']}*")
            
            with st.expander("🌍 **Análise Histórica/Hipotética**"):
                st.markdown(evento['analise'])

def exibir_marcador_hoje():
    """Insere o marcador 'HOJE' na timeline."""
    col_dot, col_content = st.columns([0.05, 0.95])
    
    with col_dot:
        st.markdown('<div class="dot-hoje">⭐</div>', unsafe_allow_html=True)
        st.markdown('<div class="line-hoje"></div>', unsafe_allow_html=True) # Linha futura
            
    with col_content:
        st.markdown(f'<p class="event-title">📍 **HOJE ({datetime.now().year})**</p>', unsafe_allow_html=True)
        st.markdown("---") # Linha horizontal
        st.info("A partir deste ponto, o relógio profético está em fase de preparação para os eventos futuros.")


def exibir_cronograma():
    """Renderiza o cronograma completo com a opção de Expandir/Reduzir."""
    st.title("📜 Cronograma Profético Bíblico")
    st.markdown("Uma timeline de eventos históricos e futuros com base nas Escrituras, fiel à formatação solicitada.")
    st.divider()

    # Opção Global de Expandir/Reduzir
    with st.expander("Clique para **Expandir/Reduzir** o Cronograma Completo", expanded=True):
        
        df = pd.DataFrame(st.session_state.cronograma)
        
        # Variáveis para controle da inserção do marcador HOJE
        hoje_inserido = False
        
        # Agrupa por Seção (I, II, III, etc.) e ordena
        for secao, grupo in df.groupby('secao', sort=False):
            st.header(secao)
            st.markdown("---")
            
            is_future_section = secao.startswith('VI.') or secao.startswith('VII.') or secao.startswith('VIII.')

            # Insere o marcador HOJE antes da primeira seção de eventos futuros
            if is_future_section and not hoje_inserido:
                exibir_marcador_hoje()
                hoje_inserido = True
                st.header(secao) # Repete o cabeçalho para a seção futura
                st.markdown("---")
            
            # Itera sobre os eventos dentro da seção
            for index, evento in grupo.iterrows():
                # Define se deve mostrar a linha pontilhada após o evento
                show_line = True
                if index == grupo.index[-1] and not is_future_section:
                    # Não mostra a linha pontilhada após o último evento de uma seção histórica/presente
                    show_line = False
                
                exibir_evento(evento, show_line)
                
                if not is_future_section:
                    st.markdown("<br>", unsafe_allow_html=True) # Espaço extra entre eventos passados

        # Caso não haja seções futuras no conjunto de dados, insere HOJE no final
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
    """Página de administração para CRUD e estudos."""
    st.title("🔑 Área Administrativa")
    st.markdown("Gerencie o cronograma e utilize o ambiente de estudos.")
    st.divider()
    
    tab1, tab2, tab3 = st.tabs(["➕ Adicionar Evento", "📝 Gerenciar Eventos", "🤖 Estudo com Gemini"])

    with tab1:
        st.subheader("Adicionar Novo Evento")
        with st.form("form_novo_evento", clear_on_submit=True):
            st.markdown("**Dados do Evento**")
            nova_secao = st.text_input("Seção (Ex: VII. A 70ª SEMANA...)", key="input_secao")
            col_data, col_titulo = st.columns(2)
            nova_data = col_data.text_input("Data do Evento (Ex: 2024, 32 d.C.)", key="input_data")
            novo_titulo = col_titulo.text_input("Título do Evento", key="input_titulo")
            nova_data_profeta = st.text_input("Profeta e Data (Ex: João, c. 95 d.C.)", key="input_profeta")
            
            st.markdown("**Conteúdo Principal**")
            nova_escritura = st.text_area("📖 Escrituras (ARA) - Fiel às palavras (MANTENHA A FORMATAÇÃO: '...texto...' (Referência))", key="input_escritura")
            nova_analise = st.text_area("🌍 Análise Histórica/Hipotética", key="input_analise")
            
            submit_button = st.form_submit_button("Salvar Novo Evento")
            
            if submit_button:
                if nova_secao and nova_data and novo_titulo:
                    novo_evento = {
                        "secao": nova_secao,
                        "data_evento": nova_data,
                        "titulo": novo_titulo,
                        "data_profeta": nova_data_profeta,
                        "escritura_ara": nova_escritura,
                        "analise": nova_analise
                    }
                    st.session_state.cronograma.append(novo_evento)
                    st.success(f"Evento '{novo_titulo}' adicionado com sucesso! Recarregue a página pública para visualizar.")
                else:
                    st.error("Preencha ao menos Seção, Data e Título.")
                    
    with tab2:
        st.subheader("Visualizar, Editar e Excluir Eventos")
        st.info("⚠️ **Importante:** A edição aqui só é salva durante sua sessão. Para persistir as mudanças no servidor, você precisará configurar um backend (ex: banco de dados).")
        
        df_editavel = pd.DataFrame(st.session_state.cronograma)
        
        st.markdown("**Altere os dados diretamente na tabela (Use o ícone 🗑️ para excluir linhas)**")
        
        # O st.data_editor permite editar e excluir linhas dinamicamente
        edited_df = st.data_editor(
            df_editavel, 
            use_container_width=True, 
            num_rows="dynamic",
            hide_index=True
        )
        
        # Atualiza a lista de eventos (session state)
        st.session_state.cronograma = edited_df.to_dict('records')
        st.success("Tabela de eventos atualizada na sua sessão.")

    with tab3:
        st.subheader("Ambiente de Estudo com I.A. (Gemini)")
        st.info("Use este espaço para interagir com o Gemini 3 Pro (ou 2.5 Pro) para formatar e analisar novos eventos antes de adicioná-los. Você precisará instalar a biblioteca `google-genai` e usar seu token.")
        
        # Exemplo de placeholder para integração da IA
        st.markdown("Integração futura da Google AI aqui para análise de texto profético.")

# --- FLUXO PRINCIPAL DO APLICATIVO ---

login_sidebar()

if st.session_state.logged_in:
    admin_page()
else:
    exibir_cronograma()
