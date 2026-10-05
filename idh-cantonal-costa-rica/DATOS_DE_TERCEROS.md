# Datos de terceros y atribución

Este repositorio redistribuye datos **procesados** a partir de fuentes públicas. Las bases armonizadas, las tablas y las figuras elaboradas por el CIOdD se publican bajo CC BY 4.0, pero eso **no relicencia** los datos de origen, que conservan los términos de sus instituciones.

| Fuente | Qué se incluye aquí | Atribución |
|---|---|---|
| PNUD Costa Rica, *Atlas de Desarrollo Humano Cantonal* (2026) | Paneles procesados (IDH, IDH-D, IDG, IPM, ISC, IVDAC y componentes) | Programa de las Naciones Unidas para el Desarrollo, Costa Rica |
| Banco Central de Costa Rica (BCCR), PIB cantonal | Panel procesado y el libro `pib_raw.xlsx` (reconstrucción del informe) | Banco Central de Costa Rica |
| BCCR, Estadísticas empresariales / Unidades Jurídicas (REVEC) | Panel procesado comprimido; no se incluye el libro original | Banco Central de Costa Rica |
| Escuela de Economía, UCR, Índice de Competitividad Cantonal | Panel procesado y el libro `icc_raw.xlsx` (reconstrucción del informe) | Escuela de Economía, Universidad de Costa Rica |
| OCHA / HDX, límites administrativos COD-AB de Costa Rica | `data/entradas/shp/` y su versión simplificada en `data/geo/` | OCHA, Humanitarian Data Exchange |
| Registro Nacional, IGN, División Territorial Administrativa 2026 | Marco de 84 cantones (`cantones_oficiales_2026.csv`) | Registro Nacional, Instituto Geográfico Nacional |

## Pendiente de confirmación por el autor

- Confirmar con cada institución que la redistribución de los paneles procesados y de los dos libros originales (`icc_raw.xlsx`, `pib_raw.xlsx`) es compatible con sus términos de uso; si no lo fuera, retirar esos archivos y mantener el script de construcción (`data/build_panels.py`) con instrucciones para obtener el original.
- Confirmar el titular de los derechos de autor que figurará en `LICENSE-CODE` (persona autora o la Universidad de Costa Rica).
- Confirmar el texto exacto de la licencia de los límites COD-AB vigente en HDX.
