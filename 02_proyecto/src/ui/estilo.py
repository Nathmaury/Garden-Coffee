import plotly.graph_objects as go
import plotly.io as pio

HOJA = "#1F4D3A"
CEREZA = "#A4243B"
SECADO = "#C08A2E"
BROTE = "#7A8B3C"
GRANO = "#2B211C"
NIEBLA = "#5B6C8F"
FONDO = "#F7F8F4"
LINEA = "#DCE2D5"

SEGMENTOS = {
    "Motores de crecimiento": HOJA,
    "Maduros estancados": SECADO,
    "Emergentes volátiles": CEREZA,
    "Marginales": "#9AA393",
}

CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Instrument+Sans:wght@400;500;600&family=Instrument+Serif&display=swap');
.stApp, .stApp p, .stApp li, .stApp label, .stApp input, .stApp textarea, .stApp button {{
    font-family: 'Instrument Sans', system-ui, sans-serif;
}}
.stApp h1, .stApp h2, .stApp h3 {{
    font-family: 'Instrument Serif', Georgia, serif;
    font-weight: 400;
    color: {GRANO};
    letter-spacing: -0.01em;
}}
.stApp h1 {{ font-size: 3rem; line-height: 1.05; max-width: 18ch; }}
.bajada {{ font-size: 1.1rem; max-width: 62ch; color: #4A403A; line-height: 1.55; }}
.cifra {{ border-left: 3px solid {HOJA}; padding: 0.2rem 0 0.2rem 0.9rem; }}
.cifra b {{ display: block; font-family: 'Instrument Serif', Georgia, serif; font-size: 2.2rem; font-weight: 400; color: {GRANO}; line-height: 1.1; }}
.cifra span {{ font-size: 0.92rem; color: #5E554F; }}
[data-testid="stChatMessage"] {{ background: #FFFFFF; border: 1px solid {LINEA}; border-radius: 10px; }}
[data-testid="stTabs"] button p {{ font-size: 1rem; }}
</style>
"""


def registrar_tema():
    pio.templates["garden"] = go.layout.Template(
        layout=dict(
            font=dict(family="Instrument Sans, system-ui, sans-serif", color=GRANO, size=13),
            title=dict(font=dict(family="Instrument Serif, Georgia, serif", size=22, color=GRANO), x=0, xanchor="left"),
            colorway=[HOJA, CEREZA, SECADO, BROTE, NIEBLA, GRANO],
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(gridcolor=LINEA, zeroline=False, linecolor=LINEA),
            yaxis=dict(gridcolor=LINEA, zeroline=False, linecolor=LINEA),
            legend=dict(orientation="h", y=-0.2, title_text=""),
            margin=dict(l=10, r=10, t=60, b=10),
            hoverlabel=dict(font_family="Instrument Sans, system-ui, sans-serif"),
        )
    )
    pio.templates.default = "plotly_white+garden"


def cifra(valor, texto):
    return f'<div class="cifra"><b>{valor}</b><span>{texto}</span></div>'