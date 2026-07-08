import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.ticker as mtick


def plotar_evolucao_subfuncoes_cultura(df):
    """
    Plota a evolução temporal da participação percentual de cada subfunção
    dentro do orçamento total da Cultura.
    """
    # Garante a ordenação cronológica para o desenho correto das linhas
    df_ordenado = df.sort_values(by="ano_exercicio")

    ax = sns.lineplot(
        data=df_ordenado,
        x="ano_exercicio",
        y="participacao_percentual",
        hue="nome_subfuncao",
        marker="o",
        markersize=7,
        linewidth=2.5,
    )

    # Customização de títulos e eixos de acordo com o padrão do projeto
    plt.title("Evolução da Participação das Subfunções no Orçamento da Cultura", pad=15)
    plt.xlabel("Ano de Exercício")
    plt.ylabel("Participação no Total da Cultura (%)")

    # Ajuste dos anos no eixo X e formato de porcentagem no eixo Y
    plt.xticks(df_ordenado["ano_exercicio"].unique())
    ax.yaxis.set_major_formatter(mtick.PercentFormatter())

    # Posiciona a legenda do lado de fora para evitar poluição visual
    plt.legend(title="Subfunção", bbox_to_anchor=(1.05, 1), loc="upper left")

    plt.tight_layout()
    plt.show()
