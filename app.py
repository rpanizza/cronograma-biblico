import streamlit as st
import pandas as pd

# --- Configurações Iniciais ---
st.set_page_config(layout="wide", page_title="Cronograma Bíblico Responsivo com Ícones")

# --- CSS OTIMIZADO (COM ÍCONES) ---
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
    
    /* CENTRALIZAÇÃO DO ÍCONE */
    display: flex;
    justify-content: center;
    align-items: center;
}

/* Pseudo-elemento para o ÍCONE dentro da bolinha */
.timeline-point::after {
    content: "✝️"; /* Ícone padrão (pode ser alterado para ⭐ ou 📜) */
    font-size: 10px; /* Tamanho pequeno para caber */
    line-height: 1; /* Garante que o ícone fique centralizado */
}

/* Cores específicas para os pontos */
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
    transition: all 0.3s ease-in-out;
}

/* Cores dos Cartões */
.card-purple { background-color: #f0e6f6; border-left-color: #A064A8; }
.card-pink { background-color: #fce4ec; border-left-color: #E91E63; }
.card-teal { background-color: #e0f7fa; border-left-color: #00BCD4; }

/* REGRAS DE RESPONSIVIDADE (MEDIA QUERIES) */
@media (max-width: 600px) {
    .event-card {
        margin-left: 0px; 
        padding: 10px; 
    }
}

h3 { margin-top: 0px !important; }
</style>
"""
st.markdown(TIMELINE_CSS, unsafe_allow_html=True)


# --- Função de Dados (Mantida a estrutura) ---
def criar_dados_cronograma():
    """Cria dados de exemplo com cores.
    # OBSERVAÇÃO: PARA TESTAR SEM EVENTOS, RETORNE 'pd.DataFrame([])'
    """
    dados = [
        {
            "id_pai": "EP001", "data_pai": "2025 A.C.", "evento_pai": "O Dilúvio Universal",
            "id_sub": None, "cor": "purple", "referencia": "Gênesis 6-9",
        },
        {
            "id_pai": "EP002", "data_pai": "2011 D.C.", "evento_pai": "Agitação no Oriente Médio",
            "id_sub": None, "cor": "pink", "referencia": "Mateus 24:6-7",
        },
    ]
    df_full = pd.DataFrame(dados)
    # df_full = pd.DataFrame([]) # Descomente esta linha para testar o modo 'sem eventos'
    return df_full

# --- Estrutura Principal do Layout ---

df_full = criar_dados_cronograma()
eventos_pai = df_full[df_full['evento_pai'].notna()].sort_values(by='data_pai', ascending=False)


# =========================================================
## 1. ⚙️ Painel de Administração (Barra Lateral)
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
st.markdown("---")

# Colunas para a Timeline: Coluna A (Ponto/Linha) | Coluna B (Conteúdo/Cartão)
col_visual, col_content = st.columns([0.05, 0.95])


## Lógica de Renderização

if eventos_pai.empty:
    # Renderiza a estrutura da Timeline, mas com a mensagem de vazio
    with col_visual:
        # Renderiza a linha vertical base
        st.markdown('<div class="timeline-line" style="height: 100px;"></div>', unsafe_allow_html=True)
        st.markdown('<div class="timeline-line" style="height: 100px;"></div>', unsafe_allow_html=True)
        
    with col_content:
        st.info("⚠️ Não há eventos registrados neste momento. Adicione o primeiro evento pelo Painel do Administrador.")
else:
    # Itera e renderiza os eventos existentes
    for index, pai in eventos_pai.iterrows():
        cor = pai['cor']
        
        # Como não carregamos todos os sub-eventos na função de dados acima, vamos simplificar para a timeline principal
        sub_eventos_presentes = df_full[
            (df_full['id_pai'] == pai['id_pai']) &
            (df_full['id_sub'].notna())
        ]
        
        # --- Coluna da Linha (Visual com Ícone) ---
        with col_visual:
            # Ponto de destaque (O ÍCONE ✝️ é injetado via CSS no ::after do .timeline-point)
            st.markdown(f'<div class="timeline-point point-{cor}"></div>', unsafe_allow_html=True)
            
            # A linha de conexão, exceto o último item
            if index < len(eventos_pai) - 1:
                st.markdown('<div class="timeline-line" style="height: 150px;"></div>', unsafe_allow_html=True)
            else:
                st.markdown('<div style="height: 50px;"></div>', unsafe_allow_html=True)
                
        # --- Coluna do Conteúdo (Cartão de Evento) ---
        with col_content:
            st.markdown(f'<div class="event-card card-{cor}">', unsafe_allow_html=True)
            
            # Data e Título
            st.markdown(f'<div class="event-date">{pai["data_pai"]}</div>', unsafe_allow_html=True)
            st.markdown(f"### **{pai['evento_pai']}**") 
            st.markdown(f"**ID:** `{pai['id_pai']}` | *(Ref: {pai['referencia']})*")
            
            # Expansor para Sub-eventos (usando a presença de sub-eventos simulados)
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
