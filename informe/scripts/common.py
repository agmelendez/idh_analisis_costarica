# -*- coding: utf-8 -*-
"""Utilidades comunes de la revisión v3 (semillas, rutas, funciones estadísticas)."""
import os, hashlib, warnings
import numpy as np, pandas as pd
from scipy import stats
warnings.filterwarnings('ignore')
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
ENT = os.environ.get('ENTRADAS', os.path.abspath(os.path.join(ROOT, '..', 'data', 'entradas')))   # carpeta con los insumos (ver README)
DAT = f'{ROOT}/datos'; TAB = f'{ROOT}/tablas'; FIG = f'{ROOT}/figuras'
for _d in (DAT, TAB, FIG): os.makedirs(_d, exist_ok=True)
SEED = 20261002
B_BOOT = 5000          # remuestreos bootstrap (percentil)
N_PERM = 9999          # permutaciones espaciales
VARS7 = ['IDH_2024','ICC_2024','PIB_percapita_2022','UJ_por_1000hab_2024','ISC_2025','IPM_2024','IVDAC_2024']
LAB7 = {'IDH_2024':'IDH (2024)','ICC_2024':'ICC (2024)','PIB_percapita_2022':'PIB per cápita (2022)',
        'UJ_por_1000hab_2024':'UJ por 1.000 hab. (2024)','ISC_2025':'ISC (2025)','IPM_2024':'IPM (2024)','IVDAC_2024':'IVDAC (2024)'}
INFRA = ['Red_vial_pavimentada_pct','Cobertura_movil_pct','Velocidad_movil_pct','Llamadas_completadas_pct',
         'Internet_hogares_pct','Entidades_financieras_xkm2','Log_viviendas_electricidad_xkm2','Log_gasto_vial_xkmrvc']
LAB_INFRA = {'Red_vial_pavimentada_pct':'Red vial cantonal pavimentada','Cobertura_movil_pct':'Cobertura de redes móviles',
 'Velocidad_movil_pct':'Velocidad de redes móviles','Llamadas_completadas_pct':'Llamadas completadas (redes móviles)',
 'Internet_hogares_pct':'Viviendas con Internet (ENAHO)','Entidades_financieras_xkm2':'Sucursales financieras por km²',
 'Log_viviendas_electricidad_xkm2':'Viviendas con electricidad por km² (log)','Log_gasto_vial_xkmrvc':'Gasto municipal vial por km de red (log)'}
PIL = ['Pilar_Economico','Pilar_Gobierno','Pilar_Empresarial','Pilar_Infraestructura','Pilar_Laboral','Pilar_Innovacion','Pilar_CalidadVida']
LAB_PIL = {'Pilar_Economico':'Económico','Pilar_Gobierno':'Gobierno','Pilar_Empresarial':'Empresarial','Pilar_Infraestructura':'Infraestructura',
           'Pilar_Laboral':'Laboral','Pilar_Innovacion':'Innovación','Pilar_CalidadVida':'Calidad de vida'}
IVC = ['IVDAC_oferta_trafico','IVDAC_demanda','IVDAC_manifestacion_violencia','IVDAC_institucional']
LAB_IVC = {'IVDAC_oferta_trafico':'IVDAC · Oferta y tráfico','IVDAC_demanda':'IVDAC · Demanda',
           'IVDAC_manifestacion_violencia':'IVDAC · Manifestación de violencia','IVDAC_institucional':'IVDAC · Institucional'}

def rng(seed_offset=0): return np.random.default_rng(SEED + seed_offset)

def sha256(path):
    h = hashlib.sha256()
    with open(path,'rb') as f:
        for b in iter(lambda: f.read(1<<20), b''): h.update(b)
    return h.hexdigest()

def bh_fdr(p):
    """Benjamini-Hochberg: devuelve q-values (misma longitud/orden que p)."""
    p = np.asarray(p, float); n = len(p); o = np.argsort(p); q = np.empty(n)
    ranked = p[o] * n / (np.arange(n) + 1)
    ranked = np.minimum.accumulate(ranked[::-1])[::-1]
    q[o] = np.minimum(ranked, 1.0); return q

def boot_ci(fn, data_idx_sampler, B=B_BOOT, seed=0, alpha=0.05):
    r = rng(seed); vals = np.array([fn(data_idx_sampler(r)) for _ in range(B)])
    return np.nanpercentile(vals, [100*alpha/2, 100*(1-alpha/2)])

def corr_boot(x, y, method='pearson', B=B_BOOT, seed=0):
    x = np.asarray(x); y = np.asarray(y); n = len(x); r = rng(seed); out = np.empty(B)
    for b in range(B):
        i = r.integers(0, n, n)
        out[b] = (stats.pearsonr(x[i], y[i])[0] if method=='pearson' else stats.spearmanr(x[i], y[i])[0])
    return np.nanpercentile(out, [2.5, 97.5])

def fmt_p(p):
    return '< 0,001' if p < 0.001 else f'{p:.3f}'.replace('.', ',')
