## Dataset y unidades
El dataset contiene el consumo doméstico anual de café de 55 países productores entre los años cafeteros 1990/91 y 2019/20. Aunque el enunciado menciona tazas, todos los valores son múltiplos exactos de 60 y Brasil registra 1.320 millones en 2019/20, equivalentes a 22 millones de sacos de 60 kg, cifra consistente con la Organización Internacional del Café. Por eso los datos se interpretan en kilogramos. Convertir a tazas requiere asumir gramos por taza.

## Tipo de café
Cada país tiene una sola fila y una sola etiqueta de tipo de café (Arabica, Robusta, Arabica/Robusta o Robusta/Arabica). La etiqueta indica el tipo predominante del país y no un desglose del consumo. No es posible saber cuánto Arábica o Robusta consume cada país, solo comparar grupos de países según su tipo predominante.

## Calidad de datos
No hay nulos, duplicados ni valores negativos, y el total de cada país coincide con la suma de sus años. Nepal y Guinea Ecuatorial reportan cero en todos los años y se tratan como no reportados. Timor-Leste, Yemen, Laos, Zambia y Guyana tienen ceros parciales. Once países tienen series casi constantes (tres o menos valores distintos en 30 años), lo que sugiere estimaciones repetidas. Hay saltos anuales mayores al 30 por ciento en países como Madagascar, Honduras y Costa Rica, que parecen revisiones estadísticas más que cambios reales de demanda.

## Metodología del forecast
Se pronostica 2020 a 2024 para 40 países con series confiables y para el total. Se excluyeron países sin reporte, con ceros o con series planas. Con solo 30 datos anuales por país se usaron modelos estadísticos clásicos en lugar de deep learning. Se compararon dos baselines (Naive y RWD, tendencia promedio) contra AutoETS, AutoARIMA y AutoTheta mediante validación cruzada temporal con tres cortes (2012, 2013 y 2014) pronosticando cinco años en cada uno.

## Resultados del backtest y elección del modelo
AutoETS tuvo el menor error promedio (sMAPE cercano a 5,5 por ciento) y rangos bien calibrados: el rango del 80 por ciento contuvo cerca del 89 por ciento de los valores reales y el de 95 por ciento cerca del 93 por ciento. Naive ganó en muchos países individuales porque varias series avanzan por escalones, típico de cifras estimadas. En la serie total, los modelos con tendencia (RWD y AutoTheta) fueron mejores. Se eligió AutoETS para todas las series por su precisión promedio, sus rangos confiables y porque decide automáticamente si incluir tendencia. Elegir un modelo distinto por país con tan pocas ventanas de validación arriesgaba sobreajuste.

## Rangos y precios
Los rangos de los pronósticos son de demanda (consumo), no de precio. El dataset no contiene precios, así que no es posible estimar rangos de precios futuros con rigor. Para hacerlo habría que integrar series externas de precios internacionales, por ejemplo el indicador compuesto de la ICO o los precios de Arábica y Robusta del Banco Mundial, y cruzarlas con la demanda.

## Segmentación de mercados
Se segmentaron los 40 países con K-Means usando cuatro variables: tamaño (logaritmo del consumo 2019), crecimiento reciente 2010-2019, logaritmo de la volatilidad y crecimiento esperado 2019-2024. Antes de agrupar se recortaron los valores extremos (percentiles 5 y 95) y se estandarizaron las variables. El silhouette fue moderado (entre 0,3 y 0,4 para k de 2 a 6), lo que indica un continuo más que grupos totalmente separados. Se eligió k = 4 por ser comparable en silhouette y más accionable. Los segmentos son Motores de crecimiento (grandes, crecimiento sostenido y estables), Maduros estancados (volumen relevante sin crecimiento), Emergentes volátiles (crecen rápido pero con mucha inestabilidad) y Marginales (volumen mínimo y alta incertidumbre).

## Score de oportunidad
El score va de 0 a 100 y combina cuatro componentes convertidos a percentiles: tamaño (35 por ciento), crecimiento esperado 2019-2024 (35 por ciento), estabilidad o baja volatilidad (15 por ciento) y certidumbre del pronóstico o rango estrecho (15 por ciento). Se usan percentiles para que Brasil no aplaste al resto por su volumen. Los pesos son una decisión de negocio; se verificó la sensibilidad con escenarios que priorizan crecimiento o volumen, y los países que se mantienen en el top 10 en los tres escenarios son las recomendaciones más robustas.

## Hallazgos principales
El consumo se multiplicó por 2,6 entre 1990 y 2019 (3,3 por ciento anual), pero el crecimiento bajó de 4,4 por ciento anual en los 2000 a 2,0 por ciento en los 2010, y 2019 fue el único año con caída. Brasil representa el 44 por ciento del consumo y explica el 45 por ciento del crecimiento. Asia y Oceanía pasó del 17 al 28 por ciento del consumo, impulsada por Indonesia, Filipinas, Vietnam y Tailandia. Centroamérica y el Caribe es la región más estancada. Los países de predominio Robusta/Arabica son los que más crecen.

## Recomendaciones de negocio
Asegurar volumen en Brasil, el mercado más grande y estable. Priorizar crecimiento en Indonesia, Filipinas y Etiopía, que combinan crecimiento con estabilidad. Entrar de forma gradual en Vietnam por su alto potencial con alta incertidumbre. Evaluar una oferta de Robusta o mezclas, porque los mercados que más crecen tienen fuerte presencia de Robusta. Mantener sin sobreinvertir en México, Centroamérica y Venezuela.

## Limitaciones
Los datos terminan en 2019 y no reflejan efectos posteriores como la pandemia. Miden consumo en países productores, no en grandes importadores como Estados Unidos, Europa o Japón. No hay precios. Parte de las series son estimaciones, lo que limita la precisión del pronóstico por país.