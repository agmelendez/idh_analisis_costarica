# -*- coding: utf-8 -*-
"""
Utilidad para aplicar la regla de la sección 5 del MANUAL_DE_USO.md
("último año disponible" vs. "serie de tiempo completa") de forma
automática y generar la nota técnica obligatoria.

Uso típico:

    from nota_tecnica import resolver_anio, nota_corte, nota_serie

    resultado = resolver_anio('idh', 2026)
    # -> {'anio_solicitado': 2026, 'anio_usado': 2024, 'ajustado': True, ...}
    print(nota_corte('idh', 2026))
    print(nota_serie('idh'))
"""
import os
import pandas as pd

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_META_PATH = os.path.join(_THIS_DIR, '..', '01_referencia', 'metadata_variables.csv')

_meta = None


def _load_meta():
    global _meta
    if _meta is None:
        _meta = pd.read_csv(_META_PATH)
    return _meta


def _buscar_variable(variable):
    meta = _load_meta()
    # variable puede venir como nombre exacto (columna 'variable') o como texto libre
    fila = meta[meta['variable'].str.contains(variable, case=False, na=False)]
    if fila.empty:
        raise ValueError(
            f"No se encontró la variable '{variable}' en metadata_variables.csv. "
            "Revise el nombre exacto en esa tabla antes de continuar."
        )
    return fila.iloc[0]


def resolver_anio(variable, anio_solicitado):
    """
    Aplica la regla de la sección 5.1: si el año solicitado no existe para la
    variable, devuelve el último año disponible y marca el ajuste.
    """
    fila = _buscar_variable(variable)
    primer_anio = int(fila['primer_anio'])
    ultimo_anio = int(fila['ultimo_anio_disponible'])
    institucion = fila['institucion']

    if anio_solicitado > ultimo_anio or anio_solicitado < primer_anio:
        anio_usado = ultimo_anio if anio_solicitado > ultimo_anio else primer_anio
        ajustado = True
    else:
        anio_usado = anio_solicitado
        ajustado = False

    return {
        'variable': fila['variable'],
        'institucion': institucion,
        'anio_solicitado': anio_solicitado,
        'anio_usado': anio_usado,
        'primer_anio_disponible': primer_anio,
        'ultimo_anio_disponible': ultimo_anio,
        'ajustado': ajustado,
    }


def nota_corte(variable, anio_solicitado):
    """Texto de nota técnica para análisis de corte (sección 5.1)."""
    r = resolver_anio(variable, anio_solicitado)
    if r['ajustado']:
        return (
            f"Nota técnica: {r['variable']} corresponde al año {r['anio_usado']}, "
            f"que es el último dato disponible en la fuente ({r['institucion']}) al momento "
            f"de este análisis (información consultada en 2026). No existen datos "
            f"posteriores a {r['anio_usado']} para esta variable "
            f"(se solicitó {r['anio_solicitado']})."
        )
    return (
        f"Nota técnica: {r['variable']} corresponde al año {r['anio_usado']}, "
        f"fuente: {r['institucion']}."
    )


def nota_serie(variable):
    """Texto de nota técnica para series de tiempo (sección 5.2)."""
    fila = _buscar_variable(variable)
    return (
        f"Nota técnica: serie de {fila['variable']}, {int(fila['primer_anio'])}"
        f"–{int(fila['ultimo_anio_disponible'])}, fuente: {fila['institucion']}. "
        f"{fila['nota']}"
    )


if __name__ == '__main__':
    # ejemplos de uso
    for var, anio in [('idh', 2026), ('icc', 2025), ('pib', 2024), ('cantidad_uj', 2024)]:
        print(nota_corte(var, anio))
    print()
    print(nota_serie('idh'))
