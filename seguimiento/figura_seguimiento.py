# -*- coding: utf-8 -*-
"""Figura del seguimiento de octubre de 2026 (requiere correr antes seguimiento_pronostico.py)."""
import os, json
import pandas as pd, numpy as np
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
RAIZ = os.path.dirname(os.path.abspath(__file__))
S = pd.read_csv(os.path.join(RAIZ, "seguimiento_municipal.csv"), dtype={"cod": str})
R = json.load(open(os.path.join(RAIZ, "seguimiento_resumen.json"))); cal = pd.DataFrame(R["calibracion"])
AZ, NA, RO = "#1f4e79", "#d98c2b", "#b03a2e"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10.5})
fig, axs = plt.subplots(1, 2, figsize=(16, 9), dpi=150, gridspec_kw=dict(width_ratios=[1, 1.25])); fig.subplots_adjust(left=0.06, right=0.97, top=0.80, bottom=0.12, wspace=0.32)
fig.text(0.06, 0.94, "Pronóstico de terrorismo por municipio: primer mes de seguimiento", fontsize=21, fontweight="bold")
fig.text(0.06, 0.9, "Octubre de 2026 observado frente al pronóstico publicado el 9 de noviembre (horizonte octubre de 2026 a marzo de 2027)", fontsize=12.5, color="#444")
fig.text(0.06, 0.868, "117 actos observados contra 105 esperados para el mes. AUC 0,92 del modelo frente a 0,90 de ordenar por los últimos doce meses. Octubre es preliminar.", fontsize=10.5, color="#666")
ax = axs[0]; x = np.arange(len(cal)); w = 0.38
ax.bar(x - w / 2, cal.esperados_con_evento, w, color=NA, label="Esperados con al menos un acto"); ax.bar(x + w / 2, cal.con_evento, w, color=AZ, label="Observados con al menos un acto")
for i, r in cal.iterrows():
    ax.text(i - w / 2, r.esperados_con_evento + 0.6, f"{r.esperados_con_evento:.0f}", ha="center", fontsize=10); ax.text(i + w / 2, r.con_evento + 0.6, f"{r.con_evento:.0f}", ha="center", fontsize=10, fontweight="bold")
ax.set_xticks(x); ax.set_xticklabels([f"{t}\n({m} mpios.)" for t, m in zip(cal.tramo, cal.municipios)]); ax.set_xlabel("Probabilidad publicada de al menos un acto en el semestre")
ax.set_title("Municipios con acto en octubre, por tramo de probabilidad", loc="left", fontsize=12.5, fontweight="bold"); ax.legend(frameon=False, loc="upper left")
for s in ("top", "right"): ax.spines[s].set_visible(False)
ax = axs[1]; t = S.sort_values("ranking").head(25).iloc[::-1]; yy = np.arange(len(t))
ax.barh(yy, t.esperado_a_la_fecha, color="#e6d2b5", height=0.7)
ax.scatter(t.observado_a_la_fecha, yy, color=[RO if o == 0 else AZ for o in t.observado_a_la_fecha], s=55, zorder=3)
ax.set_yticks(yy); ax.set_yticklabels([f"{r.ranking}. {r.mpio_cnmbr.title()}" for r in t.itertuples()], fontsize=9.5)
ax.set_title("Los 25 municipios de mayor riesgo: esperado (barra) y observado (punto)", loc="left", fontsize=12.5, fontweight="bold"); ax.set_xlabel("Actos en octubre")
for s in ("top", "right"): ax.spines[s].set_visible(False)
ax.text(0.99, 0.02, "Punto rojo: sin actos registrados en octubre", transform=ax.transAxes, ha="right", fontsize=9.5, color=RO)
fig.text(0.06, 0.03, "Fuente: Ministerio de Defensa Nacional, datos abiertos, corte 31 de octubre de 2026. El esperado mensual es un tercio de la intensidad pronosticada para el cuarto trimestre. Cálculos: Gustavo A Romero.", fontsize=8.5, color="#777")
fig.savefig(os.path.join(RAIZ, "fig4_seguimiento_octubre.png"), facecolor="white")
