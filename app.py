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

# Versão do Aplicativo (App) - Recriação do Módulo de IA com botão explícito
VERSAO_APP = "1.8.0" 
# Versão do Conteúdo (Cronologia)
VERSAO_CONTEUDO = "25.1208.18" 

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
        
        # Não precisa de st.rerun() dentro do callback, o botão já faz o rerun

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
    
    /* Título Principal (Capítulo) */
    .main-chapter-title {
        font-size: 1.5em;
        font-weight: bold;
        margin-top: 25px;
        margin-bottom: 15px;
        color: #004d40;
        border-bottom: 2px solid #004d40;
        padding-bottom: 5px;
    }
    
    /* Tamanho e hierarquia do texto no corpo */
    .detail-line b { font-size: 1.05em; color: #004d40; }
    .stAlert { font-size: 0.95em; }
    .stMarkdown p { font-size: 0.95em; }
    
    /* Linha do Tempo Vertical */
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

    /* Oculta completamente a seta de enter que tentamos colocar antes */
    .stTextArea label:after {
        content: '' !important;
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
    

# --- INTERFACE PRINCIPAL ---

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

st.caption("Toque nos títulos abaixo para expandir e ver os detalhes.")


# --- FERRAMENTA DE INTERAÇÃO E PRÉVIA DA IA ---
if admin_mode:
    with st.expander("🤖 Ferramenta de Pesquisa IA (Nova Versão)", expanded=False):
        
        st.write("Insira um tópico para interagir com o Gemini, refinando a pesquisa até obter a resposta desejada.")
        
        # 1. CAMPO DE PROMPT 
        prompt_ia_input = st.text_area(
            "Prompt para Pesquisa IA (Tópico)", 
            key='ia_prompt_area', 
            height=100
        )
        
        # 2. BOTÃO EXPLÍCITO DE PESQUISA
        if st.button("🔍 Iniciar Pesquisa Cronológica", key='run_ia_btn'):
             # Chama a função de pesquisa
            run_ia_search(st.session_state.ia_prompt_area)
            # O st.rerun() é chamado dentro de run_ia_search se necessário para atualizar o status/estado

        st.markdown("---")

        # 3. CAMPO DE RESULTADO BRUTO
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
        # Verifica se o resultado formatado existe (sinal de que 4 '|||' foram encontrados)
        is_ia_result_valid = ia_data is not None 
        
        # 4. BOTÃO MOSTRAR PRÉVIA (Desabilitado até ter resultado válido)
        if st.button("✨ Mostrar Prévia / Ocultar", key='toggle_preview_btn', disabled=not is_ia_result_valid):
            if is_ia_result_valid:
                # Inverte o estado da prévia
                st.session_state['show_ia_preview'] = not st.session_state.get('show_ia_preview', False)
            st.rerun()

        # --- PRÉVIA E SALVAMENTO DIRETO DA IA ---
        if is_ia_result_valid and st.session_state.get('show_ia_preview', False):
            
            # Campos necessários para salvar
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
            st.markdown(f"**Escrituras:**")
            st.info(f"_{biblia_ia}_")
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
                key='select_parent_ia'
            )
            parent_id_ia = next(item['id'] for item in eventos_principais_options if item['evento'] == parent_selection_ia)

            # 3. Botão de Salvar Direto da Prévia
            if st.button("💾 Salvar Evento da Prévia", key='save_ia_preview'):
                
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
                    
                    # Limpa os estados da IA e prévia
                    st.session_state['ia_response_text'] = None 
                    st.session_state['ia_raw_result'] = ""
                    st.session_state['show_ia_preview'] = False
                    st.session_state['ia_prompt_area'] = ""
                    
                    st.rerun()

                except Exception as e:
                    st.session_state['status_message'] = ('error', f"❌ Falha ao salvar evento da prévia: {str(e)}")
                    st.rerun()
        
        st.markdown("---")


# --- FORMULÁRIO DE ADIÇÃO/EDIÇÃO MANUAL (SEMPRE RETRAÍDO) ---
if admin_mode:
    
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

    # Criar lista de Eventos Principais
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
    
    # Formulário SEMPRE retraído, a menos que esteja em modo edição (edit_index is not None)
    form_expanded = item_editado is not None 

    with st.expander(form_titulo, expanded=form_expanded):
        st.write("Use este formulário apenas para **edição** de eventos existentes ou para adicionar dados **manualmente**, sem a ajuda da IA.")
        
        with st.form("form_salvar"):
            
            parent_selection = st.selectbox(
                "Escolha o Evento Pai (Título Principal/Capítulo)",
                options=[opt['evento'] for opt in eventos_principais_options],
                index=parent_default_index,
                key='select_parent_manual'
            )
            parent_id_final = next(item['id'] for item in eventos_principais_options if item['evento'] == parent_selection)

            col_input1, col_input2 = st.columns([1, 2])
            with col_input1:
                data_final = st.text_input("Data (Ex: 959 a.C. ou Futuro)", key="in_data_final_m", value=data_padrao)
            with col_input2:
                evento_final = st.text_input("Título Final do Evento (Com Emoji)", value=evento_padrao, key="final_evento_m")
            
            txt_profeta_data = st.text_input("Profeta e Data de Escrita (Ex: Livros dos Reis...) ou Título do Capítulo", 
                                             value=profeta_padrao, 
                                             key="profeta_data_input_m")
            txt_biblico = st.text_area("Escrituras (Texto Fiel) - Sem abreviações", value=bib_padrao, height=200) 
            txt_historico = st.text_area("Análise (Histórica/Hipotética)", value=hist_padrao, height=150) 
            
            if st.form_submit_button(submit_label):
                
                if not data_final or not evento_final:
                    st.session_state['status_message'] = ('error', "Data e Título são campos obrigatórios.")
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

    st.divider()


# --- ÁREA DE VISUALIZAÇÃO (LINHA DO TEMPO) ---

def is_historical_analysis(data_str):
    """Determina se a análise deve ser Histórica ou Hipotética com base na data."""
    data_str_lower = data_str.lower()
    if "futuro" in data_str_lower or "tribulação" in data_str_lower or not any(char.isdigit() for char in data_str):
        return False
    return True 


def display_event(item, is_sub_event=False, admin_mode=False):
    """Função recursiva para exibir eventos e sub-eventos."""
    global lista_eventos 
    
    # --- TÍTULO PRINCIPAL (CAPÍTULO) ---
    if item.get('parent_id') is None and not is_sub_event:
        st.markdown(f"<div class='main-chapter-title'>{item['evento']}</div>", unsafe_allow_html=True)
        return

    # --- EVENTOS CRONOLÓGICOS (LINHA DO TEMPO) ---
    
    st.markdown(f"<div class='timeline-event-card'>", unsafe_allow_html=True)
    
    titulo_card = f"**{item['data']}** {item['evento']}" 
    
    with st.expander(titulo_card):
        
        # 1. Profeta e Data
        profeta_data = item.get('profeta_data', 'Não informado')
        st.markdown(f"""
        <p class="detail-line">
            <span class="detail-icon">📅</span> 
            <b>Profeta e Data:</b> {profeta_data}
        </p>
        """, unsafe_allow_html=True)

        st.markdown("---")
        
        # 2. Escrituras (Texto Fiel)
        st.markdown(f"""
        <p class="detail-line">
            <span class="detail-icon">📖</span> 
            <b>Escrituras (ARA):</b>
        </p>
        """, unsafe_allow_html=True)
        st.info(f"_{item['escritura']}_") 
        
        st.markdown("---")

        # 3. Análise (Dinâmica)
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
        
        
        if admin_mode:
            st.markdown("---")
            col_edit, col_delete = st.columns([1, 1])
            
            if col_edit.button("✏️ Editar", key=f"edit_{item['id']}"):
                for i, evt in enumerate(lista_eventos):
                    if evt['id'] == item['id']:
                        st.session_state.edit_index = i
                        st.session_state['show_add_form'] = True 
                        break
                st.rerun()

            with col_delete:
                if st.checkbox("Confirmar Exclusão", key=f"check_del_{item['id']}"):
                    if st.button("🗑️ Excluir permanentemente", key=f"del_{item['id']}"):
                        lista_eventos = [e for e in lista_eventos if e['id'] != item['id']]
                        dados_app["eventos"] = lista_eventos
                        salvar_dados(dados_app)
                        reset_edit_states()
                        st.rerun()
    
    st.markdown("</div>", unsafe_allow_html=True)

# --- LÓGICA DE RENDERIZAÇÃO DA ÁRVORE ---

eventos_por_parent = {}
for item in lista_eventos:
    parent_id = item.get('parent_id') or None
    if parent_id not in eventos_por_parent:
        eventos_por_parent[parent_id] = []
    eventos_por_parent[parent_id].append(item)


def render_event_tree(events, parent_id):
    if parent_id in events:
        sorted_events = sorted(events[parent_id], key=lambda x: get_sort_key(x['data']), reverse=False)
        
        st.markdown("<div class='timeline-container'>", unsafe_allow_html=True)
        
        for item in sorted_events:
            display_event(item, is_sub_event=True, admin_mode=admin_mode) 
            
            if item['id'] in events:
                render_event_tree(events, item['id']) 
        
        st.markdown("</div>", unsafe_allow_html=True)
        
st.divider()

if not lista_eventos:
    st.info("O cronograma está vazio. Faça login para começar.")
else:
    # 1. Itera sobre os Títulos Principais (parent_id=None)
    for principal_event in eventos_por_parent.get(None, []):
        
        display_event(principal_event, is_sub_event=False, admin_mode=admin_mode)
        
        # 2. Renderiza Eventos Filhos (Cronológicos) deste Título Principal
        if principal_event['id'] in eventos_por_parent:
            render_event_tree(eventos_por_parent, principal_event['id'])
        
        st.markdown("<br>", unsafe_allow_html=True)

# Rodapé
st.markdown("---")
st.caption(f"App v{VERSAO_APP} | Conteúdo v{VERSAO_CONTEUDO}")
