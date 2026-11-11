# Resultados de la evaluación del agente

|                  |   casos |   respuestas |   exactitud_pct |   casos_estables |
|:-----------------|--------:|-------------:|----------------:|-----------------:|
| analisis         |       3 |            9 |           100   |                3 |
| consulta         |       4 |           12 |           100   |                4 |
| contexto         |       2 |            6 |           100   |                2 |
| fuera_de_alcance |       2 |            6 |           100   |                2 |
| grafico          |       2 |            6 |           100   |                2 |
| mercados         |       2 |            6 |           100   |                2 |
| pronostico       |       4 |           12 |            91.7 |                3 |
| TOTAL            |      19 |           57 |            98.2 |               18 |

Rondas: 3 | Pasos promedio: 2.2 | Tokens promedio: 4,420 | Tiempo promedio: 2.7 s

Fallas:

|   ronda | id   | detalle                                        |
|--------:|:-----|:-----------------------------------------------|
|       2 | P02  | no aparece el valor esperado [2989.1, 3421.11] |
