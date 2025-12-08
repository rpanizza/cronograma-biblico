# app.py
from flask import Flask, render_template, url_for, redirect, request
import sqlite3
import os

app = Flask(__name__)
# Apenas para exemplo. Em produção, use um método seguro para carregar a chave!
app.secret_key = os.environ.get('SECRET_KEY', 'sua_chave_secreta_padrao') 

DATABASE = 'database.db'

def get_db_connection():
    """Cria e retorna a conexão com o banco de dados."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row # Permite acessar colunas como dicionário
    return conn

# --- Rota Principal: Dashboard (Timeline) ---
@app.route('/')
def dashboard():
    conn = get_db_connection()
    # Busca os eventos ordenados cronologicamente (exemplo simples)
    # Você precisará criar a tabela 'events' primeiro
    events = conn.execute('SELECT title, description, date FROM events ORDER BY date ASC').fetchall()
    conn.close()
    
    # Renderiza o template, passando os eventos para o frontend
    return render_template('dashboard.html', events=events)

# --- Rota de Login ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    # Implementação de login será feita mais tarde.
    # Por enquanto, apenas renderiza o formulário.
    if request.method == 'POST':
        # ... Lógica de autenticação virá aqui ...
        return redirect(url_for('dashboard')) # Redireciona após login bem-sucedido
    return render_template('login.html')

# --- Rota de Compartilhamento (Exemplo) ---
@app.route('/share')
def share():
    # Lógica de compartilhamento: pode ser um modal ou uma página com links de redes sociais.
    return "Funcionalidade de Compartilhamento em breve!"

# --- Inicialização da Aplicação ---
if __name__ == '__main__':
    # Apenas para garantir que o BD e a tabela existam na primeira execução
    with get_db_connection() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                date TEXT NOT NULL
            );
        ''')
        # Exemplo de inserção para teste
        if not conn.execute('SELECT 1 FROM events').fetchone():
             conn.execute("INSERT INTO events (title, description, date) VALUES ('Criação', 'Gênesis 1:1', '0')")
             conn.execute("INSERT INTO events (title, description, date) VALUES ('Êxodo', 'Livro de Êxodo', '1446 A.C.')")
             conn.execute("INSERT INTO events (title, description, date) VALUES ('Nascimento de Cristo', 'Mateus 1:18', '0')")
             conn.execute("INSERT INTO events (title, description, date) VALUES ('Eventos Finais', 'Apocalipse 21:1', 'Futuro')")
             conn.commit()

    print("Banco de dados e tabela 'events' verificados/criados.")
    app.run(debug=True)
