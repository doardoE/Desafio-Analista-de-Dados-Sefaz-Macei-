from dataclasses import dataclass
from pathlib import Path


@dataclass
class Paths:
    # Define o diretório raiz do projeto
    _root: Path = Path(__file__).parent.parent.parent

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

    @property
    def banco_dados(self) -> Path:
        return self._root / "database.duckdb"

    @property
    def notebooks(self) -> Path:
        return self._root / "notebooks"


paths = Paths()
