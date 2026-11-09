# ¿Dónde es más probable el próximo atentado? Proceso gaussiano espacio-temporal sobre los actos terroristas por municipio

Gustavo A Romero. 9 de noviembre de 2026.

## Pregunta

Con las noticias de las últimas semanas sobre atentados y la polémica que desataron, la pregunta no es cuántos actos terroristas habrá en Colombia sino dónde. Este ejercicio estima, para cada uno de los 1.122 municipios, la probabilidad de que ocurra al menos un acto terrorista entre octubre de 2026 y marzo de 2027, usando un proceso gaussiano espacio-temporal sobre el registro del Ministerio de Defensa.

## Predicción previa

Antes de correr el modelo escribí que el Catatumbo (Tibú, Cúcuta, Teorama), el norte del Cauca (Jamundí, Corinto, Toribío, Cajibío), Arauca (Saravena, Arauquita) y el Bajo Cauca antioqueño concentrarían el top 20, y que Bogotá y Cali entrarían por volumen. Acertó en tres de las cuatro regiones y en Cali; falló en el Bajo Cauca, que el modelo deja entre 40 % y 60 % (Tarazá 58 %, Cáceres 41 %, El Bagre 46 %), y subestimó el sur del Cauca (Argelia, El Tambo, Patía, Balboa) y la zona Guaviare-Caquetá (Calamar, San José del Guaviare, Florencia), que sí entran al top 25. Bogotá queda en el puesto 51 con 87 %.

## Datos

Actos terroristas por municipio y fecha del Ministerio de Defensa, conjunto abierto en datos.gov.co, 15.840 registros desde enero de 2003 hasta el 30 de septiembre de 2026, agregados a 1.122 municipios por 47 trimestres desde 2015. Geometría del Marco Geoestadístico Nacional 2025 del DANE (shapefile de municipios en EPSG:4326), del que se tomaron los centroides para la distancia y una versión simplificada para el mapa. El registro pasó de 635 actos en 2021 a 742 en 2022, 839 en 2023, 1.126 en 2024, 1.398 en 2025 y 1.119 en los primeros nueve meses de 2026; desde 2024 Cauca acumula 1.028, Norte de Santander 381, Valle 371, Antioquia 228, Chocó 226, Arauca 203 y Huila 192.

## Método

Sea $n_{s,t}$ el conteo de actos en el municipio $s$ y el trimestre $t$. Se modela $y_{s,t} = \log(1 + n_{s,t}) = \mu + f(s,t) + \varepsilon_{s,t}$ con $f \sim GP(0, k)$ y núcleo separable $k = \sigma_f^2\, k_s(d_{ss'})\, k_t(|t - t'|)$: $k_s$ es Matérn 3/2 sobre la distancia en kilómetros entre centroides con escala de 80 km, y $k_t$ es una mezcla de dos Matérn 3/2 en trimestres, una corta de 1 trimestre con peso 0,3 que recoge la dinámica reciente y una larga de 30 trimestres con peso 0,7 que recoge la persistencia de los corredores. Con rejilla completa, $K = K_s \otimes K_t$ y la posterior se obtiene por eigendescomposición de las dos matrices en $O(S^3 + T^3)$, lo que permite ajustar 1.122 × 47 celdas en segundos sin aproximaciones. La varianza de ruido quedó en 0,15 y la de señal en 0,5.

Los hiperparámetros se escogieron en una rejilla por AUC predictivo fuera de muestra con dos orígenes, ajuste hasta 2025T3 pronosticando 2025T4-2026T1 y ajuste hasta 2026T1 pronosticando 2026T2-T3. La verosimilitud marginal prefería menos ruido (0,05) y una escala corta de 2 trimestres, pero validaba peor (AUC 0,86 frente a 0,89); en una tabla de conteos con 80 % de ceros la verosimilitud gaussiana sobre log(1 + n) no es el objetivo, y se prefirió el criterio predictivo. El núcleo periódico anual se probó y la verosimilitud le asignó amplitud cero: el terrorismo no tiene estacionalidad trimestral detectable.

La retro-transformación es el punto delicado. Para los conteos esperados se usa la media lognormal $\lambda = E[e^{f}] - 1$, que en validación queda 10 % por debajo de lo observado. Para la probabilidad de ocurrencia esa media está mal calibrada: en municipios sin historia la varianza posterior es la varianza a priori y la corrección $e^{V/2}$ les asigna 15 % de probabilidad cuando la frecuencia observada es 2 %. La mediana $e^{f} - 1$, en cambio, calibra por deciles (decil 1: 0,4 % pronosticado frente a 2 % observado; decil 6: 7,6 % frente a 8 %; decil 8: 25 % frente a 22 %; decil 10: 81 % frente a 85 %), y es la que se usa en $P(\geq 1) = 1 - e^{-\lambda_{med}}$ sobre la suma de los dos trimestres. La tabla completa está en `calibracion_deciles.csv`.

## Validación

Con ajuste hasta 2025T3 y pronóstico de 2025T4-2026T1, el GP obtiene AUC 0,88 frente a 0,86 de la base ingenua que ordena por la tasa de los últimos dos años, y los 50 municipios con mayor probabilidad capturan 57 % de los actos del semestre frente a 55 % de la base. En el segundo origen el AUC es 0,90. La mejora sobre la base es modesta porque el terrorismo en Colombia es extraordinariamente persistente: saber dónde ocurrió el año pasado ya explica casi todo, y lo que el GP añade es el suavizado espacial, que recoge los municipios vecinos a un foco, y la ponderación de la dinámica reciente.

## Resultados

En el país se esperan 658 actos entre octubre de 2026 y marzo de 2027 según el modelo, 316 en el cuarto trimestre y 341 en el primero de 2027, frente a 748 en los seis meses anteriores. Corregido por el sesgo de 10 % que mostró la validación, el pronóstico se ubica cerca de 720: el semestre se mantiene en el nivel máximo de la serie, sin señal de descenso ni de nueva aceleración.

Setenta municipios superan 80 % de probabilidad de al menos un acto, 154 superan 50 %, 28 superan 95 %, y en 34 la probabilidad de tres o más actos supera 50 %. En el otro extremo, 528 municipios están por debajo de 5 % y 689 por debajo de 10 %. La mediana nacional es 5,6 %.

Los treinta primeros son Tibú con 15 actos esperados en el semestre, Argelia 11, El Tambo 9, Jamundí 8, Suárez 7, Buenos Aires 7, Cajibío 7, Morales 6, Cali 5,5, Saravena 5,5, Tame 5,5, Patía 5, Santander de Quilichao 5, Cúcuta 5, Calamar 5, El Tarra 5, Popayán 5, Arauquita 4,5, Fortul 4,5, Buenaventura 4,5, San José del Guaviare 4, Corinto 4, Inzá 4, Florencia 4, Balboa 4, Toribío 4, Piendamó 4, Timbío 3,5, Caloto 3,5 y Algeciras 3,5; todos con probabilidad superior a 94 %. De los cincuenta primeros, 21 son del Cauca, 7 de Norte de Santander, 5 de Arauca, 3 del Valle, 3 de Guaviare y 3 de Huila. Por departamento, el Cauca concentra 132 de los 658 actos esperados, Norte de Santander 62, Antioquia 48, Valle 38, Huila 35, Nariño 30 y Chocó 29.

El mapa muestra cuatro bloques oscuros: el Cauca entero desde Jamundí y Buenaventura hasta Argelia y Patía, el Catatumbo con Tibú al centro y Cúcuta, El Tarra, Teorama, Convención, El Carmen y Ocaña alrededor, el piedemonte de Arauca con Saravena, Tame, Fortul y Arauquita, y el bloque Guaviare-Caquetá-Huila con Calamar, San José del Guaviare, Florencia y Algeciras. Entre ellos hay un corredor de 25 % a 50 % que baja por Huila y Tolima y otro que une el Catatumbo con el sur de Bolívar y el Bajo Cauca. Las grandes ciudades distintas de Cali quedan en la franja media: Bogotá 87 %, Pasto 62 %, Villavicencio 54 %, Medellín 35 %, Cartagena 34 %, Bucaramanga 25 % y Barranquilla 24 %.

Donde el modelo discrepa de la simple persistencia es lo que vale la pena mirar. Sube a municipios con pocos actos propios pero rodeados de focos: Piendamó, Timbío y Morales en el Cauca, Teorama y Convención en el Catatumbo, Istmina y Pradera sin ningún acto en el último año pero con 66 %. Y descuenta los brotes puntuales: Tunja tuvo seis actos en un solo trimestre de 2025 y queda en 8 %, porque la escala corta del núcleo decae a la mitad en un trimestre.

## Contrapesos

El registro mide lo que el Ministerio de Defensa clasifica y reporta como acto terrorista, una categoría administrativa que cambia con la doctrina y con la presión de los medios; el salto de 2024 y 2025 mezcla más violencia con más registro, y el modelo no puede separarlos. La agregación municipal borra la escala en que los atentados realmente ocurren, el casco urbano de Jamundí o la vía Tibú-Cúcuta, y el centroide de un municipio del Guaviare puede estar a cien kilómetros de donde pasan las cosas; el suavizado de 80 km funciona en el Cauca y es grueso en la Orinoquia.

El modelo es lento para reconocer focos nuevos: Mercaderes, con once actos en los dos últimos trimestres y casi ninguno antes, queda en 59 %, porque la escala larga pesa 0,7 y tira hacia su historia de ceros. Para vigilancia operativa conviene leer el GP junto con la tasa reciente, no en su lugar. En el otro sentido, el GP sobre log(1 + n) subestima el nivel en los municipios de conteos altos (el ajuste en muestra suma 25 % menos que lo observado), así que los actos esperados de Tibú o Argelia deben leerse como ranking y no como cifra.

Las probabilidades altas son casi tautológicas: decir que Tibú tiene 100 % de probabilidad de un acto terrorista en seis meses es decir que el Catatumbo sigue en guerra. La información útil está en la franja de 25 % a 80 %, donde el modelo discrimina y donde la calibración muestra que acierta. Y la precaución de siempre con este tipo de mapas: un municipio con 90 % de probabilidad es un lugar donde hay grupos armados operando, no una población sospechosa, y el uso del ranking para estigmatizar territorios sería leerlo al revés.

Lo que no está en el modelo y podría moverlo: la negociación o ruptura con cada grupo armado, las elecciones de 2026 que ya pasaron y las de 2027 que vienen, y los operativos de la fuerza pública que desplazan los focos. Un GP aprende persistencia y vecindad; no aprende decisiones.

## Archivos

`gp_terrorismo.py` ajusta el modelo y produce `prob_municipios_6m.csv` (ranking, probabilidad de 1 o más y de 3 o más actos, actos esperados, intensidad mediana, desviación del log), `serie_nacional_trimestral.csv`, `hiperparametros_rejilla.csv`, `calibracion_deciles.csv` y `gp_terrorismo_resumen.json`. `figuras_terrorismo.py` produce `fig1_mapa_probabilidad_6m.png`, `fig2_top30_municipios.png` y `fig3_serie_nacional.png`. Los datos están en `datos/`: `terrorismo_mindefensa_2003_2026.csv`, `centroides_mpios.csv` y `mpios_simplificado.geojson`, derivados del shapefile `MGN_ADM_MPIO_GRAFICO.shp` de la carpeta de seguridad social. Dependencias: numpy, pandas, scikit-learn, geopandas, matplotlib.
