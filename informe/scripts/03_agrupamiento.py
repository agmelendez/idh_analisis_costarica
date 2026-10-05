# -*- coding: utf-8 -*-
"""FASE 4 · Agrupamiento exploratorio: k=2..8 (silhouette, Calinski-Harabasz, Davies-Bouldin), estabilidad bootstrap (Jaccard),
sensibilidad a transformaciones, jerárquico con distancia de Gower, y concordancia con cuadrantes (ARI, NMI)."""
from common import *
from pca_lib import zscore
from sklearn.cluster import KMeans, AgglomerativeClustering
from sklearn.metrics import silhouette_score, calinski_harabasz_score, davies_bouldin_score, adjusted_rand_score, normalized_mutual_info_score
from scipy.spatial.distance import pdist, squareform
from scipy.stats import norm, rankdata
import json
m = pd.read_csv(f'{DAT}/base82.csv'); cu = pd.read_csv(f'{DAT}/cuadrantes.csv'); OUT={}
X = m[VARS7].values; Z = zscore(X, ddof=0)    # ddof=0: idéntico a StandardScaler del informe v2 (reproduce silhouette = 0,244)
def km(Zs,k,seed=42,n_init=200): return KMeans(n_clusters=k, random_state=seed, n_init=n_init).fit(Zs)
# ---- reproducción de la solución k=4 del informe v2 -----------------------------------------------
k4v2 = KMeans(n_clusters=4, random_state=42, n_init=20).fit(Z); OUT['sil_k4_v2']=float(silhouette_score(Z,k4v2.labels_)); OUT['inercia_k4_v2']=float(k4v2.inertia_)
print('silhouette k=4 (reproducción v2, semilla 42, 20 inicios):', round(OUT['sil_k4_v2'],3), '| inercia', round(k4v2.inertia_,2))
# la solución k=4 tiene múltiples óptimos locales: se adopta la de MENOR inercia (300 inicios)
k4 = KMeans(n_clusters=4, random_state=0, n_init=300).fit(Z); sil4 = silhouette_score(Z,k4.labels_); OUT['sil_k4_best']=float(sil4); OUT['inercia_k4_best']=float(k4.inertia_)
print('silhouette k=4 (mejor de 300 inicios):', round(sil4,4), '| inercia', round(k4.inertia_,2), '| tamaños', np.bincount(k4.labels_))
seeds = [KMeans(4, random_state=s, n_init=20).fit(Z) for s in range(30)]
OUT['sil_k4_rango_semillas']=[float(min(silhouette_score(Z,f.labels_) for f in seeds)), float(max(silhouette_score(Z,f.labels_) for f in seeds))]
OUT['ari_v2_vs_best']=float(adjusted_rand_score(k4v2.labels_, k4.labels_))
# ---- selección de k ------------------------------------------------------------------------------------
def metrics_for(Zs, label):
    rows=[]
    for k in range(2,9):
        f = km(Zs,k); rows.append(dict(datos=label, k=k, silhouette=silhouette_score(Zs,f.labels_), calinski_harabasz=calinski_harabasz_score(Zs,f.labels_),
                                        davies_bouldin=davies_bouldin_score(Zs,f.labels_), inercia=f.inertia_, tam_min=int(np.bincount(f.labels_).min())))
    return rows
Xln = X.copy(); Xln[:,2]=np.log(Xln[:,2]); Xrn = np.column_stack([norm.ppf((rankdata(X[:,j])-.5)/82) for j in range(7)])
Xwin = np.clip(X, np.percentile(X,5,0), np.percentile(X,95,0))
rob = (X-np.median(X,0))/stats.median_abs_deviation(X,axis=0,scale='normal'); rob = np.clip(rob,-3,3)
datasets = {'z-score (informe v2)':Z, 'ln(PIB) + z-score':zscore(Xln,ddof=0), 'Rangos→normal + z':zscore(Xrn,ddof=0), 'Winsorizado 5/95 + z':zscore(Xwin,ddof=0), 'Escala robusta (mediana/MAD, recorte ±3)':rob}
rows=[]
for lab,Zs in datasets.items(): rows += metrics_for(Zs,lab)
ks = pd.DataFrame(rows); ks.to_csv(f'{TAB}/T06a_seleccion_k.csv', index=False, encoding='utf-8-sig')
print(ks[ks.datos=='z-score (informe v2)'].round(3).to_string(index=False))
best = ks.loc[ks.groupby('datos').silhouette.idxmax()][['datos','k','silhouette']]; print(best.round(3).to_string(index=False))
OUT['k_best_by_sil']= {r.datos:int(r.k) for r in best.itertuples()}; OUT['sil_max']= {r.datos:float(r.silhouette) for r in best.itertuples()}
# ---- Gower + jerárquico (promedio) ------------------------------------------------------------------------------
rg = X.max(0)-X.min(0); D = squareform(pdist(X/rg, 'cityblock'))/7
Dln = squareform(pdist(Xln/(Xln.max(0)-Xln.min(0)),'cityblock'))/7
hier=[]
for lab,DD in [('Gower (variables originales)',D),('Gower (ln PIB)',Dln)]:
    for k in range(2,9):
        a = AgglomerativeClustering(n_clusters=k, metric='precomputed', linkage='average').fit(DD)
        hier.append(dict(metodo='Jerárquico promedio · '+lab, k=k, silhouette=silhouette_score(DD,a.labels_,metric='precomputed'), tam_min=int(np.bincount(a.labels_).min())))
hier = pd.DataFrame(hier); hier.to_csv(f'{TAB}/T06b_jerarquico_gower.csv', index=False, encoding='utf-8-sig'); print(hier.round(3).to_string(index=False))
h4 = AgglomerativeClustering(n_clusters=4, metric='precomputed', linkage='average').fit(D).labels_
# ---- concordancia cuadrantes × clúster ----------------------------------------------------------------------------
qr = cu.cuadrante_rotado.values; qo = cu.cuadrante_original.values; lab4 = k4.labels_+1
xt = pd.crosstab(pd.Series(qr,name='Cuadrante rotado'), pd.Series(lab4,name='Clúster K-means (k=4)')); xt.to_csv(f'{TAB}/T06c_cruce_cuadrante_rotado_kmeans4.csv', encoding='utf-8-sig'); print(xt)
xt2 = pd.crosstab(pd.Series(qo,name='Cuadrante original'), pd.Series(lab4,name='Clúster K-means (k=4)')); xt2.to_csv(f'{TAB}/T06c2_cruce_cuadrante_original_kmeans4.csv', encoding='utf-8-sig')
conc = pd.DataFrame([
  dict(comparacion='Cuadrante rotado vs K-means k=4', ARI=adjusted_rand_score(qr,lab4), NMI=normalized_mutual_info_score(qr,lab4)),
  dict(comparacion='Cuadrante original (sin rotar) vs K-means k=4', ARI=adjusted_rand_score(qo,lab4), NMI=normalized_mutual_info_score(qo,lab4)),
  dict(comparacion='Cuadrante rotado vs jerárquico Gower k=4', ARI=adjusted_rand_score(qr,h4), NMI=normalized_mutual_info_score(qr,h4)),
  dict(comparacion='K-means k=4 vs jerárquico Gower k=4', ARI=adjusted_rand_score(lab4,h4), NMI=normalized_mutual_info_score(lab4,h4)),
  dict(comparacion='Cuadrante rotado vs cuadrante original', ARI=adjusted_rand_score(qr,qo), NMI=normalized_mutual_info_score(qr,qo))])
# permutación para ARI cuadrante rotado vs kmeans (nulo: etiquetas permutadas)
r=rng(51); null = np.array([adjusted_rand_score(r.permutation(qr), lab4) for _ in range(5000)]); conc.loc[0,'p_permutacion']=(1+(null>=conc.loc[0,'ARI']).sum())/5001
conc.to_csv(f'{TAB}/T06d_concordancia_ARI_NMI.csv', index=False, encoding='utf-8-sig'); print(conc.round(3).to_string(index=False))
OUT.update(ari_q_km=float(conc.ARI[0]), nmi_q_km=float(conc.NMI[0]), ari_qo_km=float(conc.ARI[1]), nmi_qo_km=float(conc.NMI[1]), ari_q_h=float(conc.ARI[2]), ari_km_h=float(conc.ARI[3]), p_ari_perm=float(conc.p_permutacion[0]))
# pureza (cuadrante dominante por clúster)
pur = (xt.max(0).sum()/xt.values.sum()); OUT['pureza_km_vs_q']=float(pur)
# los cinco cantones extremos
ext5 = ['San José','Escazú','Santa Ana','Montes de Oca','Belén']
sub = pd.DataFrame({'canton':m.canton,'cluster':lab4,'q_rot':qr,'q_orig':qo}); print(sub[sub.canton.isin(ext5)])
OUT['ext5_cluster']=sub[sub.canton.isin(ext5)].set_index('canton').cluster.to_dict(); OUT['ext5_qrot']=sub[sub.canton.isin(ext5)].set_index('canton').q_rot.to_dict()
# ---- estabilidad bootstrap (Hennig): Jaccard medio por clúster, k=4 y k=2..6 ------------------------------------------------------------
def jaccard_boot(Zs, k, B=500, seed=0):
    base = KMeans(n_clusters=k, random_state=0, n_init=100).fit(Zs).labels_; r=rng(seed); J = np.zeros((B,k))
    for b in range(B):
        i = np.unique(r.integers(0,82,82)); fb = KMeans(n_clusters=k, random_state=b, n_init=5).fit(Zs[i]).labels_
        for c in range(k):
            A = set(i[base[i]==c]); best = 0
            for d in range(k):
                Bset = set(i[fb==d]); u = len(A|Bset); best = max(best, len(A&Bset)/u if u else 0)
            J[b,c]=best
    return J.mean(0), base
rows=[]
for k in range(2,7):
    j,_ = jaccard_boot(Z,k,B=400,seed=60+k); rows.append(dict(k=k, jaccard_medio=j.mean(), jaccard_min=j.min(), **{f'J_cl{c+1}':j[c] for c in range(k)}))
jb = pd.DataFrame(rows); jb.to_csv(f'{TAB}/T06e_estabilidad_jaccard.csv', index=False, encoding='utf-8-sig'); print(jb.round(3).to_string(index=False))
OUT['jacc_k4_medio']=float(jb[jb.k==4].jaccard_medio.iloc[0]); OUT['jacc_k4_min']=float(jb[jb.k==4].jaccard_min.iloc[0])
# perfil de clúster y asignación
perfil = pd.DataFrame(X, columns=VARS7); perfil['cluster']=lab4; pc = perfil.groupby('cluster').agg(['mean']).round(3); pc.columns=[c[0] for c in pc.columns]; pc['n']=perfil.groupby('cluster').size()
pc.to_csv(f'{TAB}/T06f_perfil_clusters_kmeans4.csv', encoding='utf-8-sig'); print(pc)
asig = m[['cod_canton','canton']].copy(); asig['cluster_kmeans4']=lab4; asig['cluster_jerarquico_gower4']=h4+1; asig.to_csv(f'{DAT}/clusters.csv', index=False, encoding='utf-8-sig')
json.dump(OUT, open(f'{TAB}/_cluster_resumen.json','w'), indent=1, default=lambda o: o if not hasattr(o,'item') else o.item())
