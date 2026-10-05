# -*- coding: utf-8 -*-
"""FASE 2 (parte 1) · Descriptivos ampliados y correlaciones Pearson/Spearman con IC bootstrap y FDR (familia F1: 21 pares)."""
from common import *
m = pd.read_csv(f'{DAT}/base82.csv')
# ---------- descriptivos: media, DE, mediana, IQR, min, max, asimetría, CV, Shapiro ---------------
rows=[]
for v in VARS7:
    x = m[v]; q1,q3 = x.quantile([.25,.75])
    rows.append(dict(variable=LAB7[v], n=len(x), media=x.mean(), de=x.std(), mediana=x.median(), q1=q1, q3=q3, iqr=q3-q1,
                     minimo=x.min(), maximo=x.max(), asimetria=stats.skew(x, bias=False), curtosis=stats.kurtosis(x, bias=False),
                     cv_pct=x.std()/x.mean()*100, shapiro_p=stats.shapiro(x)[1]))
desc = pd.DataFrame(rows); desc.to_csv(f'{TAB}/T01_descriptivos.csv', index=False, encoding='utf-8-sig'); print(desc.round(3).to_string(index=False))
# valores extremos (Tukey) por variable
ext=[]
for v in VARS7:
    x=m[v]; q1,q3=x.quantile([.25,.75]); lo,hi=q1-1.5*(q3-q1), q3+1.5*(q3-q1)
    out = m.loc[(x<lo)|(x>hi),'canton'].tolist(); ext.append((LAB7[v], len(out), '; '.join(out)))
pd.DataFrame(ext, columns=['variable','n_extremos_tukey','cantones']).to_csv(f'{TAB}/T01b_extremos_tukey.csv', index=False, encoding='utf-8-sig')
print(pd.DataFrame(ext).to_string(index=False))
# ---------- correlaciones: 21 pares ---------------------------------------------------------------
rows=[]
for i,a in enumerate(VARS7):
    for b in VARS7[i+1:]:
        x,y = m[a].values, m[b].values
        rp,pp = stats.pearsonr(x,y); rs,ps = stats.spearmanr(x,y)
        lpib = lambda v: np.log(m[v].values) if v=='PIB_percapita_2022' else m[v].values
        rpl,_ = stats.pearsonr(lpib(a), lpib(b))
        ci_p = corr_boot(x,y,'pearson',seed=11); ci_s = corr_boot(x,y,'spearman',seed=12)
        # Fisher IC como contraste
        z = np.arctanh(rp); se=1/np.sqrt(len(x)-3); ci_f = np.tanh([z-1.96*se, z+1.96*se])
        rows.append(dict(var1=LAB7[a], var2=LAB7[b], r_pearson=rp, ic_lo=ci_p[0], ic_hi=ci_p[1], p_pearson=pp,
                         rho_spearman=rs, rho_lo=ci_s[0], rho_hi=ci_s[1], p_spearman=ps, r_pearson_logPIB=rpl,
                         fisher_lo=ci_f[0], fisher_hi=ci_f[1]))
c = pd.DataFrame(rows)
c['q_fdr_pearson'] = bh_fdr(c.p_pearson); c['q_fdr_spearman'] = bh_fdr(c.p_spearman)
c['umbral_0_30'] = np.where(c.r_pearson.abs()>=0.30,'Sí','No')
c['signif_q05'] = np.where(c.q_fdr_pearson<0.05,'Sí','No')
c = c.reindex(c.r_pearson.abs().sort_values(ascending=False).index).reset_index(drop=True)
c.to_csv(f'{TAB}/T02_correlaciones_21_pares.csv', index=False, encoding='utf-8-sig')
print(c[['var1','var2','r_pearson','ic_lo','ic_hi','p_pearson','q_fdr_pearson','rho_spearman','r_pearson_logPIB']].round(3).to_string(index=False))
print('pares |r|>=0.30:', (c.r_pearson.abs()>=.3).sum(), '| de ellos con q<0.05:', ((c.r_pearson.abs()>=.3)&(c.q_fdr_pearson<.05)).sum(), '| pares con q<0.05:', (c.q_fdr_pearson<.05).sum())
# matrices
m[VARS7].corr('pearson').to_csv(f'{TAB}/T02b_matriz_pearson.csv', encoding='utf-8-sig'); m[VARS7].corr('spearman').to_csv(f'{TAB}/T02c_matriz_spearman.csv', encoding='utf-8-sig')
