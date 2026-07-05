import zipfile
from pathlib import Path
import pytest
from src.scripts.extract import extrair_dados


def _criar_zip(caminho_zip: Path, nome_interno: str, conteudo: str) -> None:
    caminho_zip.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(caminho_zip, "w") as zf:
        zf.writestr(nome_interno, conteudo)


class TestExtrairDadosCaminhoFeliz:
    def test_extrai_conteudo_do_zip(self, tmp_path):
        zip_path = tmp_path / "origem" / "finbra.zip"
        _criar_zip(zip_path, "finbra.csv", "col1,col2\n1,2")

        destino = tmp_path / "destino" / "finbra"
        extrair_dados(str(zip_path), str(destino))

        # extrair_dados extrai para a pasta-mãe do destino informado
        arquivo_extraido = destino.parent / "finbra.csv"
        assert arquivo_extraido.exists()
        assert arquivo_extraido.read_text(encoding="utf-8") == "col1,col2\n1,2"

    def test_cria_diretorio_destino_se_nao_existir(self, tmp_path):
        zip_path = tmp_path / "finbra.zip"
        _criar_zip(zip_path, "finbra.csv", "conteudo")

        destino = tmp_path / "pasta" / "que" / "nao" / "existe" / "finbra"
        extrair_dados(str(zip_path), str(destino))

        assert (destino.parent / "finbra.csv").exists()

    def test_e_idempotente_pode_rodar_duas_vezes(self, tmp_path):
        zip_path = tmp_path / "finbra.zip"
        _criar_zip(zip_path, "finbra.csv", "conteudo")

        destino = tmp_path / "saida" / "finbra"
        extrair_dados(str(zip_path), str(destino))
        extrair_dados(str(zip_path), str(destino))  # não pode levantar erro

        assert (destino.parent / "finbra.csv").exists()


class TestExtrairDadosCaminhoAlternativo:
    def test_lanca_file_not_found_error_se_origem_nao_existir(self, tmp_path):
        destino = tmp_path / "destino" / "finbra"

        with pytest.raises(FileNotFoundError):
            extrair_dados(str(tmp_path / "nao_existe.zip"), str(destino))


class TestExtrairDadosCaminhoTriste:
    def test_lanca_runtime_error_se_zip_estiver_corrompido(self, tmp_path):
        zip_corrompido = tmp_path / "corrompido.zip"
        zip_corrompido.write_text("Não sou um arquivo zip de verdade", encoding="latin-1")

        destino = tmp_path / "destino" / "finbra"

        with pytest.raises(RuntimeError) as exc_info:
            extrair_dados(str(zip_corrompido), str(destino))

        assert "Erro ao extrair dados do arquivo" in str(exc_info.value)
