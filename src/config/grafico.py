import matplotlib.pyplot as plt
import seaborn as sns


def configurar_graficos() -> None:
    sns.set_theme(
        style="whitegrid",  # estilo de fundo: "whitegrid", "darkgrid", "white", "dark", "ticks"
        palette="mako",  # paleta de cores padrão para todos os gráficos
        context="notebook",  # escala de fontes/linhas: "paper", "notebook", "talk", "poster"
        font_scale=1.1,  # ajuste fino no tamanho das fontes
    )

    plt.rcParams.update(
        {
            "figure.figsize": (16, 8),  # tamanho padrão de todas as figuras
            "figure.dpi": 100,
            "axes.titlesize": 16,
            "axes.titleweight": "bold",
            "axes.labelsize": 14,
            "legend.frameon": False,  # legenda sem moldura
        }
    )
