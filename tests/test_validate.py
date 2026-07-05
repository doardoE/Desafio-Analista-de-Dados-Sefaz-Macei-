import pandas as pd
import pandera.errors
import pytest
from src.scripts.validate import validar_dataframe


@pytest.fixture
def df_valido() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "ano_exercicio": [2020, 2020, 2020],
            "instituicao": [
                "Prefeitura Municipal de Maceió - AL",
                "Prefeitura Municipal de Maceió - AL",
                "Prefeitura Municipal de Maceió - AL",
            ],
            "cod_ibge": [2704302, 2704302, 2704302],
            "uf": ["AL", "AL", "AL"],
            "populacao": [1018948, 1018948, 1018948],
            "etapa_despesa": ["Despesas Empenhadas", "Despesas Empenhadas", "Despesas Empenhadas"],
            "conta": [
                "Despesas Exceto Intraorçamentárias",
                "01 - Legislativa",
                "01.031 - Ação Legislativa",
            ],
            "cod_funcao": [None, "01", "01"],
            "nome_funcao": [None, "Legislativa", "Legislativa"],
            "cod_subfuncao": [None, None, "01.031"],
            "nome_subfuncao": [None, None, "Ação Legislativa"],
            "identificador_conta": [
                "siconfi-cor_TotalDespesas",
                "siconfi-cor_TotalDespesas",
                "siconfi-cor_TotalDespesas",
            ],
            "valor": [2469568678.67, 63453817.04, 12345678.90],
        }
    )


class TestValidarDataframeCaminhoFeliz:
    def test_valida_dataframe_correto_com_sucesso(self, df_valido):
        """Um DataFrame que respeita todas as regras deve passar sem lançar exceção
        e ser retornado intacto (mesmo número de linhas e colunas).
        """
        resultado_df = validar_dataframe(df_valido)

        assert isinstance(resultado_df, pd.DataFrame)
        assert len(resultado_df) == len(df_valido)
        assert set(resultado_df.columns) == set(df_valido.columns)

    def test_aceita_funcao_e_subfuncao_nulas(self, df_valido):
        """cod_funcao, nome_funcao, cod_subfuncao e nome_subfuncao são nullable,
        então uma linha totalmente sem função/subfunção (ex: linha de totalização)
        deve ser aceita.
        """
        resultado_df = validar_dataframe(df_valido)

        assert resultado_df.loc[0, "cod_funcao"] is None or pd.isna(resultado_df.loc[0, "cod_funcao"])
        assert resultado_df.loc[0, "cod_subfuncao"] is None or pd.isna(resultado_df.loc[0, "cod_subfuncao"])

    def test_coage_cod_funcao_numerico_para_string(self, df_valido):
        """cod_funcao/cod_subfuncao têm coerce=True: se vierem como número
        (ex: pandas leu '01' como int 1), o schema deve tentar coagir para string.
        """
        df_valido.loc[1, "cod_funcao"] = "02"
        df_valido.loc[1, "conta"] = "02 - Judiciária"

        resultado_df = validar_dataframe(df_valido)

        assert resultado_df.loc[1, "cod_funcao"] == "02"


class TestValidarDataframeCaminhoTriste:
    def test_falha_se_ano_exercicio_fora_do_intervalo(self, df_valido):
        df_valido.loc[0, "ano_exercicio"] = 1899  # fora do range 1990-2080

        with pytest.raises(pandera.errors.SchemaErrors) as exc_info:
            validar_dataframe(df_valido)

        assert "ano_exercicio" in str(exc_info.value)

    def test_falha_se_uf_nao_tiver_duas_letras(self, df_valido):
        df_valido.loc[0, "uf"] = "ALA"  # 3 caracteres, deveria ser exatamente 2

        with pytest.raises(pandera.errors.SchemaErrors) as exc_info:
            validar_dataframe(df_valido)

        assert "uf" in str(exc_info.value)

    def test_falha_se_populacao_nao_for_maior_que_zero(self, df_valido):
        df_valido.loc[0, "populacao"] = 0

        with pytest.raises(pandera.errors.SchemaErrors) as exc_info:
            validar_dataframe(df_valido)

        assert "populacao" in str(exc_info.value)

    def test_falha_se_etapa_despesa_nao_estiver_na_lista_permitida(self, df_valido):
        df_valido.loc[0, "etapa_despesa"] = "Despesa Inválida"

        with pytest.raises(pandera.errors.SchemaErrors) as exc_info:
            validar_dataframe(df_valido)

        assert "etapa_despesa" in str(exc_info.value)

    def test_falha_se_cod_funcao_nao_seguir_padrao_dois_digitos(self, df_valido):
        df_valido.loc[1, "cod_funcao"] = "1"  # deveria ser "01", com 2 dígitos

        with pytest.raises(pandera.errors.SchemaErrors) as exc_info:
            validar_dataframe(df_valido)

        assert "cod_funcao" in str(exc_info.value)

    def test_falha_se_cod_subfuncao_nao_seguir_padrao_xx_xxx(self, df_valido):
        df_valido.loc[2, "cod_subfuncao"] = "01031"  # faltando o ponto separador

        with pytest.raises(pandera.errors.SchemaErrors) as exc_info:
            validar_dataframe(df_valido)

        assert "cod_subfuncao" in str(exc_info.value)

    def test_falha_se_coluna_nao_nullable_tiver_valor_nulo(self, df_valido):
        """instituicao é nullable=False, então um valor ausente deve derrubar a validação."""
        df_valido.loc[0, "instituicao"] = None

        with pytest.raises(pandera.errors.SchemaErrors) as exc_info:
            validar_dataframe(df_valido)

        assert "instituicao" in str(exc_info.value)

    def test_falha_se_linhas_duplicadas_na_chave_unica(self, df_valido):
        """A combinação (ano_exercicio, cod_ibge, conta, etapa_despesa) deve ser única."""
        df_duplicado = pd.concat([df_valido, df_valido.iloc[[0]]], ignore_index=True)

        with pytest.raises(pandera.errors.SchemaErrors) as exc_info:
            validar_dataframe(df_duplicado)

        assert "duplicate" in str(exc_info.value).lower()

    def test_falha_se_dataframe_tiver_coluna_extra_nao_esperada(self, df_valido):
        """strict=True: qualquer coluna fora do schema deve derrubar a validação."""
        df_valido["coluna_inesperada"] = "qualquer_valor"

        with pytest.raises(pandera.errors.SchemaErrors) as exc_info:
            validar_dataframe(df_valido)

        assert "coluna_inesperada" in str(exc_info.value)

    def test_falha_se_dataframe_estiver_faltando_coluna_obrigatoria(self, df_valido):
        """Remover uma coluna exigida pelo schema deve derrubar a validação."""
        df_sem_coluna = df_valido.drop(columns=["valor"])

        with pytest.raises(pandera.errors.SchemaErrors) as exc_info:
            validar_dataframe(df_sem_coluna)

        assert "valor" in str(exc_info.value)

    def test_falha_se_valor_nao_for_numerico(self, df_valido):
        df_valido["valor"] = df_valido["valor"].astype(object)
        df_valido.loc[0, "valor"] = "não é número"

        with pytest.raises((pandera.errors.SchemaErrors, TypeError, ValueError)):
            validar_dataframe(df_valido)

    def test_erro_agrega_multiplas_falhas_por_ser_lazy(self, df_valido):
        """validate(..., lazy=True) deve acumular TODAS as falhas encontradas
        (não parar na primeira), permitindo corrigir tudo de uma vez.
        """
        df_valido.loc[0, "uf"] = "ALA"
        df_valido.loc[0, "populacao"] = -5

        with pytest.raises(pandera.errors.SchemaErrors) as exc_info:
            validar_dataframe(df_valido)

        falhas = exc_info.value.failure_cases
        colunas_com_falha = set(falhas["column"])
        assert "uf" in colunas_com_falha
        assert "populacao" in colunas_com_falha
