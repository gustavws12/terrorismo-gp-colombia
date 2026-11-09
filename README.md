# ¿Dónde es más probable el próximo atentado? Proceso gaussiano espacio-temporal sobre los actos terroristas en Colombia

Probabilidad por municipio de al menos un acto terrorista en los próximos seis meses (octubre de 2026 a marzo de 2027), estimada con un proceso gaussiano espacio-temporal de núcleo separable sobre el registro del Ministerio de Defensa, con validación fuera de muestra y calibración por deciles.

Gustavo A Romero, estadístico y científico de datos. Noviembre de 2026.

## Pregunta

Con la polémica reciente sobre los atentados, la pregunta no es cuántos actos terroristas habrá sino dónde. El ejercicio estima, para cada uno de los 1.122 municipios, la probabilidad de al menos un acto en el semestre siguiente al cierre de los datos, y la compara con la regla ingenua de ordenar por la tasa reciente.

## Datos

| Serie | Fuente | Periodo | Archivo |
|---|---|---|---|
| Actos terroristas por municipio y fecha (15.840 registros) | Ministerio de Defensa Nacional, datos abiertos (datos.gov.co) | 2003-01-01 a 2026-09-30 | `datos/terrorismo_mindefensa_2003_2026.csv` |
| Centroides de los 1.122 municipios (lon, lat, área) | Derivados del Marco Geoestadístico Nacional 2025 del DANE (`MGN_ADM_MPIO_GRAFICO.shp`, EPSG:4326) | 2025 | `datos/centroides_mpios.csv` |
| Geometría municipal simplificada para el mapa | MGN 2025 del DANE, simplificada con tolerancia 0,004 grados | 2025 | `datos/mpios_simplificado.geojson` |

El modelo usa los trimestres desde 2015T1 hasta 2026T3 (47 trimestres), con los datos del último trimestre completos a 30 de septiembre.

## Método

Sea $n_{s,t}$ el conteo de actos en el municipio $s$ y el trimestre $t$. Se modela $y_{s,t} = \log(1 + n_{s,t}) = \mu + f(s,t) + \varepsilon_{s,t}$ con $f \sim GP(0, k)$ y núcleo separable

$$k\big((s,t),(s',t')\big) = \sigma_f^2\; k_s(d_{ss'})\; k_t(|t-t'|),$$

donde $k_s$ es Matérn 3/2 sobre la distancia en kilómetros entre centroides (escala 80 km) y $k_t = w\, M_{3/2}(|t-t'|;\,1) + (1-w)\, M_{3/2}(|t-t'|;\,30)$ es una mezcla de dos Matérn 3/2 en trimestres: una escala corta de un trimestre con peso $w = 0{,}3$ para la dinámica reciente y una larga de treinta trimestres para la persistencia de los corredores. Con rejilla completa, $K = K_s \otimes K_t$ y la posterior se calcula por eigendescomposición de las dos matrices en $O(S^3 + T^3)$: las 52.734 celdas se ajustan en segundos sin aproximaciones.

Los hiperparámetros ($\ell_s$, escalas temporales, $w$, $\sigma_f^2$, $\sigma_n^2$) se eligen en una rejilla por AUC predictivo fuera de muestra con dos orígenes (ajuste a 2025T3 pronosticando 2025T4-2026T1 y ajuste a 2026T1 pronosticando 2026T2-T3); la verosimilitud marginal se reporta pero prefería menos ruido y validaba peor. El núcleo periódico anual se probó y la verosimilitud le asignó amplitud cero.

Retro-transformación: los conteos esperados usan la media lognormal $\lambda = E[e^{f}] - 1$; la probabilidad de ocurrencia usa la mediana $e^{f} - 1$, porque la media infla los municipios sin historia (allí la varianza posterior es la varianza a priori) y la mediana calibra por deciles. $P(\geq 1 \text{ en 6 meses}) = 1 - e^{-(\lambda_{T+1} + \lambda_{T+2})}$.

## Scripts

1. `scripts/gp_terrorismo.py`. Agrega los datos a municipio por trimestre, selecciona hiperparámetros, valida fuera de muestra, calibra por deciles y pronostica 2026T4-2027T1. Produce `resultados/prob_municipios_6m.csv` (ranking, probabilidad de 1 o más y de 3 o más actos, actos esperados, intensidad mediana), `serie_nacional_trimestral.csv`, `hiperparametros_rejilla.csv`, `calibracion_deciles.csv` y `gp_terrorismo_resumen.json`. Corre en unos 30 segundos.
2. `scripts/figuras_terrorismo.py`. Mapa de probabilidad, top 30 y serie nacional, en `figuras/`.

Se corren en ese orden desde la raíz del repositorio (`python scripts/gp_terrorismo.py`). Dependencias: `pip install -r requirements.txt`.

## Resultados principales

Validación: con ajuste hasta 2025T3 y pronóstico de 2025T4-2026T1, AUC 0,88 frente a 0,86 de la base que ordena por la tasa de los últimos dos años; el top 50 captura 57 % de los actos frente a 55 %. En el segundo origen el AUC es 0,90. La calibración por deciles de la probabilidad con la mediana va de 0,4 % pronosticado frente a 2 % observado en el primer decil a 81 % frente a 85 % en el décimo.

Pronóstico: 658 actos en el semestre (316 y 341 por trimestre), que corregidos por el sesgo de 10 % de la validación se ubican cerca de 720, frente a 748 en el semestre anterior. Setenta municipios superan 80 % de probabilidad, 154 superan 50 % y 528 están por debajo de 5 %. El riesgo se concentra en cuatro bloques: el Cauca (21 de los 50 primeros), el Catatumbo con Tibú a la cabeza (15 actos esperados), el piedemonte de Arauca y el bloque Guaviare-Caquetá-Huila. Cali es la única gran ciudad en el top 10; Bogotá queda en el puesto 51 con 87 %.

## Figuras

`figuras/fig1_mapa_probabilidad_6m.png` mapa de probabilidad por municipio; `fig2_top30_municipios.png` actos esperados frente a observados en los treinta primeros; `fig3_serie_nacional.png` serie trimestral observada, ajustada y pronóstico; `fig4_linkedin_mapa_top30.png` composición apaisada de mapa y top 30 (`scripts/grafica_linkedin.py`).

## Limitaciones

El registro mide lo que el Ministerio de Defensa clasifica como acto terrorista, categoría administrativa que cambia con la doctrina; el salto de 2024-2025 mezcla más violencia con más registro. La agregación municipal y el centroide borran la escala real de los hechos, y el suavizado de 80 km es grueso en la Orinoquia y la Amazonia. El modelo es lento para reconocer focos nuevos (Mercaderes, con once actos en dos trimestres, queda en 59 %) y subestima el nivel en los municipios de conteos altos, así que los actos esperados deben leerse como ranking. Un municipio con alta probabilidad es un lugar donde operan grupos armados, no una población sospechosa. El modelo no incorpora negociaciones, rupturas, elecciones ni operativos.

## Notas

`notas/01_gp_terrorismo.md` contiene la discusión completa, la predicción previa y los contrapesos.

## Licencia

MIT para el código. Los datos son del Ministerio de Defensa Nacional y del DANE y se redistribuyen tal como se descargaron de portales públicos, con las derivaciones indicadas.
