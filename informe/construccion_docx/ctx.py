# -*- coding: utf-8 -*-
"""Contexto compartido para la construcción del informe v3: datos, numeración y emisores de contenido."""
import json, os
from common import *
import docx_lib as D
from docx_lib import num, pct, pf

T = lambda n: pd.read_csv(f'{TAB}/{n}.csv')
J = lambda n: json.load(open(f'{TAB}/{n}.json'))
PCA_ = J('_pca_resumen'); CL = J('_cluster_resumen'); ESP = J('_esp_resumen'); REZ = J('_rezago_resumen'); EJ2 = J('_ej2_resumen')
VAL = J('_validacion_independiente')
ALT = json.load(open(f'{FIG}/_alt_text.json'))

# Orden fijo de tablas y figuras (se comprueba al emitir cada leyenda)
TABS = ['cambios', 'fuentes', 'descr', 'corr', 'eig', 'cargas', 'trans', 'perfil', 'sens', 'kmeans', 'cruce', 'moran',
        'infra', 'pilares', 'lodo', 'seg', 'rezago', 'entorno',
        'corr21', 'cantones', 'perfil_iqr', 'tost', 'q3sinicc', 'ponder', 'moran_full', 'hashes']
FIGS = ['distrib', 'corr', 'scree', 'plano', 'mapas', 'k', 'lisa', 'forest', 'seg', 'rezago']
TN = lambda k: f'Tabla {TABS.index(k) + 1}'
FN = lambda k: f'Figura {FIGS.index(k) + 1}'
_used_t = []; _used_f = []

heads = []          # (nivel, texto)
PAGES = {}
if os.path.exists(f'{ROOT}/_pages.json'):
    PAGES = json.load(open(f'{ROOT}/_pages.json'))


class Ctx:
    def __init__(self, B):
        self.B = B

    def add(self, s):
        self.B.add(s)

    def h1(self, t, pb=False):
        heads.append((1, t)); self.add(D.h1(t, pb))

    def h2(self, t):
        heads.append((2, t)); self.add(D.h2(t))

    def p(self, t, **kw):
        self.add(D.body(t, **kw))

    def bl(self, items):
        for i in items: self.add(D.bullet(i))

    def sub(self, t):
        self.add(D.subhead(t))

    def box(self, label, t):
        self.add(D.callout(label, t))

    def tabla(self, key, cap, headers, rows, widths, aligns=None, sz=18, **kw):
        assert TABS.index(key) == len(_used_t), f'orden de tablas: se esperaba {TABS[len(_used_t)]}, llegó {key}'
        _used_t.append(key)
        self.add(D.table(headers, rows, widths, aligns, sz=sz, **kw))
        self.add(D.caption(f'**{TN(key)}.** ' + cap))

    def fig(self, key, fname, width_in, cap):
        assert FIGS.index(key) == len(_used_f), f'orden de figuras: se esperaba {FIGS[len(_used_f)]}, llegó {key}'
        _used_f.append(key)
        self.B.figure(f'{FIG}/{fname}.png', width_in, ALT[fname], fname)
        self.add(D.caption(f'**{FN(key)}.** ' + cap))


def ci(r, a='rb', lo='rb_lo', hi='rb_hi', d=2):
    return f'{num(r[a], d)} [{num(r[lo], d)}; {num(r[hi], d)}]'
