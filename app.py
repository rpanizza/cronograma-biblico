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
VERSAO_APP = "1.0.0" 
# Versão do Conteúdo (Cronologia) - Muda conforme a regra AA.MMDD.V
VERSAO_CONTEUDO = "25.1208.3" 

# Nome do arquivo onde os dados serão salvos
ARQUIVO_DADOS = 'cronograma.json'
API_KEY = st.secrets.get("GEMINI_API_KEY", "")
SENHA_CORRETA = "R$Masterkey01" # Senha de Admin

# --- FUNÇÕES DE DADOS E ORDENAÇÃO (CRÍTICO PARA CRONOLOGIA) ---

def get_sort_key(date_str):
    """Converte a data (ex: '539 a.C.') em um número para ordenação."""
    
    date_str_clean = date_str.lower().replace('.', '').strip()
    match = re.match(r'(\d+)\s*(a\.c\.|ac|d\.c\.|dc)?', date_str_clean)
    
    if not match:
        return 0 # Não pode ordenar
    
    try:
        year = int(match.group(1))
    except ValueError:
        return 0 
        
    suffix = match.group(2)
    
    if suffix and ('a.c.' in suffix or 'ac' in suffix):
        # a.C. (BC) deve ser negativo e ordenado do menor para o maior (ex: -1000 vem antes de -500)
        return -year
    else:
        # d.C. (AD) ou sem sufixo (assume-se d.C.) é positivo
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

# --- INTEGRAÇÃO COM GEMINI (IA) ---
def consultar_gemini(topico):
    if not API_KEY:
        return "⚠️ Erro: Chave API não configurada.", "Configure a chave no Streamlit Secrets."
    
    try:
        genai.configure(api_key=API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = f"""
        Você é um assistente estrito de cronologia bíblica.
        Tópico solicitado: "{topico}"
        
        Sua tarefa é gerar duas partes de texto:
        1. Um breve fato histórico sobre o evento.
        2. A referência bíblica e o texto da escritura integralmente.

        REGRAS CRÍTICAS (NÃO QUEBRE):
        - Seja fiel às palavras referenciadas exclusivamente nas escrituras.
        - NÃO use abreviações.
        - NÃO adicione ponto de vista pessoal, teológico ou interpretações.
        - Apenas cite.
        
        FORMATO DE RESPOSTA (Use '|||' para separar as duas partes):
        [Fato Histórico aqui] ||| [Referência e Texto Bíblico aqui]
        """
        
        response = model.generate_content(prompt)
        texto = response.text
        
        if "|||" in texto:
            partes = texto.split("|||")
            return partes[0].strip(), partes[1].strip()
        else:
            return texto, "Não foi possível separar automaticamente. Verifique o texto."
    except Exception as e:
        return f"Erro de conexão: {str(e)}", ""

# --- INICIALIZAÇÃO DE ESTADO ---
if 'edit_index' not in st.session_state:
    st.session_state['edit_index'] = None
    
# --- CSS PERSONALIZADO (Refinamento Visual) ---
st.markdown("""
<style>
    @media (max-width: 600px) {
        h1 { font-size: 1.8rem !important; }
        .streamlit-expanderHeader { font-size: 1rem !important; }
    }
    p { text-align: justify; }
</style>
""", unsafe_allow_html=True)

# --- CARREGA DADOS E ADMIN ---
dados_app = carregar_dados()
lista_eventos = dados_app["eventos"]
titulo_atual = dados_app.get("titulo", "Cronograma Profético")
admin_mode = (st.sidebar.text_input("Senha de Acesso", type="password") == SENHA_CORRETA)

# --- INTERFACE PRINCIPAL ---
st.title(titulo_atual)
st.markdown(f"**Versão do App:** `{VERSAO_APP}` | **Versão do Conteúdo:** `{VERSAO_CONTEUDO}`") 
st.caption("Toque nos itens abaixo para expandir e ler.")

# --- BARRA LATERAL (ADMIN E CONFIGURAÇÕES) ---
with st.sidebar:
    st.header("⚙️ Área do Editor")
    if admin_mode:
        st.success("✅ Modo Edição Ativo")
        st.divider()
        st.subheader("Personalizar")
        novo_titulo = st.text_input("Título do Projeto", value=titulo_atual)
        if novo_titulo != titulo_atual:
            dados_app["titulo"] = novo_titulo
            salvar_dados(dados_app)
            st.rerun()
        
        # Botão para cancelar edição se estiver no modo edição
        if st.session_state.edit_index is not None:
             if st.button("❌ Cancelar Edição"):
                st.session_state.edit_index = None
                st.rerun()
            
    elif st.sidebar.text_input("Senha de Acesso", type="password"): # A senha já foi digitada acima, só checa se não está vazia
        st.error("Senha incorreta")
        
    st.divider()
    st.caption(f"App v{VERSAO_APP} | Conteúdo v{VERSAO_CONTEUDO}")
    

# --- FORMULÁRIO DE ADIÇÃO/EDIÇÃO (UNIFICADO) ---
if admin_mode:
    
    form_titulo = "➕ Adicionar Novo Evento"
    data_padrao, evento_padrao, hist_padrao, bib_padrao = "", "", "", ""
    submit_label = "💾 Salvar Novo Evento"

    # Se estiver no modo edição, preenche os dados
    if st.session_state.edit_index is not None:
        idx = st.session_state.edit_index
        item = lista_eventos[idx]
        
        form_titulo = f"✏️ Editando: {item['evento']}"
        data_padrao = item['data']
        evento_padrao = item['evento']
        hist_padrao = item['historico']
        bib_padrao = item['escritura']
        submit_label = f"✅ Atualizar Evento {item['data']}"

    with st.expander(form_titulo, expanded=(st.session_state.edit_index is not None)):
        st.write("Use a IA para buscar textos ou preencha manualmente.")
        
        col_input1, col_input2 = st.columns([1, 2])
        with col_input1:
            data_temp = st.text_input("Data (ex: 539 a.C.)", key="in_data", value=data_padrao)
        with col_input2:
            evento_temp = st.text_input("Nome do Evento", key="in_evento", value=evento_padrao)
            
        if st.button("✨ Pesquisar com IA"):
            if evento_temp:
                with st.spinner("Consultando escrituras..."):
                    hist_ia, bib_ia = consultar_gemini(evento_temp)
                    st.session_state['temp_hist'] = hist_ia
                    st.session_state['temp_bib'] = bib_ia
                    st.session_state['temp_data'] = data_temp # Mantém data
                    st.session_state['temp_evento'] = evento_temp # Mantém evento
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
                    "data": data_temp, # Pega do input acima
                    "evento": evento_temp, # Pega do input acima
                    "historico": txt_historico,
                    "escritura": txt_biblico
                }
                
                if st.session_state.edit_index is not None:
                    # Modo Edição: Substitui o item
                    lista_eventos[st.session_state.edit_index] = novo_item
                    st.session_state.edit_index = None
                    st.success("Evento atualizado com sucesso!")
                else:
                    # Modo Adição: Adiciona novo item
                    lista_eventos.append(novo_item)
                    st.success("Evento salvo com sucesso!")
                    
                dados_app["eventos"] = lista_eventos
                salvar_dados(dados_app)
                # Limpa estados temporários
                st.session_state['temp_hist'] = ""
                st.session_state['temp_bib'] = ""
                st.rerun()

# --- ÁREA DE VISUALIZAÇÃO (LINHA DO TEMPO) ---
st.divider()

if not lista_eventos:
    st.info("O cronograma está vazio. Faça login para começar.")
else:
    # Ordenação dos eventos usando a função personalizada
    eventos_ordenados = sorted(lista_eventos, key=lambda x: get_sort_key(x['data']), reverse=True) # Reverse=True para que a.C. venha primeiro

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
                    # Encontra o índice do item original para edição
                    original_index = lista_eventos.index(item)
                    st.session_state.edit_index = original_index
                    st.rerun()

                # CONFIRMAÇÃO DE EXCLUSÃO
                with col_delete:
                    # Usando checkbox como confirmação simples para exclusão
                    if st.checkbox("Confirmar Exclusão", key=f"check_del_{i}"):
                        if st.button("🗑️ Excluir permanentemente", key=f"del_{i}"):
                            # Remove o item da lista original (não da lista ordenada)
                            lista_eventos.remove(item)
                            dados_app["eventos"] = lista_eventos
                            salvar_dados(dados_app)
                            st.session_state.edit_index = None # Limpa estado de edição
                            st.rerun()

# Rodapé
st.markdown("---")
st.caption(f"App v{VERSAO_APP} | Conteúdo v{VERSAO_CONTEUDO}")
