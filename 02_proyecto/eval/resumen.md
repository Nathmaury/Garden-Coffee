# Resultados de la evaluación del agente

|                  |   casos |   respuestas |   exactitud_pct |   casos_estables |
|:-----------------|--------:|-------------:|----------------:|-----------------:|
| analisis         |       3 |            9 |           100   |                3 |
| consulta         |       4 |           12 |           100   |                4 |
| contexto         |       2 |            6 |            66.7 |                0 |
| fuera_de_alcance |       2 |            6 |           100   |                2 |
| grafico          |       2 |            6 |           100   |                2 |
| mercados         |       2 |            6 |           100   |                2 |
| pronostico       |       3 |            9 |           100   |                3 |
| TOTAL            |      18 |           54 |            96.3 |               16 |

Rondas: 3 | Pasos promedio: 2.2 | Tokens promedio: 3,683 | Tiempo promedio: 2.6 s

Fallas:

|   ronda | id   | detalle                                         |
|--------:|:-----|:------------------------------------------------|
|       1 | X02  | no menciona 'tamaño'; no menciona 'crecimiento' |
|       2 | X01  | no menciona '60'                                |
