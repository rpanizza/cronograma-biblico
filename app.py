import streamlit as st
import pandas as pd
import json # Usado para simular o armazenamento/leitura de dados

# Configuração da página
st.set_page_config(
    page_title="Cronograma Profético Bíblico",
    page_icon="📜",
    layout="wide"
)

# --- 1. DADOS INICIAIS (MVP: Dados fixos, que você pode expandir) ---
# Em uma versão futura, estes dados devem ser carregados de um arquivo JSON/CSV ou banco de dados.
# Os dados iniciais são carregados no Session State para permitir a edição/adição
DADOS_INICIAIS = [
    {
        "secao": "I. OS PRIMEIROS TEMPLOS E O EXÍLIO",
        "data_evento": "959 a.C.",
        "titulo": "A Dedicação do Primeiro Templo",
        "data_profeta": "Livros dos Reis e Crônicas (Escrito c. 560–430 a.C.)",
        "escritura_ara": "Assim se concluiu toda a obra que o rei Salomão fez para a Casa do SENHOR. Então, Salomão trouxe as coisas que Davi, seu pai, havia consagrado, a prata, o ouro e os utensílios, e os depositou nos tesouros da Casa do SENHOR.' (1 Reis 7:51)",
        "analise": "O Templo de Salomão, o Primeiro Templo, demorou sete anos para ser concluído. Sua dedicação foi um evento de proporções épicas, onde o próprio Salomão orou, e a Glória (Shekinah) de Deus desceu em forma de nuvem para encher o Templo, impossibilitando os sacerdotes de ali permanecerem para ministrar. Isso marcou o auge do reino unificado de Israel sob o favor divino."
    },
    {
        "secao": "I. OS PRIMEIROS TEMPLOS E O EXÍLIO",
        "data_evento": "586 a.C.",
        "titulo": "A Destruição do Primeiro Templo",
        "data_profeta": "Jeremias e Ezequiel (Escrito c. 627–571 a.C.)",
        "escritura_ara": "Queimaram a Casa de Deus, derribaram os muros de Jerusalém, queimaram a fogo todos os seus palácios e destituíram todos os seus objetos de valor.' (2 Crônicas 36:19)",
        "analise": "A destruição foi executada pelo exército da Babilônia, liderado por Nabucodonosor II, devido à persistente idolatria e desobediência do povo de Judá e seus reis, conforme profetizado. O Templo, símbolo da presença de Deus, foi totalmente saqueado e reduzido a cinzas, dando início ao doloroso Cativeiro Babilônico, que durou sete décadas."
    },
    {
        "secao": "V. A RECONSTRUÇÃO DO RELÓGIO PROFÉTICO",
        "data_evento": "1948",
        "titulo": "Renascimento da Nação de Israel (Estado)",
        "data_profeta": "Isaías (Escrito c. 740–700 a.C.)",
        "escritura_ara": "Quem jamais ouviu tal coisa? Quem viu coisa semelhante? Acaso, pode uma terra nascer num só dia? Acaso, nasce uma nação de uma só vez? Mas, apenas Sião esteve de parto, já deu à luz seus filhos.' (Isaías 66:8)",
        "analise": "A Proclamação do Estado de Israel em 14 de maio de 1948, em um único dia, cumpriu esta profecia de um nascimento nacional repentino e milagroso. Este evento encerrou a longa diáspora e é o sinal profético mais significativo de que a atenção de Deus voltou para Israel, preparando o cenário para o reinício do relógio profético."
    },
]

# Inicializa o Session State para armazenar os dados do cronograma
if 'cronograma' not in st.session_state:
    st.session_state.cronograma = DADOS_INICIAIS
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    
# Chave de acesso administrativa (Apenas para MVP! Use st.secrets para produção)
ADMIN_PASSWORD = "SuaSenhaSegura123" 

# --- 2. FUNÇÕES DE EXIBIÇÃO ---

def exibir_evento(evento):
    """Renderiza um único evento no formato de timeline."""
    
    # Cabeçalho do evento com a data em destaque
    st.subheader(f"🗓️ {evento['data_evento']} {evento['titulo']}")
    
    with st.container(border=True):
        st.markdown(f"**📅 Profeta e Data:** {evento['data_profeta']}")
        
        # Uso do st.expander para a Escritura e Análise, mantendo o layout limpo
        with st.expander("📖 **Escrituras (ARA)**"):
            # O texto da Escritura é fiel às palavras, sem abreviações
            st.markdown(f"*{evento['escritura_ara']}*")
        
        with st.expander("🌍 **Análise Histórica/Hipotética**"):
            st.markdown(evento['analise'])

def exibir_cronograma():
    """Renderiza o cronograma completo, agrupado por seções."""
    st.title("📜 Cronograma Profético Bíblico")
    st.markdown("Uma timeline de eventos históricos e futuros com base nas Escrituras.")
    st.divider()

    # Cria um DataFrame para facilitar o agrupamento
    df = pd.DataFrame(st.session_state.cronograma)
    
    # Agrupa por Seção (I, II, III, etc.) e ordena por data (opcionalmente)
    for secao, grupo in df.groupby('secao', sort=False):
        st.header(secao)
        st.markdown("---")
        
        # Itera sobre os eventos dentro da seção
        for index, evento in grupo.iterrows():
            exibir_evento(evento)
            st.markdown("---") # Linha separadora entre eventos

# --- 3. ÁREA ADMINISTRATIVA ---

def login_sidebar():
    """Função para o login na barra lateral."""
    if st.session_state.logged_in:
        st.sidebar.success("Logado como Administrador!")
        if st.sidebar.button("Logout"):
            st.session_state.logged_in = False
            st.rerun()
    else:
        st.sidebar.header("Área Administrativa")
        password = st.sidebar.text_input("Senha", type="password")
        if st.sidebar.button("Entrar"):
            if password == ADMIN_PASSWORD:
                st.session_state.logged_in = True
                st.sidebar.success("Login bem-sucedido!")
                st.rerun() # Recarrega a página para exibir o menu Admin
            else:
                st.sidebar.error("Senha incorreta.")

def admin_page():
    """Página de administração para CRUD e estudos."""
    st.title("🔑 Área Administrativa")
    st.markdown("Aqui você pode gerenciar o cronograma e realizar seus estudos.")
    st.divider()
    
    # Abas para organizar Adicionar/Editar/Estudo
    tab1, tab2, tab3 = st.tabs(["➕ Adicionar Evento", "📝 Ver/Editar/Excluir", "🤖 Estudo com Gemini"])

    with tab1:
        st.subheader("Adicionar Novo Evento")
        with st.form("form_novo_evento", clear_on_submit=True):
            nova_secao = st.text_input("Seção (Ex: VII. A 70ª SEMANA...)", key="input_secao")
            nova_data = st.text_input("Data do Evento (Ex: 2024, 32 d.C.)", key="input_data")
            novo_titulo = st.text_input("Título do Evento", key="input_titulo")
            nova_data_profeta = st.text_input("Profeta e Data (Ex: João, c. 95 d.C.)", key="input_profeta")
            nova_escritura = st.text_area("Escrituras (ARA) - Fiel às palavras", key="input_escritura")
            nova_analise = st.text_area("Análise Histórica/Hipotética", key="input_analise")
            
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
                    # Adiciona o novo evento ao Session State
                    st.session_state.cronograma.append(novo_evento)
                    st.success(f"Evento '{novo_titulo}' adicionado com sucesso!")
                else:
                    st.error("Preencha ao menos Seção, Data e Título.")
                    
    with tab2:
        st.subheader("Visualizar e Gerenciar Eventos")
        # Exibição dos dados em uma tabela editável
        df_editavel = pd.DataFrame(st.session_state.cronograma)
        
        st.markdown("**Altere os dados diretamente na tabela abaixo para editar.**")
        st.caption("A edição só será salva na sessão do Streamlit. Para persistir, é necessário um botão 'Salvar' e um backend.")
        
        edited_df = st.data_editor(df_editavel, use_container_width=True, num_rows="dynamic")
        
        # Atualiza a lista de eventos com base na tabela editada
        st.session_state.cronograma = edited_df.to_dict('records')
        
        st.success("Tabela atualizada (na sessão atual).")

    with tab3:
        st.subheader("Ambiente de Estudo com I.A. (Gemini)")
        st.info("Aqui é onde você integraria o seu token Gemini (usando a API, ex: `google-genai`) para análise e sugestão de novos eventos, conforme seu estudo.")
        # O placeholder para a integração da IA.
        st.markdown("""
        ```python
        # Exemplo de uso futuro:
        # from google import genai
        # client = genai.Client(api_key=SEU_TOKEN)
        # 
        # prompt = st.text_area("Insira sua análise ou pergunte ao Gemini:")
        # if st.button("Analisar com Gemini"):
        #     response = client.models.generate_content(
        #         model='gemini-2.5-pro', # Ou o modelo 3 pro que você está usando
        #         contents=[f"Revise e formate este evento bíblico-profético como uma entrada de cronograma:\n\n{prompt}"]
        #     )
        #     st.write(response.text)
        ```
        """)


# --- 4. FLUXO PRINCIPAL DO APLICATIVO ---

# O login_sidebar() precisa ser chamado antes do fluxo principal.
login_sidebar()

if st.session_state.logged_in:
    admin_page()
else:
    exibir_cronograma()
