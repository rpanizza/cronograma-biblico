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

# Versão do Aplicativo (App) - Correção do SyntaxError: 'return' outside function
VERSAO_APP = "1.4.1" 
# Versão do Conteúdo (Cronologia)
VERSAO_CONTEUDO = "25.1208.13" # Incremento da versão do conteúdo devido à alteração no código

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
        # Trata casos como "Futuro" ou datas não numéricas
        if "futuro" in date_str_clean or "tribulação" in date_str_clean:
            return 999999 # Coloca profecias futuras no fim
        return 0 
    
    try: 
        year = int(match.group(1))
    except ValueError: 
        return 0 
    
    suffix = match.group(2)
    if suffix and ('a.c.' in suffix or 'ac' in suffix):
        return -year # Inverte a ordem para a.C.
    else:
        return year # Mantém a ordem para d.C.

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
    if not API_KEY: 
        return "⚠️ Erro: Chave API não configurada.", "", "", ""

    genai.configure(api_key=API_KEY)
    # Usando modelo atualizado gemini-2.5-flash
    model = genai.GenerativeModel('gemini-2.5-flash') 
    
    prompt = f"""
    Atue como assistente estrito de cronologia bíblica.
    Tópico: "{topico}"
    
    Sua tarefa é gerar QUATRO partes separadas por "|||":
    1. A data do evento (Ex: 959 a.C. ou 32 d.C. ou Futuro).
    2. UM ÚNICO EMOJI e o Título do Evento (Ex: ✨ A Dedicação do Primeiro Templo).
    3. Profeta e Data de Escrita (Ex: Livros dos Reis e Crônicas (Escrito c. 560–430 a.C.)).
    4. Referência e texto da escritura integralmente (Sem abreviações).
    5. Análise Histórica/Hipotética (Texto detalhado).
    
    FORMATO OBRIGATÓRIO: [DATA] ||| [EMOJI + TÍTULO] ||| [PROFETA E DATA] ||| [TEXTO BÍBLICO] ||| [ANÁLISE]
    """
    try:
        response = model.generate_content(prompt)
        texto = response.text.strip()
        
        # O formato agora tem 4 separadores '|||'
        if texto.count("|||") == 4:
            partes = texto.split("|||")
            data = partes[0].strip()
            evento_emoji = partes[1].strip()
            profeta_data = partes[2].strip()
            biblia = partes[3].strip()
            analise = partes[4].strip()
            
            # Limpa o emoji e o título para preencher o campo 'final_evento'
            return data, evento_emoji, profeta_data, biblia, analise
        else:
            # Retorna o texto completo como erro para o usuário verificar
            return "", "❓ Erro de Formato", f"Resultado da IA: {texto}", "", ""
    except Exception as e:
        return "", "❌ Erro de Conexão", f"Erro: {str(e)}", "", ""

# --- LÓGICA DE ESTADO E SAÍDA DE EDIÇÃO ---

def reset_edit_states():
    """Limpa todos os estados temporários de edição e adição."""
    for key in ['edit_index', 'temp_data', 'temp_profeta', 'temp_analise', 'temp_bib', 'temp_evento', 'show_add_form', 'ia_prompt']:
        if key in st.session_state:
            del st.session_state[key]
    if 'research_input' in st.session_state:
         del st.session_state['research_input']
    if 'confirm_exit' in st.session_state:
        del st.session_state['confirm_exit']

def has_unsaved_changes():
    """Verifica se há conteúdo sendo editado ou adicionado no formulário."""
    return (st.session_state.edit_index is not None or
            st.session_state.get('temp_data', '') or 
            st.session_state.get('temp_profeta', '') or 
            st.session_state.get('temp_analise', '') or 
            st.session_state.get('temp_bib', '') or
            st.session_state.get('temp_evento', '') or
            st.session_state.get('ia_prompt', '') or
            st.session_state.get('show_add_form', False))

# --- INICIALIZAÇÃO DE ESTADO E CSS ---
if 'edit_index' not in st.session_state: st.session_state['edit_index'] = None
if 'admin_pass_input' not in st.session_state: st.session_state['admin_pass_input'] = ""
if 'show_add_form' not in st.session_state: st.session_state['show_add_form'] = False
if 'confirm_exit' not in st.session_state: st.session_state['confirm_exit'] = False
if 'ia_prompt' not in st.session_state: st.session_state['ia_prompt'] = ""
if 'status_message' not in st.session_state: st.session_state['status_message'] = None


st.markdown("""
<style>
    @media (max-width: 600px) { h1 { font-size: 1.8rem !important; } }
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
    
    /* Linha do Tempo Vertical */
    .timeline-container {
        position: relative;
        padding-left: 10px;
        margin-left: 10px;
    }
    
    /* A linha vertical em si */
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

    /* Estilo para eventos na linha do tempo */
    .timeline-event-card {
        padding-left: 20px;
        margin-top: 10px;
        margin-bottom: 20px;
        position: relative;
    }
    
    /* Ponto na linha do tempo */
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

    /* Sobreescreve o padding do st.expander no modo timeline */
    .timeline-event-card > div[data-testid^="stExpander"] {
        padding: 0 !important;
    }
    
    /* Emojis para os detalhes */
    .detail-icon {
        font-size: 1.1em;
        margin-right: 5px;
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

# Exibe mensagens de status (sucesso/falha)
if st.session_state.get('status_message'):
    tipo, mensagem = st.session_state['status_message']
    if tipo == 'success':
        st.success(mensagem)
    elif tipo == 'error':
        st.error(mensagem)
    elif tipo == 'warning':
        st.warning(mensagem) # Adicionado para warnings da IA/UX
    st.session_state['status_message'] = None # Limpa após exibição

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

# --- BARRA LATERAL (ADMIN E SAÍDA) ---
with st.sidebar:
    st.header("⚙️ Ferramentas")
    
    if password_input and password_input != SENHA_CORRETA:
        st.error("⚠️ Senha incorreta. Acesso negado.")

    if admin_mode:
        st.success("✅ Modo Edição Ativo")
        st.divider()
        
        if st.button("🚪 Sair do Modo Edição", key='exit_admin_btn'):
            if has_unsaved_changes():
                st.session_state['confirm_exit'] = True
            else:
                st.session_state['admin_pass_input'] = '' 
                reset_edit_states()
        
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
    
    # 1. Recupera valores padrão ou temporários
    data_padrao = item_editado['data'] if item_editado else st.session_state.get('temp_data', '')
    evento_padrao = item_editado['evento'] if item_editado else st.session_state.get('temp_evento', '')
    profeta_padrao = item_editado.get('profeta_data', '') if item_editado else st.session_state.get('temp_profeta', '')
    hist_padrao = item_editado['historico'] if item_editado else st.session_state.get('temp_analise', '')
    bib_padrao = item_editado['escritura'] if item_editado else st.session_state.get('temp_bib', '')
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
    
    
    with st.expander(form_titulo, expanded=(item_editado is not None or st.session_state.get('show_add_form', False))):
        st.write("Insira o tópico para pesquisa da IA ou use o campo abaixo para o título final do evento.")
        
        # --- CAMPO DE PROMPT MAXIMIZADO ---
        prompt_ia_input = st.text_area(
            "Prompt para Pesquisa IA / Título do Evento", 
            key='ia_prompt_area', 
            value=st.session_state.get('ia_prompt', evento_padrao.split(' ', 1)[-1] if evento_padrao and evento_padrao[0] in '📜✨❓❌' else evento_padrao), # Tenta remover o emoji se for edição
            height=150
        )
            
        if st.button("✨ Pesquisar Cronologia (Fiel) com IA"):
            if prompt_ia_input:
                with st.spinner("Consultando escrituras e formatando dados..."):
                    data, evento_emoji, profeta_data, biblia, analise = consultar_gemini_cronologia(prompt_ia_input)
                    
                    if "Erro" in evento_emoji or "❓" in evento_emoji:
                        st.session_state['status_message'] = ('error', f"Falha na IA: {evento_emoji} | {profeta_data}")
                    else:
                        # Pré-preenche estados temporários
                        st.session_state['temp_data'] = data
                        st.session_state['temp_evento'] = evento_emoji
                        st.session_state['temp_profeta'] = profeta_data
                        st.session_state['temp_bib'] = biblia
                        st.session_state['temp_analise'] = analise
                        st.session_state['ia_prompt'] = prompt_ia_input # Mantém o prompt para reuso

                        st.session_state['status_message'] = ('success', "Dados da IA preenchidos! Por favor, revise e salve.")

            else:
                st.session_state['status_message'] = ('warning', "Digite um tópico para pesquisar no campo de interação.")
            st.rerun()
        
        st.markdown("---")
        
        with st.form("form_salvar"):
            
            # SELECTBOX PARA EVENTO PAI
            parent_selection = st.selectbox(
                "Escolha o Evento Pai (Título Principal/Capítulo)",
                options=[opt['evento'] for opt in eventos_principais_options],
                index=parent_default_index,
                key='select_parent'
            )
            parent_id_final = next(item['id'] for item in eventos_principais_options if item['evento'] == parent_selection)

            col_input1, col_input2 = st.columns([1, 2])
            with col_input1:
                # Usa valor temporário se adicionando
                data_final = st.text_input("Data (Ex: 959 a.C. ou Futuro)", key="in_data_final", value=data_padrao)
            with col_input2:
                # Usa valor temporário se adicionando
                evento_final = st.text_input("Título Final do Evento (Com Emoji)", value=evento_padrao, key="final_evento")
            
            # Usa valor temporário se adicionando
            txt_profeta_data = st.text_input("Profeta e Data de Escrita (Ex: Livros dos Reis...) ou Título do Capítulo", 
                                             value=profeta_padrao, 
                                             key="profeta_data_input")
            # Usa valor temporário se adicionando
            txt_biblico = st.text_area("Escrituras (Texto Fiel) - Sem abreviações", value=bib_padrao, height=200) 
            # Usa valor temporário se adicionando
            txt_historico = st.text_area("Análise (Histórica/Hipotética)", value=hist_padrao, height=150) 
            
            if st.form_submit_button(submit_label):
                
                # Validação mínima
                if not data_final or not evento_final:
                    st.session_state['status_message'] = ('error', "Data e Título são campos obrigatórios.")
                    # AQUI ESTAVA O ERRO! Substituí 'return' por 'st.rerun()'
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
                        # Modo Edição: Substitui
                        idx = lista_eventos.index(item_editado)
                        lista_eventos[idx] = novo_item
                        st.session_state.edit_index = None
                    else:
                        # Modo Adição: Adiciona
                        lista_eventos.append(novo_item)
                        
                    dados_app["eventos"] = lista_eventos
                    salvar_dados(dados_app)
                    
                    st.session_state['status_message'] = ('success', "✅ Evento salvo/atualizado com sucesso!")
                    # Limpa estados temporários
                    reset_edit_states()
                    st.session_state['show_add_form'] = False # Colapsa o formulário
                    st.rerun()

                except Exception as e:
                    st.session_state['status_message'] = ('error', f"❌ Falha ao salvar evento: {str(e)}")
                    st.rerun()

    st.divider()


# --- ÁREA DE VISUALIZAÇÃO (LINHA DO TEMPO) - Reposicionada para Visualização Imediata ---

def is_historical_analysis(data_str):
    """Determina se a análise deve ser Histórica ou Hipotética com base na data."""
    data_str_lower = data_str.lower()
    # Hipotético se contiver "futuro", "tribulação" ou não contiver um número (não cronológico)
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
    
    # O evento é o título com a data: "959 a.C. A Dedicação do Primeiro Templo"
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
                        break
                st.session_state['show_add_form'] = True
                st.rerun()

            with col_delete:
                if st.checkbox("Confirmar Exclusão", key=f"check_del_{item['id']}"):
                    if st.button("🗑️ Excluir permanentemente", key=f"del_{item['id']}"):
                        lista_eventos = [e for e in lista_eventos if e['id'] != item['id']]
                        dados_app["eventos"] = lista_eventos
                        salvar_dados(dados_app)
                        reset_edit_states()
                        st.rerun()
    
    st.markdown("</div>", unsafe_allow_html=True) # Fecha timeline-event-card

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
        
        # Envolve todos os eventos cronológicos na classe timeline-container
        st.markdown("<div class='timeline-container'>", unsafe_allow_html=True)
        
        for item in sorted_events:
            display_event(item, is_sub_event=True, admin_mode=admin_mode) 
            
            # Se houver sub-eventos, eles continuam aninhados (pode ser sub-sub-eventos)
            if item['id'] in events:
                render_event_tree(events, item['id']) 
        
        st.markdown("</div>", unsafe_allow_html=True)
        
st.divider()

if not lista_eventos:
    st.info("O cronograma está vazio. Faça login para começar.")
else:
    # 1. Itera sobre os Títulos Principais (parent_id=None)
    for principal_event in eventos_por_parent.get(None, []):
        
        # Renderiza o Título Principal (Capítulo I, II, III...)
        display_event(principal_event, is_sub_event=False, admin_mode=admin_mode)
        
        # 2. Renderiza Eventos Filhos (Cronológicos) deste Título Principal
        if principal_event['id'] in eventos_por_parent:
            render_event_tree(eventos_por_parent, principal_event['id'])
        
        st.markdown("<br>", unsafe_allow_html=True)

# Rodapé
st.markdown("---")
st.caption(f"App v{VERSAO_APP} | Conteúdo v{VERSAO_CONTEUDO}")
