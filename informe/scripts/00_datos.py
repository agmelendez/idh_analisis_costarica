# -*- coding: utf-8 -*-
"""FASE 1 · Auditoría y construcción de datos (revisión externa v3).
Reconstruye dataset_analisis desde los paneles, lo coteja contra el publicado, agrega población 2023,
área, densidad, región BCCR, año común 2022-23, manifiesto con hashes y controles de calidad."""
import sys; sys.path.insert(0, __file__.rsplit('/',1)[0])
from common import *
import geopandas as gpd, glob
A = ENT
ref = pd.read_csv(f'{A}/01_referencia/cantones_oficiales_2026.csv')
idh = pd.read_csv(f'{A}/02_datos_procesados/panel_idh_pnud.csv')
icc = pd.read_csv(f'{A}/02_datos_procesados/panel_icc_ucr.csv')
pib = pd.read_csv(f'{A}/02_datos_procesados/panel_pib_bccr.csv')
uj  = pd.read_csv(f'{A}/panel_uj_cantonal_bccr.csv.gz', low_memory=False)
ds1 = pd.read_csv(f'{A}/ds1.csv'); ds2 = pd.read_csv(f'{A}/ds2.csv')

def get(df, var, anio):
    s = df[(df.variable==var)&(df.anio==anio)][['cod_canton','valor']].copy()
    s['valor'] = pd.to_numeric(s['valor'], errors='coerce'); return s.set_index('cod_canton')['valor']

# ---- reconstrucción desde paneles -----------------------------------------------------------
base = ref[['cod_canton','provincia','canton','area_km2']].set_index('cod_canton')
base['IDH_2024']=get(idh,'idh',2024); base['ISC_2025']=get(idh,'isc',2025); base['IPM_2024']=get(idh,'ipm_ipm',2024)
base['IVDAC_2024']=get(idh,'ivdac',2024); base['ICC_2024']=get(icc,'icc',2024)
base['pob_2024']=get(icc,'pob',2024); base['pob_2023']=get(icc,'pob',2023); base['pea_2024']=get(icc,'pea',2024)
base['PIB_2022_mill_crc']=get(pib,'pib',2022)
ujx = uj[(uj.anio==2024)&(uj.cod_canton!=999)].groupby('cod_canton')['cantidad_uj'].sum(min_count=1)
base['UJ_total_2024']=ujx
ujx22 = uj[(uj.anio==2022)&(uj.cod_canton!=999)].groupby('cod_canton')['cantidad_uj'].sum(min_count=1)
base['UJ_total_2022']=ujx22
base['PIB_percapita_2022']=base.PIB_2022_mill_crc/base.pob_2024                 # escenario A (original)
base['UJ_por_1000hab_2024']=base.UJ_total_2024/base.pob_2024*1000
# escenario B: población 2023 (año de población más cercano a 2022 disponible en el repositorio)
base['PIB_percapita_2022_pob2023']=base.PIB_2022_mill_crc/base.pob_2023
base['UJ_por_1000hab_2024_pob2023']=base.UJ_total_2024/base.pob_2023*1000
# escenario C: ventana 2022-2023 (IDH, ISC, IVDAC y UJ de 2022; PIB 2022; ICC 2023; IPM 2024 único corte)
base['IDH_2022']=get(idh,'idh',2022); base['ISC_2022']=get(idh,'isc',2022); base['IVDAC_2022']=get(idh,'ivdac',2022)
base['ICC_2023']=get(icc,'icc',2023)
base['UJ_por_1000hab_2022_pob2023']=base.UJ_total_2022/base.pob_2023*1000
base = base.reset_index()

# ---- cotejo contra el dataset publicado (v2) ---------------------------------------------------
chk = ds1.merge(base, on='cod_canton', suffixes=('_pub','_rec'))
rows=[]
for v in VARS7:
    d = (chk[v+'_pub'] - chk[v+'_rec']).abs().max(); rows.append((v, d))
cot = pd.DataFrame(rows, columns=['variable','max_dif_abs_vs_publicado'])
print(cot.to_string(index=False)); assert cot.max_dif_abs_vs_publicado.max() < 1e-6, 'No reproduce el dataset publicado'

# ---- unión con indicadores del Ejercicio 2 (insumos normalizados ICC 2024), región y geografía --
ex2 = ds2[['cod_canton']+PIL+INFRA+IVC].copy()
m = ds1[['cod_canton']].merge(base, on='cod_canton').merge(ex2, on='cod_canton')
reg = pd.read_excel(f'{A}/pib_raw.xlsx'); reg = reg[reg['Año']==2022][['Código Cantón','Región']].rename(columns={'Código Cantón':'cod_canton','Región':'region_bccr'})
m = m.merge(reg, on='cod_canton', how='left')
assert m.region_bccr.notna().all()
m['densidad_pob_2024']=m.pob_2024/m.area_km2; m['ln_densidad_pob_2024']=np.log(m.densidad_pob_2024); m['ln_area']=np.log(m.area_km2); m['ln_pob_2024']=np.log(m.pob_2024)
# ICC normalizado: confirmar min-max 0-100 por año (variables 'n')
m = m.sort_values('cod_canton').reset_index(drop=True)
m.to_csv(f'{DAT}/base82.csv', index=False, encoding='utf-8-sig')
base.to_csv(f'{DAT}/base84_completa.csv', index=False, encoding='utf-8-sig')
print('base82:', m.shape, '| faltantes en variables clave:', int(m[VARS7+INFRA+PIL+IVC].isna().sum().sum()))
print('Cantones fuera de la muestra de 82:', sorted(set(base.cod_canton)-set(m.cod_canton)))

# ---- auditoría de calidad ----------------------------------------------------------------------
aud=[]
aud.append(('Duplicados de cod_canton en base82', int(m.cod_canton.duplicated().sum())))
aud.append(('Cantones en marco oficial', len(ref)))
aud.append(('Cantones en la muestra', len(m)))
for v in VARS7+INFRA+PIL+IVC:
    aud.append((f'Faltantes · {v}', int(m[v].isna().sum())))
rng_rows=[]
for v in VARS7+INFRA+PIL+IVC+['pob_2024','area_km2']:
    rng_rows.append((v, m[v].min(), m[v].max()))
pd.DataFrame(aud, columns=['control','valor']).to_csv(f'{TAB}/A01_auditoria_datos.csv', index=False, encoding='utf-8-sig')
pd.DataFrame(rng_rows, columns=['variable','min','max']).to_csv(f'{TAB}/A01b_rangos.csv', index=False, encoding='utf-8-sig')

# ---- consistencia de población 2023 vs 2024 (ediciones de proyección) ------------------------
pp = base.dropna(subset=['pob_2023','pob_2024']).copy(); pp['ratio']=pp.pob_2024/pp.pob_2023
print('Población 2024/2023: mediana %.3f, rango %.3f–%.3f, total 2023=%.0f total 2024(mismos cantones)=%.0f' % (
      pp.ratio.median(), pp.ratio.min(), pp.ratio.max(), pp.pob_2023.sum(), pp.pob_2024.sum()))
pp[['cod_canton','canton','pob_2023','pob_2024','ratio']].to_csv(f'{TAB}/A02_poblacion_2023_vs_2024.csv', index=False, encoding='utf-8-sig')

# ---- manifiesto de datos (variable × año × fuente × edición × extracción × hash) --------------
files = {
 'panel_idh_pnud.csv': f'{A}/02_datos_procesados/panel_idh_pnud.csv', 'panel_icc_ucr.csv': f'{A}/02_datos_procesados/panel_icc_ucr.csv',
 'panel_pib_bccr.csv': f'{A}/02_datos_procesados/panel_pib_bccr.csv', 'panel_uj_cantonal_bccr.csv.gz': f'{A}/panel_uj_cantonal_bccr.csv.gz',
 'baseICC2023_2024.xlsx': f'{A}/icc_raw.xlsx', 'PIB,_VA_impuesto_X_M (3).xlsx': f'{A}/pib_raw.xlsx',
 'cantones_oficiales_2026.csv': f'{A}/01_referencia/cantones_oficiales_2026.csv', 'cri_admin2.shp (OCHA/HDX COD-AB v01)': f'{A}/shp/cri_admin2.shp'}
h = pd.DataFrame([(k, sha256(p), os.path.getsize(p)) for k,p in files.items()], columns=['archivo','sha256','bytes'])
h.to_csv(f'{TAB}/A03_hashes_archivos_fuente.csv', index=False, encoding='utf-8-sig')
print(h.to_string(index=False))
