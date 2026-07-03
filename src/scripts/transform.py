from src.config import paths, df_config
import pandas as pd
import logging

logger = logging.getLogger("transform")


# função para transformar os dados do dataframe de entrada
def transformar_dados_finbra(list_path_arquivos: list) -> pd.DataFrame:
    logger.info("Iniciando a transformação dos dados extraídos...")
    if not paths.path_dados_extraidos.exists():
        raise ValueError("O caminho para os dados extraídos não existe.")

    if not list_path_arquivos:
        logger.warning("Nenhum arquivo CSV encontrado..")
        return pd.DataFrame()

    dfs = []
    for path_arquivo_csv in list_path_arquivos:
        try:
            # pega o exercício do arquivo CSV, que está na primeira linha do arquivo
            with open(path_arquivo_csv, "r", encoding=df_config.encoding) as f:
                linha_exercicio = f.readline().strip().split(sep=":")
                ano = int(linha_exercicio[1].strip())

            df = pd.read_csv(
                path_arquivo_csv,
                sep=df_config.sep,
                skiprows=df_config.skiprows,
                encoding=df_config.encoding,
                decimal=df_config.decimal,
                thousands=df_config.thousands,
            )

            df["ano_exercicio"] = ano
            df["cod_funcao"] = None
            df["nome_funcao"] = None
            df["cod_subfuncao"] = None
            df["nome_subfuncao"] = None

            # ragex para extrair o código e o nome da função e subfunção da coluna "conta"
            padrao_subfuncao = r"^(\d{2}\.\d{3})\s*-\s*(.*)$"
            padrao_funcao = r"^(\d{2})\s*-\s*(.*)$"

            # mascaras para identificar quais linhas correspondem a função e subfunção
            mascara_fun = df["Conta"].str.match(padrao_funcao, na=False)
            mascara_sub = df["Conta"].str.match(padrao_subfuncao, na=False)

            # preenche as colunas de função e subfunção com os valores extraídos da coluna "conta"
            df.loc[mascara_sub, ["cod_subfuncao", "nome_subfuncao"]] = (
                df.loc[mascara_sub, "Conta"].str.extract(padrao_subfuncao).values
            )
            df.loc[mascara_fun, ["cod_funcao", "nome_funcao"]] = (
                df.loc[mascara_fun, "Conta"].str.extract(padrao_funcao).values
            )

            # preenche a coluna "cod_funcao" com o código da função correspondente à subfunção, caso exista
            df.loc[df["cod_subfuncao"].notna(), "cod_funcao"] = df["cod_subfuncao"].str.slice(0, 2)
            df["nome_funcao"] = df["cod_funcao"].map(df_config.dict_funcao)

            # renomeia as colunas do dataframe de acordo com o dicionário de colunas definido em df_config
            df = df.rename(columns=df_config.colunas)

            # altera o tipo das colunas de função e subfunção para string e substitui "None" por None
            df["cod_funcao"] = df["cod_funcao"].astype("str").replace("None", None)
            df["nome_funcao"] = df["nome_funcao"].astype("str").replace("None", None)
            df["cod_subfuncao"] = df["cod_subfuncao"].astype("str").replace("None", None)
            df["nome_subfuncao"] = df["nome_subfuncao"].astype("str").replace("None", None)

            dfs.append(df)
        except Exception as e:
            logger.error(f"Erro Inesperado ao processar o arquivo '{path_arquivo_csv}': {e}")
            raise RuntimeError(f"Erro Inesperado ao processar o arquivo '{path_arquivo_csv}': {e}")

    if not dfs:
        logger.warning("Nenhum DataFrame foi criado a partir dos arquivos CSV extraídos.")
        return pd.DataFrame()

    return pd.concat(dfs, ignore_index=True)
