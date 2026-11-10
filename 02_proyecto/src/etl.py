import re
import duckdb
import pandas as pd
from src import config
from src.regions import add_region

YEAR_PATTERN = r"\d{4}/\d{2}"
COLUMNS = ["country", "coffee_type", "year", "crop_year", "consumption_kg", "reported", "zero_flag", "flat_series"]


def load_raw(path=config.RAW_FILE):
    return pd.read_parquet(path)


def get_year_cols(df):
    cols = [c for c in df.columns if re.fullmatch(YEAR_PATTERN, str(c))]
    if not cols:
        raise ValueError("No se encontraron columnas de año con formato YYYY/YY")
    return cols


def quality_report(df):
    year_cols = get_year_cols(df)
    diff = (df[year_cols].sum(axis=1) - df["Total_domestic_consumption"]).abs()
    return {
        "filas": len(df),
        "paises_unicos": int(df["Country"].nunique()),
        "paises_duplicados": int(df["Country"].duplicated().sum()),
        "nulos": int(df.isna().sum().sum()),
        "negativos": int((df[year_cols] < 0).sum().sum()),
        "max_diff_total": float(diff.max()),
    }


def to_long(df, flat_threshold=3):
    year_cols = get_year_cols(df)
    zero_share = (df[year_cols] == 0).mean(axis=1) * 100
    distinct = df[year_cols].nunique(axis=1)
    no_report = df.loc[zero_share == 100, "Country"].tolist()
    flat = df.loc[distinct <= flat_threshold, "Country"].tolist()

    out = df.melt(
        id_vars=["Country", "Coffee type"],
        value_vars=year_cols,
        var_name="crop_year",
        value_name="consumption_kg",
    )
    out["year"] = out["crop_year"].str[:4].astype(int)
    out = out.rename(columns={"Country": "country", "Coffee type": "coffee_type"})
    out["reported"] = ~out["country"].isin(no_report)
    out["zero_flag"] = out["consumption_kg"].eq(0)
    out["flat_series"] = out["country"].isin(flat)
    return out[COLUMNS].sort_values(["country", "year"]).reset_index(drop=True)


def build_countries(df_long):
    return (
        df_long.groupby("country", as_index=False)
        .agg(
            coffee_type=("coffee_type", "first"),
            region=("region", "first"),
            reported=("reported", "first"),
            flat_series=("flat_series", "first"),
        )
    )


def save(df_long):
    config.DATA_PROCESSED.mkdir(parents=True, exist_ok=True)
    df_db = add_region(df_long)
    df_db.to_parquet(config.DATA_PROCESSED / "consumo_largo.parquet", index=False)
    countries = build_countries(df_db)
    with duckdb.connect(str(config.DB_PATH)) as con:
        con.register("consumo_view", df_db)
        con.register("paises_view", countries)
        con.execute("CREATE OR REPLACE TABLE consumo AS SELECT * FROM consumo_view")
        con.execute("CREATE OR REPLACE TABLE paises AS SELECT * FROM paises_view")


def run():
    df = load_raw()
    df_long = to_long(df)
    save(df_long)
    return df_long, quality_report(df)


if __name__ == "__main__":
    df_long, report = run()
    print(report)
    print(f"Tabla consumo: {len(df_long)} filas | Base: {config.DB_PATH}")