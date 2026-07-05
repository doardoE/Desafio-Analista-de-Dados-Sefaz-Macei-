import shutil
import zipfile
import pandas as pd
import pandera.errors
import pytest
from contextlib import contextmanager, ExitStack
from pathlib import Path
from src.pipeline import pipeline_principal
from src.config import paths


@contextmanager
def _pasta_real_isolada(pasta: Path):
    """Isola uma pasta REAL do projeto para o teste, sem monkeypatch.

    Se a pasta já existir (dados de um ambiente real), faz backup e restaura
    ao final. A pasta fica ausente durante o teste até que o próprio código
    testado (ou o teste) a crie — o que é exatamente o que o pipeline espera
    encontrar em cada cenário (compactos/extraidos precisam existir com
    conteúdo; processados só é criada pelo próprio pipeline).
    """
    backup = pasta.parent / f"{pasta.name}_backup_teste"
    existia = pasta.exists()
    if existia:
        pasta.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(pasta), str(backup))
    try:
        yield pasta
    finally:
        if pasta.exists():
            shutil.rmtree(pasta)
        if existia:
            shutil.move(str(backup), str(pasta))


@pytest.fixture
def ambiente_pipeline():
    """Isola as 3 pastas reais usadas pelo pipeline (compactos, extraidos,
    processados) durante o teste. Nenhuma delas é pré-criada aqui: cada
    teste decide o que precisa existir para o cenário que está exercitando.
    """
    with ExitStack() as stack:
        compactos = stack.enter_context(_pasta_real_isolada(paths.path_dados_compactos))
        extraidos = stack.enter_context(_pasta_real_isolada(paths.path_dados_extraidos))
        processados = stack.enter_context(_pasta_real_isolada(paths.path_dados_processados))
        yield compactos, extraidos, processados


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


def _criar_zip_com_csv(caminho_zip: Path, conteudo_csv: str, nome_csv: str = "finbra_test.csv") -> None:
    """Cria um .csv temporário e o compacta em `caminho_zip`."""
    caminho_zip.parent.mkdir(parents=True, exist_ok=True)
    csv_temporario = caminho_zip.parent / nome_csv
    csv_temporario.write_text(conteudo_csv, encoding="latin-1")
    with zipfile.ZipFile(caminho_zip, "w") as z:
        z.write(csv_temporario, arcname=nome_csv)
    csv_temporario.unlink()


# ==============================================================================
# CAMINHO FELIZ (Happy Path)
# ==============================================================================
class TestPipelineCaminhoFeliz:
    def test_pipeline_completo_gera_parquet_valido(self, ambiente_pipeline):
        """Fluxo ponta a ponta 100% real: zip -> extração -> transformação
        -> validação -> parquet salvo em disco, com o conteúdo conferido.
        """
        compactos, extraidos, processados = ambiente_pipeline
        _criar_zip_com_csv(compactos / "dados.zip", _conteudo_csv_valido(ano=2026))

        pipeline_principal()

        arquivos_extraidos = list(extraidos.rglob("*.csv"))
        assert len(arquivos_extraidos) == 1

        caminho_parquet = processados / "finbra.parquet"
        assert caminho_parquet.exists()

        df_final = pd.read_parquet(caminho_parquet)
        assert len(df_final) == 2
        assert (df_final["ano_exercicio"] == 2026).all()
        assert df_final.loc[0, "cod_funcao"] == "01"
        assert df_final.loc[0, "nome_funcao"] == "Legislativa"
        assert df_final.loc[1, "cod_subfuncao"] == "01.031"
        assert df_final.loc[1, "nome_subfuncao"] == "Ação Legislativa"

    def test_pipeline_preserva_estrutura_de_subpastas_na_extracao(self, ambiente_pipeline):
        """A extração deve refletir a árvore de subpastas de
        path_dados_compactos dentro de path_dados_extraidos.
        Como `extrair_dados` extrai para a pasta-mãe do destino calculado
        (extraidos/subpasta/<stem_do_zip>), o CSV acaba em extraidos/subpasta/.
        """
        compactos, extraidos, processados = ambiente_pipeline
        _criar_zip_com_csv(compactos / "uf" / "al" / "capitais.zip", _conteudo_csv_valido())

        pipeline_principal()

        arquivo_esperado = extraidos / "uf" / "al" / "finbra_test.csv"
        assert arquivo_esperado.exists()

    def test_pipeline_processa_e_concatena_multiplos_arquivos_zip(self, ambiente_pipeline):
        """Vários zips devem virar um único DataFrame concatenado no parquet final."""
        compactos, extraidos, processados = ambiente_pipeline
        _criar_zip_com_csv(compactos / "dados_2025.zip", _conteudo_csv_valido(ano=2025), nome_csv="a.csv")
        _criar_zip_com_csv(compactos / "dados_2026.zip", _conteudo_csv_valido(ano=2026), nome_csv="b.csv")

        pipeline_principal()

        df_final = pd.read_parquet(processados / "finbra.parquet")
        assert len(df_final) == 4
        assert set(df_final["ano_exercicio"].unique()) == {2025, 2026}


# ==============================================================================
# CAMINHOS ALTERNATIVOS (Alternative Paths)
# ==============================================================================
class TestPipelineCaminhoAlternativo:
    def test_pipeline_nao_faz_nada_se_pasta_de_compactos_nao_existir(self, ambiente_pipeline):
        """Sem a pasta de compactados sequer existir, `rglob` retorna vazio e
        o pipeline deve retornar cedo, sem criar nada em processados.
        """
        compactos, extraidos, processados = ambiente_pipeline
        # propositalmente não criamos nem `compactos` nem nenhum zip

        pipeline_principal()

        assert not processados.exists()

    def test_pipeline_nao_faz_nada_se_nao_houver_zips(self, ambiente_pipeline):
        """Pasta de compactados existe, mas está vazia."""
        compactos, extraidos, processados = ambiente_pipeline
        compactos.mkdir(parents=True)

        pipeline_principal()

        assert not processados.exists()

    def test_pipeline_falha_na_validacao_se_zip_nao_tiver_nenhum_csv(self, ambiente_pipeline):
        """Um .zip sem nenhum .csv gera DataFrame vazio na transformação;
        como o schema é `strict=True` e exige colunas obrigatórias, a
        validação real deve rejeitar esse DataFrame vazio.
        """
        compactos, extraidos, processados = ambiente_pipeline
        compactos.mkdir(parents=True)
        arquivo_txt = compactos / "leiame.txt"
        arquivo_txt.write_text("nada de CSV aqui", encoding="utf-8")
        with zipfile.ZipFile(compactos / "dados.zip", "w") as z:
            z.write(arquivo_txt, arcname="leiame.txt")

        with pytest.raises(pandera.errors.SchemaErrors):
            pipeline_principal()

        assert not processados.exists()


# ==============================================================================
# CAMINHOS TRISTES (Sad Paths)
# ==============================================================================
class TestPipelineCaminhoTriste:
    def test_pipeline_propaga_erro_real_de_extracao_se_zip_estiver_corrompido(self, ambiente_pipeline):
        """Um .zip corrompido faz `extrair_dados` (função real) lançar
        RuntimeError; o pipeline não deve engolir esse erro."""
        compactos, extraidos, processados = ambiente_pipeline
        compactos.mkdir(parents=True)
        (compactos / "corrompido.zip").write_text("Não sou um zip de verdade", encoding="latin-1")

        with pytest.raises(RuntimeError, match="Erro ao extrair dados do arquivo"):
            pipeline_principal()

        assert not processados.exists()

    def test_pipeline_propaga_erro_real_de_transformacao_se_csv_estiver_corrompido(self, ambiente_pipeline):
        """Um CSV sem o cabeçalho de exercício esperado faz
        `transformar_dados_finbra` (função real) lançar RuntimeError."""
        compactos, extraidos, processados = ambiente_pipeline
        conteudo_corrompido = "Texto corrompido sem separador de ano\n"
        _criar_zip_com_csv(compactos / "dados.zip", conteudo_corrompido)

        with pytest.raises(RuntimeError, match="Erro Inesperado ao processar o arquivo"):
            pipeline_principal()

        assert not processados.exists()

    def test_pipeline_propaga_erro_real_de_validacao_se_dado_violar_schema(self, ambiente_pipeline):
        """Um CSV com UF inválida (3 letras) deve fazer o `validar_dataframe`
        real rejeitar o DataFrame."""
        compactos, extraidos, processados = ambiente_pipeline
        conteudo_invalido = (
            "Exercício: 2026\n"
            "Escopo: Municipios\n"
            "Tabela: Despesas de Teste\n"
            "Instituição;Cod.IBGE;UF;População;Coluna;Conta;Identificador da Conta;Valor\n"
            "Prefeitura;2704302;ALX;100000;Despesas Empenhadas;01 - Legislativa;id_teste;1500,50\n"
        )
        _criar_zip_com_csv(compactos / "dados.zip", conteudo_invalido)

        with pytest.raises(pandera.errors.SchemaErrors) as exc_info:
            pipeline_principal()

        assert "uf" in str(exc_info.value)
        assert not processados.exists()