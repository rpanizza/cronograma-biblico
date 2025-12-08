import streamlit as st
import google.generativeai as genai
import json
import os
import re

# --- CONFIGURAÇÃO INICIAL E VERSÕES ---
st.set_page_config(
    page_title="Cronograma Dinâmico", 
    layout="centered", 
    initial_sidebar_state="auto"
)

# Versão do Aplicativo (App) - Muda apenas quando o CÓDIGO muda
VERSAO_APP = "1.1.0" 
# Versão do Conteúdo (Cronologia) - Muda conforme a regra AA.MMDD.V
VERSAO_CONTEUDO = "25.1208.4" 

# Nome do arquivo onde os dados serão salvos
ARQUIVO_DADOS = 'cronograma.json'
API_KEY = st.secrets.get("GEMINI_API_KEY", "")
SENHA_CORRETA = "R$Masterkey01" # Senha de Admin

# --- FUNÇÕES DE ORDENAÇÃO E DADOS ---

def get_sort_key(date_str):
    """Converte a data (ex: '539 a.C.') em um número para ordenação."""
    date_str_clean = date_str.lower().replace('.', '').strip()
    match = re.match(r'(\d+)\s*(a\.c\.|ac|d\.c\.|dc)?', date_str_clean)
    
    if not match: return 0
    
    try:
        year = int(match.group(1))
    except ValueError: return 0 
        
    suffix = match.group(2)
    
    if suffix and ('a.c.' in suffix or 'ac' in suffix):
        return -year
    else:
        return year

def carregar_dados():
    dados_padrao = {
        "titulo": "📜 Cronograma Profético Dinâmico",
        "eventos": []
    }
    if not os.path.exists(ARQUIVO_DADOS):
        return dados_padrao
    with open(ARQUIVO_DADOS, 'r', encoding='utf-8') as f:
        try:
            conteudo = json.load(f)
            if isinstance(conteudo, list):
                return {"titulo": "📜 Cronograma Profético Dinâmico", "eventos": conteudo}
            return conteudo
        except json.JSONDecodeError:
            return dados_padrao

def salvar_dados(dados):
    with open(ARQUIVO_DADOS, 'w', encoding='utf-8') as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)

# --- INTEGRAÇÃO COM GEMINI: CRONOLOGIA (STRICT) ---
def consultar_gemini_cronologia(topico):
    if not API_KEY: return "⚠️ Erro: Chave API não configurada.", ""
    
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = f"""
    Atue como assistente estrito de cronologia bíblica para preenchimento de banco de dados.
    Tópico: "{topico}"
    Sua tarefa é gerar duas partes de texto: 1. Fato histórico. 2. Referência e texto da escritura integralmente.
    REGRAS CRÍTICAS: Seja fiel *exclusivamente* às escrituras. NÃO use abreviações. NÃO adicione ponto de vista.
    FORMATO OBRIGATÓRIO: [Fato Histórico] ||| [Referência e Texto Bíblico]
    """
    try:
        response = model.generate_content(prompt)
        texto = response.text
        if "|||" in texto:
            partes = texto.split("|||")
            return partes[0].strip(), partes[1].strip()
        else:
            return texto, "Não foi possível separar. Verifique o texto."
    except Exception as e:
        return f"Erro de conexão: {str(e)}", ""

# --- INTEGRAÇÃO COM GEMINI: PESQUISA (FLEXÍVEL) ---
def consultar_gemini_research(topico, model_name):
    if not API_KEY: return "⚠️ Erro: Chave API não configurada.", ""
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel(model_name)
    
    prompt = f"""
    Pesquise e explique o tópico abaixo de forma detalhada e didática, focando em fornecer contexto histórico e referências bíblicas relevantes. 
    Tópico: "{topico}"
    Sua resposta deve ser estruturada em duas seções principais:
    1. HISTÓRICO/CONTEXTO (Detalhes e fatos).
    2. ESCRITURAS RELACIONADAS (Citações relevantes).
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Erro ao executar pesquisa com {model_name}: {str(e)}"


# --- INICIALIZAÇÃO DE ESTADO ---
if 'edit_index' not in st.session_state: st.session_state['edit_index'] = None
if 'research_topic' not in st.session_state: st.session_state['research_topic'] = ""
if 'research_output' not in st.session_state: st.session_state['research_output'] = ""
    
# --- CSS PERSONALIZADO ---
st.markdown("""
<style>
    @media (max-width: 600px) {
        h1 { font-size: 1.8rem !important; }
    }
    p { text-align: justify; }
</style>
""", unsafe_allow_html=True)

# --- CARREGA DADOS E ADMIN CHECK ---
dados_app = carregar_dados()
lista_eventos = dados_app["eventos"]
titulo_atual = dados_app.get("titulo", "Cronograma Profético")
admin_mode = (st.sidebar.text_input("Senha de Acesso", type="password") == SENHA_CORRETA)

# --- INTERFACE PRINCIPAL ---

st.title(titulo_atual)

# LAYOUT DA VERSÃO (Uma abaixo da outra)
st.markdown(f"**Versão do App:** `{VERSAO_APP}`")
st.markdown(f"**Versão do Conteúdo:** `{VERSAO_CONTEUDO}`")

st.caption("Toque nos itens abaixo para expandir e ler.")

# --- BARRA LATERAL (ADMIN E BACKUP) ---
with st.sidebar:
    st.header("⚙️ Ferramentas")
    if admin_mode:
        st.success("✅ Modo Edição Ativo")
        st.divider()
        st.subheader("Personalizar")
        novo_titulo = st.text_input("Título do Projeto", value=titulo_atual)
        if novo_titulo != titulo_atual:
            dados_app["titulo"] = novo_titulo
            salvar_dados(dados_app)
            st.rerun()

        st.divider()
        st.subheader("Salvamento e Backup")
        # BOTÃO DE BACKUP EXTERNO
        json_data = json.dumps(dados_app, indent=4, ensure_ascii=False)
        st.download_button(
            label="⬇️ Backup Externo (.json)",
            data=json_data,
            file_name='backup_cronograma.json',
            mime='application/json'
        )
        
        # Botão para cancelar edição se estiver no modo edição
        if st.session_state.edit_index is not None:
             if st.button("❌ Cancelar Edição"):
                st.session_state.edit_index = None
                st.rerun()
            
    st.divider()
    st.caption(f"App v{VERSAO_APP} | Conteúdo v{VERSAO_CONTEUDO}")
    

# --- FORMULÁRIO DE ADIÇÃO/EDIÇÃO (UNIFICADO) ---
if admin_mode:
    
    # Se estiver no modo edição, preenche os dados
    item_editado = None
    if st.session_state.edit_index is not None:
        item_editado = lista_eventos[st.session_state.edit_index]
    
    form_titulo = f"✏️ Editando: {item_editado['evento']}" if item_editado else "➕ Adicionar Novo Evento"
    data_padrao = item_editado['data'] if item_editado else ""
    evento_padrao = item_editado['evento'] if item_editado else ""
    hist_padrao = item_editado['historico'] if item_editado else ""
    bib_padrao = item_editado['escritura'] if item_editado else ""
    submit_label = f"✅ Atualizar Evento {data_padrao}" if item_editado else "💾 Salvar Novo Evento"

    with st.expander(form_titulo, expanded=(item_editado is not None or st.session_state.get('show_add_form', False))):
        st.write("Use a IA para buscar textos ou preencha manualmente.")
        
        col_input1, col_input2 = st.columns([1, 2])
        with col_input1:
            data_temp = st.text_input("Data (ex: 539 a.C.)", key="in_data", value=data_padrao)
        with col_input2:
            evento_temp = st.text_input("Nome do Evento", key="in_evento", value=evento_padrao)
            
        if st.button("✨ Pesquisar Cronologia (Fiel) com IA"):
            if evento_temp:
                with st.spinner("Consultando escrituras..."):
                    hist_ia, bib_ia = consultar_gemini_cronologia(evento_temp)
                    st.session_state['temp_hist'] = hist_ia
                    st.session_state['temp_bib'] = bib_ia
            else:
                st.warning("Digite o nome do evento primeiro.")
        
        # Se a IA preencheu, usa os valores temporários do state
        val_hist = st.session_state.get('temp_hist', hist_padrao)
        val_bib = st.session_state.get('temp_bib', bib_padrao)
        
        with st.form("form_salvar"):
            txt_historico = st.text_area("Fato Histórico", value=val_hist, height=100)
            txt_biblico = st.text_area("Texto das Escrituras (Fiel)", value=val_bib, height=150)
            
            if st.form_submit_button(submit_label):
                novo_item = {
                    "data": data_temp,
                    "evento": evento_temp,
                    "historico": txt_historico,
                    "escritura": txt_biblico
                }
                
                if item_editado is not None:
                    lista_eventos[st.session_state.edit_index] = novo_item
                    st.session_state.edit_index = None
                    st.success("Evento atualizado com sucesso!")
                else:
                    lista_eventos.append(novo_item)
                    st.success("Evento salvo com sucesso!")
                    
                dados_app["eventos"] = lista_eventos
                salvar_dados(dados_app)
                st.session_state['temp_hist'] = ""
                st.session_state['temp_bib'] = ""
                st.rerun()

    st.divider()
    
    # --- FERRAMENTA DE PESQUISA GEMINI ---
    with st.expander("🔬 Ferramenta de Estudo e Pesquisa (Gemini)", expanded=False):
        
        # Ação para limpar pesquisa
        def clear_research():
            st.session_state.research_topic = ""
            st.session_state.research_output = ""
            st.session_state.edit_index = None
            st.rerun()

        st.subheader("Pesquisa Rápida e Raciocínio Profundo")
        
        col_model, col_topic = st.columns([1, 2])
        with col_model:
            model_selected = st.selectbox(
                "Escolha o Modelo",
                options=['gemini-1.5-flash (Rápido/Padrão)', 'gemini-1.5-pro (Raciocínio 3 Pro)'],
                key='model_selection'
            )
            model_key = 'gemini-1.5-flash' if 'flash' in model_selected else 'gemini-1.5-pro'
        
        with col_topic:
            st.session_state.research_topic = st.text_input("Tópico de Pesquisa/Estudo", key='topic_input', value=st.session_state.research_topic)

        col_run, col_clear = st.columns([1, 1])
        if col_run.button("▶️ Executar Pesquisa"):
            if st.session_state.research_topic:
                with st.spinner(f"Consultando {model_selected}..."):
                    st.session_state.research_output = consultar_gemini_research(st.session_state.research_topic, model_key)
            else:
                st.warning("Digite um tópico para pesquisar.")

        if col_clear.button("🗑️ Limpar Pesquisa / Novo Assunto"):
            clear_research()
            
        st.markdown("---")
        
        if st.session_state.research_output:
            st.subheader("Resultado da Pesquisa")
            st.markdown(st.session_state.research_output)
            
            # BOTÃO PARA SALVAR NO CRONOGRAMA
            if st.button("📝 Salvar Resultado no Cronograma"):
                # Simula a separação Histórico/Escritura para o formulário de adição
                # Seções: 1. HISTÓRICO/CONTEXTO. 2. ESCRITURAS RELACIONADAS.
                
                output = st.session_state.research_output
                hist_match = re.search(r'1\. HISTÓRICO/CONTEXTO(.*?)2\. ESCRITURAS RELACIONADAS', output, re.DOTALL)
                bib_match = re.search(r'2\. ESCRITURAS RELACIONADAS(.*)', output, re.DOTALL)
                
                hist_temp = hist_match.group(1).strip() if hist_match else output
                bib_temp = bib_match.group(1).strip() if bib_match else "Texto bíblico não separado, por favor, revise manualmente."
                
                # Preenche o formulário principal
                st.session_state['temp_hist'] = hist_temp
                st.session_state['temp_bib'] = bib_temp
                st.session_state['show_add_form'] = True # Força a expansão do formulário
                
                st.success("Resultado transferido para o formulário 'Adicionar Novo Evento'. Preencha a Data e o Evento e salve.")
                st.rerun()

# --- ÁREA DE VISUALIZAÇÃO (LINHA DO TEMPO) ---
st.divider()

if not lista_eventos:
    st.info("O cronograma está vazio. Faça login para começar.")
else:
    # Ordenação dos eventos usando a função personalizada
    eventos_ordenados = sorted(lista_eventos, key=lambda x: get_sort_key(x['data']), reverse=True)

    for i, item in enumerate(eventos_ordenados):
        titulo_card = f"🗓️ **{item['data']}** — {item['evento']}"
        
        with st.expander(titulo_card):
            # Parte Histórica
            st.markdown(f"""
            **Contexto Histórico:**
            {item['historico']}
            """)
            
            st.markdown("---")
            
            # Parte Bíblica (Itálico)
            st.markdown("**📖 Escrituras (Texto Fiel):**")
            st.info(f"_{item['escritura']}_")
            
            if admin_mode:
                col_edit, col_delete = st.columns([1, 1])
                
                # BOTÃO DE EDIÇÃO
                if col_edit.button("✏️ Editar", key=f"edit_{i}"):
                    original_index = lista_eventos.index(item)
                    st.session_state.edit_index = original_index
                    st.session_state['show_add_form'] = True
                    st.rerun()

                # CONFIRMAÇÃO DE EXCLUSÃO
                with col_delete:
                    if st.checkbox("Confirmar Exclusão", key=f"check_del_{i}"):
                        if st.button("🗑️ Excluir permanentemente", key=f"del_{i}"):
                            lista_eventos.remove(item)
                            dados_app["eventos"] = lista_eventos
                            salvar_dados(dados_app)
                            st.session_state.edit_index = None 
                            st.rerun()

# Rodapé
st.markdown("---")
st.caption("Fim do Cronograma.")
