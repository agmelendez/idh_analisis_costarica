# Desarrollo humano, competitividad y seguridad en los cantones de Costa Rica

Repositorio de reproducibilidad de dos estudios del **Centro de Investigación Observatorio del Desarrollo (CIOdD), Universidad de Costa Rica**, bajo la coordinación de **MSI. Agustín Gómez Meléndez**.

🌐 **Sitio:** https://USUARIO.github.io/idh-cantonal-costa-rica/ · 📦 **Repositorio:** https://github.com/USUARIO/idh-cantonal-costa-rica

| Estudio | Documento | Código |
|---|---|---|
| **Artículo.** *Heterogeneidad territorial del desarrollo humano cantonal en Costa Rica: reclasificación estadística de rupturas naturales y validación externa con productividad, competitividad y tejido empresarial (2010–2025)* | [`documentos/`](documentos) | [`articulo/`](articulo) |
| **Informe técnico v3.** *Perfiles cantonales de desarrollo, competitividad y seguridad en Costa Rica: análisis exploratorio de 82 cantones con datos de 2022 a 2025* | [`documentos/`](documentos) | [`informe/`](informe) |

## Contenido

```
documentos/     artículo e informe (PDF y DOCX)
data/
  armonizadas/  bases finales en CSV (llave: cod_canton)
  entradas/     insumos de los scripts: paneles procesados, ds1–ds3, shapefile, libros originales ICC y PIB
  geo/          límites cantonales simplificados (GeoJSON)
  DICCIONARIO_DATOS.csv · MANUAL_DE_USO.md · MANIFEST_SHA256.txt
articulo/       scripts a1–a5 + resultados publicados
informe/        scripts 00–10 + 54 tablas de referencia y figuras
assets/ + *.html  sitio de GitHub Pages
```

## Reproducir

```bash
git clone https://github.com/USUARIO/idh-cantonal-costa-rica.git && cd idh-cantonal-costa-rica
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

python informe/run_all.py                            # informe: scripts 00–09
python informe/scripts/10_verificar_reproduccion.py  # compara con informe/resultados_referencia/
bash articulo/scripts/run_all.sh                     # artículo: scripts a1–a5
```

Versiones de referencia: Python 3.13.16 y las fijadas en [`requirements.txt`](requirements.txt). Los resultados con simulación (bootstrap, permutaciones, K-means) dependen de la semilla y de las versiones; con las versiones fijadas se reproducen exactamente (ver la página *Código* del sitio). Las semillas están declaradas en los scripts (`informe`: 20261002; `articulo`: 20260819–20260822).

## Datos

Consulte el [diccionario](data/DICCIONARIO_DATOS.csv) y el [manual de uso](data/MANUAL_DE_USO.md) antes de combinar fuentes: los vacíos tienen cuatro orígenes distintos (cantón inexistente, año fuera de rango, confidencialidad, no clasificable) y **no equivalen a cero**. Cada variable conserva su último año disponible.

## Alcance

Diseños transversales y descriptivos sobre un censo de 84 cantones (82 con datos completos). Las asociaciones no establecen causalidad; los valores *p* e intervalos miden estabilidad, no inferencia a una población mayor; cuadrantes y conglomerados son posiciones relativas, no evaluaciones de desempeño.

> Los cuadrantes del artículo (PCA con PIB per cápita y UJ en logaritmo natural) y del informe (escala original) **no coinciden** cantón por cantón: son especificaciones distintas.

## Licencias

- Contenido (textos, tablas, figuras, bases armonizadas): [CC BY 4.0](LICENSE).
- Código: [MIT](LICENSE-CODE).
- Datos de origen: términos de sus instituciones; ver [DATOS_DE_TERCEROS.md](DATOS_DE_TERCEROS.md).

## Cómo citar

Ver [`CITATION.cff`](CITATION.cff) (GitHub muestra el botón «Cite this repository»).

## Uso de inteligencia artificial

Los análisis, el código, los documentos y la organización de este repositorio se elaboraron con apoyo de un asistente de IA generativa (Claude, de Anthropic). Las cifras provienen de análisis efectivamente ejecutados sobre los datos del Observatorio; el diseño metodológico, la interpretación y la responsabilidad final corresponden al autor.

## Contacto

agustin.gomez@ucr.ac.cr
