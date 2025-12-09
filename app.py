import streamlit as st
import pandas as pd

# --- Configurações da Página ---
st.set_page_config(layout="wide", page_title="Cronograma Bíblico Profético - Timeline Visual")

# --- Função para Criar o DataFrame (Dados do Cronograma) ---
def criar_dados_cronograma():
    """Cria um DataFrame do Pandas com a estrutura de Eventos Pai e Sub-eventos."""
    dados = [
        # --- EVENTO PAI 1 ---
        {
            "id_pai": "EP001",
            "data_pai": "2025 A.C.",
            "evento_pai": "O Dilúvio Universal",
            "id_sub": None,
            "data_sub": None,
            "descricao_sub": None,
            "profecia_sub": None,
            "analise_hist_sub": None,
            "referencia": "Gênesis 6-9",
        },
        # --- EVENTO PAI 2 ---
        {
            "id_pai": "EP002",
            "data_pai": "2011 D.C.",
            "evento_pai": "Agitação no Oriente Médio",
            "id_sub": None,
            "data_sub": None,
            "descricao_sub": None,
            "profecia_sub": None,
            "analise_hist_sub": None,
            "referencia": "Mateus 24:6-7",
        },
        # --- SUB-EVENTOS do EP002 ---
        {
            "id_pai": "EP002",
            "data_pai": None,
            "evento_pai": None,
            "id_sub": "ES002-1",
            "data_sub": "Março 2011",
            "descricao_sub": "Início do conflito civil na Síria, escalando para uma guerra complexa com envolvimento regional.",
            "profecia_sub": "Onde há menção de 'nação se levantará contra nação', interpretado como conflitos intensos.",
            "analise_hist_sub": "A Primavera Árabe e a subsequente Guerra Civil Síria mudaram o equilíbrio geopolítico na região.",
            "referencia": "Mateus 24:7",
        },
        # --- EVENTO PAI 3 ---
        {
            "id_pai": "EP003",
            "data_pai": "Futuro (Indefinido)",
            "evento_pai": "Reconstrução do Templo em Jerusalém",
            "id_sub": None,
            "data_sub": None,
            "descricao_sub": None,
            "profecia_sub": None,
            "analise_hist_sub": None,
            "referencia": "Daniel 9:27, Apocalipse 11:1-2",
        },
    ]
    return pd.DataFrame(dados)

# --- Renderização da Timeline ---
st.title("📖 Timeline do Cronograma Bíblico Profético")
st.markdown("---")

# Carrega os dados
df = criar_dados_cronograma()

# Obtém uma lista única dos IDs e Eventos Pais, ordenados pela data (para a timeline)
eventos_pai = df[df['evento_pai'].notna()].sort_values(by='data_pai', ascending=False)

st.header("⏳ Eventos Principais")

# Colunas para a Timeline: Coluna A (Linha) | Coluna B (Conteúdo)
# A coluna A (Linha) será muito estreita para dar o efeito de destaque
col_line, col_content = st.columns([0.1, 0.9])

# Define o estilo CSS para o ponto destacado (bolha)
HIGHLIGHT_STYLE = """
<style>
.highlight-point {
    width: 20px;
    height: 20px;
    background-color: #007BFF; /* Cor Azul */
    border-radius: 50%;
    margin: 5px 0 5px 5px; /* Ajuste para centralizar o ponto */
    display: flex;
    justify-content: center;
    align-items: center;
    box-shadow: 0 0 10px rgba(0, 123, 255, 0.7); /* Efeito de brilho */
}
.dot-line {
    border-left: 2px dashed #ccc; /* Linha pontilhada sutil */
    height: 100px; /* Altura da linha entre os pontos */
    margin-left: 15px; /* Posição da linha */
}
</style>
"""
st.markdown(HIGHLIGHT_STYLE, unsafe_allow_html=True)


# Itera sobre cada Evento Pai para criar a estrutura da Timeline
for index, pai in eventos_pai.iterrows():
    # Encontra todos os sub-eventos relacionados a este Evento Pai
    sub_eventos = df[
        (df['id_pai'] == pai['id_pai']) &
        (df['id_sub'].notna())
    ]
    
    # --- 1. Coluna da Linha (Visual) ---
    with col_line:
        # Ponto Destacado (Bolha) para o evento
        st.markdown('<div class="highlight-point"></div>', unsafe_allow_html=True)
        
        # Linha pontilhada abaixo do ponto (Exceto para o último item, que não precisa de linha)
        if index < len(eventos_pai) - 1:
            st.markdown('<div class="dot-line"></div>', unsafe_allow_html=True)
            
    # --- 2. Coluna do Conteúdo (Texto) ---
    with col_content:
        # Cabeçalho do Evento Pai
        st.markdown(f"## 📅 **{pai['data_pai']}**")
        st.markdown(f"### **{pai['id_pai']}** | **{pai['evento_pai']}**")
        st.markdown(f"*(Referência Principal: {pai['referencia']})*")

        # Expansor para Sub-eventos
        if not sub_eventos.empty:
            with st.expander(f"➕ Detalhes e Sub-eventos de {pai['evento_pai']}"):
                for sub_index, sub in sub_eventos.iterrows():
                    st.markdown("---") # Separador para cada sub-evento
                    
                    st.markdown(f"#### ➡️ **{sub['data_sub']}**")
                    
                    st.markdown(f"""
                        * **ID de Identificação:** `{sub['id_sub']}`
                        * **Descrição do Sub-evento:** {sub['descricao_sub']}
                        * **Profecia Relacionada:** {sub['profecia_sub']}
                        * **Análise Histórica:** {sub['analise_hist_sub']}
                        * **Referência Bíblica:** {sub['referencia']}
                    """)
        else:
            st.info("Não há detalhes ou sub-eventos expandíveis para este marco principal.")
        
        # Espaço extra para alinhar com a linha pontilhada
        st.markdown("<br><br><br>", unsafe_allow_html=True)

st.markdown("---")
st.success("Fim do Cronograma Exibido.")
