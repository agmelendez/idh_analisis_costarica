import pickle, numpy as np, pandas as pd, warnings
from sklearn.metrics import adjusted_rand_score
from scipy import stats
warnings.filterwarnings('ignore')
from common import W; O=f'{W}/out'
P=pickle.load(open(f'{O}/res.pkl','rb')); res=P['res']; A=P['A']; VARS=P['VARS']; SHORT=P['SHORT']; labs=pickle.load(open(f'{O}/labs.pkl','rb'))
pr,lg=res['principal'],res['log']
# ARI entre especificaciones
for k in range(2,7): print('ARI principal vs log k=',k, round(adjusted_rand_score(labs[('principal',k)],labs[('log',k)]),3))
# congruencia de Tucker (cargas varimax)
def tucker(a,b): return (a*b).sum(0)/np.sqrt((a**2).sum(0)*(b**2).sum(0))
print('Tucker varimax',tucker(pr['Lr'],lg['Lr']).round(4),'sin rotar',np.abs(tucker(pr['L'],lg['L'])).round(4))
# correlación de puntajes
for j in range(2): print('corr scores rot comp',j+1,np.corrcoef(pr['Sr'][:,j],lg['Sr'][:,j])[0,1].round(4),'spearman',stats.spearmanr(pr['Sr'][:,j],lg['Sr'][:,j])[0].round(4))
# cuadrantes
def quad(S):
    return np.where((S[:,0]>=0)&(S[:,1]>=0),'Q1',np.where((S[:,0]<0)&(S[:,1]>=0),'Q2',np.where((S[:,0]<0)&(S[:,1]<0),'Q3','Q4')))
qU=quad(pr['Sstd']); qR=quad(pr['Sr']); qRl=quad(lg['Sr'])
print('sin rotar',pd.Series(qU).value_counts().sort_index().to_dict(),'varimax',pd.Series(qR).value_counts().sort_index().to_dict(),'varimax log',pd.Series(qRl).value_counts().sort_index().to_dict())
print('cantones que cambian de cuadrante sin rotar->varimax:',(qU!=qR).sum(),' principal->log (varimax):',(qR!=qRl).sum())
print(pd.crosstab(qU,qR))
print(pd.crosstab(qR,qRl))
print('ARI cuadrantes unrot vs rot',adjusted_rand_score(qU,qR),'rot vs log',adjusted_rand_score(qR,qRl))
# extremos
for nm,S in [('principal',pr['Sr']),('log',lg['Sr'])]:
    df=pd.DataFrame(S,columns=['C1','C2']); df['canton']=A.canton
    print(nm,'top5 C1',df.nlargest(5,'C1').canton.tolist(),'low5 C1',df.nsmallest(5,'C1').canton.tolist(),'top5 C2',df.nlargest(5,'C2').canton.tolist(),'low5 C2',df.nsmallest(5,'C2').canton.tolist())
# pearson dif
Rp,Rl=pr['R'],lg['R']; print(pd.DataFrame(Rp,index=SHORT,columns=SHORT).round(2)); print(pd.DataFrame(Rl-Rp,index=SHORT,columns=SHORT).round(2))
# perfil kmeans k=3,4 principal y log
Z=pr['Z']
for kind,k in [('principal',3),('principal',4),('log',3),('log',4)]:
    lab=labs[(kind,k)]; Zs=res[kind]['Z']; c=Zs.groupby(lab).mean(); c['n']=np.bincount(lab); c.columns=SHORT+['n']
    # ordenar por centroide ICC desc
    print(kind,k); print(c.sort_values('ICC',ascending=False).round(2))
    for g in c.sort_values('ICC',ascending=False).index: print(g, A.canton[lab==g].tolist() if (lab==g).sum()<=30 else (lab==g).sum())
