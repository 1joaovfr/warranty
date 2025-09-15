import sqlite3

DB_NAME = "garantias.db"

def criar_banco_de_dados():
    """Cria a estrutura inicial do banco de dados, sem popular com dados."""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        print(f"Banco de dados '{DB_NAME}' conectado com sucesso.")

        # Tabela 1: Empresas (para o dropdown)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Empresas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                codigo_empresa TEXT NOT NULL UNIQUE,
                nome TEXT
            )
        ''')

        # Tabela 2: Clientes
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Clientes (
                cnpj TEXT PRIMARY KEY,
                codigo_cliente TEXT,
                nome_cliente TEXT,
                grupo_cliente TEXT
            )
        ''')

        # Tabela 3: Produtos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Produtos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                codigo_item TEXT NOT NULL UNIQUE,
                descricao TEXT,
                grupo_estoque TEXT
            )
        ''')

        # Tabela 4: Códigos de Avaria
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS CodigosAvaria (
                codigo TEXT PRIMARY KEY,
                descricao_tecnica TEXT,
                classificacao TEXT,
                grupo_relacionado TEXT
            )
        ''')

        # Tabela 5: Notas Fiscais (Transacional)
        # ALTERAÇÃO: Adicionada a coluna 'data_lancamento'
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS NotasFiscais (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                numero_nota TEXT NOT NULL,
                data_nota TEXT NOT NULL,
                cnpj_cliente TEXT,
                data_lancamento TEXT,
                FOREIGN KEY (cnpj_cliente) REFERENCES Clientes (cnpj)
            )
        ''')

        # Tabela 6: Itens da Garantia (Transacional Principal)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ItensGarantia (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_nota_fiscal INTEGER,
                codigo_produto TEXT,
                valor_item REAL,
                status TEXT DEFAULT 'Pendente de Análise',
                codigo_analise TEXT,
                numero_serie TEXT,
                codigo_avaria TEXT,
                descricao_avaria TEXT,
                procedente_improcedente TEXT,
                produzido_revenda TEXT,
                fornecedor TEXT,
                ressarcimento TEXT,
                FOREIGN KEY (id_nota_fiscal) REFERENCES NotasFiscais (id) ON DELETE CASCADE,
                FOREIGN KEY (codigo_produto) REFERENCES Produtos (codigo_item),
                FOREIGN KEY (codigo_avaria) REFERENCES CodigosAvaria (codigo)
            )
        ''')

        conn.commit()
        conn.close()
        print("Estrutura do banco de dados criada/verificada com sucesso!")

    except sqlite3.Error as e:
        print(f"Ocorreu um erro ao criar o banco de dados: {e}")

if __name__ == "__main__":
    criar_banco_de_dados()