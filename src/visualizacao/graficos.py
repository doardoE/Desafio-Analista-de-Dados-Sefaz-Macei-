import matplotlib.pyplot as plt
import seaborn as sns


def plotar_soma_valores_deflacionados_por_ano(df):
    # Convertendo para bilhões
    df["valor_nominal_bi"] = df["sum(valor_nominal)"] / 1e9
    df["valor_real_bi"] = df["sum(valor_real)"] / 1e9

    sns.lineplot(data=df, x=df["ano_exercicio"], y=df["valor_nominal_bi"], marker="o", label="Valor Nominal")
    sns.lineplot(data=df, x=df["ano_exercicio"], y=df["valor_real_bi"], marker="o", label="Valor Real (deflacionado)")

    # adiciona os valores as bolinhas
    for x, y in zip(df["ano_exercicio"], df["valor_nominal_bi"]):
        plt.annotate(f"{y:,.0f}", (x, y), textcoords="offset points", xytext=(0, 8), ha="center", fontsize=12)

    for x, y in zip(df["ano_exercicio"], df["valor_real_bi"]):
        plt.annotate(f"{y:,.0f}", (x, y), textcoords="offset points", xytext=(0, -14), ha="center", fontsize=12)

    plt.title("Soma dos Valores Nominais x Reais por Ano em Bilhões")
    plt.xlabel("Ano de Exercício")
    plt.ylabel("Valor (R$ bilhões)")
    plt.xticks(df["ano_exercicio"])
    plt.legend()
    plt.show()
