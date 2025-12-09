import streamlit as st
import pandas as pd
from datetime import datetime

# --- Configurações Iniciais ---
st.set_page_config(layout="wide", page_title="Cronograma Bíblico Estilo Cartão")

# --- CSS NOVO LAYOUT (BASEADO NA IMAGEM ANEXADA) ---
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
    border-radius: 50%;
    position: relative;
    top: 5px; /* Ponto ligeiramente mais baixo */
    left: -22px; /* Ajuste para centralizar na linha */
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
    color: white; /* Ícone branco para contraste no ponto colorido */
}

/* Cores específicas para os pontos */
.point-purple { background-color: #A064A8; }
.point-pink { background-color: #E91E63; }
.point-teal { background-color: #00BCD4; }
.point-lavender { background-color: #D3B3E1; } /* Nova cor */

/* Estilo para o Cartão de Evento */
.event-card {
    border-radius: 8px;
    padding: 15px;
    margin-bottom: 25px;
    box-shadow: none; /* Remove a sombra forte do cartão */
    border: none;
    transition: all 0.3s ease-in-out;
}

/* Cores dos Cartões (Fundo Sólido Suave) */
.card-purple { background-color: #f0e6f6; } /* Fundo claro sem borda lateral */
.card-pink { background-color: #fce4ec; }
.card-teal { background-color: #e0f7fa; }
.card-lavender { background-color: #f7f2fa; }

/* Estilo para a Data - Alinhada à Esquerda e Destacada */
.event-date-col {
    font-size: 1.1em;
    font-weight: bold;
    color: #495057;
    text-align: right; /* Garante que a data fique próxima à linha */
    padding-right: 25px;
    margin-top: 5px; /* Alinha com o ponto */
}

/* Garante que o conteúdo do Streamlit se alinhe corretamente */
h3 { margin-top: 0px !important; }
</style>
"""
st.markdown(TIMELINE_CSS, unsafe_allow_html=True)


# --- Função de Dados (NOVA ESTRUTURA DE ID BASEADA EM DATA) ---
def criar_dados_cronograma():
    """Cria dados de exemplo com cores e IDs no formato: AAAA.MM.DD.V"""
    dados = [
        # Novo formato de ID (2025 A.C. é simulado como 0025)
        {
            "id_pai": "0025.00.00.1", "data_pai": "2025 A.C.", "evento_pai": "O Dilúvio Universal",
            "id_sub": None, "cor": "purple", "referencia": "Gênesis 6-9",
        },
        # Novo formato de ID (2011 D.C.)
        {
            "id_pai": "2011.03.00.1", "data_pai": "2011 D.C.", "evento_pai": "Agitação no Oriente Médio",
            "id_sub": None, "cor": "pink", "referencia": "Mateus 24:6-7",
        },
        # Sub-evento
        {
            "id_pai": "2011.03.00.1", "data_pai": None, "evento_pai": None, "id_sub": "2011.03.20.1",
            "data_sub": "Março 2011", "descricao_sub": "Guerra Civil Síria.",
            "profecia_sub": "Nações contra nações.", "analise_hist_sub": "Primavera Árabe.",
            "cor": "pink", "referencia": "Mateus 24:7",
        },
        # Futuro
        {
            "id_pai": "3000.01.01.1", "data_pai": "Futuro (Indefinido)", "evento_pai": "Reconstrução do Templo",
            "id_sub": None, "cor": "teal", "referencia": "Daniel 9:27",
        },
        {
            "id_pai": "3000.02.01.1", "data_pai": "Futuro (Breve)", "evento_pai": "Gogue e Magogue",
            "id_sub": None, "cor": "lavender", "referencia": "Ezequiel 38-39",
        },
    ]
    df_full = pd.DataFrame(dados)
    return df_full

# --- Estrutura Principal do Layout ---

df_full = criar_dados_cronograma()
# Ordena por ID Pai para garantir a cronologia baseada no novo ID
eventos_pai = df_full[df_full['evento_pai'].notna()].sort_values(by='id_pai', ascending=False)


# =========================================================
## 1. ⚙️ Painel de Administração (Barra Lateral)
# =========================================================

with st.sidebar:
    st.title("⚙️ Painel do Administrador")
    st.markdown("---")
    
    st.subheader("➕ Adicionar Novo Evento Principal")
    
    # OBS: O ID será gerado automaticamente na lógica real, aqui apenas inputamos a data
    novo_data_pai = st.text_input("Data do Evento (Ex: 2025 A.C.)", "")
    novo_evento_pai = st.text_input("Título do Evento Principal", "")
    novo_referencia = st.text_input("Referência Bíblica", "")
    novo_cor = st.selectbox("Cor de Destaque", ["purple", "pink", "teal", "lavender"])
    
    if st.button("Salvar Evento"):
        if novo_data_pai and novo_evento_pai:
            st.success(f"Simulação de salvamento: Evento '{novo_evento_pai}' adicionado.")
        else:
            st.error("Por favor, preencha a Data e o Título do Evento.")


# =========================================================
## 2. 📖 Timeline Visual (Corpo Principal)
# =========================================================

st.header("📖 Cronograma Bíblico Profético (Visual Estilo Cartão)")
st.markdown("---")

# Colunas: Coluna A (Data/Texto) | Coluna B (Visual/Ponto) | Coluna C (Cartão/Conteúdo)
# Proporção ajustada para o novo layout de 3 colunas, com a linha no centro
col_date, col_visual, col_content = st.columns([0.25, 0.05, 0.70])


## Lógica de Renderização

if eventos_pai.empty:
    with col_date:
        st.info("Cronograma vazio.")
    with col_visual:
        st.markdown('<div class="timeline-line" style="height: 100px;"></div>', unsafe_allow_html=True)
    with col_content:
        st.empty() 
else:
    for index, pai in eventos_pai.iterrows():
        cor = pai['cor']
        
        sub_eventos_presentes = df_full[
            (df_full['id_pai'] == pai['id_pai']) &
            (df_full['id_sub'].notna())
        ]
        
        # --- Coluna da DATA (Esquerda) ---
        with col_date:
            # Data destacada e alinhada à direita, próxima à linha
            st.markdown(f'<div class="event-date-col">{pai["data_pai"]}</div>', unsafe_allow_html=True)
            # Adiciona espaço para alinhar com o próximo ponto/cartão
            st.markdown('<div style="height: 110px;"></div>', unsafe_allow_html=True)
            
        # --- Coluna da LINHA (Centro) ---
        with col_visual:
            # Ponto de destaque (com o ícone ✝️)
            st.markdown(f'<div class="timeline-point point-{cor}"></div>', unsafe_allow_html=True)
            
            # A linha de conexão, exceto o último item
            if index < len(eventos_pai) - 1:
                st.markdown('<div class="timeline-line" style="height: 150px;"></div>', unsafe_allow_html=True)
            else:
                st.markdown('<div style="height: 50px;"></div>', unsafe_allow_html=True)
                
        # --- Coluna do CONTEÚDO (Cartão à Direita) ---
        with col_content:
            # Cartão principal com cor de fundo
            st.markdown(f'<div class="event-card card-{cor}">', unsafe_allow_html=True)
            
            st.markdown(f"### **{pai['evento_pai']}**") 
            st.markdown(f"**ID:** `{pai['id_pai']}` | *(Ref: {pai['referencia']})*")
            
            # Expansor para Sub-eventos
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
            
            # Espaço vertical para alinhar
            st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)

st.success("Fim do Cronograma Exibido.")
