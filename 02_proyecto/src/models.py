import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler
from statsforecast import StatsForecast
from statsforecast.models import AutoARIMA, AutoETS, AutoTheta, Naive, RandomWalkWithDrift

from src.regions import add_region

HORIZONTE = 5
NIVELES = [80, 95]
MODELOS = ["Naive", "RWD", "AutoETS", "AutoARIMA", "AutoTheta"]
MODELO_FINAL = "AutoETS"
VARIABLES_SEGMENTACION = ["log_consumo", "cagr_reciente_pct", "log_volatilidad", "crec_esperado_pct"]
PESOS_SCORE = {"tamano": 0.35, "crecimiento": 0.35, "estabilidad": 0.15, "certidumbre": 0.15}


def cagr(inicio, fin, anios):
    return (fin / inicio) ** (1 / anios) - 1


def _con_unique_id(df):
    return df.reset_index() if "unique_id" not in df.columns else df


def preparar_series(df_long):
    valido = df_long[df_long["reported"]]
    excluir = df_long.loc[~df_long["reported"] | df_long["flat_series"] | df_long["zero_flag"], "country"].unique()
    paises = df_long[~df_long["country"].isin(excluir)]
    series = paises.rename(columns={"country": "unique_id", "consumption_kg": "y"})[["unique_id", "year", "y"]]
    total = (
        valido.groupby("year", as_index=False)["consumption_kg"].sum()
        .rename(columns={"consumption_kg": "y"})
        .assign(unique_id="TOTAL")
    )
    series = pd.concat([series, total], ignore_index=True)
    series["ds"] = pd.to_datetime(series["year"].astype(str), format="%Y")
    return series[["unique_id", "ds", "y"]]


def backtest(series):
    sf = StatsForecast(
        models=[Naive(), RandomWalkWithDrift(), AutoETS(season_length=1), AutoARIMA(season_length=1), AutoTheta(season_length=1)],
        freq="YS",
        n_jobs=1,
    )
    cv = _con_unique_id(sf.cross_validation(df=series, h=HORIZONTE, n_windows=3, step_size=1, level=NIVELES))
    smape_serie = pd.DataFrame({
        m: (2 * (cv[m] - cv["y"]).abs() / (cv["y"].abs() + cv[m].abs()) * 100).groupby(cv["unique_id"]).mean()
        for m in MODELOS
    })
    evaluacion = pd.DataFrame({
        "smape_promedio_pct": smape_serie.mean(),
        "smape_total_pct": smape_serie.loc["TOTAL"],
        "series_donde_gana": smape_serie.idxmin(axis=1).value_counts().reindex(MODELOS, fill_value=0),
        "cobertura_80_pct": pd.Series({m: cv["y"].between(cv[f"{m}-lo-80"], cv[f"{m}-hi-80"]).mean() * 100 for m in MODELOS}),
        "cobertura_95_pct": pd.Series({m: cv["y"].between(cv[f"{m}-lo-95"], cv[f"{m}-hi-95"]).mean() * 100 for m in MODELOS}),
    }).astype(float)
    evaluacion["series_donde_gana"] = evaluacion["series_donde_gana"].astype(int)
    evaluacion["seleccionado"] = evaluacion.index == MODELO_FINAL
    return evaluacion.rename_axis("modelo").reset_index().sort_values("smape_promedio_pct")


def pronosticar(series):
    sf = StatsForecast(models=[AutoETS(season_length=1)], freq="YS", n_jobs=1)
    fc = _con_unique_id(sf.forecast(df=series, h=HORIZONTE, level=NIVELES))
    m = MODELO_FINAL
    return pd.DataFrame({
        "country": fc["unique_id"],
        "year": fc["ds"].dt.year,
        "consumo_kg": fc[m].astype(float),
        "rango80_bajo_kg": fc[f"{m}-lo-80"].astype(float),
        "rango80_alto_kg": fc[f"{m}-hi-80"].astype(float),
        "rango95_bajo_kg": fc[f"{m}-lo-95"].astype(float),
        "rango95_alto_kg": fc[f"{m}-hi-95"].astype(float),
        "modelo": m,
    })


def construir_variables(df_long, series, pronostico):
    pivot = df_long[df_long["reported"]].pivot(index="country", columns="year", values="consumption_kg")
    paises = [p for p in series["unique_id"].unique() if p != "TOTAL"]
    p = pivot.loc[paises]
    f_fin = pronostico[pronostico["year"] == pronostico["year"].max()].set_index("country").loc[paises]
    f = pd.DataFrame(index=pd.Index(paises, name="country"))
    f["consumo_2019_mkg"] = p[2019] / 1e6
    f["log_consumo"] = np.log10(p[2019])
    f["cagr_hist_pct"] = cagr(p[1990], p[2019], 29) * 100
    f["cagr_reciente_pct"] = cagr(p[2010], p[2019], 9) * 100
    f["volatilidad_pct"] = (p.pct_change(axis=1) * 100).std(axis=1)
    f["log_volatilidad"] = np.log10(f["volatilidad_pct"])
    f["crec_esperado_pct"] = cagr(p[2019], f_fin["consumo_kg"], HORIZONTE) * 100
    f["incertidumbre_pct"] = (f_fin["rango80_alto_kg"] - f_fin["rango80_bajo_kg"]) / f_fin["consumo_kg"] * 100
    return f


def segmentar(features, k=4):
    x_raw = features[VARIABLES_SEGMENTACION]
    x_raw = x_raw.clip(x_raw.quantile(0.05), x_raw.quantile(0.95), axis=1)
    x = StandardScaler().fit_transform(x_raw)
    out = features.copy()
    out["cluster"] = KMeans(n_clusters=k, n_init=50, random_state=42).fit_predict(x)
    perfil = out.groupby("cluster")[["consumo_2019_mkg", "volatilidad_pct"]].median()
    nombres = {perfil["consumo_2019_mkg"].idxmax(): "Motores de crecimiento"}
    resto = perfil.drop(list(nombres))
    nombres[resto["volatilidad_pct"].idxmax()] = "Emergentes volátiles"
    resto = perfil.drop(list(nombres))
    nombres[resto["consumo_2019_mkg"].idxmin()] = "Marginales"
    resto = perfil.drop(list(nombres))
    nombres[resto.index[0]] = "Maduros estancados"
    out["segmento"] = out["cluster"].map(nombres)
    return out, float(silhouette_score(x, out["cluster"]))


def calcular_score(features, pesos=PESOS_SCORE):
    componentes = pd.DataFrame({
        "tamano": features["log_consumo"].rank(pct=True),
        "crecimiento": features["crec_esperado_pct"].rank(pct=True),
        "estabilidad": (-features["volatilidad_pct"]).rank(pct=True),
        "certidumbre": (-features["incertidumbre_pct"]).rank(pct=True),
    })
    return (componentes * pd.Series(pesos)).sum(axis=1) * 100


def run(df_long):
    series = preparar_series(df_long)
    evaluacion = backtest(series)
    pronostico = pronosticar(series)
    mercados, silhouette = segmentar(construir_variables(df_long, series, pronostico))
    mercados["score"] = calcular_score(mercados)
    mercados["ranking"] = mercados["score"].rank(ascending=False, method="min").astype(int)
    info = add_region(df_long.drop_duplicates("country")[["country", "coffee_type"]])
    mercados = mercados.reset_index().merge(info, on="country", how="left")
    columnas = [
        "ranking", "country", "region", "coffee_type", "segmento", "score", "consumo_2019_mkg",
        "cagr_hist_pct", "cagr_reciente_pct", "volatilidad_pct", "crec_esperado_pct", "incertidumbre_pct",
    ]
    mercados = mercados[columnas].sort_values("ranking").reset_index(drop=True)
    return {"pronosticos": pronostico, "evaluacion_modelos": evaluacion, "mercados": mercados}, silhouette