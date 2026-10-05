# -*- coding: utf-8 -*-
"""Figuras accesibles (paleta Okabe-Ito, redundancia de marcadores, tipografía ≥ 9 pt al tamaño impreso, patrón para 'sin dato')."""
from common import *
from spatial_lib import load_geo
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt, matplotlib.patches as mpatches
from matplotlib.colors import LinearSegmentedColormap
from adjustText import adjust_text
plt.rcParams.update({'font.size':10.5,'axes.titlesize':11.5,'axes.labelsize':10.5,'xtick.labelsize':10,'ytick.labelsize':10,'legend.fontsize':10,'figure.dpi':110,'savefig.dpi':220,
                     'axes.spines.top':False,'axes.spines.right':False,'font.family':'DejaVu Sans'})
OI = dict(blue='#0072B2', orange='#E69F00', green='#009E73', verm='#D55E00', sky='#56B4E9', purple='#CC79A7', yellow='#F0E442', grey='#8A8A8A', black='#111111')
QC = {'Q1':OI['blue'],'Q2':OI['green'],'Q3':OI['verm'],'Q4':OI['orange']}; QM = {'Q1':'o','Q2':'s','Q3':'^','Q4':'D'}
QL = {'Q1':'Q1 (económico +, seguridad +)','Q2':'Q2 (económico −, seguridad +)','Q3':'Q3 (económico −, seguridad −)','Q4':'Q4 (económico +, seguridad −)'}
m = pd.read_csv(f'{DAT}/base82_con_ejes.csv'); cl = pd.read_csv(f'{DAT}/clusters.csv'); cu = pd.read_csv(f'{DAT}/cuadrantes.csv')
ALT = {}
def save(fig, name, alt):
    fig.savefig(f'{FIG}/{name}.png', bbox_inches='tight', facecolor='white'); plt.close(fig); ALT[name]=alt
# -------- F1 distribuciones ----------------------------------------------------------------------------------------------
fig, axes = plt.subplots(2,4, figsize=(7.4,5.4)); axes=axes.ravel(); r=rng(5)
for i,v in enumerate(VARS7):
    ax=axes[i]; x=m[v].values; bp=ax.boxplot(x, vert=True, widths=.55, patch_artist=True, showfliers=False, boxprops=dict(facecolor='#CFE3F3',color=OI['blue']), medianprops=dict(color=OI['verm'],lw=2), whiskerprops=dict(color=OI['blue']), capprops=dict(color=OI['blue']))
    ax.scatter(1+r.uniform(-.17,.17,len(x)), x, s=9, color=OI['black'], alpha=.45, zorder=3, linewidths=0)
    ax.set_title(LAB7[v].replace(' (','\n('), fontsize=10); ax.set_xticks([]); ax.tick_params(axis='y', labelsize=9.5)
axes[7].axis('off'); axes[7].text(0,0.5,'Línea naranja: mediana.\nCaja: rango intercuartílico.\nPuntos: los 82 cantones.\nPIB per cápita en millones\nde colones de 2022 por habitante\n(población 2024).', fontsize=9.5, va='center')
fig.tight_layout(); save(fig,'fig01_distribuciones','Siete diagramas de caja con los 82 cantones superpuestos como puntos, uno por variable (IDH, ICC, PIB per cápita, unidades jurídicas por mil habitantes, ISC, IPM e IVDAC). El PIB per cápita y el IPM muestran valores extremos altos; el IDH es el más homogéneo.')
# -------- F2 correlaciones (Pearson inferior, Spearman superior) ----------------------------------------------------------
cm = LinearSegmentedColormap.from_list('div',[OI['verm'],'#FFFFFF',OI['blue']])
P = m[VARS7].corr('pearson').values; S = m[VARS7].corr('spearman').values; n=7
fig, ax = plt.subplots(figsize=(6.6,5.9)); M = np.where(np.tril(np.ones((n,n)))==1, P, S); np.fill_diagonal(M, np.nan)
im=ax.imshow(M, vmin=-1, vmax=1, cmap=cm)
for i in range(n):
    for j in range(n):
        if i==j: ax.text(j,i,'1',ha='center',va='center',fontsize=10); continue
        ax.text(j,i,f'{M[i,j]:.2f}'.replace('.',','),ha='center',va='center',fontsize=9.5,color='white' if abs(M[i,j])>0.68 else 'black')
short=['IDH','ICC','PIB pc','UJ/1000','ISC','IPM','IVDAC']; ax.set_xticks(range(n)); ax.set_xticklabels(short,rotation=0); ax.set_yticks(range(n)); ax.set_yticklabels(short)
ax.xaxis.tick_top(); [s.set_visible(False) for s in ax.spines.values()]
ax.text(0.02,-0.12,'Triángulo inferior: Pearson  ·  Triángulo superior: Spearman',transform=ax.transAxes,fontsize=10)
cb=fig.colorbar(im,ax=ax,fraction=0.045,pad=0.03); cb.set_label('Coeficiente de correlación')
save(fig,'fig02_correlaciones','Matriz de correlación entre las siete variables: Pearson en el triángulo inferior y Spearman en el superior. Las asociaciones más fuertes son ISC con IVDAC (negativa), IDH con ICC y el ICC con unidades jurídicas por habitante (positivas).')
# -------- F3 scree + análisis paralelo -------------------------------------------------------------------------------------
eig = pd.read_csv(f'{TAB}/T03b_autovalores_analisis_paralelo.csv'); fig, ax = plt.subplots(figsize=(6.2,3.9)); k=np.arange(1,8)
ax.plot(k,eig.autovalor,'o-',color=OI['blue'],lw=2,label='Autovalores observados'); ax.plot(k,eig.PA_normal_p95,'s--',color=OI['verm'],lw=1.8,label='Análisis paralelo: percentil 95'); ax.plot(k,eig.PA_normal_media,':',color=OI['grey'],lw=2,label='Análisis paralelo: media')
ax.axhline(1,color=OI['black'],lw=.8,ls='-.',label='Criterio de Kaiser (= 1)'); ax.set_xlabel('Componente'); ax.set_ylabel('Autovalor'); ax.set_xticks(k); ax.legend(frameon=False,loc='upper right')
for i,(a,b) in enumerate(zip(eig.autovalor[:2],eig.PA_normal_p95[:2])): ax.annotate(f'{a:.2f}'.replace('.',','),(i+1,a),textcoords='offset points',xytext=(8,6),fontsize=10)
save(fig,'fig03_scree_paralelo','Gráfico de sedimentación: el primer autovalor (4,05) supera claramente al análisis paralelo; el segundo (1,33) supera la media del análisis paralelo (1,25) y el criterio de Kaiser, pero queda ligeramente por debajo del percentil 95 (1,36).')
# -------- F4 plano de ejes rotados -------------------------------------------------------------------------------------------
ld = pd.read_csv(f'{TAB}/T03c_cargas_comunalidades.csv'); fig, ax = plt.subplots(figsize=(7.0,6.0))
for q in ['Q1','Q2','Q3','Q4']:
    s=m[m.q_rot==q]; ax.scatter(s.E,s.S,s=48,c=QC[q],marker=QM[q],edgecolor='white',linewidth=.6,label=f'{QL[q]} (n={len(s)})',zorder=3)
ax.axhline(0,color=OI['grey'],lw=1); ax.axvline(0,color=OI['grey'],lw=1)
for i,v in enumerate(VARS7):
    x,y=ld.Eje_economico_rot[i]*3.2, ld.Eje_seguridad_rot[i]*2.6; ax.annotate('',xy=(x,y),xytext=(0,0),arrowprops=dict(arrowstyle='->',color='#444',lw=1.2)); 
lab_pos = {'IDH':(2.3,1.85),'ICC':(2.95,0.9),'PIB pc':(2.8,0.0),'UJ/1000':(2.8,0.5),'ISC':(0.1,2.55),'IPM':(-1.95,-1.5),'IVDAC':(0.2,-2.35)}
txt=[]
for i,(v,nm) in enumerate(zip(VARS7,short)):
    x,y=ld.Eje_economico_rot[i]*3.2, ld.Eje_seguridad_rot[i]*2.6; txt.append(ax.text(x*1.06,y*1.06,nm,fontsize=10,fontweight='bold',color='#222'))
lbl = m[(m.E.abs()>1.7)|(m.S.abs()>1.65)|(m.canton.isin(['Talamanca','Matina','Hojancha','Buenos Aires','Coto Brus']))]
tt=[ax.text(r.E,r.S,r.canton,fontsize=9,color='#222') for r in lbl.itertuples()]
adjust_text(tt+txt, ax=ax, expand=(1.15,1.3), arrowprops=dict(arrowstyle='-',color='#999',lw=.5))
ax.set_xlabel('Eje económico-empresarial (puntaje rotado, varimax; 0 = promedio de los 82 cantones)'); ax.set_ylabel('Eje de seguridad (puntaje rotado, varimax)')
ax.set_ylim(-2.7,1.9); ax.legend(loc='upper center',bbox_to_anchor=(.5,-.12),ncol=2,frameon=False,fontsize=9.5); save(fig,'fig04_plano_ejes_rotados','Dispersión de los 82 cantones según sus puntajes rotados en el eje económico-empresarial (horizontal) y el eje de seguridad (vertical). Los cuatro cuadrantes se distinguen por color y forma de marcador; se superponen los vectores de las siete variables según sus cargas rotadas.')
# -------- F5 mapa original vs rotado -----------------------------------------------------------------------------------------
g = load_geo().merge(cu[['cod_canton','cuadrante_original','cuadrante_rotado']], on='cod_canton', how='left'); g['geometry']=g.geometry.simplify(0.0025)
def draw_map(ax, col, title):
    nod = g[g[col].isna()]; nod.plot(ax=ax, facecolor='white', edgecolor='#555', hatch='////', linewidth=.4)
    for q in QC: g[g[col]==q].plot(ax=ax, color=QC[q], edgecolor='white', linewidth=.35)
    ax.set_xlim(-86.1,-82.5); ax.set_ylim(8.0,11.3); ax.set_axis_off(); ax.set_title(title, fontsize=11)
fig, axes = plt.subplots(1,2, figsize=(7.4,4.9)); draw_map(axes[0],'cuadrante_original','Puntajes sin rotar (informe anterior)'); draw_map(axes[1],'cuadrante_rotado','Puntajes rotados (este informe)')
h=[mpatches.Patch(facecolor=QC[q],label=QL[q]) for q in QC]+[mpatches.Patch(facecolor='white',edgecolor='#555',hatch='////',label='Sin dato (Monteverde y Puerto Jiménez)')]
fig.legend(handles=h,loc='lower center',ncol=2,frameon=False,fontsize=9.5,bbox_to_anchor=(.5,-.04)); fig.tight_layout(rect=(0,.07,1,1)); save(fig,'fig05_mapa_cuadrantes','Dos mapas de Costa Rica con los cuadrantes cantonales: a la izquierda según puntajes sin rotar y a la derecha según puntajes rotados. Los colores (azul, verde, bermellón, naranja) identifican Q1 a Q4 y un sombreado diagonal indica los dos cantones sin dato.')
# -------- F6 selección de k ------------------------------------------------------------------------------------------------------
ks = pd.read_csv(f'{TAB}/T06a_seleccion_k.csv'); jb = pd.read_csv(f'{TAB}/T06e_estabilidad_jaccard.csv'); fig, axes = plt.subplots(1,4, figsize=(7.4,3.0))
styles = {'z-score (informe v2)':(OI['blue'],'o'),'ln(PIB) + z-score':(OI['green'],'s'),'Rangos→normal + z':(OI['orange'],'^'),'Winsorizado 5/95 + z':(OI['purple'],'D'),'Escala robusta (mediana/MAD, recorte ±3)':(OI['verm'],'v')}
for ax,(col,tt) in zip(axes[:3],[('silhouette','Silhouette (↑)'),('calinski_harabasz','Calinski-Harabasz (↑)'),('davies_bouldin','Davies-Bouldin (↓)')]):
    for lab,(c,mk) in styles.items():
        s=ks[ks.datos==lab]; ax.plot(s.k,s[col],marker=mk,color=c,lw=1.4,ms=4.5,label=lab if col=='silhouette' else None)
    ax.set_title(tt,fontsize=10); ax.set_xlabel('k'); ax.set_xticks(range(2,9)); ax.tick_params(labelsize=9)
axes[0].axhline(.25,color='#444',ls=':',lw=1); axes[3].bar(jb.k,jb.jaccard_medio,color=OI['sky']); axes[3].axhline(.75,color='#444',ls=':',lw=1); axes[3].axhline(.6,color='#444',ls=':',lw=1); axes[3].set_title('Estabilidad (Jaccard)',fontsize=10); axes[3].set_xlabel('k'); axes[3].set_ylim(0,1); axes[3].set_xticks(range(2,7))
fig.legend(loc='lower center',ncol=2,fontsize=8.5,frameon=False,bbox_to_anchor=(.5,-.17)); fig.tight_layout(); save(fig,'fig06_seleccion_k','Cuatro paneles que comparan soluciones de K-means con k de 2 a 8: índice de silhouette, índice de Calinski-Harabasz, índice de Davies-Bouldin y estabilidad por remuestreo (Jaccard medio, k de 2 a 6). La separación es débil en todos los casos y mayor con k=2 o k=3 que con k=4.')
# -------- F7 forest Q3 vs resto (crudo y ajustado) ----------------------------------------------------------------------------
A=pd.read_csv(f'{TAB}/T08a_q3rot_vs_resto_infraestructura.csv'); Bp=pd.read_csv(f'{TAB}/T08b_q3rot_vs_resto_pilares.csv'); AI=pd.read_csv(f'{TAB}/T10a_ajustado_infra.csv'); AP=pd.read_csv(f'{TAB}/T10b_ajustado_pilares.csv')
crude=pd.concat([A,Bp]).reset_index(drop=True); adj=pd.concat([AI,AP]).reset_index(drop=True); N=len(crude)
ypos=np.array([ (N+1-i) if i<8 else (N+1-i-1) for i in range(N)],float)   # hueco entre grupos
fig, axes = plt.subplots(1,2, figsize=(7.6,6.4), sharey=True)
for k,(ax,df,xc,xl,xh,pq,ttl) in enumerate(zip(axes,[crude,adj],['rb','beta_sem'],['rb_lo','lo_sem'],['rb_hi','hi_sem'],['q_fdr','q_sem'],['Diferencia cruda\n(rank-biserial, IC 95 %)','Diferencia ajustada (desv. est.)\nerror espacial + densidad + región'])):
    for i in range(N):
        sig = df.loc[i,pq]<0.05; c=OI['verm'] if sig else '#444'
        ax.errorbar(df.loc[i,xc], ypos[i], xerr=[[df.loc[i,xc]-df.loc[i,xl]],[df.loc[i,xh]-df.loc[i,xc]]], fmt='o', mfc=c if sig else 'white', mec=c, color=c, capsize=2.5, ms=6.5, lw=1.4)
    ax.axvline(0,color='#222',lw=1); ax.set_title(ttl,fontsize=10); ax.set_xlabel('Efecto' if k==0 else 'Desviaciones estándar')
yt=list(ypos)+[ypos[0]+1.2, ypos[8]+1.0]; ylab=[r.variable for r in crude.itertuples()]+['INFRAESTRUCTURA Y CONECTIVIDAD','PILARES DEL ICC']
axes[0].set_yticks(yt); axes[0].set_yticklabels(ylab, fontsize=9.5)
for t in axes[0].get_yticklabels()[-2:]: t.set_fontweight('bold'); t.set_fontsize(9)
axes[0].set_ylim(ypos.min()-.8, ypos.max()+1.9)
fig.legend(handles=[plt.Line2D([],[],marker='o',color=OI['verm'],ls='',label='q (FDR) < 0,05'),plt.Line2D([],[],marker='o',mfc='white',mec='#444',color='#444',ls='',label='q (FDR) ≥ 0,05')],loc='lower center',ncol=2,frameon=False,bbox_to_anchor=(.55,-.01))
fig.tight_layout(rect=(0,.04,1,1)); save(fig,'fig07_forest_q3','Gráfico de bosque con quince indicadores. Panel izquierdo: diferencia cruda entre Q3 y el resto del país (correlación rank-biserial con intervalo de confianza). Panel derecho: diferencia ajustada por densidad de población y región con modelo de error espacial. Casi todas las diferencias crudas son negativas y significativas; tras el ajuste, la mayoría de las diferencias de infraestructura se acercan a cero.')
# -------- F8 eje de seguridad: panel interno vs externo ----------------------------------------------------------------------------
PA=pd.read_csv(f'{TAB}/T11a_panelA_interno.csv'); PB=pd.read_csv(f'{TAB}/T11b_panelB_externo.csv'); fig,ax=plt.subplots(figsize=(7.2,5.4)); order=list(PA.variable); yy=np.arange(len(order))[::-1]
for i,v in enumerate(order):
    a=PA[PA.variable==v].iloc[0]; b=PB[PB.variable==v].iloc[0]
    ax.errorbar(a.r,yy[i]+.13,xerr=[[a.r-a.lo],[a.hi-a.r]],fmt='o',color=OI['grey'],capsize=2.5,ms=6.5,lw=1.4,label='Panel A · interno (eje con todas las variables)' if i==0 else None)
    ax.errorbar(b.r,yy[i]-.13,xerr=[[b.r-b.lo],[b.hi-b.r]],fmt='D',color=OI['blue'],capsize=2.5,ms=6,lw=1.4,label='Panel B · externo (eje sin la familia del componente)' if i==0 else None)
ax.axvline(0,color='#222',lw=1); ax.set_yticks(yy); ax.set_yticklabels(order); ax.set_xlabel('Correlación de Pearson con el eje de seguridad (IC 95 % bootstrap)'); ax.legend(frameon=False,loc='upper center',bbox_to_anchor=(.45,-.12),ncol=1,fontsize=9.5)
save(fig,'fig08_eje_seguridad_paneles','Gráfico de puntos con intervalos de confianza de la correlación de once componentes (siete pilares del ICC y cuatro componentes del IVDAC) con el eje de seguridad. En gris, el eje que incluye todas las variables (descomposición interna); en azul, el eje reconstruido sin la familia de cada componente (comparación externa).')
# -------- F9 LISA ------------------------------------------------------------------------------------------------------------------
li=pd.read_csv(f'{TAB}/T15_lisa.csv'); gl=load_geo(); gl['geometry']=gl.geometry.simplify(0.0025)
cmap_l={'Alto-Alto':OI['blue'],'Bajo-Bajo':OI['verm'],'Alto-Bajo':OI['sky'],'Bajo-Alto':OI['orange']}
fig,axes=plt.subplots(1,2,figsize=(7.4,4.7))
for ax,eje in zip(axes,['Eje económico','Eje de seguridad']):
    d=gl.merge(li[li.eje==eje][['cod_canton','cluster_fdr','cluster_sin_ajuste']],on='cod_canton',how='left')
    d[d.cluster_fdr.isna()].plot(ax=ax,facecolor='white',edgecolor='#555',hatch='////',linewidth=.4)
    d[d.cluster_fdr=='No significativo (FDR)'].plot(ax=ax,color='#E4E4E4',edgecolor='white',linewidth=.35)
    for c,col in cmap_l.items():
        sub=d[(d.cluster_sin_ajuste==c)&(d.cluster_fdr=='No significativo (FDR)')]; sub.plot(ax=ax,color=col,alpha=.35,edgecolor='white',linewidth=.35)
        sub=d[d.cluster_fdr==c]; sub.plot(ax=ax,color=col,edgecolor='black',linewidth=.9)
    ax.set_xlim(-86.1,-82.5); ax.set_ylim(8.0,11.3); ax.set_axis_off(); ax.set_title(eje,fontsize=11)
h=[mpatches.Patch(facecolor=cmap_l['Alto-Alto'],label='Alto-Alto'),mpatches.Patch(facecolor=cmap_l['Bajo-Bajo'],label='Bajo-Bajo'),mpatches.Patch(facecolor=cmap_l['Alto-Bajo'],label='Alto-Bajo'),mpatches.Patch(facecolor=cmap_l['Bajo-Alto'],label='Bajo-Alto'),
   mpatches.Patch(facecolor='#E4E4E4',label='No significativo'),mpatches.Patch(facecolor='white',edgecolor='#555',hatch='////',label='Sin dato')]
fig.legend(handles=h,loc='lower center',ncol=3,frameon=False,fontsize=9.5,bbox_to_anchor=(.5,0.0))
fig.tight_layout(rect=(0,.09,1,1)); save(fig,'fig09_lisa','Dos mapas de agrupamientos locales de Moran (LISA) para el eje económico y el eje de seguridad. Tras corregir por comparaciones múltiples quedan seis cantones alto-alto y uno bajo-bajo en el eje económico y ninguno en el eje de seguridad; los agrupamientos con p menor que 0,05 sin ajuste se muestran en color tenue.')
# -------- F10 rezago: rangos por escenario -----------------------------------------------------------------------------------------
rz=pd.read_csv(f'{TAB}/T16_rezago_estabilidad_rangos.csv').head(12); fig,ax=plt.subplots(figsize=(6.6,4.6)); yy=np.arange(len(rz))[::-1]
for i,r in enumerate(rz.itertuples()):
    ax.plot([r.rango_min,r.rango_max],[yy[i]]*2,color=OI['sky'],lw=6,solid_capstyle='round',zorder=1); ax.scatter(r.rango_mediano,yy[i],s=60,color=OI['verm'],zorder=3,marker='D'); ax.scatter(r.rango_E0,yy[i],s=48,facecolor='white',edgecolor='black',zorder=4)
ax.set_yticks(yy); ax.set_yticklabels(rz.canton); ax.set_xlabel('Posición dentro de Q3 (1 = mayor rezago relativo)'); ax.set_xlim(0,18); ax.invert_xaxis() if False else None
ax.legend(handles=[plt.Line2D([],[],color=OI['sky'],lw=6,label='Rango en 13 escenarios'),plt.Line2D([],[],marker='D',color=OI['verm'],ls='',label='Mediana'),plt.Line2D([],[],marker='o',mfc='white',mec='black',ls='',label='Versión original (pesos iguales, 8 indicadores)')],frameon=False,loc='upper center',bbox_to_anchor=(.4,-.13),fontsize=9.5)
save(fig,'fig10_rezago_rangos','Gráfico de rangos: para los doce cantones de Q3 con mayor rezago relativo en el índice de infraestructura normalizada, muestra la posición mínima, máxima y mediana en trece escenarios de construcción del índice. Talamanca y Matina son los más estables; los demás cantones varían varias posiciones.')
import json; json.dump(ALT, open(f'{FIG}/_alt_text.json','w'), ensure_ascii=False, indent=1); print('ok', list(ALT))
