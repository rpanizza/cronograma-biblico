import streamlit as st
import google.generativeai as genai
import json
import os
import re
import uuid 

# --- CONFIGURAÇÃO INICIAL E VERSÕES ---
st.set_page_config(
    page_title="Cronograma Dinâmico", 
    layout="centered", 
    initial_sidebar_state="auto"
)

# Versão do Aplicativo (App) - Correção da API Gemini e UX do Prompt
VERSAO_APP = "1.2.2" 
# Versão do Conteúdo (Cronologia)
VERSAO_CONTEUDO = "25.1208.9" 

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
    try: year = int(match.group(1))
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
            
            # Garante que dados antigos tenham IDs únicos e parent_id
            for event in conteudo.get("eventos", []):
                if 'id' not in event:
                    event['id'] = str(uuid.uuid4())
                if 'parent_id' not in event:
                    event['parent_id'] = None
            
            return conteudo
        except json.JSONDecodeError:
            return dados_padrao

def salvar_dados(dados):
    with open(ARQUIVO_DADOS, 'w', encoding='utf-8') as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)

# --- INTEGRAÇÃO COM GEMINI: CRONOLOGIA (STRICT + EMOJI) ---
def consultar_gemini_cronologia(topico):
    if not API_KEY: return "⚠️ Erro: Chave API não configurada.", "", ""
    # Usando modelo atualizado
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-2.5-flash') 
    
    prompt = f"""
    Atue como assistente estrito de cronologia bíblica para preenchimento de banco de dados.
    Tópico: "{topico}"
    Sua tarefa é gerar TRÊS partes: 1. UM ÚNICO EMOJI. 2. Fato histórico. 3. Referência e texto da escritura integralmente.
    REGRAS CRÍTICAS: O emoji deve ser o primeiro item, sem texto extra. Use FORMATO OBRIGATÓRIO.
    FORMATO OBRIGATÓRIO: [EMOJI] ||| [Fato Histórico] ||| [Referência e Texto Bíblico]
    """
    try:
        response = model.generate_content(prompt)
        texto = response.text
        if texto.count("|||") == 2:
            partes = texto.split("|||")
            return partes[0].strip(), partes[1].strip(), partes[2].strip()
        else:
            return "❓", texto, "Não foi possível separar. Verifique o texto."
    except Exception as e:
        return "❌", f"Erro de conexão: {str(e)}", ""

# --- INTEGRAÇÃO COM GEMINI: PESQUISA (FLEXÍVEL) ---
def consultar_gemini_research(topico, model_name):
    if not API_KEY: return "⚠️ Erro: Chave API não configurada.", ""
    genai.configure(api_key=API_KEY)
    # Modelos são passados já atualizados: gemini-2.5-flash ou gemini-2.5-pro
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

# --- LÓGICA DE ESTADO E SAÍDA DE EDIÇÃO ---

def reset_edit_states():
    """Limpa todos os estados temporários de edição e adição."""
    for key in ['edit_index', 'temp_hist', 'temp_bib', 'temp_evento', 'research_topic', 'show_add_form']:
        if key in st.session_state:
            del st.session_state[key]
    if 'research_input' in st.session_state: # Novo campo
         del st.session_state['research_input']
    if 'confirm_exit' in st.session_state:
        del st.session_state['confirm_exit']

def has_unsaved_changes():
    """Verifica se há conteúdo sendo editado ou adicionado no formulário."""
    return (st.session_state.edit_index is not None or
            st.session_state.get('temp_hist', '') or 
            st.session_state.get('temp_bib', '') or
            st.session_state.get('temp_evento', '') or
            st.session_state.get('show_add_form', False))

# --- INICIALIZAÇÃO DE ESTADO E CSS ---
if 'edit_index' not in st.session_state: st.session_state['edit_index'] = None
if 'research_input' not in st.session_state: st.session_state['research_input'] = "Digite aqui o tópico de pesquisa..." # Novo estado para o prompt unificado
if 'admin_pass_input' not in st.session_state: st.session_state['admin_pass_input'] = ""
if 'show_add_form' not in st.session_state: st.session_state['show_add_form'] = False
if 'confirm_exit' not in st.session_state: st.session_state['confirm_exit'] = False

st.markdown("""
<style>
    @media (max-width: 600px) { h1 { font-size: 1.8rem !important; } }
    p { text-align: justify; }
    /* Estilo para indentação de sub-eventos */
    .sub-event-card {
        padding-left: 20px;
        margin-top: 5px;
        border-left: 3px solid #f0f2f6; /* Cor da borda para visual de árvore */
    }
</style>
""", unsafe_allow_html=True)

# --- CARREGA DADOS E ADMIN CHECK ---
dados_app = carregar_dados()
lista_eventos = dados_app["eventos"]
titulo_atual = dados_app.get("titulo", "Cronograma Profético")

# Senha de Acesso no Sidebar (Define o modo admin)
password_input = st.sidebar.text_input("Senha de Acesso", type="password", key='admin_pass_input')
admin_mode = (password_input == SENHA_CORRETA)

# --- INTERFACE PRINCIPAL ---

st.title(titulo_atual)

# LAYOUT DA VERSÃO
st.markdown(f"""
<div style='line-height: 1.2; margin-bottom: 1rem;'>
    <p style='margin: 0; font-size: 0.95em;'>
        <b>Versão do App:</b> <code>{VERSAO_APP}</code>
    </p>
    <p style='margin: 0; font-size: 0.95em;'>
        <b>Versão do Conteúdo:</b> <code>{VERSAO_CONTEUDO}</code>
    </p>
    <p style='margin: 0; font-size: 0.95em;'>
        <b>Bíblia:</b> <i>Almeida Revista e Atualizada (ARA)</i>
    </p>
</div>
""", unsafe_allow_html=True)

st.caption("Toque nos itens abaixo para expandir e ler.")

# --- BARRA LATERAL (ADMIN E SAÍDA) ---
with st.sidebar:
    st.header("⚙️ Ferramentas")
    
    # AVISO DE SENHA INCORRETA
    if password_input and password_input != SENHA_CORRETA:
        st.error("⚠️ Senha incorreta. Acesso negado.")

    if admin_mode:
        st.success("✅ Modo Edição Ativo")
        st.divider()
        
        # BOTÃO SAIR DO MODO EDIÇÃO
        if st.button("🚪 Sair do Modo Edição", key='exit_admin_btn'):
            if has_unsaved_changes():
                st.session_state['confirm_exit'] = True
            else:
                # Limpa a senha para sair do modo admin
                st.session_state['admin_pass_input'] = '' 
                reset_edit_states()
        
        # CONFIRMAÇÃO DE SAÍDA
        if st.session_state.get('confirm_exit', False):
            st.warning("⚠️ Você possui conteúdo não salvo (edição ou adição em andamento)! Se sair, perderá o conteúdo.")
            col_confirm, col_cancel = st.columns(2)
            if col_confirm.button("Confirmar Saída (Perder Dados)"):
                st.session_state['admin_pass_input'] = ''
                st.session_state['confirm_exit'] = False
                reset_edit_states()
            if col_cancel.button("Cancelar Saída"):
                st.session_state['confirm_exit'] = False
                st.rerun()

        st.divider()
        st.subheader("Personalizar")
        novo_titulo = st.text_input("Título do Projeto", value=titulo_atual)
        if novo_titulo != titulo_atual:
            dados_app["titulo"] = novo_titulo
            salvar_dados(dados_app)
            st.rerun()

        st.divider()
        st.subheader("Salvamento e Backup")
        
        json_data = json.dumps(dados_app, indent=4, ensure_ascii=False)
        st.download_button(
            label="⬇️ Backup Externo (.json)",
            data=json_data,
            file_name='backup_cronograma.json',
            mime='application/json'
        )
        
        if st.session_state.edit_index is not None:
             if st.button("❌ Cancelar Edição"):
                st.session_state.edit_index = None
                reset_edit_states()
            
    st.divider()
    st.caption(f"App v{VERSAO_APP} | Conteúdo v{VERSAO_CONTEUDO}")
    

# --- FORMULÁRIO DE ADIÇÃO/EDIÇÃO (UNIFICADO) ---
if admin_mode:
    
    item_editado = None
    if st.session_state.edit_index is not None:
        item_editado = lista_eventos[st.session_state.edit_index]
    
    form_titulo = f"✏️ Editando: {item_editado['evento']}" if item_editado else "➕ Adicionar Novo Evento"
    data_padrao = item_editado['data'] if item_editado else ""
    evento_padrao = item_editado['evento'] if item_editado else ""
    hist_padrao = item_editado['historico'] if item_editado else ""
    bib_padrao = item_editado['escritura'] if item_editado else ""
    parent_id_padrao = item_editado.get('parent_id') if item_editado else None
    submit_label = f"✅ Atualizar Evento {data_padrao}" if item_editado else "💾 Salvar Novo Evento"

    # Criar lista de Eventos Principais (para o selectbox Pai)
    eventos_principais_options = [
        {"evento": "Nenhum (Evento Principal/Raiz)", "id": None}
    ]
    
    # Adiciona todos os eventos para que sub-eventos também possam ser pais
    for event in lista_eventos:
        # Garante que não possa ser pai de si mesmo
        if not item_editado or event['id'] != item_editado.get('id'):
            eventos_principais_options.append({"evento": f"{event['data']} - {event['evento']}", "id": event['id']})

    # Encontra o índice padrão para o selectbox
    parent_default_index = 0
    if parent_id_padrao:
        for i, option in enumerate(eventos_principais_options):
            if option['id'] == parent_id_padrao:
                parent_default_index = i
                break
    
    
    with st.expander(form_titulo, expanded=(item_editado is not None or st.session_state.get('show_add_form', False))):
        st.write("Use a IA para buscar textos ou preencha manualmente.")
        
        # SELECTBOX PARA EVENTO PAI
        parent_selection = st.selectbox(
            "Escolha o Evento Pai (Árvore de Estudo)",
            options=[opt['evento'] for opt in eventos_principais_options],
            index=parent_default_index
        )
        # Encontra o ID do evento pai selecionado
        parent_id_final = next(item['id'] for item in eventos_principais_options if item['evento'] == parent_selection)
        
        col_input1, col_input2 = st.columns([1, 2])
        with col_input1:
            data_temp = st.text_input("Data (ex: 08/12/25)", key="in_data", value=data_padrao)
        with col_input2:
            evento_temp = st.text_input("Tópico para IA", key="in_evento_ia", value=evento_padrao) # Novo campo para IA
            
        if st.button("✨ Pesquisar Cronologia (Fiel) com IA"):
            if evento_temp:
                with st.spinner("Consultando escrituras..."):
                    emoji_ia, hist_ia, bib_ia = consultar_gemini_cronologia(evento_temp)
                    
                    # Concatena emoji ao evento
                    evento_com_emoji = f"{emoji_ia} {evento_temp}"
                    
                    st.session_state['temp_hist'] = hist_ia
                    st.session_state['temp_bib'] = bib_ia
                    st.session_state['temp_evento'] = evento_com_emoji # Salva o evento com emoji
            else:
                st.warning("Digite o nome do evento primeiro.")
        
        # Usa o evento com emoji se a IA rodou, senão usa o padrão/editado
        val_evento = st.session_state.get('temp_evento', evento_padrao)
        val_hist = st.session_state.get('temp_hist', hist_padrao)
        val_bib = st.session_state.get('temp_bib', bib_padrao)
        
        with st.form("form_salvar"):
            # O campo de nome de evento é preenchido com o emoji + texto
            evento_final = st.text_input("Nome/Título Final do Evento (Com Emoji)", value=val_evento, key="final_evento")
            txt_historico = st.text_area("Fato Histórico", value=val_hist, height=150)
            txt_biblico = st.text_area("Texto das Escrituras (Fiel)", value=val_bib, height=200) 
            
            if st.form_submit_button(submit_label):
                novo_item = {
                    "id": item_editado['id'] if item_editado else str(uuid.uuid4()),
                    "parent_id": parent_id_final,
                    "data": data_temp,
                    "evento": evento_final,
                    "historico": txt_historico,
                    "escritura": txt_biblico
                }
                
                if item_editado is not None:
                    # Modo Edição: Substitui
                    idx = lista_eventos.index(item_editado)
                    lista_eventos[idx] = novo_item
                    st.session_state.edit_index = None
                    st.success("Evento atualizado com sucesso!")
                else:
                    # Modo Adição: Adiciona
                    lista_eventos.append(novo_item)
                    st.success("Evento salvo com sucesso!")
                    
                dados_app["eventos"] = lista_eventos
                salvar_dados(dados_app)
                # Limpa estados temporários
                reset_edit_states()
                st.rerun()

    st.divider()
    
    # --- FERRAMENTA DE PESQUISA GEMINI (UX DE PROMPT UNIFICADO) ---
    with st.expander("🔬 Ferramenta de Estudo e Pesquisa (Gemini)", expanded=False):
        
        st.subheader("Pesquisa Rápida e Raciocínio Profundo")
        
        col_model, col_run = st.columns([1, 2])
        with col_model:
            model_selected = st.selectbox(
                "Escolha o Modelo",
                options=['gemini-2.5-flash (Rápido/Padrão)', 'gemini-2.5-pro (Raciocínio Pro)'], # Nomes atualizados
                key='model_selection'
            )
            model_key = 'gemini-2.5-flash' if 'flash' in model_selected else 'gemini-2.5-pro'
        
        # Campo de Interação Único (Input/Output)
        st.session_state.research_input = st.text_area(
            "Digite seu prompt de estudo ou veja o resultado da IA aqui:", 
            key='research_input', 
            value=st.session_state.research_input,
            height=350 # Campo aumentado
        )

        col_run_ai, col_clear = st.columns([1, 1])
        if col_run_ai.button("▶️ Executar Pesquisa"):
            if st.session_state.research_input and st.session_state.research_input != "Digite aqui o tópico de pesquisa...":
                with st.spinner(f"Consultando {model_selected}..."):
                    # O output é injetado diretamente no input
                    st.session_state.research_input = consultar_gemini_research(
                        st.session_state.research_input, model_key
                    )
            else:
                st.warning("Digite um tópico para pesquisar no campo de interação.")
            st.rerun()

        if col_clear.button("🗑️ Limpar Pesquisa / Novo Assunto"):
            st.session_state.research_input = "Digite aqui o tópico de pesquisa..."
            st.rerun()
            
        st.markdown("---")
        
        if st.button("📝 Salvar Resultado no Cronograma"):
            output = st.session_state.research_input # Pega o texto do campo de interação
            
            # Tenta separar o texto nos formatos HISTÓRICO/CONTEXTO e ESCRITURAS RELACIONADAS
            hist_match = re.search(r'1\. HISTÓRICO/CONTEXTO(.*?)2\. ESCRITURAS RELACIONADAS', output, re.DOTALL)
            bib_match = re.search(r'2\. ESCRITURAS RELACIONADAS(.*)', output, re.DOTALL)
            
            hist_temp = hist_match.group(1).strip() if hist_match else output
            bib_temp = bib_match.group(1).strip() if bib_match else "Texto bíblico não separado, por favor, revise manualmente."
            
            # Define o primeiro parágrafo como título temporário
            title_match = re.match(r'#+\s*(.*?)\n', output)
            temp_title = title_match.group(1).strip() if title_match else "Resultado da Pesquisa (Ajustar Título)"

            st.session_state['temp_hist'] = hist_temp
            st.session_state['temp_bib'] = bib_temp
            st.session_state['temp_evento'] = temp_title
            st.session_state['show_add_form'] = True 
            
            st.success("Resultado transferido para o formulário 'Adicionar Novo Evento'. Revise a Data, o Título e o Evento Pai.")
            st.rerun()

# --- ÁREA DE VISUALIZAÇÃO (LINHA DO TEMPO) ---
st.divider()

def display_event(item, is_sub_event=False, admin_mode=False):
    """Função recursiva para exibir eventos e sub-eventos."""
    global lista_eventos # CORREÇÃO: Colocado no início da função
    
    # Aplica indentação para sub-eventos
    container_class = "sub-event-card" if is_sub_event else ""
    
    # Adiciona uma div de controle para aplicar o CSS
    st.markdown(f"<div class='{container_class}'>", unsafe_allow_html=True)
    
    titulo_prefix = "🔗 " if is_sub_event else "🗓️ "
    titulo_card = f"{titulo_prefix} **{item['data']}** — {item['evento']}"
    
    with st.expander(titulo_card):
        st.markdown(f"""
        **Contexto Histórico:**
        {item['historico']}
        """)
        
        st.markdown("---")
        
        st.markdown("**📖 Escrituras (Texto Fiel):**")
        st.info(f"_{item['escritura']}_")
        
        if admin_mode:
            col_edit, col_delete = st.columns([1, 1])
            
            if col_edit.button("✏️ Editar", key=f"edit_{item['id']}"):
                # Encontra o índice na lista não-ordenada usando o ID
                for i, evt in enumerate(lista_eventos):
                    if evt['id'] == item['id']:
                        st.session_state.edit_index = i
                        break
                st.session_state['show_add_form'] = True
                st.rerun()

            with col_delete:
                if st.checkbox("Confirmar Exclusão", key=f"check_del_{item['id']}"):
                    if st.button("🗑️ Excluir permanentemente", key=f"del_{item['id']}"):
                        # Remove o item pelo ID
                        lista_eventos = [e for e in lista_eventos if e['id'] != item['id']]
                        dados_app["eventos"] = lista_eventos
                        salvar_dados(dados_app)
                        reset_edit_states()
                        st.rerun()
    
    # Fecha a div de controle
    st.markdown("</div>", unsafe_allow_html=True)

# Organiza eventos em uma estrutura hierárquica (dicionário)
eventos_por_parent = {}
for item in lista_eventos:
    parent_id = item.get('parent_id') or None
    if parent_id not in eventos_por_parent:
        eventos_por_parent[parent_id] = []
    eventos_por_parent[parent_id].append(item)

# Ordena os eventos principais (parent_id é None)
eventos_principais = sorted(eventos_por_parent.get(None, []), key=lambda x: get_sort_key(x['data']), reverse=True)

# FUNÇÃO PARA VISUALIZAÇÃO RECURSIVA
def render_event_tree(events, parent_id, is_sub_event):
    if parent_id in events:
        for item in sorted(events[parent_id], key=lambda x: get_sort_key(x['data']), reverse=False):
            display_event(item, is_sub_event, admin_mode)
            # Chama recursivamente para sub-eventos
            if item['id'] in events:
                render_event_tree(events, item['id'], True)
        
if not lista_eventos:
    st.info("O cronograma está vazio. Faça login para começar.")
else:
    # Renderiza a árvore, começando pelos eventos principais
    render_event_tree(eventos_por_parent, None, False)


# Rodapé
st.markdown("---")
st.caption(f"App v{VERSAO_APP} | Conteúdo v{VERSAO_CONTEUDO}")
