import json
import re
from functools import lru_cache
from pathlib import Path

import duckdb
import plotly.express as px
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from src import config

MAX_FILAS = 100
CONTEXTO = Path(__file__).with_name("contexto.md")
PROHIBIDAS = re.compile(
    r"\b(insert|update|delete|drop|create|alter|attach|detach|copy|pragma|install|load|export|import|call|truncate)\b|read_\w+\s*\(|glob\s*\(",
    re.IGNORECASE,
)
TIPOS_GRAFICO = {"linea": px.line, "barras": px.bar, "dispersion": px.scatter, "area": px.area}

ESQUEMAS = [
    {
        "type": "function",
        "function": {
            "name": "consultar_datos",
            "description": "Ejecuta una consulta SQL de solo lectura (DuckDB) sobre las tablas del proyecto y devuelve el resultado en CSV. Úsala para obtener cualquier cifra antes de responder.",
            "parameters": {
                "type": "object",
                "properties": {"sql": {"type": "string", "description": "Una sola consulta SELECT o WITH en dialecto DuckDB."}},
                "required": ["sql"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "crear_grafico",
            "description": "Ejecuta una consulta SQL y genera un gráfico Plotly con el resultado. Úsala cuando el usuario pida un gráfico o cuando una visualización aclare la respuesta.",
            "parameters": {
                "type": "object",
                "properties": {
                    "sql": {"type": "string", "description": "Consulta SELECT que devuelve los datos ya agregados para el gráfico."},
                    "tipo": {"type": "string", "enum": ["linea", "barras", "barras_horizontales", "dispersion", "area"]},
                    "x": {"type": "string", "description": "Columna del resultado para el eje X (en barras_horizontales, la columna de categorías)."},
                    "y": {"type": "string", "description": "Columna del resultado para el eje Y (en barras_horizontales, la columna de valores)."},
                    "color": {"type": "string", "description": "Columna opcional para separar series por color."},
                    "titulo": {"type": "string", "description": "Título del gráfico en español."},
                },
                "required": ["sql", "tipo", "x", "y", "titulo"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "buscar_contexto",
            "description": "Busca en la documentación del análisis (metodología, calidad de datos, supuestos, hallazgos y limitaciones). Úsala para preguntas de por qué, cómo se calculó algo o qué significa una métrica.",
            "parameters": {
                "type": "object",
                "properties": {"consulta": {"type": "string", "description": "Tema a buscar, en español."}},
                "required": ["consulta"],
            },
        },
    },
]


def validar_sql(sql):
    limpio = sql.strip().rstrip(";").strip()
    if ";" in limpio:
        raise ValueError("Solo se permite una consulta por llamada.")
    if not re.match(r"^(select|with)\b", limpio, re.IGNORECASE):
        raise ValueError("Solo se permiten consultas SELECT o WITH.")
    if PROHIBIDAS.search(limpio):
        raise ValueError("La consulta contiene operaciones no permitidas.")
    return limpio


def ejecutar_sql(sql):
    if not config.DB_PATH.exists():
        raise FileNotFoundError("La base de datos no existe. Ejecuta: python -m src.build")
    with duckdb.connect(str(config.DB_PATH), read_only=True) as con:
        return con.execute(validar_sql(sql)).fetchdf()


def a_texto(df):
    total = len(df)
    texto = df.head(MAX_FILAS).round(2).to_csv(index=False)
    if total > MAX_FILAS:
        texto += f"\n(Se muestran {MAX_FILAS} de {total} filas. Agrega o filtra para obtener menos filas.)"
    return texto if total else "La consulta no devolvió filas."


def consultar_datos(sql, registro):
    df = ejecutar_sql(sql)
    registro["consultas"].append(sql)
    return a_texto(df)


def crear_grafico(sql, tipo, x, y, titulo, registro, color=None):
    df = ejecutar_sql(sql)
    faltantes = [c for c in (x, y, color) if c and c not in df.columns]
    if faltantes:
        raise ValueError(f"Columnas no encontradas: {faltantes}. Columnas disponibles: {list(df.columns)}")
    if tipo == "barras_horizontales":
        fig = px.bar(df, x=y, y=x, color=color, orientation="h", title=titulo)
        fig.update_layout(yaxis=dict(categoryorder="total ascending"))
    elif tipo in TIPOS_GRAFICO:
        fig = TIPOS_GRAFICO[tipo](df, x=x, y=y, color=color, title=titulo)
    else:
        raise ValueError(f"Tipo de gráfico no soportado: {tipo}")
    if tipo == "linea":
        fig.update_traces(mode="lines+markers")
    registro["consultas"].append(sql)
    registro["graficos"].append(fig)
    return f"Gráfico '{titulo}' creado y mostrado al usuario. Datos usados:\n{a_texto(df)}"


@lru_cache(maxsize=1)
def _indice_contexto():
    texto = CONTEXTO.read_text(encoding="utf-8")
    secciones = [s.strip() for s in re.split(r"^## ", texto, flags=re.MULTILINE) if s.strip()]
    vectorizador = TfidfVectorizer(strip_accents="unicode", lowercase=True)
    return secciones, vectorizador, vectorizador.fit_transform(secciones)


def buscar_contexto(consulta, registro, k=2):
    secciones, vectorizador, matriz = _indice_contexto()
    similitud = cosine_similarity(vectorizador.transform([consulta]), matriz)[0]
    mejores = similitud.argsort()[::-1][:k]
    registro["contexto"].append(consulta)
    return "\n\n".join(f"## {secciones[i]}" for i in mejores)


FUNCIONES = {"consultar_datos": consultar_datos, "crear_grafico": crear_grafico, "buscar_contexto": buscar_contexto}


def ejecutar(nombre, argumentos, registro):
    try:
        args = json.loads(argumentos or "{}")
        if nombre not in FUNCIONES:
            raise ValueError(f"Herramienta desconocida: {nombre}")
        return FUNCIONES[nombre](registro=registro, **args)
    except Exception as error:
        return f"ERROR: {error} Corrige la llamada e inténtalo de nuevo."