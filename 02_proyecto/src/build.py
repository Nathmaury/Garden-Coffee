import time
import duckdb
import pandas as pd
from src import config, etl, models


def guardar_tablas(tablas):
    with duckdb.connect(str(config.DB_PATH)) as con:
        for nombre, df in tablas.items():
            con.register("tmp_view", df)
            con.execute(f"CREATE OR REPLACE TABLE {nombre} AS SELECT * FROM tmp_view")
            con.unregister("tmp_view")


def resumen_tablas():
    with duckdb.connect(str(config.DB_PATH), read_only=True) as con:
        tablas = [t[0] for t in con.execute("SHOW TABLES").fetchall()]
        return {t: con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0] for t in tablas}


def main():
    inicio = time.time()
    print("1/3 ETL y calidad de datos")
    df_long, reporte = etl.run()
    print(reporte)
    print("2/3 Backtest, pronóstico y segmentación (puede tardar 1-2 minutos)")
    tablas, silhouette = models.run(df_long)
    if config.PRECIOS_FILE.exists():
        reales = pd.read_csv(config.PRECIOS_REALES_FILE) if config.PRECIOS_REALES_FILE.exists() else None
        tablas["pronostico_precios"] = models.pronosticar_precios(etl.load_precios(), reales)
    print("3/3 Guardando tablas en DuckDB")
    guardar_tablas(tablas)
    for tabla, filas in resumen_tablas().items():
        print(f"  {tabla}: {filas} filas")
    print(f"Silhouette de la segmentación: {silhouette:.3f}")
    print(f"Base lista en {config.DB_PATH} ({time.time() - inicio:.0f} s)")


if __name__ == "__main__":
    main()