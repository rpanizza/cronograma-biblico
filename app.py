import streamlit as st
import pandas as pd
from datetime import datetime

# --- Configurações Iniciais ---
st.set_page_config(layout="wide", page_title="Cronograma Bíblico Pontilhado com Bolhas")

# --- CSS OTIMIZADO (NOVA LINHA DE BOLINHAS) ---
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
    background-color: #ccc; /* Cinza sutil */
    border-radius: 50%;
    margin: 5px 0 5px 12px; /* Margem ajustada para alinhar com o centro da linha */
    box-shadow: 0 0 2px rgba(0, 0, 0, 0.1);
}

/* --- Container da Linha Pontilhada --- */
.dot-line-container {
    height: 150px; /* Altura do espaço entre eventos */
    display: flex;
    flex-direction: column;
    justify-content: space-evenly; /* Distribui as bolinhas uniformemente */
    align-items: center;
    padding-left: 20px; /* Alinha o container na coluna visual */
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
def renderizar_bolinhas_menores(num_bolinhas=5):
    """Gera o HTML para a linha pontilhada de bolhas."""
    bolhas_html = '<div class="dot-line-container">'
    # Repete a bolinha menor o número de vezes desejado
    for _ in range(num_bolinhas):
        bolhas_html += '<div class="small-dot"></div>'
    bolhas_html += '</div>'
    return bolhas_html


# --- Função de Dados (Estrutura Mantida) ---
def criar_dados_cronograma():
    """Cria dados de exemplo com cores e IDs no formato: AAAA.MM.DD.V"""
    dados = [
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
