import sqlite3
import random
from datetime import datetime, timedelta

DB_NAME = "garantias.db"

def buscar_dados_existentes(conn):
    """Busca dados das tabelas de lookup para usar na geração de dados."""
    cursor = conn.cursor()
    
    cursor.execute("SELECT cnpj FROM Clientes")
    clientes = [row[0] for row in cursor.fetchall()]
    
    cursor.execute("SELECT codigo_item FROM Produtos")
    produtos = [row[0] for row in cursor.fetchall()]
    
    cursor.execute("SELECT codigo, classificacao FROM CodigosAvaria")
    avarias = {row[0]: row[1] for row in cursor.fetchall()}
    
    if not all([clientes, produtos, avarias]):
        print("ERRO: Uma ou mais tabelas (Clientes, Produtos, CodigosAvaria) está vazia.")
        print("Por favor, execute os scripts de importação primeiro.")
        return None, None, None
        
    return clientes, produtos, avarias

def gerar_dados_falsos(num_notas=100):
    """Gera e insere dados falsos no banco de dados para fins de teste."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    clientes, produtos, avarias = buscar_dados_existentes(conn)
    if not clientes:
        conn.close()
        return

    print(f"A gerar {num_notas} notas fiscais falsas...")
    
    total_itens_gerados = 0
    total_itens_analisados = 0
    total_ressarcimentos = 0
    
    hoje = datetime.now()
    
    for i in range(num_notas):
        print(f"A gerar nota {i+1}/{num_notas}...", end='\r')
        
        # Gera datas aleatórias para a nota e o lançamento
        dias_atras_nota = random.randint(1, 365)
        data_nota = hoje - timedelta(days=dias_atras_nota)
        
        # O lançamento ocorre alguns dias depois da data da nota
        dias_atras_lancamento = dias_atras_nota - random.randint(1, 10)
        if dias_atras_lancamento <= 0: dias_atras_lancamento = 1
        data_lancamento = hoje - timedelta(days=dias_atras_lancamento)

        cnpj = random.choice(clientes)
        num_nota = str(random.randint(10000, 99999))
        
        # --- CORREÇÃO 1: Adicionar a 'data_lancamento' ao inserir a nota fiscal ---
        cursor.execute(
            "INSERT INTO NotasFiscais (numero_nota, data_nota, cnpj_cliente, data_lancamento) VALUES (?, ?, ?, ?)",
            (num_nota, data_nota.strftime('%Y-%m-%d'), cnpj, data_lancamento.strftime('%Y-%m-%d'))
        )
        id_nota_fiscal = cursor.lastrowid
        
        num_itens_por_nota = random.randint(1, 5)
        for _ in range(num_itens_por_nota):
            total_itens_gerados += 1
            codigo_produto = random.choice(produtos)
            valor_item = round(random.uniform(50.0, 800.0), 2)
            
            letra_mes = "ABCDEFGHIJKL"[data_lancamento.month - 1]
            like_pattern = f"{letra_mes}%"
            date_pattern = f"{data_lancamento.year:04d}-{data_lancamento.month:02d}"
            
            # --- CORREÇÃO 2: Usar JOIN para buscar a data_lancamento na tabela NotasFiscais ---
            cursor.execute("""
                SELECT ig.codigo_analise 
                FROM ItensGarantia ig
                JOIN NotasFiscais nf ON ig.id_nota_fiscal = nf.id
                WHERE ig.codigo_analise LIKE ? AND STRFTIME('%Y-%m', nf.data_lancamento) = ?
            """, (like_pattern, date_pattern))
            
            resultados = cursor.fetchall()
            if not resultados:
                proximo_numero = 1
            else:
                numeros = [int(cod[0][1:]) for cod in resultados if cod[0][1:].isdigit()]
                proximo_numero = max(numeros) + 1 if numeros else 1
            codigo_analise = f"{letra_mes}{proximo_numero:03d}"

            # --- CORREÇÃO 3: Remover a coluna 'data_lancamento' do INSERT em ItensGarantia ---
            cursor.execute(
                """INSERT INTO ItensGarantia (id_nota_fiscal, codigo_produto, valor_item, codigo_analise) 
                   VALUES (?, ?, ?, ?)""",
                (id_nota_fiscal, codigo_produto, valor_item, codigo_analise)
            )
            id_item = cursor.lastrowid
            
            # Simular análise para 90% dos itens
            if random.random() < 0.9:
                total_itens_analisados += 1
                codigo_avaria = random.choice(list(avarias.keys()))
                procedencia = avarias[codigo_avaria]
                ressarcimento = 0.0
                if procedencia == 'Procedente' and random.random() < 0.6:
                    ressarcimento = round(valor_item * random.uniform(0.4, 0.9), 2)
                    total_ressarcimentos += 1

                cursor.execute(
                    """UPDATE ItensGarantia SET
                       status = 'Analisado',
                       numero_serie = ?,
                       codigo_avaria = ?,
                       procedente_improcedente = ?,
                       produzido_revenda = ?,
                       fornecedor = ?,
                       ressarcimento = ?
                       WHERE id = ?""",
                    (
                        str(random.randint(100000, 999999)),
                        codigo_avaria,
                        procedencia,
                        random.choice(['Produzido', 'Revenda']),
                        random.choice(['Fornecedor A', 'Fornecedor B', 'Fornecedor C']),
                        f"{ressarcimento:.2f}",
                        id_item
                    )
                )
    
    conn.commit()
    conn.close()
    
    print("\n" + "="*40)
    print("População do Banco de Dados Concluída!")
    print(f"Total de notas fiscais geradas: {num_notas}")
    print(f"Total de itens gerados: {total_itens_gerados}")
    print(f"Total de itens analisados: {total_itens_analisados}")
    print(f"Total de itens com ressarcimento: {total_ressarcimentos}")
    print("="*40)

if __name__ == "__main__":
    gerar_dados_falsos(num_notas=150) # Aumentei para 150 para ter mais dados