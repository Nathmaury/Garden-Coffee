# High Garden Coffee agente analítico

Esta es la parte funcional de mi solución al reto, la idea es que cualquier persona de Garden Coffee pueda hacerle preguntas a los datos sin saber programar.

El proyecto toma el dataset de consumo de café, arma una base de datos con todo lo que salió del análisis (pronósticos, segmentos de mercado y un score de oportunidad) y encima de eso tiene un agente con LLM. Le preguntas algo, el agente consulta los datos, te responde con cifras reales y, si hace falta te arma un gráfico, todo se usa desde una app en Streamlit.

El análisis completo con el EDA y por qué tomé cada decisión está en `../01_notebook_eda/`.

## Cómo está armado

```text
coffee_db.parquet
      │
      ▼
src/etl.py ─────────► limpieza, formato largo, banderas de calidad y regiones
      │
      ▼
src/models.py ──────► comparación de modelos, pronóstico 2020-2024 con rangos,
      │               segmentación y score de oportunidad
      ▼
coffee.duckdb ──────► base con 5 tablas: consumo, paises, pronosticos,
      │               evaluacion_modelos y mercados
      ▼
src/agent/ ─────────► agente con Azure OpenAI y tres herramientas:
      │                 consultar_datos  → hace consultas SQL
      │                 crear_grafico    → hace la consulta y arma el gráfico
      │                 buscar_contexto  → busca en la documentación del análisis
      ▼
app.py ─────────────► la app: chat con el agente, panorama, pronósticos y mercados
```

Algunas cosas que tuve en cuenta al diseñar el agente:

- No calcula nada de memoria porque toda cifra sale de una consulta a la base y si una consulta falla, lee el error y la corrige solo.
- No puede modificar los datos. La base se abre en solo lectura y además cualquier SQL que no sea un SELECT se bloquea.
- Si le preguntan algo que los datos no tienen, como precios o un país que no está, lo dice en lugar de inventar.
- Puede explicar el análisis (la metodología, los supuestos, las limitaciones) porque busca en un documento con todo eso. Para la búsqueda usé TF-IDF, así no tuve que desplegar otro modelo en Azure.
- La conexión con el LLM está en un solo archivo, `src/agent/llm.py`. Si se quiere cambiar de modelo o de proveedor, solo se toca ese.

## Qué se necesita

- Python 3.11 o superior 
- Un deployment de Azure OpenAI con soporte de function calling. Yo usé `gpt-5.4-mini`.

## Instalación

Todo se corre desde esta carpeta, `02_proyecto`.

En Windows (PowerShell):
```
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

En Mac o Linux:
```
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Después hay que copiar `.env.example` como `.env` y llenar los datos de Azure:

```
AZURE_OPENAI_ENDPOINT=https://tu-recurso.openai.azure.com/
AZURE_OPENAI_API_KEY=tu-key
LLM_MODEL=nombre-de-tu-deployment
```

## Cómo correrlo

Primero se construye la base de datos, tarda uno o dos minutos porque entrena y compara los modelos:
```
python -m src.build
```

Y después se abre la app:
```
streamlit run app.py
```
la app construye la base sola la primera vez.

Si quieres probar el agente sin la app, también se puede desde la terminal:
```
python -m src.agent.cli
```

## Cómo evalué el agente

No quería quedarme con la buena respuesta que dio entonces que armé 18 preguntas de prueba en 7 categorías (están en `eval/golden_set.json`)

Para las preguntas con números, el script calcula la respuesta correcta por su cuenta con SQL, sin pasar por el agente, y revisa que ese número aparezca en lo que respondió (con un 3 % de margen por redondeos). En las otras revisa que mencione lo que debe, que haga el gráfico o que reconozca cuando los datos no alcanzan.

Como un LLM no responde igual todas las veces, corrí todo 3 veces:

```
python -m eval.run_eval 3
```

| Categoría | Preguntas | Respuestas | Aciertos | Bien en las 3 rondas |
|---|---|---|---|---|
| Análisis | 3 | 9 | 100 % | 3 |
| Consultas | 4 | 12 | 100 % | 4 |
| Contexto | 2 | 6 | 100 % | 2 |
| Fuera de alcance | 2 | 6 | 100 % | 2 |
| Gráficos | 2 | 6 | 100 % | 2 |
| Mercados | 2 | 6 | 100 % | 2 |
| Pronósticos | 4 | 12 | 91,7 % | 3 |
| **Total** | **19** | **57** | **98,2 %** | **18** |

En promedio cada respuesta toma 2,7 segundos y unos 4.400 tokens. El detalle de cada respuesta queda en `eval/resultados.csv`.

Lo más útil de evaluar fue todo lo que encontré en el camino:

- Al principio el agente calculaba mal el crecimiento anual porqu usaba 30 años entre 1990 y 2019 cuando son 29, le agregué una regla con un ejemplo al prompt y desde ahí acertó siempre.
- Cuando le preguntaba por Estados Unidos respondía bien, pero daba muchas vueltas buscándolo (hasta 7 pasos). Le agregué una regla para que lo revise con una sola consulta.
- En esa misma pregunta hubo un fallo que en realidad era del evaluador. El agente dijo "no tengo datos" y el script no reconocía esa frase, así que amplié la lista.
- Al sumar los rangos de precios, el agente confundía la tabla de pronóstico de consumo con la de precios, porque se llaman parecido, y respondía en kilos. Lo resolví dejando explícito en el prompt cuál es cuál, y agregué una pregunta de prueba que lo mide.
- Solo quedó una falla en 57 respuestas, en una pregunta de pronóstico que acertó en las otras dos rondas.

## Qué hay en cada carpeta

```
02_proyecto/
├── app.py                 la app de Streamlit
├── requirements.txt
├── .env.example
├── .streamlit/config.toml colores y estilo de la app
├── data/
│   ├── raw/               el dataset original, no se modifica
│   └── processed/         la base que genera el build
├── eval/
│   ├── golden_set.json    las preguntas de prueba
│   ├── run_eval.py        el script de evaluación
│   ├── resultados.csv     cada respuesta del agente
│   └── resumen.md         el resumen de resultados
└── src/
    ├── config.py          rutas y variables de entorno
    ├── etl.py             carga y limpieza de datos
    ├── regions.py         a qué región pertenece cada país
    ├── models.py          pronóstico, segmentación y score
    ├── build.py           corre todo el proceso de datos
    ├── agent/
    │   ├── llm.py         conexión con Azure OpenAI
    │   ├── tools.py       las herramientas del agente
    │   ├── prompts.py     las instrucciones del agente
    │   ├── contexto.md    la documentación que consulta
    │   ├── loop.py        el ciclo de pregunta y respuesta
    │   └── cli.py         el chat en la terminal
    └── ui/estilo.py       paleta y tipografía
```

## Cosas a tener en cuenta

- El enunciado habla de tazas, pero los datos están en kilogramos. Todos los valores son múltiplos de 60 y coinciden con los sacos de 60 kg que reporta la ICO.
- El dataset no tiene precios, así que investigué por aparte el precio internacional de cada año (FMI y Organización Internacional del Café) y calculé rangos de precio futuro con su propia historia. Son rangos amplios, porque el precio se comporta como una caminata aleatoria. Las fuentes están en `data/external/FUENTES.md`.
- Los datos son solo de países productores y llegan hasta 2019. No están los grandes importadores ni lo que pasó después como la pandemia.
- Algunos países tienen cifras que parecen estimadas, los deje fuera del pronóstico y quedan marcados en la base.
- El tipo de café es el que predomina en cada país, no cuánto se consume de cada uno
