import streamlit as st
import google.generativeai as genai
import json
import os

# --- CONFIGURAÇÃO INICIAL ---
st.set_page_config(page_title="Cronograma das Escrituras", layout="centered")

# Nome do arquivo onde os dados serão salvos
ARQUIVO_DADOS = 'cronograma.json'

# Tenta pegar a chave API dos "Segredos" do Streamlit (para quando estiver online)
# Ou usa uma string vazia se estiver rodando local sem configurar ainda
API_KEY = st.secrets.get("GEMINI_API_KEY", "") 

# --- FUNÇÕES DE BANCO DE DADOS (SIMPLES) ---
def carregar_dados():
    if not os.path.exists(ARQUIVO_DADOS):
        return []
    with open(ARQUIVO_DADOS, 'r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def salvar_dados(dados):
    with open(ARQUIVO_DADOS, 'w', encoding='utf-8') as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)

# --- INTEGRAÇÃO COM GEMINI (IA) ---
def consultar_gemini(topico):
    if not API_KEY:
        return "⚠️ Erro: Chave API não configurada.", "Configure a chave no Streamlit Secrets."
    
    try:
        genai.configure(api_key=API_KEY)
        # Usando modelo flash para resposta rápida e econômica
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # PROMPT ESTRITO CONFORME SUA REGRA
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

# --- INTERFACE DO USUÁRIO ---

st.title("📜 Cronograma Profético Dinâmico")
st.markdown("Amplie os itens abaixo para ver os fatos históricos e as escrituras.")

# --- BARRA LATERAL (LOGIN) ---
with st.sidebar:
    st.header("Área do Editor")
    senha_input = st.text_input("Senha de Acesso", type="password")
    
    # DEFINE SUA SENHA AQUI (Simples)
    SENHA_CORRETA = "1234" 
    admin_mode = (senha_input == SENHA_CORRETA)
    
    if admin_mode:
        st.success("✅ Modo Edição Ativo")
    elif senha_input:
        st.error("Senha incorreta")
        
    st.divider()
    st.caption("Versão do Sistema: 25.1206.3")

# Carrega os dados existentes
lista_eventos = carregar_dados()

# --- ÁREA DE CRIAÇÃO (SÓ APARECE SE TIVER A SENHA) ---
if admin_mode:
    with st.expander("➕ Adicionar Novo Evento (Clique Aqui)", expanded=True):
        st.write("Preencha o tópico e use a IA para buscar o texto fiel.")
        
        # Passo 1: Definir o tópico para pesquisa
        col_input1, col_input2 = st.columns([1, 2])
        with col_input1:
            data_temp = st.text_input("Data (ex: 539 a.C.)", key="in_data")
        with col_input2:
            evento_temp = st.text_input("Nome do Evento", key="in_evento")
            
        # Botão para chamar o Gemini
        if st.button("✨ Pesquisar Texto Fiel com Gemini"):
            if evento_temp:
                with st.spinner("Consultando escrituras..."):
                    hist_ia, bib_ia = consultar_gemini(evento_temp)
                    # Salva no estado temporário para preencher o formulário abaixo
                    st.session_state['temp_hist'] = hist_ia
                    st.session_state['temp_bib'] = bib_ia
            else:
                st.warning("Digite o nome do evento primeiro.")

        # Passo 2: Formulário final de salvamento
        with st.form("form_salvar"):
            st.markdown("### Revisar e Salvar")
            # Usa os valores trazidos pela IA (ou vazio se não tiver ainda)
            val_hist = st.session_state.get('temp_hist', "")
            val_bib = st.session_state.get('temp_bib', "")
            
            # Campos de texto editáveis
            txt_historico = st.text_area("Fato Histórico", value=val_hist, height=100)
            txt_biblico = st.text_area("Texto das Escrituras (Fiel)", value=val_bib, height=150)
            
            submit = st.form_submit_button("💾 Salvar no Cronograma")
            
            if submit:
                novo_item = {
                    "data": data_temp,
                    "evento": evento_temp,
                    "historico": txt_historico,
                    "escritura": txt_biblico
                }
                lista_eventos.append(novo_item)
                salvar_dados(lista_eventos)
                st.success(f"Evento '{evento_temp}' salvo!")
                # Limpa os campos da IA
                st.session_state['temp_hist'] = ""
                st.session_state['temp_bib'] = ""
                st.rerun()

# --- ÁREA DE VISUALIZAÇÃO (LINHA DO TEMPO) ---
st.divider()

if not lista_eventos:
    st.info("O cronograma está vazio. Faça login para adicionar o primeiro evento.")
else:
    # Exibe os itens (pode-se adicionar lógica de ordenação aqui se quiser)
    for i, item in enumerate(lista_eventos):
        # O cabeçalho do acordeão
        titulo = f"🗓️ **{item['data']}** — {item['evento']}"
        
        with st.expander(titulo):
            # Conteúdo interno (Expandido)
            st.markdown(f"**Contexto Histórico:**\n{item['historico']}")
            st.markdown("---")
            st.markdown(f"**📖 Escrituras:**")
            # Caixa de destaque para a escritura
            st.info(item['escritura'])
            
            # Botão de excluir (Só para admin)
            if admin_mode:
                if st.button("🗑️ Excluir este item", key=f"del_{i}"):
                    lista_eventos.pop(i)
                    salvar_dados(lista_eventos)
                    st.rerun()
