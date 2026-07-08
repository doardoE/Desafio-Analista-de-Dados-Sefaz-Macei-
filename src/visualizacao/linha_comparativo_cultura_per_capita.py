import matplotlib.pyplot as plt
import seaborn as sns


def plotar_comparativo_cultura_per_capita(df):
    # Força a correção do nome caso ele venha sem acento da query
    df["grupo"] = df["grupo"].replace({"Maceio": "Maceió"})

    # Dicionário explícito para garantir as cores corretas por grupo
    paleta_cores = {"Maceió": "#1f77b4", "Média das Demais Capitais": "#7f7f7f"}

    ax = sns.lineplot(
        data=df,
        x="ano_exercicio",
        y="cultura_per_capita",
        hue="grupo",
        marker="o",
        markersize=8,
        linewidth=2.5,
        palette=paleta_cores,  # <--- Usando o mapeamento seguro aqui
    )

    # Adiciona os valores monetários logo acima/abaixo dos pontos
    for _, linha in df.iterrows():
        # Ajusta o offset dependendo do grupo para evitar colisões visuais
        offset = 1.5 if linha["grupo"] == "Maceió" else -2.5

        ax.text(
            x=linha["ano_exercicio"],
            y=linha["cultura_per_capita"] + offset,
            s=f"R$ {linha['cultura_per_capita']:.2f}",
            horizontalalignment="center",
            fontsize=10,
            weight="bold" if linha["grupo"] == "Maceió" else "normal",
        )

    # Customização de títulos e eixos
    plt.title(
        "Investimento em Cultura per Capita: Maceió vs. Média das Demais Capitais\n(Valor Pago dividido pela População)",
        pad=15,
    )
    plt.xlabel("Ano de Exercício")
    plt.ylabel("Valor por Habitante (R$)")

    # Ajuste dos anos no eixo X
    plt.xticks(df["ano_exercicio"].unique())

    plt.tight_layout()
    plt.show()
