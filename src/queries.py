import duckdb


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


def soma_valores_deflacionados_por_ano(con):
    return con.sql("""
        WITH anos_validos AS (
            SELECT ano_exercicio
            FROM finbra
            GROUP BY ano_exercicio
            HAVING COUNT(DISTINCT uf) = 26
        )
            
        SELECT ano_exercicio, SUM(valor_nominal), SUM(valor_real)
        FROM finbra
        WHERE ano_exercicio IN (SELECT ano_exercicio FROM anos_validos)
        GROUP BY ano_exercicio
    """)


def frequencia_valor_municipio(con, mun: str):
    return con.sql(f"""
    SELECT 
        ano_exercicio,
        regexp_extract(instituicao, 'Prefeitura Municipal (?:de|do|da) (.*) - [A-Z]{2}', 1) AS municipio,
        valor_real
    FROM finbra
    WHERE municipio = '{mun}' OR uf = '{mun}'
""")


def frequencia_valor_ano(con, ano):
    return con.sql(f"""
    SELECT valor_real
    FROM finbra
    WHERE ano_exercicio = '{ano}'
""")


if __name__ == "__main__":
    con = duckdb.connect("dados.duckdb")
