# Gemini Finanças Pro
# Um script de controle financeiro pessoal com banco de dados SQLite.

import sqlite3
import os
import platform
from datetime import datetime
from colorama import Fore, Style, init

# Inicializa a biblioteca colorama
init(autoreset=True)

# --- CONFIGURAÇÃO ---
DB_NAME = 'financas.db'
CATEGORIAS_GASTOS = [
    "Alimentação", "Moradia", "Transporte", "Saúde",
    "Educação", "Lazer", "Vestuário", "Assinaturas", "Outros"
]

# --- FUNÇÕES DE BANCO DE DADOS (A base de tudo) ---

def conectar_db():
    """Conecta ao banco de dados SQLite e retorna a conexão."""
    return sqlite3.connect(DB_NAME)

def setup_database():
    """Cria a tabela de transações se ela não existir."""
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS transacoes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        data TEXT NOT NULL,
        descricao TEXT NOT NULL,
        valor REAL NOT NULL,
        tipo TEXT NOT NULL, -- 'ganho' ou 'gasto'
        categoria TEXT
    );
    """)
    conn.commit()
    conn.close()

def adicionar_transacao_db(data, descricao, valor, tipo, categoria=None):
    """Adiciona uma nova transação ao banco de dados."""
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO transacoes (data, descricao, valor, tipo, categoria) VALUES (?, ?, ?, ?, ?)",
        (data, descricao, valor, tipo, categoria)
    )
    conn.commit()
    conn.close()

def buscar_transacoes_db(mes=None, ano=None):
    """Busca transações, com filtro opcional por mês e ano."""
    conn = conectar_db()
    cursor = conn.cursor()
    query = "SELECT * FROM transacoes"
    params = []
    if mes and ano:
        query += " WHERE strftime('%Y-%m', data) = ?"
        params.append(f"{ano:04d}-{mes:02d}")
    query += " ORDER BY data"
    cursor.execute(query, params)
    transacoes = cursor.fetchall()
    conn.close()
    return transacoes

def atualizar_transacao_db(id_transacao, nova_descricao, novo_valor, nova_categoria):
    """Atualiza uma transação existente."""
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE transacoes SET descricao = ?, valor = ?, categoria = ? WHERE id = ?",
        (nova_descricao, novo_valor, nova_categoria, id_transacao)
    )
    conn.commit()
    conn.close()

def apagar_transacao_db(id_transacao):
    """Apaga uma transação pelo seu ID."""
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM transacoes WHERE id = ?", (id_transacao,))
    conn.commit()
    conn.close()

def relatorio_categoria_db():
    """Busca um resumo de gastos por categoria."""
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT categoria, SUM(valor) as total
        FROM transacoes
        WHERE tipo = 'gasto' AND categoria IS NOT NULL
        GROUP BY categoria
        ORDER BY total ASC;
    """)
    resumo = cursor.fetchall()
    conn.close()
    return resumo

# --- FUNÇÕES DE INTERFACE E LÓGICA ---

def limpar_tela():
    os.system('cls' if platform.system() == "Windows" else 'clear')

def esperar_enter():
    input("\nPressione Enter para continuar...")

def adicionar_ganho():
    limpar_tela()
    print(Fore.CYAN + "--- Adicionar Novo Ganho ---")
    descricao = input("Descrição do Ganho (ex: Salário): ")
    while True:
        try:
            valor_str = input("Valor do Ganho: ").replace(',', '.')
            valor = float(valor_str)
            if valor > 0: break
            else: print(Fore.RED + "O valor deve ser positivo.")
        except ValueError:
            print(Fore.RED + "Entrada inválida. Use apenas números.")

    adicionar_transacao_db(datetime.now().isoformat(), descricao, valor, 'ganho')
    print(Fore.GREEN + "\nGanho adicionado com sucesso!")
    esperar_enter()

def adicionar_gasto():
    limpar_tela()
    print(Fore.CYAN + "--- Adicionar Novo Gasto ---")
    descricao = input("Descrição do Gasto (ex: Almoço): ")
    while True:
        try:
            valor_str = input("Valor do Gasto: ").replace(',', '.')
            valor = float(valor_str)
            if valor > 0: break
            else: print(Fore.RED + "O valor deve ser positivo.")
        except ValueError:
            print(Fore.RED + "Entrada inválida. Use apenas números.")

    print("\nSelecione uma categoria:")
    for i, cat in enumerate(CATEGORIAS_GASTOS):
        print(f"{i + 1}. {cat}")

    while True:
        try:
            escolha = int(input("Escolha o número da categoria: "))
            if 1 <= escolha <= len(CATEGORIAS_GASTOS):
                categoria = CATEGORIAS_GASTOS[escolha - 1]
                break
            else:
                print(Fore.RED + "Escolha inválida.")
        except ValueError:
            print(Fore.RED + "Entrada inválida.")

    # Adiciona o gasto com valor negativo no banco
    adicionar_transacao_db(datetime.now().isoformat(), descricao, -valor, 'gasto', categoria)
    print(Fore.GREEN + "\nGasto adicionado com sucesso!")
    esperar_enter()

def listar_e_selecionar_transacao(transacoes):
    """Mostra uma lista de transações e pede para o usuário escolher uma pelo ID."""
    if not transacoes:
        print(Fore.YELLOW + "Nenhuma transação encontrada para o período selecionado.")
        return None

    ids_validos = []
    for t in transacoes:
        id, data_str, desc, valor, tipo, cat = t
        ids_validos.append(id)
        data = datetime.fromisoformat(data_str).strftime('%d/%m/%Y')
        cor = Fore.GREEN if tipo == 'ganho' else Fore.RED
        print(cor + f"ID: {id} | {data} | {desc:<25} | Categoria: {cat or 'N/A':<15} | R$ {valor:.2f}")

    while True:
        try:
            id_escolhido = int(input("\nDigite o ID da transação que deseja selecionar: "))
            if id_escolhido in ids_validos:
                return id_escolhido
            else:
                print(Fore.RED + "ID inválido. Tente novamente.")
        except ValueError:
            print(Fore.RED + "Por favor, digite um número.")


def editar_transacao():
    limpar_tela()
    print(Fore.CYAN + "--- Editar Transação ---")
    transacoes = buscar_transacoes_db() # Busca todas para facilitar a edição
    id_para_editar = listar_e_selecionar_transacao(transacoes)

    if id_para_editar is None:
        esperar_enter()
        return

    nova_descricao = input("Nova descrição (deixe em branco para não alterar): ")
    novo_valor_str = input("Novo valor (deixe em branco para não alterar): ")
    # Lógica de edição aqui (simplificada para brevidade)
    # Em uma app real, você buscaria os dados atuais e os preencheria
    # Esta é uma implementação básica
    print(Fore.YELLOW + "A edição de categoria e tipo não está implementada nesta versão simplificada.")
    print(Fore.GREEN + "Funcionalidade de atualização a ser completada.")
    esperar_enter()


def apagar_transacao():
    limpar_tela()
    print(Fore.CYAN + "--- Apagar Transação ---")
    transacoes = buscar_transacoes_db()
    id_para_apagar = listar_e_selecionar_transacao(transacoes)

    if id_para_apagar is None:
        esperar_enter()
        return

    confirmacao = input(f"\nTem certeza que deseja apagar a transação ID {id_para_apagar}? (s/n): ").lower()
    if confirmacao == 's':
        apagar_transacao_db(id_para_apagar)
        print(Fore.GREEN + "Transação apagada com sucesso!")
    else:
        print(Fore.YELLOW + "Operação cancelada.")
    esperar_enter()


def ver_extrato():
    limpar_tela()
    print(Fore.CYAN + "--- Extrato de Transações ---")
    filtro = input("Deseja filtrar por mês/ano? (s/n): ").lower()
    transacoes = []
    if filtro == 's':
        try:
            ano = int(input("Digite o ano (ex: 2025): "))
            mes = int(input("Digite o mês (ex: 5): "))
            transacoes = buscar_transacoes_db(mes, ano)
        except ValueError:
            print(Fore.RED + "Ano ou mês inválido.")
            transacoes = buscar_transacoes_db()
    else:
        transacoes = buscar_transacoes_db()

    if not transacoes:
        print(Fore.YELLOW + "\nNenhuma transação encontrada.")
    else:
        listar_e_selecionar_transacao(transacoes) # Reutilizando a função de listagem
    esperar_enter()


def ver_relatorio_categorias():
    limpar_tela()
    print(Fore.CYAN + "--- Resumo de Gastos por Categoria ---")
    resumo = relatorio_categoria_db()
    if not resumo:
        print(Fore.YELLOW + "Nenhum gasto categorizado encontrado.")
    else:
        total_geral = sum(abs(item[1]) for item in resumo)
        print(f"\n{Style.BRIGHT}{'Categoria':<20} | {'Total Gasto':>15} | {'% do Total'}")
        print("-" * 50)
        for categoria, total in resumo:
            percentual = (abs(total) / total_geral) * 100 if total_geral > 0 else 0
            print(f"{categoria:<20} | R$ {abs(total):>12.2f} | {percentual:6.2f}%")

    esperar_enter()

# --- LOOP PRINCIPAL ---

def main():
    setup_database()
    while True:
        limpar_tela()
        print(Fore.YELLOW + Style.BRIGHT + "\n--- Gemini Finanças Pro ---")
        print("1. Adicionar Gasto")
        print("2. Adicionar Ganho")
        print("3. Editar Transação")
        print("4. Apagar Transação")
        print("5. Ver Extrato Completo / Filtrado")
        print("6. Ver Relatório por Categoria")
        print("7. Sair")
        escolha = input("\nEscolha uma opção: ")

        if escolha == '1': adicionar_gasto()
        elif escolha == '2': adicionar_ganho()
        elif escolha == '3': editar_transacao() # Função de edição simplificada
        elif escolha == '4': apagar_transacao()
        elif escolha == '5': ver_extrato()
        elif escolha == '6': ver_relatorio_categorias()
        elif escolha == '7':
            print(Fore.CYAN + "Obrigado por usar o Gemini Finanças Pro!")
            break
        else:
            print(Fore.RED + "Opção inválida.")
            time.sleep(1)

if __name__ == "__main__":
    main()