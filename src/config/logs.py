from src.config.Paths import paths
import logging
import sys


def configura_log():
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        force=True,
        handlers=[
            logging.FileHandler(f"{paths._root}/execucao_projeto.log", mode="a", encoding="utf-8"),
            logging.StreamHandler(sys.stdout),
        ],
    )

    # Silencia logs de depuração visuais que poluem o Jupyter e o terminal
    logging.getLogger("matplotlib").setLevel(logging.WARNING)
    logging.getLogger("PIL").setLevel(logging.WARNING)
