# -*- coding: utf-8 -*-
"""Validación metodológica independiente: reimplementa desde cero (NumPy/SciPy) los cálculos centrales y los
compara con las implementaciones de librería usadas en el análisis. Es distinta de la 'verificación de reproducción'
(10_verificar_reproduccion.py), que sólo comprueba que el código vuelve a producir las mismas tablas."""
from common import *
from pca_lib import zscore, pca_varimax, quadrant, tucker
from spatial_lib import build_W
import json
from scipy.stats import mannwhitneyu, pearsonr
from statsmodels.stats.multitest import multipletests
from factor_analyzer.factor_analyzer import calculate_kmo
from esda.moran import Moran

m = pd.read_csv(f'{DAT}/base82_con_ejes.csv'); R = {}
Z = zscore(m[VARS7].values)

# 1) Autovalores: eigh (propio) vs sklearn PCA
ev = np.sort(np.linalg.eigvalsh(np.corrcoef(Z, rowvar=False)))[::-1]
res = pca_varimax(Z, VARS7); R['eig_max_abs_diff'] = float(np.abs(ev - res['lam']).max())

# 2) Varimax (SVD, con normalización de Kaiser) escrito a mano vs factor_analyzer
def varimax(L, gamma=1.0, q=1000, tol=1e-10):
    p, k = L.shape; Rm = np.eye(k); d = 0
    for _ in range(q):
        d_old = d; Lr = L @ Rm
        u, s, vt = np.linalg.svd(L.T @ (Lr**3 - (gamma / p) * Lr @ np.diag((Lr**2).sum(0))))
        Rm = u @ vt; d = s.sum()
        if d_old != 0 and d / d_old < 1 + tol: break
    return L @ Rm, Rm
L = res['L']; h = np.sqrt((L**2).sum(1, keepdims=True))     # normalización de Kaiser (por filas), como en SPSS/R/factor_analyzer
Ln, R_own = varimax(L / h); Lr_own = (L / h) @ R_own * h
a = np.sort(np.abs(Lr_own), axis=1); b = np.sort(np.abs(res['Lr']), axis=1)
R['varimax_max_abs_diff_cargas'] = float(np.abs(np.abs(Lr_own[:, np.argsort(-np.abs(Lr_own).sum(0))]) -
                                                  np.abs(res['Lr'][:, np.argsort(-np.abs(res['Lr']).sum(0))])).max())
# 3) Puntajes rotados: S_rot = Z V Λ^-1/2 R  vs  Z · (V Λ^-1/2 R)  y vs. regresión sobre las cargas rotadas
S_dir = Z @ (res['V'][:, :2] / np.sqrt(res['lam'][:2])) @ res['R']
R['puntajes_rotados_max_abs_diff'] = float(np.abs(S_dir - res['Sr']).max())
R['corr_puntajes_ortogonales'] = float(np.corrcoef(res['Sr'].T)[0, 1])        # deben ser ~0 (rotación ortogonal)
R['var_puntajes'] = [float(x) for x in res['Sr'].var(0, ddof=1)]                # deben ser ~1
# 4) Comunalidades: suma de cargas^2 sin rotar = rotadas
R['comunalidad_max_abs_diff'] = float(np.abs((res['L']**2).sum(1) - (res['Lr']**2).sum(1)).max())
# 5) KMO propio vs factor_analyzer
Rm = np.corrcoef(Z, rowvar=False); Ri = np.linalg.inv(Rm); Pp = -Ri / np.sqrt(np.outer(np.diag(Ri), np.diag(Ri))); np.fill_diagonal(Pp, 0)
off = Rm - np.eye(7); kmo_own = (off**2).sum() / ((off**2).sum() + (Pp**2).sum())
R['kmo_diff'] = float(abs(kmo_own - calculate_kmo(Z)[1]))
# 6) Moran I manual con W estandarizada por filas vs esda
w, _ = build_W(m); Wm = w.full()[0]; mm = pd.read_csv(f'{DAT}/base82_con_ejes.csv')
dif = []
for col in ['IDH_2024', 'ICC_2024', 'ISC_2025', 'E', 'S']:
    if col not in mm: continue
    x = mm[col].values; xc = x - x.mean(); I_own = (len(x) / Wm.sum()) * (xc @ Wm @ xc) / (xc @ xc)
    dif.append(abs(I_own - Moran(x, w, permutations=0).I))
R['moran_max_abs_diff'] = float(max(dif))
# 7) BH propio vs statsmodels
p = np.random.default_rng(1).uniform(size=60)**2
R['bh_max_abs_diff'] = float(np.abs(bh_fdr(p) - multipletests(p, method='fdr_bh')[1]).max())
# 8) rank-biserial propio (2U/(n1 n2) − 1) vs fórmula por rangos de Wendt
x = m['Red_vial_pavimentada_pct'].values; g = (m.Q3_rot == 1).values
U = mannwhitneyu(x[g], x[~g], alternative='two-sided').statistic; rb = 2 * U / (g.sum() * (~g).sum()) - 1
ranks = stats.rankdata(x); rb_w = 2 * (ranks[g].mean() - ranks[~g].mean()) / len(x)
R['rank_biserial_diff'] = float(abs(rb - rb_w))
# 9) IC de Fisher propio vs scipy
r_, _ = pearsonr(m.IDH_2024, m.ICC_2024); z = np.arctanh(r_); se = 1 / np.sqrt(len(m) - 3)
lo, hi = np.tanh([z - 1.959964 * se, z + 1.959964 * se]); ci = pearsonr(m.IDH_2024, m.ICC_2024).confidence_interval(0.95)
R['fisher_ci_diff'] = float(max(abs(lo - ci.low), abs(hi - ci.high)))
# 10) Cuadrantes con los puntajes propios vs publicados
q_own = quadrant(S_dir[:, 0] * np.sign(res['Lr'][VARS7.index('ICC_2024'), 0]), S_dir[:, 1])
R['cuadrantes_iguales_pct'] = float((q_own == m.q_rot.values).mean() * 100)
R['TOL'] = '1e-6 (2e-3 para cargas varimax: tolerancia de convergencia de factor_analyzer, 1e-5 en el criterio)'
R['todo_ok'] = bool(all(abs(R[k]) < 1e-6 for k in ['eig_max_abs_diff', 'puntajes_rotados_max_abs_diff', 'comunalidad_max_abs_diff', 'kmo_diff', 'moran_max_abs_diff', 'bh_max_abs_diff', 'rank_biserial_diff', 'fisher_ci_diff', 'corr_puntajes_ortogonales'])
                    and R['varimax_max_abs_diff_cargas'] < 2e-3 and abs(R['var_puntajes'][0] - 1) < 1e-6 and R['cuadrantes_iguales_pct'] == 100)
json.dump(R, open(f'{TAB}/_validacion_independiente.json', 'w'), indent=1)
for k, v in R.items(): print(k, v)
