#!/usr/bin/env bash
# Reproduce el análisis del artículo (secciones 3-4 y anexos). Ejecutar desde articulo/scripts/
set -euo pipefail
cd "$(dirname "$0")"
for s in a1_base a2_main a3_km a4_sens a5_final a6_exportar; do echo ">>> $s.py"; python "$s.py"; done
# copia las salidas a articulo/resultados_reproducidas/
mkdir -p ../resultados_reproducidas
cp ../_trabajo/out/*.csv ../resultados_reproducidas/ 2>/dev/null || true
cp ../_trabajo/fig/*.png ../resultados_reproducidas/ 2>/dev/null || true
python verificar_reproduccion.py
echo "Listo. Resultados reproducidos en articulo/resultados_reproducidas/ (comparados con articulo/resultados/)."
