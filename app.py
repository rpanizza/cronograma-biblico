import streamlit as st
import pandas as pd

# --- Configurações Iniciais ---
# Define o layout como "wide" para telas grandes, mas o CSS fará a adaptação
st.set_page_config(layout="wide", page_title="Cronograma Bíblico Responsivo")

# --- CSS OTIMIZADO PARA RESPONSIVIDADE ---
# O uso de porcentagens e margens automáticas ajuda na adaptação.
TIMELINE_CSS = """
<style>
/* Estilo para a linha vertical */
.timeline-line {
    border-left: 3px solid #ccc; /* Linha cinza clara e sutil */
    margin-left: 10px;
    height: 100%;
    padding-left: 10px;
}

/* Base do Ponto de Destaque */
.timeline-point {
    width: 20px;
    height: 20px;
    border: 3px solid #ffffff; 
    border-radius: 50%;
    position: relative;
    top: -5px; 
    left: -22px; 
    box-shadow: 0 0 5px rgba(0, 0, 0, 0.2); 
    z-index: 10; 
}

/* Cores específicas para os pontos (mantidas as cores para consistência) */
.point-purple { background-color: #A064A8; }
.point-pink { background-color: #E91E63; }
.point-teal { background-color: #00BCD4; }

/* Estilo para o Cartão de Evento */
.event-card {
    border-radius: 8px;
    padding: 15px;
    margin-bottom: 25px;
    box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.1);
    border-left: 5px solid; 
    margin-left: -15px; 
    /* Adiciona transição para suavizar mudanças de layout (opcional) */
    transition: all 0.3s ease-in-out;
}

/* Cores dos Cartões */
.card-purple { background-color: #f0e6f6; border-left-color: #A064A8; }
.card-pink { background-color: #fce4ec; border-left-color: #E91E63; }
.card-teal { background-color: #e0f7fa; border-left-color: #00BCD4; }

/* REGRAS DE RESPONSIVIDADE (MEDIA QUERIES) */
@media (max-width: 600px) {
    /* Em telas muito pequenas, o conteúdo pode ocupar 100% da largura */
    .stApp > div {
        padding-left: 1rem;
        padding-right: 1rem;
    }
    /* Oculta a linha e o ponto (opcional, mas comum para simplicidade em telas pequenas) */
    /* .timeline-point, .timeline-line { display: none !important; } */
    
    /* Se a linha for mantida, garante que o cartão não fique muito deslocado */
    .event-card {
        margin-left: 0px; 
        padding: 10px; 
    }
}

/* Hack para melhorar o layout dos títulos Streamlit */
h3 { margin-top: 0px !important; }
</style>
"""
st.markdown(TIMELINE_CSS, unsafe_allow_html=True)


# --- Função de Dados (Mantida a estrutura) ---
def criar_dados_cronograma():
    """Cria dados de exemplo com cores para o visual do painel."""
    dados = [
        {
            "id_pai": "EP001", "data_pai": "2025 A.C.", "evento_pai": "O Dilúvio Universal",
            "id_sub": None, "cor": "purple", "referencia": "Gênesis 6-9",
        },
        {
            "id_pai": "EP002", "data_pai": "2011 D.C.", "evento_pai": "Agitação no Oriente Médio",
            "id_sub": None, "cor": "pink", "referencia": "Mateus 24:6-7",
        },
        {
            "id_pai": "EP002", "data_pai": None, "evento_pai": None, "id_sub": "ES002-1",
            "data_sub": "Março 2011", "descricao_sub": "Guerra Civil Síria.",
            "profecia_sub": "Nações contra nações.", "analise_hist_sub": "Primavera Árabe.",
            "cor": "pink", "referencia": "Mateus 24:7",
        },
        {
            "id_pai": "EP003", "data_pai": "Futuro", "evento_pai": "Reconstrução do Templo",
            "id_sub": None, "cor": "teal", "referencia": "Daniel 9:27",
        },
        {
            "id_pai": "EP004", "data_pai": "Futuro (Breve)", "evento_pai": "Gogue e Magogue",
            "id_sub": None, "cor": "purple", "referencia": "Ezequiel 38-39",
        },
    ]
    df_full = pd.DataFrame(dados)
    return df_full

# --- Estrutura Principal do Layout ---

df_full = criar_dados_cronograma()
eventos_pai = df_full[df_full['evento_pai'].notna()].sort_values(by='data_pai', ascending=False)


# =========================================================
## 1. ⚙️ Painel de Administração (Barra Lateral)
# A barra lateral é naturalmente responsiva no Streamlit: ela se oculta e pode ser aberta
# com um toque (ou clique) em dispositivos móveis.
# =========================================================

with st.sidebar:
    st.title("⚙️ Painel do Administrador")
    st.markdown("---")
    
    st.subheader("➕ Adicionar Novo Evento Principal")
    
    novo_data_pai = st.text_input("Data do Evento (Ex: 2025 A.C. ou 2011 D.C.)", "")
    novo_evento_pai = st.text_input("Título do Evento Principal", "")
    novo_referencia = st.text_input("Referência Bíblica", "")
    novo_cor = st.selectbox("Cor de Destaque", ["purple", "pink", "teal", "outra..."])
    
    if st.button("Salvar Evento"):
        if novo_data_pai and novo_evento_pai:
            st.success(f"Simulação de salvamento: Evento '{novo_evento_pai}' adicionado.")
        else:
            st.error("Por favor, preencha a Data e o Título do Evento.")


# =========================================================
## 2. 📖 Timeline Visual (Corpo Principal)
# =========================================================

st.header("📖 Timeline do Cronograma Bíblico Profético")
st.markdown("A história profética e os eventos estão representados abaixo.")
st.markdown("---")

# Colunas para a Timeline: Coluna A (Ponto/Linha) | Coluna B (Conteúdo/Cartão)
# Esta proporção ([0.05, 0.95]) é mantida, mas a largura total se adapta à tela.
col_visual, col_content = st.columns([0.05, 0.95])


# Renderização da Timeline
