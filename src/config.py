from dataclasses import dataclass
from pathlib import Path
import logging
import sys


@dataclass
class Paths:
    # Define o diretório raiz do projeto
    _root: Path = Path(__file__).parent.parent

    @property
    def path_dados_compactos(self) -> Path:
        return self._root / "dados_compactos"

    @property
    def path_dados_extraidos(self) -> Path:
        return self._root / "dados_extraidos"

    @property
    def path_dados_processados(self) -> Path:
        return self._root / "dados_processados"

    @property
    def dados(self) -> Path:
        return self._root / "dados_processados" / "finbra.parquet"

    @property
    def dados_deflacionados(self) -> Path:
        return self._root / "dados_processados" / "finbra_deflacionado.parquet"


paths = Paths()


class DataFrameConfig:
    # Configurações do DataFrame
    sep: str = ";"
    skiprows: int = 3
    encoding: str = "latin-1"
    decimal: str = ","
    thousands: str = "."

    colunas: dict = {
        "Instituição": "instituicao",
        "Cod.IBGE": "cod_ibge",
        "UF": "uf",
        "População": "populacao",
        "Coluna": "etapa_despesa",
        "Conta": "conta",
        "Identificador da Conta": "identificador_conta",
        "Valor": "valor",
    }

    dict_funcao: dict[str, str] = {
        "01": "Legislativa",
        "02": "Judiciária",
        "03": "Essencial à Justiça",
        "04": "Administração",
        "05": "Defesa Nacional",
        "06": "Segurança Pública",
        "07": "Relações Exteriores",
        "08": "Assistência Social",
        "09": "Previdência Social",
        "10": "Saúde",
        "11": "Trabalho",
        "12": "Educação",
        "13": "Cultura",
        "14": "Direitos da Cidadania",
        "15": "Urbanismo",
        "16": "Habitação",
        "17": "Saneamento",
        "18": "Gestão Ambiental",
        "19": "Ciência e Tecnologia",
        "20": "Agricultura",
        "22": "Indústria",
        "23": "Comércio e Serviços",
        "24": "Comunicações",
        "25": "Energia",
        "26": "Transporte",
        "27": "Desporto e Lazer",
        "28": "Encargos Especiais",
    }


df_config = DataFrameConfig()


logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler(f"{paths._root}/execucao_projeto.log", mode="a", encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)

# Silencia logs de depuração visuais que poluem o Jupyter e o terminal
logging.getLogger("matplotlib").setLevel(logging.WARNING)
logging.getLogger("PIL").setLevel(logging.WARNING)
