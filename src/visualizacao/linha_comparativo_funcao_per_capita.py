import matplotlib.pyplot as plt
import seaborn as sns


def plotar_comparativo_funcao_per_capita(df, funcao: str):
    df = df.copy()
    df["grupo"] = df["grupo"].replace({"Maceio": "Maceió"})

    paleta_cores = {"Maceió": "#1f77b4", "Média das Demais Capitais": "#7f7f7f"}

    ax = sns.lineplot(
        data=df,
        x="ano_exercicio",
        y="valor_per_capita",
        hue="grupo",
        marker="o",
        markersize=8,
        linewidth=2.5,
        palette=paleta_cores,
    )

    # offset proporcional à escala dos dados, em vez de um valor fixo calibrado para Cultura
    amplitude = df["valor_per_capita"].max() - df["valor_per_capita"].min()
    offset_base = max(amplitude * 0.06, 0.5)

    for _, linha in df.iterrows():
        offset = offset_base if linha["grupo"] == "Maceió" else -offset_base
        ax.text(
            x=linha["ano_exercicio"],
            y=linha["valor_per_capita"] + offset,
            s=f"R$ {linha['valor_per_capita']:.2f}",
            horizontalalignment="center",
            fontsize=10,
            weight="bold" if linha["grupo"] == "Maceió" else "normal",
        )

    plt.title(
        f"Investimento em {funcao} per Capita: Maceió vs. Média das Demais Capitais\n(Valor Pago dividido pela População)",
        pad=15,
    )
    plt.xlabel("Ano de Exercício")
    plt.ylabel("Valor por Habitante (R$)")
    plt.xticks(df["ano_exercicio"].unique())
    plt.tight_layout()
    plt.show()
