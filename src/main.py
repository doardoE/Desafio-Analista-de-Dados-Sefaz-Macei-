import logging
import subprocess
import sys

from src.pipeline import pipeline_principal
from src.deflacao.deflacao import cria_parquet_deflacionado
from src.query_descritiva import cria_view_dados_analise_descritiva
from src.config.Paths import paths
from src.config.ConexaoBanco import db
from src.config.logs import configura_log

logger = logging.getLogger("main")


def executar_notebook(path_notebooks, nome_arquivo) -> None:
    subprocess.run(
        [
            sys.executable,
            "-m",
            "nbconvert",
            "--execute",
            str(path_notebooks / nome_arquivo),
            "--to",
            "notebook",
            "--inplace",
        ],
        capture_output=True,
        check=True,
    )
    logger.info(f"Notebook {nome_arquivo} executado com sucesso.")


if __name__ == "__main__":
    configura_log()
    logger.info("Iniciando execução do main.py...")

    pipeline_principal(paths.path_dados_compactos, paths.path_dados_extraidos, paths.path_dados_processados)

    # adiciona após o pipeline principal a função de deflação dos dados e criação da view
    cria_parquet_deflacionado(paths.dados, paths.dados_deflacionados)
    logger.info("Deflação de dados concluída.")

    # cria view geral
    db.con.sql(f"CREATE OR REPLACE VIEW finbra AS SELECT * FROM '{paths.dados_deflacionados}';")

    # cria view para analise descritiva
    cria_view_dados_analise_descritiva(db.con)
    logger.info("Views no Duckdb criadas.")

    # fecha conexão com banco e reexecuta os notebooks do zero (banco como readonly) e atualiza as saídas
    logger.info("Iniciando execução dos Notebooks...")
    db.close()
    executar_notebook(paths.notebooks, "analise_exploratoria.ipynb")
    executar_notebook(paths.notebooks, "analise_descritiva.ipynb")
    logger.info("Execução do main.py concluída com sucesso.")
