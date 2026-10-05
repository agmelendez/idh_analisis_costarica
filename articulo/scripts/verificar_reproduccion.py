# Compara articulo/resultados_reproducidas/*.csv con articulo/resultados/*.csv (tolerancia numérica 1e-9).
import pandas as pd, numpy as np, glob, os, json, platform, sys
HERE=os.path.dirname(os.path.abspath(__file__)); A=os.path.abspath(os.path.join(HERE,'..')); TOL=1e-9
res=[];ok=0;mx=0.0
for f in sorted(glob.glob(f'{A}/resultados/*.csv')):
    n=os.path.basename(f); g=f'{A}/resultados_reproducidas/{n}'
    if not os.path.exists(g): res.append([n,'ausente']); continue
    a=pd.read_csv(f,encoding='utf-8-sig'); b=pd.read_csv(g,encoding='utf-8-sig')
    if a.shape!=b.shape or list(a.columns)!=list(b.columns): res.append([n,'forma']); continue
    d=0.0
    for c in a.columns:
        if pd.api.types.is_numeric_dtype(a[c]) and pd.api.types.is_numeric_dtype(b[c]):
            x,y=a[c].values.astype(float),b[c].values.astype(float)
            d=np.inf if (np.isnan(x)!=np.isnan(y)).any() else max(d,float(np.nanmax(np.abs(x-y))) if (~np.isnan(x)).any() else 0.0)
        elif not (a[c].astype(str).values==b[c].astype(str).values).all(): d=np.inf
    if d<=TOL: ok+=1; mx=max(mx,d)
    else: res.append([n,str(d)])
out=dict(n_tablas=len(glob.glob(f'{A}/resultados/*.csv')),n_iguales=ok,tol=TOL,max_diff=f'{mx:.1e}',entorno=f'Python {platform.python_version()}',diferencias=res)
json.dump(out,open(f'{A}/verificacion_reproduccion.json','w'),indent=1,ensure_ascii=False); print(json.dumps(out,indent=1,ensure_ascii=False)); sys.exit(0 if not res else 1)
