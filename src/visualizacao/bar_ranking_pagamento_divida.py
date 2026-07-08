import math  # <--- IMPORTAÇÃO NECESSÁRIA PARA O isnan
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import seaborn as sns


def plotar_ranking_pagamento_vs_divida(df, funcao_selecionada):

    # Filtra e ordena os dados para a função escolhida (Maior Índice para o Menor)
    df_filtrado = df[df["nome_funcao"] == funcao_selecionada].sort_values(by="indice_pagamento", ascending=False)

    # Criando uma paleta condicional baseada na regra de negócio (Verde >= 100%, Cinza < 100%)
    cores = ["#2ca02c" if x >= 1.0 else "#7f7f7f" for x in df_filtrado["indice_pagamento"]]

    ax = sns.barplot(
        data=df_filtrado,
        x="indice_pagamento",
        y="municipio",
        palette=cores,
        hue="municipio",
        legend=False,
    )

    # Linha vertical de corte em 100% (Índice = 1.0)
    plt.axvline(
        x=1.0,
        color="red",
        linestyle="--",
        linewidth=1.5,
        label="Ponto de Equilíbrio (100%)",
    )

    # Adicionando os rótulos de dados textuais nas pontas de cada barra (Indicador A e B)
    for i, linha in enumerate(df_filtrado.itertuples()):
        taxa_texto = f"{linha.taxa_residual * 100:.1f}%" if not math.isnan(linha.taxa_residual) else "0.0%"

        texto_label = f" {linha.indice_pagamento * 100:.1f}% (Restos: {taxa_texto})"

        ax.text(
            x=linha.indice_pagamento,
            y=i,
            s=texto_label,
            color="black",
            va="center",
            fontsize=10,
            weight="bold" if linha.indice_pagamento >= 1.0 else "normal",
        )

    # Títulos e rótulos de eixos
    plt.title(
        f"Ranking de Capitais: Índice de Pagamento vs Estoque de Restos — Função: {funcao_selecionada}\n(Valores > 100% indicam quitação de dívidas de anos anteriores)",
        pad=15,
    )
    plt.xlabel("Índice de Pagamento (Valor Pago / Valor Empenhado)")
    plt.ylabel("Capitais")

    # Formata o eixo X dinamicamente para exibir porcentagem baseada no valor decimal (1.0 = 100%)
    ax.xaxis.set_major_formatter(mtick.PercentFormatter(1.0))

    plt.tight_layout()
    plt.show()
