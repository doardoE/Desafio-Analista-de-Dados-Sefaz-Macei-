import zipfile
from pathlib import Path
import logging

logger = logging.getLogger("extract")


# Função para extrair dados de um arquivo compactado e salvar em outro local.
def extrair_dados(path_origem: str, path_destino: str):

    if not Path(path_origem).exists():
        raise FileNotFoundError(f"O arquivo de origem '{path_origem}' não foi encontrado.")

    Path(path_destino).parent.mkdir(parents=True, exist_ok=True)

    try:
        with zipfile.ZipFile(path_origem, "r") as zip_ref:
            zip_ref.extractall(Path(path_destino).parent)

    except Exception as e:
        logger.error(f"Erro ao extrair dados do arquivo '{path_origem}'")
        raise RuntimeError(f"Erro ao extrair dados do arquivo '{path_origem}': {e}")
