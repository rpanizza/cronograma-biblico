# Linhas 105 a 124 (Função de Dados)
def criar_dados_cronograma():
    """Cria dados de exemplo com cores e IDs no formato: AAAA.MM.DD.V"""
    dados = [
        # ... vários dicionários aqui ...
        {
            "id_pai": "3000.02.01.1", "data_pai": "Futuro (Breve)", "evento_pai": "Gogue e Magogue",
            "id_sub": None, "cor": "lavender", "referencia": "Ezequiel 38-39",
        },
    ]  # Linha 125 (Fechamento da lista)
    df_full = pd.DataFrame(dados) # Linha 126 (Onde o erro foi reportado)
    return df_full
