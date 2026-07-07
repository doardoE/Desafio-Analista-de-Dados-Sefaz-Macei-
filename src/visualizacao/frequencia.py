import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


def plotar_frequencia_categoria(df: pd.DataFrame, nome_coluna_original: str):
    """
    Gera um gráfico de barras horizontais mostrando as categorias mais frequentes.
    """
    if df.empty:
        return

    # Criando o gráfico de barras horizontais
    ax = sns.barplot(
        data=df,
        x="contagem",
        y="categoria",
        hue="categoria",
    )

    # Adiciona os rótulos de percentual ao final de cada barra
    for i, row in df.iterrows():
        ax.text(
            row["contagem"] + (df["contagem"].max() * 0.01),  # Pequeno espaçamento após a barra
            i,
            f"{row['percentual']}%",
            va="center",
            fontsize=10,
            fontweight="bold",
        )

    plt.title(f"Frequência de Registros por {nome_coluna_original.replace('_', ' ').title()}")
    plt.xlabel("Quantidade de Registros na Base", fontsize=11)
    plt.ylabel("")  # Remove o nome do eixo Y pois as categorias já são autoexplicativas
    plt.grid(axis="x", linestyle="--", alpha=0.5)

    plt.tight_layout()
    plt.show()
