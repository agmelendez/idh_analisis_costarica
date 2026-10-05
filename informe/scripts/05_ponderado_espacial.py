# -*- coding: utf-8 -*-
"""FASE 2 (parte 2) · Estimandos distintos (cantón vs población) y dependencia espacial (Moran global, LISA con FDR, join counts)."""
from common import *
from spatial_lib import *
from esda import Moran, Moran_Local, Join_Counts
import json
m = pd.read_csv(f'{DAT}/base82_con_ejes.csv'); w,_ = build_W(m); OUT={}
np.random.seed(SEED)
# ---------- perfil por cuadrante: no ponderado (mediana, IQR) y ponderado por población ------------------------
tot_pop = m.pob_2024.sum(); OUT['pob_total_82']=float(tot_pop)
rows=[]
for q in ['Q1','Q2','Q3','Q4']:
    s = m[m.q_rot==q]; row=dict(cuadrante=q, n=len(s), pob=s.pob_2024.sum(), pct_pob=s.pob_2024.sum()/tot_pop*100, pct_area=s.area_km2.sum()/m.area_km2.sum()*100, densidad_mediana=s.densidad_pob_2024.median())
    for v in VARS7:
        row[v+'_med']=s[v].median(); row[v+'_q1']=s[v].quantile(.25); row[v+'_q3']=s[v].quantile(.75); row[v+'_media']=s[v].mean(); row[v+'_media_pond']=np.average(s[v], weights=s.pob_2024)
    rows.append(row)
prof = pd.DataFrame(rows); prof.to_csv(f'{TAB}/T12_perfil_cuadrantes_rotados.csv', index=False, encoding='utf-8-sig')
print(prof[['cuadrante','n','pob','pct_pob','pct_area','densidad_mediana']].round(2).to_string(index=False))
print(prof[['cuadrante']+[v+'_med' for v in VARS7]].round(3).to_string(index=False)); print(prof[['cuadrante']+[v+'_media' for v in VARS7]].round(3).to_string(index=False))
OUT['pct_pob_q']={r.cuadrante: float(r.pct_pob) for r in prof.itertuples()}; OUT['pct_area_q']={r.cuadrante: float(r.pct_area) for r in prof.itertuples()}
# perfil con cuadrante original (para contraste)
rows=[]
for q in ['Q1','Q2','Q3','Q4']:
    s=m[m.q_orig==q]; row=dict(cuadrante=q, n=len(s), pct_pob=s.pob_2024.sum()/tot_pop*100)
    for v in VARS7: row[v+'_media']=s[v].mean()
    rows.append(row)
pd.DataFrame(rows).to_csv(f'{TAB}/T12b_perfil_cuadrantes_originales.csv', index=False, encoding='utf-8-sig')
# ---------- Q3 vs resto: diferencia de medias no ponderada vs ponderada por población ---------------------------------
def wmean(x,wt): return np.average(x,weights=wt)
def comp_w(vars_, labels, fam, seed):
    rows=[]; q3=(m.Q3_rot==1).values; B=3000
    for j,v in enumerate(vars_):
        x=m[v].values; wt=m.pob_2024.values; rr=rng(seed*50+j)
        d_u = x[q3].mean()-x[~q3].mean(); d_w = wmean(x[q3],wt[q3])-wmean(x[~q3],wt[~q3]); bu=np.empty(B); bw=np.empty(B)
        ia=np.where(q3)[0]; ib=np.where(~q3)[0]
        for t in range(B):
            a=rr.choice(ia,len(ia)); b=rr.choice(ib,len(ib)); bu[t]=x[a].mean()-x[b].mean(); bw[t]=wmean(x[a],wt[a])-wmean(x[b],wt[b])
        sd = x.std(ddof=1)
        rows.append(dict(familia=fam, variable=labels[v], dif_media_no_pond=d_u, lo_u=np.percentile(bu,2.5), hi_u=np.percentile(bu,97.5), dif_media_pond=d_w, lo_w=np.percentile(bw,2.5), hi_w=np.percentile(bw,97.5),
                         dif_est_no_pond=d_u/sd, dif_est_pond=d_w/sd, misma_direccion=('Sí' if np.sign(d_u)==np.sign(d_w) else 'No')))
    return pd.DataFrame(rows)
cw = pd.concat([comp_w(INFRA,LAB_INFRA,'F2',1), comp_w(PIL,LAB_PIL,'F3',2)]); cw.to_csv(f'{TAB}/T13_q3_ponderado_vs_no_ponderado.csv', index=False, encoding='utf-8-sig'); print(cw.round(2).to_string(index=False))
# ---------- Moran global -------------------------------------------------------------------------------------------------
rows=[]
for nm,col in [(LAB7[v],v) for v in VARS7]+[('Eje económico (rotado)','E'),('Eje de seguridad (rotado)','S')]+[(LAB_INFRA[v],v) for v in INFRA]+[(LAB_PIL[v],v) for v in PIL]+[(LAB_IVC[v],v) for v in IVC]:
    mi = Moran(m[col].values, w, permutations=N_PERM); rows.append(dict(variable=nm, clave=col, I=mi.I, E_I=mi.EI, z_sim=mi.z_sim, p_sim=mi.p_sim))
mo = pd.DataFrame(rows); mo['q_fdr']=bh_fdr(mo.p_sim); mo.to_csv(f'{TAB}/T14_moran_global.csv', index=False, encoding='utf-8-sig'); print(mo.round(3).to_string(index=False))
OUT['moran_E']=float(mo.loc[mo.clave=='E','I'].iloc[0]); OUT['moran_S']=float(mo.loc[mo.clave=='S','I'].iloc[0]); OUT['p_moran_E']=float(mo.loc[mo.clave=='E','p_sim'].iloc[0]); OUT['p_moran_S']=float(mo.loc[mo.clave=='S','p_sim'].iloc[0])
OUT['n_moran_signif']=int((mo.q_fdr<0.05).sum()); OUT['n_moran_total']=len(mo)
# join counts de pertenencia a Q3 (agrupamiento espacial de Q3)
jc = Join_Counts(m.Q3_rot.values.astype(int), w, permutations=N_PERM); OUT.update(jc_bb=float(jc.bb), jc_bb_exp=float(jc.mean_bb), jc_bb_p=float(jc.p_sim_bb))
print('Join counts Q3: BB=%d (esperado %.1f), p=%.4f' % (jc.bb, jc.mean_bb, jc.p_sim_bb))
# ---------- LISA para los dos ejes, con FDR local ----------------------------------------------------------------------------
lisa_rows=[]; lab_q={1:'Alto-Alto',2:'Bajo-Alto',3:'Bajo-Bajo',4:'Alto-Bajo'}
for col,nm in [('E','Eje económico'),('S','Eje de seguridad')]:
    lm = Moran_Local(m[col].values, w, permutations=N_PERM, seed=SEED); q = lm.q.copy(); p=lm.p_sim; qf=bh_fdr(p)
    sig_raw = p<0.05; sig_fdr = qf<0.05
    cl = np.where(sig_fdr, [lab_q[k] for k in q], 'No significativo (FDR)'); clr = np.where(sig_raw, [lab_q[k] for k in q], 'No significativo')
    for i in range(82): lisa_rows.append(dict(eje=nm, cod_canton=m.cod_canton[i], canton=m.canton[i], Ii=lm.Is[i], p_sim=p[i], q_fdr=qf[i], cuadrante_lisa=lab_q[q[i]], cluster_fdr=cl[i], cluster_sin_ajuste=clr[i]))
    print(nm, '| clusters p<0.05 sin ajuste:', int(sig_raw.sum()), '| con FDR q<0.05:', int(sig_fdr.sum()), pd.Series(cl).value_counts().to_dict())
    OUT[f'lisa_{col}_raw']=int(sig_raw.sum()); OUT[f'lisa_{col}_fdr']=int(sig_fdr.sum()); OUT[f'lisa_{col}_dist']={k:int(v) for k,v in pd.Series(cl).value_counts().items()}
lisa = pd.DataFrame(lisa_rows); lisa.to_csv(f'{TAB}/T15_lisa.csv', index=False, encoding='utf-8-sig')
print(lisa[lisa.cluster_fdr!='No significativo (FDR)'][['eje','canton','cluster_fdr','Ii','q_fdr']].round(3).to_string(index=False))
json.dump(OUT, open(f'{TAB}/_esp_resumen.json','w'), indent=1, default=lambda o: o if not hasattr(o,'item') else o.item())
