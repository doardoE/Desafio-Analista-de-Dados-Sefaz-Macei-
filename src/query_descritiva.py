from src.config.ConexaoBanco import db
from src.query_exploratoria import anos_assiduos


def cria_view_dados_filtrados(con):
    funcoes_assiduas = ["Saúde", "Educação", "Cultura"]
    return con.sql(f"""
        CREATE OR REPLACE VIEW dados_filtrados AS SELECT
            instituicao,
            uf,
            ano_exercicio,
            nome_funcao,
            nome_subfuncao,
            populacao,
            SUM(CASE WHEN etapa_despesa = 'Despesas Empenhadas' THEN valor_real END) AS valor_empenhado,
            SUM(CASE WHEN etapa_despesa = 'Despesas Liquidadas' THEN valor_real END) AS valor_liquidado,
            SUM(CASE WHEN etapa_despesa = 'Despesas Pagas' THEN valor_real END) AS valor_pago,
            SUM(CASE WHEN etapa_despesa = 'Inscrição de Restos a Pagar Não Processados' THEN valor_real END) AS valor_restos_a_pagar_nao_processados,
            SUM(CASE WHEN etapa_despesa = 'Inscrição de Restos a Pagar Processados' THEN valor_real END) AS valor_restos_a_pagar_processados
        FROM finbra
        WHERE nome_funcao IN {funcoes_assiduas}
        AND ano_exercicio IN {anos_assiduos(con)}
        GROUP BY instituicao, uf, ano_exercicio, nome_funcao, nome_subfuncao, populacao;
    """)


def tabela_filtrada(con):
    return con.sql("SELECT * FROM dados_filtrados")


def tabela_com_taxa_execucao(con):
    return con.sql("""
        WITH dados_nacionais AS (
            SELECT 
                ano_exercicio,
                nome_funcao,
                SUM(valor_empenhado) AS total_empenhado,
                SUM(valor_pago) AS total_pago
            FROM dados_filtrados
            GROUP BY ano_exercicio, nome_funcao
        )
        SELECT 
            *,
            CASE 
                WHEN total_empenhado > 0 THEN (total_pago / total_empenhado) * 100 
                ELSE 0 
            END AS taxa_execucao
        FROM dados_nacionais
        ORDER BY ano_exercicio, nome_funcao;
    """)


def obter_dados_pagamento_vs_divida(con):
    return con.sql("""
        WITH acumulado_capital AS (
            SELECT 
                regexp_extract(instituicao, 'Prefeitura Municipal (?:de|do|da) (.*)', 1) AS municipio,
                nome_funcao,
                SUM(valor_empenhado) AS total_empenhado,
                SUM(valor_pago) AS total_pago,
                SUM(
                   COALESCE(valor_restos_a_pagar_nao_processados, 0) +
                   COALESCE(valor_restos_a_pagar_processados, 0)
                ) AS total_restos
            FROM dados_filtrados
            GROUP BY municipio, nome_funcao
        )
        SELECT 
            municipio,
            nome_funcao,
            CASE WHEN total_empenhado > 0 THEN total_pago / total_empenhado ELSE 0 END AS indice_pagamento,
            CASE WHEN total_empenhado > 0 THEN total_restos / total_empenhado ELSE 0 END AS taxa_residual
        FROM acumulado_capital
        WHERE total_empenhado > 0;
    """)


tabela_filtrada(db.con).show()
