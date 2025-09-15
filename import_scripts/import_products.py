import pandas as pd
import sqlite3
import os

# --- Configurações ---
# Garanta que o nome do arquivo Excel e do banco de dados estão corretos.
NOME_ARQUIVO_EXCEL = 'base_produtos.xlsx' 
NOME_BANCO_DADOS = 'garantias.db'

# Mapeamento das colunas: {Nome no Excel: Nome na Tabela do Banco de Dados}
MAPEAMENTO_COLUNAS = {
    'codigo_item': 'codigo_item',
    'descricao': 'descricao',
    'grupo_estoque': 'grupo_estoque'
}

def importar_produtos_do_excel():
    """
    Lê um arquivo Excel com dados de produtos e os insere na tabela 'Produtos'
    do banco de dados SQLite.
    """
    # Verifica se o arquivo Excel existe na pasta
    if not os.path.exists(NOME_ARQUIVO_EXCEL):
        print(f"Erro: Arquivo '{NOME_ARQUIVO_EXCEL}' não encontrado!")
        print("Por favor, coloque o arquivo na mesma pasta do script e tente novamente.")
        return

    print(f"Iniciando a importação do arquivo '{NOME_ARQUIVO_EXCEL}'...")

    try:
        # 1. Ler o arquivo Excel usando pandas
        df = pd.read_excel(NOME_ARQUIVO_EXCEL)
        
        # Renomeia as colunas do DataFrame para corresponder ao banco de dados, se necessário
        df.rename(columns=MAPEAMENTO_COLUNAS, inplace=True)

        # 2. Conectar ao banco de dados SQLite
        conn = sqlite3.connect(NOME_BANCO_DADOS)
        cursor = conn.cursor()
        
        produtos_inseridos = 0
        produtos_ignorados = 0

        # 3. Iterar sobre cada linha do DataFrame e inserir no banco de dados
        for index, row in df.iterrows():
            # A instrução 'INSERT OR IGNORE' é útil para não dar erro se o produto já existir.
            # Ela simplesmente ignora a inserção de códigos de item duplicados.
            cursor.execute("""
                INSERT OR IGNORE INTO Produtos (codigo_item, descricao, grupo_estoque) 
                VALUES (?, ?, ?)
            """, (
                row['codigo_item'], 
                row['descricao'], 
                row['grupo_estoque']
            ))
            
            # Verifica se a última operação realmente inseriu uma linha
            if cursor.rowcount > 0:
                produtos_inseridos += 1
            else:
                produtos_ignorados += 1
        
        # 4. Salvar (commit) as alterações e fechar a conexão
        conn.commit()
        conn.close()

        print("\n--- Importação Concluída! ---")
        print(f"Total de linhas no Excel: {len(df)}")
        print(f"Produtos novos inseridos: {produtos_inseridos}")
        print(f"Produtos já existentes (ignorados): {produtos_ignorados}")

    except FileNotFoundError:
        print(f"Erro: O arquivo '{NOME_ARQUIVO_EXCEL}' não foi encontrado.")
    except KeyError as e:
        print(f"Erro: Uma coluna esperada não foi encontrada no arquivo Excel: {e}")
        print("Verifique se os nomes das colunas no seu arquivo Excel estão corretos.")
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")

if __name__ == "__main__":
    importar_produtos_do_excel()