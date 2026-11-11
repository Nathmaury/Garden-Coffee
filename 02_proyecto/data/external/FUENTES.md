# Fuente de los precios

Investigación complementariaporque el dataset original no trae precios.

- Precios mensuales de Arábica (Other Mild Arabicas) y Robusta en centavos de dólar por libra, del Fondo Monetario Internacional (Primary Commodity Prices) y la Organización Internacional del Café, compilados en el dataset `coffee_price` del paquete de R `stevedata`.
- Calculé el promedio de cada año de 1990 a 2019 y lo convertí a dólares por kilo (1 libra = 0,453592 kg).
- Validación: comparé 1992 a 2019 con las series anuales del FMI publicadas en FRED (PCOFFOTMUSDA y PCOFFROBUSDA). Diferencia promedio de 1,4 % en Arábica y 3,7 % en Robusta.
- Precios reales de 2020 a 2024 para validar los rangos: series anuales del FMI publicadas en FRED (PCOFFOTMUSDA y PCOFFROBUSDA).