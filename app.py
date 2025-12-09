import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

# --- Configurações Iniciais ---
st.set_page_config(layout="wide", page_title="Cronograma Bíblico: Esfera em Destaque")

# Nome do arquivo de dados
DATA_FILE = "cronograma_data.json"

# --- Funções de Persistência (Mantidas da V10.0) ---

def carregar_dados():
    """Carrega dados do arquivo JSON ou retorna dados vazios/exemplo se o arquivo não existir."""
    if os.path.exists(DATA_FILE) and os.path.getsize(DATA_FILE) > 0:
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return criar_dados_exemplo()
    return criar_dados_exemplo()

def salvar_dados(dados):
    """Salva a lista de dados no arquivo JSON."""
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)
    st.rerun()

def criar_dados_exemplo():
    """Cria dados de exemplo para inicialização."""
    return [
        {
            "id_pai": "0025.00.00.1", "data_pai": "2025 A.C.", "evento_pai": "O Dilúvio Universal",
            "id_sub": None, "cor": "red", "referencia": "Gênesis 6-9",
        },
        {
            "id_pai": "2011.03.00.1", "data_pai": "2011 D.C.", "evento_pai": "Agitação no Oriente Médio",
            "id_sub": None, "cor": "blue", "referencia": "Mateus 24:6-7",
        },
        {
            "id_pai": "3000.01.01.1", "data_pai": "Futuro (Indefinido)", "evento_pai": "Reconstrução do Templo",
            "id_sub": None, "cor": "green", "referencia": "Daniel 9:27",
        },
        {
            "id_pai": "3000.02.01.1", "data_pai": "Futuro (Breve)", "evento_pai": "Gogue e Magogue",
            "id_sub": None, "cor": "orange", "referencia": "Ezequiel 38-39",
        }
    ]

def gerar_novo_id(data_str):
    """Gera um ID único baseado na data e na versão atual."""
    try:
        if data_str.lower() in ["futuro", "indefinido", "futuro (indefinido)", "futuro (breve)"]:
             prefix = f"3999.12.31."
        elif "a.c." in data_str.lower():
            ano = int(data_str.lower().replace(" a.c.", "").strip())
            prefix = f"{ano:04d}.00.00." 
        else:
            if "/" in data_str:
                dt = datetime.strptime(data_str, "%Y/%m/%d")
            elif len(data_str) == 4 and data_str.isdigit():
                dt = datetime.strptime(data_str, "%Y")
            else:
                dt = datetime.strptime(data_str, "%Y")
            prefix = dt.strftime("%Y.%m.%d.")
    except ValueError:
        prefix = "9999.00.00." 
        
    df = pd.DataFrame(st.session_state.cronograma_data)
    if not df.empty:
        max_id = df[df['id_pai'].str.startswith(prefix)].apply(lambda x: x['id_pai'].split('.')[-1], axis=1).astype(int).max()
        nova_versao = (max_id if pd.notna(max_id) else 0) + 1
    else:
        nova_versao = 1
        
    return prefix + str(nova_versao)


# --- Inicialização do Estado ---
if 'cronograma_data' not in st.session_state:
    st.session_state.cronograma_data = carregar_dados()

df_full = pd.DataFrame(st.session_state.cronograma_data)
eventos_pai = df_full[df_full['evento_pai'].notna()].sort_values(by='id_pai', ascending=False)

# --- CSS NOVO LAYOUT: ESFERA EM DESTAQUE ---
TIMELINE_CSS = """
<style>
/* ------------------------------------- */
/* --- NOVO ESTILO: ESFERA DE DESTAQUE --- */
/* ------------------------------------- */

/* Ponto de Destaque (Principal) */
.timeline-sphere {
    width: 30px; /* Maior para o efeito 3D */
    height: 30px;
    border-radius: 50%;
    position: relative;
    top: 5px; /* Alinha com o início do cartão */
    left: -15px; /* Ajuste para o centro da coluna visual */
    
    /* Efeito de Esfera/Brilho (Gradient para profundidade) */
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.4);
    border: 1px solid rgba(255, 255, 255, 0.3);
    
    z-index: 10;
    display: flex;
    justify-content: center;
    align-items: center;
}

/* Pseudo-elemento para o ÍCONE (Centralizado) */
.timeline-sphere::after {
    content: "✝️"; 
    font-size: 14px; /* Ícone maior */
    line-height: 1; 
    color: white; 
    text-shadow: 0 0 5px rgba(0, 0, 0, 0.8);
}

/* Cores das Esferas */
.sphere-red { 
    background: radial-gradient(circle at 10px 10px, #FF5733, #C70039); /* Laranja-Vermelho */
}
.sphere-blue { 
    background: radial-gradient(circle at 10px 10px, #00BFFF, #1E90FF); /* Azul Claro-Escuro */
}
.sphere-green { 
    background: radial-gradient(circle at 10px 10px, #3CB371, #2E8B57); /* Verde Floresta */
}
.sphere-orange { 
    background: radial-gradient(circle at 10px 10px, #FFD700, #FF8C00); /* Dourado-Laranja */
}

/* --- Bolinha Menor (Linha Pontilhada) --- */
.small-dot {
    width: 4px; /* Menor e mais discreta */
    height: 4px;
    background-color: #6c757d; /* Cinza médio */
    border-radius: 50%;
    margin: 6px 0 6px 14px; /* Alinhamento com a nova esfera */
}

/* --- Container da Linha Pontilhada --- */
.dot-line-container {
    height: 150px; 
    display: flex;
    flex-direction: column;
    justify-content: space-evenly; 
    align-items: center;
    padding-left: 15px; /* Alinha com a coluna */
}

/* Estilo para o Cartão de Evento (Conteúdo) */
.event-card {
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 30px;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.15); /* Sombra forte para destacar */
    border: 1px solid #333; /* Borda sutil para modo escuro */
    background-color: #1e1e1e; /* Fundo levemente escuro (Ótimo em Streamlit Dark Mode) */
    transition: all 0.3s ease-in-out;
}

/* Alinhamento Vertical: Container para envolver o Card e o Ponto */
.event-wrapper {
    display: flex;
    align-items: center; /* Alinha o conteúdo verticalmente */
    margin-bottom: 20px;
}

/* Cabeçalho do Cartão */
.card-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom:
