# Artículo — reproducción

Reproduce las tablas y figuras de la sección 4 y los anexos de *Heterogeneidad territorial del desarrollo humano cantonal en Costa Rica* (2 de octubre de 2026).

```bash
pip install -r ../requirements.txt
bash scripts/run_all.sh        # a1 → a6 + verificación (≈ 25–30 min)
```

| Script | Función |
|---|---|
| `common.py` | Carga `data/entradas/ds1.csv` (n=82) y `ds3.csv` (n=84); Jenks de 5 clases. Rutas relativas; `ENTRADAS` y `TRABAJO` permiten cambiarlas. |
| `a1_base.py` | IDG (\|IDG−1\| y IDG bruto) |
| `a2_main.py` | Tabla 5 (Spearman; permutación B=1999, semilla 20260819; bootstrap 5000, semilla 20260820; BH sobre 4 p; Kruskal-Wallis + ε²; Dunn-Holm), descriptivos, extremos de Tukey, PCA (KMO, Bartlett, análisis paralelo 2000 semilla 20260821, MAP, varimax sin normalización de Kaiser). `kind='log'` = logaritmo natural (especificación principal); `kind='principal'` = escala original (sensibilidad) |
| `a3_km.py` | K-means k=2..8 (Lloyd, k-means++, n_init=100, semilla 20260822): inercia, silueta, CH, DB, ARI bootstrap (500) y entre 30 semillas |
| `a4_sens.py` | Comparación entre especificaciones |
| `a5_final.py` | Cuadrantes con puntajes varimax, K-means k=3, figuras 4, 5, 7, 8 y A1 |
| `a6_exportar.py` | Exporta IDG, autovalores y cargas |
| `verificar_reproduccion.py` | Compara con `resultados/` |

## Advertencias

- Las columnas `GAM`, `LITO`, `FRONT`, `PERIF` de `cantones_resultados.csv` (Anexo F) son una clasificación de referencia generada durante el análisis; requieren validación del autor.
- Las figuras 1, 2, 3 y 6 del artículo (histograma de Jenks, conteos por categoría, PIB e IPM por categoría y mapas comparativos) se incluyen como imágenes del documento; los scripts de este paquete regeneran las figuras 4, 5, 7, 8 y A1.
- Los scripts de construcción del DOCX con control de cambios de la sesión original no se incluyen.
