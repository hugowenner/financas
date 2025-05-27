# log_sessoes.py
import sqlite3
from datetime import datetime

DB_NAME = 'financas.db' # O mesmo banco de dados do backend.py

def conectar_db_log():
    """Conecta ao banco de dados para logs."""
    return sqlite3.connect(DB_NAME)

def setup_historico_logins_table():
    """Cria a tabela de histórico de logins se ela não existir."""
    conn = conectar_db_log()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS historico_logins (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        data_login TEXT NOT NULL,
        status TEXT NOT NULL, -- SUCESSO, FALHA, FALHA_USUARIO_INEXISTENTE
        ip_address TEXT 
    );
    """)
    conn.commit()
    conn.close()
    print("Tabela 'historico_logins' verificada/criada.") # Para debug inicial

def registrar_evento_login_db(username, status, ip_address=None):
    """Registra um evento de login (sucesso ou falha) no banco de dados."""
    conn = conectar_db_log()
    cursor = conn.cursor()
    data_atual = datetime.now().isoformat()
    try:
        cursor.execute(
            "INSERT INTO historico_logins (username, data_login, status, ip_address) VALUES (?, ?, ?, ?)",
            (username, data_atual, status, ip_address)
        )
        conn.commit()
    except Exception as e:
        print(f"Erro ao registrar evento de login no DB: {e}")
    finally:
        conn.close()

def buscar_historico_logins_db(limit=100):
    """Busca o histórico de logins, limitado pela quantidade especificada."""
    conn = conectar_db_log()
    cursor = conn.cursor()
    cursor.execute("SELECT username, data_login, status, ip_address FROM historico_logins ORDER BY data_login DESC LIMIT ?", (limit,))
    historico = cursor.fetchall()
    conn.close()
    return historico