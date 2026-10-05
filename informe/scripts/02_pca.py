# -*- coding: utf-8 -*-
"""FASE 3 · Reducción dimensional: KMO/Bartlett, Kaiser, análisis paralelo, cargas sin rotar y rotadas, comunalidades,
puntajes rotados directos, cuadrantes rotados vs no rotados, estabilidad bootstrap y sensibilidad (transformaciones, extremos, LOO, escenarios de año)."""
from common import *
from pca_lib import *
from factor_analyzer.factor_analyzer import calculate_kmo, calculate_bartlett_sphericity
from sklearn.metrics import adjusted_rand_score
import json
m = pd.read_csv(f'{DAT}/base82.csv'); OUT={}
X = m[VARS7].values; Z = zscore(X)
# ---- adecuación muestral ---------------------------------------------------------------------------
kmo_v, kmo_t = calculate_kmo(X); chi2, pbart = calculate_bartlett_sphericity(X)
OUT.update(kmo_total=float(kmo_t), bartlett_chi2=float(chi2), bartlett_p=float(pbart))
pd.DataFrame({'variable':[LAB7[v] for v in VARS7],'KMO':kmo_v}).to_csv(f'{TAB}/T03a_kmo.csv', index=False, encoding='utf-8-sig')
print('KMO total', round(kmo_t,3), '| Bartlett chi2', round(chi2,1), 'p', pbart)
# ---- solución base ---------------------------------------------------------------------------------
res = pca_varimax(Z, VARS7, k=2)
lam = res['lam']; pa_n_mean, pa_n_p95 = parallel_analysis(Z, 2000, seed=1); pa_p_mean, pa_p_p95 = parallel_analysis_perm(Z, 2000, seed=2)
eig = pd.DataFrame({'componente':[f'C{i+1}' for i in range(7)], 'autovalor':lam, 'pct_varianza':res['ratio']*100,
      'pct_acumulado':np.cumsum(res['ratio'])*100, 'PA_normal_media':pa_n_mean, 'PA_normal_p95':pa_n_p95, 'PA_perm_media':pa_p_mean, 'PA_perm_p95':pa_p_p95})
eig['retener_Kaiser']=np.where(eig.autovalor>=1,'Sí','No'); eig['retener_PA_p95']=np.where(eig.autovalor>eig.PA_normal_p95,'Sí','No')
eig.to_csv(f'{TAB}/T03b_autovalores_analisis_paralelo.csv', index=False, encoding='utf-8-sig'); print(eig.round(3).to_string(index=False))
OUT.update(eig1=float(lam[0]), eig2=float(lam[1]), eig3=float(lam[2]), var1=float(res['ratio'][0]*100), var2=float(res['ratio'][1]*100),
           var12=float(res['ratio'][:2].sum()*100), n_kaiser=int((lam>=1).sum()), n_pa=int((lam>pa_n_p95).sum()), n_pa_perm=int((lam>pa_p_p95).sum()))
# cargas
cargas = pd.DataFrame({'variable':[LAB7[v] for v in VARS7], 'C1_sin_rotar':res['L'][:,0], 'C2_sin_rotar':res['L'][:,1],
   'Eje_economico_rot':res['Lr'][:,0], 'Eje_seguridad_rot':res['Lr'][:,1], 'comunalidad':res['comm']})
# varianza explicada tras rotación (suma de cargas^2)
ss_rot = (res['Lr']**2).sum(0); OUT.update(ss_rot_econ=float(ss_rot[0]), ss_rot_sec=float(ss_rot[1]), pct_rot_econ=float(ss_rot[0]/7*100), pct_rot_sec=float(ss_rot[1]/7*100))
cargas.to_csv(f'{TAB}/T03c_cargas_comunalidades.csv', index=False, encoding='utf-8-sig'); print(cargas.round(3).to_string(index=False)); print('SS rotados', ss_rot.round(3))
# ---- puntajes y cuadrantes ---------------------------------------------------------------------------
S_raw = res['S']                                   # puntajes estandarizados no rotados (C1, C2)
# orientación de la versión original: C1 y C2 tal como en el informe v2 (PC1 + economía, PC2 + ISC)
pc1_o, pc2_o = m_orig = (pd.read_csv(f'{ENT}/ds2.csv')[['PC1','PC2']].values.T)
q_orig = pd.read_csv(f'{ENT}/ds2.csv')['cuadrante'].str[:2].values
e, s = res['Sr'][:,0], res['Sr'][:,1]; q_rot = quadrant(e, s)
# verificación: puntajes originales (no estandarizados) = S_raw * sqrt(lam)
# los puntajes originales (v2) se calcularon con z-score con ddof=0 → difieren de los actuales solo por el factor constante sqrt((n-1)/n)
assert abs(np.corrcoef(pc1_o, S_raw[:,0])[0,1])>0.999999 and abs(np.corrcoef(pc2_o, S_raw[:,1])[0,1])>0.999999
assert np.array_equal(quadrant(np.sign(np.corrcoef(pc1_o,S_raw[:,0])[0,1])*S_raw[:,0], np.sign(np.corrcoef(pc2_o,S_raw[:,1])[0,1])*S_raw[:,1]), q_orig)
tr = pd.crosstab(pd.Series(q_orig, name='Cuadrante original (sin rotar)'), pd.Series(q_rot, name='Cuadrante rotado'))
tr.to_csv(f'{TAB}/T04a_matriz_transicion.csv', encoding='utf-8-sig'); print(tr)
chg = (q_orig != q_rot)
OUT.update(n_cambian=int(chg.sum()), ari_rot_vs_orig=float(adjusted_rand_score(q_orig, q_rot)), pct_igual=float((~chg).mean()*100))
tabla = m[['cod_canton','canton','provincia','region_bccr']].copy()
tabla['E_rot']=e; tabla['S_rot']=s; tabla['C1_sin_rotar_std']=S_raw[:,0]; tabla['C2_sin_rotar_std']=S_raw[:,1]
tabla['cuadrante_original']=q_orig; tabla['cuadrante_rotado']=q_rot; tabla['cambia']=np.where(chg,'Sí','No')
tabla.to_csv(f'{TAB}/T04b_cuadrantes_canton_por_canton.csv', index=False, encoding='utf-8-sig')
print('Cantones que cambian de cuadrante:', chg.sum()); print(tabla[chg][['canton','cuadrante_original','cuadrante_rotado','E_rot','S_rot']].round(2).to_string(index=False))
print('Conteo original:', pd.Series(q_orig).value_counts().sort_index().to_dict(), '| rotado:', pd.Series(q_rot).value_counts().sort_index().to_dict())
OUT['n_q_orig']=pd.Series(q_orig).value_counts().sort_index().to_dict(); OUT['n_q_rot']=pd.Series(q_rot).value_counts().sort_index().to_dict()
# cantones cercanos a un umbral (|puntaje|<0.25): clasificación frágil
near = tabla[(tabla.E_rot.abs()<0.25)|(tabla.S_rot.abs()<0.25)]; OUT['n_frontera']=len(near)
near[['canton','E_rot','S_rot','cuadrante_rotado']].to_csv(f'{TAB}/T04c_cantones_frontera.csv', index=False, encoding='utf-8-sig')
print('Cantones frontera (|puntaje|<0.25):', len(near))
# comparación con la reconstrucción del informe v2 (puntajes no estandarizados × R estimada por MCO)
L_raw = res['L']; L_rot_free = res['Lr']
# --- la R del informe v2 se recuperó por MCO entre cargas sin rotar y rotadas; con puntajes NO estandarizados
Rv2,*_ = np.linalg.lstsq(L_raw, L_rot_free, rcond=None)
sc_v2 = (S_raw*np.sqrt(lam[:2])) @ Rv2
OUT['r_eje_seg_v2_vs_directo']=float(np.corrcoef(sc_v2[:,1], s)[0,1]); OUT['r_eje_seg_directo_ISC']=float(np.corrcoef(s, m.ISC_2025)[0,1]); OUT['r_eje_seg_v2_ISC']=float(np.corrcoef(sc_v2[:,1], m.ISC_2025)[0,1])
OUT['r_eje_econ_directo_ICC']=float(np.corrcoef(e, m.ICC_2024)[0,1])
print('corr eje seguridad directo vs ISC: %.3f | v2 vs ISC: %.3f | v2 vs directo %.3f' % (OUT['r_eje_seg_directo_ISC'], OUT['r_eje_seg_v2_ISC'], OUT['r_eje_seg_v2_vs_directo']))
print('corr eje económico vs ICC', round(OUT['r_eje_econ_directo_ICC'],3), '| corr(E,S)=', round(np.corrcoef(e,s)[0,1],4), '(ortogonal por construcción: puntajes estandarizados)')
# ---- estabilidad bootstrap de las cargas rotadas ------------------------------------------------------
B=2000; r=rng(31); Lb=np.empty((B,7,2)); tuck=np.empty((B,2)); VEb=np.empty(B)
for b in range(B):
    i = r.integers(0,82,82); Zb = zscore(X[i]); rb = pca_varimax(Zb, VARS7, 2); Lb[b]=rb['Lr']; VEb[b]=rb['ratio'][:2].sum()
    tuck[b]=[tucker(rb['Lr'][:,0],res['Lr'][:,0]), tucker(rb['Lr'][:,1],res['Lr'][:,1])]
bt = pd.DataFrame({'variable':[LAB7[v] for v in VARS7]})
for j,nm in enumerate(['econ','seg']):
    bt[f'carga_{nm}']=res['Lr'][:,j]; bt[f'ic_lo_{nm}']=np.percentile(Lb[:,:,j],2.5,0); bt[f'ic_hi_{nm}']=np.percentile(Lb[:,:,j],97.5,0)
bt.to_csv(f'{TAB}/T03d_cargas_bootstrap.csv', index=False, encoding='utf-8-sig'); print(bt.round(2).to_string(index=False))
OUT.update(tucker_econ_p05=float(np.percentile(tuck[:,0],5)), tucker_sec_p05=float(np.percentile(tuck[:,1],5)), tucker_econ_med=float(np.median(tuck[:,0])), tucker_sec_med=float(np.median(tuck[:,1])),
           var12_boot_lo=float(np.percentile(VEb,2.5)*100), var12_boot_hi=float(np.percentile(VEb,97.5)*100))
print('Tucker bootstrap mediana econ/seg: %.3f/%.3f; p5: %.3f/%.3f' % (OUT['tucker_econ_med'],OUT['tucker_sec_med'],OUT['tucker_econ_p05'],OUT['tucker_sec_p05']))
# ---- sensibilidad: escenarios de transformación / extremos / escenarios de año -----------------------------
def run_scenario(name, Xs, names=VARS7, idx=None, scale='z'):
    Zs = zscore(Xs) if scale=='z' else Xs
    rs = pca_varimax(Zs, names, 2); qs = quadrant(rs['Sr'][:,0], rs['Sr'][:,1]); return rs, qs
from scipy.stats import norm, rankdata
def inv_normal(x): return norm.ppf((rankdata(x)-0.5)/len(x))
scen={}
Xlog = X.copy(); Xlog[:,2]=np.log(Xlog[:,2]); scen['S1 · ln(PIB per cápita)'] = (Xlog, None)
scen['S2 · Transformación de rangos a normal (todas)'] = (np.column_stack([inv_normal(X[:,j]) for j in range(7)]), None)
lo,hi = np.percentile(X,5,0), np.percentile(X,95,0); scen['S3 · Winsorización 5/95 (todas)'] = (np.clip(X,lo,hi), None)
Xlog2 = X.copy(); Xlog2[:,[2,3,5]]=np.log(Xlog2[:,[2,3,5]]); scen['S4 · ln de PIB, UJ e IPM (asimétricas)'] = (Xlog2, None)
ext5 = m.canton.isin(['San José','Escazú','Santa Ana','Montes de Oca','Belén']).values
scen['S5 · Sin los 5 cantones extremos en UJ (San José, Escazú, Santa Ana, Montes de Oca, Belén)'] = (X[~ext5], ~ext5)
XB = m[['IDH_2024','ICC_2024','PIB_percapita_2022_pob2023','UJ_por_1000hab_2024_pob2023','ISC_2025','IPM_2024','IVDAC_2024']].values
okB = ~np.isnan(XB).any(1); scen['S6 · Población 2023 como denominador (PIB y UJ)'] = (XB[okB], okB)
XC = m[['IDH_2022','ICC_2023','PIB_percapita_2022_pob2023','UJ_por_1000hab_2022_pob2023','ISC_2022','IPM_2024','IVDAC_2022']].values
okC = ~np.isnan(XC).any(1); scen['S7 · Ventana 2022–2023 (IDH/ISC/IVDAC/UJ 2022, PIB 2022, ICC 2023, IPM 2024)'] = (XC[okC], okC)
rows=[]; scen_q={}
for nm,(Xs,idx) in scen.items():
    rs,qs = run_scenario(nm, Xs); sel = np.ones(82,bool) if idx is None else idx
    qb = q_rot[sel]; qo = q_orig[sel]
    row=dict(escenario=nm, n=int(sel.sum()), var_2comp=rs['ratio'][:2].sum()*100, tucker_econ=tucker(rs['Lr'][:,0],res['Lr'][:,0]), tucker_seg=tucker(rs['Lr'][:,1],res['Lr'][:,1]),
             pct_mismo_cuadrante_vs_rotado_base=(qs==qb).mean()*100, ARI_vs_rotado_base=adjusted_rand_score(qb,qs), n_Q3=int((qs=='Q3').sum()),
             jaccard_Q3_vs_Q3_rotado_base=len(set(np.where(qs=='Q3')[0])&set(np.where(qb=='Q3')[0]))/len(set(np.where(qs=='Q3')[0])|set(np.where(qb=='Q3')[0])))
    for j,v in enumerate(VARS7): row['Ce_'+v]=rs['Lr'][j,0]; row['Cs_'+v]=rs['Lr'][j,1]
    rows.append(row); scen_q[nm]=(sel,qs)
sens = pd.DataFrame(rows); sens.to_csv(f'{TAB}/T05_sensibilidad_pca.csv', index=False, encoding='utf-8-sig')
print(sens[['escenario','n','var_2comp','tucker_econ','tucker_seg','pct_mismo_cuadrante_vs_rotado_base','ARI_vs_rotado_base','n_Q3','jaccard_Q3_vs_Q3_rotado_base']].round(3).to_string(index=False))
# LOO por cantón
loo=[]
for i in range(82):
    keep = np.ones(82,bool); keep[i]=False; rs=pca_varimax(zscore(X[keep]), VARS7, 2); qs=quadrant(rs['Sr'][:,0],rs['Sr'][:,1])
    loo.append(dict(canton_excluido=m.canton[i], tucker_econ=tucker(rs['Lr'][:,0],res['Lr'][:,0]), tucker_seg=tucker(rs['Lr'][:,1],res['Lr'][:,1]),
                    n_cambian=int((qs!=q_rot[keep]).sum()), var_2comp=rs['ratio'][:2].sum()*100))
loo=pd.DataFrame(loo).sort_values('n_cambian',ascending=False); loo.to_csv(f'{TAB}/T05b_leave_one_out.csv', index=False, encoding='utf-8-sig')
print(loo.head(6).round(3).to_string(index=False)); print('LOO: tucker min econ/seg', loo.tucker_econ.min().round(4), loo.tucker_seg.min().round(4), '| max cambios', loo.n_cambian.max())
OUT.update(loo_tucker_min_econ=float(loo.tucker_econ.min()), loo_tucker_min_seg=float(loo.tucker_seg.min()), loo_max_cambios=int(loo.n_cambian.max()), loo_med_cambios=float(loo.n_cambian.median()))
# estabilidad de membresía de cuadrante por remuestreo (clasificación del cantón con soluciones bootstrap proyectadas)
B2=1000; r=rng(41); cnt = {k:np.zeros(82) for k in ['Q1','Q2','Q3','Q4']}
mu, sd = X.mean(0), X.std(0, ddof=1)
for b in range(B2):
    i = r.integers(0,82,82); Xb=X[i]; mub, sdb = Xb.mean(0), Xb.std(0,ddof=1); Zb=(Xb-mub)/sdb
    rb = pca_varimax(Zb, VARS7, 2); 
    # proyectar los 82 cantones con la solución bootstrap: S = Z_full V Λ^-1/2 R
    Zf = (X-mub)/sdb; Sb = Zf @ rb['V'][:,:2] / np.sqrt(rb['lam'][:2])
    Sb = Sb @ rb['R'] if False else None
    # reconstruir puntajes rotados con la matriz de pesos que dio lugar a Lr: W = V Λ^-1/2 R_ord; obtener R_ord de pca_varimax
    Sf = (Zf @ rb['V'][:,:2] / np.sqrt(rb['lam'][:2])) @ rb['R']
    qb = quadrant(Sf[:,0], Sf[:,1])
    for k in cnt: cnt[k] += (qb==k)
stab = pd.DataFrame({k:v/B2 for k,v in cnt.items()}); stab.insert(0,'canton',m.canton); stab['cuadrante_rotado']=q_rot
stab['prob_cuadrante_asignado']=[stab.loc[i, q_rot[i]] for i in range(82)]
stab.to_csv(f'{TAB}/T05c_estabilidad_cuadrante_bootstrap.csv', index=False, encoding='utf-8-sig')
OUT.update(n_estables_80=int((stab.prob_cuadrante_asignado>=0.8).sum()), n_inestables_60=int((stab.prob_cuadrante_asignado<0.6).sum()), prob_media=float(stab.prob_cuadrante_asignado.mean()))
print('Membresía bootstrap: prob media %.3f; ≥0.80: %d cantones; <0.60: %d' % (OUT['prob_media'],OUT['n_estables_80'],OUT['n_inestables_60']))
# guardar objetos
tabla.to_csv(f'{DAT}/cuadrantes.csv', index=False, encoding='utf-8-sig')
json.dump(OUT, open(f'{TAB}/_pca_resumen.json','w'), indent=1, default=lambda o: o if not hasattr(o,'item') else o.item())
