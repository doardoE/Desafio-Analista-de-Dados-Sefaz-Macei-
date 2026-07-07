from src.config.Paths import paths
import duckdb


class ConexaoBanco:
    def __init__(self):
        self.con: duckdb.DuckDBPyConnection = duckdb.connect(
            database=paths.banco_dados,
        )


db = ConexaoBanco()
