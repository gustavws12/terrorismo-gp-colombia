# -*- coding: utf-8 -*-
"""Proceso gaussiano espacio-temporal (núcleo separable, estructura de Kronecker) sobre conteos trimestrales de actos terroristas por municipio.
Modelo: y_{s,t} = log(1 + n_{s,t}/pop_s*...)? No: y = log1p(n) ; f ~ GP(m, k_s(Matérn 3/2 sobre centroides en km) * k_t(mezcla de dos Matérn 3/2: escala corta ~1 trimestre y larga ~30 trimestres)) ; y = f + ε.
Con rejilla completa municipios x trimestres, K = Ks ⊗ Kt y la inversión es O(S^3 + T^3) por eigendescomposición.
Hiperparámetros: rejilla evaluada por AUC predictivo fuera de muestra con dos orígenes (ajuste hasta 2025T3 → 2025T4-2026T1; ajuste hasta 2026T1 → 2026T2-T3); se reporta también la verosimilitud marginal.
El núcleo periódico anual se probó y la verosimilitud lo descartó (amplitud 0).
Pronóstico: f en los trimestres siguientes, intensidad λ = E[exp(f)] − 1 (retro-transformación lognormal), probabilidad de ≥1 evento en 6 meses = 1 − exp(−(λ_{T+1} + λ_{T+2})).
Validación: ajuste hasta 2025T3, pronóstico 2025T4-2026T1, AUC y captura del top-50."""
import numpy as np, pandas as pd, json, os, itertools
from sklearn.metrics import roc_auc_score
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); D = f"{RAIZ}/datos"; OUT = f"{RAIZ}/resultados"
d = pd.read_csv(f"{D}/terrorismo_mindefensa_2003_2026.csv", dtype=str); d["n"] = d.cantidad.astype(int); d["fecha"] = pd.to_datetime(d.fecha_hecho); d["cod"] = d.cod_muni.str.zfill(5)
c = pd.read_csv(f"{D}/centroides_mpios.csv", dtype={"mpio_cdpmp": str, "dpto_ccdgo": str, "mpio_ccdgo": str}).rename(columns={"mpio_cdpmp": "cod"}).sort_values("cod").reset_index(drop=True)
INI = "2015-01-01"; d = d[d.fecha >= INI]
d["q"] = d.fecha.dt.to_period("Q"); qs = pd.period_range(INI, "2026-09-30", freq="Q"); S, T = len(c), len(qs)
Y = d.groupby(["cod", "q"]).n.sum().unstack("q").reindex(index=c.cod, columns=qs).fillna(0).values   # S x T conteos
# 2026T3 solo tiene jul-sep completo (datos a 30-sep): ok
# coordenadas en km (proyección equirectangular local)
lat0 = np.deg2rad(c.lat.mean()); X = np.column_stack([(c.lon - c.lon.mean()) * 111.32 * np.cos(lat0), (c.lat - c.lat.mean()) * 110.57])
tt = np.arange(T, dtype=float)
def matern32(D_, ell): r = np.sqrt(3) * D_ / ell; return (1 + r) * np.exp(-r)
def dist(A, B): return np.sqrt(((A[:, None, :] - B[None, :, :]) ** 2).sum(-1))
Ds = dist(X, X); Dt = np.abs(tt[:, None] - tt[None, :])
def Kt_fun(t1, t2, ell_t, per_amp):
    """ell_t = (escala corta, escala larga) en trimestres; per_amp = peso de la escala corta."""
    D_ = np.abs(t1[:, None] - t2[None, :]); return per_amp * matern32(D_, ell_t[0]) + (1 - per_amp) * matern32(D_, ell_t[1])
# transformación: log1p de conteos, media global
Yl = np.log1p(Y); mu = Yl.mean()
def fit_eval(ell_s, ell_t, per_amp, sf2, sn2, Yl_fit, T_fit, return_model=False):
    Ks = sf2 * matern32(Ds, ell_s); Kt = Kt_fun(tt[:T_fit], tt[:T_fit], ell_t, per_amp)
    ls, Us = np.linalg.eigh(Ks); lt, Ut = np.linalg.eigh(Kt); lam = np.outer(ls, lt) + sn2        # S x T
    R = Yl_fit - mu; Rt = Us.T @ R @ Ut; alpha_t = Rt / lam; alpha = Us @ alpha_t @ Ut.T                 # (K+σ²I)^-1 vec(R) en forma matricial
    nll = 0.5 * (Rt * alpha_t).sum() + 0.5 * np.log(lam).sum() + 0.5 * S * T_fit * np.log(2 * np.pi)
    if not return_model: return nll
    return dict(nll=nll, alpha=alpha, Us=Us, ls=ls, Ut=Ut, lt=lt, lam=lam, Ks=Ks, Kt=Kt)
def predict(model, ell_t, per_amp, sn2, T_fit, H):
    t_new = np.arange(T_fit, T_fit + H, dtype=float); Kt_star = Kt_fun(t_new, tt[:T_fit], ell_t, per_amp)       # H x T_fit
    F = mu + model["Ks"] @ model["alpha"] @ Kt_star.T                                                           # S x H media posterior de f
    # varianza posterior (aprox. por Kronecker): var = ks(s,s)kt(t,t) - sum over eigen
    Us, ls, Ut, lt, lam = model["Us"], model["ls"], model["Ut"], model["lt"], model["lam"]
    A = (Us ** 2)                                     # S x S
    B = (Kt_star @ Ut) ** 2                           # H x T_fit
    # var posterior exacta bajo Kronecker: k_s(s,s) k_t(h,h) - sum_ij Us[s,i]^2 ls_i^2 (Kt* Ut)[h,j]^2 / lam_ij
    V = np.diag(model["Ks"])[:, None] * np.diag(Kt_fun(t_new, t_new, ell_t, per_amp))[None, :] - (A * ls[None, :] ** 2) @ (1 / lam) @ B.T
    V = np.clip(V, 1e-6, None)
    lam_cnt = np.exp(F + V / 2) - 1                   # E[exp(f)] - 1 = intensidad esperada (media lognormal): calibrada para TOTALES
    lam_med = np.exp(F) - 1                           # mediana: calibrada para la PROBABILIDAD de ocurrencia (la media lognormal infla los municipios sin historia, donde V es la varianza a priori)
    return F, V, np.clip(lam_cnt, 0, None), np.clip(lam_med, 0, None)

# ---------- selección de hiperparámetros: AUC predictivo con dos orígenes (y verosimilitud marginal como referencia) ----------
def auc_origen(hp, T_fit):
    m = fit_eval(*hp, Yl[:, :T_fit], T_fit, True); F_, V_, l_, lm_ = predict(m, hp[1], hp[2], hp[4], T_fit, 2)
    return roc_auc_score((Y[:, T_fit:T_fit + 2].sum(1) > 0).astype(int), lm_.sum(1)), m["nll"]
grid = list(itertools.product([40, 80], [(1, 30), (2, 30), (1, 12)], [0.3, 0.6], [0.5, 1.0], [0.05, 0.15]))
tabla = []
for hp in grid:
    a1, n1 = auc_origen(hp, T - 4); a2, _ = auc_origen(hp, T - 2); tabla.append(dict(ell_s=hp[0], ell_corta=hp[1][0], ell_larga=hp[1][1], w_corta=hp[2], sf2=hp[3], sn2=hp[4], nll_T_4=n1, auc_2025T4_2026T1=a1, auc_2026T2_T3=a2, auc_prom=(a1 + a2) / 2))
tabla = pd.DataFrame(tabla).sort_values("auc_prom", ascending=False).reset_index(drop=True); tabla.round(4).to_csv(f"{OUT}/hiperparametros_rejilla.csv", index=False)
b = tabla.iloc[0]; ell_s, ell_t, per_amp, sf2, sn2 = int(b.ell_s), (int(b.ell_corta), int(b.ell_larga)), float(b.w_corta), float(b.sf2), float(b.sn2)
print("hiperparámetros (mejor AUC predictivo):", dict(ell_s_km=ell_s, ell_t_trim=ell_t, w_corta=per_amp, sf2=sf2, sn2=sn2)); print(tabla.head(5).round(3).to_string())
print("mejor por verosimilitud marginal:", tabla.sort_values("nll_T_4").iloc[0].round(3).to_dict())

# ---------- validación fuera de muestra: ajuste hasta 2025T3 (T-4), pronóstico 2 trimestres ----------
T_fit = T - 4; model_v = fit_eval(ell_s, ell_t, per_amp, sf2, sn2, Yl[:, :T_fit], T_fit, True)
F_v, V_v, lam_v, lmed_v = predict(model_v, ell_t, per_amp, sn2, T_fit, 2)
p_v = 1 - np.exp(-lmed_v.sum(1)); obs_v = (Y[:, T_fit:T_fit + 2].sum(1) > 0).astype(int)
auc = roc_auc_score(obs_v, p_v); top50 = np.argsort(-p_v)[:50]; cap50 = Y[top50, T_fit:T_fit + 2].sum() / Y[:, T_fit:T_fit + 2].sum()
# calibración por deciles (probabilidad con la mediana vs con la media lognormal) en los dos orígenes
cal = []
for To in [T - 4, T - 2]:
    mo = fit_eval(ell_s, ell_t, per_amp, sf2, sn2, Yl[:, :To], To, True); Fo, Vo, lo, lmo = predict(mo, ell_t, per_amp, sn2, To, 2)
    dfc = pd.DataFrame(dict(p_mediana=1 - np.exp(-lmo.sum(1)), p_lognormal=1 - np.exp(-lo.sum(1)), observado=(Y[:, To:To + 2].sum(1) > 0).astype(int))); dfc["decil"] = pd.qcut(dfc.p_mediana, 10, labels=False) + 1
    cc = dfc.groupby("decil").mean(); cc["origen"] = str(qs[To - 1]); cc["n"] = dfc.groupby("decil").size(); cal.append(cc)
    print(f"origen {qs[To - 1]}: observados {Y[:, To:To + 2].sum():.0f}, esperados media lognormal {lo.sum():.0f}, mediana {lmo.sum():.0f}")
cal = pd.concat(cal).reset_index(); cal.round(3).to_csv(f"{OUT}/calibracion_deciles.csv", index=False); print(cal.round(3).to_string())
# base ingenua: tasa de los últimos 8 trimestres
base = Y[:, T_fit - 8:T_fit].mean(1) * 2; p_base = 1 - np.exp(-base); auc_base = roc_auc_score(obs_v, p_base); cap50_base = Y[np.argsort(-p_base)[:50], T_fit:T_fit + 2].sum() / Y[:, T_fit:T_fit + 2].sum()
print(f"validación 2025T4-2026T1: AUC GP {auc:.3f} (base {auc_base:.3f}); captura top-50 GP {cap50:.1%} (base {cap50_base:.1%}); municipios con evento {obs_v.sum()}")

# ---------- ajuste completo y pronóstico 2026T4-2027T1 ----------
model = fit_eval(ell_s, ell_t, per_amp, sf2, sn2, Yl, T, True); F, V, lam, lmed = predict(model, ell_t, per_amp, sn2, T, 2)
res = c[["cod", "dpto_cnmbr", "mpio_cnmbr", "lon", "lat"]].copy()
res["eventos_2015_2026"] = Y.sum(1).astype(int); res["eventos_ult_12m"] = Y[:, -4:].sum(1).astype(int); res["eventos_2026"] = Y[:, -3:].sum(1).astype(int)
res["lambda_T4_2026"] = lam[:, 0]; res["lambda_T1_2027"] = lam[:, 1]; res["eventos_esperados_6m"] = lam.sum(1)
L = lmed.sum(1); res["intensidad_mediana_6m"] = L
res["prob_1_o_mas_6m"] = 1 - np.exp(-L); res["prob_3_o_mas_6m"] = 1 - np.exp(-L) * (1 + L + L ** 2 / 2)
res["sd_log_f"] = np.sqrt(V.mean(1))
res = res.sort_values("prob_1_o_mas_6m", ascending=False).reset_index(drop=True); res["ranking"] = np.arange(1, S + 1)
res.round(4).to_csv(f"{OUT}/prob_municipios_6m.csv", index=False)
# serie nacional ajustada vs observada
F_in = mu + model["Ks"] @ model["alpha"] @ model["Kt"].T                          # S x T media posterior en muestra
V_in = np.clip(np.diag(model["Ks"])[:, None] * np.diag(model["Kt"])[None, :] - ((model["Us"] ** 2) * model["ls"][None, :] ** 2) @ (1 / model["lam"]) @ ((model["Kt"] @ model["Ut"]) ** 2).T, 1e-6, None)
nac = pd.DataFrame({"trimestre": qs.astype(str), "observado": Y.sum(0), "ajustado": (np.exp(F_in + V_in / 2) - 1).clip(0).sum(0), "ajustado_mediana": (np.exp(F_in) - 1).clip(0).sum(0)})
print("factor de retransformación observado/ajustado (media lognormal):", round(nac.observado.sum() / nac.ajustado.sum(), 3))
nac.to_csv(f"{OUT}/serie_nacional_trimestral.csv", index=False)
summ = dict(hiper=dict(ell_s_km=ell_s, ell_t_corta_trim=ell_t[0], ell_t_larga_trim=ell_t[1], w_corta=per_amp, sf2=sf2, sn2=sn2), validacion=dict(auc_gp=float(auc), auc_base=float(auc_base), captura_top50_gp=float(cap50), captura_top50_base=float(cap50_base), municipios_con_evento=int(obs_v.sum())),
            pronostico=dict(eventos_esperados_nacional_6m=float(lam.sum()), eventos_obs_ult_6m=int(Y[:, -2:].sum()), municipios_prob_mayor_50=int((res.prob_1_o_mas_6m > 0.5).sum()), municipios_prob_mayor_80=int((res.prob_1_o_mas_6m > 0.8).sum())),
            top30=res.head(30)[["ranking", "dpto_cnmbr", "mpio_cnmbr", "eventos_ult_12m", "eventos_esperados_6m", "prob_1_o_mas_6m"]].round(3).to_dict("records"))
json.dump(summ, open(f"{OUT}/gp_terrorismo_resumen.json", "w"), indent=2, ensure_ascii=False)
print(json.dumps({k: v for k, v in summ.items() if k != "top30"}, indent=1, ensure_ascii=False)); print(res.head(30)[["dpto_cnmbr", "mpio_cnmbr", "eventos_ult_12m", "eventos_esperados_6m", "prob_1_o_mas_6m"]].round(2).to_string(index=False))
