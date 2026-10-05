# -*- coding: utf-8 -*-
"""Biblioteca de PCA + varimax con puntajes rotados calculados directamente y orientación declarada."""
from common import *
from sklearn.decomposition import PCA
from factor_analyzer.rotator import Rotator

def zscore(X, robust=False, ddof=1):
    X = np.asarray(X, float)
    if robust:
        med = np.median(X, 0); mad = stats.median_abs_deviation(X, axis=0, scale='normal'); return (X - med) / mad
    return (X - X.mean(0)) / X.std(0, ddof=ddof)

def pca_varimax(Z, names, k=2, ref_econ='ICC_2024', ref_sec='ISC_2025', sec_sign=1, eig_from_corr=None):
    """PCA sobre Z (ya estandarizada). Devuelve dict con cargas sin rotar, rotadas, comunalidades y puntajes.
    Puntajes de componentes estandarizados S = Z V Λ^-1/2; puntajes rotados S_rot = S R, con la MISMA R
    que rota las cargas (L_rot = L R).  Orientación: eje económico con signo + en `ref_econ`; eje de
    seguridad con signo + en `ref_sec`; el eje 1 es el que mayor |carga| tiene en ref_econ."""
    n, p = Z.shape
    pca = PCA(n_components=p).fit(Z)
    lam = pca.explained_variance_
    V = pca.components_.T
    L = V[:, :k] * np.sqrt(lam[:k])
    S = Z @ V[:, :k] / np.sqrt(lam[:k])
    if k >= 2:
        rot = Rotator(method='varimax'); Lr = rot.fit_transform(L); R = rot.rotation_
    else:
        Lr, R = L.copy(), np.eye(1)
    Sr = S @ R
    names = list(names)
    if k >= 2:
        ie = names.index(ref_econ); isx = names.index(ref_sec)
        c_econ = int(np.argmax(np.abs(Lr[ie]))); c_sec = 1 - c_econ
        order = [c_econ, c_sec]
        Lr = Lr[:, order]; Sr = Sr[:, order]; R = R[:, order]
        if Lr[ie, 0] < 0: Lr[:, 0] *= -1; Sr[:, 0] *= -1; R[:, 0] *= -1
        if sec_sign*Lr[isx, 1] < 0: Lr[:, 1] *= -1; Sr[:, 1] *= -1; R[:, 1] *= -1
    comm = (Lr**2).sum(1)
    return dict(lam=lam, ratio=pca.explained_variance_ratio_, L=L, Lr=Lr, R=R, S=S, Sr=Sr, comm=comm, V=V, pca=pca)

def quadrant(e, s):
    q = np.where((e>=0)&(s>=0),'Q1', np.where((e<0)&(s>=0),'Q2', np.where((e<0)&(s<0),'Q3','Q4')))
    return q

def tucker(a, b):
    a = np.asarray(a); b = np.asarray(b); return float((a*b).sum()/np.sqrt((a**2).sum()*(b**2).sum()))

def parallel_analysis(Z, n_iter=2000, seed=0, q=95):
    n, p = Z.shape; r = rng(seed); ev = np.empty((n_iter, p))
    for i in range(n_iter):
        X = r.standard_normal((n, p)); ev[i] = np.sort(np.linalg.eigvalsh(np.corrcoef(X, rowvar=False)))[::-1]
    return ev.mean(0), np.percentile(ev, q, axis=0)

def parallel_analysis_perm(Z, n_iter=2000, seed=0, q=95):
    """Análisis paralelo por permutación de columnas (conserva marginales, rompe asociaciones)."""
    n, p = Z.shape; r = rng(seed); ev = np.empty((n_iter, p))
    for i in range(n_iter):
        X = np.column_stack([r.permutation(Z[:, j]) for j in range(p)])
        ev[i] = np.sort(np.linalg.eigvalsh(np.corrcoef(X, rowvar=False)))[::-1]
    return ev.mean(0), np.percentile(ev, q, axis=0)
