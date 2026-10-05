# -*- coding: utf-8 -*-
"""Revision metodologica: Tabla 5 (inferencia), descriptivos, PCA (principal y log), K-means k=2..8, cuadrantes varimax."""
import numpy as np, pandas as pd, json, warnings, sklearn, scipy
from scipy import stats
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score, calinski_harabasz_score, davies_bouldin_score, adjusted_rand_score
from factor_analyzer.factor_analyzer import calculate_kmo, calculate_bartlett_sphericity
from factor_analyzer.rotator import Rotator
import scikit_posthocs as sp
from common import *
warnings.filterwarnings('ignore')
O=f'{W}/out'
SEED_PERM=20260819; SEED_BOOT=20260820; SEED_PA=20260821; SEED_KM=20260822
VARS=['IDH_2024','ICC_2024','PIB_percapita_2022','UJ_por_1000hab_2024','ISC_2025','IPM_2024','IVDAC_2024']
SHORT=['IDH','ICC','PIB pc','UJ/1.000','ISC','IPM','IVDAC']
full=full.copy()
A=full[full.ICC_2024.notna()].reset_index(drop=True)  # n=82
assert len(A)==82
# =============== 1. TABLA 5 ===============
ext=[('PIB_percapita_2022','PIB per cápita'),('ICC_2024','ICC'),('UJ_por_1000hab_2024','UJ/1.000 hab.'),('IPM_2024','IPM')]
rng=np.random.default_rng(SEED_PERM); B=1999; rb=np.random.default_rng(SEED_BOOT); NB=5000
rows=[]
for v,lab in ext:
    s=full[['IDH_cat',v]].dropna(); x=s.IDH_cat.values.astype(float); y=s[v].values; n=len(s)
    rho=stats.spearmanr(x,y)[0]
    ry=stats.rankdata(y); rx=stats.rankdata(x)
    # permutación: se permutan los rangos de y; estadístico = rho (bilateral, |rho|)
    def r_of(a,b): return np.corrcoef(a,b)[0,1]
    obs=abs(r_of(rx,ry)); cnt=0
    for _ in range(B):
        if abs(r_of(rx,rng.permutation(ry)))>=obs-1e-12: cnt+=1
    p=(cnt+1)/(B+1)
    # bootstrap de cantones
    bs=[]
    for _ in range(NB):
        idx=rb.integers(0,n,n)
        xb,yb=x[idx],y[idx]
        if np.ptp(xb)==0 or np.ptp(yb)==0: continue
        bs.append(stats.spearmanr(xb,yb)[0])
    lo,hi=np.percentile(bs,[2.5,97.5])
    groups=[g[v].values for _,g in s.groupby('IDH_cat')]
    H,pk=stats.kruskal(*groups); eps2=H/(n-1)
    rows.append(dict(variable=v,label=lab,n=n,rho=rho,ci_lo=lo,ci_hi=hi,n_boot_valid=len(bs),b_extremos=cnt,p_perm=p,H=H,p_kw=pk,eps2=eps2,gl=len(groups)-1,tamanos=[len(g) for g in groups]))
t5=pd.DataFrame(rows)
# BH solo sobre los 4 p de permutación
p=t5.p_perm.values; o=np.argsort(p); m=len(p); q=np.empty(m); prev=1
for rank,i in list(enumerate(o,1))[::-1]:
    prev=min(prev,p[i]*m/rank); q[i]=prev
t5['q_fdr']=q
t5.to_csv(f'{O}/T5_validacion_externa.csv',index=False,encoding='utf-8-sig')
print(t5.drop(columns=['tamanos']).round(5).to_string())
print(t5.tamanos.tolist())
# Dunn (planificadas): Bajo-Medio, Medio-Alto, Alto-MuyAlto, Bajo-MuyAlto ; Muy bajo (n=1) excluido de contrastes
dun=[]
for v,lab in ext:
    s=full[['IDH_cat',v]].dropna().copy(); s['g']=s.IDH_cat.astype(int)
    P=sp.posthoc_dunn(s,val_col=v,group_col='g',p_adjust=None)
    pairs=[(1,2),(2,3),(3,4),(1,4)]
    ps=np.array([P.loc[a,b] for a,b in pairs]); 
    # Holm sobre las 4 comparaciones planificadas, dentro de la variable
    oo=np.argsort(ps); adj=np.empty(4); run=0
    for k,i in enumerate(oo): run=max(run,(4-k)*ps[i]); adj[i]=min(1,run)
    for (a,b),pr,pa in zip(pairs,ps,adj):
        ma=s[s.g==a][v].median(); mb=s[s.g==b][v].median()
        dun.append(dict(variable=v,par=f'{CATS[a]} vs {CATS[b]}',p_dunn=pr,p_holm=pa,mediana_a=ma,mediana_b=mb,n_a=int((s.g==a).sum()),n_b=int((s.g==b).sum())))
dun=pd.DataFrame(dun); dun.to_csv(f'{O}/T5b_dunn_planificado.csv',index=False,encoding='utf-8-sig'); print(dun.round(4).to_string())
# medianas por categoría (apoyo)
med=full.groupby('IDH_cat')[['PIB_percapita_2022','ICC_2024','UJ_por_1000hab_2024','IPM_2024']].agg(['count','median']).round(3); print(med)

# =============== 2. DESCRIPTIVOS ===============
def desc(df):
    r=pd.DataFrame({'media':df.mean(),'de':df.std(),'min':df.min(),'q1':df.quantile(.25),'mediana':df.median(),'q3':df.quantile(.75),'max':df.max()})
    r['ric']=r.q3-r.q1; r['asim']=df.skew(); r['curt']=df.kurt(); r['cv']=r.de/r.media*100; return r
D=desc(A[VARS]); D.to_csv(f'{O}/T6_descriptivos.csv',encoding='utf-8-sig'); print(D.round(3))
# extremos: fences de Tukey y z robusto
ext_rows=[]
for v in VARS:
    s=A[v]; q1,q3=s.quantile(.25),s.quantile(.75); iqr=q3-q1; lo,hi=q1-1.5*iqr,q3+1.5*iqr
    mad=np.median(np.abs(s-s.median()))*1.4826
    for i in s.index[(s<lo)|(s>hi)]:
        ext_rows.append(dict(variable=v,canton=A.canton[i],valor=s[i],z_robusto=(s[i]-s.median())/mad,lado='alto' if s[i]>hi else 'bajo'))
EX=pd.DataFrame(ext_rows); EX.to_csv(f'{O}/T6b_extremos_tukey.csv',index=False,encoding='utf-8-sig'); print(EX.groupby('variable').size()); print(EX.sort_values('z_robusto',ascending=False).head(15).round(2))
# =============== 3. ESPECIFICACIONES ===============
def spec_matrix(kind):
    X=A[VARS].copy()
    if kind=='log':
        X['PIB_percapita_2022']=np.log(X['PIB_percapita_2022']); X['UJ_por_1000hab_2024']=np.log(X['UJ_por_1000hab_2024'])
    Z=pd.DataFrame(StandardScaler().fit_transform(X),columns=VARS)  # ddof=0 como en analisis.py
    return X,Z
print('skew log:',pd.Series({v:stats.skew(np.log(A[v]),bias=False) for v in ['PIB_percapita_2022','UJ_por_1000hab_2024']}))
def parallel(Z,B=2000,seed=SEED_PA):
    r=np.random.default_rng(seed); n,p=Z.shape; X=Z.values
    perm=np.empty((B,p)); norm=np.empty((B,p))
    for b in range(B):
        Xp=np.column_stack([r.permutation(X[:,j]) for j in range(p)])
        perm[b]=np.sort(np.linalg.eigvalsh(np.corrcoef(Xp,rowvar=False)))[::-1]
        Xn=r.standard_normal((n,p)); norm[b]=np.sort(np.linalg.eigvalsh(np.corrcoef(Xn,rowvar=False)))[::-1]
    return perm,norm
res={}
for kind in ['principal','log']:
    X,Z=spec_matrix(kind); R=np.corrcoef(Z.values,rowvar=False)
    ev=np.sort(np.linalg.eigvalsh(R))[::-1]
    pca=PCA().fit(Z.values); assert np.allclose(pca.explained_variance_*(81/82)*82/81, pca.explained_variance_)
    eig=pca.explained_variance_; # ddof=1 en sklearn; autovalores de R: ev
    kmo_v,kmo_all=calculate_kmo(Z.values); chi,pb=calculate_bartlett_sphericity(Z.values)
    perm,norm=parallel(Z)
    pa95=np.percentile(perm,95,axis=0); pamean=perm.mean(0); pn95=np.percentile(norm,95,axis=0)
    k_kaiser=int((ev>=1).sum()); k_pa=int((ev>pa95).sum()); k_pan=int((ev>pn95).sum())
    # sin rotar (autovectores de R)
    w,V=np.linalg.eigh(R); o=np.argsort(w)[::-1]; w,V=w[o],V[:,o]
    k=2
    L=V[:,:k]*np.sqrt(w[:k])
    # signo: igual que sklearn (svd_flip) para reproducir
    comps=pca.components_[:k].T
    for j in range(k):
        if np.sign(comps[np.argmax(np.abs(comps[:,j])),j])!=np.sign(V[np.argmax(np.abs(V[:,j])),j]) : V[:,j]*=-1
    L=V[:,:k]*np.sqrt(w[:k])
    Sstd=Z.values@V[:,:k]/np.sqrt(w[:k])         # puntajes estandarizados sin rotar
    rot=Rotator(method='varimax',normalize=False); Lr=rot.fit_transform(L)
    Lr_kn=Rotator(method='varimax',normalize=True).fit_transform(L); T=np.linalg.pinv(L)@Lr
    # signos para interpretación: PC1 rot positivo en ICC; PC2 rot positivo en ISC
    sg=np.array([np.sign(Lr[1,0]),np.sign(Lr[4,1])]); Lr=Lr*sg; T=T*sg
    Sr=Sstd@T
    h2=(L**2).sum(1)
    # MAP de Velicer
    def vmap(R):
        w_,V_=np.linalg.eigh(R); o_=np.argsort(w_)[::-1]; w_,V_=w_[o_],V_[:,o_]; out=[]
        for m in range(0,len(w_)-1):
            if m==0: C=R.copy()
            else:
                A_=V_[:,:m]*np.sqrt(w_[:m]); C=R-A_@A_.T
            d_=np.sqrt(np.diag(C)); P=C/np.outer(d_,d_); off=P[np.triu_indices_from(P,1)]; out.append(np.mean(off**2))
        return np.array(out)
    mapv=vmap(R); k_map=int(np.argmin(mapv))
    p_pa2=(1+(perm[:,1]>=ev[1]).sum())/(len(perm)+1); p_pa1=(1+(perm[:,0]>=ev[0]).sum())/(len(perm)+1); p90=np.percentile(perm,90,axis=0)
    res[kind]=dict(mapv=mapv,k_map=k_map,p_pa=[p_pa1,p_pa2],pa90=p90,Lr_kn=Lr_kn,perm=perm,X=X,Z=Z,R=R,ev=ev,pa95=pa95,pamean=pamean,pn95=pn95,kmo_v=kmo_v,kmo=kmo_all,chi=chi,pb=pb,k_kaiser=k_kaiser,k_pa=k_pa,k_pan=k_pan,L=L,Lr=Lr,T=T,Sstd=Sstd,Sr=Sr,h2=h2,V=V,w=w)
    print(f'\n=== {kind} === ev={np.round(ev,3)} %var={np.round(ev/7*100,2)} cum2={ev[:2].sum()/7*100:.2f}')
    print('PA95 perm',np.round(pa95,3),'mean',np.round(pamean,3),'PA95 norm',np.round(pn95,3))
    print('Kaiser',k_kaiser,'PA(perm)',k_pa,'PA(norm)',k_pan,'KMO',round(kmo_all,3),dict(zip(SHORT,np.round(kmo_v,3))),'Bartlett chi2',round(chi,2),'p',pb, 'gl',21)
    print('MAP',np.round(mapv,4),'k_MAP',k_map,'p_PA lambda1,lambda2',p_pa1,p_pa2,'PA90',np.round(p90,3));print('L\n',pd.DataFrame(L,index=SHORT).round(3).T); print('Lr\n',pd.DataFrame(Lr,index=SHORT).round(3).T); print('h2',np.round(h2,3))
    print('Lr Kaiser-norm\n',pd.DataFrame(Lr_kn*sg,index=SHORT).round(3).T);print('var rotada',np.round((Lr**2).sum(0)/7*100,2))
import pickle; pickle.dump(dict(res=res,A=A,VARS=VARS,SHORT=SHORT,t5=t5,dun=dun),open(f'{O}/res.pkl','wb'))
