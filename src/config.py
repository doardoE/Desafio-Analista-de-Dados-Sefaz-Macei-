from dataclasses import dataclass
from pathlib import Path


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


paths = Paths()
