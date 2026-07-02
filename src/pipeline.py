from src.config import paths
from src.scripts.extract import extrair_dados
from src.scripts.transform import transformar_dados_finbra

"""
Pipeline principal para preparar os dados para análise, ele
-> 1. percorre todos os arquivos compactados em path_dados_compactos e extrai para path_dados_extraidos
-> 2. junta todos os arquivos extraídos em um único dataframe
-> 3. chama a função de validação do dataframe de entrada com pandera
-> 4. salva o dataframe validado em path_dados_validados
"""


def pipeline_principal():

    # 1. percorre todos os arquivos compactados em path_dados_compactos e extrai para path_dados_extraidos
    for path_arquivo_zip in paths.path_dados_compactos.rglob("*.zip"):
        subpasta_relativa = path_arquivo_zip.relative_to(paths.path_dados_compactos).parent
        caminho_destino_final = paths.path_dados_extraidos / subpasta_relativa / path_arquivo_zip.stem
        extrair_dados(str(path_arquivo_zip), str(caminho_destino_final))

    df = transformar_dados_finbra()
    print(df.head())


if __name__ == "__main__":
    pipeline_principal()
