# -*- coding: utf-8 -*-
"""Figuras del GP espacio-temporal de terrorismo: mapa de probabilidad a 6 meses, top-30 y serie nacional."""
import numpy as np, pandas as pd, geopandas as gpd, matplotlib, os, json
matplotlib.use("Agg"); import matplotlib.pyplot as plt, matplotlib.patheffects as pe; from matplotlib.colors import LinearSegmentedColormap, BoundaryNorm
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); D = f"{RAIZ}/datos"; OUT = f"{RAIZ}/resultados"; FIG = f"{RAIZ}/figuras"
AZUL, NARANJA, AQUA, AMAR, GRIS, GRISC, TXT, TXT2, SURF = "#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#9a9893", "#d9d8d4", "#0b0b0b", "#52514e", "#fcfcfb"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11, "axes.edgecolor": GRISC, "axes.labelcolor": TXT2, "xtick.color": TXT2, "ytick.color": TXT2,
                     "axes.spines.top": False, "axes.spines.right": False, "figure.facecolor": SURF, "axes.facecolor": SURF, "axes.grid": True, "grid.color": "#e8e7e3"})
res = pd.read_csv(f"{OUT}/prob_municipios_6m.csv", dtype={"cod": str}); res["cod"] = res.cod.str.zfill(5)
g = gpd.read_file(f"{D}/mpios_simplificado.geojson"); g["cod"] = g.mpio_cdpmp.astype(str).str.zfill(5); g = g.merge(res[["cod", "prob_1_o_mas_6m", "eventos_esperados_6m", "eventos_ult_12m"]], on="cod", how="left")
summ = json.load(open(f"{OUT}/gp_terrorismo_resumen.json")); nac = pd.read_csv(f"{OUT}/serie_nacional_trimestral.csv")
FUENTE = "Fuente: Elaboración propia con Ministerio de Defensa (actos terroristas por municipio, datos.gov.co, 2015-2026 a 30 de septiembre) y MGN 2025 del DANE. Proceso gaussiano espacio-temporal separable (Matérn 3/2 espacial, 80 km; mezcla de dos escalas temporales) sobre log(1 + conteo trimestral)."

# ---------- Figura 1: mapa de probabilidad de al menos un acto terrorista en 2026T4-2027T1 ----------
cmap = LinearSegmentedColormap.from_list("prob", ["#f3f2ee", "#fbd9a8", AMAR, NARANJA, "#b8321a", "#5c0f0a"])
bounds = [0, 0.05, 0.1, 0.25, 0.5, 0.8, 0.95, 1.0001]; norm = BoundaryNorm(bounds, cmap.N)
fig, ax = plt.subplots(figsize=(10.8, 12.2), dpi=150); fig.subplots_adjust(left=0.01, right=0.99, top=0.915, bottom=0.075); ax.set_axis_off(); ax.grid(False)
g.plot(column="prob_1_o_mas_6m", cmap=cmap, norm=norm, ax=ax, edgecolor="#ffffff", linewidth=0.15, missing_kwds={"color": "#eeede9"})
ax.set_xlim(-79.3, -66.6); ax.set_ylim(-4.4, 12.7)
etiq = {"54810": (6, 2), "81736": (6, 4), "76001": (-6, 6), "76364": (-6, -4), "19050": (-6, -2), "19256": (-6, 4), "95015": (6, -4), "18001": (-6, -4), "81794": (6, -4), "76109": (-6, 0), "54001": (6, -4)}
for _, r in g[g.cod.isin(etiq)].iterrows():
    pt = r.geometry.representative_point(); dx, dy = etiq[r.cod]
    ax.annotate(r.mpio_cnmbr.title().replace("Santiago De Cali", "Cali").replace("San José De Cúcuta", "Cúcuta"), (pt.x, pt.y), xytext=(dx, dy), textcoords="offset points", fontsize=8, ha="left" if dx > 0 else "right", va="center", color=TXT, path_effects=[pe.withStroke(linewidth=2.5, foreground=SURF)])
sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm); cb = fig.colorbar(sm, ax=ax, orientation="horizontal", fraction=0.03, pad=0.01, aspect=40, ticks=bounds[:-1] + [1])
cb.set_ticklabels(["0", "5 %", "10 %", "25 %", "50 %", "80 %", "95 %", "100 %"]); cb.ax.tick_params(labelsize=9); cb.outline.set_visible(False)
cb.set_label("Probabilidad de al menos un acto terrorista entre octubre de 2026 y marzo de 2027", color=TXT2, fontsize=9.5)
fig.suptitle("¿Dónde es más probable el próximo atentado?", x=0.02, y=0.975, ha="left", fontsize=15, color=TXT)
fig.text(0.02, 0.945, f"Probabilidad por municipio de al menos un acto terrorista entre octubre de 2026 y marzo de 2027. {summ['pronostico']['municipios_prob_mayor_80']} municipios superan 80 % y\n{summ['pronostico']['municipios_prob_mayor_50']} superan 50 %; se esperan {summ['pronostico']['eventos_esperados_nacional_6m']:.0f} actos en el país frente a 748 en los seis meses anteriores. Cauca, Catatumbo, Arauca y Guaviare\nconcentran el riesgo.", fontsize=10.5, color=TXT2, va="top")
fig.text(0.02, 0.012, FUENTE + f"\nValidación fuera de muestra (ajuste a 2025T3, pronóstico 2025T4-2026T1): AUC {summ['validacion']['auc_gp']:.2f} frente a {summ['validacion']['auc_base']:.2f} de la tasa de los últimos dos años.".replace(".", ","), fontsize=7.5, color=TXT2, wrap=True)
fig.savefig(f"{FIG}/fig1_mapa_probabilidad_6m.png"); plt.close(fig)

# ---------- Figura 2: top 30 municipios, eventos esperados y observados ----------
t = res.head(30).iloc[::-1]
fig, ax = plt.subplots(figsize=(12.96, 9.2), dpi=150); fig.subplots_adjust(left=0.27, right=0.97, top=0.86, bottom=0.11)
y = np.arange(len(t)); ax.barh(y + 0.2, t.eventos_ult_12m / 2, height=0.38, color=GRISC, label="Observados: promedio semestral de los últimos 12 meses")
ax.barh(y - 0.2, t.eventos_esperados_6m, height=0.38, color=NARANJA, label="Pronóstico GP: actos esperados octubre 2026 - marzo 2027")
ax.set_yticks(y); ax.set_yticklabels([f"{m.title()} ({d.title()})" for m, d in zip(t.mpio_cnmbr, t.dpto_cnmbr)], fontsize=9)
for yi, (e, p) in enumerate(zip(t.eventos_esperados_6m, t.prob_1_o_mas_6m)): ax.text(e + 0.2, yi - 0.2, f"{e:.1f}".replace(".", ","), va="center", fontsize=8, color=TXT2)
ax.set_xlabel("Actos terroristas en seis meses"); ax.legend(frameon=False, fontsize=9.5, loc="lower right"); ax.grid(axis="y", visible=False)
fig.suptitle("Los 30 municipios con mayor riesgo: el modelo pronostica persistencia, no explosión", x=0.01, y=0.975, ha="left", fontsize=14, color=TXT)
ax.set_title("Todos tienen probabilidad superior a 94 % de al menos un acto en el semestre. Tibú encabeza con 15 actos esperados; el modelo revierte hacia la media\nen Suárez, Patía e Inzá y sube a Argelia, Morales y Piendamó. En los municipios de conteos altos el GP sobre log(1 + n) subestima el nivel: léase como ranking.", loc="left", fontsize=10, color=TXT2, pad=10)
fig.text(0.01, 0.012, FUENTE, fontsize=7.5, color=TXT2, wrap=True)
fig.savefig(f"{FIG}/fig2_top30_municipios.png"); plt.close(fig)

# ---------- Figura 3: serie nacional trimestral observada, ajustada y pronóstico ----------
nac["q"] = pd.PeriodIndex(nac.trimestre, freq="Q"); x = nac.q.dt.to_timestamp()
lam = summ["pronostico"]; lam_q = [sum(r["lambda_T4_2026"] for _, r in res.iterrows()), sum(r["lambda_T1_2027"] for _, r in res.iterrows())]
xf = pd.PeriodIndex(["2026Q4", "2027Q1"], freq="Q").to_timestamp()
fig, ax = plt.subplots(figsize=(12.96, 5.6), dpi=150); fig.subplots_adjust(left=0.06, right=0.98, top=0.82, bottom=0.2)
ax.bar(x, nac.observado, width=70, color=GRISC, label="Actos terroristas observados por trimestre")
ax.plot(x, nac.ajustado, color=AZUL, lw=2.2, label="Ajuste del GP (suma de intensidades municipales)")
ax.plot(xf, lam_q, color=NARANJA, lw=2.4, marker="o", ms=6, label="Pronóstico 2026T4-2027T1")
for xi, v in zip(xf, lam_q): ax.annotate(f"{v:.0f}", (xi, v), xytext=(0, 8), textcoords="offset points", ha="center", fontsize=9.5, color=NARANJA)
ax.annotate(f"{nac.observado.iloc[-1]:.0f} en 2026T3", (x.iloc[-1], nac.observado.iloc[-1]), xytext=(-60, 12), textcoords="offset points", fontsize=9, color=TXT2)
ax.set_ylabel("Actos por trimestre"); ax.legend(frameon=False, fontsize=9.5, loc="upper left"); ax.set_ylim(0, None)
fig.suptitle("El terrorismo se cuadruplicó desde 2021 y el modelo espera que se mantenga cerca del máximo", x=0.01, y=0.985, ha="left", fontsize=13.5, color=TXT)
ax.set_title(f"Actos terroristas trimestrales en Colombia, 2015-2026, y pronóstico del GP: {lam_q[0]:.0f} en 2026T4 y {lam_q[1]:.0f} en 2027T1 ({lam['eventos_esperados_nacional_6m']:.0f} en el semestre, 748 en el anterior).", loc="left", fontsize=11, color=TXT2, pad=10)
fig.text(0.01, 0.012, FUENTE + " El ajuste suma E[exp(f)] − 1 sobre municipios y queda 25 % por debajo del total observado (sesgo de la transformación log(1 + n) en los municipios de conteos altos); en la validación fuera de muestra el pronóstico quedó 10 % por debajo de lo observado (626 frente a 692). Corregido por ese sesgo, el semestre pronosticado se ubica alrededor de 720 actos, en el nivel de los últimos doce meses.", fontsize=7.5, color=TXT2, wrap=True)
fig.savefig(f"{FIG}/fig3_serie_nacional.png"); plt.close(fig); print("ok", lam_q)
