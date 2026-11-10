# High Garden Coffee reto técnico NTT Data

Solucion en dos capas sobre el dataset de consumo domestico de café (1990–2020).

- `01_notebook_eda/`: esta capa es la analítica, aqui estan calidad de datos, EDA, el pronóstico con rangos y la segmentación de mercados, el notebook también está exportado en HTML, por si se quiere ver sin instalar nada.
- `02_proyecto/`: capa funcional, pipeline de datos, agente LLM que consulta los datos, genera gráficos e insights, evaluación y app Streamlit.

Recomiendo empezar por el notebook para entender el análisis y después abrir la app, las instrucciones para correrla están en `02_proyecto/README.md`.
