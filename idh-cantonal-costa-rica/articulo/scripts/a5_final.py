# -*- coding: utf-8 -*-
import pickle, json, numpy as np, pandas as pd, warnings
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from sklearn.metrics import adjusted_rand_score, silhouette_score
from scipy import stats
warnings.filterwarnings('ignore')
from common import *
from common import W; O=f'{W}/out'; FG=f'{W}/fig'
import os; os.makedirs(FG,exist_ok=True)
P=pickle.load(open(f'{O}/res.pkl','rb')); res=P['res']; A=P['A'].copy(); SHORT=P['SHORT']; VARS=P['VARS']; labs=pickle.load(open(f'{O}/labs.pkl','rb'))
lg=res['log']; pr=res['principal']
plt.rcParams.update({'font.size':10,'axes.edgecolor':'#333','axes.spines.top':False,'axes.spines.right':False})
NAVY='#1F3864'; GRN='#2E7D4F'; YEL='#E8B84B'; RED='#B5382A'; BLU='#3A7CB8'
LAB=['IDH','ICC','PIB per cápita','UJ/1.000 hab.','ISC','IPM','IVDAC']
J={}
# ---- cuadrantes varimax (log) ----
S=lg['Sr']; A['C1']=S[:,0]; A['C2']=S[:,1]
def quad(s1,s2): return np.where((s1>=0)&(s2>=0),'Q1',np.where((s1<0)&(s2>=0),'Q2',np.where((s1<0)&(s2<0),'Q3','Q4')))
A['Q']=quad(A.C1,A.C2)
# comparación: sin rotar (log) y sin rotar original
Su=lg['Sstd']; A['Q_unrot_log']=quad(Su[:,0],Su[:,1]); A['Q_unrot_raw']=quad(pr['Sstd'][:,0],pr['Sstd'][:,1]); A['Q_varimax_raw']=quad(pr['Sr'][:,0],pr['Sr'][:,1])
# k-means k=3 (log), reetiquetado por ICC desc
lab=labs[('log',3)]; cen=pd.Series(A.ICC_2024.groupby(lab).mean()); order=cen.sort_values(ascending=False).index.tolist(); mp={o:i+1 for i,o in enumerate(order)}
A['K3']=[mp[x] for x in lab]
lab4=labs[('principal',4)]; cen4=A.ICC_2024.groupby(lab4).mean().sort_values(ascending=False).index.tolist(); mp4={o:i+1 for i,o in enumerate(cen4)}; A['K4raw']=[mp4[x] for x in lab4]
# conjuntos de referencia
GAM=['San José','Escazú','Desamparados','Goicoechea','Santa Ana','Alajuelita','Vázquez de Coronado','Tibás','Moravia','Montes de Oca','Curridabat','Heredia','Barva','Santo Domingo','Santa Bárbara','San Rafael','San Isidro','Belén','Flores','San Pablo','Cartago','Paraíso','La Unión','Oreamuno','El Guarco','Alajuela']
FRONT=['La Cruz','Upala','Los Chiles','San Carlos','Sarapiquí','Pococí','Talamanca','Coto Brus','Buenos Aires','Corredores','Golfito']
LITO=['La Cruz','Liberia','Santa Cruz','Carrillo','Nicoya','Nandayure','Abangares','Puntarenas','Esparza','Garabito','Parrita','Quepos','Osa','Golfito','Corredores','Limón','Pococí','Matina','Talamanca']
for nm,L in [('GAM',GAM),('FRONT',FRONT),('LITO',LITO)]: 
    assert set(L)<=set(A.canton),set(L)-set(A.canton); A[nm]=A.canton.isin(L)
A['PERIF']=A.FRONT|A.LITO
J['sets']={'GAM':GAM,'FRONT':FRONT,'LITO':LITO}
print('GAM n',A.GAM.sum(),'FRONT',A.FRONT.sum(),'LITO',A.LITO.sum(),'PERIF',A.PERIF.sum())
# ---- tablas de cuadrantes ----
rows=[]
for q in ['Q1','Q2','Q3','Q4']:
    g=A[A.Q==q]; rows.append(dict(Q=q,n=len(g),IDH=g.IDH_2024.mean(),ICC=g.ICC_2024.mean(),ISC=g.ISC_2025.mean(),IVDAC=g.IVDAC_2024.mean(),IPM=g.IPM_2024.mean(),
      GAM=int(g.GAM.sum()),PERIF=int(g.PERIF.sum()),FRONT=int(g.FRONT.sum()),LITO=int(g.LITO.sum()),prov=g.provincia.value_counts().to_dict(),cantones=g.canton.tolist()))
TQ=pd.DataFrame(rows); print(TQ.drop(columns=['cantones']).round(3).to_string()); J['TQ']=TQ.to_dict('records')
# conglomerados
rows=[]
for c in [1,2,3]:
    g=A[A.K3==c]; rows.append(dict(K=c,n=len(g),IDH=g.IDH_2024.mean(),ICC=g.ICC_2024.mean(),GAM=int(g.GAM.sum()),PERIF=int(g.PERIF.sum()),FRONT=int(g.FRONT.sum()),LITO=int(g.LITO.sum()),prov=g.provincia.value_counts().to_dict(),cantones=g.canton.tolist(),
        quad=g.Q.value_counts().to_dict()))
TK=pd.DataFrame(rows); print(TK.drop(columns=['cantones']).round(3).to_string()); J['TK']=TK.to_dict('records')
cross=pd.crosstab(A.Q,A.K3); print(cross); J['cross']=cross.to_dict()
# centroides estandarizados (k=3, log)
Zl=lg['Z'].copy(); Zl['K3']=A.K3.values; cen=Zl.groupby('K3').mean(); cen.columns=LAB; print(cen.round(2)); J['centroids']=cen.round(3).to_dict()
# centroides en unidades originales
orig=A.groupby('K3')[VARS].median(); print(orig.round(3))
# silueta de k=3 por cluster
from sklearn.metrics import silhouette_samples
ss=silhouette_samples(lg['Z'].values,A.K3.values); J['sil_by_cluster']={int(c):float(ss[A.K3.values==c].mean()) for c in [1,2,3]}; J['sil_neg']=int((ss<0).sum()); print(J['sil_by_cluster'],J['sil_neg'])
# comparaciones de especificación
J['ARI_quad_unrot_vs_varimax_raw']=adjusted_rand_score(A.Q_unrot_raw,A.Q_varimax_raw); J['n_change_unrot_varimax_raw']=int((A.Q_unrot_raw!=A.Q_varimax_raw).sum())
J['n_change_unrot_varimax_log']=int((A.Q_unrot_log!=A.Q).sum()); J['n_change_raw_log_varimax']=int((A.Q_varimax_raw!=A.Q).sum()); J['ARI_quad_raw_log']=adjusted_rand_score(A.Q_varimax_raw,A.Q)
J['ARI_K3_raw_log']=adjusted_rand_score(labs[('principal',3)],labs[('log',3)]); J['ARI_K4raw_K3log']=adjusted_rand_score(labs[('principal',4)],labs[('log',3)])
J['ARI_K4_raw_log']=adjusted_rand_score(labs[('principal',4)],labs[('log',4)])
def tucker(a,b): return (a*b).sum(0)/np.sqrt((a**2).sum(0)*(b**2).sum(0))
J['tucker_varimax']=tucker(pr['Lr'],lg['Lr']).tolist(); J['corr_scores']=[float(np.corrcoef(pr['Sr'][:,j],lg['Sr'][:,j])[0,1]) for j in range(2)]
print({k:v for k,v in J.items() if k.startswith(('ARI','n_change','tucker','corr'))})
# cantones que cambian de cuadrante entre raw-varimax y log-varimax
J['cambian_raw_log']=A.loc[A.Q_varimax_raw!=A.Q,['canton','Q_varimax_raw','Q']].values.tolist()
# posiciones de extremos
for nm,SS in [('raw',pr['Sr']),('log',lg['Sr'])]:
    d=pd.DataFrame(SS,columns=['C1','C2']); d['canton']=A.canton.values; d['r1']=d.C1.rank(ascending=False); J[f'top_C1_{nm}']=d.nlargest(5,'C1').canton.tolist(); J[f'bot_C1_{nm}']=d.nsmallest(5,'C1').canton.tolist()
J['rank_corr_C1']=float(stats.spearmanr(pr['Sr'][:,0],lg['Sr'][:,0])[0]); J['rank_corr_C2']=float(stats.spearmanr(pr['Sr'][:,1],lg['Sr'][:,1])[0])
# Belén
ib=A.index[A.canton=='Belén'][0]; J['belen_C1_raw']=float(pr['Sr'][ib,0]); J['belen_C1_log']=float(lg['Sr'][ib,0]); print('Belen',J['belen_C1_raw'],J['belen_C1_log'])
# --- guardar A
A.to_pickle(f'{O}/A_final.pkl'); A.drop(columns=[]).to_csv(f'{O}/cantones_resultados.csv',index=False,encoding='utf-8-sig')
json.dump(J,open(f'{O}/J.json','w'),ensure_ascii=False,indent=1,default=str)

# ================== FIGURAS ==================
# Fig 4 Pearson (log)
R=lg['R']; fig,ax=plt.subplots(figsize=(6.6,5.6)); im=ax.imshow(R,vmin=-1,vmax=1,cmap='RdBu_r')
ax.set_xticks(range(7)); ax.set_xticklabels(LAB,rotation=45,ha='right'); ax.set_yticks(range(7)); ax.set_yticklabels(LAB)
for i in range(7):
    for j in range(7): ax.text(j,i,f'{R[i,j]:.2f}',ha='center',va='center',fontsize=8,color='white' if abs(R[i,j])>0.6 else 'black')
cb=plt.colorbar(im,fraction=0.04,pad=0.04); cb.set_label('r de Pearson'); ax.set_title('Figura 4. Matriz de correlación de Pearson (n=82)\nPIB per cápita y UJ/1.000 hab. en logaritmo natural',fontsize=11,fontweight='bold')
for s in ax.spines.values(): s.set_visible(True)
plt.tight_layout(); plt.savefig(f'{FG}/fig4.png',dpi=200); plt.close()
# Fig 5 scree + PA
fig,ax=plt.subplots(figsize=(6.6,4.0)); x=np.arange(1,8)
ax.plot(x,lg['ev'],'o-',color=NAVY,lw=2,label='Autovalores observados (especificación principal)')
ax.plot(x,lg['pa95'],'s--',color='#777',ms=4,lw=1.2,label='Análisis paralelo: percentil 95 (2.000 permutaciones)')
ax.plot(x,pr['ev'],'o:',color='#9aa7c0',ms=4,lw=1,label='Autovalores, escala original (sensibilidad)')
ax.axhline(1,color=RED,ls='--',lw=1,label='Criterio de Kaiser (autovalor=1)')
ax.set_xlabel('Componente'); ax.set_ylabel('Autovalor'); ax.set_title('Figura 5. Gráfico de sedimentación con análisis paralelo (7 variables)',fontsize=11,fontweight='bold'); ax.legend(fontsize=7.5,frameon=False,loc='upper right'); plt.tight_layout(); plt.savefig(f'{FG}/fig5.png',dpi=200); plt.close()
# Fig 7 biplot varimax
fig,ax=plt.subplots(figsize=(7.2,6.6)); cq={'Q1':GRN,'Q2':YEL,'Q3':RED,'Q4':BLU}; lq={'Q1':'Q1 (+,+)','Q2':'Q2 (-,+)','Q3':'Q3 (-,-)','Q4':'Q4 (+,-)'}
for q in ['Q1','Q2','Q3','Q4']:
    g=A[A.Q==q]; ax.scatter(g.C1,g.C2,s=34,color=cq[q],alpha=.85,edgecolor='white',lw=.5,label=f'{lq[q]}, n={len(g)}')
ax.axhline(0,color='#888',lw=.8); ax.axvline(0,color='#888',lw=.8)
Lr=lg['Lr']; sc=2.2
offs={'IDH':(.05,.08),'ICC':(.05,.2),'PIB per cápita':(.05,-.2),'UJ/1.000 hab.':(.05,-.05),'ISC':(.05,.08),'IPM':(-.05,-.2),'IVDAC':(-.05,-.2)}
for i,v in enumerate(LAB):
    ax.annotate('',xy=(Lr[i,0]*sc,Lr[i,1]*sc),xytext=(0,0),arrowprops=dict(arrowstyle='-|>',color='#333',lw=1.6))
    ox,oy=offs[v]; ax.text(Lr[i,0]*sc+ox,Lr[i,1]*sc+oy,v,fontsize=8.5,ha='left' if Lr[i,0]>=0 else 'right')
for nm in ['Belén','San José','Escazú','Los Chiles','Buenos Aires','Limón','Quepos','San Pablo','Naranjo']:
    r=A[A.canton==nm].iloc[0]; ax.annotate(nm,(r.C1,r.C2),fontsize=7,xytext=(3,3),textcoords='offset points',color='#222')
ax.set_xlim(-2.7,3.9); ax.set_ylim(-2.9,2.6)
ax.set_xlabel('Componente 1 rotado (económico-empresarial)'); ax.set_ylabel('Componente 2 rotado (seguridad ciudadana)')
ax.set_title('Figura 7. Biplot de componentes principales rotados (varimax)\ny cuadrantes cantonales (n=82)',fontsize=11,fontweight='bold'); ax.legend(fontsize=8,frameon=False,loc='lower left'); plt.tight_layout(); plt.savefig(f'{FG}/fig7.png',dpi=200); plt.close()
# Fig 8 kmeans k=3
fig,ax=plt.subplots(figsize=(7.0,5.8)); ck={1:BLU,2:YEL,3:RED}
for c in [1,2,3]:
    g=A[A.K3==c]; ax.scatter(g.C1,g.C2,s=34,color=ck[c],alpha=.85,edgecolor='white',lw=.5,label=f'Conglomerado {c}, n={len(g)}')
ax.axhline(0,color='#888',lw=.8); ax.axvline(0,color='#888',lw=.8)
ax.set_xlabel('Componente 1 rotado (económico-empresarial)'); ax.set_ylabel('Componente 2 rotado (seguridad ciudadana)')
sil3=float(silhouette_score(lg['Z'].values,A.K3.values))
ax.set_title(f'Figura 8. Conglomerados K-means (k=3) en el plano de los\ncomponentes rotados (silueta promedio={sil3:.3f})',fontsize=11,fontweight='bold'); ax.legend(fontsize=8.5,frameon=False,loc='lower left'); plt.tight_layout(); plt.savefig(f'{FG}/fig8.png',dpi=200); plt.close()
J['sil3']=sil3
# Fig A1 diagnóstico de k
D=pd.read_csv(f'{O}/K_diagnostico.csv'); fig,axs=plt.subplots(2,2,figsize=(7.4,5.6))
for ax,(c,t) in zip(axs.flat,[('silueta','Silueta promedio'),('CH','Índice de Calinski-Harabasz'),('DB','Índice de Davies-Bouldin (menor = mejor)'),('ARI_boot_media','Estabilidad: ARI medio (bootstrap, 500)')]):
    for sp,col,lb in [('log',NAVY,'ln (principal)'),('principal',RED,'escala original')]:
        d=D[D.spec==sp]; ax.plot(d.k,d[c],'o-',color=col,ms=4,label=lb)
    ax.axvline(3,color='#aaa',ls=':'); ax.set_title(t,fontsize=9); ax.set_xlabel('k',fontsize=8)
axs[0,0].legend(fontsize=7,frameon=False); fig.suptitle('Figura A1. Diagnóstico del número de conglomerados (K-means, k=2 a 8)',fontsize=10.5,fontweight='bold'); plt.tight_layout(); plt.savefig(f'{FG}/figA1.png',dpi=200); plt.close()
print('ok')
