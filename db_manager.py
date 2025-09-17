import sqlite3
from datetime import datetime

DB_NAME = "garantias.db"

# =================================================================================
# --- FUNÇÕES DE BUSCA (SELECT) ---
# =================================================================================

def buscar_cliente_por_cnpj(cnpj):
    try:
        conn = sqlite3.connect(DB_NAME)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Clientes WHERE cnpj = ?", (cnpj,))
        cliente = cursor.fetchone()
        conn.close()
        return dict(cliente) if cliente else None
    except sqlite3.Error as e:
        print(f"Erro ao buscar cliente: {e}")
        return None

def buscar_produto_por_codigo(codigo):
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT codigo_item FROM Produtos WHERE codigo_item = ?", (codigo,))
        produto = cursor.fetchone()
        conn.close()
        return produto is not None
    except sqlite3.Error as e:
        print(f"Erro ao buscar produto: {e}")
        return False

def buscar_todas_empresas():
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT codigo_empresa FROM Empresas ORDER BY codigo_empresa")
        empresas = [row[0] for row in cursor.fetchall()]
        conn.close()
        return empresas
    except sqlite3.Error as e:
        print(f"Erro ao buscar empresas: {e}")
        return []

def buscar_todos_codigos_avaria():
    try:
        conn = sqlite3.connect(DB_NAME)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT codigo, descricao_tecnica, classificacao FROM CodigosAvaria ORDER BY codigo")
        rows = cursor.fetchall()
        conn.close()
        return {row['codigo']: {'descricao': row['descricao_tecnica'], 'classificacao': row['classificacao']} for row in rows}
    except sqlite3.Error as e:
        print(f"Erro ao buscar códigos de avaria: {e}")
        return {}

# db_manager.py

def buscar_itens_pendentes():
    try:
        conn = sqlite3.connect(DB_NAME)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        query = """
            SELECT 
                ig.id, 
                ig.codigo_analise,
                nf.numero_nota, 
                nf.data_nota,
                c.nome_cliente, 
                ig.codigo_produto,
                ig.ressarcimento -- Linha adicionada
            FROM ItensGarantia ig
            JOIN NotasFiscais nf ON ig.id_nota_fiscal = nf.id
            JOIN Clientes c ON nf.cnpj_cliente = c.cnpj
            WHERE ig.status = 'Pendente de Análise'
            ORDER BY nf.data_nota
        """
        cursor.execute(query)
        itens = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return itens
    except sqlite3.Error as e:
        print(f"Erro ao buscar itens pendentes: {e}")
        return []

# db_manager.py

def buscar_garantias_filtradas(filtros):
    try:
        conn = sqlite3.connect(DB_NAME)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        query = """
            SELECT 
                ig.id, nf.numero_nota, nf.data_nota, c.cnpj, c.nome_cliente,
                ig.codigo_analise, ig.codigo_produto, ig.status, 
                ig.procedente_improcedente, ig.valor_item,
                ig.ressarcimento -- CAMPO ADICIONADO
            FROM ItensGarantia ig
            JOIN NotasFiscais nf ON ig.id_nota_fiscal = nf.id
            JOIN Clientes c ON nf.cnpj_cliente = c.cnpj
        """
        
        condicoes = []
        parametros = []
        
        if filtros['cnpj']:
            condicoes.append("c.cnpj LIKE ?")
            parametros.append(f"%{filtros['cnpj']}%")
        if filtros['razao_social']:
            condicoes.append("c.nome_cliente LIKE ?")
            parametros.append(f"%{filtros['razao_social']}%")
        if filtros['numero_nota']:
            condicoes.append("nf.numero_nota LIKE ?")
            parametros.append(f"%{filtros['numero_nota']}%")
        if filtros['status'] and filtros['status'] != 'Todos':
            condicoes.append("ig.status = ?")
            parametros.append(filtros['status'])

        if condicoes:
            query += " WHERE " + " AND ".join(condicoes)

        query += " ORDER BY nf.data_nota DESC, nf.numero_nota"
        
        cursor.execute(query, parametros)
        garantias = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return garantias
    except sqlite3.Error as e:
        print(f"Erro ao buscar garantias filtradas: {e}")
        return []


def buscar_detalhes_completos_item(id_item):
    try:
        conn = sqlite3.connect(DB_NAME)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM ItensGarantia WHERE id = ?", (id_item,))
        item = cursor.fetchone()
        conn.close()
        return dict(item) if item else None
    except sqlite3.Error as e:
        print(f"Erro ao buscar detalhes do item: {e}")
        return None

def buscar_grupo_estoque_produto(codigo_produto):
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT grupo_estoque FROM Produtos WHERE codigo_item = ?", (codigo_produto,))
        resultado = cursor.fetchone()
        conn.close()
        return resultado[0] if resultado else None
    except sqlite3.Error as e:
        print(f"Erro ao buscar grupo de estoque: {e}")
        return None

def obter_proximo_numero_analise(letra_mes):
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT codigo_analise FROM ItensGarantia WHERE codigo_analise LIKE ? ORDER BY codigo_analise DESC LIMIT 1",
            (f"{letra_mes}%",)
        )
        ultimo_codigo = cursor.fetchone()
        conn.close()
        
        if ultimo_codigo:
            numero = int(ultimo_codigo[0][1:])
            return numero + 1
        else:
            return 1
    except sqlite3.Error as e:
        print(f"Erro ao obter próximo número de análise: {e}")
        return 1

# --- NOVAS FUNÇÕES PARA POPULAR OS FILTROS ---
def obter_anos_disponiveis():
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        query = "SELECT DISTINCT STRFTIME('%Y', data_lancamento) FROM NotasFiscais WHERE data_lancamento IS NOT NULL ORDER BY 1 DESC"
        cursor.execute(query)
        anos = [row[0] for row in cursor.fetchall()]
        conn.close()
        return anos
    except sqlite3.Error as e:
        print(f"Erro ao obter anos disponíveis: {e}")
        return []

def obter_nomes_clientes():
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        query = "SELECT DISTINCT nome_cliente FROM Clientes ORDER BY nome_cliente"
        cursor.execute(query)
        clientes = [row[0] for row in cursor.fetchall()]
        conn.close()
        return clientes
    except sqlite3.Error as e:
        print(f"Erro ao obter nomes de clientes: {e}")
        return []

def obter_codigos_produtos():
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        query = "SELECT DISTINCT codigo_item FROM Produtos ORDER BY codigo_item"
        cursor.execute(query)
        produtos = [row[0] for row in cursor.fetchall()]
        conn.close()
        return produtos
    except sqlite3.Error as e:
        print(f"Erro ao obter códigos de produtos: {e}")
        return []

# db_manager.py

def buscar_dados_completos_para_gestao(filtros={}):
    try:
        conn = sqlite3.connect(DB_NAME)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        base_query = """
            SELECT
                ig.id, nf.data_lancamento, nf.numero_nota, nf.data_nota,
                c.cnpj, c.nome_cliente, c.grupo_cliente,
                ig.codigo_analise, ig.codigo_produto, p.grupo_estoque,
                ig.codigo_avaria, ig.valor_item, ig.status, 
                ig.procedente_improcedente, ig.ressarcimento,
                ig.numero_serie, -- CAMPO ADICIONADO
                ig.fornecedor    -- CAMPO ADICIONADO
            FROM ItensGarantia AS ig
            LEFT JOIN NotasFiscais AS nf ON ig.id_nota_fiscal = nf.id
            LEFT JOIN Clientes AS c ON nf.cnpj_cliente = c.cnpj
            LEFT JOIN Produtos AS p ON ig.codigo_produto = p.codigo_item
        """
        
        condicoes = []
        parametros = []
        
        if filtros.get('ano'):
            condicoes.append("STRFTIME('%Y', nf.data_lancamento) = ?")
            parametros.append(filtros['ano'])
        if filtros.get('mes'):
            condicoes.append("STRFTIME('%m', nf.data_lancamento) = ?")
            parametros.append(filtros['mes'])
        if filtros.get('cliente'):
            condicoes.append("c.nome_cliente = ?")
            parametros.append(filtros['cliente'])
        if filtros.get('produto'):
            condicoes.append("ig.codigo_produto = ?")
            parametros.append(filtros['produto'])
            
        if condicoes:
            base_query += " WHERE " + " AND ".join(condicoes)
            
        base_query += " ORDER BY nf.data_lancamento DESC, ig.id DESC"
        
        cursor.execute(base_query, parametros)
        dados = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return dados
    except sqlite3.Error as e:
        print(f"Erro ao buscar dados para gestão: {e}")
        return []

# --- FUNÇÃO ATUALIZADA PARA ACEITAR MAIS FILTROS ---
def obter_estatisticas_garantia(filtros={}):
    try:
        conn = sqlite3.connect(DB_NAME)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        base_from = "FROM ItensGarantia ig JOIN NotasFiscais nf ON ig.id_nota_fiscal = nf.id LEFT JOIN Clientes c ON nf.cnpj_cliente = c.cnpj"
        
        condicoes = []
        params = []
        if filtros.get('ano'):
            condicoes.append("STRFTIME('%Y', nf.data_lancamento) = ?")
            params.append(filtros['ano'])
        if filtros.get('mes'):
            condicoes.append("STRFTIME('%m', nf.data_lancamento) = ?")
            params.append(filtros['mes'])
        if filtros.get('cliente'):
            condicoes.append("c.nome_cliente = ?")
            params.append(filtros['cliente'])
        if filtros.get('produto'):
            condicoes.append("ig.codigo_produto = ?")
            params.append(filtros['produto'])

        where_sql = " AND ".join(condicoes) if condicoes else "1=1"
        
        query = f"""
            SELECT 'Procedente' as categoria, COUNT(ig.id) as quantidade, SUM(ig.valor_item) as valor_total
            {base_from} WHERE ig.procedente_improcedente = 'Procedente' AND {where_sql}
            UNION ALL
            SELECT 'Improcedente' as categoria, COUNT(ig.id) as quantidade, SUM(ig.valor_item) as valor_total
            {base_from} WHERE ig.procedente_improcedente = 'Improcedente' AND {where_sql}
            UNION ALL
            SELECT 'Pendente' as categoria, COUNT(ig.id) as quantidade, SUM(ig.valor_item) as valor_total
            {base_from} WHERE ig.status = 'Pendente de Análise' AND {where_sql}
        """
        
        final_params = params * 3
        cursor.execute(query, final_params)
        resultados = cursor.fetchall()
        conn.close()
        
        estatisticas = {'Procedente': {'quantidade': 0, 'valor_total': 0}, 'Improcedente': {'quantidade': 0, 'valor_total': 0}, 'Pendente': {'quantidade': 0, 'valor_total': 0}}
        for row in resultados:
            cat = row['categoria']
            if cat in estatisticas:
                estatisticas[cat]['quantidade'] = row['quantidade'] or 0
                estatisticas[cat]['valor_total'] = row['valor_total'] or 0
        return estatisticas
    except sqlite3.Error as e:
        print(f"Erro ao obter estatísticas: {e}")
        return {}

# --- FUNÇÃO ATUALIZADA PARA ACEITAR MAIS FILTROS ---


def obter_estatisticas_ressarcimento(filtros={}):
    try:
        conn = sqlite3.connect(DB_NAME)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        base_from = "FROM ItensGarantia ig JOIN NotasFiscais nf ON ig.id_nota_fiscal = nf.id LEFT JOIN Clientes c ON nf.cnpj_cliente = c.cnpj"

        condicoes = ["ig.ressarcimento IS NOT NULL", "CAST(ig.ressarcimento AS REAL) > 0"]
        params = []

        if filtros.get('ano'):
            condicoes.append("STRFTIME('%Y', nf.data_lancamento) = ?")
            params.append(filtros['ano'])
        if filtros.get('mes'):
            condicoes.append("STRFTIME('%m', nf.data_lancamento) = ?")
            params.append(filtros['mes'])
        if filtros.get('cliente'):
            condicoes.append("c.nome_cliente = ?")
            params.append(filtros['cliente'])
        if filtros.get('produto'):
            condicoes.append("ig.codigo_produto = ?")
            params.append(filtros['produto'])
            
        where_sql = " WHERE " + " AND ".join(condicoes)
        
        query = f"""
            SELECT
                SUM(CASE WHEN ig.procedente_improcedente = 'Procedente' THEN CAST(ig.ressarcimento AS REAL) ELSE 0 END) as valor_procedente,
                COUNT(CASE WHEN ig.procedente_improcedente = 'Procedente' AND CAST(ig.ressarcimento AS REAL) > 0 THEN ig.id END) as qtd_procedente,

                SUM(CASE WHEN ig.procedente_improcedente = 'Improcedente' THEN CAST(ig.ressarcimento AS REAL) ELSE 0 END) as valor_improcedente,
                COUNT(CASE WHEN ig.procedente_improcedente = 'Improcedente' THEN ig.id END) as qtd_improcedente,

                -- ALTERAÇÃO AQUI: Mudado de ig.valor_item para ig.ressarcimento
                SUM(CASE WHEN ig.status = 'Pendente de Análise' THEN CAST(ig.ressarcimento AS REAL) ELSE 0 END) as valor_pendente,
                COUNT(CASE WHEN ig.status = 'Pendente de Análise' THEN ig.id END) as qtd_pendente
            {base_from}
            {where_sql}
        """
        
        cursor.execute(query, params)
        row = cursor.fetchone()
        conn.close()
        
        estatisticas = {
            'Procedente': {'quantidade': row['qtd_procedente'] or 0, 'valor_total': row['valor_procedente'] or 0},
            'Improcedente': {'quantidade': row['qtd_improcedente'] or 0, 'valor_total': row['valor_improcedente'] or 0},
            'Pendente': {'quantidade': row['qtd_pendente'] or 0, 'valor_total': row['valor_pendente'] or 0}
        }
        return estatisticas
    except sqlite3.Error as e:
        print(f"Erro ao obter estatísticas de ressarcimento: {e}")
        return {'Procedente': {'quantidade': 0, 'valor_total': 0}, 'Improcedente': {'quantidade': 0, 'valor_total': 0}, 'Pendente': {'quantidade': 0, 'valor_total': 0}}

# =================================================================================
# --- FUNÇÕES DE ESCRITA ---
# =================================================================================


def salvar_nota_e_itens(cnpj, numero_nota, data_nota, itens):
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        data_lancamento = datetime.now().strftime('%Y-%m-%d')
        mes = int(data_lancamento.split('-')[1])
        letra_mes = chr(64 + mes) 
        proximo_numero = obter_proximo_numero_analise(letra_mes)
        cursor.execute("INSERT INTO NotasFiscais (numero_nota, data_nota, cnpj_cliente, data_lancamento) VALUES (?, ?, ?, ?)", (numero_nota, data_nota, cnpj, data_lancamento))
        id_nota_fiscal = cursor.lastrowid
        for item in itens:
            grupo_do_produto = buscar_grupo_estoque_produto(item['codigo'])
            e_tucho = (grupo_do_produto == 'TUCHOS HIDRAULICOS')
            codigo_analise_item = None
            if e_tucho:
                codigo_analise_item = f"{letra_mes}{proximo_numero:03d}"
                proximo_numero += 1
            for _ in range(item['quantidade']):
                codigo_final = None
                if e_tucho:
                    codigo_final = codigo_analise_item
                else:
                    codigo_final = f"{letra_mes}{proximo_numero:03d}"
                    proximo_numero += 1
                
                # Comando INSERT atualizado para incluir 'ressarcimento'
                sql_insert = "INSERT INTO ItensGarantia (id_nota_fiscal, codigo_produto, valor_item, codigo_analise, ressarcimento) VALUES (?, ?, ?, ?, ?)"
                params = (id_nota_fiscal, item['codigo'], item['valor'], codigo_final, item.get('ressarcimento'))
                cursor.execute(sql_insert, params)
        
        conn.commit()
        conn.close()
        return True, "Nota fiscal e itens salvos com sucesso!"
    except sqlite3.Error as e:
        if conn: conn.rollback()
        print(f"Erro ao salvar nota fiscal: {e}")
        return False, f"Erro ao salvar nota fiscal: {e}"


def salvar_analise_item(id_item, dados_analise):
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        # Query de UPDATE sem o campo 'ressarcimento'
        query = """
            UPDATE ItensGarantia SET
                status = 'Analisado', codigo_analise = ?, numero_serie = ?,
                codigo_avaria = ?, descricao_avaria = ?, procedente_improcedente = ?,
                produzido_revenda = ?, fornecedor = ?
            WHERE id = ?"""
        
        # Parâmetros sem o valor de ressarcimento
        params = (
            dados_analise['codigo_analise'], dados_analise['numero_serie'], 
            dados_analise['codigo_avaria'], dados_analise['descricao_avaria'], 
            dados_analise['procedente_improcedente'], dados_analise['produzido_revenda'], 
            dados_analise['fornecedor'], 
            id_item
        )
        cursor.execute(query, params)
        conn.commit()
        conn.close()
        return True, "Análise salva com sucesso!"
    except sqlite3.Error as e:
        print(f"Erro ao salvar análise: {e}")
        return False, f"Erro ao salvar análise: {e}"

def excluir_varios_itens(lista_ids):
    if not lista_ids: return True, "Nenhum item selecionado para exclusão."
    conn = None
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        notas_fiscais_afetadas = set()
        placeholders_ids = ','.join('?' for _ in lista_ids)
        query_select_nf = f"SELECT DISTINCT id_nota_fiscal FROM ItensGarantia WHERE id IN ({placeholders_ids})"
        cursor.execute(query_select_nf, lista_ids)
        for row in cursor.fetchall(): notas_fiscais_afetadas.add(row[0])
        query_delete_itens = f"DELETE FROM ItensGarantia WHERE id IN ({placeholders_ids})"
        cursor.execute(query_delete_itens, lista_ids)
        if notas_fiscais_afetadas:
            for id_nota in notas_fiscais_afetadas:
                cursor.execute("SELECT COUNT(*) FROM ItensGarantia WHERE id_nota_fiscal = ?", (id_nota,))
                contagem = cursor.fetchone()[0]
                if contagem == 0:
                    cursor.execute("DELETE FROM NotasFiscais WHERE id = ?", (id_nota,))
        conn.commit()
        quantidade = len(lista_ids)
        singular_plural = "item" if quantidade == 1 else "itens"
        return True, f"{quantidade} {singular_plural} excluído(s) com sucesso."
    except sqlite3.Error as e:
        if conn: conn.rollback()
        print(f"Erro ao excluir múltiplos itens: {e}")
        return False, f"Erro ao excluir itens: {e}"
    finally:
        if conn: conn.close()