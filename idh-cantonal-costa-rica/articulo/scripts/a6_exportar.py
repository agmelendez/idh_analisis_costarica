# Exporta tablas auxiliares (IDG, autovalores con análisis paralelo, cargas) a partir de los intermedios de a1 y a2.
import pickle, numpy as np, pandas as pd
from common import W
O=f'{W}/out'
d=pd.read_pickle(f'{O}/d_idg.pkl')
d[['cod_canton','provincia','canton','IDH_2024','IDHD_2024','IDG_2024','IDH_cat','IDHD_cat','IDG_cat','dist_paridad','dist_cat']].to_csv(f'{O}/IDG_clasificacion_cantonal.csv',index=False,encoding='utf-8-sig')
P=pickle.load(open(f'{O}/res.pkl','rb')); res=P['res']; SHORT=P['SHORT']
ESP=[('log','ln (principal)'),('principal','escala original')]
ev_rows=[];ld_rows=[]
for k,lab in ESP:
    r=res[k]; p=len(r['ev'])
    for i in range(p):
        ev_rows.append(dict(especificacion=lab,componente=i+1,autovalor=r['ev'][i],pct_varianza=100*r['ev'][i]/p,AP_p95_permutacion=r['pa95'][i],AP_media=r['pamean'][i],AP_p95_normal=r['pn95'][i]))
    for j,v in enumerate(SHORT):
        ld_rows.append(dict(especificacion=lab,variable=v,PC1_sin_rotar=r['L'][j,0],PC2_sin_rotar=r['L'][j,1],PC1_varimax=r['Lr'][j,0],PC2_varimax=r['Lr'][j,1],comunalidad=r['h2'][j],KMO=r['kmo_v'][j]))
pd.DataFrame(ev_rows).to_csv(f'{O}/PCA_autovalores_analisis_paralelo.csv',index=False,encoding='utf-8-sig')
pd.DataFrame(ld_rows).to_csv(f'{O}/PCA_cargas_comunalidades_KMO.csv',index=False,encoding='utf-8-sig')
print('exportadas 3 tablas auxiliares')
