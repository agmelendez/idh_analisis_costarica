import pandas as pd, numpy as np, jenkspy
import os
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.abspath(os.path.join(HERE,'..','..'))
ENT=os.environ.get('ENTRADAS',f'{ROOT}/data/entradas')          # insumos (ds1.csv, ds3.csv)
W=os.environ.get('TRABAJO',os.path.join(HERE,'..','_trabajo'))   # carpeta de trabajo (intermedios; no versionada)
os.makedirs(f'{W}/out',exist_ok=True); os.makedirs(f'{W}/fig',exist_ok=True)
d3=pd.read_csv(f'{ENT}/ds3.csv',encoding='utf-8-sig'); d1=pd.read_csv(f'{ENT}/ds1.csv',encoding='utf-8-sig')
CATS=['Muy Bajo','Bajo','Medio','Alto','Muy Alto']
def jenks5(s):
    v=s.dropna().values; b=list(jenkspy.jenks_breaks(v,n_classes=5))
    def a(x):
        for i in range(5):
            lo,hi=b[i],b[i+1]
            if (i==4 and lo<=x<=hi) or (i<4 and lo<=x<hi): return i
        return 4
    return s.apply(lambda x: a(x) if pd.notna(x) else np.nan), b
d3['IDH_cat'],bIDH=jenks5(d3.IDH_2024); d3['IDHD_cat'],bIDHD=jenks5(d3.IDHD_2024); d3['IDG_cat'],bIDG=jenks5(d3.IDG_2024)
full=d3.merge(d1[['cod_canton','ICC_2024','UJ_por_1000hab_2024','ISC_2025','IVDAC_2024']],on='cod_canton',how='left')
