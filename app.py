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

# Versão do Aplicativo (App) - Painel de Controle Centralizado e Edição/Exclusão de Títulos
VERSAO_APP = "1.9.0" 
# Versão do Conteúdo (Cronologia)
VERSAO_CONTEUDO = "25.1208.19" 

# Nome do arquivo onde os dados serão salvos
ARQUIVO_DADOS = 'cronograma.json'
API_KEY = st.secrets.get("GEMINI_API_KEY", "")
SENHA_CORRETA = "R$Masterkey01" # Senha de Admin

# --- FUNÇÕES DE ORDENAÇÃO E DADOS ---

def get_sort_key(date_str):
    """Converte a data (ex: '539 a.C.') em um número para ordenação."""
    date_str_clean = date_str.lower().replace('.', '').strip()
    match = re.match(r'(\d+)\s*(a\.c\.|ac|d\.c\.|dc)?', date_str_clean)
    if not match: 
        if "futuro" in date_str_clean or "tribulação" in date_str_clean:
            return 999999 
        return 0 
    
    try: 
        year = int(match.group(1))
    except ValueError: 
        return 0 
    
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
            
            for event in conteudo.get("eventos", []):
                if 'id' not in event:
                    event['id'] = str(uuid.uuid4())
                # Garante que todos os eventos tenham parent_id
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
    if not API_KEY: 
        return "⚠️ Erro: Chave API não configurada.", "", "", "", "", "Chave API não configurada."
        
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-2.5-flash') 
    
    prompt = f"""
    Atue como assistente estrito de cronologia bíblica.
    Tópico: "{topico}"
    
    Sua tarefa é gerar CINCO partes separadas por "|||":
    1. A data do evento (Ex: 959 a.C. ou 32 d.C. ou Futuro).
    2. UM ÚNICO EMOJI e o Título do Evento (Ex: ✨ A Dedicação do Primeiro Templo).
    3. Profeta e Data de Escrita (Ex: Livros dos Reis e Crônicas (Escrito c. 560–430 a.C.)).
    4. Referência e texto da escritura integralmente (Sem abreviações).
    5. Análise Histórica/Hipotética (Texto detalhado, com parágrafos curtos).
    
    FORMATO OBRIGATÓRIO: [DATA] ||| [EMOJI + TÍTULO] ||| [PROFETA E DATA] ||| [TEXTO BÍBLICO] ||| [ANÁLISE]
    """
    try:
        response = model.generate_content(prompt)
        texto = response.text.strip()
        
        # O formato deve ter 4 separadores '|||'
        if texto.count("|||") == 4:
            partes = texto.split("|||")
            data = partes[0].strip()
            evento_emoji = partes[1].strip()
            profeta_data = partes[2].strip()
            biblia = partes[3].strip()
            analise = partes[4].strip()
            # Retorna as 5 partes separadas e o texto bruto
            return data, evento_emoji, profeta_data, biblia, analise, texto
        else:
            # Retorna um texto de erro e o texto bruto para inspeção
            return "", "❓ Erro de Formato", f"Resultado da IA: {texto}", "", "", texto
    except Exception as e:
        # Retorna um texto de erro e o erro
        return "", "❌ Erro de Conexão", f"Erro: {str(e)}", "", "", str(e)

# --- LÓGICA DE ESTADO E SAÍDA DE EDIÇÃO ---

def reset_edit_states():
    """Limpa todos os estados temporários de edição, adição, e os resultados da IA."""
    # Estados de Edição/Adição
    for key in ['edit_index', 'show_add_form', 'confirm_exit', 'show_ia_preview']:
        if key in st.session_state:
            del st.session_state[key]
            
    # Resultados da IA e temporários do formulário
    for key in ['ia_prompt_area', 'ia_response_text', 'ia_raw_result']:
        if key in st.session_state:
            del st.session_state[key]


def has_unsaved_changes():
    """Verifica se há conteúdo sendo editado ou adicionado no formulário."""
    return (st.session_state.edit_index is not None or
            st.session_state.get('show_add_form', False))
            
def run_ia_search(prompt):
    """Executa a pesquisa da IA e armazena os resultados."""
    if not prompt:
        st.session_state['status_message'] = ('warning', "Digite um tópico para pesquisar.")
        st.session_state['ia_response_text'] = None
        st.session_state['ia_raw_result'] = ""
        st.session_state['show_ia_preview'] = False 
        return
        
    # Limpa estados de visualização antes de pesquisar
    st.session_state['ia_response_text'] = None
    st.session_state['ia_raw_result'] = ""
    st.session_state['show_ia_preview'] = False 
    
    with st.spinner("Consultando IA e formatando dados..."):
        data, evento_emoji, profeta_data, biblia, analise, raw_text = consultar_gemini_cronologia(prompt)
        
        st.session_state['ia_raw_result'] = raw_text # Armazena o texto bruto (sempre)

        if raw_text.count("|||") == 4:
            # Formato válido
            ia_full_response = {
                'data': data, 'evento': evento_emoji, 'profeta': profeta_data, 
                'biblia': biblia, 'analise': analise
            }
            st.session_state['ia_response_text'] = ia_full_response
            st.session_state['status_message'] = ('success', "Pesquisa concluída! Use 'Mostrar Prévia' para revisar e salvar.")
        else:
            # Formato inválido
            st.session_state['status_message'] = ('error', f"Falha no formato da IA. Verifique o Resultado Bruto: Esperado 4 separadores '|||', encontrado {raw_text.count('|||')}.")
            st.session_state['ia_response_text'] = None # Garante que não há objeto para salvar
    
    st.rerun()

# --- INICIALIZAÇÃO DE ESTADO E CSS ---
# Estados principais
if 'edit_index' not in st.session_state: st.session_state['edit_index'] = None
if 'admin_pass_input' not in st.session_state: st.session_state['admin_pass_input'] = ""
if 'show_add_form' not in st.session_state: st.session_state['show_add_form'] = False
if 'confirm_exit' not in st.session_state: st.session_state['confirm_exit'] = False
if 'status_message' not in st.session_state: st.session_state['status_message'] = None
if 'is_admin' not in st.session_state: st.session_state['is_admin'] = False

# Estados da IA
if 'ia_prompt_area' not in st.session_state: st.session_state['ia_prompt_area'] = ""
if 'ia_response_text' not in st.session_state: st.session_state['ia_response_text'] = None # Resultado da IA (Formatado)
if 'ia_raw_result' not in st.session_state: st.session_state['ia_raw_result'] = "" # Resultado Bruto
if 'show_ia_preview' not in st.session_state: st.session_state['show_ia_preview'] = False # Controle da Prévia


st.markdown("""
<style>
    @media (max-width: 600px) { 
        h1 { font-size: 1.8rem !important; }
        .detail-line b { display: block; }
    }
    p { text-align: justify; }
    
    /* Título Principal (Capítulo) - Usado para renderizar o Cronograma na Pré-Visualização */
    .main-chapter-title {
        font-size: 1.5em;
        font-weight: bold;
        margin-top: 25px;
        margin-bottom: 15px;
        color: #004d40;
        border-bottom: 2px solid #004d40;
        padding-bottom: 5px;
    }
    
    /* Título para os Cards no Painel (para diferenciar do formato final) */
    .panel-chapter-title {
        font-size: 1.1em;
        font-weight: bold;
        color: #d35400; /* Laranja para destaque no Painel */
        margin-bottom: 5px;
    }
    
    /* Tamanho e hierarquia do texto no corpo */
    .detail-line b { font-size: 1.05em; color: #004d40; }
    .stAlert { font-size: 0.95em; }
    .stMarkdown p { font-size: 0.95em; }
    
    /* Linha do Tempo Vertical para a PRÉ-VISUALIZAÇÃO (Área Principal) */
    .timeline-container {
        position: relative;
        padding-left: 10px;
        margin-left: 10px;
    }
    
    .timeline-container::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        bottom: 0;
        width: 3px;
        background-color: #f0f2f6;
        z-index: 0;
    }

    /* Estilo de Card para PRÉ-VISUALIZAÇÃO */
    .timeline-event-card {
        padding-left: 20px;
        margin-top: 10px;
        margin-bottom: 20px;
        position: relative;
    }
    
    .timeline-event-card::before {
        content: '•';
        position: absolute;
        left: -8px;
        top: 22px; 
        font-size: 24px;
        line-height: 0;
        color: #004d40;
        background-color: white;
        border-radius: 50%;
        padding: 5px;
        z-index: 1;
    }

    .timeline-event-card > div[data-testid^="stExpander"] {
        padding: 0 !important;
    }
    
    .detail-icon {
        font-size: 1.1em;
        margin-right: 5px;
    }
    
    /* Estilo para a prévia da IA (corpo da caixa) */
    .ia-preview-box {
        border: 1px solid #004d40;
        border-radius: 5px;
        padding: 10px;
        margin-bottom: 15px;
    }
    .ia-preview-box h5 {
        margin-top: 0;
        color: #004d40;
        border-bottom: 1px dashed #e0e0e0;
        padding-bottom: 5px;
    }
    
    /* Card de Evento dentro do PAINEL DE CONTROLE (para Edição) */
    .panel-event-card {
        border: 1px solid #ccc;
        border-radius: 5px;
        padding: 10px;
        margin-bottom: 10px;
        background-color: #fafafa;
    }
    
    .panel-event-card .stButton {
        margin-top: 5px;
    }
    
</style>
""", unsafe_allow_html=True)


# --- LÓGICA DE LOGIN ---
dados_app = carregar_dados()
lista_eventos = dados_app["eventos"]
titulo_atual = dados_app.get("titulo", "Cronograma Profético")

# Lógica de autenticação
if st.session_state.admin_pass_input == SENHA_CORRETA and not st.session_state.is_admin:
    st.session_state.is_admin = True
    st.rerun()

admin_mode = st.session_state.is_admin

# --- BARRA LATERAL (ADMIN E SAÍDA) ---
with st.sidebar:
    st.header("⚙️ Ferramentas")
    
    if not admin_mode:
        password_input = st.text_input("Senha de Acesso", type="password", key='admin_pass_input')
        if password_input and password_input != SENHA_CORRETA:
            st.error("⚠️ Senha incorreta. Acesso negado.")
    
    if admin_mode:
        st.success("✅ Modo Edição Ativo")
        st.divider()
        
        if st.button("🚪 Sair do Modo Edição", key='exit_admin_btn'):
            if has_unsaved_changes():
                st.session_state['confirm_exit'] = True
            else:
                st.session_state.is_admin = False 
                st.session_state.admin_pass_input = '' 
                reset_edit_states()
                st.rerun() 
        
        if st.session_state.get('confirm_exit', False):
            st.warning("⚠️ Você possui conteúdo não salvo! Se sair, perderá o conteúdo.")
            col_confirm, col_cancel = st.columns(2)
            if col_confirm.button("Confirmar Saída (Perder Dados)"):
                st.session_state.is_admin = False
                st.session_state.admin_pass_input = ''
                st.session_state['confirm_exit'] = False
                reset_edit_states()
                st.rerun()
            if col_cancel.button("Cancelar Saída"):
                st.session_state['confirm_exit'] = False

        st.divider()
        st.subheader("Configurações Gerais")
        
        novo_titulo_geral = st.text_input("Título do Projeto", value=titulo_atual)
        if novo_titulo_geral != titulo_atual:
            dados_app["titulo"] = novo_titulo_geral
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
            
    st.divider()
    st.caption(f"App v{VERSAO_APP} | Conteúdo v{VERSAO_CONTEUDO}")
    

# --- FUNÇÕES DE RENDERIZAÇÃO ---

def is_historical_analysis(data_str):
    """Determina se a análise deve ser Histórica ou Hipotética com base na data."""
    data_str_lower = data_str.lower()
    if "futuro" in data_str_lower or "tribulação" in data_str_lower or not any(char.isdigit() for char in data_str):
        return False
    return True 

def display_event_preview(item, is_sub_event=False):
    """Função recursiva para exibir eventos e sub-eventos na Pré-Visualização (somente leitura)."""
    
    # --- TÍTULO PRINCIPAL (CAPÍTULO) ---
    if item.get('parent_id') is None and not is_sub_event:
        st.markdown(f"<div class='main-chapter-title'>{item['evento']}</div>", unsafe_allow_html=True)
        return

    # --- EVENTOS CRONOLÓGICOS (LINHA DO TEMPO) ---
    
    st.markdown(f"<div class='timeline-event-card'>", unsafe_allow_html=True)
    
    titulo_card = f"**{item['data']}** {item['evento']}" 
    
    with st.expander(titulo_card):
        
        profeta_data = item.get('profeta_data', 'Não informado')
        st.markdown(f"""
        <p class="detail-line">
            <span class="detail-icon">📅</span> 
            <b>Profeta e Data:</b> {profeta_data}
        </p>
        """, unsafe_allow_html=True)

        st.markdown("---")
        
        st.markdown(f"""
        <p class="detail-line">
            <span class="detail-icon">📖</span> 
            <b>Escrituras (ARA):</b>
        </p>
        """, unsafe_allow_html=True)
        st.info(f"_{item['escritura']}_") 
        
        st.markdown("---")

        data_evento = item['data']
        is_hist = is_historical_analysis(data_evento)
        analise_titulo_emoji = "🌍" if is_hist else "🔮"
        analise_titulo_texto = "Análise Histórica" if is_hist else "Análise Hipotética"
        
        st.markdown(f"""
        <p class="detail-line">
            <span class="detail-icon">{analise_titulo_emoji}</span> 
            <b>{analise_titulo_texto}:</b>
        </p>
        """, unsafe_allow_html=True)
        st.markdown(f"{item['historico']}") 
    
    st.markdown("</div>", unsafe_allow_html=True)


def render_preview_tree(events_list, events_by_parent):
    """Renderiza a pré-visualização completa do cronograma (somente leitura)."""
    
    def render_recursive(events, parent_id):
        if parent_id in events:
            sorted_events = sorted(events[parent_id], key=lambda x: get_sort_key(x['data']), reverse=False)
            
            st.markdown("<div class='timeline-container'>", unsafe_allow_html=True)
            
            for item in sorted_events:
                display_event_preview(item, is_sub_event=True) 
                
                if item['id'] in events:
                    render_recursive(events, item['id']) 
            
            st.markdown("</div>", unsafe_allow_html=True)

    if not events_list:
        st.info("O cronograma está vazio. Faça login e use o Painel de Controle para adicionar eventos.")
        return
        
    # 1. Itera sobre os Títulos Principais (parent_id=None)
    for principal_event in events_by_parent.get(None, []):
        
        display_event_preview(principal_event, is_sub_event=False)
        
        # 2. Renderiza Eventos Filhos (Cronológicos) deste Título Principal
        if principal_event['id'] in events_by_parent:
            render_recursive(events_by_parent, principal_event['id'])
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        
def display_event_control(item, admin_mode=False):
    """Renderiza o card de controle de um evento/título no Painel (com botões de ação)."""
    global lista_eventos 
    
    is_title = item.get('parent_id') is None
    
    st.markdown("<div class='panel-event-card'>", unsafe_allow_html=True)
    
    if is_title:
        st.markdown(f"<div class='panel-chapter-title'>[CAPÍTULO] {item['evento']}</div>", unsafe_allow_html=True)
    else:
        # Usa o 'data' no título do card no painel para facilitar identificação
        st.markdown(f"**{item['data']}** - {item['evento']}")
        
    st.caption(f"ID: {item['id'][:8]}...")
    
    col_edit, col_delete = st.columns([1, 1])
    
    if col_edit.button("✏️ Editar", key=f"edit_panel_{item['id']}"):
        for i, evt in enumerate(lista_eventos):
            if evt['id'] == item['id']:
                st.session_state.edit_index = i
                break
        # Força a expansão do Painel e do Formulário de Edição
        st.session_state['control_panel_expanded'] = True
        st.rerun()

    with col_delete:
        if st.checkbox("Confirmar Exclusão", key=f"check_del_panel_{item['id']}"):
            if st.button("🗑️ Excluir permanentemente", key=f"del_panel_{item['id']}"):
                
                # Exclui o próprio evento
                lista_eventos = [e for e in lista_eventos if e['id'] != item['id']]
                
                # Se for um título (parent_id=None), desvincula todos os filhos dele
                if is_title:
                    for event in lista_eventos:
                        if event.get('parent_id') == item['id']:
                            event['parent_id'] = None # Torna o filho em um novo título/capítulo
                
                dados_app["eventos"] = lista_eventos
                salvar_dados(dados_app)
                reset_edit_states()
                st.session_state['status_message'] = ('success', f"✅ {'Título' if is_title else 'Evento'} excluído e filhos reassociados, se aplicável.")
                st.rerun()
    
    st.markdown("</div>", unsafe_allow_html=True)

# --- INÍCIO DA INTERFACE PRINCIPAL ---

st.title(titulo_atual)

# Exibe mensagens de status (sucesso/falha)
if st.session_state.get('status_message'):
    tipo, mensagem = st.session_state['status_message']
    if tipo == 'success':
        st.success(mensagem)
    elif tipo == 'error':
        st.error(mensagem)
    elif tipo == 'warning':
        st.warning(mensagem)
    st.session_state['status_message'] = None 

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


# --- PAINEL DE CONTROLE CENTRALIZADO (MODO ADMIN) ---
if admin_mode:
    
    # Renderização da árvore de eventos
    eventos_por_parent = {}
    for item in lista_eventos:
        parent_id = item.get('parent_id') or None
        if parent_id not in eventos_por_parent:
            eventos_por_parent[parent_id] = []
        eventos_por_parent[parent_id].append(item)
    
    # Ordena todos os eventos
    todos_eventos_ordenados = sorted(lista_eventos, key=lambda x: (x.get('parent_id') or x['id'], get_sort_key(x['data'])), reverse=False)

    
    # Determina se o painel deve estar expandido
    is_editing = st.session_state.edit_index is not None
    
    # Se estiver editando, expande o painel automaticamente. Caso contrário, usa o estado anterior.
    control_panel_expanded = is_editing or st.session_state.get('control_panel_expanded', False)

    with st.expander("🛠️ Painel de Controle (Edição Completa)", expanded=control_panel_expanded, key='control_panel_expander'):
        
        # Salva o estado expandido/contraído
        st.session_state['control_panel_expanded'] = st.session_state.control_panel_expander
        
        st.header("1. Ferramentas da IA e Prévia")
        
        # --- FERRAMENTA DE INTERAÇÃO E PRÉVIA DA IA ---
        st.subheader("🤖 Pesquisa e Geração de Conteúdo")
        
        prompt_ia_input = st.text_area(
            "Prompt para Pesquisa IA (Tópico)", 
            key='ia_prompt_area', 
            height=100
        )
        
        if st.button("🔍 Iniciar Pesquisa Cronológica", key='run_ia_btn_panel'):
            run_ia_search(st.session_state.ia_prompt_area)

        st.markdown("---")

        # Campo de Resultado Bruto
        st.subheader("Resultado Bruto da IA")
        st.caption("Verifique se o texto abaixo contém **quatro separadores `|||`** para garantir a formatação correta.")
        st.text_area(
            "Resultado Bruto",
            value=st.session_state.get('ia_raw_result', 'Nenhum resultado de pesquisa.'),
            key='ia_raw_result_display',
            height=150,
            disabled=True 
        )

        st.markdown("---")
        
        ia_data = st.session_state.get('ia_response_text')
        is_ia_result_valid = ia_data is not None 
        
        # Botão Mostrar Prévia (Desabilitado até ter resultado válido)
        if st.button("✨ Mostrar Prévia / Ocultar", key='toggle_preview_btn_panel', disabled=not is_ia_result_valid):
            if is_ia_result_valid:
                st.session_state['show_ia_preview'] = not st.session_state.get('show_ia_preview', False)
            st.rerun()

        # Prévia e Salvamento Direto da IA
        if is_ia_result_valid and st.session_state.get('show_ia_preview', False):
            
            data_ia = ia_data['data']
            evento_ia = ia_data['evento']
            profeta_ia = ia_data['profeta']
            biblia_ia = ia_data['biblia']
            analise_ia = ia_data['analise']
            
            # 1. Prévia Formatada
            st.markdown("<div class='ia-preview-box'>", unsafe_allow_html=True)
            st.markdown("<h5>Prévia do Evento da IA (Revisão)</h5>", unsafe_allow_html=True)
            st.markdown(f"**Data:** `{data_ia}` | **Título:** `{evento_ia}`")
            st.markdown(f"**Profeta/Data:** *{profeta_ia}*")
            st.markdown(f"**Escrituras:**"); st.info(f"_{biblia_ia}_")
            st.markdown(f"**Análise:** {analise_ia}")
            st.markdown("</div>", unsafe_allow_html=True)
            
            # 2. Seleção de Evento Pai
            eventos_principais_options = [
                {"evento": "Nenhum (Título Principal/Capítulo Novo)", "id": None}
            ]
            for event in lista_eventos:
                eventos_principais_options.append({"evento": f"{event['data']} - {event['evento']}", "id": event['id']})

            parent_selection_ia = st.selectbox(
                "Escolha o Evento Pai para a Prévia",
                options=[opt['evento'] for opt in eventos_principais_options],
                index=0,
                key='select_parent_ia_panel'
            )
            parent_id_ia = next(item['id'] for item in eventos_principais_options if item['evento'] == parent_selection_ia)

            # 3. Botão de Salvar Direto da Prévia
            if st.button("💾 Salvar Evento da Prévia", key='save_ia_preview_panel'):
                
                try:
                    novo_item = {
                        "id": str(uuid.uuid4()),
                        "parent_id": parent_id_ia,
                        "data": data_ia,
                        "evento": evento_ia,
                        "historico": analise_ia,
                        "escritura": biblia_ia,
                        "profeta_data": profeta_ia
                    }
                    
                    lista_eventos.append(novo_item)
                    dados_app["eventos"] = lista_eventos
                    salvar_dados(dados_app)
                    
                    st.session_state['status_message'] = ('success', "✅ Evento da Prévia salvo com sucesso!")
                    reset_edit_states() # Limpa estados da IA e prévia
                    st.rerun()

                except Exception as e:
                    st.session_state['status_message'] = ('error', f"❌ Falha ao salvar evento da prévia: {str(e)}")
                    st.rerun()
        
        st.markdown("---")

        # --- FORMULÁRIO DE ADIÇÃO/EDIÇÃO MANUAL (SEMPRE DENTRO DO PAINEL) ---
        st.header("2. Adição e Edição Manual")
        
        item_editado = None
        if st.session_state.edit_index is not None:
            item_editado = lista_eventos[st.session_state.edit_index]
        
        form_titulo = f"✏️ Editando: {item_editado['evento']}" if item_editado else "✍️ Adicionar Novo Evento (Manual)"
        
        # 1. Recupera valores (apenas para edição)
        data_padrao = item_editado['data'] if item_editado else ''
        evento_padrao = item_editado['evento'] if item_editado else ''
        profeta_padrao = item_editado.get('profeta_data', '') if item_editado else ''
        hist_padrao = item_editado['historico'] if item_editado else ''
        bib_padrao = item_editado['escritura'] if item_editado else ''
        parent_id_padrao = item_editado.get('parent_id') if item_editado else None
        
        submit_label = f"✅ Atualizar Evento {data_padrao}" if item_editado else "💾 Salvar Novo Evento"

        # Criar lista de Eventos Principais para seleção de Pai
        eventos_principais_options = [
            {"evento": "Nenhum (Título Principal/Capítulo Novo)", "id": None}
        ]
        for event in lista_eventos:
            if not item_editado or event['id'] != item_editado.get('id'):
                eventos_principais_options.append({"evento": f"{event['data']} - {event['evento']}", "id": event['id']})

        parent_default_index = 0
        if parent_id_padrao:
            for i, option in enumerate(eventos_principais_options):
                if option['id'] == parent_id_padrao:
                    parent_default_index = i
                    break
        
        # Formulário SEMPRE expandido quando em modo edição.
        form_expanded = item_editado is not None 

        with st.expander(form_titulo, expanded=form_expanded):
            st.write("Use este formulário para **edição** ou para adicionar dados **manualmente**.")
            
            with st.form("form_salvar_manual_panel"):
                
                # Permite definir o item como Título Principal (parent_id=None) ou filho de outro.
                parent_selection = st.selectbox(
                    "Escolha o Evento Pai (Deixe em 'Nenhum' para criar um Título/Capítulo Principal)",
                    options=[opt['evento'] for opt in eventos_principais_options],
                    index=parent_default_index,
                    key='select_parent_manual_panel'
                )
                parent_id_final = next(item['id'] for item in eventos_principais_options if item['evento'] == parent_selection)

                col_input1, col_input2 = st.columns([1, 2])
                with col_input1:
                    # Títulos Principais não precisam de data, mas a IA sempre fornece, então permitimos vazio
                    data_final = st.text_input("Data (Ex: 959 a.C. ou Futuro)", key="in_data_final_m_panel", value=data_padrao)
                with col_input2:
                    evento_final = st.text_input("Título Final do Evento (Com Emoji)", value=evento_padrao, key="final_evento_m_panel")
                
                txt_profeta_data = st.text_input("Profeta e Data de Escrita (ou Subtítulo)", 
                                                 value=profeta_padrao, 
                                                 key="profeta_data_input_m_panel")
                txt_biblico = st.text_area("Escrituras (Texto Fiel) - Sem abreviações", value=bib_padrao, height=200) 
                txt_historico = st.text_area("Análise (Histórica/Hipotética)", value=hist_padrao, height=150) 
                
                if st.form_submit_button(submit_label):
                    
                    if not evento_final:
                        st.session_state['status_message'] = ('error', "O Título do Evento é obrigatório.")
                        st.rerun() 

                    try:
                        novo_item = {
                            "id": item_editado['id'] if item_editado else str(uuid.uuid4()),
                            "parent_id": parent_id_final,
                            "data": data_final,
                            "evento": evento_final,
                            "historico": txt_historico,
                            "escritura": txt_biblico,
                            "profeta_data": txt_profeta_data
                        }
                        
                        if item_editado is not None:
                            idx = lista_eventos.index(item_editado)
                            lista_eventos[idx] = novo_item
                            st.session_state.edit_index = None
                            status_msg = "✅ Evento atualizado com sucesso!"
                        else:
                            lista_eventos.append(novo_item)
                            status_msg = "✅ Evento salvo com sucesso!"
                            
                        dados_app["eventos"] = lista_eventos
                        salvar_dados(dados_app)
                        
                        st.session_state['status_message'] = ('success', status_msg)
                        reset_edit_states() 
                        st.rerun()

                    except Exception as e:
                        st.session_state['status_message'] = ('error', f"❌ Falha ao salvar evento: {str(e)}")
                        st.rerun()
        
        # O botão para adicionar novo evento força o formulário a aparecer (limpando o modo edição)
        if st.session_state.edit_index is None:
            if st.button("➕ Adicionar Novo Evento/Título Manualmente"):
                st.session_state.edit_index = None
                st.session_state['control_panel_expanded'] = True
                st.rerun()

        st.markdown("---")
        
        # --- VISUALIZAÇÃO DA ÁRVORE DE CONTROLE (Edição/Exclusão) ---
        st.header("3. Gerenciamento de Eventos (Árvore)")
        st.write("Clique em 'Editar' para abrir o formulário acima.")
        
        # Itera sobre os Títulos Principais (parent_id=None) e seus filhos
        for principal_event in eventos_por_parent.get(None, []):
            
            # 1. Título Principal
            display_event_control(principal_event, admin_mode=admin_mode)
            
            # 2. Eventos Filhos em um bloco indentado
            if principal_event['id'] in eventos_por_parent:
                
                # Renderiza os filhos
                sorted_children = sorted(eventos_por_parent[principal_event['id']], key=lambda x: get_sort_key(x['data']), reverse=False)
                
                with st.expander(f"Conteúdo de: {principal_event['evento']}", expanded=False):
                    for child in sorted_children:
                        display_event_control(child, admin_mode=admin_mode)
                        
                        # Se houver sub-níveis (filho de um filho), não exibiremos a recursão aqui
                        # para manter a interface de controle mais simples e plana.
                        if child['id'] in eventos_por_parent:
                             st.caption(f"⚠️ O evento '{child['evento']}' tem subeventos (nível 3). Edite-os separadamente.")
        
        st.markdown("---")

# --- ÁREA DE PRÉ-VISUALIZAÇÃO (CORPO PRINCIPAL) ---

st.header("🖼️ Pré-Visualização Final do Cronograma")
st.caption("Esta é a visualização do usuário final (somente leitura). Use o Painel de Controle para fazer alterações.")
st.divider()

eventos_por_parent_preview = {}
for item in lista_eventos:
    parent_id = item.get('parent_id') or None
    if parent_id not in eventos_por_parent_preview:
        eventos_por_parent_preview[parent_id] = []
    eventos_por_parent_preview[parent_id].append(item)

# Renderiza a Pré-Visualização
render_preview_tree(lista_eventos, eventos_por_parent_preview)


# Rodapé
st.markdown("---")
st.caption(f"App v{VERSAO_APP} | Conteúdo v{VERSAO_CONTEUDO}")
