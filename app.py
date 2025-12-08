import streamlit as st
import google.generativeai as genai
import json
import os

# --- CONFIGURAÇÃO INICIAL ---
st.set_page_config(page_title="Cronograma Dinâmico", layout="centered")

# Nome do arquivo onde os dados serão salvos
ARQUIVO_DADOS = 'cronograma.json'
VERSAO_ATUAL = "25.1207.2"

# Tenta pegar a chave API dos Segredos do Streamlit
API_KEY = st.secrets.get("GEMINI_API_KEY", "")

# --- FUNÇÕES DE BANCO DE DADOS ---
def carregar_dados():
    # Estrutura padrão caso o arquivo não exista
    dados_padrao = {
        "titulo": "📜 Cronograma Profético Dinâmico",
        "eventos": []
    }
    
    if not os.path.exists(ARQUIVO_DADOS):
        return dados_padrao
        
    with open(ARQUIVO_DADOS, 'r', encoding='utf-8') as f:
        try:
            conteudo = json.load(f)
            # Migração: Se o arquivo antigo era apenas uma lista, converte para o novo formato
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

# --- CARREGA DADOS ---
dados_app = carregar_dados()
lista_eventos = dados_app["eventos"]
titulo_atual = dados_app.get("titulo", "Cronograma Profético")

# --- INTERFACE DO USUÁRIO ---

# Exibe o título editável
st.title(titulo_atual)
st.markdown("Amplie os itens abaixo para ver os fatos históricos e as escrituras.")

# --- BARRA LATERAL (LOGIN E CONFIGURAÇÕES) ---
with st.sidebar:
    st.header("⚙️ Área do Editor")
    senha_input = st.text_input("Senha de Acesso", type="password")
    
    # SENHA (Alterar conforme necessidade)
    SENHA_CORRETA = "R$Masterkey01" 
    admin_mode = (senha_input == SENHA_CORRETA)
    
    if admin_mode:
        st.success("✅ Modo Edição Ativo")
        st.divider()
        
        # --- EDITOR DE TÍTULO ---
        st.subheader("Personalizar")
        novo_titulo = st.text_input("Título do Projeto", value=titulo_atual)
        if novo_titulo != titulo_atual:
            dados_app["titulo"] = novo_titulo
            salvar_dados(dados_app)
            st.rerun() # Recarrega a página para atualizar o título
            
    elif senha_input:
        st.error("Senha incorreta")
        
    st.divider()
    st.caption(f"Versão do Sistema: {VERSAO_ATUAL}")

# --- ÁREA DE CRIAÇÃO (ADMIN) ---
if admin_mode:
    with st.expander("➕ Adicionar Novo Evento", expanded=False):
        st.write("Preencha o tópico e use a IA para buscar o texto fiel.")
        
        col_input1, col_input2 = st.columns([1, 2])
        with col_input1:
            data_temp = st.text_input("Data (ex: 539 a.C.)", key="in_data")
        with col_input2:
            evento_temp = st.text_input("Nome do Evento", key="in_evento")
            
        if st.button("✨ Pesquisar com IA"):
            if evento_temp:
                with st.spinner("Consultando escrituras..."):
                    hist_ia, bib_ia = consultar_gemini(evento_temp)
                    st.session_state['temp_hist'] = hist_ia
                    st.session_state['temp_bib'] = bib_ia
            else:
                st.warning("Digite o nome do evento primeiro.")

        with st.form("form_salvar"):
            val_hist = st.session_state.get('temp_hist', "")
            val_bib = st.session_state.get('temp_bib', "")
            
            txt_historico = st.text_area("Fato Histórico", value=val_hist, height=100)
            txt_biblico = st.text_area("Texto das Escrituras (Fiel)", value=val_bib, height=150)
            
            if st.form_submit_button("💾 Salvar no Cronograma"):
                novo_item = {
                    "data": data_temp,
                    "evento": evento_temp,
                    "historico": txt_historico,
                    "escritura": txt_biblico
                }
                lista_eventos.append(novo_item)
                dados_app["eventos"] = lista_eventos # Atualiza a lista
                salvar_dados(dados_app) # Salva tudo
                st.success("Evento salvo!")
                st.session_state['temp_hist'] = ""
                st.session_state['temp_bib'] = ""
                st.rerun()

# --- ÁREA DE VISUALIZAÇÃO (LINHA DO TEMPO) ---
st.divider()

if not lista_eventos:
    st.info("O cronograma está vazio. Faça login para começar.")
else:
    for i, item in enumerate(lista_eventos):
        titulo_card = f"🗓️ **{item['data']}** — {item['evento']}"
        
        with st.expander(titulo_card):
            # Correção aplicada aqui: Usando aspas triplas para segurança
            st.markdown(f"""
            **Contexto Histórico:**
            {item['historico']}
            """)
            
            st.markdown("---")
            st.markdown("**📖 Escrituras:**")
            st.info(item['escritura'])
            
            if admin_mode:
                if st.button("🗑️ Excluir", key=f"del_{i}"):
                    lista_eventos.pop(i)
                    dados_app["eventos"] = lista_eventos
                    salvar_dados(dados_app)
                    st.rerun()

# Rodapé
st.markdown("---")
st.caption(f"Projeto Cronograma | Versão {VERSAO_ATUAL}")