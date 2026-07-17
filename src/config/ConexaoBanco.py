from src.config.Paths import paths
import duckdb


class ConexaoBanco:
    def __init__(self):
        self.con: duckdb.DuckDBPyConnection = duckdb.connect(
            database=paths.banco_dados,
        )

    def close(self) -> None:
        if self.con is not None:
            self.con.close()
            self.con = None


db = ConexaoBanco()
