# -*- coding: utf-8 -*-
"""Índice interno de rezago relativo de infraestructura normalizada (casos para validación diagnóstica) con escenarios de sensibilidad."""
from common import *
from pca_lib import zscore
import json
m = pd.read_csv(f'{DAT}/base82_con_ejes.csv'); OUT={}
Xi = m[INFRA].values; Z = zscore(Xi)                        # z-scores sobre los 82 cantones; mayor valor del indicador = mejor dotación
Zr = (Xi-np.median(Xi,0))/stats.median_abs_deviation(Xi,axis=0,scale='normal')
q3 = np.where(m.Q3_rot==1)[0]; names = m.canton.values
def rank_in_q3(index):     # 1 = mayor rezago relativo dentro de Q3
    s = pd.Series(index[q3], index=names[q3]); return s.rank(ascending=False, method='min')
scen={}; idx={}
idx['E0 · Pesos iguales, 8 indicadores (versión original)'] = -Z.mean(1)
dens = [INFRA.index('Entidades_financieras_xkm2'), INFRA.index('Log_viviendas_electricidad_xkm2')]
keep6=[i for i in range(8) if i not in dens]; idx['E1 · Sin las 2 densidades por km² (6 indicadores)'] = -Z[:,keep6].mean(1)
pc = np.linalg.eigh(np.corrcoef(Xi,rowvar=False)); w1 = pc[1][:,-1]; w1 = w1*np.sign(w1.sum()); idx['E2 · Ponderación por 1.er componente principal (8)'] = -(Z@w1)/np.abs(w1).sum()
idx['E3 · z robusto (mediana/MAD), pesos iguales'] = -np.clip(Zr,-3,3).mean(1)
for i,v in enumerate(INFRA): idx[f'L{i+1} · Sin {LAB_INFRA[v]}'] = -np.delete(Z,i,1).mean(1)
idx['E4 · Sin ENAHO (precisión cantonal no verificada)'] = -np.delete(Z,INFRA.index('Internet_hogares_pct'),1).mean(1)
R = pd.DataFrame({k: rank_in_q3(v) for k,v in idx.items()})
summ = pd.DataFrame({'canton':R.index, 'rango_E0':R.iloc[:,0].values, 'rango_mediano':R.median(1).values, 'rango_min':R.min(1).values, 'rango_max':R.max(1).values,
                     'pct_escenarios_top5':(R<=5).mean(1).values*100, 'pct_escenarios_top8':(R<=8).mean(1).values*100, 'indice_E0':idx[list(idx)[0]][q3]})
summ['provincia']=m.set_index('canton').loc[summ.canton,'provincia'].values; summ['ln_dens']=m.set_index('canton').loc[summ.canton,'ln_densidad_pob_2024'].values
summ = summ.sort_values(['rango_mediano','rango_E0']).reset_index(drop=True); summ.to_csv(f'{TAB}/T16_rezago_estabilidad_rangos.csv', index=False, encoding='utf-8-sig')
R.to_csv(f'{TAB}/T16b_rezago_rangos_por_escenario.csv', encoding='utf-8-sig'); print(summ.head(12).round(1).to_string(index=False)); print('n escenarios:', R.shape[1])
# ¿mide ruralidad? correlación del índice con densidad poblacional (82 cantones y dentro de Q3)
for k in list(idx)[:3]:
    rho_all = stats.spearmanr(idx[k], m.ln_densidad_pob_2024)[0]; rho_q3 = stats.spearmanr(idx[k][q3], m.ln_densidad_pob_2024.values[q3])[0]
    print(k, '| rho con ln densidad (82): %.2f | dentro de Q3: %.2f' % (rho_all,rho_q3)); OUT[k[:2]]=dict(rho82=float(rho_all), rho_q3=float(rho_q3))
# concordancia entre escenarios (Kendall tau medio vs E0)
tau = [stats.kendalltau(R.iloc[:,0], R[c])[0] for c in R.columns[1:]]; OUT['tau_medio_vs_E0']=float(np.mean(tau)); OUT['tau_min']=float(np.min(tau)); OUT['n_esc']=int(R.shape[1])
# lista top-5 del escenario original y su estabilidad
OUT['top5_E0']=R.iloc[:,0].sort_values().index[:5].tolist(); OUT['top5_E0_pct']=summ.set_index('canton').loc[OUT['top5_E0'],'pct_escenarios_top5'].round(0).to_dict()
OUT['mediana_top5']=summ.canton.head(5).tolist()
print(OUT)
# fórmula e índice por cantón (todos los 82) para anexo
pd.DataFrame({'canton':names,'cuadrante_rotado':m.q_rot,'indice_rezago_E0':idx[list(idx)[0]]}).to_csv(f'{TAB}/T16c_indice_rezago_82.csv', index=False, encoding='utf-8-sig')
json.dump(OUT, open(f'{TAB}/_rezago_resumen.json','w'), indent=1, default=lambda o: o if not hasattr(o,'item') else o.item())
