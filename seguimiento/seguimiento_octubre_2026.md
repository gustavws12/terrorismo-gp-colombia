# Seguimiento del pronóstico de terrorismo: octubre de 2026

Gustavo A Romero. 23 de noviembre de 2026. Pronóstico publicado el 9 de noviembre con datos hasta septiembre; horizonte octubre de 2026 a marzo de 2027. Datos observados: Ministerio de Defensa, corte 31 de octubre de 2026 (última actualización del portal, 17 de noviembre). Es el primer mes de seis.

## Nacional

Octubre registró 117 actos. El modelo esperaba 105 para el mes (un tercio de la intensidad del cuarto trimestre) y la publicación dio 660 a 720 para el semestre, es decir 110 a 120 por mes. Va dentro del rango. Para cerrar el semestre en 658, el resto debe promediar 108 por mes.

## Por municipio

66 municipios tuvieron al menos un acto; el modelo esperaba 58. El AUC del ordenamiento publicado es 0,92, frente a 0,90 de ordenar por los actos de los últimos doce meses (en la validación de la publicación fueron 0,88 y 0,86). Los 30 primeros concentran 49 % de los actos (42 % la línea base); los 50 primeros, 61 % (63 % la base); los 100 primeros, 78 % (76 %).

| Probabilidad publicada (semestre) | Municipios | Con acto en octubre | Esperados con acto | Actos | Actos esperados |
|---|---|---|---|---|---|
| 0 a 5 % | 528 | 2 | 1,8 | 2 | 13,7 |
| 5 a 20 % | 289 | 4 | 5,2 | 4 | 12,6 |
| 20 a 50 % | 151 | 7 | 9,6 | 7 | 14,9 |
| 50 a 80 % | 84 | 19 | 13,3 | 24 | 18,5 |
| 80 a 100 % | 70 | 34 | 28,2 | 80 | 45,8 |

La probabilidad de ocurrencia está bien calibrada abajo y se queda corta arriba. El conteo esperado está mal repartido: sobra en los municipios de bajo riesgo y falta en los de alto, donde ocurrieron 80 actos contra 46 esperados. Es el sesgo conocido de la media lognormal.

## Aciertos y fallas

Aciertos: Tibú (4 actos, 2,8 esperados), Cali (5), Saravena (5), Tame (4), Patía (3), El Tarra (3), Popayán (8), Algeciras (7), Arauquita (2), Timbío (2), Teorama (1), Mercaderes (1), Bogotá (2). Tunja, que se descontó a 8 %, no registró actos.

Fallas por exceso: cinco de los ocho primeros del ranking, todos del Cauca, no registraron actos en octubre: Argelia, El Tambo, Suárez, Buenos Aires y Morales. Tampoco Calamar, Fortul, Buenaventura, San José del Guaviare, Corinto ni Florencia.

Fallas por defecto: Socha (3 %), Sogamoso (6 %) y Duitama (11 %), en Boyacá, tuvieron un acto cada uno; también La Tola, Yacuanquer y San Pablo en Nariño, y Bucaramanga (25 %).

Por departamento, el Cauca tuvo más actos de los esperados (34 contra 22) aunque sus municipios de cabeza quedaron en cero: la violencia se movió dentro del departamento, hacia Popayán, Patía, Inzá y Balboa. Arauca (14 contra 4) y Huila (14 contra 6) también quedaron por encima; Antioquia (2 contra 7) y Cundinamarca (0 contra 4), por debajo.

## Contrapesos

Un mes de seis no evalúa una probabilidad semestral: un municipio con 100 % y cero actos en octubre no es todavía un error. Octubre es preliminar; septiembre subió 14 % entre dos descargas con once días de diferencia. El AUC de un mes se apoya en 66 municipios con evento. La comparación mensual supone riesgo constante dentro del trimestre.

Archivos: `seguimiento_pronostico.py`, `figura_seguimiento.py`, `seguimiento_municipal.csv`, `seguimiento_resumen.json`, `fig4_seguimiento_octubre.png`.
