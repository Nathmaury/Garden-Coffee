import json
import re
import sys
import time
import unicodedata
from pathlib import Path

import pandas as pd

from src.agent.loop import Agente
from src.agent.tools import ejecutar_sql

CARPETA = Path(__file__).parent
TOLERANCIA = 0.03
FRASES_RECHAZO = ["no contiene", "no tiene", "no tengo", "no hay", "no incluye", "no dispon", "no es posible", "no puedo", "no se puede", "no cuento", "fuera del alcance", "no aparece", "no esta", "no figura", "no forma parte", "no se encuentra", "solo incluye", "unicamente"]


def normalizar(texto):
    texto = unicodedata.normalize("NFKD", texto.lower())
    return "".join(c for c in texto if not unicodedata.combining(c))


def numeros(texto):
    valores = set()
    for token in re.findall(r"\d[\d.,]*\d|\d", texto):
        for limpio in (token.replace(",", ""), token.replace(".", "").replace(",", ".")):
            try:
                valores.add(float(limpio))
            except ValueError:
                pass
    return valores


def aparece(esperado, encontrados):
    return any(abs(v - esperado) <= abs(esperado) * TOLERANCIA for v in encontrados)


def evaluar(caso, resultado):
    respuesta = resultado["respuesta"]
    texto = normalizar(respuesta)
    fallas = []
    if "sql" in caso:
        esperados = [float(v) for v in ejecutar_sql(caso["sql"]).iloc[0].tolist()]
        encontrados = numeros(respuesta)
        faltan = [round(v, 2) for v in esperados if not aparece(v, encontrados)]
        if faltan:
            fallas.append(f"no aparece el valor esperado {faltan}")
    if "sql_texto" in caso:
        esperado = str(ejecutar_sql(caso["sql_texto"]).iloc[0, 0])
        if normalizar(esperado) not in texto:
            fallas.append(f"no menciona '{esperado}'")
    for palabra in caso.get("contiene", []):
        if normalizar(palabra) not in texto:
            fallas.append(f"no menciona '{palabra}'")
    if caso.get("grafico") and not resultado["graficos"]:
        fallas.append("no generó gráfico")
    if caso.get("rechazo") and not any(f in texto for f in FRASES_RECHAZO):
        fallas.append("no indicó que los datos no permiten responder")
    return not fallas, "; ".join(fallas)


def main():
    rondas = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    casos = json.loads((CARPETA / "golden_set.json").read_text(encoding="utf-8"))
    filas = []
    for ronda in range(1, rondas + 1):
        print(f"\nRonda {ronda} de {rondas}")
        for caso in casos:
            inicio = time.time()
            try:
                resultado = Agente().preguntar(caso["pregunta"])
                correcto, detalle = evaluar(caso, resultado)
            except Exception as error:
                resultado = {"respuesta": "", "pasos": 0, "tokens": 0, "graficos": []}
                correcto, detalle = False, f"error: {error}"
            filas.append({
                "ronda": ronda,
                "id": caso["id"],
                "categoria": caso["categoria"],
                "pregunta": caso["pregunta"],
                "correcto": correcto,
                "detalle": detalle,
                "pasos": resultado["pasos"],
                "tokens": resultado["tokens"],
                "segundos": round(time.time() - inicio, 1),
                "respuesta": resultado["respuesta"],
            })
            print(f"{'OK   ' if correcto else 'FALLA'} {caso['id']} {caso['pregunta']} {detalle}")

    df = pd.DataFrame(filas)
    df.to_csv(CARPETA / "resultados.csv", index=False, encoding="utf-8")
    por_caso = df.groupby(["categoria", "id"])["correcto"].mean().reset_index()
    resumen = df.groupby("categoria").agg(casos=("id", "nunique"), respuestas=("id", "count"), exactitud_pct=("correcto", "mean"))
    resumen["casos_estables"] = por_caso.assign(estable=por_caso["correcto"] == 1).groupby("categoria")["estable"].sum()
    total = pd.DataFrame(
        {
            "casos": [df["id"].nunique()],
            "respuestas": [len(df)],
            "exactitud_pct": [df["correcto"].mean()],
            "casos_estables": [int((por_caso["correcto"] == 1).sum())],
        },
        index=["TOTAL"],
    )
    resumen = pd.concat([resumen, total])
    resumen["exactitud_pct"] = (resumen["exactitud_pct"] * 100).round(1)
    metricas = (
        f"Rondas: {rondas} | Pasos promedio: {df['pasos'].mean():.1f} | Tokens promedio: {df['tokens'].mean():,.0f} | "
        f"Tiempo promedio: {df['segundos'].mean():.1f} s"
    )
    fallas = df[~df["correcto"]][["ronda", "id", "detalle"]]
    texto_fallas = "\n\nFallas:\n\n" + fallas.to_markdown(index=False) if len(fallas) else "\n\nSin fallas."
    (CARPETA / "resumen.md").write_text(
        "# Resultados de la evaluación del agente\n\n" + resumen.to_markdown() + f"\n\n{metricas}" + texto_fallas + "\n",
        encoding="utf-8",
    )
    print("\n", resumen.to_string())
    print(metricas)


if __name__ == "__main__":
    main()