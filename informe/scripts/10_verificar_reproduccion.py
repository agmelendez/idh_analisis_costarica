# -*- coding: utf-8 -*-
"""Verificación de REPRODUCCIÓN: copia el paquete a un directorio limpio, lo ejecuta desde cero y compara cada tabla
(.csv/.json) con la de resultados_referencia/. No valida la metodología (para eso: 09_validacion_independiente.py)."""
import os, sys, shutil, subprocess, tempfile, json, platform
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, '..')); TOL = 1e-6
tmp = tempfile.mkdtemp(prefix='repro_'); dst = os.path.join(tmp, 'pkg')
os.makedirs(dst); shutil.copytree(os.path.join(ROOT, 'scripts'), os.path.join(dst, 'scripts'), ignore=shutil.ignore_patterns('__pycache__'))
shutil.copy(os.path.join(ROOT, 'run_all.py'), dst)
env = {**os.environ, 'ENTRADAS': os.environ.get('ENTRADAS', os.path.abspath(os.path.join(ROOT, '..', 'data', 'entradas')))}
r = subprocess.run([sys.executable, os.path.join(dst, 'run_all.py')], cwd=dst, env=env)
assert r.returncode == 0, 'La ejecución limpia falló'
ref = os.path.join(ROOT, 'resultados_referencia', 'tablas'); nuevo = os.path.join(dst, 'tablas'); n = 0; ok = 0; maxd = 0.0; dif = []
for f in sorted(os.listdir(ref)):
    if f.startswith('_validacion') and False: continue
    p0, p1 = os.path.join(ref, f), os.path.join(nuevo, f); n += 1
    if not os.path.exists(p1): dif.append((f, 'ausente')); continue
    if f.endswith('.csv'):
        a, b = pd.read_csv(p0), pd.read_csv(p1)
        if a.shape != b.shape or list(a.columns) != list(b.columns): dif.append((f, 'forma')); continue
        d = 0.0
        for c in a.columns:
            if pd.api.types.is_numeric_dtype(a[c]) and pd.api.types.is_numeric_dtype(b[c]):
                x, y = a[c].values.astype(float), b[c].values.astype(float); both = ~(np.isnan(x) | np.isnan(y))
                if (np.isnan(x) != np.isnan(y)).any(): d = np.inf
                elif both.any(): d = max(d, float(np.abs(x[both] - y[both]).max()))
            elif not (a[c].fillna('').astype(str).values == b[c].fillna('').astype(str).values).all(): d = np.inf
    else:
        a, b = json.load(open(p0)), json.load(open(p1))
        def flat(o, k=''):
            if isinstance(o, dict):
                for kk, v in o.items(): yield from flat(v, f'{k}/{kk}')
            elif isinstance(o, list):
                for i, v in enumerate(o): yield from flat(v, f'{k}[{i}]')
            else: yield k, o
        A, Bd = dict(flat(a)), dict(flat(b)); d = 0.0
        if A.keys() != Bd.keys(): d = np.inf
        else:
            for k in A:
                if isinstance(A[k], (int, float)) and not isinstance(A[k], bool): d = max(d, abs(A[k] - Bd[k]))
                elif A[k] != Bd[k]: d = np.inf
    if d <= TOL: ok += 1; maxd = max(maxd, d)
    else: dif.append((f, d))
res = dict(n_tablas=n, n_iguales=ok, tol=f'{TOL:g}', max_diff=f'{maxd:.1e}', entorno=f'Python {platform.python_version()}, directorio temporal nuevo, sin resultados previos', diferencias=[list(map(str, x)) for x in dif])
json.dump(res, open(os.path.join(ROOT, 'resultados_referencia', 'verificacion_reproduccion.json'), 'w'), indent=1, ensure_ascii=False)
print(json.dumps(res, indent=1, ensure_ascii=False)); shutil.rmtree(tmp, ignore_errors=True); sys.exit(0 if not dif else 1)
