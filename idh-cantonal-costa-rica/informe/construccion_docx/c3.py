# -*- coding: utf-8 -*-
"""Secciones 7–10, apéndice y anexos del informe v3."""
from ctx import *
import importlib.metadata as im, sys, platform


def run(c):
    P = PCA_; K = CL; S = ESP; EJ = EJ2
    aI = T('T10a_ajustado_infra'); aP = T('T10b_ajustado_pilares'); pB = T('T11b_panelB_externo'); inf = T('T08a_q3rot_vs_resto_infraestructura')
    # ------------------------------------------------------------ 7. Discusión
    c.h1('7. Discusión', pb=True)
    c.p(f'**Estructura del desempeño cantonal.** Dentro de las siete variables analizadas, la covariación entre cantones se resume en dos dimensiones —una económico-empresarial y otra de seguridad— que explican {num(P["var12"],1)}% de la varianza. La primera es sólida; la segunda es exploratoria (su autovalor no supera el percentil 95 del análisis paralelo) y descansa principalmente en la asociación entre el ISC y el IVDAC. El hallazgo no equivale a afirmar que el comportamiento cantonal en general se reduzca a dos dimensiones: aplica al conjunto específico de variables disponibles, y la inclusión de otras (capital social, migración, gestión ambiental) podría revelar dimensiones adicionales. Lo que sí respalda la evidencia es que, dentro de ese conjunto, la posición de un cantón en el eje económico no predice su posición en el eje de seguridad: ambos ejes son ortogonales por construcción, y las variables que los definen (ICC, PIB per cápita y unidades jurídicas, por un lado; ISC e IVDAC, por otro) muestran correlaciones cruzadas débiles a moderadas (por ejemplo, ICC–ISC r = 0,32; PIB per cápita–ISC r = 0,18).')
    c.p(f'**Clasificación en cuadrantes.** La rotación varimax produce ejes interpretables, y los puntajes rotados son coherentes con las cargas (r = {num(P["r_eje_seg_directo_ISC"],2)} entre el eje de seguridad y el ISC). Pero la partición de los cantones en cuatro cuadrantes impone umbrales arbitrarios sobre un continuo: {P["n_frontera"]} de 82 cantones están cerca de un umbral, el solapamiento de Q3 entre escenarios de sensibilidad va de 0,60 a 0,87 y la probabilidad media de pertenencia es de {num(P["prob_media"],2)}. La corrección del cálculo de los puntajes modificó la asignación de {P["n_cambian"]} cantones, lo que muestra el riesgo de usar los cuadrantes como categorías firmes. El agrupamiento K-means no aporta una verificación independiente: su separación es débil, la solución de k = 4 es inestable, y la concordancia con los cuadrantes es moderada. La estructura que mejor se sostiene es el gradiente continuo bidimensional, y los cuadrantes son una forma conveniente, no única ni definitiva, de describirlo.')
    c.p('**El cuadrante Q3 y la infraestructura.** La versión 2 concluía que la brecha de Q3 se concentraba en infraestructura pública y no en conectividad. El análisis recalculado matiza ese hallazgo en tres aspectos. Primero, la composición de Q3 cambia (23 cantones, 15 comunes con la versión previa), y con ella la lectura de los pilares: los siete pilares del ICC son menores en Q3, no solo los de infraestructura e innovación. Segundo, los indicadores de infraestructura son puntajes normalizados y, en su mayoría, medidas de densidad por superficie; su correlación con la densidad poblacional es de 0,62 a 0,99 y, al controlarla junto con la región, las brechas de pavimentación, sucursales, electricidad y gasto vial desaparecen. Esto es compatible con que Q3 sea sobre todo un conjunto de cantones rurales, de baja densidad, donde esos indicadores por kilómetro cuadrado son estructuralmente bajos, y no permite afirmar que exista un rezago específico de infraestructura de acceso. Tampoco permite descartarlo: la medición de acceso requiere indicadores de otra naturaleza. Tercero, en la conectividad el panorama es mixto: la cobertura móvil es equivalente entre grupos, la velocidad no es concluyente, el acceso a Internet de hogares es menor en Q3 con evidencia no robusta, y la proporción de llamadas completadas es mayor, en sentido contrario al esperado.')
    c.p(f'**Pilares y gobernanza.** Tras el ajuste por densidad y región, los pilares Económico y de Gobierno mantienen diferencias de magnitud moderada (≈ −0,60 DE) con q = {num(aP.q_sem[0],3)}, es decir, no superan el umbral convencional al controlar por comparaciones múltiples, pero tampoco se desvanecen. Los datos son compatibles con que, más allá de la ruralidad, Q3 tenga una menor capacidad económica e institucional relativa; la evidencia es sugestiva y requiere una muestra mayor o un diseño distinto para decidir.')
    c.p(f'**El eje de seguridad.** Con la comparación externa (eje sin la familia evaluada), los pilares Innovación, Calidad de vida e Infraestructura del ICC se asocian positivamente con el eje de seguridad, y los pilares Económico, Empresarial y Laboral no. Esto es coherente con la idea de que la seguridad se relaciona más con las capacidades colectivas y el entorno que con la actividad económica privada por sí misma, pero la asociación es transversal y no permite distinguir dirección ni mecanismo: la seguridad puede ser tanto causa como consecuencia de la inversión y la innovación. Entre los componentes del IVDAC, Demanda y Manifestación de violencia se asocian de forma similar con el eje, y no hay base para jerarquizar uno sobre otro; la implicación de política de la versión 2 (priorizar violencia sobre consumo) no se sostiene con estos datos.')
    c.p(f'**Dependencia espacial.** La autocorrelación positiva es fuerte (I de Moran de {num(S["moran_E"],2)} y {num(S["moran_S"],2)} en los ejes) y los residuos de varios modelos ajustados conservan dependencia espacial, por lo que los valores p de los contrastes clásicos subestiman la incertidumbre. Los análisis con modelo de error espacial son más prudentes y se privilegian para las conclusiones sobre la persistencia de diferencias. El agrupamiento de cantones del eje económico en torno al Gran Área Metropolitana es claro; en seguridad, ningún cantón destaca tras el control de comparaciones múltiples.')
    c.p('**Implicaciones.** El informe describe asociaciones y posiciones relativas; no establece causalidad ni evalúa necesidades. Sus resultados son útiles para (i) plantear hipótesis de diagnóstico, (ii) identificar cantones cuya situación conviene verificar con indicadores físicos de acceso (Talamanca, Matina, Hojancha, Buenos Aires y Coto Brus) y (iii) mostrar qué tipo de indicadores no permiten decidir entre explicaciones alternativas. No sustituyen un diagnóstico territorial con datos directos ni deben usarse como criterio de asignación de recursos.')

    # ------------------------------------------------------------ 8. Limitaciones
    c.h1('8. Limitaciones')
    c.h2('8.1 Temporalidad y denominadores')
    c.p('Las variables corresponden a años distintos (2022 a 2025); el PIB per cápita de 2022 es hasta tres años anterior a otras variables y se divide por una población proyectada para 2024, mientras que el ICC publica también la población de 2023 con cifras distintas (ediciones de proyección diferentes). La población de 2022 no está en el repositorio. La clasificación es robusta a usar la población 2023 (clasificación idéntica), pero no a la ventana común 2022–2023, que reduce Q3 a 17 cantones (ARI = 0,52). El análisis es transversal: no permite evaluar estabilidad temporal ni dirección causal.')
    c.h2('8.2 Medición')
    c.p('Los indicadores de infraestructura y conectividad son puntajes normalizados de 0 a 100 elaborados por el ICC, no mediciones físicas; dos de ellos incorporan una transformación logarítmica y varios son densidades por superficie, que no equivalen a acceso. El indicador de Internet proviene de ENAHO, una encuesta de hogares cuyo diseño muestral no está pensado para estimaciones cantonales; su precisión a ese nivel no fue verificada. El PIB per cápita es una medida aproximada por el desajuste entre numerador y denominador. El IPM tiene un único corte (2024). Los indicadores del ICC y del PNUD son, además, índices compuestos cuyas ponderaciones internas no se evaluaron aquí.')
    c.h2('8.3 Inferencia')
    c.p('Los 82 cantones son un censo; los valores p, los intervalos y la FDR describen estabilidad frente a remuestreo y ajuste, no inferencia a una población. Se realizaron numerosos contrastes; aunque se controló la tasa de descubrimiento falso dentro de familias definidas, las decisiones de análisis (transformaciones, escenarios, modelos) ofrecen grados de libertad del investigador que no se cuantifican. El tamaño de Q3 (23 cantones) limita la potencia de los contrastes y de los modelos ajustados, cuyos intervalos son amplios. Los tamaños de efecto y los intervalos deben pesar más que el valor p.')
    c.h2('8.4 Dependencia espacial')
    c.p('Los cantones vecinos son similares, y los contrastes de grupos que asumen independencia subestiman la incertidumbre. Se emplearon modelos de error espacial y permutaciones, pero la matriz de contigüidad reina es una de varias especificaciones posibles, y no se evaluaron modelos con efectos de desborde (rezago espacial) ni regresión geográficamente ponderada. El mapa utiliza límites administrativos de 2022 (OCHA/HDX) que difieren en trazos menores de la división territorial 2026 y se presenta como apoyo visual.')
    c.h2('8.5 Circularidad y construcción de los ejes')
    c.p('Los pilares del ICC y los componentes del IVDAC forman parte de los índices que definen los ejes. La descomposición interna es descriptiva; la comparación externa (eje sin la familia evaluada) mitiga pero no elimina la dependencia, porque los demás componentes del mismo instituto o metodología comparten información. El segundo componente descansa en el par ISC–IVDAC y no supera el percentil 95 del análisis paralelo. Los cuadrantes dependen de umbrales arbitrarios en cero, por lo que la clasificación individual es incierta para 36 cantones cercanos a un umbral.')
    c.h2('8.6 Generalización')
    c.p('Los resultados describen a los 82 cantones en los años indicados y con las siete variables incluidas; no se extienden a otros años, a otras variables ni a la escala de distritos u hogares (falacia ecológica). El análisis ponderado por población muestra que las conclusiones para cantones no son necesariamente las mismas que para la población. El índice de rezago es relativo al conjunto de los 82 cantones y a los ocho indicadores normalizados disponibles.')

    # ------------------------------------------------------------ 9. Recomendaciones
    c.h1('9. Recomendaciones')
    c.bl([
        'Replicar el análisis en una ventana de tiempo común y, de existir, con series de 2019 a 2022, para evaluar si la disociación entre las dimensiones económica y de seguridad es estable en el tiempo o específica del corte 2022–2025, usando un mismo denominador poblacional para todas las variables.',
        'Validar con indicadores físicos de acceso —por ejemplo, porcentaje de viviendas con servicio eléctrico, kilómetros de red vial pavimentada por habitante y distancia a servicios financieros y de salud— los cinco casos señalados (Talamanca, Matina, Hojancha, Buenos Aires y Coto Brus) antes de cualquier decisión de asignación de recursos.',
        'Medir el acceso y no solo la densidad: sustituir o complementar los puntajes normalizados del ICC por indicadores de acceso en unidades físicas o poblacionales, y evaluar la conectividad móvil y de Internet con mediciones directas.',
        'Incorporar la estructura espacial en los análisis futuros (modelos de rezago y de error espacial, regresión geográficamente ponderada) y evaluar otras especificaciones de vecindad.',
        'Tratar el eje de seguridad con mediciones desagregadas y con comparación externa, sin construir el eje con las variables que luego se quieran explicar, y recopilar información sobre violencia y consumo a escala cantonal que permita jerarquizar componentes.',
        'Actualizar el PIB per cápita cantonal en cuanto el BCCR publique cifras posteriores a 2022 y completar la cobertura de los cantones sin datos de ICC, y repetir el análisis para verificar si el desfase temporal afecta los resultados.',
        'Si se desea un diseño explicativo, abordarlo con datos de panel y supuestos de identificación explícitos; el diseño actual no permite estimar efectos causales.',
    ])

    # ------------------------------------------------------------ 10. Bibliografía
    c.h1('10. Fuentes de datos y bibliografía')
    c.sub('Fuentes de datos')
    c.p('Se distingue la edición citada, el año de observación del dato (Tabla 2) y la fecha de acceso. Esta última no quedó registrada en los metadatos del repositorio; la integridad de los archivos se documenta con sumas SHA-256 (Anexo E).')
    refs_d = [
        'Banco Central de Costa Rica. (2023). *PIB cantonal para Costa Rica, 2019-2022* [Conjunto de datos]. BCCR. (Año de observación utilizado: 2022).',
        'Banco Central de Costa Rica. (2025). *Estadísticas de Unidades Jurídicas, 2005-2024. Registro de Variables Económicas (REVEC)* [Conjunto de datos]. BCCR. (Año de observación utilizado: 2024).',
        'Escuela de Economía, Universidad de Costa Rica. (2024). *Índice de Competitividad Cantonal (ICC) 2023-2024: índice general, siete pilares e indicadores base de infraestructura y conectividad* [Conjunto de datos]. UCR. (Años de observación: 2023 y 2024).',
        'Observatorio del Desarrollo. (2026). *Documentación interna del repositorio cantonal: manual de uso, diccionario de variables y paneles procesados* [Documento interno no publicado]. Universidad de Costa Rica.',
        'Programa de las Naciones Unidas para el Desarrollo. (2026). *Atlas de Desarrollo Humano Cantonal 2026: Índice de Desarrollo Humano, Índice de Seguridad Ciudadana, Índice de Pobreza Multidimensional e Índice de Vulnerabilidad a Drogas y Actividades Conexas*. PNUD Costa Rica. (Años de observación: 2024 y 2025).',
        'Registro Nacional, Instituto Geográfico Nacional. (2026). *División Territorial Administrativa de Costa Rica 2026*. Registro Nacional.',
        'United Nations Office for the Coordination of Humanitarian Affairs y Humanitarian Data Exchange. (2022). *Costa Rica — Subnational Administrative Boundaries (COD-AB), versión 01* [Conjunto de datos]. https://data.humdata.org/dataset/cod-ab-cri',
    ]
    for r in refs_d: c.add(D.bullet(r))
    c.sub('Referencias metodológicas y software')
    refs_m = [
        'Anselin, L. (1995). Local indicators of spatial association—LISA. *Geographical Analysis, 27*(2), 93–115.',
        'Benjamini, Y., y Hochberg, Y. (1995). Controlling the false discovery rate: A practical and powerful approach to multiple testing. *Journal of the Royal Statistical Society: Series B, 57*(1), 289–300.',
        'Gower, J. C. (1971). A general coefficient of similarity and some of its properties. *Biometrics, 27*(4), 857–871.',
        'Hodges, J. L., y Lehmann, E. L. (1963). Estimation of location based on ranks. *Annals of Mathematical Statistics, 34*(2), 598–611.',
        'Horn, J. L. (1965). A rationale and test for the number of factors in factor analysis. *Psychometrika, 30*(2), 179–185.',
        'Hubert, L., y Arabie, P. (1985). Comparing partitions. *Journal of Classification, 2*(1), 193–218.',
        'Kaiser, H. F. (1958). The varimax criterion for analytic rotation in factor analysis. *Psychometrika, 23*(3), 187–200.',
        'Kerby, D. S. (2014). The simple difference formula: An approach to teaching nonparametric correlation. *Comprehensive Psychology, 3*, Artículo 11.IT.3.1.',
        'Lakens, D. (2017). Equivalence tests: A practical primer for t tests, correlations, and meta-analyses. *Social Psychological and Personality Science, 8*(4), 355–362.',
        'Lorenzo-Seva, U., y ten Berge, J. M. F. (2006). Tucker’s congruence coefficient as a meaningful index of factor similarity. *Methodology, 2*(2), 57–64.',
        'Moran, P. A. P. (1950). Notes on continuous stochastic phenomena. *Biometrika, 37*(1–2), 17–23.',
        'Pedregosa, F., Varoquaux, G., Gramfort, A., Michel, V., Thirion, B., Grisel, O., … Duchesnay, É. (2011). Scikit-learn: Machine learning in Python. *Journal of Machine Learning Research, 12*, 2825–2830.',
        'Rey, S. J., y Anselin, L. (2007). PySAL: A Python library of spatial analytical methods. *The Review of Regional Studies, 37*(1), 5–27.',
        'Robinson, W. S. (1950). Ecological correlations and the behavior of individuals. *American Sociological Review, 15*(3), 351–357.',
        'Rousseeuw, P. J. (1987). Silhouettes: A graphical aid to the interpretation and validation of cluster analysis. *Journal of Computational and Applied Mathematics, 20*, 53–65.',
        'Schuirmann, D. J. (1987). A comparison of the two one-sided tests procedure and the power approach for assessing the equivalence of average bioavailability. *Journal of Pharmacokinetics and Biopharmaceutics, 15*(6), 657–680.',
        'Seabold, S., y Perktold, J. (2010). statsmodels: Econometric and statistical modeling with Python. *Proceedings of the 9th Python in Science Conference*, 92–96.',
        'Virtanen, P., Gommers, R., Oliphant, T. E., Haberland, M., Reddy, T., Cournapeau, D., … SciPy 1.0 Contributors. (2020). SciPy 1.0: Fundamental algorithms for scientific computing in Python. *Nature Methods, 17*, 261–272.',
    ]
    for r in refs_m: c.add(D.bullet(r))

    # ------------------------------------------------------------ Apéndice A
    c.h1('Apéndice A. Ficha de reproducción', pb=True)
    c.p('Este apéndice sustituye al código que la versión 2 incluía en el cuerpo del documento. El código, los datos de entrada, los resultados de referencia y las instrucciones completas se entregan en la carpeta reproducibilidad_v3/ (README.md). Aquí se registran únicamente los elementos necesarios para auditar y volver a ejecutar el análisis.')
    c.h2('A.1 Entorno y ejecución')
    pk = ['numpy', 'pandas', 'scipy', 'scikit-learn', 'statsmodels', 'factor_analyzer', 'libpysal', 'esda', 'spreg', 'geopandas', 'shapely', 'matplotlib', 'python-docx']
    ver = {}
    for k in pk:
        try: ver[k] = im.version(k)
        except Exception: ver[k] = '—'
    rows = [['Python', platform.python_version()]] + [[k, ver[k]] for k in pk] + [
        ['Semilla maestra', str(SEED)], ['Bootstrap (percentil)', f'{B_BOOT:,}'.replace(',', '.') + ' remuestreos (2.000 para cargas del PCA; 1.000 para pertenencia a cuadrantes; 400 para estabilidad de K-means)'],
        ['Permutaciones espaciales', f'{N_PERM:,}'.replace(',', '.')], ['Inicializaciones de K-means', '300 (mejor inercia)'],
        ['Orden de ejecución', 'python run_all.py (ejecuta los scripts 00 a 09 en secuencia)'],
        ['Verificación de reproducción', 'python 10_verificar_reproduccion.py'],
    ]
    c.tabla('entorno', 'Entorno de ejecución y parámetros de simulación. Las versiones corresponden a las usadas para producir las cifras de este informe (archivo requirements.txt del paquete).', ['Elemento', 'Versión o valor'], rows, [2600, 7000], ['left', 'left'], sz=17)
    vr = f'{TAB}/_verificacion_reproduccion.json'
    c.h2('A.2 Verificación de reproducción y validación metodológica')
    if os.path.exists(vr):
        V = json.load(open(vr))
        c.p(f'**Verificación de reproducción.** El script 10_verificar_reproduccion.py ejecuta todo el procesamiento desde cero en un directorio limpio ({V["entorno"]}) y compara cada tabla resultante con la tabla de referencia entregada: {V["n_iguales"]} de {V["n_tablas"]} tablas coinciden dentro de la tolerancia numérica de {V["tol"]} (diferencia máxima observada: {V["max_diff"]}). Esto demuestra que el código reproduce las cifras de este informe; no demuestra que la metodología sea correcta.')
    else:
        c.p('**Verificación de reproducción.** Pendiente de ejecución.')
    c.p(f'**Validación metodológica independiente.** El script 09_validacion_independiente.py reimplementa desde cero, con NumPy y SciPy, los cálculos centrales y los compara con las funciones de librería utilizadas: autovalores (diferencia máxima {VAL["eig_max_abs_diff"]:.1e}), varimax con normalización de Kaiser (diferencia máxima en cargas {VAL["varimax_max_abs_diff_cargas"]:.1e}, atribuible a la tolerancia de convergencia de factor_analyzer), puntajes rotados (diferencia máxima {VAL["puntajes_rotados_max_abs_diff"]:.1e}; correlación entre ejes {VAL["corr_puntajes_ortogonales"]:.0e}; varianza de los puntajes igual a 1), comunalidades, KMO, I de Moran (diferencia máxima {VAL["moran_max_abs_diff"]:.1e}), ajuste de Benjamini–Hochberg frente a statsmodels, rank-biserial por dos fórmulas, intervalo de Fisher frente a SciPy y asignación de cuadrantes (concordancia de {num(VAL["cuadrantes_iguales_pct"],0)}%). Todas las comprobaciones pasan: {"sí" if VAL["todo_ok"] else "no"}.')
    c.p('Los resultados con simulación (bootstrap, permutaciones, K-means con múltiples inicializaciones) dependen de la semilla y de la versión de las librerías; el paquete entrega los resultados de referencia para comparar. La tabla A03 del paquete y el Anexo E registran las sumas de verificación de las entradas.')

    # ------------------------------------------------------------ Anexos
    c.h1('Anexo B. Correlaciones entre las siete variables', pb=True)
    cr = T('T02_correlaciones_21_pares')
    rows = [[f'{r.var1} — {r.var2}', num(r.r_pearson, 2), f'{num(r.fisher_lo,2)}; {num(r.fisher_hi,2)}', f'{num(r.ic_lo,2)}; {num(r.ic_hi,2)}', num(r.rho_spearman, 2), f'{num(r.rho_lo,2)}; {num(r.rho_hi,2)}', pf(r.q_fdr_pearson), pf(r.q_fdr_spearman), num(r.r_pearson_logPIB, 2)] for r in cr.itertuples()]
    c.tabla('corr21', 'Los 21 pares de correlaciones (n = 82). IC Fisher e IC bootstrap: intervalos del 95% de la r de Pearson; IC ρ: bootstrap del coeficiente de Spearman; q: FDR (familia F1, 21 pruebas) para Pearson y Spearman; r (ln PIB): Pearson con el logaritmo del PIB per cápita.',
            ['Par', 'r', 'IC Fisher', 'IC boot.', 'ρ', 'IC ρ', 'q Pearson', 'q Spearman', 'r (ln PIB)'], rows, [2750, 560, 1050, 1050, 560, 1050, 700, 750, 700], sz=14)

    c.h1('Anexo C. Clasificación cantonal y perfil de los cuadrantes', pb=True)
    q = T('T04b_cuadrantes_canton_por_canton'); pbt = T('T05c_estabilidad_cuadrante_bootstrap').set_index('canton'); fr = set(T('T04c_cantones_frontera').canton)
    rows = [[r.canton, r.provincia, num(r.E_rot, 2), num(r.S_rot, 2), r.cuadrante_original, r.cuadrante_rotado, 'Sí' if r.cambia == 'Sí' else '—', num(pbt.loc[r.canton, 'prob_cuadrante_asignado'], 2), 'Sí' if r.canton in fr else '—'] for r in q.itertuples()]
    c.tabla('cantones', 'Puntajes rotados de los 82 cantones, cuadrante de la versión 2 (sin rotar) y de la versión 3 (rotado), si cambia, probabilidad de pertenencia al cuadrante asignado (1.000 soluciones bootstrap) y cantón frontera (|puntaje| < 0,25 respecto de algún umbral). E: eje económico-empresarial; S: eje de seguridad.',
            ['Cantón', 'Provincia', 'E', 'S', 'v2', 'v3', 'Cambia', 'Prob. pert.', 'Frontera'], rows, [1900, 1300, 750, 750, 650, 650, 800, 1000, 900], sz=15)
    pi = T('T12_perfil_cuadrantes_rotados')
    vv = [('IDH_2024', 'IDH', 3), ('ICC_2024', 'ICC', 1), ('PIB_percapita_2022', 'PIB pc', 1), ('UJ_por_1000hab_2024', 'UJ', 1), ('ISC_2025', 'ISC', 3), ('IPM_2024', 'IPM', 3), ('IVDAC_2024', 'IVDAC', 3)]
    rows = [[NOM_ for NOM_ in [r.cuadrante]] + [f'{num(getattr(r, v + "_med"), d)} [{num(getattr(r, v + "_q1"), d)}; {num(getattr(r, v + "_q3"), d)}]' for v, _, d in vv] for r in pi.itertuples()]
    c.tabla('perfil_iqr', 'Mediana [Q1; Q3] de cada variable por cuadrante rotado.', ['Cuad.'] + [n for _, n, _ in vv], rows, [700] + [1300] * 7, sz=14)

    c.h1('Anexo D. Resultados completos del Ejercicio 2')
    inf = T('T08a_q3rot_vs_resto_infraestructura'); pil = T('T08b_q3rot_vs_resto_pilares'); al = pd.concat([inf, pil], ignore_index=True)
    rows = [[r.variable, num(r.d, 2), f'{num(r.d_lo,2)}; {num(r.d_hi,2)}', f'{num(r.d_ic90_lo,2)}; {num(r.d_ic90_hi,2)}', pf(r.p_tost), 'Sí' if r.equivalente == 'Sí' else 'No concluyente', pf(r.p_mw)] for r in al.itertuples()]
    c.tabla('tost', 'Tamaño de efecto estandarizado (d de Cohen; Q3 − resto) con IC 95% bootstrap, prueba de equivalencia TOST (margen ±0,5 DE; IC 90% de d) y valor p de Mann–Whitney sin ajustar. «Sí»: equivalencia demostrada (p TOST < 0,05); «No concluyente»: no se demuestra equivalencia.',
            ['Indicador', 'd', 'IC 95% de d', 'IC 90% de d', 'p TOST', 'Equivalencia', 'p M–W'], rows, [2700, 600, 1400, 1400, 800, 1500, 800], sz=15)
    a1 = T('T08e_q3sinICC_vs_resto_infraestructura'); a2 = T('T08f_q3sinICC_vs_resto_pilares'); b = pd.concat([T('T08a_q3rot_vs_resto_infraestructura'), T('T08b_q3rot_vs_resto_pilares')], ignore_index=True); b1 = pd.concat([a1, a2], ignore_index=True)
    rows = [[r0.variable, f'{num(r0.rb,2)} [{num(r0.rb_lo,2)}; {num(r0.rb_hi,2)}]', pf(r0.q_fdr), f'{num(r1.rb,2)} [{num(r1.rb_lo,2)}; {num(r1.rb_hi,2)}]', pf(r1.q_fdr)] for r0, r1 in zip(b.itertuples(), b1.itertuples())]
    c.tabla('q3sinicc', 'Contraste de Q3 definido con la solución base (n = 23) y con la solución sin ICC (n = 24): rank-biserial con IC 95% bootstrap y q (FDR).',
            ['Indicador', 'rb base [IC 95%]', 'q base', 'rb sin ICC [IC 95%]', 'q sin ICC'], rows, [2900, 2000, 800, 2000, 900], sz=15)
    c.p('Los modelos ajustados con errores robustos HC3 (MCO) dan resultados cualitativamente similares a los del modelo de error espacial de la ' + TN('infra') + ' y de la ' + TN('pilares') + ': tras controlar por densidad y región, los coeficientes de Q3 para pavimentación, sucursales, electricidad y gasto vial son cercanos a cero (entre −0,09 y 0,07 DE en MCO). Los residuos de MCO presentan autocorrelación espacial significativa en cinco de los ocho indicadores (I de Moran de los residuos de 0,19 a 0,25; Tabla T10a del paquete), lo que respalda el uso del modelo de error espacial.')

    c.h1('Anexo E. Dependencia espacial, ponderación y archivos fuente')
    w = T('T13_q3_ponderado_vs_no_ponderado')
    rows = [[r.variable, f'{num(r.dif_media_no_pond,1)} [{num(r.lo_u,1)}; {num(r.hi_u,1)}]', f'{num(r.dif_media_pond,1)} [{num(r.lo_w,1)}; {num(r.hi_w,1)}]', num(r.dif_est_no_pond, 2), num(r.dif_est_pond, 2), r.misma_direccion] for r in w.itertuples()]
    c.tabla('ponder', 'Diferencia de medias Q3 − resto (en las unidades de cada indicador) sin ponderar y ponderada por población (2024), con IC bootstrap del 95%, y diferencia estandarizada (en DE del indicador).',
            ['Indicador', 'Sin ponderar [IC]', 'Ponderada [IC]', 'DE no pond.', 'DE pond.', 'Mismo sentido'], rows, [2700, 1900, 1900, 900, 900, 900], sz=15)
    mo = T('T14_moran_global')
    rows = [[r.variable, num(r.I, 3), num(r.z_sim, 2), pf(r.p_sim), pf(r.q_fdr)] for r in mo.itertuples()]
    c.tabla('moran_full', 'I de Moran global de las 28 variables y ejes (contigüidad reina, 9.999 permutaciones; q: FDR en la familia F5). E(I) = −0,012.',
            ['Variable', 'I', 'z', 'p', 'q (FDR)'], rows, [3900, 1100, 1100, 1100, 1100], sz=15)
    h = T('A03_hashes_archivos_fuente')
    rows = [[r.archivo, f'{r.bytes:,}'.replace(',', '.'), r.sha256[:16] + '…' + r.sha256[-8:]] for r in h.itertuples()]
    c.tabla('hashes', 'Archivos fuente utilizados: tamaño en bytes y suma SHA-256 (se muestran los primeros 16 y los últimos 8 caracteres; la suma completa figura en el paquete reproducibilidad_v3/ en resultados_referencia/tablas/A03_hashes_archivos_fuente.csv).',
            ['Archivo', 'Bytes', 'SHA-256'], rows, [4200, 1500, 3900], ['left', 'right', 'left'], sz=15)
