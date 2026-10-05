# -*- coding: utf-8 -*-
"""
Valida los paneles procesados en 02_datos_procesados/ contra el inventario
declarado en la sección 3 del MANUAL_DE_USO.md (años esperados, cobertura
cantonal esperada, marco de 84 cantones). Genera un reporte en markdown.
"""
import pandas as pd
import os

OUT = '/home/claude/project/costa_rica_cantonal'
REF = pd.read_csv(f'{OUT}/01_referencia/cantones_oficiales_2026.csv')
REF_CODES = set(REF['cod_canton'])

report = []
def log(line=''):
    report.append(line)
    print(line)

log('# Reporte de validación de paneles procesados')
log()
log('Generado automáticamente por `03_analisis/validar_paneles.py`. Compara cada panel de')
log('`02_datos_procesados/` contra lo declarado en la sección 3 y 6 del MANUAL_DE_USO.md.')
log()

# Expectativas declaradas en el manual (sección 3 y 6)
expectativas = {
    'panel_idh_pnud.csv': dict(anio_min=2010, anio_max=2025, cantones_max=84),
    'panel_icc_ucr.csv': dict(anio_min=2023, anio_max=2024, cantones_max=82),
    'panel_pib_bccr.csv': dict(anio_min=2019, anio_max=2022, cantones_max=84),
    'panel_va_actividad_bccr.csv': dict(anio_min=2019, anio_max=2022, cantones_max=84),
}

def validar_csv(nombre):
    exp = expectativas[nombre]
    df = pd.read_csv(f'{OUT}/02_datos_procesados/{nombre}')
    log(f'## {nombre}')
    log()
    log(f'- Filas: {len(df):,}')
    log(f'- Rango de años observado: {df.anio.min()}–{df.anio.max()} '
        f'(esperado {exp["anio_min"]}–{exp["anio_max"]})')
    ok_anio = (df.anio.min() >= exp['anio_min']) and (df.anio.max() <= exp['anio_max'])
    log(f'  -> {"OK" if ok_anio else "REVISAR"}')
    cantones_fuera_marco = sorted(set(df.cod_canton.unique()) - REF_CODES)
    log(f'- Códigos de cantón fuera del marco de 84 (`cantones_oficiales_2026.csv`): '
        f'{cantones_fuera_marco if cantones_fuera_marco else "ninguno"}')
    cantones_por_anio = df.groupby('anio')['cod_canton'].nunique()
    log(f'- Cantones distintos por año:')
    for a, n in cantones_por_anio.items():
        log(f'    - {a}: {n} cantones (máximo esperado {exp["cantones_max"]})')
    valor_col = 'valor' if 'valor' in df.columns else 'Valor Agregado'
    pct_valor_na = df[valor_col].isna().mean() * 100
    log(f'- % de valores NA en la columna `{valor_col}`: {pct_valor_na:.1f}%')
    if 'nota_disponibilidad' in df.columns:
        log(f'- Motivos de NA registrados (`nota_disponibilidad`):')
        conteo = df['nota_disponibilidad'].fillna('').replace('', '(vacío/dato válido)').value_counts()
        for motivo, n in conteo.items():
            log(f'    - {motivo}: {n:,}')
    log()

for f in expectativas:
    validar_csv(f)

# --- panel UJ (formato semi-ancho, parquet) ---
log('## panel_uj_cantonal_bccr.parquet (+ .csv.gz)')
log()
uj = pd.read_parquet(f'{OUT}/02_datos_procesados/panel_uj_cantonal_bccr.parquet')
log(f'- Filas: {len(uj):,}')
log(f'- Rango de años observado: {uj.anio.min()}–{uj.anio.max()} (esperado 2005–2024)')
cod_canton_num = pd.to_numeric(uj['cod_canton'], errors='coerce')
fuera_marco = sorted(set(int(c) for c in cod_canton_num.dropna().unique()) - REF_CODES - {999})
log(f'- Códigos de cantón fuera del marco de 84 (excluyendo 999=sin distribuir): '
    f'{fuera_marco if fuera_marco else "ninguno"}')
log(f'- Filas con código 999 (sin distribuir): {(cod_canton_num == 999).sum():,}')
n_conf = uj['nota_disponibilidad'].str.contains('confidencial', na=False).sum()
n_ncla = uj['nota_disponibilidad'].str.contains('no_clasificable', na=False).sum()
log(f'- Filas con al menos una celda marcada "confidencial": {n_conf:,} '
    f'({n_conf/len(uj)*100:.1f}% de las filas)')
log(f'- Filas con al menos una celda marcada "no_clasificable" (Tamaño/CIIU "nd"): {n_ncla:,} '
    f'({n_ncla/len(uj)*100:.1f}% de las filas)')
log()

# --- consistencia de huecos por cantón nuevo en panel IDH ---
log('## Verificación específica: cantones nuevos en panel_idh_pnud.csv')
log()
idh = pd.read_csv(f'{OUT}/02_datos_procesados/panel_idh_pnud.csv')
for cod, desde in [(216, 2019), (612, 2022), (613, 2022)]:
    sub = idh[(idh.cod_canton == cod) & (idh.variable == 'idh')].sort_values('anio')
    antes = sub[sub.anio < desde]['valor']
    despues = sub[sub.anio >= desde]['valor']
    log(f'- Cantón {cod}: años < {desde} con valor no nulo = {antes.notna().sum()} '
        f'(debe ser 0) | años >= {desde} con valor no nulo = {despues.notna().sum()} '
        f'de {len(despues)}')
log()

# --- metadata_variables.csv: consistencia interna ---
log('## metadata_variables.csv')
log()
meta = pd.read_csv(f'{OUT}/01_referencia/metadata_variables.csv')
log(f'- Filas (familias de variables registradas): {len(meta)}')
malformadas = meta[meta['primer_anio'] > meta['ultimo_anio_disponible']]
log(f'- Filas con primer_anio > ultimo_anio_disponible (inconsistentes): {len(malformadas)}')
log()

log('---')
log(f'Validación ejecutada correctamente. Total de paneles revisados: '
    f'{len(expectativas) + 1} (incluye panel_uj_cantonal_bccr).')

with open(f'{OUT}/03_analisis/reporte_validacion.md', 'w', encoding='utf-8') as f:
    f.write('\n'.join(report))

print('\n--- reporte guardado en 03_analisis/reporte_validacion.md ---')
