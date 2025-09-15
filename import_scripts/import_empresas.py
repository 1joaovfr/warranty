import pandas as pd
import sqlite3

# --- CONFIGURAÇÕES ---
# Certifique-se de que estes nomes correspondem aos seus arquivos e colunas.
DB_FILE = "garantias.db"
EXCEL_FILE = "base_empresas.xlsx"      # Coloque o nome do seu arquivo Excel aqui
COLUMN_CODE_NAME = "codigo_empresa" # Altere para o nome exato da coluna do CÓDIGO no seu Excel
COLUMN_NAME = "nome"        # Altere para o nome exato da coluna do NOME no seu Excel

def importar_empresas():
    """Lê um arquivo Excel e insere o código e o nome das empresas no banco de dados."""
    try:
        # 1. Ler o arquivo Excel
        df = pd.read_excel(EXCEL_FILE)
        print(f"Arquivo '{EXCEL_FILE}' lido com sucesso. {len(df)} linhas encontradas.")

        # 2. Validar se as colunas existem
        required_columns = [COLUMN_CODE_NAME, COLUMN_NAME]
        for col in required_columns:
            if col not in df.columns:
                print(f"ERRO: A coluna '{col}' não foi encontrada no arquivo Excel.")
                print(f"Colunas disponíveis: {list(df.columns)}")
                return

        # 3. Conectar ao banco de dados
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        print(f"Conexão com o banco de dados '{DB_FILE}' estabelecida.")

        # 4. Inserir os dados
        empresas_inseridas = 0
        for index, row in df.iterrows():
            codigo_empresa = row[COLUMN_CODE_NAME]
            nome_empresa = row[COLUMN_NAME]
            
            # Garante que o código da empresa não é nulo ou vazio
            if pd.notna(codigo_empresa) and str(codigo_empresa).strip():
                # 'INSERT OR IGNORE' não insere se o codigo_empresa já existir (devido à restrição UNIQUE)
                cursor.execute(
                    "INSERT OR IGNORE INTO Empresas (codigo_empresa, nome) VALUES (?, ?)", 
                    (str(codigo_empresa).strip(), str(nome_empresa).strip())
                )
                if cursor.rowcount > 0:
                    empresas_inseridas += 1
        
        # 5. Salvar e fechar
        conn.commit()
        conn.close()

        print("\n--- Resultado da Importação ---")
        print(f"Total de novas empresas inseridas: {empresas_inseridas}")
        print("Importação concluída!")

    except FileNotFoundError:
        print(f"ERRO: O arquivo '{EXCEL_FILE}' não foi encontrado. Coloque-o na mesma pasta do script.")
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")

if __name__ == "__main__":
    importar_empresas()