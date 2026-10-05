# -*- coding: utf-8 -*-
from common import *
import geopandas as gpd, libpysal
from libpysal.weights import Queen, W, KNN
SHP = f'{ENT}/shp/cri_admin2.shp'
def load_geo():
    g = gpd.read_file(SHP); g['cod_canton'] = g.adm2_pcode.str[2:].astype(int); return g
def build_W(m, g=None, verbose=False):
    """Contigüidad Queen calculada con los 84 polígonos y luego restringida a los cantones de la muestra (82), estandarizada por filas."""
    g = load_geo() if g is None else g
    g = g.sort_values('cod_canton').reset_index(drop=True)
    wq = Queen.from_dataframe(g, use_index=False, silence_warnings=True)
    ids = g.cod_canton.tolist(); keep = set(m.cod_canton)
    neigh = {ids[i]: [ids[j] for j in wq.neighbors[i] if ids[j] in keep] for i in range(len(ids)) if ids[i] in keep}
    order = m.cod_canton.tolist()
    # islas tras restringir: asignar vecino más cercano por centroide
    gg = g.set_index('cod_canton'); cen = gg.geometry.to_crs(5367).centroid if gg.crs is not None else gg.geometry.centroid
    isl = [k for k,v in neigh.items() if len(v)==0]
    for k in isl:
        d = {j: cen[k].distance(cen[j]) for j in keep if j!=k}; neigh[k] = [min(d, key=d.get)]
    w = W({k: neigh[k] for k in order}, id_order=order); w.transform = 'r'
    if verbose: print('islas reasignadas:', isl, '| vecinos medios: %.2f' % np.mean([len(v) for v in neigh.values()]))
    return w, isl
