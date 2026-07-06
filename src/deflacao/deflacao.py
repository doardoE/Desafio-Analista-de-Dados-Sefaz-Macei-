from src.config import paths
from src.deflacao.ipca_utils import busca_numero_indice, deflacionar
import duckdb
import logging


logger = logging.getLogger("deflacao")


def cria_parquet_deflacionado(path_arquivo_dados_originais, path_arquivo_deflacionado) -> None:
    logger.info("Iniciando deflação dos dados finbra.")

    try:
        data_min = int(duckdb.sql(f"SELECT min(ano_exercicio) FROM '{path_arquivo_dados_originais}'").fetchone()[0])
        data_max = int(duckdb.sql(f"SELECT max(ano_exercicio) FROM '{path_arquivo_dados_originais}'").fetchone()[0])

        df_numero_indice = busca_numero_indice(data_min, data_max)
        df_deflacao = deflacionar(df_numero_indice, data_max)

        # salva tabela no duckdb
        duckdb.register("tabela_inflacao", df_deflacao)

        # salva um novo parquet com valores deflacionados calculados
        duckdb.sql(f"""
            COPY (
                SELECT
                    f.*,
                    f.valor AS valor_nominal,
                    ROUND(f.valor * i.deflacao, 2) AS valor_real
                FROM "{path_arquivo_dados_originais}" f
                LEFT JOIN tabela_inflacao i
                    ON f.ano_exercicio = i.ano
            )
            TO '{path_arquivo_deflacionado}'
            (FORMAT PARQUET);
        """)

        logger.info(".parquet com valores deflacionados criado criada com sucesso.")

    except Exception:
        logger.exception("Erro ao criar arquivo .parquet (finbra_deflacionado).")
        raise


if __name__ == "__main__":
    cria_parquet_deflacionado(paths.dados, paths.dados_deflacionados)
