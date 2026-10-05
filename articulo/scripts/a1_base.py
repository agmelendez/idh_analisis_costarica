# Parte A: IDG, inferencia Tabla 5, descriptivos y chequeo de extremos
from common import *
from scipy import stats
import json
O=f'{W}/out'
# ---------- A. IDG ----------
d=d3.copy()
d['dist_paridad']=(d.IDG_2024-1).abs()
d['dist_cat'],bD=jenks5(d.dist_paridad)   # 0 = más cerca de paridad
print('Jenks |IDG-1|',np.round(bD,4),d.dist_cat.value_counts().sort_index().tolist())
below=(d.IDG_2024<1).sum(); above=(d.IDG_2024>1).sum(); print('IDG<1',below,'IDG>1',above, 'min',d.IDG_2024.min(),'max',d.IDG_2024.max())
near=((d.IDG_2024-1).abs()<=0.02).sum(); print('|IDG-1|<=0.02:',near)
print(d[d.IDG_2024>1][['canton','IDG_2024','IDH_cat']])
print('IDG bruto Jenks',np.round(bIDG,4),d.IDG_cat.value_counts().sort_index().tolist())
for c in range(5): print('dist',c,d[d.dist_cat==c].sort_values('dist_paridad')[['canton','IDG_2024']].round(3).values.tolist()[:40] if c in(0,4) else len(d[d.dist_cat==c]))
# comparación con IDH
r,p=stats.spearmanr(d.IDH_cat,d.dist_cat); print('Spearman cat IDH vs cat distancia',r,p)
r2,p2=stats.spearmanr(d.IDH_2024,d.IDG_2024); print('rho IDH-IDG continuo',r2,p2, 'rho IDH vs dist',stats.spearmanr(d.IDH_2024,d.dist_paridad))
print(pd.crosstab(d.IDH_cat,d.dist_cat))
print(pd.crosstab(d.IDH_cat,d.IDG_cat))
d.to_pickle(f'{O}/d_idg.pkl')
