import streamlit as st
import pandas as pd
from datetime import datetime

# --- Configurações Iniciais ---
st.set_page_config(layout="wide", page_title="Cronograma Bíblico Profético - Painel Admin")

# --- CSS para a Timeline Visual (Refinado para Cores e Layout) ---
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
    border: 3px solid #ffffff; /* Borda branca para destacar o ponto */
    border-radius: 50%;
    position: relative;
    top: -5px; 
    left: -22px; 
    box-shadow: 0 0 5px rgba(0, 0, 0, 0.2); /* Sutil sombra */
    z-index: 10; 
}

/* Cores específicas para os pontos */
.point-purple { background-color: #A064A8; }
.point-pink { background-color: #E91E63; }
.point-teal { background-color: #00BCD4; }

/* Estilo para o Cartão de Evento (Cores de Fundo) */
.event-card {
    border-radius: 8px;
    padding: 15px;
    margin-bottom: 25px;
    box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.1);
    border-left: 5px solid; /* Borda lateral para dar o toque de cor */
    margin-left: -15px; /* Puxa o card para perto da linha */
}

/* Cores dos Cartões */
.card-purple { background-color: #f0e6f6; border-left-color: #A064A8; }
.card-pink { background-color: #fce4ec; border-left-color: #E91E63; }
.card-teal { background-color: #e0f7fa; border-left-color: #00BCD4; }

/* Estilo para a Data */
.event-date {
    font-size: 1em;
    font-weight: bold;
    color: #495057;
    margin-bottom: 5px;
}

/* Hack para melhorar o layout dos títulos Streamlit */
h3 { margin-top: 0px !important; }
</style>
"""
st.markdown(TIMELINE_CSS, unsafe_allow_html=True)


# --- Função de Dados (Adaptada para Cores) ---
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
        # Sub-evento
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
    # Filtra e ordena apenas os Eventos Pai para a Timeline de Nível Superior
    df_full = pd.DataFrame(dados)
    return df_full

# --- Estrutura Principal do Layout ---

df_full = criar_dados_cronograma()
eventos_pai = df_full[df_full['evento_pai'].notna()].sort_values(by='data_pai', ascending=False)


## 1. Painel de Administração (Lado Esquerdo)

# Cria o painel lateral para a entrada de dados (Simulação de um painel de administração)
with st.sidebar:
    st.title("⚙️ Painel do Administrador")
    st.markdown("---")
    
    st.subheader("➕ Adicionar Novo Evento Principal")
    
    # Campos de entrada de dados
    novo_data_pai = st.text_input("Data do Evento (Ex: 2025 A.C. ou 2011 D.C.)", "")
    novo_evento_pai = st.text_input("Título do Evento Principal", "")
    novo_referencia = st.text_input("Referência Bíblica", "")
    novo_cor = st.selectbox("Cor de Destaque", ["purple", "pink", "teal", "outra..."])
    
    # Um botão que, na implementação real, adicionaria o evento ao DataFrame/Banco de Dados
    if st.button("Salvar Evento"):
        if novo_data_pai and novo_evento_pai:
            st.success(f"Simulação de salvamento: Evento '{novo_evento_pai}' adicionado.")
            # A lógica real de atualização do DataFrame e recarregamento iria aqui
        else:
            st.error("Por favor, preencha a Data e o Título do Evento.")
            
    st.markdown("---")
    st.info("Aqui também ficariam os campos para editar ou excluir eventos.")


## 2. Timeline Visual (Lado Direito)

# Título da Timeline
st.header("📖 Timeline do Cronograma Bíblico Profético")
st.markdown("A história profética e os eventos estão representados abaixo.")
st.markdown("---")

# Colunas para a Timeline: Coluna A (Ponto/Linha) | Coluna B (Conteúdo/Cartão)
col_visual, col_content = st.columns([0.05, 0.95])


# Renderização da Timeline
for index, pai in eventos_pai.iterrows():
    cor = pai['cor']
    
    # Encontra os sub-eventos
    sub_eventos = df_full[
        (df_full['id_pai'] == pai['id_pai']) &
        (df_full['id_sub'].notna())
    ]
    
    # --- Coluna da Linha (Visual) ---
    with col_visual:
        # Ponto de destaque com a cor específica
        st.markdown(f'<div class="timeline-point point-{cor}"></div>', unsafe_allow_html=True)
        
        # A linha de conexão, exceto o último item
        if index < len(eventos_pai) - 1:
            st.markdown('<div class="timeline-line" style="height: 150px;"></div>', unsafe_allow_html=True)
        else:
            st.markdown('<div style="height: 50px;"></div>', unsafe_allow_html=True)
            
    # --- Coluna do Conteúdo (Cartão de Evento) ---
    with col_content:
        # Cartão principal com a cor de fundo e borda lateral
        st.markdown(f'<div class="event-card card-{cor}">', unsafe_allow_html=True)
        
        # Data e Título
        st.markdown(f'<div class="event-date">{pai["data_pai"]}</div>', unsafe_allow_html=True)
        st.markdown(f"### **{pai['evento_pai']}**") # Título principal
        st.markdown(f"**ID:** `{pai['id_pai']}` | *(Ref: {pai['referencia']})*")
        
        # Expansor para Sub-eventos
        if not sub_eventos.empty:
            # Note: O Streamlit não permite CSS direto no st.expander, mas o card já está colorido
            with st.expander(f"➕ Mostrar detalhes e sub-eventos"):
                for sub_index, sub in sub_eventos.iterrows():
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
        
        # Espaço vertical para alinhamento
        st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)

st.success("Fim do Cronograma Exibido.")
