import matplotlib.pyplot as plt
import seaborn as sns


def plotar_linha_taxa_execucao(df):
    ax = sns.lineplot(
        data=df,
        x="ano_exercicio",
        y="taxa_execucao",
        hue="nome_funcao",
        marker="o",
        linewidth=2.5,
        palette=["#1f77b4", "#ff7f0e", "#2ca02c"],  # Cores distintas para as 3 áreas
    )

    for _, linha in df.iterrows():
        ax.text(
            x=linha["ano_exercicio"],
            y=linha["taxa_execucao"] + 0.5,  # O "+ 1.5" serve para deslocar o texto um pouco acima da bolinha
            s=f"{linha['taxa_execucao']:.1f}%",  # Formata o valor com 1 casa decimal e símbolo de %
            horizontalalignment="center",
            verticalalignment="bottom",
            fontsize=9,
            weight="bold",
        )

    # Customização de títulos e eixos
    plt.title(
        "Taxa de Execução Orçamentária Nacional (Capitais)\nProporção do Valor Pago em relação ao Empenhado",
        fontsize=14,
        pad=15,
    )
    plt.xlabel("Ano de Exercício", fontsize=12)
    plt.ylabel("Taxa de Execução (%)", fontsize=12)

    # Ajuste do eixo X para exibir apenas anos inteiros
    plt.xticks(df["ano_exercicio"].unique())

    # Adiciona o símbolo de porcentagem no eixo Y para clareza
    import matplotlib.ticker as mtick

    plt.gca().yaxis.set_major_formatter(mtick.PercentFormatter())

    # Posicionamento da legenda
    plt.legend(title="Função Orçamentária", bbox_to_anchor=(1.05, 1), loc="upper left")

    plt.tight_layout()
    plt.show()
