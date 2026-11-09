# -*- coding: utf-8 -*-
"""Composición apaisada para LinkedIn: mapa + top 30, 1900 x 1000 px."""
import numpy as np, pandas as pd, geopandas as gpd, matplotlib, os, json
matplotlib.use("Agg"); import matplotlib.pyplot as plt, matplotlib.patheffects as pe; from matplotlib.colors import LinearSegmentedColormap, BoundaryNorm
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); D = f"{RAIZ}/datos"; OUT = f"{RAIZ}/resultados"; FIG = f"{RAIZ}/figuras"
NARANJA, AMAR, GRISC, TXT, TXT2, SURF = "#eb6834", "#eda100", "#d9d8d4", "#0b0b0b", "#52514e", "#fcfcfb"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 12, "axes.edgecolor": GRISC, "axes.labelcolor": TXT2, "xtick.color": TXT2, "ytick.color": TXT2,
                     "axes.spines.top": False, "axes.spines.right": False, "figure.facecolor": SURF, "axes.facecolor": SURF, "axes.grid": True, "grid.color": "#e8e7e3"})
res = pd.read_csv(f"{OUT}/prob_municipios_6m.csv", dtype={"cod": str}); res["cod"] = res.cod.str.zfill(5)
g = gpd.read_file(f"{D}/mpios_simplificado.geojson"); g["cod"] = g.mpio_cdpmp.astype(str).str.zfill(5); g = g.merge(res[["cod", "prob_1_o_mas_6m", "eventos_esperados_6m"]], on="cod", how="left")
summ = json.load(open(f"{OUT}/gp_terrorismo_resumen.json"))
cmap = LinearSegmentedColormap.from_list("prob", ["#f3f2ee", "#fbd9a8", AMAR, NARANJA, "#b8321a", "#5c0f0a"]); bounds = [0, 0.05, 0.1, 0.25, 0.5, 0.8, 0.95, 1.0001]; norm = BoundaryNorm(bounds, cmap.N)
fig = plt.figure(figsize=(19.2, 8.9), dpi=100)
axm = fig.add_axes([-0.02, 0.14, 0.56, 0.71]); axm.set_axis_off(); axm.grid(False)
g.plot(column="prob_1_o_mas_6m", cmap=cmap, norm=norm, ax=axm, edgecolor="#ffffff", linewidth=0.15, missing_kwds={"color": "#eeede9"}); axm.set_xlim(-79.3, -66.6); axm.set_ylim(-4.4, 12.7)
etiq = {"54810": (6, 2), "81736": (6, 4), "76001": (-6, 6), "76364": (-6, -4), "19050": (-6, -2), "19256": (-6, 4), "95015": (6, -4), "18001": (-6, -4), "81794": (6, -4), "54001": (6, -4)}
for _, r in g[g.cod.isin(etiq)].iterrows():
    pt = r.geometry.representative_point(); dx, dy = etiq[r.cod]
    axm.annotate(r.mpio_cnmbr.title().replace("Santiago De Cali", "Cali").replace("San José De Cúcuta", "Cúcuta"), (pt.x, pt.y), xytext=(dx, dy), textcoords="offset points", fontsize=10, ha="left" if dx > 0 else "right", va="center", color=TXT, path_effects=[pe.withStroke(linewidth=2.5, foreground=SURF)])
cax = fig.add_axes([0.06, 0.125, 0.38, 0.02]); sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm); cb = fig.colorbar(sm, cax=cax, orientation="horizontal", ticks=bounds[:-1] + [1])
cb.set_ticklabels(["0", "5 %", "10 %", "25 %", "50 %", "80 %", "95 %", "100 %"]); cb.ax.tick_params(labelsize=10); cb.outline.set_visible(False); cb.set_label("Probabilidad de al menos un acto terrorista, octubre 2026 - marzo 2027", color=TXT2, fontsize=10.5, labelpad=4)
# top 30
t = res.head(30).iloc[::-1]; ax = fig.add_axes([0.62, 0.145, 0.36, 0.68])
y = np.arange(len(t)); ax.barh(y + 0.2, t.eventos_ult_12m / 2, height=0.38, color=GRISC, label="Observados: promedio semestral de los últimos 12 meses")
ax.barh(y - 0.2, t.eventos_esperados_6m, height=0.38, color=NARANJA, label="Pronóstico GP: actos esperados en el semestre")
ax.set_yticks(y); ax.set_yticklabels([f"{m.title().replace('Santiago De Cali', 'Cali').replace('San José De Cúcuta', 'Cúcuta').replace('San José Del Guaviare', 'San José del Guaviare')} ({d.title().replace(' Del ', ' del ').replace(' De ', ' de ')})" for m, d in zip(t.mpio_cnmbr, t.dpto_cnmbr)], fontsize=10)
for yi, e in enumerate(t.eventos_esperados_6m): ax.text(e + 0.2, yi - 0.2, f"{e:.1f}".replace(".", ","), va="center", fontsize=9.5, color=TXT2)
ax.set_xlabel("Actos terroristas en seis meses", fontsize=11); ax.legend(frameon=False, fontsize=10.5, loc="lower right"); ax.grid(axis="y", visible=False); ax.tick_params(axis="x", labelsize=10.5)
ax.set_title("Los 30 municipios con mayor riesgo: todos con probabilidad superior a 94 %", loc="left", fontsize=13, color=TXT, pad=12)
fig.text(0.01, 0.95, "¿Dónde es más probable el próximo atentado?", fontsize=22, color=TXT, va="center")
fig.text(0.01, 0.895, f"Probabilidad por municipio de al menos un acto terrorista entre octubre de 2026 y marzo de 2027, estimada con un proceso gaussiano espacio-temporal sobre el registro del Ministerio de Defensa.\n{summ['pronostico']['municipios_prob_mayor_80']} municipios superan 80 %, {summ['pronostico']['municipios_prob_mayor_50']} superan 50 % y 528 están por debajo de 5 %; se esperan entre 660 y 720 actos en el semestre, frente a 748 en el anterior. Cauca, Catatumbo, Arauca y Guaviare concentran el riesgo.", fontsize=12, color=TXT2, va="center")
fig.text(0.01, 0.02, "Fuente: Elaboración propia con Ministerio de Defensa (actos terroristas por municipio, datos.gov.co, 2015-2026 a 30 de septiembre) y MGN 2025 del DANE. GP separable: Matérn 3/2 espacial (80 km) y mezcla de dos escalas temporales sobre log(1 + conteo trimestral).\nValidación fuera de muestra (ajuste a 2025T3, pronóstico 2025T4-2026T1): AUC 0,88 frente a 0,86 de la tasa de los últimos dos años. Código y datos: github.com/gustavws12/terrorismo-gp-colombia", fontsize=9.5, color=TXT2)
fig.savefig(f"{FIG}/fig4_linkedin_mapa_top30.png"); print("ok")
