import pandas as pd
import sqlite3

# --- CONFIGURAÇÕES ---
# Certifique-se de que estes nomes correspondem aos seus ficheiros e colunas.
DB_FILE = "garantias.db"
EXCEL_FILE = "base_clientes.xlsx"  # Coloque o nome do seu ficheiro Excel aqui

# Nomes exatos das colunas no seu ficheiro Excel
COLUMN_CNPJ = "cnpj"
COLUMN_CODIGO = "codigo_cliente"
COLUMN_NOME = "nome_cliente"
COLUMN_GRUPO = "grupo_cliente"

def importar_clientes():
    """Lê um ficheiro Excel e insere os dados na tabela Clientes do banco de dados."""
    try:
        # 1. Ler o ficheiro Excel
        df = pd.read_excel(EXCEL_FILE)
        print(f"Ficheiro '{EXCEL_FILE}' lido com sucesso. {len(df)} linhas encontradas.")

        # 2. Validar se as colunas necessárias existem
        required_columns = [COLUMN_CNPJ, COLUMN_CODIGO, COLUMN_NOME, COLUMN_GRUPO]
        for col in required_columns:
            if col not in df.columns:
                print(f"ERRO: A coluna '{col}' não foi encontrada no ficheiro Excel.")
                print(f"Colunas disponíveis: {list(df.columns)}")
                return

        # 3. Conectar ao banco de dados
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        print(f"Conexão com o banco de dados '{DB_FILE}' estabelecida.")

        # 4. Inserir os dados
        clientes_inseridos = 0
        for index, row in df.iterrows():
            cnpj = row[COLUMN_CNPJ]
            codigo_cliente = row[COLUMN_CODIGO]
            nome_cliente = row[COLUMN_NOME]
            grupo_cliente = row[COLUMN_GRUPO]
            
            # Garante que o CNPJ não é nulo ou vazio
            if pd.notna(cnpj) and str(cnpj).strip():
                # 'INSERT OR IGNORE' não insere se o 'cnpj' já existir (devido à restrição PRIMARY KEY)
                cursor.execute(
                    "INSERT OR IGNORE INTO Clientes (cnpj, codigo_cliente, nome_cliente, grupo_cliente) VALUES (?, ?, ?, ?)", 
                    (
                        str(cnpj).strip(), 
                        str(codigo_cliente).strip(), 
                        str(nome_cliente).strip(), 
                        str(grupo_cliente).strip() if pd.notna(grupo_cliente) else None # Trata grupos vazios
                    )
                )
                if cursor.rowcount > 0:
                    clientes_inseridos += 1
        
        # 5. Salvar e fechar
        conn.commit()
        conn.close()

        print("\n--- Resultado da Importação ---")
        print(f"Total de novos clientes inseridos: {clientes_inseridos}")
        print("Importação concluída!")

    except FileNotFoundError:
        print(f"ERRO: O ficheiro '{EXCEL_FILE}' não foi encontrado. Coloque-o na mesma pasta do script.")
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")

if __name__ == "__main__":
    importar_clientes()