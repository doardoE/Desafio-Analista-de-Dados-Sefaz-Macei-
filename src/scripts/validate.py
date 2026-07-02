import pandas as pd
import pandera.pandas as pa


# Schema do Pandera para validação do DataFrame
def schema():
    return pa.DataFrameSchema(
        columns={
            "ano_exercicio": pa.Column(pa.Int, nullable=False, checks=pa.Check.in_range(1990, 2080)),
            "instituicao": pa.Column(pa.String, nullable=False),
            "cod_ibge": pa.Column(pa.Int, nullable=False),
            "uf": pa.Column(pa.String, nullable=False, checks=pa.Check.str_length(2, 2)),
            "populacao": pa.Column(pa.Int, nullable=False, checks=pa.Check.greater_than(0)),
            "etapa_despesa": pa.Column(
                pa.String,
                nullable=False,
                # Valida se veio apenas os estágios oficiais da despesa pública
                checks=pa.Check.isin(
                    [
                        "Despesas Empenhadas",
                        "Despesas Liquidadas",
                        "Despesas Pagas",
                        "Inscrição de Restos a Pagar Não Processados",
                        "Inscrição de Restos a Pagar Processados",
                    ]
                ),
            ),
            "conta": pa.Column(pa.String, nullable=False),
            "cod_funcao": pa.Column(
                pa.String,
                nullable=True,
                checks=pa.Check.str_matches(r"^\d{2}$"),
                coerce=True,  # Converte automaticamente para string se o pandas ler como número
            ),
            "nome_funcao": pa.Column(pa.String, nullable=True),
            "cod_subfuncao": pa.Column(
                pa.String,
                nullable=True,
                # Se houver subfunção, precisa seguir o padrão "XX.XXX"
                checks=pa.Check.str_matches(r"^\d{2}\.\d{3}$"),
                coerce=True,
            ),
            "nome_subfuncao": pa.Column(pa.String, nullable=True),
            "identificador_conta": pa.Column(pa.String, nullable=False),
            "valor": pa.Column(
                pa.Float,
                nullable=False,
            ),
        },
        unique=["ano_exercicio", "cod_ibge", "conta", "etapa_despesa"],
        strict=True,
    )


def validar_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    df_validado = schema().validate(df, lazy=True)
    return df_validado
