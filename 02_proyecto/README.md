# High Garden Coffee — Agente analítico

## Descripción

## Arquitectura

## Requisitos
- Python 3.11 o superior
- API key de Anthropic

## Instalacion

Windows (PowerShell):
```
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Mac/Linux:
```
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Configuracion
Copiar `.env.example` como `.env` y completar `ANTHROPIC_API_KEY` y `LLM_MODEL`.

## Ejecución
```
python -m src.build
streamlit run app.py
```

## Estructura

## Evaluación

## Supuestos y limitaciones