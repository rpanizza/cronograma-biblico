import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

# --- Configurações Iniciais ---
st.set_page_config(layout="wide", page_title="Cronograma Bíblico Persistente")

# Nome do arquivo de dados
DATA_FILE = "cronograma_data.json"

# --- Funções de Persistência de Dados ---

def carregar_dados():
    """Carrega dados do arquivo JSON ou retorna dados vazios/exemplo se o arquivo não existir."""
    if os.path.exists(DATA_FILE) and os.path.getsize(DATA_FILE) > 0:
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            st.warning("Arquivo de dados JSON corrompido. Carregando dados de exemplo.")
            return criar_dados_exemplo()
    return criar_dados_exemplo()

def salvar_dados(dados):
    """Salva a lista de dados no arquivo JSON."""
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)
    # Recarrega a página para atualizar a visualização
    st.rerun()

def criar_dados_exemplo():
    """Cria dados de exemplo para inicialização."""
    return [
        {
            "id_pai": "0025.00.00.1", "data_pai": "2025 A.C.", "evento_pai": "O Dilúvio Universal",
            "id_sub": None, "cor": "purple", "referencia": "Gênesis 6-9",
        },
        {
            "id_pai": "2011.03.00.1", "data_pai": "2011 D.C.", "evento_pai": "Agitação no Oriente Médio",
            "id_sub": None, "cor": "pink", "referencia": "Mateus 24:6-7",
        },
        {
            "id_pai": "2011.03.00.1", "data_pai": None, "evento_pai": None, "id_sub": "2011.03.20.1",
            "data_sub": "Março 2011", "descricao_sub": "Guerra Civil Síria.",
            "profecia_sub": "Nações contra nações.", "analise_hist_sub": "Primavera Árabe.",
            "cor": "pink", "referencia": "Mateus 24:7",
        },
        {
            "id_pai": "3000.01.01.1", "data_pai": "Futuro (Indefinido)", "evento_pai": "Reconstrução do Templo",
            "id_sub": None, "cor": "teal", "referencia": "Daniel 9:27",
        },
        {
            "id_pai": "3000.02.01.1", "data_pai": "Futuro (Breve)", "evento_pai": "Gogue e Magogue",
            "id_sub": None, "cor": "lavender", "referencia": "Ezequiel 38-39",
        }
    ]

def gerar_novo_id(data_str):
    """Gera um ID único baseado na data e na versão atual."""
    try:
        # Tenta formatar a data, usa 00 se falhar (para datas como "Futuro")
        if data_str.lower() in ["futuro", "indefinido", "2025 a.c."]:
             prefix = f"3999.12.31." # Coloca datas futuras no fim
        elif "a.c." in data_str.lower():
            # Simula datas A.C. como prefixo baixo
            ano = int(data_str.lower().replace(" a.c.", "").strip())
            prefix = f"{ano:04d}.00.00." 
        else:
            # Assume AAAA ou AAAA/MM/DD
            if "/" in data_str:
                dt = datetime.strptime(data_str, "%Y/%m/%d")
            elif len(data_str) == 4 and data_str.isdigit():
                dt = datetime.strptime(data_str, "%Y")
            else:
                dt = datetime.strptime(data_str, "%Y")
            prefix = dt.strftime("%Y.%m.%d.")
    except ValueError:
        prefix = "9999.00.00." # ID alto para dados inválidos
        
    # Versão: Encontra a próxima versão válida
    df = pd.DataFrame(st.session_state.cronograma_data)
    if not df.empty:
        max_id = df[df['id_pai'].str.startswith(prefix)].apply(lambda x: x['id_pai'].split('.')[-1], axis=1).astype(int).max()
        nova_versao = (max_id if pd.notna(max_id) else 0) + 1
    else:
        nova_versao = 1
        
    return prefix + str(nova_versao)


# --- Inicialização do Estado (Correção do SyntaxError implícito aqui) ---
if 'cronograma_data' not in st.session_state:
    st.session_state.cronograma_data = carregar_dados()

df_full = pd.DataFrame(st.session_state.cronograma_data)
eventos_pai = df_full[df_full['evento_pai'].notna()].sort_values(by='id_pai', ascending=False)

# --------------------------------------------------------------------------
# ... (O restante do código CSS e renderização da Timeline, mantido) ...
# --------------------------------------------------------------------------

TIMELINE_CSS = """
<style>
/* ------------------------------------- */
/* --- NOVO ESTILO: BOLINHAS PONTILHADAS --- */
/* ------------------------------------- */

/* Ponto de Destaque (Principal) */
.timeline-point {
    width: 20px;
    height: 20px;
    border-radius: 50%;
    position: relative;
    top: 5px; 
    left: -22px; 
    box-shadow: 0 0 5px rgba(0, 0, 0, 0.2); 
    z-index: 10;
    
    display: flex;
    justify-content: center;
    align-items: center;
}

/* Pseudo-elemento para o ÍCONE (mantido) */
.timeline-point::after {
    content: "✝️"; 
    font-size: 10px; 
    line-height: 1; 
    color: white; 
}

/* --- Bolinha Menor (Conector) --- */
.small-dot {
    width: 6px;
    height: 6px;
    background-color: #ccc; 
    border-radius: 50%;
    margin: 5px 0 5px 12px; 
    box-shadow: 0 0 2px rgba(0, 0, 0, 0.1);
}

/* --- Container da Linha Pontilhada --- */
.dot-line-container {
    height: 150px; 
    display: flex;
    flex-direction: column;
    justify-content: space-evenly; 
    align-items: center;
    padding-left: 20px; 
}
/* ------------------------------------- */


/* Cores (Mantidas) */
.point-purple { background-color: #A064A8; }
.point-pink { background-color: #E91E63; }
.point-teal { background-color: #00BCD4; }
.point-lavender { background-color: #D3B3E1; }

/* Estilos de Cartão (Mantidos) */
.event-card {
    border-radius: 8px;
    padding: 15px;
    margin-bottom: 25px;
    box-shadow: none; 
    border: none;
    transition: all 0.3s ease-in-out;
}
.card-purple { background-color: #f0e6f6; } 
.card-pink { background-color: #fce4ec; }
.card-teal { background-color: #e0f7fa; }
.card-lavender { background-color: #f7f2fa; }

/* Estilo para a Data */
.event-date-col {
    font-size: 1.1em;
    font-weight: bold;
    color: #495057;
    text-align: right; 
    padding-right: 25px;
    margin-top: 5px; 
}

h3 { margin-top: 0px !important; }
</style>
"""
st.markdown(TIMELINE_CSS, unsafe_allow_html=True)


# --- Função Auxiliar: Gera as Bolinhas Menores ---
def renderizar_bolinhas_menores(num_bolinhas=4):
    """Gera o HTML para a linha pontilhada de bolhas."""
    bolhas_html = '<div class="dot-line-container">'
    for _ in range(num_bolinhas):
        bolhas_html += '<div class="small-dot"></div>'
    bolhas_html += '</div>'
    return bolhas_html


# =========================================================
## 1. ⚙️ Painel de Administração (Barra Lateral)
# =========================================================
with st.sidebar:
    st.title("⚙️ Painel do Administrador")
    st.markdown("---")
    
    st.subheader("➕ Adicionar Novo Evento Principal")
    
    novo_data_pai = st.text_input("Data do Evento (Ex: 2025 D.C. ou Futuro)", key="input_data")
    novo_evento_pai = st.text_input("Título do Evento Principal", key="input_titulo")
    novo_referencia = st.text_input("Referência Bíblica", key="input_ref")
    novo_cor = st.selectbox("Cor de Destaque", ["purple", "pink", "teal", "lavender"], key="input_cor")
    
    if st.button("Salvar Evento"):
        if novo_data_pai and novo_evento_pai:
            novo_id = gerar_novo_id(novo_data_pai)
            
            novo_evento = {
                "id_pai": novo_id, 
                "data_pai": novo_data_pai, 
                "evento_pai": novo_evento_pai,
                "id_sub": None, 
                "cor": novo_cor, 
                "referencia": novo_referencia,
            }
            
            st.session_state.cronograma_data.append(novo_evento)
            salvar_dados(st.session_state.cronograma_data)
            st.success(f"Evento '{novo_evento_pai}' adicionado com ID: {novo_id}")
            # A função salvar_dados já chama st.rerun()
        else:
            st.error("Por favor, preencha a Data e o Título do Evento.")


# =========================================================
## 2. 📖 Timeline Visual (Corpo Principal)
# =========================================================

st.header("📖 Cronograma Bíblico Pontilhado com Bolhas")
st.markdown("---")

col_date, col_visual, col_content = st.columns([0.25, 0.05, 0.70])


## Lógica de Renderização

if eventos_pai.empty:
    with col_date:
        st.info("Cronograma vazio.")
    with col_visual:
        st.markdown('<div style="height: 100px;"></div>', unsafe_allow_html=True) 
    with col_content:
        st.empty() 
else:
    for index, pai in eventos_pai.iterrows():
        cor = pai['cor']
        
        # Filtra os sub-eventos
        sub_eventos_presentes = df_full[
            (df_full['id_pai'] == pai['id_pai']) &
            (df_full['id_sub'].notna())
        ]
        
        # --- Coluna da DATA (Esquerda) ---
        with col_date:
            st.markdown(f'<div class="event-date-col">{pai["data_pai"]}</div>', unsafe_allow_html=True)
            st.markdown('<div style="height: 110px;"></div>', unsafe_allow_html=True)
            
        # --- Coluna da LINHA (Centro) ---
        with col_visual:
            st.markdown(f'<div class="timeline-point point-{cor}"></div>', unsafe_allow_html=True)
            
            if index < len(eventos_pai) - 1:
                st.markdown(renderizar_bolinhas_menores(), unsafe_allow_html=True)
            else:
                st.markdown('<div style="height: 50px;"></div>', unsafe_allow_html=True)
                
        # --- Coluna do CONTEÚDO (Cartão à Direita) ---
        with col_content:
            st.markdown(f'<div class="event-card card-{cor}">', unsafe_allow_html=True)
            
            st.markdown(f"### **{pai['evento_pai']}**") 
            st.markdown(f"**ID:** `{pai['id_pai']}` | *(Ref: {pai['referencia']})*")
            
            if not sub_eventos_presentes.empty:
                with st.expander(f"➕ Mostrar detalhes e sub-eventos"):
                    for sub_index, sub in sub_eventos_presentes.iterrows():
                        st.markdown("---") 
                        st.markdown(f"##### ➡️ **{sub['data_sub']}**")
                        st.markdown(f"""
                            * **ID de Identificação:** `{sub['id_sub']}`
                            * **Descrição:** {sub['descricao_sub']}
                            * **Profecia Relacionada:** {sub['profecia_sub']}
                            * **Análise Histórica:** {sub['analise_hist_sub']}
                            * **Referência Bíblica:** {sub['referencia']}
                        """)
            else:
                st.markdown("*Este é um marco principal sem sub-eventos detalhados.*")
                
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)

st.success("Fim do Cronograma Exibido.")
