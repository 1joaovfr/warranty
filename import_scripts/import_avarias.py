import pandas as pd
import sqlite3

# --- CONFIGURAÇÕES ---
# Certifique-se de que estes nomes correspondem aos seus ficheiros e colunas.
DB_FILE = "garantias.db"
EXCEL_FILE = "base_avarias.xlsx"  # Coloque o nome do seu ficheiro Excel aqui

# Nomes exatos das colunas no seu ficheiro Excel
COLUMN_CODIGO = "codigo"
COLUMN_DESCRICAO = "descricao_tecnica"
COLUMN_CLASSIFICACAO = "classificacao"
COLUMN_GRUPO = "grupo_relacionado"

def importar_avarias():
    """Lê um ficheiro Excel e insere os dados na tabela CodigosAvaria do banco de dados."""
    try:
        # 1. Ler o ficheiro Excel
        df = pd.read_excel(EXCEL_FILE)
        print(f"Ficheiro '{EXCEL_FILE}' lido com sucesso. {len(df)} linhas encontradas.")

        # 2. Validar se as colunas necessárias existem
        required_columns = [COLUMN_CODIGO, COLUMN_DESCRICAO, COLUMN_CLASSIFICACAO, COLUMN_GRUPO]
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
        avarias_inseridas = 0
        for index, row in df.iterrows():
            codigo = row[COLUMN_CODIGO]
            descricao = row[COLUMN_DESCRICAO]
            classificacao = row[COLUMN_CLASSIFICACAO]
            grupo = row[COLUMN_GRUPO]
            
            # Garante que o código da avaria não é nulo ou vazio
            if pd.notna(codigo) and str(codigo).strip():
                # 'INSERT OR IGNORE' não insere se o 'codigo' já existir (devido à restrição PRIMARY KEY)
                cursor.execute(
                    "INSERT OR IGNORE INTO CodigosAvaria (codigo, descricao_tecnica, classificacao, grupo_relacionado) VALUES (?, ?, ?, ?)", 
                    (str(codigo).strip(), str(descricao).strip(), str(classificacao).strip(), str(grupo).strip())
                )
                if cursor.rowcount > 0:
                    avarias_inseridas += 1
        
        # 5. Salvar e fechar
        conn.commit()
        conn.close()

        print("\n--- Resultado da Importação ---")
        print(f"Total de novas avarias inseridas: {avarias_inseridas}")
        print("Importação concluída!")

    except FileNotFoundError:
        print(f"ERRO: O ficheiro '{EXCEL_FILE}' não foi encontrado. Coloque-o na mesma pasta do script.")
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")

if __name__ == "__main__":
    importar_avarias()