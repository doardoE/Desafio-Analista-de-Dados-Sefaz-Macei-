import pandas as pd
import pytest
from pathlib import Path
from src.scripts.transform import transformar_dados_finbra


def _criar_csv_finbra(caminho_csv: Path, conteudo: str) -> None:
    caminho_csv.parent.mkdir(parents=True, exist_ok=True)
    caminho_csv.write_text(conteudo, encoding="latin-1")


class TestTransformarDadosFinbraCaminhoFeliz:
    def test_transforma_dados_com_sucesso(self, tmp_path):
        arquivo_csv = tmp_path / "finbra_test.csv"
        conteudo = (
            "Exercício: 2020\n"
            "Escopo: Capitais\n"
            "Tabela: Despesas por Função (Anexo I-E)\n"
            "Instituição;Cod.IBGE;UF;População;Coluna;Conta;Identificador da Conta;Valor\n"
            'Prefeitura Municipal de Maceió - AL;2704302;AL;1018948;"Despesas Empenhadas";'
            '"Despesas Exceto Intraorçamentárias";"siconfi-cor_TotalDespesas";2469568678,67\n'
            'Prefeitura Municipal de Maceió - AL;2704302;AL;1018948;"Despesas Empenhadas";'
            '"01 - Legislativa";"siconfi-cor_TotalDespesas";63453817,04\n'
            'Prefeitura Municipal de Maceió - AL;2704302;AL;1018948;"Despesas Empenhadas";'
            '"01.031 - Ação Legislativa";"siconfi-cor_TotalDespesas";12345678,90\n'
        )
        _criar_csv_finbra(arquivo_csv, conteudo)

        resultado_df = transformar_dados_finbra([arquivo_csv], path_extraidos=tmp_path)

        assert isinstance(resultado_df, pd.DataFrame)
        assert len(resultado_df) == 3
        assert (resultado_df["ano_exercicio"] == 2020).all()
        assert "conta" in resultado_df.columns
        assert "Conta" not in resultado_df.columns

    def test_extrai_funcao_via_regex(self, tmp_path):
        arquivo_csv = tmp_path / "finbra_test.csv"
        conteudo = (
            "Exercício: 2020\n"
            "Escopo: Capitais\n"
            "Tabela: Despesas de Teste\n"
            "Instituição;Cod.IBGE;UF;População;Coluna;Conta;Identificador da Conta;Valor\n"
            "Prefeitura;2704302;AL;100000;Despesas Empenhadas;01 - Legislativa;id_teste;1500,50\n"
        )
        _criar_csv_finbra(arquivo_csv, conteudo)

        resultado_df = transformar_dados_finbra([arquivo_csv], path_extraidos=tmp_path)

        assert resultado_df.loc[0, "cod_funcao"] == "01"
        assert resultado_df.loc[0, "nome_funcao"] == "Legislativa"

    def test_extrai_subfuncao_e_preenche_funcao_pai(self, tmp_path):
        arquivo_csv = tmp_path / "finbra_test.csv"
        conteudo = (
            "Exercício: 2020\n"
            "Escopo: Capitais\n"
            "Tabela: Despesas de Teste\n"
            "Instituição;Cod.IBGE;UF;População;Coluna;Conta;Identificador da Conta;Valor\n"
            "Prefeitura;2704302;AL;100000;Despesas Empenhadas;01.031 - Ação Legislativa;id_teste;500,00\n"
        )
        _criar_csv_finbra(arquivo_csv, conteudo)

        resultado_df = transformar_dados_finbra([arquivo_csv], path_extraidos=tmp_path)

        assert resultado_df.loc[0, "cod_subfuncao"] == "01.031"
        assert resultado_df.loc[0, "nome_subfuncao"] == "Ação Legislativa"
        assert resultado_df.loc[0, "cod_funcao"] == "01"
        assert resultado_df.loc[0, "nome_funcao"] == "Legislativa"

    def test_linha_sem_funcao_ou_subfuncao_fica_nula(self, tmp_path):
        arquivo_csv = tmp_path / "finbra_test.csv"
        conteudo = (
            "Exercício: 2020\n"
            "Escopo: Capitais\n"
            "Tabela: Despesas de Teste\n"
            "Instituição;Cod.IBGE;UF;População;Coluna;Conta;Identificador da Conta;Valor\n"
            'Prefeitura;2704302;AL;100000;Despesas Empenhadas;"Despesas Exceto Intraorçamentárias";'
            "id_teste;2469568678,67\n"
        )
        _criar_csv_finbra(arquivo_csv, conteudo)

        resultado_df = transformar_dados_finbra([arquivo_csv], path_extraidos=tmp_path)

        assert pd.isna(resultado_df.loc[0, "cod_funcao"]) or resultado_df.loc[0, "cod_funcao"] is None
        assert pd.isna(resultado_df.loc[0, "cod_subfuncao"]) or resultado_df.loc[0, "cod_subfuncao"] is None


class TestTransformarDadosFinbraCaminhoAlternativo:
    def test_lanca_erro_se_path_dados_extraidos_nao_existir(self, tmp_path):
        path_inexistente = tmp_path / "pasta_que_nao_existe"

        with pytest.raises(ValueError) as exc_info:
            transformar_dados_finbra([], path_extraidos=path_inexistente)

        assert "O caminho para os dados extraídos não existe." in str(exc_info.value)

    def test_retorna_df_vazio_se_nao_tiver_arquivos_csv(self, tmp_path):
        resultado_df = transformar_dados_finbra([], path_extraidos=tmp_path)

        assert isinstance(resultado_df, pd.DataFrame)
        assert resultado_df.empty


class TestTransformarDadosFinbraCaminhoTriste:
    def test_lanca_runtime_error_se_arquivo_estiver_corrompido(self, tmp_path):
        arquivo_corrompido = tmp_path / "finbra_test.csv"
        _criar_csv_finbra(arquivo_corrompido, "Texto corrompido sem separador de ano")

        with pytest.raises(RuntimeError) as exc_info:
            transformar_dados_finbra([arquivo_corrompido], path_extraidos=tmp_path)

        assert "Erro Inesperado ao processar o arquivo" in str(exc_info.value)
