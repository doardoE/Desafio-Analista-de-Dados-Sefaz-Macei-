import zipfile
import pandas as pd
import pandera.errors
import pytest
from pathlib import Path
from src.pipeline import pipeline_principal


def _cria_zip_com_csv(caminho_zip: Path, conteudo_csv: str, nome_csv: str = "finbra_test.csv") -> None:
    caminho_zip.parent.mkdir(parents=True, exist_ok=True)
    csv_temporario = caminho_zip.parent / nome_csv
    csv_temporario.write_text(conteudo_csv, encoding="latin-1")
    with zipfile.ZipFile(caminho_zip, "w") as z:
        z.write(csv_temporario, arcname=nome_csv)
    csv_temporario.unlink()


def _conteudo_csv_valido(ano: int = 2026) -> str:
    """Conteúdo de um CSV no layout real do FINBRA, com 2 linhas que
    respeitam 100% o schema do pandera.
    """
    return (
        f"Exercício: {ano}\n"
        "Escopo: Municipios\n"
        "Tabela: Despesas de Teste\n"
        "Instituição;Cod.IBGE;UF;População;Coluna;Conta;Identificador da Conta;Valor\n"
        "Prefeitura;2704302;AL;100000;Despesas Empenhadas;01 - Legislativa;id_teste;1500,50\n"
        "Prefeitura;2704302;AL;100000;Despesas Empenhadas;01.031 - Ação Legislativa;id_teste;500,00\n"
    )


class TestPipelinePrincipalCaminhoFeliz:
    def test_pipeline_completo_gera_parquet_valido(self, tmp_path):
        compactos = tmp_path / "compactos"
        extraidos = tmp_path / "extraidos"
        processados = tmp_path / "processados"
        _cria_zip_com_csv(compactos / "dados.zip", _conteudo_csv_valido(ano=2026))

        pipeline_principal(compactos, extraidos, processados)

        assert len(list(extraidos.rglob("*.csv"))) == 1

        caminho_parquet = processados / "finbra.parquet"
        assert caminho_parquet.exists()

        df_final = pd.read_parquet(caminho_parquet)
        assert len(df_final) == 2
        assert (df_final["ano_exercicio"] == 2026).all()
        assert df_final.loc[0, "cod_funcao"] == "01"
        assert df_final.loc[0, "nome_funcao"] == "Legislativa"
        assert df_final.loc[1, "cod_subfuncao"] == "01.031"
        assert df_final.loc[1, "nome_subfuncao"] == "Ação Legislativa"

    def test_pipeline_processa_e_concatena_multiplos_arquivos_zip(self, tmp_path):
        compactos = tmp_path / "compactos"
        extraidos = tmp_path / "extraidos"
        processados = tmp_path / "processados"
        _cria_zip_com_csv(compactos / "dados_2025.zip", _conteudo_csv_valido(ano=2025), nome_csv="a.csv")
        _cria_zip_com_csv(compactos / "dados_2026.zip", _conteudo_csv_valido(ano=2026), nome_csv="b.csv")

        pipeline_principal(compactos, extraidos, processados)

        df_final = pd.read_parquet(processados / "finbra.parquet")
        assert len(df_final) == 4
        assert set(df_final["ano_exercicio"].unique()) == {2025, 2026}


class TestPipelinePrincipalCaminhoAlternativo:
    def test_pipeline_nao_faz_nada_se_pasta_de_compactos_nao_existir(self, tmp_path):
        compactos = tmp_path / "compactos"  # nunca criada
        extraidos = tmp_path / "extraidos"
        processados = tmp_path / "processados"

        pipeline_principal(compactos, extraidos, processados)

        assert not extraidos.exists()
        assert not processados.exists()

    def test_pipeline_nao_faz_nada_se_nao_houver_zips(self, tmp_path):
        compactos = tmp_path / "compactos"
        extraidos = tmp_path / "extraidos"
        processados = tmp_path / "processados"
        compactos.mkdir()

        pipeline_principal(compactos, extraidos, processados)

        assert not processados.exists()

    def test_pipeline_falha_na_validacao_se_zip_nao_tiver_nenhum_csv(self, tmp_path):
        compactos = tmp_path / "compactos"
        extraidos = tmp_path / "extraidos"
        processados = tmp_path / "processados"
        compactos.mkdir()

        arquivo_txt = compactos / "test.txt"
        arquivo_txt.write_text("nada de CSV aqui", encoding="utf-8")

        with zipfile.ZipFile(compactos / "dados.zip", "w") as z:
            z.write(arquivo_txt, arcname="test.txt")

        with pytest.raises(pandera.errors.SchemaErrors):
            pipeline_principal(compactos, extraidos, processados)

        assert not processados.exists()


class TestPipelinePrincipalCaminhoTriste:
    def test_pipeline_propaga_erro_real_de_extracao_se_zip_estiver_corrompido(self, tmp_path):
        compactos = tmp_path / "compactos"
        extraidos = tmp_path / "extraidos"
        processados = tmp_path / "processados"
        compactos.mkdir()
        (compactos / "corrompido.zip").write_text("Não sou um zip de verdade", encoding="latin-1")

        with pytest.raises(RuntimeError, match="Erro ao extrair dados do arquivo"):
            pipeline_principal(compactos, extraidos, processados)

        assert not processados.exists()

    def test_pipeline_propaga_erro_real_de_transformacao_se_csv_estiver_corrompido(self, tmp_path):
        compactos = tmp_path / "compactos"
        extraidos = tmp_path / "extraidos"
        processados = tmp_path / "processados"
        _cria_zip_com_csv(compactos / "dados.zip", "Texto corrompido sem separador de ano\n")

        with pytest.raises(RuntimeError, match="Erro Inesperado ao processar o arquivo"):
            pipeline_principal(compactos, extraidos, processados)

        assert not processados.exists()

    def test_pipeline_propaga_erro_real_de_validacao_se_dado_violar_schema(self, tmp_path):
        """Um CSV com UF inválida (3 letras) deve fazer o `validar_dataframe`
        real rejeitar o DataFrame."""
        compactos = tmp_path / "compactos"
        extraidos = tmp_path / "extraidos"
        processados = tmp_path / "processados"
        conteudo_invalido = (
            "Exercício: 2026\n"
            "Escopo: Municipios\n"
            "Tabela: Despesas de Teste\n"
            "Instituição;Cod.IBGE;UF;População;Coluna;Conta;Identificador da Conta;Valor\n"
            "Prefeitura;2704302;ALX;100000;Despesas Empenhadas;01 - Legislativa;id_teste;1500,50\n"
        )
        _cria_zip_com_csv(compactos / "dados.zip", conteudo_invalido)

        with pytest.raises(pandera.errors.SchemaErrors) as exc_info:
            pipeline_principal(compactos, extraidos, processados)

        assert "uf" in str(exc_info.value)
        assert not processados.exists()
