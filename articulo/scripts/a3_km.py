import pickle, numpy as np, pandas as pd, warnings, time
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score, calinski_harabasz_score, davies_bouldin_score, adjusted_rand_score, silhouette_samples
warnings.filterwarnings('ignore')
from common import W; O=f'{W}/out'
P=pickle.load(open(f'{O}/res.pkl','rb')); res=P['res']; A=P['A']; VARS=P['VARS']; SHORT=P['SHORT']
SEED_KM=20260822; NINIT=100; NBOOT=500; NSEED=30
rows=[]; labs={}
for kind in ['principal','log']:
    Z=res[kind]['Z'].values
    rb=np.random.default_rng(SEED_KM+1)
    for k in range(2,9):
        km=KMeans(n_clusters=k,n_init=NINIT,random_state=SEED_KM,algorithm='lloyd',init='k-means++').fit(Z)
        lab=km.labels_; labs[(kind,k)]=lab
        sil=silhouette_score(Z,lab); ss=silhouette_samples(Z,lab)
        # estabilidad: bootstrap
        ari_b=[]
        for b in range(NBOOT):
            idx=rb.integers(0,len(Z),len(Z))
            kb=KMeans(n_clusters=k,n_init=20,random_state=int(rb.integers(1e9)),algorithm='lloyd').fit(Z[idx])
            ari_b.append(adjusted_rand_score(lab,kb.predict(Z)))
        # repeticiones con otras semillas
        ari_s=[]; inert=[]
        for s in range(NSEED):
            ks=KMeans(n_clusters=k,n_init=NINIT,random_state=1000+s,algorithm='lloyd').fit(Z)
            ari_s.append(adjusted_rand_score(lab,ks.labels_)); inert.append(ks.inertia_)
        rows.append(dict(spec=kind,k=k,inercia=km.inertia_,silueta=sil,sil_neg=int((ss<0).sum()),sil_min_cluster=min(ss[lab==c].mean() for c in range(k)),CH=calinski_harabasz_score(Z,lab),DB=davies_bouldin_score(Z,lab),
            tamanos=sorted(np.bincount(lab).tolist(),reverse=True),ARI_boot_media=np.mean(ari_b),ARI_boot_p05=np.percentile(ari_b,5),ARI_boot_med=np.median(ari_b),ARI_seed_min=np.min(ari_s),inercia_rango_seeds=(min(inert),max(inert))))
        print(kind,k,round(sil,3),round(calinski_harabasz_score(Z,lab),1),round(davies_bouldin_score(Z,lab),3),sorted(np.bincount(lab).tolist(),reverse=True),'ARIb',round(np.mean(ari_b),3),'ARIs',round(np.min(ari_s),3),flush=True)
D=pd.DataFrame(rows); D.to_csv(f'{O}/K_diagnostico.csv',index=False,encoding='utf-8-sig')
pickle.dump(labs,open(f'{O}/labs.pkl','wb'))
