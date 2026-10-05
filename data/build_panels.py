# -*- coding: utf-8 -*-
"""
Construye los paneles procesados (formato largo) y el registro de metadatos
para el proyecto de comportamiento cantonal de Costa Rica.
Lee directamente de los archivos originales (carpeta staged) y escribe en
02_datos_procesados/ y 01_referencia/metadata_variables.csv
"""
import pandas as pd
import numpy as np
import os

BASE = '/mnt/user-data/uploads/Desarrollo Humano y Productividad'
OUT = '/home/claude/project/costa_rica_cantonal'
REF = pd.read_csv(f'{OUT}/01_referencia/cantones_oficiales_2026.csv')
REF_CODES = set(REF['cod_canton'])
CANTON_NAME = dict(zip(REF['cod_canton'], REF['canton']))
PROV_NAME = dict(zip(REF['cod_canton'], REF['provincia']))

# cantones nuevos y su primer año real de existencia en las series (observado en los datos)
CANTON_NUEVO_DESDE = {216: 2019, 612: 2022, 613: 2022}

metadata_rows = []

def add_meta(fuente_archivo, institucion, familia, variable, cobertura, p_anio, u_anio, anio_pub, serie_continua, nota):
    metadata_rows.append(dict(
        fuente_archivo=fuente_archivo, institucion=institucion, familia_variable=familia,
        variable=variable, cobertura_geografica=cobertura, primer_anio=p_anio,
        ultimo_anio_disponible=u_anio, anio_publicacion_fuente=anio_pub,
        serie_continua=serie_continua, nota=nota,
    ))


def nota_disponibilidad_row(cod_canton, anio):
    if cod_canton in CANTON_NUEVO_DESDE and anio < CANTON_NUEVO_DESDE[cod_canton]:
        return 'canton_no_existia'
    return ''


# ---------------------------------------------------------------------------
# 1. PNUD - familia IDH (formato: hoja = Cantón + años en columnas)
# ---------------------------------------------------------------------------
IDH_DIR = f'{BASE}/Indice de Desarrollo Humano'

idh_files = {
    'Índice de Desarrollo Humano Atlas 2026.xlsx': {
        'IDH': 'idh', 'IEV': 'iev', 'Esperanza de Vida': 'esperanza_vida', 'IC': 'ic_conocimiento',
        'Años Prom Escolaridad': 'anios_prom_escolaridad', 'Años Esperados': 'anios_esperados_escolaridad',
        'IBM': 'ibm', 'Ingreso promedio estimado': 'ingreso_promedio_estimado',
    },
    'Índice de Desarrollo Género Atlas 2026.xlsx': {
        'IDG': 'idg', 'IBM mujeres': 'ibm_mujeres', 'IBM Hombres': 'ibm_hombres',
        'IEV Mujeres': 'iev_mujeres', 'IEV Hombres': 'iev_hombres', 'IC Mujeres': 'ic_mujeres',
        'IC Hombres': 'ic_hombres', 'Años esperados Mujeres': 'anios_esperados_mujeres',
        'Años esperamos Hombres': 'anios_esperados_hombres',
        'Años de escolaridad Mujeres': 'anios_escolaridad_mujeres',
        'Años de escolaridad Hombres': 'anios_escolaridad_hombres',
    },
    'Índice de Desarrollo Humano ajustado por Desigualdad Atlas 2026.xlsx': {
        'IDH-D': 'idh_ajustado_desigualdad', 'IEV Ajustado': 'iev_ajustado',
        'IC Ajustado': 'ic_ajustado', 'IBM Ajustado': 'ibm_ajustado',
    },
    'Índice de Desigualdad de Género Atlas 2026.xlsx': {
        'IDG-D': 'idg_ajustado_desigualdad', '% Control prenatal completo': 'pct_control_prenatal',
        'Tasa de natalidad adolescentes': 'tasa_natalidad_adolescente',
        'Al menos secundaria Hombres': 'pct_secundaria_hombres',
        'Al menos secundaria Mujeres': 'pct_secundaria_mujeres',
        'Regidores Hombres': 'regidores_hombres', 'Regidores Mujeres': 'regidoras_mujeres',
        'Tasa de participación Mujeres': 'tasa_participacion_mujeres',
        'Tasa de participación Hombres': 'tasa_participacion_hombres',
    },
    'Índice de Seguridad Ciudadana Atlas 2026.xlsx': {
        'ISC': 'isc', 'Tasa de homicidios': 'tasa_homicidios',
        'Tasa de ViolenciacontraMujeres': 'tasa_violencia_mujeres',
        'Tasa de Robos y Hurtos': 'tasa_robos_hurtos',
    },
    'Índice de Vulnerabilidad a Drogas y Acrividades Conexas Atlas 2026.xlsx': {
        'IVDAC': 'ivdac', 'Índice oferta y tráfico': 'ivdac_oferta_trafico',
        'Índice demanda': 'ivdac_demanda', 'Índice manifestación violencia': 'ivdac_manifestacion_violencia',
        'Índice institucional': 'ivdac_institucional',
    },
}

idh_long_frames = []
for fname, sheets in idh_files.items():
    path = f'{IDH_DIR}/{fname}'
    for sheet, varname in sheets.items():
        df = pd.read_excel(path, sheet_name=sheet, header=0)
        # primera columna = 'Cantón' con formato "101: San José"
        first_col = df.columns[0]
        df = df.rename(columns={first_col: 'canton_raw'})
        df = df.dropna(subset=['canton_raw'])
        df['cod_canton'] = df['canton_raw'].astype(str).str.split(':').str[0].str.strip().astype(int)
        year_cols = [c for c in df.columns if isinstance(c, (int, float)) and not pd.isna(c)]
        year_cols = sorted(year_cols)
        melted = df.melt(id_vars=['cod_canton'], value_vars=year_cols, var_name='anio', value_name='valor')
        melted['anio'] = melted['anio'].astype(int)
        melted['variable'] = varname
        melted['fuente'] = fname
        idh_long_frames.append(melted)
        p_anio, u_anio = int(min(year_cols)), int(max(year_cols))
        add_meta(fname, 'PNUD', 'Desarrollo Humano Cantonal', varname, 'cantonal (84, con huecos por canton nuevo)',
                  p_anio, u_anio, 2026, 'si', 'Serie anual; ver canton_no_existia para Rio Cuarto/Monteverde/Puerto Jimenez')

# IPM (corte único 2024, otra estructura: Cantón con ID + IPM + componentes)
ipm_path = f'{IDH_DIR}/Índice de Pobreza Multidimensional Atlas 2026.xlsx'
ipm = pd.read_excel(ipm_path, sheet_name='IPM 2024', header=0)
first_col = ipm.columns[0]
ipm = ipm.rename(columns={first_col: 'canton_raw'}).dropna(subset=['canton_raw'])
ipm['cod_canton'] = ipm['canton_raw'].astype(str).str.split(':').str[0].str.strip()
ipm['cod_canton'] = pd.to_numeric(ipm['cod_canton'], errors='coerce')
ipm = ipm.dropna(subset=['cod_canton'])
ipm['cod_canton'] = ipm['cod_canton'].astype(int)
value_cols = [c for c in ipm.columns if c not in ('canton_raw', 'cod_canton')]
melted = ipm.melt(id_vars=['cod_canton'], value_vars=value_cols, var_name='variable', value_name='valor')
melted['anio'] = 2024
melted['fuente'] = 'Índice de Pobreza Multidimensional Atlas 2026.xlsx'
melted['variable'] = 'ipm_' + melted['variable'].astype(str).str.lower().str.replace(' ', '_')
idh_long_frames.append(melted[['cod_canton', 'anio', 'variable', 'valor', 'fuente']])
add_meta(ipm_path.split('/')[-1], 'PNUD', 'Desarrollo Humano Cantonal', 'ipm (y componentes)', 'cantonal (84)',
          2024, 2024, 2026, 'no', 'Corte transversal unico, no es serie de tiempo')

idh_panel = pd.concat(idh_long_frames, ignore_index=True)
idh_panel['canton'] = idh_panel['cod_canton'].map(CANTON_NAME)
idh_panel['provincia'] = idh_panel['cod_canton'].map(PROV_NAME)
idh_panel['nota_disponibilidad'] = idh_panel.apply(lambda r: nota_disponibilidad_row(r['cod_canton'], r['anio']), axis=1)
# si nota_disponibilidad indica canton_no_existia, forzamos valor a NA aunque la celda tuviera algo
idh_panel.loc[idh_panel['nota_disponibilidad'] == 'canton_no_existia', 'valor'] = np.nan
idh_panel = idh_panel[['cod_canton', 'canton', 'provincia', 'anio', 'variable', 'valor', 'fuente', 'nota_disponibilidad']]
idh_panel.to_csv(f'{OUT}/02_datos_procesados/panel_idh_pnud.csv', index=False, encoding='utf-8-sig')
print('panel_idh_pnud:', idh_panel.shape)

# ---------------------------------------------------------------------------
# 2. UCR - ICC (panel largo: filas = cantón-año)
# ---------------------------------------------------------------------------
icc_path = f'{BASE}/Indice de Competititivdad/baseICC2023_2024.xlsx'
icc = pd.read_excel(icc_path, sheet_name='Datos', header=0)
icc = icc.rename(columns={'cid': 'cod_canton'})
id_cols = ['year', 'cod_canton', 'canton']
value_cols = [c for c in icc.columns if c not in id_cols]
icc_long = icc.melt(id_vars=id_cols, value_vars=value_cols, var_name='variable', value_name='valor')
icc_long = icc_long.rename(columns={'year': 'anio'})
icc_long['fuente'] = 'baseICC2023_2024.xlsx'
icc_long['canton'] = icc_long['cod_canton'].map(CANTON_NAME)
icc_long['provincia'] = icc_long['cod_canton'].map(PROV_NAME)
icc_long['nota_disponibilidad'] = ''
icc_long = icc_long[['cod_canton', 'canton', 'provincia', 'anio', 'variable', 'valor', 'fuente', 'nota_disponibilidad']]
icc_long.to_csv(f'{OUT}/02_datos_procesados/panel_icc_ucr.csv', index=False, encoding='utf-8-sig')
print('panel_icc_ucr:', icc_long.shape)
for v in sorted(icc['icc'].to_frame().columns):
    pass
add_meta('baseICC2023_2024.xlsx', 'UCR - Escuela de Economia', 'Indice de Competitividad Cantonal',
          'icc y pilares (peconomico, pgobierno, pempresarial, pinfraestructura, plaboral, pinnovacion, pcalidadvida) + ranks/categorias',
          'cantonal (81-82, sin Monteverde ni Puerto Jimenez)', 2023, 2024, 2026, 'no',
          'Rio Cuarto ausente en 2023; Monteverde y Puerto Jimenez ausentes en ambos anios')

# ---------------------------------------------------------------------------
# 3. BCCR - PIB cantonal
# ---------------------------------------------------------------------------
pib_path = f'{BASE}/Producto Interno Bruto/PIB,_VA_impuesto_X_M (3).xlsx'
pib = pd.read_excel(pib_path, sheet_name='Base_PIB_regional', header=0)
pib = pib.rename(columns={'Año': 'anio', 'Código Cantón': 'cod_canton', 'Región': 'region'})
pib.columns = [c.strip() for c in pib.columns]
id_cols = ['anio', 'cod_canton', 'region']
value_cols = ['Valor Agregado', 'Impuestos a los producto', 'PIB', 'Exportaciones', 'Importaciones']
pib_long = pib.melt(id_vars=id_cols, value_vars=value_cols, var_name='variable', value_name='valor')
varmap = {'Valor Agregado': 'valor_agregado', 'Impuestos a los producto': 'impuestos_productos', 'PIB': 'pib',
          'Exportaciones': 'exportaciones', 'Importaciones': 'importaciones'}
pib_long['variable'] = pib_long['variable'].map(varmap)
pib_long['fuente'] = 'PIB,_VA_impuesto_X_M (3).xlsx'
pib_long['canton'] = pib_long['cod_canton'].map(CANTON_NAME)
pib_long['provincia'] = pib_long['cod_canton'].map(PROV_NAME)
pib_long['nota_disponibilidad'] = ''
pib_long = pib_long[['cod_canton', 'canton', 'provincia', 'anio', 'variable', 'valor', 'fuente', 'nota_disponibilidad']]
pib_long.to_csv(f'{OUT}/02_datos_procesados/panel_pib_bccr.csv', index=False, encoding='utf-8-sig')
print('panel_pib_bccr:', pib_long.shape)
add_meta('PIB,_VA_impuesto_X_M (3).xlsx', 'BCCR', 'PIB Cantonal',
          'valor_agregado, impuestos_productos, pib, exportaciones, importaciones', 'cantonal (82 en 2019-2021, 84 en 2022)',
          2019, 2022, 2026, 'si', 'Serie corta; sin datos 2023-2026 al momento de este manual')

# ---------------------------------------------------------------------------
# 4. BCCR - Valor agregado por actividad economica (ya viene en formato largo)
# ---------------------------------------------------------------------------
va_path = f'{BASE}/Producto Interno Bruto/Valor_agregado_por actividad_economica (2).xlsx'
va = pd.read_excel(va_path, sheet_name='VA', header=0)
va = va.rename(columns={'Año': 'anio', 'Código Cantón': 'cod_canton'})
va.columns = [c.strip() for c in va.columns]
va['canton'] = va['cod_canton'].map(CANTON_NAME)
va['provincia'] = va['cod_canton'].map(PROV_NAME)
va['nota_disponibilidad'] = ''
keep = ['cod_canton', 'canton', 'provincia', 'anio', 'Tipo actividad económica', 'Código AE',
        'Actividad Económica', 'Tipo producción', 'Código Sección', 'Sección CIIU', 'Valor Agregado',
        'nota_disponibilidad']
keep = [c for c in keep if c in va.columns or c.strip() in va.columns]
va2 = va.rename(columns=lambda c: c.strip())
cols_final = ['cod_canton', 'canton', 'provincia', 'anio', 'Tipo actividad económica', 'Código AE',
              'Actividad Económica', 'Tipo producción', 'Código Sección', 'Sección CIIU', 'Valor Agregado',
              'nota_disponibilidad']
va2 = va2[[c for c in cols_final if c in va2.columns]]
va2['fuente'] = 'Valor_agregado_por actividad_economica (2).xlsx'
va2.to_csv(f'{OUT}/02_datos_procesados/panel_va_actividad_bccr.csv', index=False, encoding='utf-8-sig')
print('panel_va_actividad_bccr:', va2.shape)
add_meta('Valor_agregado_por actividad_economica (2).xlsx', 'BCCR', 'PIB Cantonal por actividad',
          'valor_agregado por seccion/clase CIIU', 'cantonal (82 en 2019-2021, 84 en 2022)', 2019, 2022, 2026, 'si',
          'Desagregacion sectorial del PIB cantonal; misma cobertura que panel_pib_bccr')

# ---------------------------------------------------------------------------
# 5. BCCR - Unidades Juridicas cantonal (C2 Mipymes + C3 Grandes)
# ---------------------------------------------------------------------------
uj_path = f'{BASE}/Unidades Jurídiacs BCR/Estadisticas_empresariales_2005_2024.xlsx'

def load_uj_sheet(sheet, tamano_col, cuadro_label):
    df = pd.read_excel(uj_path, sheet_name=sheet, header=1)
    df = df.rename(columns={'Año': 'anio', 'Cantón': 'cod_canton'})
    df.columns = [c.strip() for c in df.columns]
    df = df.dropna(subset=['cod_canton'])
    df['cod_canton'] = pd.to_numeric(df['cod_canton'], errors='coerce')
    df = df.dropna(subset=['cod_canton'])
    df['cod_canton'] = df['cod_canton'].astype(int)
    df['cuadro'] = cuadro_label
    return df

c2 = load_uj_sheet('C2', 'Tamaño', 'C2_mipymes')
c3 = load_uj_sheet('C3', 'Tamaño', 'C3_grandes')
uj = pd.concat([c2, c3], ignore_index=True, sort=False)

value_cols = ['Cantidad UJ', 'Número de trabajadores', 'Masa salarial (₡)', 'Ingresos (₡)',
              'Exportaciones ($)', 'Importaciones ($)']
value_cols = [c for c in value_cols if c in uj.columns]
varmap_uj = {'Cantidad UJ': 'cantidad_uj', 'Número de trabajadores': 'numero_trabajadores',
             'Masa salarial (₡)': 'masa_salarial_crc', 'Ingresos (₡)': 'ingresos_crc',
             'Exportaciones ($)': 'exportaciones_usd', 'Importaciones ($)': 'importaciones_usd'}

# NOTA: este panel se mantiene en formato "semi-ancho" (una fila por
# cantón-año-tamaño-actividad-cuadro, columnas = las 6 variables) en vez del
# formato largo estándar del resto de paneles, porque al ser >450 mil
# combinaciones el formato largo generaría >2.8 millones de filas (>250 MB).
# Esto es una excepción documentada en la sección 8 del manual.

def clasificar_celda(v):
    if isinstance(v, str):
        vs = v.strip().lower()
        if vs == 'x':
            return np.nan, 'confidencial'
        if vs == 'nd':
            return np.nan, 'no_clasificable'
        try:
            return float(v), ''
        except ValueError:
            return np.nan, 'no_clasificable'
    return v, ''

notas_por_fila = []
for col, newcol in varmap_uj.items():
    parsed = uj[col].apply(clasificar_celda)
    uj[newcol] = parsed.apply(lambda t: t[0])
    notas_por_fila.append(parsed.apply(lambda t: t[1]))

notas_df = pd.concat(notas_por_fila, axis=1)
notas_df.columns = list(varmap_uj.values())

def resumir_notas(row):
    conf = [c for c in row.index if row[c] == 'confidencial']
    ncla = [c for c in row.index if row[c] == 'no_clasificable']
    partes = []
    if conf:
        partes.append('confidencial:' + '|'.join(conf))
    if ncla:
        partes.append('no_clasificable:' + '|'.join(ncla))
    return ';'.join(partes)

uj['nota_disponibilidad'] = notas_df.apply(resumir_notas, axis=1)
uj.loc[uj['cod_canton'] == 999, 'nota_disponibilidad'] = (
    uj.loc[uj['cod_canton'] == 999, 'nota_disponibilidad'] + ';sin_distribuir_999'
).str.strip(';')
# Tamaño == 'nd' -> UJ activa pero no clasificable por tamaño (regla sección 4, punto 4)
uj.loc[uj['Tamaño'] == 'nd', 'nota_disponibilidad'] = (
    uj.loc[uj['Tamaño'] == 'nd', 'nota_disponibilidad'] + ';no_clasificable_tamano'
).str.strip(';')

uj['fuente'] = 'Estadisticas_empresariales_2005_2024.xlsx (' + uj['cuadro'] + ')'
uj['canton'] = uj['cod_canton'].map(CANTON_NAME)
uj['provincia'] = uj['cod_canton'].map(PROV_NAME)
uj['anio'] = uj['anio'].astype(int)
ciiu_col = 'Clase CIIU' if 'Clase CIIU' in uj.columns else ('Seccion' if 'Seccion' in uj.columns else None)

final_cols = ['cod_canton', 'canton', 'provincia', 'anio', 'cuadro', 'Tamaño']
if 'Clase CIIU' in uj.columns:
    final_cols.append('Clase CIIU')
if 'Seccion' in uj.columns:
    final_cols.append('Seccion')
final_cols += list(varmap_uj.values()) + ['fuente', 'nota_disponibilidad']
final_cols = [c for c in final_cols if c in uj.columns]
uj_final = uj[final_cols].copy()
for c in ['Tamaño', 'Clase CIIU', 'Seccion', 'cuadro', 'fuente', 'canton', 'provincia', 'nota_disponibilidad']:
    if c in uj_final.columns:
        uj_final[c] = uj_final[c].astype(str)
uj_final.to_parquet(f'{OUT}/02_datos_procesados/panel_uj_cantonal_bccr.parquet', index=False)
uj_final.to_csv(f'{OUT}/02_datos_procesados/panel_uj_cantonal_bccr.csv.gz', index=False, encoding='utf-8-sig', compression='gzip')
print('panel_uj_cantonal_bccr:', uj_final.shape)
add_meta('Estadisticas_empresariales_2005_2024.xlsx', 'BCCR', 'Unidades Juridicas cantonal (C2+C3)',
          'cantidad_uj, numero_trabajadores, masa_salarial_crc, ingresos_crc, exportaciones_usd, importaciones_usd',
          'cantonal (hasta 84 + codigo 999 sin distribuir)', 2005, 2024, 2026, 'si',
          'Celdas "x"=confidencial, "nd"=no_clasificable; ver hoja C4 del archivo original para representatividad')

# datasets nacionales (sin desagregacion cantonal) - se registran en metadata pero no se procesan como panel cantonal
add_meta('Estadisticas_empresariales_2005_2024.xlsx (C1)', 'BCCR', 'Unidades Juridicas nacional por tamaño',
          'cantidad_uj, numero_trabajadores, masa_salarial, ingresos, exportaciones, importaciones', 'nacional', 2005, 2024, 2026, 'si', 'Sin desagregacion cantonal')
add_meta('Estadisticas_empresariales_2005_2024.xlsx (C5/C5.ZF/C5.Resto)', 'BCCR', 'Empleo y salarios nacional por sección CIIU y sexo',
          'trabajadores, masa_salarial, salario_promedio, salario_mediana, valor_agregado, ingresos_reales', 'nacional', 2005, 2024, 2026, 'si', 'Sin desagregacion cantonal; C5.ZF/C5.Resto separan zona franca')
add_meta('Aporte_UJ_PIB_segun_actividad_economica_tamano.xlsx', 'BCCR', 'Aporte de las UJ al PIB',
          'aporte % al PIB por seccion CIIU y tamaño', 'nacional', 2018, 2022, 2026, 'si', '2022 es dato preliminar; sin desagregacion cantonal, no usar como fuente cantonal')

# ---------------------------------------------------------------------------
# Registro de metadatos
# ---------------------------------------------------------------------------
meta_df = pd.DataFrame(metadata_rows)
meta_df.to_csv(f'{OUT}/01_referencia/metadata_variables.csv', index=False, encoding='utf-8-sig')
print('metadata_variables:', meta_df.shape)
print(meta_df[['familia_variable', 'primer_anio', 'ultimo_anio_disponible', 'cobertura_geografica']])
