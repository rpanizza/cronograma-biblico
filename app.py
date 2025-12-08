import streamlit as st
import pandas as pd

# --- Configurações da Página ---
# Define a largura da página e o título
st.set_page_config(layout="wide", page_title="Cronograma Bíblico Profético")

## 📜 Função para Criar o DataFrame (Dados do Cronograma)
# Para manter a fidelidade às escrituras (conforme sua instrução),
# é crucial que os dados inseridos aqui sejam baseados na sua análise
# das referências. Este é apenas um exemplo estrutural.
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
        # --- EVENTO PAI 2 (Exemplo prático solicitado - Adaptado) ---
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
            "id_pai": "EP002", # ID do Pai
            "data_pai": None,
            "evento_pai": None,
            "id_sub": "ES002-1",
            "data_sub": "Março 2011",
            "descricao_sub": "Início do conflito civil na Síria, escalando para uma guerra complexa com envolvimento regional.",
            "profecia_sub": "Onde há menção de 'nação se levantará contra nação', interpretado como conflitos intensos.",
            "analise_hist_sub": "A Primavera Árabe e a subsequente Guerra Civil Síria mudaram o equilíbrio geopolítico na região.",
            "referencia": "Mateus 24:7",
        },
        {
            "id_pai": "EP002", # ID do Pai
            "data_pai": None,
            "evento_pai": None,
            "id_sub": "ES002-2",
            "data_sub": "Julho 2014",
            "descricao_sub": "Conflitos específicos na região de Gaza, intensificando a tensão entre Israel e grupos armados.",
            "profecia_sub": "Alusões a tempos de angústia e guerras nas fronteiras.",
            "analise_hist_sub": "Operações militares de grande escala com impacto significativo na população civil.",
            "referencia": "Lucas 21:10-11",
        },
        # --- EVENTO PAI 3 (Profecias de Longo Prazo) ---
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
        # --- SUB-EVENTO do EP003 ---
        {
            "id_pai": "EP003", # ID do Pai
            "data_pai": None,
            "evento_pai": None,
            "id_sub": "ES003-1",
            "data_sub": "Futuro",
            "descricao_sub": "A preparação e as negociações para a edificação do Terceiro Templo.",
            "profecia_sub": "A visão de Daniel sobre o templo e o 'abominável da desolação'.",
            "analise_hist_sub": "A principal dificuldade é a localização atual do Domo da Rocha no Monte do Templo.",
            "referencia": "2 Tessalonicenses 2:4",
        },
    ]
    return pd.DataFrame(dados)

# --- Título e Introdução do Aplicativo ---
st.title("📖 Timeline do Cronograma Bíblico Profético")
st.markdown("---") # Linha horizontal para separar o título da timeline

# Carrega os dados
df = criar_dados_cronograma()

# Obtém uma lista única dos IDs e Eventos Pais, ordenados pela data (para a timeline)
eventos_pai = df[df['evento_pai'].notna()].sort_values(by='data_pai', ascending=False)

## ⏳ Renderização da Timeline Vertical
st.header("⏳ Eventos Principais")

# Itera sobre cada Evento Pai para criar a estrutura da Timeline
for index, pai in eventos_pai.iterrows():
    # Encontra todos os sub-eventos relacionados a este Evento Pai
    sub_eventos = df[
        (df['id_pai'] == pai['id_pai']) & # Corresponde ao ID Pai
        (df['id_sub'].notna())           # Garante que é um sub-evento (não a linha Pai original)
    ]
    
    # 1. Cabeçalho do Evento Pai (O que aparece na Timeline)
    st.markdown(f"## 📅 **{pai['data_pai']}**")
    st.markdown(f"### **{pai['id_pai']}** | **{pai['evento_pai']}**")
    st.markdown(f"*(Referência Principal: {pai['referencia']})*")

    # 2. Expansor para Sub-eventos (A setinha de expandir/retrair)
    if not sub_eventos.empty:
        # Usa o 'evento_pai' como título do Expander
        with st.expander(f"➕ Detalhes e Sub-eventos de {pai['evento_pai']}"):
            # Itera sobre cada sub-evento dentro do expander
            for sub_index, sub in sub_eventos.iterrows():
                st.markdown("---") # Separador para cada sub-evento
                
                # Exibe as informações detalhadas
                st.markdown(f"#### ➡️ **{sub['data_sub']}**")
                
                # Uso do Markdown para formatação simples e destaque
                st.markdown(f"""
                    * **ID de Identificação:** `{sub['id_sub']}`
                    * **Descrição do Sub-evento:** {sub['descricao_sub']}
                    * **Profecia Relacionada:** {sub['profecia_sub']}
                    * **Análise Histórica:** {sub['analise_hist_sub']}
                    * **Referência Bíblica:** {sub['referencia']}
                """)
    else:
        # Mensagem caso não haja sub-eventos
        st.info("Não há detalhes ou sub-eventos expandíveis para este marco principal.")

    st.markdown("---") # Separador visual grande entre Eventos Pais

st.success("Fim do Cronograma Exibido.")
