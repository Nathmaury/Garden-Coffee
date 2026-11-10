import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src import build, config
from src.agent import llm
from src.agent.loop import Agente
from src.agent.tools import ejecutar_sql
from src.ui import estilo

st.set_page_config(page_title="Garden Coffee | Agente analítico", page_icon="☕", layout="wide")
estilo.registrar_tema()
st.markdown(estilo.CSS, unsafe_allow_html=True)

AVATARES = {"user": ":material/person:", "assistant": ":material/query_stats:"}

SUGERENCIAS = [
    "¿Qué mercados conviene priorizar y por qué?",
    "Muéstrame la evolución del consumo de Vietnam",
    "¿Cuánto consumirá Brasil en 2024 y con qué rango?",
    "Compara el crecimiento por región en la última década",
    "¿Por qué se eligió AutoETS para el pronóstico?",
    "¿Cuál será el precio del café en 2025?",
]


@st.cache_resource(show_spinner="Preparando la base de datos por primera vez (1-2 minutos)")
def preparar_base():
    if not config.DB_PATH.exists():
        build.main()
    return True


@st.cache_data(show_spinner=False)
def consulta(sql):
    return ejecutar_sql(sql)


def agente_disponible():
    try:
        llm.cliente()
        return True, ""
    except Exception as error:
        return False, str(error)


def miles(valor, decimales=0):
    texto = f"{valor:,.{decimales}f}"
    return texto.replace(",", "X").replace(".", ",").replace("X", ".")


def encabezado():
    total = consulta("SELECT year, SUM(consumption_kg) AS kg FROM consumo WHERE reported GROUP BY year ORDER BY year").set_index("year")["kg"]
    region = consulta(
        "SELECT year, region, SUM(consumption_kg) AS kg FROM consumo WHERE reported AND year IN (1990, 2019) GROUP BY year, region"
    )
    brasil = consulta("SELECT consumption_kg AS kg FROM consumo WHERE country = 'Brazil' AND year = 2019")["kg"].iloc[0]
    futuro = consulta("SELECT consumo_kg FROM pronosticos WHERE country = 'TOTAL' AND year = 2024")["consumo_kg"].iloc[0]
    asia = region[region["region"] == "Asia y Oceanía"].set_index("year")["kg"]

    st.title("Garden Coffee | Análisis de demanda")
    st.markdown(
        '<p class="subtitulo">Consumo doméstico de café en 55 países productores entre 1990 y 2019, con pronóstico a 2024. '
        "Pregúntale al agente o revisa el panorama, los pronósticos y los mercados.</p>",
        unsafe_allow_html=True,
    )
    st.markdown(
        estilo.kpis([
            ("Consumo 2019", f"{miles(total[2019] / 1e6)} M kg"),
            ("Crecimiento desde 1990", f"×{miles(total[2019] / total[1990], 1)}"),
            ("Participación de Brasil", f"{miles(brasil / total[2019] * 100)} %"),
            ("Participación de Asia", f"{miles(asia[2019] / total[2019] * 100)} %"),
            ("Crecimiento anual esperado a 2024", f"{miles(((futuro / total[2019]) ** (1 / 5) - 1) * 100, 1)} %"),
        ]),
        unsafe_allow_html=True,
    )


def contenido(item, indice):
    st.markdown(item["texto"])
    for j, fig in enumerate(item.get("graficos", [])):
        st.plotly_chart(fig, width="stretch", key=f"grafico_{indice}_{j}")
    if item.get("consultas"):
        with st.expander(f"Ver las consultas SQL usadas ({len(item['consultas'])})"):
            for sql in item["consultas"]:
                st.code(sql, language="sql")
            st.caption(f"{item['pasos']} pasos del agente y {miles(item['tokens'])} tokens.")


def pestana_agente():
    disponible, error = agente_disponible()
    if not disponible:
        st.info(f"El agente no está configurado: {error}. Completa el archivo .env como indica el README y reinicia la app.")
        return
    if "agente" not in st.session_state:
        st.session_state.agente = Agente()
        st.session_state.historial = []

    _, col_boton = st.columns([5, 1])
    if col_boton.button("Nueva conversación", width="stretch", disabled=not st.session_state.historial):
        st.session_state.agente.reiniciar()
        st.session_state.historial = []
        st.rerun()

    for indice, item in enumerate(st.session_state.historial):
        with st.chat_message(item["rol"], avatar=AVATARES[item["rol"]]):
            contenido(item, indice)

    sugerida = None
    if not st.session_state.historial:
        st.markdown("Empieza con una de estas preguntas o escribe la tuya abajo.")
        columnas = st.columns(3)
        for i, texto in enumerate(SUGERENCIAS):
            if columnas[i % 3].button(texto, key=f"sugerencia_{i}", width="stretch"):
                sugerida = texto

    pregunta = st.chat_input("Pregunta sobre consumo, pronósticos o mercados") or sugerida
    if not pregunta:
        return

    st.session_state.historial.append({"rol": "user", "texto": pregunta})
    with st.chat_message("user", avatar=AVATARES["user"]):
        st.markdown(pregunta)
    agente = st.session_state.agente
    previo = list(agente.mensajes)
    with st.chat_message("assistant", avatar=AVATARES["assistant"]):
        with st.spinner("Consultando los datos"):
            try:
                r = agente.preguntar(pregunta)
                respuesta = {"rol": "assistant", "texto": r["respuesta"], "graficos": r["graficos"], "consultas": r["consultas"], "pasos": r["pasos"], "tokens": r["tokens"]}
            except Exception as e:
                agente.mensajes = previo
                respuesta = {"rol": "assistant", "texto": f"No pude completar la consulta con el modelo. Detalle: {e}"}
    st.session_state.historial.append(respuesta)
    st.rerun()


def pestana_panorama():
    total = consulta("SELECT year, SUM(consumption_kg) / 1e6 AS millones_kg FROM consumo WHERE reported GROUP BY year ORDER BY year")
    fig = px.line(total, x="year", y="millones_kg", markers=True, title="Consumo total en países productores",
                  labels={"year": "Año", "millones_kg": "Millones de kg"})
    st.plotly_chart(fig, width="stretch")

    col1, col2 = st.columns(2)
    region = consulta("SELECT year, region, SUM(consumption_kg) AS kg FROM consumo WHERE reported GROUP BY year, region ORDER BY year")
    fig = px.area(region, x="year", y="kg", color="region", groupnorm="percent", title="Participación por región",
                  labels={"year": "Año", "kg": "% del consumo", "region": "Región"})
    col1.plotly_chart(fig, width="stretch")

    top = consulta(
        "SELECT country, consumption_kg / 1e6 AS millones_kg FROM consumo WHERE year = 2019 AND reported ORDER BY consumption_kg DESC LIMIT 10"
    )
    fig = px.bar(top, x="millones_kg", y="country", orientation="h", title="Los 10 mayores consumidores en 2019",
                 labels={"millones_kg": "Millones de kg", "country": ""})
    fig.update_layout(yaxis=dict(categoryorder="total ascending"))
    col2.plotly_chart(fig, width="stretch")


def pestana_pronosticos():
    paises = consulta("SELECT DISTINCT country FROM pronosticos WHERE country <> 'TOTAL' ORDER BY country")["country"].tolist()
    eleccion = st.selectbox("Serie", ["Total"] + paises)
    serie = "TOTAL" if eleccion == "Total" else eleccion.replace("'", "''")

    if serie == "TOTAL":
        hist = consulta("SELECT year, SUM(consumption_kg) / 1e6 AS v FROM consumo WHERE reported GROUP BY year ORDER BY year")
    else:
        hist = consulta(f"SELECT year, consumption_kg / 1e6 AS v FROM consumo WHERE country = '{serie}' ORDER BY year")
    fut = consulta(f"SELECT * FROM pronosticos WHERE country = '{serie}' ORDER BY year")
    m = lambda c: fut[c] / 1e6

    fig = go.Figure()
    fig.add_scatter(x=fut["year"], y=m("rango95_alto_kg"), line=dict(width=0), showlegend=False, hoverinfo="skip")
    fig.add_scatter(x=fut["year"], y=m("rango95_bajo_kg"), line=dict(width=0), fill="tonexty", fillcolor="rgba(11,46,89,0.10)", name="Rango 95 %")
    fig.add_scatter(x=fut["year"], y=m("rango80_alto_kg"), line=dict(width=0), showlegend=False, hoverinfo="skip")
    fig.add_scatter(x=fut["year"], y=m("rango80_bajo_kg"), line=dict(width=0), fill="tonexty", fillcolor="rgba(11,46,89,0.22)", name="Rango 80 %")
    fig.add_scatter(x=hist["year"], y=hist["v"], mode="lines", name="Histórico", line=dict(color=estilo.TINTA))
    fig.add_scatter(x=fut["year"], y=m("consumo_kg"), mode="lines+markers", name="Pronóstico", line=dict(color=estilo.AZUL, dash="dash"))
    fig.update_layout(title=f"{eleccion}: histórico y pronóstico 2020–2024", xaxis_title="Año", yaxis_title="Millones de kg")
    st.plotly_chart(fig, width="stretch")

    ultimo = fut.iloc[-1]
    st.markdown(
        f"Para 2024 el modelo espera **{miles(ultimo['consumo_kg'] / 1e6)} millones de kg**, con un 80 % de probabilidad "
        f"de quedar entre {miles(ultimo['rango80_bajo_kg'] / 1e6)} y {miles(ultimo['rango80_alto_kg'] / 1e6)}."
    )

    st.subheader("Cómo se eligió el modelo")
    evaluacion = consulta("SELECT * FROM evaluacion_modelos ORDER BY smape_promedio_pct")
    st.dataframe(
        evaluacion,
        hide_index=True,
        width="stretch",
        column_config={
            "modelo": "Modelo",
            "smape_promedio_pct": st.column_config.NumberColumn("Error promedio (sMAPE %)", format="%.2f"),
            "smape_total_pct": st.column_config.NumberColumn("Error en el total (%)", format="%.2f"),
            "series_donde_gana": "Series donde gana",
            "cobertura_80_pct": st.column_config.NumberColumn("Acierto rango 80 %", format="%.1f"),
            "cobertura_95_pct": st.column_config.NumberColumn("Acierto rango 95 %", format="%.1f"),
            "seleccionado": st.column_config.CheckboxColumn("Elegido"),
        },
    )
    st.caption("Backtest con tres cortes (2012, 2013 y 2014) pronosticando cinco años en cada uno.")


def pestana_mercados():
    mercados = consulta("SELECT * FROM mercados ORDER BY ranking")
    fig = px.scatter(
        mercados, x="cagr_reciente_pct", y="consumo_2019_mkg", color="segmento", hover_name="country",
        size="score", size_max=22, log_y=True, color_discrete_map=estilo.SEGMENTOS,
        title="Tamaño y crecimiento reciente de cada mercado",
        labels={"cagr_reciente_pct": "Crecimiento anual 2010–2019 (%)", "consumo_2019_mkg": "Consumo 2019 (millones de kg, escala log)", "segmento": "Segmento"},
    )
    st.plotly_chart(fig, width="stretch")

    st.subheader("Ranking de oportunidad")
    st.dataframe(
        mercados[["ranking", "country", "region", "segmento", "score", "consumo_2019_mkg", "crec_esperado_pct", "volatilidad_pct"]],
        hide_index=True,
        width="stretch",
        column_config={
            "ranking": "#",
            "country": "País",
            "region": "Región",
            "segmento": "Segmento",
            "score": st.column_config.ProgressColumn("Score", min_value=0, max_value=100, format="%.0f"),
            "consumo_2019_mkg": st.column_config.NumberColumn("Consumo 2019 (M kg)", format="%.1f"),
            "crec_esperado_pct": st.column_config.NumberColumn("Crec. esperado anual (%)", format="%.1f"),
            "volatilidad_pct": st.column_config.NumberColumn("Volatilidad (%)", format="%.1f"),
        },
    )
    st.caption("El score combina tamaño (35 %), crecimiento esperado (35 %), estabilidad (15 %) y certidumbre del pronóstico (15 %).")


def barra_lateral():
    with st.sidebar:
        st.subheader("Sobre estos datos")
        st.markdown(
            "Consumo doméstico de café en 55 países productores, de 1990 a 2019, en kilogramos. "
            "Los pronósticos llegan a 2024 y no incluyen precios, porque el dataset no los tiene."
        )
        if st.button("Recalcular datos y modelos", width="stretch"):
            with st.spinner("Recalculando (1-2 minutos)"):
                build.main()
            st.cache_data.clear()
            st.rerun()


preparar_base()
barra_lateral()
encabezado()
tab_agente, tab_panorama, tab_pronosticos, tab_mercados = st.tabs(["Pregúntale a los datos", "Panorama", "Pronósticos", "Mercados"])
with tab_agente:
    pestana_agente()
with tab_panorama:
    pestana_panorama()
with tab_pronosticos:
    pestana_pronosticos()
with tab_mercados:
    pestana_mercados()