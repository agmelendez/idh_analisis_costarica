# Reporte de validación de paneles procesados

Generado automáticamente por `03_analisis/validar_paneles.py`. Compara cada panel de
`02_datos_procesados/` contra lo declarado en la sección 3 y 6 del MANUAL_DE_USO.md.

## panel_idh_pnud.csv

- Filas: 45,360
- Rango de años observado: 2010–2025 (esperado 2010–2025)
  -> OK
- Códigos de cantón fuera del marco de 84 (`cantones_oficiales_2026.csv`): ninguno
- Cantones distintos por año:
    - 2010: 84 cantones (máximo esperado 84)
    - 2011: 84 cantones (máximo esperado 84)
    - 2012: 84 cantones (máximo esperado 84)
    - 2013: 84 cantones (máximo esperado 84)
    - 2014: 84 cantones (máximo esperado 84)
    - 2015: 84 cantones (máximo esperado 84)
    - 2016: 84 cantones (máximo esperado 84)
    - 2017: 84 cantones (máximo esperado 84)
    - 2018: 84 cantones (máximo esperado 84)
    - 2019: 84 cantones (máximo esperado 84)
    - 2020: 84 cantones (máximo esperado 84)
    - 2021: 84 cantones (máximo esperado 84)
    - 2022: 84 cantones (máximo esperado 84)
    - 2023: 84 cantones (máximo esperado 84)
    - 2024: 84 cantones (máximo esperado 84)
    - 2025: 84 cantones (máximo esperado 84)
- % de valores NA en la columna `valor`: 2.4%
- Motivos de NA registrados (`nota_disponibilidad`):
    - (vacío/dato válido): 44,268
    - canton_no_existia: 1,092

## panel_icc_ucr.csv

- Filas: 10,432
- Rango de años observado: 2023–2024 (esperado 2023–2024)
  -> OK
- Códigos de cantón fuera del marco de 84 (`cantones_oficiales_2026.csv`): ninguno
- Cantones distintos por año:
    - 2023: 81 cantones (máximo esperado 82)
    - 2024: 82 cantones (máximo esperado 82)
- % de valores NA en la columna `valor`: 0.0%
- Motivos de NA registrados (`nota_disponibilidad`):
    - (vacío/dato válido): 10,432

## panel_pib_bccr.csv

- Filas: 1,650
- Rango de años observado: 2019–2022 (esperado 2019–2022)
  -> OK
- Códigos de cantón fuera del marco de 84 (`cantones_oficiales_2026.csv`): ninguno
- Cantones distintos por año:
    - 2019: 82 cantones (máximo esperado 84)
    - 2020: 82 cantones (máximo esperado 84)
    - 2021: 82 cantones (máximo esperado 84)
    - 2022: 84 cantones (máximo esperado 84)
- % de valores NA en la columna `valor`: 0.0%
- Motivos de NA registrados (`nota_disponibilidad`):
    - (vacío/dato válido): 1,650

## panel_va_actividad_bccr.csv

- Filas: 37,122
- Rango de años observado: 2019–2022 (esperado 2019–2022)
  -> OK
- Códigos de cantón fuera del marco de 84 (`cantones_oficiales_2026.csv`): ninguno
- Cantones distintos por año:
    - 2019: 82 cantones (máximo esperado 84)
    - 2020: 82 cantones (máximo esperado 84)
    - 2021: 82 cantones (máximo esperado 84)
    - 2022: 84 cantones (máximo esperado 84)
- % de valores NA en la columna `Valor Agregado`: 0.0%
- Motivos de NA registrados (`nota_disponibilidad`):
    - (vacío/dato válido): 37,122

## panel_uj_cantonal_bccr.parquet (+ .csv.gz)

- Filas: 469,272
- Rango de años observado: 2005–2024 (esperado 2005–2024)
- Códigos de cantón fuera del marco de 84 (excluyendo 999=sin distribuir): ninguno
- Filas con código 999 (sin distribuir): 7,489
- Filas con al menos una celda marcada "confidencial": 349,960 (74.6% de las filas)
- Filas con al menos una celda marcada "no_clasificable" (Tamaño/CIIU "nd"): 64,972 (13.8% de las filas)

## Verificación específica: cantones nuevos en panel_idh_pnud.csv

- Cantón 216: años < 2019 con valor no nulo = 0 (debe ser 0) | años >= 2019 con valor no nulo = 6 de 6
- Cantón 612: años < 2022 con valor no nulo = 0 (debe ser 0) | años >= 2022 con valor no nulo = 3 de 3
- Cantón 613: años < 2022 con valor no nulo = 0 (debe ser 0) | años >= 2022 con valor no nulo = 3 de 3

## metadata_variables.csv

- Filas (familias de variables registradas): 49
- Filas con primer_anio > ultimo_anio_disponible (inconsistentes): 0

---
Validación ejecutada correctamente. Total de paneles revisados: 5 (incluye panel_uj_cantonal_bccr).