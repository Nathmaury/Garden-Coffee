# High Garden Coffee  Agente analítico

## Descripción

## Arquitectura

## Requisitos
- Python 3.11 o superior
- Un deployment de Azure OpenAI con soporte de function calling

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

## Configuración
Copiar `.env.example` como `.env` y completar `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_API_KEY` y `LLM_MODEL` con nombre del deployment

## Ejecución
```
python -m src.build
streamlit run app.py
```

## Estructura