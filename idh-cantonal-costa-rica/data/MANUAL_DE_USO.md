# Manual de uso — Base de información cantonal de Costa Rica

**Proyecto:** Comportamiento cantonal de Costa Rica (Desarrollo Humano y Productividad)
**Fecha de elaboración:** 17 de agosto de 2026
**Alcance:** este documento describe el inventario, la cobertura temporal, la cobertura cantonal y las reglas de tratamiento de vacíos de todas las bases de datos disponibles en la carpeta `Desarrollo Humano y Productividad`, antes de iniciar cualquier análisis o cálculo. Es el documento de referencia que debe consultarse cada vez que se combinen, agreguen o comparen variables entre fuentes.

---

## 1. Marco de referencia cantonal

Costa Rica tiene actualmente **84 cantones** (7 provincias, 84 cantones, 490 distritos). El marco de referencia oficial para este proyecto es la hoja `CUADRO_CANTON` del archivo:

> `DTA-TABLA POR PROVINCIA-CANTÓN-DISTRITO 2026.xlsx` (Registro Nacional — Instituto Geográfico Nacional, División Territorial Administrativa 2026)

De esa hoja se derivó la tabla canónica de este proyecto:

> `01_referencia/cantones_oficiales_2026.csv` — columnas: `cod_provincia, provincia, cod_canton, canton, area_km2` (84 filas).

**Regla de oro:** toda tabla de trabajo debe unirse (join) contra este archivo usando el código de cantón de 3 dígitos (`cod_canton`, formato `PDD` = provincia + 2 dígitos de cantón dentro de la provincia, p. ej. `101` = San José/San José, `216` = Alajuela/Río Cuarto). Cualquier cantón del marco de referencia que no aparezca en una fuente debe tratarse como **dato faltante explícito (NA)**, nunca como cero, salvo que la fuente indique lo contrario (ver sección 5).

Los dos cantones más recientes —**Monteverde (612)** y **Puerto Jiménez (613)**, ambos segregados de Puntarenas— y **Río Cuarto (216)** —segregado de Alajuela— no tienen historia completa en ninguna fuente porque no existían como entidad administrativa independiente en los primeros años de cada serie. Antes de 2019, Río Cuarto no existe en ninguna base cantonal; antes de 2022, Monteverde y Puerto Jiménez tampoco. Esto **no es un error de captura**, es la fecha real desde la que existe la unidad territorial, y se debe documentar así en cualquier resultado que los incluya.

Región BCCR (usada por las bases de PIB y Valor Agregado): Central, Chorotega, Pacífico Central, Brunca, Huetar Caribe, Huetar Norte (6 regiones que agrupan los 84 cantones; ver columna `Región` en esas bases).

---

## 2. Estructura de carpetas originales

```
Desarrollo Humano y Productividad/
├── DTA-TABLA POR PROVINCIA-CANTÓN-DISTRITO 2026.xlsx      ← marco de referencia (IGN/Registro Nacional)
├── Indice de Desarrollo Humano/                            ← PNUD (Atlas de Desarrollo Humano Cantonal)
│   ├── Índice de Desarrollo Humano Atlas 2026.xlsx
│   ├── Índice de Desarrollo Género Atlas 2026.xlsx
│   ├── Índice de Desarrollo Humano ajustado por Desigualdad Atlas 2026.xlsx
│   ├── Índice de Desigualdad de Género Atlas 2026.xlsx
│   ├── Índice de Pobreza Multidimensional Atlas 2026.xlsx
│   ├── Índice de Seguridad Ciudadana Atlas 2026.xlsx
│   └── Índice de Vulnerabilidad a Drogas y Actividades Conexas Atlas 2026.xlsx
├── Indice de Competititivdad/                              ← Escuela de Economía, UCR
│   ├── baseICC2023_2024.xlsx
│   └── InformeICC2024.pdf - Ecodatos.pdf
├── Producto Interno Bruto/                                 ← Banco Central de Costa Rica (BCCR)
│   ├── PIB,_VA_impuesto_X_M (3).xlsx
│   ├── Valor_agregado_por actividad_economica (2).xlsx
│   ├── Guia-uso-PIB-Cantonal.pdf
│   └── presentacion-pib-regional-2019-2021.pdf
└── Unidades Jurídicas BCR/                                 ← Banco Central de Costa Rica (BCCR)
    ├── Estadisticas_empresariales_2005_2024.xlsx
    └── Aporte_UJ_PIB_segun_actividad_economica_tamano.xlsx
```

---

## 3. Inventario detallado por fuente

### 3.1 Índice de Desarrollo Humano y familia de índices — PNUD

**Institución que genera la información:** Programa de las Naciones Unidas para el Desarrollo (PNUD), Costa Rica — Atlas de Desarrollo Humano Cantonal.

| Archivo | Hojas (variables) | Años disponibles | Cobertura cantonal | Notas |
|---|---|---|---|---|
| `Índice de Desarrollo Humano Atlas 2026.xlsx` | IDH, IEV (índice esperanza de vida), Esperanza de Vida, IC (índice de conocimiento), Años Prom. Escolaridad, Años Esperados (de escolaridad), IBM (índice de bienestar material), Ingreso promedio estimado | **2010–2024** | 84 filas nominales, pero Río Cuarto solo desde 2019, Monteverde/Puerto Jiménez solo desde 2022 (resto de años = NA) | Serie anual continua para los 81 cantones "originales" |
| `Índice de Desarrollo Género Atlas 2026.xlsx` | IDG, IBM/IEV/IC/Años esperados/Años escolaridad, por sexo (Hombres/Mujeres) | 2010–2024 | Igual patrón que el IDH | Columnas vacías extra (>2024) sin datos, ignorar |
| `Índice de Desarrollo Humano ajustado por Desigualdad Atlas 2026.xlsx` | IDH-D, IEV/IC/IBM ajustados | 2010–2024 | Igual patrón que el IDH | — |
| `Índice de Desigualdad de Género Atlas 2026.xlsx` | IDG-D, % control prenatal, natalidad adolescente, escolaridad secundaria por sexo, regidoras/regidores, tasa de participación por sexo | 2010–2024 | Igual patrón que el IDH | — |
| `Índice de Pobreza Multidimensional Atlas 2026.xlsx` | IPM 2024 (única hoja, con `IPM_rank`) | **Solo 2024** (corte transversal, no serie de tiempo) | 84 cantones | No usar para análisis histórico; es una foto única |
| `Índice de Seguridad Ciudadana Atlas 2026.xlsx` | ISC, tasa de homicidios, tasa de violencia contra mujeres, tasa de robos y hurtos | **2020–2025** | 84 cantones | Única familia PNUD con dato preliminar de 2025 |
| `Índice de Vulnerabilidad a Drogas y Actividades Conexas Atlas 2026.xlsx` | IVDAC, índice oferta y tráfico, índice demanda, índice manifestación de violencia, índice institucional | **2020–2024** | 84 cantones | — |

**Notas de tratamiento:**
- El "Cantón" en estas hojas viene codificado como texto `"101: San José"`; para unir con el marco de referencia hay que separar el código antes de los dos puntos.
- Las hojas con columnas "Unnamed" adicionales al final (IC Mujeres/Hombres, IDG-D, ISC, IVDAC) tienen columnas vacías sobrantes del formato original del Atlas — deben descartarse, no son años adicionales.
- La familia IDH (2010–2024) y la familia ISC/IVDAC (2020–2025/2024) **no comparten el mismo rango de años**; cualquier panel combinado debe declarar explícitamente el rango común (2020–2024) o tratar cada familia por separado.

### 3.2 Índice de Competitividad Cantonal (ICC) — Escuela de Economía, UCR

**Institución que genera la información:** Escuela de Economía, Universidad de Costa Rica (UCR) — proyecto Ecodatos/Observatorio de Desarrollo.

| Archivo | Hoja de datos | Años disponibles | Cobertura cantonal | Notas |
|---|---|---|---|---|
| `baseICC2023_2024.xlsx` | `Datos` (formato panel largo: una fila por cantón-año); `Variables` documenta cada columna (ICC general, 7 pilares con sus rankings y categorías, más variables base: población, PEA, área, indicadores normalizados) | **2023–2024** | 2024: 82 cantones · 2023: 81 cantones (falta Río Cuarto, código 216) | **Monteverde (612) y Puerto Jiménez (613) no están incluidos en ninguno de los dos años** — el ICC todavía no los cubre |
| `InformeICC2024.pdf - Ecodatos.pdf` | Informe metodológico y de resultados | — | — | Documento de referencia metodológica, no contiene datos tabulares reutilizables directamente |

**Notas de tratamiento:** el ICC es la fuente con menor cobertura cantonal y menor profundidad temporal de todo el proyecto. Cualquier análisis que combine ICC con IDH o PIB debe limitarse a los 81–82 cantones cubiertos y dejar explícito que Monteverde y Puerto Jiménez quedan fuera.

### 3.3 Producto Interno Bruto Cantonal — Banco Central de Costa Rica (BCCR)

**Institución que genera la información:** Banco Central de Costa Rica (BCCR), Departamento de Estadística Macroeconómica — Sistema de PIB Regional/Cantonal.

| Archivo | Estructura | Años disponibles | Cobertura cantonal | Notas |
|---|---|---|---|---|
| `PIB,_VA_impuesto_X_M (3).xlsx` (hoja `Base_PIB_regional`) | Panel por cantón-año: Región, Provincia, Cantón, Valor Agregado, Impuestos a los productos, PIB, Exportaciones, Importaciones (todo en millones de colones corrientes, según guía del BCCR) | **2019–2022** | 2019–2021: 82 cantones · 2022: 84 cantones (primer año con Río Cuarto **y** Monteverde/Puerto Jiménez juntos) | Serie corta; el BCCR aún no publica 2023–2026 a nivel cantonal |
| `Valor_agregado_por actividad_economica (2).xlsx` (hoja `VA`) | Panel detallado por cantón-año-actividad económica (CIIU Rev. 4, nivel Sección/Clase), con tipo de actividad y tipo de producción (mercado/no mercado) | **2019–2022** | Igual patrón que el archivo anterior | Base "larga" (37,122 filas); útil para desagregar el PIB por sector, pero mucho más pesada de procesar |
| `Guia-uso-PIB-Cantonal.pdf` | Metodología oficial de construcción del PIB cantonal | — | — | Consultar antes de cualquier cálculo de tasas de crecimiento o comparaciones intercantonales |
| `presentacion-pib-regional-2019-2021.pdf` | Presentación de resultados 2019–2021 | — | — | Material de contexto/divulgación |

**Notas de tratamiento:** el PIB cantonal es la serie más corta de todo el proyecto (4 años). No hay dato de PIB cantonal para 2023, 2024, 2025 ni 2026 al momento de este manual — cualquier cálculo que requiera esos años debe marcarse como **no disponible**, no debe estimarse por defecto salvo que se indique explícitamente una metodología de proyección.

### 3.4 Unidades Jurídicas (empresas/comercio) — Banco Central de Costa Rica (BCCR)

**Institución que genera la información:** Banco Central de Costa Rica (BCCR), a partir del Registro de Variables Económicas (REVEC).

| Archivo | Hojas | Años disponibles | Cobertura cantonal | Notas |
|---|---|---|---|---|
| `Estadisticas_empresariales_2005_2024.xlsx` | `Contenido` (índice), `C1` (nacional por tamaño), **`C2`** (Mipymes: cantidad UJ, trabajadores, masa salarial, ingresos, exportaciones, importaciones — por tamaño, actividad económica a 4 dígitos CIIU, provincia y **cantón**), **`C3`** (empresas grandes: mismas variables, por sección CIIU y **cantón**), `C4` (representatividad/cobertura de los datos publicados), `C5`/`C5.ZF`/`C5.Resto` (trabajadores, masa salarial, salarios, valor agregado por sección CIIU y sexo — **nivel nacional, sin desagregación cantonal**), `Códigos` (diccionario de códigos CIIU, tamaño y división territorial) | **2005–2024** | C2 y C3: 84 códigos de cantón presentes en el archivo, incluye un código especial **999 = "no distribuido/sin clasificar"** que debe excluirse o tratarse aparte en cualquier agregación cantonal | Es la única fuente con serie histórica larga (20 años) y con desagregación cantonal |
| `Aporte_UJ_PIB_segun_actividad_economica_tamano.xlsx` | Una hoja por año: `2018`…`2022` — aporte de las UJ al PIB por sección CIIU y tamaño de empresa (según ingresos y según cantidad de trabajadores) | **2018–2022** (2022 es preliminar) | **Nivel nacional únicamente, sin desagregación cantonal** | No usar como fuente cantonal; solo sirve como contexto nacional/sectorial |

**Notas de tratamiento — muy importante:**
- En `C2` y `C3`, las celdas suprimidas por confidencialidad estadística (pocas unidades jurídicas en esa combinación de año/tamaño/actividad/cantón) aparecen literalmente como el texto **`"x"`**. Esto **no es un dato faltante en el sentido de "no se recolectó"**, es un valor real que el BCCR no puede publicar por ley. Debe tratarse como **NA con motivo "confidencial"**, y nunca imputarse como cero. La hoja `C4` cuantifica qué porcentaje del total agregado representan las celdas efectivamente publicadas, año por año — debe usarse para calificar la confiabilidad de cualquier agregación cantonal basada en C2/C3.
- El código de tamaño/actividad **`"nd"`** (no disponible) identifica unidades jurídicas activas en el año que no tienen información suficiente para clasificar su tamaño o actividad — tampoco debe imputarse.
- Algunas combinaciones cantón-año pueden estar completamente ausentes de C2/C3 (no solo con "x") cuando no hay ninguna unidad jurídica de ese tipo en ese cantón ese año; en ese caso el valor correcto para agregaciones de conteo es **0**, no NA. Antes de decidir entre NA y 0 hay que distinguir "la fila no existe porque no hay UJ" de "la fila existe pero el valor está suprimido (x)".

---

## 4. Reglas de tratamiento de vacíos (resumen operativo)

Cuando el sistema deba calcular algo (comparaciones, rankings, promedios, tasas de crecimiento, índices compuestos) y encuentre un vacío, debe aplicar esta jerarquía, en orden:

1. **Cantón no existía todavía como entidad administrativa en ese año** (Río Cuarto antes de 2019; Monteverde/Puerto Jiménez antes de 2022, y en el caso del ICC, en ningún año disponible). → Tratar como **NA estructural**; excluir de denominadores nacionales de ese año en vez de sumar cero.
2. **Año fuera del rango cubierto por la fuente** (p. ej. pedir PIB cantonal 2024, 2025 o 2026; pedir ICC 2020; pedir IPM histórico antes de 2024). → Responder explícitamente que **no existe el dato**, no aproximar ni interpolar salvo que el usuario pida expresamente una estimación y acepte la metodología.
3. **Celda suprimida por confidencialidad estadística** (`"x"` en C2/C3 de Unidades Jurídicas). → **NA con motivo "confidencial"**; para agregados cantonales, usar la hoja `C4` para reportar qué porcentaje del total queda sin cubrir.
4. **Código `"nd"`** (tamaño o actividad no clasificable). → **NA con motivo "no clasificable"**.
5. **Fila ausente por ausencia real de unidades/observaciones** (no hay ninguna unidad jurídica de esa categoría en ese cantón-año). → **0**, no NA.
6. **Cantón faltante en el ICC** (Monteverde, Puerto Jiménez, y Río Cuarto en 2023). → **NA**; el ICC nunca debe usarse para calcular promedios nacionales "de los 84 cantones" sin aclarar la cobertura real.

Todo resultado, gráfico o tabla que el proyecto produzca debe indicar, junto al dato, la cantidad real de cantones y años cubiertos (p. ej. "n=82 cantones, 2019–2021" en vez de asumir 84/2010–2026).

---

## 5. Regla del "último año disponible" y nota técnica obligatoria

Todas las fuentes de este proyecto fueron **consultadas/publicadas en 2026**, pero ninguna tiene datos hasta 2026, y la mayoría ni siquiera hasta 2025 (ver tabla de la sección 6). Esto obliga a separar dos conceptos que no deben confundirse nunca dentro del proyecto:

- **Año de publicación/consulta de la fuente**: 2026 para las cuatro instituciones (PNUD, UCR, BCCR).
- **Año(s) al que corresponde realmente el dato**: varía por variable, entre 2005 y 2025 según la tabla de la sección 6.

Esto rige dos tipos de análisis de forma distinta:

### 5.1 Análisis de corte (foto de un año / rankings / mapas / comparaciones entre cantones en "el año más reciente")

Cuando se pida analizar "el año más reciente", "la situación actual" o un año puntual que no exista en la fuente (por ejemplo 2025 o 2026), la regla es:

1. Tomar, para **cada variable por separado**, el último año realmente disponible en su fuente (columna `ultimo_anio_disponible` del registro `01_referencia/metadata_variables.csv`, ver sección 7).
2. Si el año pedido por el usuario **no existe** para esa variable (p. ej. se pide 2025 o 2026 y la variable solo llega a 2022 o 2024), ese año queda **excluido del análisis** y se usa el último año disponible en su lugar — nunca se proyecta, extrapola o rellena un valor para el año faltante salvo que el usuario lo pida explícitamente y acepte una metodología de proyección.
3. Cuando dos o más variables de fuentes distintas se combinan en el mismo cuadro/gráfico/mapa (p. ej. IDH + ICC + PIB + Unidades Jurídicas), **cada una conserva su propio último año disponible** — no se fuerza a todas al mismo año artificialmente. Lo que se homologa es el cantón (vía `cod_canton`), no el año.
4. **Toda salida (cuadro, gráfico, mapa o afirmación de análisis) que use esta regla debe llevar una nota técnica** con el siguiente formato mínimo:

   > *Nota técnica: [nombre de la variable] corresponde al año [AAAA], que es el último dato disponible en la fuente ([institución]) al momento de este análisis (información consultada en 2026). No existen datos posteriores a [AAAA] para esta variable.*

   Si distintas variables de un mismo cuadro tienen años distintos, la nota técnica debe listarlas todas, variable por variable (no basta una nota genérica para todo el cuadro).

### 5.2 Análisis de series de tiempo (evolución, tendencias, tasas de crecimiento)

Cuando se pida analizar la evolución de una variable en el tiempo, la regla es la opuesta a la del corte transversal:

1. Usar **la mayor cantidad de años posible** para esa variable, es decir todo su rango disponible según la sección 6 (p. ej. IDH 2010–2024 completos, no solo los últimos años).
2. No recortar la serie para "emparejarla" con el año más corto de otra variable salvo que el análisis sea explícitamente comparativo entre variables con distinto período — en ese caso se declara el período común y se explica por qué es más corto que el máximo de cada variable individual.
3. La nota técnica de una serie de tiempo debe indicar el rango completo usado y su fuente:

   > *Nota técnica: serie de [nombre de la variable], [primer año]–[último año disponible], fuente: [institución]. Serie sin dato en: [lista de años/cantones excluidos, si aplica, incluyendo los años en que un cantón nuevo —Río Cuarto, Monteverde o Puerto Jiménez— todavía no existía].*

### 5.3 Resumen de la regla

| Tipo de análisis | Año a usar | Qué hacer si el año pedido no existe | Nota técnica obligatoria |
|---|---|---|---|
| Corte transversal / mapa / ranking de "último año" | Último año disponible **por variable** | Excluir el año pedido, usar el último disponible, avisarlo | Sí, indicando el año real usado y la fuente |
| Serie de tiempo / tendencia | Todo el rango disponible **por variable** | No aplica (se usa el máximo histórico posible) | Sí, indicando el rango real usado, huecos y fuente |

Esta regla y su nota técnica no son opcionales: ningún cuadro, gráfico, mapa o texto de análisis debe publicarse dentro de este proyecto sin declarar explícitamente el año o rango de años real de cada variable que contiene.

---

## 6. Cobertura temporal comparada (vista rápida)

| Familia de variables | Institución | Primer año | Último año | Frecuencia | Cobertura cantonal máxima |
|---|---|---|---|---|---|
| IDH, IDG, IDH-D, IDG-D y componentes | PNUD | 2010 | 2024 | Anual | 84 (con huecos por cantón nuevo) |
| Índice de Pobreza Multidimensional (IPM) | PNUD | 2024 | 2024 | Corte único | 84 |
| Índice de Seguridad Ciudadana (ISC) y componentes | PNUD | 2020 | 2025 | Anual | 84 |
| Índice de Vulnerabilidad a Drogas (IVDAC) y componentes | PNUD | 2020 | 2024 | Anual | 84 |
| Índice de Competitividad Cantonal (ICC) y pilares | UCR – Escuela de Economía | 2023 | 2024 | Anual | 81–82 (nunca incluye Monteverde/Puerto Jiménez) |
| PIB cantonal / Valor Agregado por actividad | BCCR | 2019 | 2022 | Anual | 82 (2019–2021) → 84 (2022) |
| Unidades Jurídicas cantonal (C2, C3) | BCCR | 2005 | 2024 | Anual | hasta 84 + código 999 "sin distribuir" |
| Unidades Jurídicas nacional (C1, C5, C5.ZF, C5.Resto) | BCCR | 2005 (C5: 2006) | 2024 | Anual | Nacional, sin desagregación cantonal |
| Aporte UJ al PIB por sección/tamaño | BCCR | 2018 | 2022 (preliminar) | Anual | Nacional, sin desagregación cantonal |

**No existe información 2025 ni 2026 para**: IDH y familia PNUD relacionada (excepto ISC, que sí llega a 2025), ICC, PIB cantonal, ni Unidades Jurídicas. El sistema debe asumirlo por defecto y avisar cuando se le pida un año fuera de rango, en lugar de fallar silenciosamente o inventar un valor.

---

## 7. Fuentes institucionales (para citar en cualquier salida del proyecto)

- **Índice de Desarrollo Humano cantonal y familia de índices relacionados** (IDH, IDG, IDH-D, IDG-D, IPM, ISC, IVDAC): Programa de las Naciones Unidas para el Desarrollo (PNUD), Costa Rica — Atlas de Desarrollo Humano Cantonal.
- **Índice de Competitividad Cantonal (ICC)**: Escuela de Economía, Universidad de Costa Rica (UCR).
- **Producto Interno Bruto Cantonal y Valor Agregado por actividad económica**: Banco Central de Costa Rica (BCCR).
- **Unidades Jurídicas (estadísticas empresariales y aporte al PIB por sección CIIU y tamaño)**: Banco Central de Costa Rica (BCCR), con base en el Registro de Variables Económicas (REVEC).
- **Marco cantonal oficial (84 cantones, códigos, áreas)**: Registro Nacional — Instituto Geográfico Nacional (IGN), División Territorial Administrativa 2026.

---

## 8. Estructura de trabajo del proyecto (ya construida)

```
costa_rica_cantonal/
├── MANUAL_DE_USO.md                        ← este documento
├── 00_fuentes_originales/                  ← copias de trabajo de los archivos crudos (no modificar)
├── build_panels.py                         ← script que genera todos los paneles y el registro de metadatos a partir de los archivos originales
├── 01_referencia/
│   ├── cantones_oficiales_2026.csv         ← marco cantonal canónico (84 cantones)
│   ├── metadata_variables.csv              ← registro de TODAS las variables: fuente, institución, primer/último año disponible, año de publicación de la fuente (2026), cobertura cantonal, tipo de nota de disponibilidad
│   └── periodos_comunes.csv                ← escenarios A/B/C de la sección 10, con la intersección real de cantones por año
├── 02_datos_procesados/                    ← paneles limpios en formato largo (cod_canton, canton, provincia, anio, variable, valor, fuente, nota_disponibilidad)
│   ├── panel_idh_pnud.csv                  ← IDH, IDG, IDH-D, IDG-D, IPM, ISC, IVDAC y todos sus componentes (2010–2025 según variable)
│   ├── panel_icc_ucr.csv                   ← ICC y los 7 pilares, con rankings y categorías (2023–2024)
│   ├── panel_pib_bccr.csv                  ← PIB, Valor Agregado, Impuestos, Exportaciones, Importaciones cantonales (2019–2022)
│   ├── panel_va_actividad_bccr.csv         ← Valor Agregado por actividad económica CIIU, cantón-año-actividad (2019–2022)
│   └── panel_uj_cantonal_bccr.parquet / .csv.gz  ← Unidades Jurídicas por cantón (C2 Mipymes + C3 Grandes), 2005–2024, formato semi-ancho (ver sección 3.4), con "x"/"nd" ya convertidos a NA con motivo
└── 03_analisis/
    ├── nota_tecnica.py                     ← dado un año pedido y una variable, devuelve el año real a usar y el texto de la nota técnica de la sección 5
    ├── validar_paneles.py                  ← corre las validaciones de la sección 9 y regenera reporte_validacion.md
    └── reporte_validacion.md               ← salida más reciente de validar_paneles.py
```

**Convención de `02_datos_procesados`**: todos los paneles comparten las columnas `cod_canton`, `canton`, `provincia`, `anio`, `variable`, `valor`, `fuente`, `nota_disponibilidad` (vacío = dato válido; `"confidencial"`, `"no_clasificable"`, `"canton_no_existia"`, `"fuera_de_rango"` según la jerarquía de la sección 4). Esto permite combinar cualquier familia de variables con un `join` sobre `cod_canton` (+ `anio` cuando corresponda) sin perder la trazabilidad de por qué falta un dato.

`metadata_variables.csv` es el archivo que cualquier cuadro, gráfico o mapa debe consultar antes de fijar el año a mostrar: contiene, por variable, el primer y el último año con dato real, para aplicar automáticamente la regla de la sección 5.

---

## 9. Validación de los paneles procesados

Los paneles de `02_datos_procesados/` fueron validados contra el inventario de la sección 3 y la cobertura de la sección 6 con el script `03_analisis/validar_paneles.py`. El detalle completo queda en `03_analisis/reporte_validacion.md` (regenerar ese archivo cada vez que se vuelva a correr `build_panels.py`). Resultado de la validación más reciente:

- **Rangos de años**: los cinco paneles coinciden exactamente con lo declarado en la sección 3/6 (IDH 2010–2025 combinado —2010–2024 para la mayoría de variables, 2020–2025 para ISC—; ICC 2023–2024; PIB y Valor Agregado 2019–2022; Unidades Jurídicas cantonal 2005–2024).
- **Códigos de cantón**: ningún panel tiene códigos fuera del marco oficial de 84 cantones (más el código especial `999 = sin distribuir` en Unidades Jurídicas, tratado aparte).
- **Cantones por año**: confirma numéricamente los patrones de la sección 3 — IDH mantiene 84 filas nominales todos los años (con huecos internos por cantón nuevo); ICC pasa de 81 cantones (2023) a 82 (2024); PIB y Valor Agregado pasan de 82 cantones (2019–2021) a 84 (2022); Unidades Jurídicas cantonal ya trae 84 códigos + el 999 en toda la serie.
- **Huecos por cantón nuevo**: se verificó fila por fila que Río Cuarto (216), Monteverde (612) y Puerto Jiménez (613) tienen valor nulo en el IDH antes de su primer año real (2019 y 2022 respectivamente) y valor no nulo desde entonces — 0 excepciones encontradas.
- **Unidades Jurídicas — hallazgo corregido durante la validación**: la primera versión del panel no marcaba con `nota_disponibilidad` las filas donde el campo `Tamaño = "nd"` (empresa activa pero no clasificable por tamaño), a pesar de que la sección 4 exige tratarlas como "no clasificable". Se corrigió en `build_panels.py` (motivo `no_clasificable_tamano`) y se regeneró el panel: **64,972 filas (13.8% del panel) quedan ahora correctamente marcadas** como no clasificables por tamaño, además de las **349,960 filas (74.6%) con al menos una celda suprimida por confidencialidad** y las **7,489 filas con código 999 (sin distribuir)**.
- **`metadata_variables.csv`**: las 49 familias de variables registradas tienen `primer_anio <= ultimo_anio_disponible`; ninguna fila inconsistente.

**Regla operativa derivada de la validación**: antes de usar cualquier panel en un análisis, correr `python3 03_analisis/validar_paneles.py` si hubo cambios en los archivos originales o en `build_panels.py`, y revisar `reporte_validacion.md` en vez de asumir que los paneles siguen siendo correctos.

---

## 10. Período de análisis común

Cuando un cuadro, gráfico o mapa combina **variables de distintas fuentes en el mismo año** (no series de tiempo de una sola variable, que siguen la regla 5.2), hay que usar la intersección real de cantones y años entre esas fuentes, no asumirla. Se calculó y se dejó registrada en `01_referencia/periodos_comunes.csv`:

| Escenario | Fuentes combinadas | Período | Cantones en la intersección por año | Nota |
|---|---|---|---|---|
| **A — sin ICC** | IDH (PNUD) + PIB cantonal (BCCR) + Unidades Jurídicas cantonal (BCCR) | **2019–2022** | 2019: 82 · 2020: 82 · 2021: 82 · 2022: 84 | Es la intersección más amplia disponible en el proyecto; 2022 es el único año de este escenario con los 84 cantones completos en las tres fuentes a la vez. |
| **B — con ICC** | IDH (PNUD) + ICC (UCR) + Unidades Jurídicas cantonal (BCCR) | **2023–2024** | 2023: 81 · 2024: 82 | El PIB cantonal **no** entra en este escenario porque no cubre 2023–2024. Monteverde y Puerto Jiménez quedan fuera siempre (el ICC no los cubre); Río Cuarto además queda fuera en 2023. |
| **C — serie de tiempo de una variable** | Cualquier variable individual | Su rango completo (ver `metadata_variables.csv`) | No aplica un período común — se usa el máximo histórico de esa variable, sin recortar (regla 5.2) | Aplica, por ejemplo, a "evolución del IDH de San José 2010–2024": no se limita a 2019–2022 solo porque el PIB tenga menos años. |

**Cómo elegir el escenario en la práctica:**

1. ¿El análisis mezcla variables de más de una fuente en un mismo corte de tiempo (p. ej. "IDH vs. PIB per cápita 2022" o "ICC vs. Unidades Jurídicas 2024")? → Usar el escenario A o B según si el ICC está incluido, y declarar el número real de cantones de esa combinación específica (no asumir 84).
2. ¿El análisis es la evolución de una sola variable en el tiempo (p. ej. "serie del IDH de Puntarenas")? → Usar el escenario C (rango completo de esa variable), con la nota técnica de la sección 5.2.
3. ¿El análisis mezcla variables de distintas fuentes **y también** se quiere ver su evolución en el tiempo (p. ej. "IDH vs. PIB per cápita, 2019–2022")? → Usar el escenario A o B como período, pero declarar también, variable por variable, si algún año del período tiene menos cantones que otros (como pasa en el escenario A entre 2019–2021 y 2022).

Todo cuadro/gráfico/mapa que combine fuentes debe indicar en su nota técnica cuál de estos tres escenarios usó y cuántos cantones entraron realmente en la intersección de ese año — igual que exige la sección 5 con el año.

---

## 11. Próximos pasos sugeridos

1. ~~Validar los paneles procesados contra el inventario de la sección 3~~ — hecho, ver sección 9.
2. ~~Definir el "período de análisis común" cuando se combinen fuentes~~ — hecho, ver sección 10.
3. Decidir, para cada pregunta de análisis, si se trabaja con el universo completo de 84 cantones (aceptando huecos y reportándolos) o con el subconjunto de cantones con historia completa en todas las fuentes relevantes (escenario A o B de la sección 10).
4. A partir de ahí, iniciar el análisis cantonal propiamente dicho (rankings del último año disponible, series de tiempo, correlaciones entre desarrollo humano/competitividad/PIB/tejido empresarial, mapas, agrupamientos regionales, etc.), aplicando siempre la nota técnica de la sección 5 y el escenario de período de la sección 10.
