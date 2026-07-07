def tabela_completa(con):
    return con.sql("SELECT * FROM finbra;")


def summarize(con):
    return con.sql("SUMMARIZE SELECT * FROM finbra;")


def completude_dados(con):
    return con.sql("""
        SELECT ano_exercicio, COUNT(DISTINCT uf) AS 'qtd_capitais'
        FROM finbra
        GROUP BY ano_exercicio
        ORDER BY ano_exercicio;
    """)


def capitais_assiduas(con):
    """aqui são as capitais que entregaram dados em todos os anos para análise junto de 2025,
    trazendo as análises dessas, o mais perto do presente."""

    return con.sql("""
        SELECT
            regexp_extract(instituicao, 'Prefeitura Municipal (?:de|do|da) (.*) - [A-Z]{2}', 1) AS municipio,
            uf
        FROM finbra
        GROUP BY uf, municipio
        HAVING COUNT(DISTINCT ano_exercicio) = (
            SELECT COUNT(DISTINCT ano_exercicio) FROM finbra
        )
        ORDER BY uf;
    """)


def anos_assiduos(con) -> list:
    # .fetchall() extrai os dados direto do DuckDB como uma lista de tuplas: [(2020,), (2021,)]
    resultados = con.sql("""
        SELECT ano_exercicio
        FROM finbra
        GROUP BY ano_exercicio
        HAVING COUNT(DISTINCT uf) = 26
    """).fetchall()

    # Usamos uma list comprehension para extrair o número de dentro da tupla e retornar uma lista limpa: [2020, 2021]
    return [linha[0] for linha in resultados]


def soma_valores_deflacionados_pagas_por_ano(con):
    anos_validos = anos_assiduos(con)
    return con.sql(f"""
        SELECT ano_exercicio, SUM(valor_nominal), SUM(valor_real)
        FROM finbra
        WHERE ano_exercicio IN {anos_validos}
        AND etapa_despesa = 'Despesas Pagas'
        GROUP BY ano_exercicio
    """)


def frequencia_categoria(con, coluna: str, top_n: int = 15):
    """Retorna a contagem de frequência de uma coluna categórica específica,
    Colunas recomendadas: 'etapa_despesa', 'nome_funcao', 'nome_subfuncao"""

    # Lista de colunas permitidas para evitar SQL Injection dinâmico
    colunas_validas = ["etapa_despesa", "nome_funcao", "nome_subfuncao"]
    if coluna not in colunas_validas:
        raise ValueError(f"Coluna inválida. Escolha entre: {colunas_validas}")

    return con.sql(f"""
        SELECT 
            {coluna} AS categoria, 
            COUNT(*) AS contagem,
            ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM finbra), 2) AS percentual
        FROM finbra
        WHERE {coluna} IS NOT NULL
        GROUP BY {coluna}
        ORDER BY contagem DESC
        LIMIT {top_n};
    """)


def soma_valores_por_etapas(con):
    anos_validos = anos_assiduos(con)
    return con.sql(f"""
        SELECT
            etapa_despesa,
            ROUND(SUM(valor_real), 2) AS total_valor_real,
            ROUND(SUM(valor_real) / 1000000, 2) AS total_valor_milhoes,
            ROUND(SUM(valor_real) / SUM(populacao), 2) AS despesa_per_capita
        FROM finbra
        WHERE ano_exercicio IN {anos_validos}
        GROUP BY etapa_despesa
        ORDER BY despesa_per_capita DESC
    """)


""" despesas real e per-capta de funções por ano válido. """


def funcoes_por_valor_ano(con):
    return con.sql(f"""
        SELECT
            cod_funcao,
            nome_funcao,
            ROUND(SUM(valor_real) / SUM(populacao), 2) AS total_valor_per_capta,
            ROUND(AVG(valor_real / populacao), 2) AS media_valor_per_capta,
            FROM finbra
            WHERE ano_exercicio IN {anos_assiduos(con)}
            AND etapa_despesa = 'Despesas Pagas'
            AND cod_funcao IS NOT NULL
            GROUP BY cod_funcao, nome_funcao
            ORDER BY media_valor_per_capta DESC
    """)
