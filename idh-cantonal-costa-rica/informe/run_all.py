# -*- coding: utf-8 -*-
"""Ejecuta el procesamiento completo en orden. Uso: python run_all.py  (desde la carpeta reproducibilidad_v3)."""
import subprocess, sys, os, time
HERE = os.path.dirname(os.path.abspath(__file__)); S = os.path.join(HERE, 'scripts')
ORDEN = ['00_datos', '01_descriptivo_correlacion', '02_pca', '03_agrupamiento', '04_ejercicio2', '05_ponderado_espacial', '06_rezago', '07_figuras', '09_validacion_independiente']
for n in ORDEN:
    t = time.time(); print(f'>>> {n}.py', flush=True)
    r = subprocess.run([sys.executable, os.path.join(S, n + '.py')], cwd=S, env={**os.environ, 'ENTRADAS': os.environ.get('ENTRADAS', os.path.abspath(os.path.join(HERE, '..', 'data', 'entradas')))})
    if r.returncode: sys.exit(f'Falló {n}.py')
    print(f'    ok ({time.time()-t:.0f} s)', flush=True)
print('Procesamiento completo. Resultados en datos/, tablas/ y figuras/.')
