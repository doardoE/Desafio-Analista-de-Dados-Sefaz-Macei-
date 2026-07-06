import sidrapy
import pandas as pd
import logging


logger = logging.getLogger("ipca")


def busca_numero_indice(ano_inicio: int, ano_fim: int) -> pd.DataFrame:
    """Função que retorna o número índice do período em parâmetro.
    Foi utilizado a biblioteca sidrapy  (https://sidrapy.readthedocs.io/pt-br/latest/)"""

    try:
        df_ipca_bruto = sidrapy.get_table(
            table_code="1737",  # tabela do IPCA
            territorial_level="1",
            ibge_territorial_code="all",
            variable="2266",  # Número-índice (base: dezembro de 1993 = 100)
            period="all",
        )

        df_ipca = df_ipca_bruto[["D2N", "V"]]

        # filtra só os de dezembro
        filtro = df_ipca["D2N"].str.contains("dezembro", na=False, case=False)
        df = df_ipca.loc[filtro, ["D2N", "V"]]

        # formata a tabela
        df["ano"] = df["D2N"].str[-4:].astype(int)
        df["numero_indice"] = pd.to_numeric(df["V"], errors="coerce")
        df = df.drop(columns=["D2N", "V"])

        # aplica filtro por ano por parâmetro
        df = df[df["ano"].between(ano_inicio, ano_fim)]

        return df
    except Exception:
        logger.error("Ocorreu um erro ao buscar índices IPCA")
        raise RuntimeError("Ocorreu um erro ao buscar índices IPCA")


def deflacionar(df_ipca: pd.DataFrame, ano_base: int) -> pd.DataFrame:
    """Essa função calcula o deflator de acordo com o ano base"""

    df = df_ipca.copy()

    indice_base = df.loc[df_ipca["ano"] == ano_base, "numero_indice"].values[0]
    df["deflacao"] = indice_base / df_ipca["numero_indice"]

    return df
