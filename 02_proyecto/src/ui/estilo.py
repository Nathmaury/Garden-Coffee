import plotly.graph_objects as go
import plotly.io as pio

AZUL = "#245E40"
AZUL_MEDIO = "#2F6DB5"
AZUL_CLARO = "#9DB7DA"
AMBAR = "#C77D1A"
VERDE = "#1F8A84"
GRIS = "#7A8699"
TINTA = "#1A2433"
TENUE = "#5A6577"
LINEA = "#D9E0EA"
FONDO = "#F4F6FA"

SEGMENTOS = {
    "Motores de crecimiento": AZUL,
    "Maduros estancados": GRIS,
    "Emergentes volátiles": AMBAR,
    "Marginales": "#C3CAD5",
}

CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600&display=swap');
.stApp, .stApp p, .stApp li, .stApp label, .stApp input, .stApp textarea, .stApp button, .stApp h1, .stApp h2, .stApp h3 {{
    font-family: 'IBM Plex Sans', system-ui, -apple-system, 'Segoe UI', sans-serif;
}}
.stApp h1 {{ font-size: 1.8rem; font-weight: 600; color: {AZUL}; letter-spacing: -0.005em; padding-bottom: 0.2rem; }}
.stApp h2, .stApp h3 {{ font-size: 1.1rem; font-weight: 600; color: {AZUL_MEDIO}; }}
.subtitulo {{ color: {TENUE}; font-size: 1rem; max-width: 70ch; margin-bottom: 1.2rem; }}

[data-testid="stSidebar"] {{ background: {AZUL}; }}
[data-testid="stSidebar"] p, [data-testid="stSidebar"] li {{ color: #D6E0EE; }}
[data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {{ color: #FFFFFF; }}
[data-testid="stSidebar"] .stButton button {{ background: transparent; color: #FFFFFF; border: 1px solid rgba(255,255,255,0.45); }}
[data-testid="stSidebar"] .stButton button:hover {{ background: rgba(255,255,255,0.1); border-color: #FFFFFF; color: #FFFFFF; }}
[data-testid="stSidebar"] .stButton button p {{ color: #FFFFFF; }}

.kpis {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
    background: #FFFFFF;
    border: 1px solid {LINEA};
    border-top: 3px solid {AZUL};
    border-radius: 6px;
    margin-bottom: 1.5rem;
}}
.kpi {{ padding: 0.9rem 1.1rem; border-left: 1px solid {LINEA}; }}
.kpi:first-child {{ border-left: none; }}
.kpi span {{ display: block; font-size: 0.82rem; color: {TENUE}; }}
.kpi b {{ display: block; font-size: 1.45rem; font-weight: 600; color: {AZUL}; font-variant-numeric: tabular-nums; margin-top: 0.15rem; }}

[data-testid="stChatMessage"] {{ background: #FFFFFF; border: 1px solid {LINEA}; border-radius: 6px; padding: 1rem; }}
.stMain .stButton button {{ background: #FFFFFF; border: 1px solid {LINEA}; border-radius: 6px; text-align: left; justify-content: flex-start; min-height: 3.2rem; }}
.stMain .stButton button:hover {{ border-color: {AZUL_MEDIO}; color: {AZUL}; }}
.stButton button p {{ white-space: normal; overflow: visible; text-overflow: clip; }}
[data-testid="stTabs"] button p {{ font-size: 0.95rem; font-weight: 500; }}
[data-testid="stTabs"] button[aria-selected="true"] p {{ color: {AZUL}; font-weight: 600; }}
[data-testid="stExpander"] {{ background: #FFFFFF; }}
</style>
"""


def registrar_tema():
    pio.templates["garden"] = go.layout.Template(
        layout=dict(
            font=dict(family="IBM Plex Sans, system-ui, sans-serif", color=TINTA, size=13),
            title=dict(font=dict(family="IBM Plex Sans, system-ui, sans-serif", size=16, color=AZUL), x=0, xanchor="left"),
            colorway=[AZUL, AZUL_MEDIO, AMBAR, GRIS, VERDE, AZUL_CLARO],
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(gridcolor="#E3E8F0", zeroline=False, linecolor=LINEA),
            yaxis=dict(gridcolor="#E3E8F0", zeroline=False, linecolor=LINEA),
            legend=dict(orientation="h", y=-0.2, title_text=""),
            margin=dict(l=10, r=10, t=50, b=10),
            hoverlabel=dict(font_family="IBM Plex Sans, system-ui, sans-serif"),
        )
    )
    pio.templates.default = "plotly_white+garden"


def kpis(items):
    celdas = "".join(f'<div class="kpi"><span>{etiqueta}</span><b>{valor}</b></div>' for etiqueta, valor in items)
    return f'<div class="kpis">{celdas}</div>'