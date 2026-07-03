from src.config import paths
from src.scripts.extract import extrair_dados
from src.scripts.transform import transformar_dados_finbra
from src.scripts.validate import validar_dataframe
import logging

"""
Pipeline principal para preparar os dados para análise, ele
-> 1. percorre todos os arquivos compactados em path_dados_compactos e extrai para path_dados_extraidos
-> 2. junta todos os arquivos extraídos em um único dataframe
-> 3. chama a função de validação do dataframe de entrada com pandera
-> 4. salva o dataframe validado em path_dados_validados
"""

logger = logging.getLogger("pipeline")


def pipeline_principal():
    logger.info("Iniciando pipeline principal...")

    # adiciona métricas para logs
    total_arquivos_zip = len(list(paths.path_dados_compactos.rglob("*.zip")))
    if total_arquivos_zip == 0:
        logger.warning("Nenhum arquivo compactado encontrado em path_dados_compactos.")
        return

    # 1. percorre todos os arquivos compactados em path_dados_compactos e extrai para path_dados_extraidos
    for path_arquivo_zip in paths.path_dados_compactos.rglob("*.zip"):
        subpasta_relativa = path_arquivo_zip.relative_to(paths.path_dados_compactos).parent
        caminho_destino_final = paths.path_dados_extraidos / subpasta_relativa / path_arquivo_zip.stem
        extrair_dados(str(path_arquivo_zip), str(caminho_destino_final))
    logger.info("Extração de dados concluída.")

    # 2. junta todos os arquivos extraídos em um único dataframe
    df = transformar_dados_finbra()
    logger.info("Transformação de dados concluída.")

    # 3. chama a função de validação do dataframe de entrada com pandera
    df = validar_dataframe(df)
    logger.info("Validação de dados concluída")

    # 4. salva o dataframe validado em path_dados_processados
    paths.path_dados_processados.mkdir(parents=True, exist_ok=True)
    caminho_final = paths.path_dados_processados / "finbra.parquet"
    df.to_parquet(caminho_final, index=False)
    logger.info("Salvamento de dados concluído.")

    # adiciona métricas para logs
    len_csvs = len(list(paths.path_dados_extraidos.rglob("*.csv")))
    logger.info("Pipeline concluído com sucesso.")
    logger.info(f"- Total de arquivos compactados encontrados: {total_arquivos_zip}")
    logger.info(f"- Total de arquivos CSV extraídos: {len_csvs}")
    logger.info(f"- Total de linhas no dataframe validado: {len(df)}")


if __name__ == "__main__":
    pipeline_principal()
