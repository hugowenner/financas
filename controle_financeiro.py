import csv
import os
import platform
from datetime import datetime
import time
from colorama import Fore, Style, init

# Inicializa a biblioteca colorama para funcionar no Windows
init(autoreset=True)

# Nome do arquivo que guardará os dados
NOME_ARQUIVO = 'transacoes.csv'
# Cabeçalho do nosso arquivo CSV
CABECALHO = ['Data', 'Descricao', 'Valor', 'Tipo']
# Lista para manter as transações em memória
transacoes = []

def limpar_tela():
    """Limpa a tela do terminal, funciona em Windows, Linux e macOS."""
    if platform.system() == "Windows":
        os.system('cls')
    else:
        os.system('clear')

def carregar_transacoes():
    """Carrega as transações do arquivo CSV para a memória."""
    try:
        with open(NOME_ARQUIVO, mode='r', newline='', encoding='utf-8') as arquivo:
            leitor_csv = csv.DictReader(arquivo)
            for linha in leitor_csv:
                # Converte o valor de string para float ao carregar
                linha['Valor'] = float(linha['Valor'])
                transacoes.append(linha)
        print(Fore.CYAN + "Dados anteriores carregados com sucesso!")
    except FileNotFoundError:
        print(Fore.CYAN + "Bem-vindo! Nenhum arquivo de dados encontrado, começando um novo controle.")
    except Exception as e:
        print(Fore.RED + f"Ocorreu um erro ao carregar o arquivo: {e}")
    time.sleep(2)

def salvar_transacao(nova_transacao):
    """Salva uma nova transação no arquivo CSV."""
    try:
        # Verifica se o arquivo já existe para decidir se escreve o cabeçalho
        arquivo_existe = os.path.isfile(NOME_ARQUIVO)
        with open(NOME_ARQUIVO, mode='a', newline='', encoding='utf-8') as arquivo:
            escritor_csv = csv.DictWriter(arquivo, fieldnames=CABECALHO)
            if not arquivo_existe:
                escritor_csv.writeheader()  # Escreve o cabeçalho se o arquivo for novo
            escritor_csv.writerow(nova_transacao)
    except Exception as e:
        print(Fore.RED + f"Ocorreu um erro ao salvar a transação: {e}")


def mostrar_menu():
    """Mostra o menu principal."""
    limpar_tela()
    print(Fore.YELLOW + "--- CONTROLE FINANCEIRO (Python) ---")
    print("1. Adicionar Salário")
    print("2. Adicionar Outro Ganho")
    print("3. Adicionar Gasto")
    print("4. Ver Resumo Financeiro")
    print("5. Ver Extrato Detalhado")
    print("6. Sair")
    print(Fore.YELLOW + "------------------------------------")

# --- NOVA FUNÇÃO ---
def adicionar_salario():
    """Adiciona o salário, pedindo apenas o valor."""
    limpar_tela()
    print(Fore.CYAN + "--- Adicionar Salário ---")
    while True:
        try:
            valor_str = input("Digite o valor do salário: ").replace(',', '.')
            valor = float(valor_str)
            if valor > 0:
                break
            else:
                print(Fore.RED + "O valor deve ser positivo.")
        except ValueError:
            print(Fore.RED + "Entrada inválida. Por favor, digite apenas números.")
    
    nova_transacao = {
        'Data': datetime.now().isoformat(),
        'Descricao': 'Salário',
        'Valor': valor,
        'Tipo': 'Ganho'
    }
    
    transacoes.append(nova_transacao)
    salvar_transacao(nova_transacao)
    
    print(Fore.GREEN + f"\nSalário de R$ {valor:.2f} adicionado com sucesso!")
    time.sleep(2)

def adicionar_outro_ganho():
    """Adiciona uma transação de ganho."""
    limpar_tela()
    descricao = input("Descrição do Ganho (ex: Freelance, Venda): ")
    while True:
        try:
            valor_str = input("Digite o valor do ganho: ").replace(',', '.')
            valor = float(valor_str)
            if valor > 0:
                break
            else:
                print(Fore.RED + "O valor deve ser positivo.")
        except ValueError:
            print(Fore.RED + "Entrada inválida. Por favor, digite apenas números.")
    
    nova_transacao = {
        'Data': datetime.now().isoformat(),
        'Descricao': descricao,
        'Valor': valor,
        'Tipo': 'Ganho'
    }
    
    transacoes.append(nova_transacao)
    salvar_transacao(nova_transacao)
    
    print(Fore.GREEN + f"\nGanho de R$ {valor:.2f} adicionado com sucesso!")
    time.sleep(2)

def adicionar_gasto():
    """Adiciona uma transação de gasto."""
    limpar_tela()
    descricao = input("Descrição do Gasto (ex: Almoço, Uber): ")
    while True:
        try:
            valor_str = input("Digite o valor do gasto: ").replace(',', '.')
            valor = float(valor_str)
            if valor > 0:
                break
            else:
                print(Fore.RED + "O valor deve ser positivo.")
        except ValueError:
            print(Fore.RED + "Entrada inválida. Por favor, digite apenas números.")

    nova_transacao = {
        'Data': datetime.now().isoformat(),
        'Descricao': descricao,
        'Valor': -valor,  # Salva o gasto como um número negativo
        'Tipo': 'Gasto'
    }

    transacoes.append(nova_transacao)
    salvar_transacao(nova_transacao)

    print(Fore.GREEN + f"\nGasto de R$ {valor:.2f} adicionado com sucesso!")
    time.sleep(2)


def ver_resumo():
    """Calcula e exibe o resumo financeiro."""
    limpar_tela()
    total_ganhos = sum(t['Valor'] for t in transacoes if t['Tipo'] == 'Ganho')
    total_gastos = sum(t['Valor'] for t in transacoes if t['Tipo'] == 'Gasto')
    saldo_atual = total_ganhos + total_gastos

    print(Fore.YELLOW + "--- RESUMO FINANCEIRO ---")
    print(Fore.GREEN + f"Total de Ganhos: R$ {total_ganhos:.2f}")
    print(Fore.RED + f"Total de Gastos: R$ {abs(total_gastos):.2f}")
    print("-------------------------")
    print(Fore.CYAN + f"Saldo Atual:     R$ {saldo_atual:.2f}")
    
    input("\nPressione Enter para voltar ao menu...")


def ver_extrato():
    """Exibe todas as transações em ordem."""
    limpar_tela()
    print(Fore.YELLOW + "--- EXTRATO DETALHADO ---")

    if not transacoes:
        print("Nenhuma transação encontrada.")
    else:
        # Ordena as transações por data para exibição
        transacoes_ordenadas = sorted(transacoes, key=lambda t: t['Data'])
        for t in transacoes_ordenadas:
            data_formatada = datetime.fromisoformat(t['Data']).strftime('%d/%m/%Y %H:%M')
            valor = t['Valor']
            descricao = t['Descricao']
            
            # Formata a linha com cores diferentes para ganho e gasto
            if t['Tipo'] == 'Ganho':
                print(Fore.GREEN + f"{data_formatada} - {descricao:<30} - R$ {valor:8.2f}")
            else:
                print(Fore.RED + f"{data_formatada} - {descricao:<30} - R$ {valor:8.2f}")

    input("\nPressione Enter para voltar ao menu...")

# --- BLOCO PRINCIPAL DO PROGRAMA (ATUALIZADO) ---
if __name__ == "__main__":
    carregar_transacoes()
    while True:
        mostrar_menu()
        escolha = input("Escolha uma opção: ")
        
        if escolha == '1':
            adicionar_salario()
        elif escolha == '2':
            adicionar_outro_ganho()
        elif escolha == '3':
            adicionar_gasto()
        elif escolha == '4':
            ver_resumo()
        elif escolha == '5':
            ver_extrato()
        elif escolha == '6':
            break
        else:
            print(Fore.RED + "Opção inválida, tente novamente.")
            time.sleep(2)

    print(Fore.YELLOW + "Obrigado por usar o Controle Financeiro! Até logo.")