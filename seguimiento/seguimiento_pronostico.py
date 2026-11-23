# -*- coding: utf-8 -*-
"""Seguimiento del pronostico GP de terrorismo (publicado el 9 de noviembre de 2026, horizonte octubre 2026 - marzo 2027)
contra lo observado. Corte de datos: 31 de octubre de 2026 (primer mes de seis)."""
import os, json
import numpy as np, pandas as pd

RAIZ = os.path.dirname(os.path.abspath(__file__))
P = pd.read_csv(os.path.join(RAIZ, "..", "resultados", "prob_municipios_6m.csv"), dtype={"cod": str}); P["cod"] = P.cod.str.zfill(5)
O = pd.read_csv(os.path.join(RAIZ, "terrorismo_muni_mes_corte_20261031.csv"), dtype=str)
O["n"] = O.n.astype(float); O["mes"] = O.mes.str[:7]; O["cod"] = O.cod_muni.str.zfill(5)
MES = sorted(m for m in O.mes.unique() if m >= "2026-10"); k = len(MES)
obs = O[O.mes.isin(MES)].groupby("cod").n.sum()
P["obs"] = P.cod.map(obs).fillna(0); P["evento"] = (P.obs > 0).astype(int)
fuera = obs[~obs.index.isin(P.cod)].sum()
# esperado para los meses observados: el trimestre T4 repartido por igual
P["esp"] = P.lambda_T4_2026 * k / 3.0
P["p_mes"] = 1 - (1 - P.prob_1_o_mas_6m.clip(upper=0.999999)) ** (k / 6.0)     # prob. de al menos uno en k meses, riesgo constante

def auc(score, y):
    r = pd.Series(score).rank().values; n1 = y.sum(); n0 = len(y) - n1
    return (r[y == 1].sum() - n1 * (n1 + 1) / 2) / (n1 * n0)

y = P.evento.values
base = P.eventos_ult_12m.values
res = dict(
    meses_observados=MES, corte="2026-10-31",
    nacional=dict(observado=float(P.obs.sum() + fuera), esperado_gp=float(P.esp.sum()), esperado_semestre=float(P.eventos_esperados_6m.sum()),
                  ritmo_necesario_resto=float((P.eventos_esperados_6m.sum() - P.obs.sum()) / (6 - k))),
    municipios_con_evento=int(y.sum()), municipios_esperados_con_evento=float(P.p_mes.sum()),
    auc_gp=float(auc(P.prob_1_o_mas_6m.values, y)), auc_base_12m=float(auc(base, y)),
    captura=dict(), sorpresas=[], ausentes=[])
for N in (10, 30, 50, 100):
    top = P.sort_values("ranking").head(N); tb = P.sort_values("eventos_ult_12m", ascending=False).head(N)
    res["captura"][f"top{N}"] = dict(eventos_gp=float(top.obs.sum() / P.obs.sum()), eventos_base=float(tb.obs.sum() / P.obs.sum()),
                                      municipios_con_evento_gp=int(top.evento.sum()), municipios_con_evento_base=int(tb.evento.sum()))
# calibracion por tramos de probabilidad semestral
P["tramo"] = pd.cut(P.prob_1_o_mas_6m, [-0.01, .05, .2, .5, .8, 1.0], labels=["0-5 %", "5-20 %", "20-50 %", "50-80 %", "80-100 %"])
cal = P.groupby("tramo", observed=True).agg(municipios=("cod", "size"), con_evento=("evento", "sum"), esperados_con_evento=("p_mes", "sum"), eventos=("obs", "sum"), eventos_esperados=("esp", "sum")).round(1)
res["calibracion"] = cal.reset_index().to_dict("records")
s = P[P.evento == 1].sort_values("prob_1_o_mas_6m").head(10)
res["sorpresas"] = s[["mpio_cnmbr", "dpto_cnmbr", "obs", "prob_1_o_mas_6m", "ranking"]].to_dict("records")
a = P[(P.evento == 0)].sort_values("ranking").head(10)
res["ausentes"] = a[["mpio_cnmbr", "dpto_cnmbr", "esp", "prob_1_o_mas_6m", "ranking"]].round(2).to_dict("records")
t = P.sort_values("ranking").head(15)[["ranking", "mpio_cnmbr", "dpto_cnmbr", "esp", "obs", "prob_1_o_mas_6m"]].round(2)
P.sort_values("ranking")[["ranking", "cod", "dpto_cnmbr", "mpio_cnmbr", "prob_1_o_mas_6m", "eventos_esperados_6m", "esp", "obs", "evento"]].rename(columns={"esp": "esperado_a_la_fecha", "obs": "observado_a_la_fecha"}).round(3).to_csv(os.path.join(RAIZ, "seguimiento_municipal.csv"), index=False)
json.dump(res, open(os.path.join(RAIZ, "seguimiento_resumen.json"), "w"), ensure_ascii=False, indent=1, default=float)
print(json.dumps({k_: v for k_, v in res.items() if k_ not in ("calibracion", "sorpresas", "ausentes")}, ensure_ascii=False, indent=0, default=float))
print(cal); print(t.to_string(index=False)); print(pd.DataFrame(res["sorpresas"]).to_string(index=False)); print(pd.DataFrame(res["ausentes"]).to_string(index=False)); print("fuera del marco:", fuera)
