# -*- coding: utf-8 -*-
"""FASE 5 · Ejercicio 2 recalculado: Q3 (rotado) vs resto; FDR; IC bootstrap; TOST; ajustes por densidad/región; modelos de error espacial;
leave-one-domain-out (sin ICC, sin IVDAC, sin ISC); panel interno vs externo para el eje de seguridad."""
from common import *
from pca_lib import *
from spatial_lib import *
import statsmodels.api as sm, statsmodels.formula.api as smf
from spreg import ML_Error
from sklearn.metrics import adjusted_rand_score
import json
m = pd.read_csv(f'{DAT}/base82.csv'); cu = pd.read_csv(f'{DAT}/cuadrantes.csv'); w,_ = build_W(m); OUT={}
assert (m.cod_canton.values==cu.cod_canton.values).all()
m['E']=cu.E_rot.values; m['S']=cu.S_rot.values; m['q_rot']=cu.cuadrante_rotado.values; m['q_orig']=cu.cuadrante_original.values
# ---------------- variantes de definición de Q3 -----------------------------------------------
X = m[VARS7].values
def lodo(drop, ref_econ='ICC_2024', ref_sec='ISC_2025', sec_sign=1):
    keep=[v for v in VARS7 if v not in drop]; Xs=m[keep].values; rs=pca_varimax(zscore(Xs), keep, 2, ref_econ, ref_sec, sec_sign)
    return keep, rs, quadrant(rs['Sr'][:,0], rs['Sr'][:,1])
vars_L1, r1, q1 = lodo(['ICC_2024'], ref_econ='UJ_por_1000hab_2024')                 # sin ICC
vars_L2, r2, q2 = lodo(['IVDAC_2024'])                                                  # sin IVDAC
vars_L3, r3, q3 = lodo(['ISC_2025'], ref_sec='IVDAC_2024', sec_sign=-1)                 # sin ISC
for nm,(vv,rs,qq) in {'L1 sin ICC':(vars_L1,r1,q1),'L2 sin IVDAC':(vars_L2,r2,q2),'L3 sin ISC':(vars_L3,r3,q3)}.items():
    print(nm, '| var 2 comp: %.1f%%' % (rs['ratio'][:2].sum()*100), '| Q3 n=%d' % (qq=='Q3').sum(), '| ARI vs Q rot base: %.3f' % adjusted_rand_score(m.q_rot, qq))
    print(pd.DataFrame(rs['Lr'], index=vv, columns=['E','S']).round(2).T.to_string())
m['E_L1']=r1['Sr'][:,0]; m['S_L1']=r1['Sr'][:,1]; m['q_L1']=q1; m['E_L2']=r2['Sr'][:,0]; m['S_L2']=r2['Sr'][:,1]; m['q_L2']=q2; m['E_L3']=r3['Sr'][:,0]; m['S_L3']=r3['Sr'][:,1]; m['q_L3']=q3
m['Q3_rot']=(m.q_rot=='Q3').astype(int); m['Q3_orig']=(m.q_orig=='Q3').astype(int); m['Q3_L1']=(m.q_L1=='Q3').astype(int)
OUT.update(n_Q3_rot=int(m.Q3_rot.sum()), n_Q3_orig=int(m.Q3_orig.sum()), n_Q3_L1=int(m.Q3_L1.sum()),
           jacc_Q3_rot_L1=float(((m.Q3_rot==1)&(m.Q3_L1==1)).sum()/((m.Q3_rot==1)|(m.Q3_L1==1)).sum()), jacc_Q3_rot_orig=float(((m.Q3_rot==1)&(m.Q3_orig==1)).sum()/((m.Q3_rot==1)|(m.Q3_orig==1)).sum()),
           inter_Q3_rot_orig=int(((m.Q3_rot==1)&(m.Q3_orig==1)).sum()), inter_Q3_rot_L1=int(((m.Q3_rot==1)&(m.Q3_L1==1)).sum()),
           ARI_rot_L1=float(adjusted_rand_score(m.q_rot,m.q_L1)), ARI_rot_L2=float(adjusted_rand_score(m.q_rot,m.q_L2)), ARI_rot_L3=float(adjusted_rand_score(m.q_rot,m.q_L3)),
           var2_L1=float(r1['ratio'][:2].sum()*100), var2_L2=float(r2['ratio'][:2].sum()*100), var2_L3=float(r3['ratio'][:2].sum()*100),
           r_S_L2_ISC=float(np.corrcoef(m.S_L2,m.ISC_2025)[0,1]), r_S_L3_IVDAC=float(np.corrcoef(m.S_L3,m.IVDAC_2024)[0,1]), r_S_base_S_L1=float(np.corrcoef(m.S,m.S_L1)[0,1]),
           r_E_base_E_L1=float(np.corrcoef(m.E,m.E_L1)[0,1]), r_S_base_S_L2=float(np.corrcoef(m.S,m.S_L2)[0,1]), r_S_base_S_L3=float(np.corrcoef(m.S,m.S_L3)[0,1]))
print(OUT)
m[['cod_canton','canton','E','S','q_rot','q_orig','E_L1','S_L1','q_L1','E_L2','S_L2','q_L2','E_L3','S_L3','q_L3']].to_csv(f'{TAB}/T07_ejes_y_cuadrantes_lodo.csv', index=False, encoding='utf-8-sig')
# ---------------- comparación de grupos: Q3 vs resto ---------------------------------------------------
def rb_from_u(u, n1, n2): return 2*u/(n1*n2) - 1                        # >0: Q3 tiende a valores mayores
def hl_shift(a,b): return float(np.median((a[:,None]-b[None,:]).ravel()))
def compare(df, flag, vars_, labels, family, seed=0, margin=0.5, B=B_BOOT):
    rows=[]; a_idx = np.where(df[flag].values==1)[0]; b_idx = np.where(df[flag].values==0)[0]
    for j,v in enumerate(vars_):
        x = df[v].values; a=x[a_idx]; b=x[b_idx]; n1,n2=len(a),len(b)
        u,p = stats.mannwhitneyu(a,b,alternative='two-sided', method='asymptotic'); rb = rb_from_u(u,n1,n2)
        sp = np.sqrt(((n1-1)*a.var(ddof=1)+(n2-1)*b.var(ddof=1))/(n1+n2-2)); d=(a.mean()-b.mean())/sp
        rr = rng(seed*100+j); hl=np.empty(B); rbb=np.empty(B); db=np.empty(B)
        for t in range(B):
            ia=rr.choice(a_idx,n1); ib=rr.choice(b_idx,n2); aa=x[ia]; bb=x[ib]; uu=stats.mannwhitneyu(aa,bb,alternative='two-sided',method='asymptotic')[0]
            rbb[t]=rb_from_u(uu,n1,n2); hl[t]=np.median(aa)-np.median(bb)
            spb=np.sqrt(((n1-1)*aa.var(ddof=1)+(n2-1)*bb.var(ddof=1))/(n1+n2-2)); db[t]=(aa.mean()-bb.mean())/spb if spb>0 else np.nan
        # TOST (Welch) sobre diferencia estandarizada: H0: |d|>=margin
        se = np.sqrt(a.var(ddof=1)/n1 + b.var(ddof=1)/n2); dfw = se**4/((a.var(ddof=1)/n1)**2/(n1-1)+(b.var(ddof=1)/n2)**2/(n2-1)); diff=a.mean()-b.mean(); dm = margin*sp
        p_low = 1-stats.t.cdf((diff+dm)/se, dfw); p_up = stats.t.cdf((diff-dm)/se, dfw); p_tost = max(p_low,p_up)
        ci90 = np.nanpercentile(db,[5,95])
        rows.append(dict(familia=family, variable=labels[v], clave=v, n_Q3=n1, n_resto=n2, med_Q3=np.median(a), q1_Q3=np.percentile(a,25), q3_Q3=np.percentile(a,75), med_resto=np.median(b), q1_resto=np.percentile(b,25), q3_resto=np.percentile(b,75),
                         dif_medianas=np.median(a)-np.median(b), dif_med_lo=np.percentile(hl,2.5), dif_med_hi=np.percentile(hl,97.5), HL=hl_shift(a,b),
                         U=u, p_mw=p, rb=rb, rb_lo=np.percentile(rbb,2.5), rb_hi=np.percentile(rbb,97.5), d=d, d_lo=np.nanpercentile(db,2.5), d_hi=np.nanpercentile(db,97.5),
                         d_ic90_lo=ci90[0], d_ic90_hi=ci90[1], p_tost=p_tost, equiv_margen=margin, equivalente=('Sí' if p_tost<0.05 else 'No concluyente')))
    t = pd.DataFrame(rows); t['q_fdr']=bh_fdr(t.p_mw); t['signif_fdr']=np.where(t.q_fdr<0.05,'Sí','No'); return t
INF = compare(m,'Q3_rot',INFRA,LAB_INFRA,'F2 · Infraestructura y conectividad (8)',seed=1)
PLR = compare(m,'Q3_rot',PIL,LAB_PIL,'F3 · Pilares del ICC (7)',seed=2)
INF_o = compare(m,'Q3_orig',INFRA,LAB_INFRA,'F2 · Q3 original (sin rotar)',seed=3,B=2000); PLR_o = compare(m,'Q3_orig',PIL,LAB_PIL,'F3 · Q3 original (sin rotar)',seed=4,B=2000)
INF_1 = compare(m,'Q3_L1',INFRA,LAB_INFRA,'F2 · Q3 definido sin ICC',seed=5,B=2000); PLR_1 = compare(m,'Q3_L1',PIL,LAB_PIL,'F3 · Q3 definido sin ICC',seed=6,B=2000)
for nm,t in [('T08a_q3rot_vs_resto_infraestructura',INF),('T08b_q3rot_vs_resto_pilares',PLR),('T08c_q3orig_vs_resto_infraestructura',INF_o),('T08d_q3orig_vs_resto_pilares',PLR_o),('T08e_q3sinICC_vs_resto_infraestructura',INF_1),('T08f_q3sinICC_vs_resto_pilares',PLR_1)]:
    t.to_csv(f'{TAB}/{nm}.csv', index=False, encoding='utf-8-sig')
cols=['variable','med_Q3','med_resto','dif_medianas','dif_med_lo','dif_med_hi','rb','rb_lo','rb_hi','p_mw','q_fdr','d','p_tost','equivalente']
print(INF[cols].round(3).to_string(index=False)); print(PLR[cols].round(3).to_string(index=False))
print('--- Q3 original'); print(INF_o[['variable','dif_medianas','rb','p_mw','q_fdr']].round(3).to_string(index=False)); print(PLR_o[['variable','dif_medianas','rb','p_mw','q_fdr']].round(3).to_string(index=False))
print('--- Q3 sin ICC'); print(INF_1[['variable','dif_medianas','rb','p_mw','q_fdr']].round(3).to_string(index=False)); print(PLR_1[['variable','dif_medianas','rb','p_mw','q_fdr']].round(3).to_string(index=False))
# ---------------- densidad: ¿mide cobertura o dispersión? ----------------------------------------------
dens = []
for v in INFRA:
    rs,ps = stats.spearmanr(m[v], m.ln_densidad_pob_2024); rp,pp = stats.pearsonr(m[v], m.ln_densidad_pob_2024)
    dens.append(dict(variable=LAB_INFRA[v], rho_vs_ln_densidad_poblacional=rs, p=ps, r_pearson=rp))
dens=pd.DataFrame(dens); dens.to_csv(f'{TAB}/T09_infra_vs_densidad_poblacional.csv', index=False, encoding='utf-8-sig'); print(dens.round(3).to_string(index=False))
q3 = m.Q3_rot==1
OUT.update(med_dens_Q3=float(m.loc[q3,'densidad_pob_2024'].median()), med_dens_resto=float(m.loc[~q3,'densidad_pob_2024'].median()),
           rho_densQ3=float(stats.spearmanr(m.Q3_rot, m.ln_densidad_pob_2024)[0]), pdensQ3=float(stats.mannwhitneyu(m.loc[q3,'ln_densidad_pob_2024'], m.loc[~q3,'ln_densidad_pob_2024'])[1]))
# ---------------- modelos ajustados: indicador (z) ~ Q3 + ln densidad + región (HC3) y SEM ------------------------------
def adjusted(df, flag, vars_, labels, family, use_density=True):
    rows=[]; wl = w
    for v in vars_:
        y=(df[v]-df[v].mean())/df[v].std(ddof=1); d=df.assign(y=y)
        f = 'y ~ ' + flag + (' + ln_densidad_pob_2024' if use_density else '') + ' + C(region_bccr)'
        ols = smf.ols(f, d).fit(cov_type='HC3'); b=ols.params[flag]; ci=ols.conf_int().loc[flag]; p=ols.pvalues[flag]
        # SEM (error espacial) con las mismas covariables
        Xm = pd.get_dummies(d[['region_bccr']], drop_first=True).astype(float); 
        Xm.insert(0, flag, d[flag].astype(float)); 
        if use_density: Xm.insert(1,'ln_dens', d.ln_densidad_pob_2024.values)
        try:
            sem = ML_Error(y.values.reshape(-1,1), Xm.values, w=wl, name_y='y', name_x=list(Xm.columns)); bs=sem.betas[1][0]; se_s=np.sqrt(sem.vm[1,1]); ps=2*(1-stats.norm.cdf(abs(bs/se_s))); lam=float(sem.lam)
        except Exception as ex: bs=se_s=ps=lam=np.nan
        # Moran de residuos OLS
        from esda import Moran
        mi = Moran(ols.resid.values, wl, permutations=999, seed=SEED) if False else Moran(np.asarray(ols.resid), wl, permutations=2999)
        rows.append(dict(familia=family, variable=labels[v], beta_Q3_sd=b, lo=ci[0], hi=ci[1], p_ols=p, beta_sem=bs, lo_sem=bs-1.96*se_s, hi_sem=bs+1.96*se_s, p_sem=ps, lambda_sem=lam, moran_resid=mi.I, p_moran_resid=mi.p_sim))
    t=pd.DataFrame(rows); t['q_ols']=bh_fdr(t.p_ols); t['q_sem']=bh_fdr(t.p_sem.fillna(1)); return t
np.random.seed(SEED)
ADJ_I = adjusted(m,'Q3_rot',INFRA,LAB_INFRA,'F2'); ADJ_P = adjusted(m,'Q3_rot',PIL,LAB_PIL,'F3')
ADJ_I.to_csv(f'{TAB}/T10a_ajustado_infra.csv', index=False, encoding='utf-8-sig'); ADJ_P.to_csv(f'{TAB}/T10b_ajustado_pilares.csv', index=False, encoding='utf-8-sig')
print(ADJ_I.round(3).to_string(index=False)); print(ADJ_P.round(3).to_string(index=False))
# sin controlar densidad (solo región) para aislar el papel de la densidad
ADJ_I0 = adjusted(m,'Q3_rot',INFRA,LAB_INFRA,'F2 (solo región)', use_density=False); ADJ_I0.to_csv(f'{TAB}/T10c_ajustado_infra_solo_region.csv', index=False, encoding='utf-8-sig')
# ---------------- Panel de correlaciones con el eje de seguridad: interno vs externo -----------------------------------
def corr_panel(axis, comps, labels, family, seed):
    rows=[]
    for j,v in enumerate(comps):
        x=m[v].values; y=m[axis].values; r,p=stats.pearsonr(x,y); rs,ps=stats.spearmanr(x,y); ci=corr_boot(x,y,'pearson',B=B_BOOT,seed=seed*10+j)
        rows.append(dict(familia=family, variable=labels[v], r=r, lo=ci[0], hi=ci[1], p=p, rho=rs, p_rho=ps, n=len(x)))
    t=pd.DataFrame(rows); t['q_fdr']=bh_fdr(t.p); return t
comps = PIL+IVC; LAB_ALL={**LAB_PIL, **LAB_IVC}
PA = corr_panel('S', comps, LAB_ALL, 'A · Descomposición interna: eje de seguridad (ISC, IVDAC, ICC… entran al PCA)', 7)
# Panel B: correlaciones con ejes que EXCLUYEN la familia del componente
rowsB=[]
pb_icc = corr_panel('S_L1', PIL, LAB_PIL, 'B1 · Pilares ICC vs eje de seguridad construido SIN ICC', 8)
pb_iv  = corr_panel('S_L2', IVC, LAB_IVC, 'B2 · Componentes IVDAC vs eje de seguridad construido SIN IVDAC', 9)
PB = pd.concat([pb_icc,pb_iv]); PB['q_fdr']=np.concatenate([bh_fdr(pb_icc.p), bh_fdr(pb_iv.p)])
PA.to_csv(f'{TAB}/T11a_panelA_interno.csv', index=False, encoding='utf-8-sig'); PB.to_csv(f'{TAB}/T11b_panelB_externo.csv', index=False, encoding='utf-8-sig')
# ISC con el eje sin ISC y sin IVDAC
for nm,ax in [('ISC vs eje (sin ISC)','S_L3')]:
    r,p=stats.pearsonr(m.ISC_2025, m[ax]); print(nm, round(r,3)); OUT['r_ISC_S_L3']=float(r)
print(PA[['variable','r','lo','hi','p','q_fdr']].round(3).to_string(index=False)); print(PB[['familia','variable','r','lo','hi','p','q_fdr']].round(3).to_string(index=False))
# correlaciones con el eje económico (baseline y sin ICC)
rowsE=[]
for j,v in enumerate(PIL):
    for ax,lab in [('E','Eje económico (con ICC)'),('E_L1','Eje económico (sin ICC)')]:
        r,p=stats.pearsonr(m[v],m[ax]); rowsE.append(dict(pilar=LAB_PIL[v], eje=lab, r=r, p=p))
pd.DataFrame(rowsE).to_csv(f'{TAB}/T11c_pilares_vs_eje_economico.csv', index=False, encoding='utf-8-sig')
m.to_csv(f'{DAT}/base82_con_ejes.csv', index=False, encoding='utf-8-sig')
json.dump(OUT, open(f'{TAB}/_ej2_resumen.json','w'), indent=1, default=lambda o: o if not hasattr(o,'item') else o.item())
