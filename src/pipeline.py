from config import paths
from scripts.extract import extrair_dados

"""
Pipeline principal para preparar os dados para análise, ele
-> 1. percorre todos os arquivos compactados em path_base_origem e extrai para path_base_destino
-> 2. junta todos os arquivos extraídos em um único dataframe
-> 3. chama a função de validação do dataframe de entrada com pandera
-> 4. salva o dataframe validado em path_base_destino
"""


def pipeline_principal():

    # 1. percorre todos os arquivos compactados em path_base_origem e extrai para path_base_destino
    for path_arquivo_zip in paths.path_dados_compactos.rglob("*.zip"):
        subpasta_relativa = path_arquivo_zip.relative_to(
            paths.path_dados_compactos
        ).parent
        caminho_destino_final = (
            paths.path_dados_extraidos / subpasta_relativa / path_arquivo_zip.stem
        )
        extrair_dados(str(path_arquivo_zip), str(caminho_destino_final))


if __name__ == "__main__":
    pipeline_principal()
