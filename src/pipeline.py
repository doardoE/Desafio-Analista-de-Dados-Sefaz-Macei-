from pathlib import Path
from src.config.Paths import paths
from src.config.ConexaoBanco import db
from src.config.logs import configura_log
from src.scripts.extract import extrair_dados
from src.scripts.transform import transformar_dados_finbra
from src.scripts.validate import validar_dataframe
from src.deflacao.deflacao import cria_parquet_deflacionado
import logging


"""
Pipeline principal para preparar os dados para análise, ele
-> 1. percorre todos os arquivos compactados em path_dados_compactos e extrai para path_dados_extraidos
-> 2. junta todos os arquivos extraídos em um único dataframe
-> 3. chama a função de validação do dataframe de entrada com pandera
-> 4. salva o dataframe validado em path_dados_validados (finbra.parquet)
-> .. Faz deflação dos valores e salva um novo parquet (finbra_deflacionado.parquet)
-> .. Cria uma view desses dados para utilizar nos notebooks python
"""

logger = logging.getLogger("pipeline")


def pipeline_principal(path_compactos: Path, path_extraidos: Path, path_processados: Path):
    logger.info("Iniciando pipeline principal...")

    # adiciona métricas para logs
    list_path_compactos = list(path_compactos.rglob("*.zip"))
    if len(list_path_compactos) == 0:
        logger.warning("Nenhum arquivo compactado encontrado em path_dados_compactos.")
        return

    # 1. percorre todos os arquivos compactados em path_dados_compactos e extrai para path_dados_extraidos
    for path_arquivo_zip in list_path_compactos:
        subpasta_relativa = path_arquivo_zip.relative_to(path_compactos).parent
        caminho_destino_final = path_extraidos / subpasta_relativa / path_arquivo_zip.stem
        extrair_dados(str(path_arquivo_zip), str(caminho_destino_final))
    logger.info("Extração de dados concluída.")

    # 2. junta todos os arquivos extraídos em um único dataframe
    list_path_extraidos = list(path_extraidos.rglob("*.csv"))
    df = transformar_dados_finbra(list_path_extraidos, path_extraidos)
    logger.info("Transformação de dados concluída.")

    # 3. chama a função de validação do dataframe de entrada com pandera
    df = validar_dataframe(df)
    logger.info("Validação de dados concluída")

    # 4. salva o dataframe validado em path_dados_processados
    path_processados.mkdir(parents=True, exist_ok=True)
    caminho_final = path_processados / "finbra.parquet"
    df.to_parquet(caminho_final, index=False)
    logger.info("Salvamento de dados concluído.")

    # adiciona métricas para logs
    logger.info("Pipeline concluído com sucesso.")
    logger.info(f"- Total de arquivos compactados encontrados: {len(list_path_compactos)}")
    logger.info(f"- Total de arquivos CSV extraídos: {len(list_path_extraidos)}")
    logger.info(f"- Total de linhas no dataframe validado: {len(df)}")


if __name__ == "__main__":
    configura_log()
    pipeline_principal(paths.path_dados_compactos, paths.path_dados_extraidos, paths.path_dados_processados)

    # adiciona após o pipeline principal a função de deflação dos dados e criação da view
    cria_parquet_deflacionado(paths.dados, paths.dados_deflacionados)

    db.con.sql(f"CREATE OR REPLACE VIEW finbra AS SELECT * FROM '{paths.dados_deflacionados}';")
