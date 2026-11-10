"""Módulo Parte 3 (V6 — 40 a 45 páginas): Capítulo 3 (Objetivos y Metodología de Trabajo
100% cerrado y formalizado con las Figuras 3.1 a 3.4 y Tablas 3.1 y 3.2) y Capítulo 4
(Marco Normativo, Ético y de Propiedad Intelectual con la Tabla 4.1).
"""

from __future__ import annotations

from pathlib import Path
from docx import Document

from entrega2_v6_part1 import add_v6_figure, add_v6_table
from src.analytics.multivariate_engine import MultivariateModelArtifacts


def write_chapter_3_metodologia(
    doc: Document, artifacts: MultivariateModelArtifacts, figures_dir: Path
) -> None:
    """Redacta de forma exhaustiva el Capítulo 3 (Objetivos y Metodología de Trabajo — Págs. 20-31)."""
    hr = artifacts.health_report
    opt = artifacts.optimal_cluster_metrics

    doc.add_heading("CAPÍTULO 3. OBJETIVOS Y METODOLOGÍA DE TRABAJO", level=1)

    # =========================================================================
    # 3.1. OBJETIVO GENERAL Y OBJETIVOS ESPECÍFICOS
    # =========================================================================
    doc.add_heading("3.1. Objetivo General y Objetivos Específicos", level=2)
    doc.add_paragraph(
        "El objetivo general del presente Trabajo Fin de Máster se formula en términos medibles y verificables "
        "como sigue: Diseñar, implementar y validar empíricamente un prototipo de Sistema de Apoyo a la Decisión "
        "(DSS) basado en una arquitectura de datos Lakehouse Medallion, aprendizaje estadístico multivariante no "
        "supervisado y analítica visual interactiva, capaz de integrar métricas técnico-tácticas ajustadas por "
        "posesión y variables de coste económico-financiero en las seis principales ligas europeas para detectar "
        "ineficiencias de valoración de mercado (Net Value) y recuperar clones estadísticos de futbolistas."
    )
    doc.add_paragraph(
        "Para materializar de forma sistemática este propósito general y asegurar su plena trazabilidad con los "
        "módulos de software desarrollados en el repositorio del proyecto, se establecen seis objetivos "
        "específicos formulados en infinitivo y vinculados a umbrales cuantitativos de verificación:"
    )
    doc.add_paragraph(
        "En primer lugar (OE1), construir un pipeline de ingesta automatizada y persistencia documental en la "
        "capa Bronze (MongoDB y respaldo transaccional JSON Lines) conectado al servicio API-Football REST v3 "
        "mediante extracción por lotes de clubes (TeamBatchLiveExtractor), control de tasa (Rate Limiting de "
        "100 peticiones diarias y cadencia de 6,5 segundos), retroceso exponencial y sellado criptográfico "
        "SHA-256 sobre la totalidad de las plantillas de La Liga, Premier League, Serie A, Bundesliga, Ligue 1 "
        "y Eredivisie (4.460 registros brutos y 3.443 futbolistas únicos)."
    )
    doc.add_paragraph(
        "En segundo lugar (OE2), implementar un motor híbrido de resolución de entidades (Entity Matching) en "
        "tres niveles secuenciales —diccionario determinístico Crosswalk Reep Register, bloqueo biométrico por "
        "año de nacimiento y nacionalidad, y distancia de edición normalizada de Levenshtein combinada con "
        "token_sort_ratio >= 0,85 en RapidFuzz— que enlace sin falsos positivos las estadísticas deportivas "
        "con las valoraciones de mercado de Transfermarkt y los salarios brutos anuales de Capology."
    )
    doc.add_paragraph(
        "En tercer lugar (OE3), desarrollar la capa Silver de ingeniería de características deportivas y "
        "financieras sobre almacenamiento columnar Apache Parquet y DuckDB, ejecutando la validación "
        "contractual IngestionGate (JSON Schema Draft 2020-12 y filtro >= 600 minutos disputados, promoviendo "
        f"N = {hr.sample_size} jugadores), la relativización de métricas por 90 minutos, el ajuste contextual "
        "defensivo al 50% de posesión (mitigando la Paradoja de Sobiech) y la normalización paramétrica de "
        "potencia de Yeo-Johnson."
    )
    doc.add_paragraph(
        "En cuarto lugar (OE4), programar la compuerta de gobernanza psicométrica ModelHealthGate para auditar "
        f"la matriz de correlaciones muestrales (verificando N = {hr.sample_size} >= 300, índice global de "
        f"Kaiser-Meyer-Olkin KMO = {hr.kmo_global:.4f} >= 0,70 y prueba de esfericidad de Bartlett con "
        f"Chi-cuadrado = {hr.bartlett_chi2:,.2f}, p < 0,05) y ejecutar el Análisis de Componentes Principales "
        f"(ACP) reteniendo d = {artifacts.n_components_retained} factores ortogonales que explican el "
        f"{artifacts.cumulative_variance * 100:.2f}% de la varianza común."
    )
    doc.add_paragraph(
        "En quinto lugar (OE5), entrenar y validar cruzadamente en la capa Gold los algoritmos de agrupamiento "
        "particional (K-Means) y jerárquico aglomerativo (Método de Mínima Varianza de Ward) sobre el subespacio "
        f"latente del ACP, seleccionando la partición óptima (K* = {opt.k_clusters}) mediante los índices de "
        f"Silueta ({opt.silhouette_kmeans:.4f}), Caliński-Harabasz ({opt.calinski_harabasz_kmeans:.2f}) y "
        f"Davies-Bouldin ({opt.davies_bouldin_kmeans:.4f}), exigiendo una concordancia inter-algorítmica medida "
        f"por el Índice de Rand Ajustado de ARI = {opt.adjusted_rand_index:.4f} >= 0,70, e indexando un buscador "
        "de clones tácticos mediante k-Nearest Neighbors (k-NN)."
    )
    doc.add_paragraph(
        "En sexto lugar (OE6), formular el indicador econométrico diferencial Net Value = Z_ACP_Rendimiento - "
        "Z_Coste_Financiero para clasificar la cohorte europea en cuatro cuadrantes estratégicos y desplegar "
        "una interfaz interactiva de Visual Analytics en Streamlit estructurada en cinco vistas operativas con "
        "recomendaciones prescriptivas Next Best Action (NBA)."
    )

    # =========================================================================
    # 3.2. MARCO METODOLÓGICO DUAL: DSRM ARTICULADA CON CRISP-DM
    # =========================================================================
    doc.add_heading(
        "3.2. Marco Metodológico Dual: Metodología de Ciencia del Diseño (DSRM - Peffers et al., 2007) articulada con CRISP-DM",
        level=2,
    )
    doc.add_paragraph(
        "Dado que el presente Trabajo Fin de Máster se enmarca en la Tipología 2 (Desarrollo de Software y "
        "Construcción de Prototipos Analíticos) del Reglamento de la Escuela Superior de Ingeniería y Tecnología "
        "de la UNIR, el diseño metodológico requiere un marco dual que gobierne simultáneamente la ingeniería "
        "del artefacto de software y el ciclo de vida del modelado estadístico de datos masivos. Para ello, se "
        "articula la Metodología de Investigación en Ciencia del Diseño (Design Science Research Methodology, "
        "DSRM) formalizada por Hevner et al. (2004) y Peffers et al. (2007) con el estándar industrial "
        "Cross-Industry Standard Process for Data Mining (CRISP-DM) establecido por Wirth e Hipp (2000) y "
        "Chapman et al. (2000)."
    )
    doc.add_paragraph(
        "La Ciencia del Diseño (DSRM; Peffers et al., 2007) sostiene que el conocimiento científico en ingeniería "
        "de sistemas de información se genera y valida a través de la creación rigurosa de artefactos innovadores "
        "(modelos, algoritmos, arquitecturas e interfaces) destinados a resolver problemas organizacionales no "
        "triviales. Peffers et al. (2007) estructuran este proceso en seis actividades secuenciales e iterativas: "
        "(1) identificación del problema y motivación; (2) definición de los objetivos cuantitativos de la "
        "solución; (3) diseño y desarrollo arquitectónico del artefacto; (4) demostración operativa del artefacto "
        "en un escenario real; (5) evaluación empírica de su rendimiento frente a métricas formales; y (6) "
        "comunicación científica de los resultados."
    )
    doc.add_paragraph(
        "Por su parte, el estándar CRISP-DM (Wirth & Hipp, 2000) proporciona la granularidad operativa necesaria "
        "para gobernar las transformaciones estadísticas dentro de las actividades de desarrollo y evaluación de "
        "DSRM, dividiendo el flujo analítico en seis fases: Comprensión del Negocio (Business Understanding), "
        "Comprensión de los Datos (Data Understanding), Preparación de los Datos (Data Preparation), Modelado "
        "(Modeling), Evaluación (Evaluation) y Despliegue (Deployment). Como se detalla en la Tabla 3.1, la "
        "hibridación de ambos marcos garantiza que ninguna decisión de programación en Python carezca de "
        "fundamento teórico en el dominio del scouting y que ninguna transformación matemática se ejecute sin "
        "una puerta de validación de software."
    )

    add_v6_table(
        doc=doc,
        table_number="3.1",
        title="Articulación metodológica dual entre Design Science Research Methodology (DSRM), CRISP-DM y la arquitectura del software.",
        headers=[
            "Actividad DSRM (Peffers et al., 2007)",
            "Fase Equivalente en CRISP-DM (Wirth & Hipp, 2000)",
            "Capa Medallion y Módulos Python Implementados",
            "Artefacto Verificable y Criterio de Calidad",
        ],
        rows=[
            [
                "1. Identificación del Problema y Motivación",
                "Fase 1: Comprensión del Negocio (Business Understanding)",
                "Definición de ontologías financieras y sesgos cognitivos (Capítulos 1 y 2).",
                "Delimitación del sesgo de posesión (Sobiech) y fragmentación de fuentes.",
            ],
            [
                "2. Definición de Objetivos de la Solución",
                "Fase 2: Comprensión de los Datos (Data Understanding)",
                "src/ingestion/api_client.py, live_extractor.py, mongo_loader.py (Capa Bronze).",
                "Extracción de 6 ligas (4.460 registros, 3.443 únicos) con hash SHA-256.",
            ],
            [
                "3. Diseño y Desarrollo del Artefacto",
                "Fase 3: Preparación de los Datos (Data Preparation)",
                "src/ingestion/fuzzy_matcher.py, data_contracts.py, feature_engineering.py (Silver).",
                "Entity Matching >= 0,85, IngestionGate ALLOW (N = 1.777), ajuste 50% y Yeo-Johnson.",
            ],
            [
                "4. Demostración Operativa con Datos Reales",
                "Fase 4: Modelado Matemático (Modeling)",
                "src/analytics/model_health.py, multivariate_engine.py (Capa Gold en DuckDB).",
                "ModelHealthGate (KMO = 0,7889), ACP SVD (4 PCs = 82,34%), K-Means/Ward y k-NN.",
            ],
            [
                "5. Evaluación Empírica Rigurosa",
                "Fase 5: Evaluación Estadística (Evaluation)",
                "src/analytics/clustering_validator.py y suite pytest (tests/test_*.py).",
                "ARI = 0,7235 >= 0,70, Silueta = 0,4014, Davies-Bouldin = 0,8981 y 9/9 tests PASSED.",
            ],
            [
                "6. Comunicación y Transferencia Ejecutiva",
                "Fase 6: Despliegue Analítico (Deployment)",
                "src/dashboard/app.py, views.py, components.py y Memoria TFM UNIR.",
                "Cuadro de mando Streamlit con 5 vistas, Pizza/Radar H2H y Scorecard NBA.",
            ],
        ],
        source_note="Elaboración propia adaptando Peffers et al. (2007), Hevner et al. (2004) y Wirth & Hipp (2000).",
    )

    # =========================================================================
    # 3.3. ARQUITECTURA DE DATOS POR CAPAS (MEDALLION ARCHITECTURE)
    # =========================================================================
    doc.add_heading(
        "3.3. Arquitectura de Datos por Capas (Medallion Architecture): Detalle exhaustivo de Bronze, Silver y Gold",
        level=2,
    )
    doc.add_paragraph(
        "Para superar la fragilidad estructural de los scripts monolíticos y de las hojas de cálculo desconectadas, "
        "el prototipo implementa una arquitectura de ingeniería de datos Lakehouse Multi-Hop conocida en la "
        "literatura de sistemas distribuidos como Arquitectura Medallion (Armbrust et al., 2021). Este patrón "
        "desacopla el ciclo de vida del dato en tres capas de refinamiento progresivo e inmutabilidad creciente "
        "—Bronze, Silver y Gold—, asegurando que cualquier anomalía estadística en los modelos finales pueda "
        "rastrearse de forma determinista hasta el documento JSON bruto original."
    )
    doc.add_paragraph(
        "La Capa Bronze (Ingesta Inmutable y Persistencia Documental NoSQL) constituye la zona de aterrizaje "
        "primaria de los datos externos. Dado que el servicio API-Football REST v3 devuelve estructuras "
        "jerárquicas profundamente anidadas (donde un mismo objeto jugador contiene sub-documentos polimórficos "
        "de metadatos biográficos, club de pertenencia, liga, apariciones, goles, pases, regates y duelos), "
        "el modelo relacional clásico resulta rígido e ineficiente en fase de captura. Por ello, el módulo "
        "src/ingestion/mongo_loader.py implementa un repositorio NoSQL orientado a documentos sobre MongoDB "
        "(con respaldo transaccional automático en formato JSON Lines dentro de data/raw/live_players_bronze.jsonl "
        "y data/raw/raw_financial_records.jsonl). Cada registro ingerido es enriquecido en el instante de su "
        "captura con una marca temporal UTC en estándar ISO-8601 y una huella criptográfica inmutable SHA-256 "
        "calculada sobre el cuerpo canónico del payload, garantizando la integridad forense del dato en reposo."
    )
    doc.add_paragraph(
        "La Capa Silver (Feature Store Columnar y Homologación Contractual) recibe los registros deduplicados "
        "de la capa Bronze, ejecuta el enlace probabilístico de entidades frente a las fuentes financieras "
        "(Transfermarkt y Capology) y somete el conjunto resultante al escrutinio de la compuerta IngestionGate "
        "(src/processing/data_contracts.py). Aquellos registros que cumplen simultáneamente el esquema tipado "
        "JSON Schema Draft 2020-12 y el umbral de exposición mínima competitiva (>= 600 minutos disputados en "
        "la temporada) son procesados por el motor SportsFeatureEngineer (src/processing/feature_engineering.py). "
        "En esta etapa se calculan las quince tasas deportivas por 90 minutos, se aplica el factor de corrección "
        "de posesión del club a las cinco métricas defensivas, se ejecutan las transformaciones paramétricas "
        "de potencia de Yeo-Johnson y se materializa el resultado en formato columnar comprimido Apache Parquet "
        "(data/interim/players_silver.parquet) y en la tabla relacional silver_players dentro de DuckDB."
    )
    doc.add_paragraph(
        "La Capa Gold (Inferencia Multivariante y Motor Analítico OLAP en Proceso) constituye el estrato de "
        "consumo ejecutivo y científico del DSS. Tras verificar las condiciones psicométricas en ModelHealthGate, "
        "el motor ScoutingMultivariateEngine (src/analytics/multivariate_engine.py) proyecta la matriz "
        "estandarizada sobre las Componentes Principales retenidas, asigna las etiquetas de agrupamiento "
        "táctico (K-Means y Ward), estima las distancias de similitud k-NN y computa el diferencial econométrico "
        "Net Value junto con la regla prescriptiva Next Best Action. La tabla analítica resultante de 97 "
        "columnas y N = 1.777 jugadores se persiste en data/processed/players_gold_analytics.parquet y como "
        "tabla nativa gold_players en el motor OLAP embebido DuckDB (data/processed/scouting_gold.duckdb; "
        "Raasveldt & Mühleisen, 2019). La elección de DuckDB frente a motores relacionales cliente-servidor "
        "tradicionales permite ejecutar consultas vectorizadas SIMD en memoria con tiempos de respuesta "
        "inferiores a 5 milisegundos desde la interfaz interactiva de Streamlit. La Figura 3.1 ilustra el "
        "diagrama arquitectónico C4 de contenedores del sistema, mientras que la Figura 3.2 presenta el embudo "
        "de linaje cuantitativo (Data Funnel Chart) verificado sobre la cohorte europea real."
    )

    add_v6_figure(
        doc=doc,
        figure_number="3.1",
        title="Diagrama C4 de Contenedores de la Arquitectura Lakehouse Medallion (Bronze MongoDB/JSONL, Silver Parquet y Gold DuckDB/ML).",
        image_path=figures_dir / "fig01_medallion_c4_architecture.png",
        source_note="Elaboración propia a partir del diseño de ingeniería de software implementado en el repositorio scouting_dss_tfm.",
    )

    add_v6_figure(
        doc=doc,
        figure_number="3.2",
        title="Diagrama de Flujo y Embudo de Linaje de Datos (Data Funnel Chart): De 4.460 registros brutos en API-Football v3 a la muestra Gold (N = 1.777).",
        image_path=figures_dir / "fig02_data_lineage_funnel.png",
        source_note="Elaboración propia a partir de la auditoría de trazabilidad del pipeline sobre las 6 ligas europeas (temporada 2023/24).",
    )

    # =========================================================================
    # 3.4. DATA ENRICHMENT PIPELINE Y RESOLUCIÓN DE ENTIDADES
    # =========================================================================
    doc.add_heading(
        "3.4. Data Enrichment Pipeline y Resolución de Entidades: Justificación del Entity Matching en 3 niveles",
        level=2,
    )
    doc.add_paragraph(
        "La integración de bases de datos deportivas (API-Football) y financieras (Transfermarkt y Capology) "
        "se enfrenta al problema clásico de Resolución de Entidades o Record Linkage en ausencia de claves "
        "primarias compartidas (Fellegi & Sunter, 1969; Christen, 2012). En el ámbito futbolístico internacional, "
        "un mismo jugador suele figurar bajo representaciones léxicas divergentes entre proveedores debido al "
        "uso de nombres deportivos o apodos (por ejemplo, 'Rodri' frente a 'Rodrigo Hernández Cascante'), "
        "abreviaturas de pila ('M. Odegaard' frente a 'Martin Ødegaard'), transliteraciones de alfabetos no "
        "latinos o signos diacríticos ('S. Guirassy' frente a 'Serhou Guirassy'). Una unión relacional exacta "
        "(INNER JOIN por cadena literal) descartaría erróneamente a más del 35% de la muestra, mientras que un "
        "emparejamiento difuso ingenuo sobre el nombre completo produciría una elevada tasa de falsos positivos "
        "al confundir jugadores homónimos de distintos clubes o edades (como los múltiples futbolistas "
        "registrados bajo los apellidos 'Dembélé', 'Traoré', 'Silva' o 'Hernández')."
    )
    doc.add_paragraph(
        "Para resolver este dilema garantizando simultáneamente alta exhaustividad (Recall) y precisión estricta "
        "(Precision), el módulo src/ingestion/fuzzy_matcher.py implementa un algoritmo jerárquico en cascada de "
        "tres niveles inspirado en los diccionarios de correspondencia de código abierto (Reep Register / "
        "paquete dcaribou) y en la teoría de bloqueo indexado de Christen (2012):"
    )
    doc.add_paragraph(
        "En el Nivel 1 (Diccionario Determinístico Crosswalk), el sistema consulta una tabla maestra de "
        "identificadores cruzados que mapea de forma biunívoca el player_id de API-Football con su identificador "
        "financiero homólogo para aquellos futbolistas previamente catalogados y auditados. Si existe una "
        "entrada en el diccionario Crosswalk, el enlace se resuelve en tiempo constante O(1) con certidumbre "
        "determinística (score = 1,00)."
    )
    doc.add_paragraph(
        "En el Nivel 2 (Normalización Canónica y Bloqueo Biométrico Determinístico), los registros no resueltos "
        "en el primer nivel se someten a una descomposición Unicode NFKD que elimina acentos y diacríticos, "
        "convierte la cadena a minúsculas ASCII y suprime partículas irrelevantes ('jr', 'filho', 'dos santos'). "
        "Acto seguido, en lugar de comparar cada registro deportivo contra la totalidad del catálogo financiero "
        "—lo que supondría una complejidad cuadrática O(N x M) y un alto riesgo de colisión léxica—, se aplica "
        "una clave de bloqueo biométrico estricto basada en el año de nacimiento (birth_year con tolerancia "
        "máxima de +-1 año por discrepancias de registro juvenil) y la compatibilidad del club o liga. Este "
        "bloqueo reduce el espacio de búsqueda en más de un 96% e impide matemáticamente que un juvenil sea "
        "enlazado con el salario de un jugador veterano homónimo."
    )
    doc.add_paragraph(
        "En el Nivel 3 (Similitud Léxica Híbrida vía RapidFuzz con Corte Estricto >= 0,85), dentro de cada "
        "bloque biométrico compatible se evalúa una función de similitud convexa que combina la métrica de "
        "distancia de edición de Levenshtein verdaderamente normalizada de Yujian y Bo (2007) con el operador "
        "invariante al orden de palabras token_sort_ratio implementado en C++ por la librería RapidFuzz:"
    )
    doc.add_paragraph(
        "    d_N(A, B) = (2 * d_L(A, B)) / (|A| + |B| + d_L(A, B))    ==>    s_N(A, B) = 1 - d_N(A, B)\n"
        "    S_hibrida(A, B) = 0,60 * s_N(A, B) + 0,40 * token_sort_ratio(A, B)"
    )
    doc.add_paragraph(
        "Únicamente aquellos pares candidatos cuya similitud híbrida alcanza o supera el umbral estricto "
        "tau = 0,85 (85,0% de concordancia léxica dentro del mismo bloque biométrico) son aceptados y "
        "promovidos a la capa Silver; cualquier candidato con S_hibrida < 0,85 es derivado a la cola de "
        "auditoría y descartado para preservar la pureza econométrica del modelo Net Value. La Figura 3.3 "
        "muestra el diagrama de flujo de este algoritmo de tres niveles junto con la distribución empírica "
        "de las puntuaciones de similitud obtenidas sobre nuestra cohorte europea."
    )

    add_v6_figure(
        doc=doc,
        figure_number="3.3",
        title="Diagrama de Flujo del Algoritmo Entity Matching en 3 Niveles (Crosswalk Reep Register, Bloqueo Biométrico y RapidFuzz >= 0,85).",
        image_path=figures_dir / "fig03_entity_matching_flowchart.png",
        source_note="Elaboración propia a partir de la ejecución del módulo src/ingestion/fuzzy_matcher.py sobre los 3.443 jugadores únicos.",
    )

    # =========================================================================
    # 3.5. GOBERNANZA DEL DATO Y PUERTAS DE CALIDAD
    # =========================================================================
    doc.add_heading(
        "3.5. Gobernanza del Dato y Puertas de Calidad: IngestionGate (JSON Schema) y ModelHealthGate (N >= 300, KMO >= 0,70, Bartlett p < 0,05)",
        level=2,
    )
    doc.add_paragraph(
        "En los sistemas de aprendizaje automático en producción (MLOps), la degradación silenciosa de los datos "
        "de entrada o la violación de los supuestos matemáticos del modelo constituyen la causa principal de "
        "inferencias erróneas (Schelter et al., 2018; Sculley et al., 2015). Para dotar al prototipo de "
        "gobernanza determinista, se han diseñado dos compuertas de control de calidad automatizadas que actúan "
        "como cortafuegos entre las capas de la arquitectura Medallion (Figura 3.4):"
    )
    doc.add_paragraph(
        "La primera compuerta, IngestionGate (src/processing/data_contracts.py), se ubica en la transición "
        "Bronze -> Silver y valida cada registro frente al contrato formal config/data_contract_schema.json "
        "(especificado bajo el estándar JSON Schema Draft 2020-12). Esta compuerta verifica la integridad de "
        "tipos de datos, la ausencia de valores nulos en claves primarias y métricas críticas, la pertenencia "
        "del grupo posicional al dominio válido {'DF', 'MF', 'FW', 'GK'}, la acotación física de la posesión "
        "media del equipo en el intervalo [25%, 80%], la positividad estricta de las variables financieras "
        "y el cumplimiento del umbral mínimo de exposición competitiva de 600 minutos disputados. En función "
        "de la tasa de registros inválidos, IngestionGate emite uno de tres estados operativos: ALLOW (cuando "
        "la muestra válida supera los 300 jugadores y la tasa de error estructural es inferior al 5%), DEGRADED "
        "(cuando la tasa de error se sitúa entre el 5% y el 20%, activando alertas de linaje) o BLOCKED (cuando "
        "la muestra útil cae por debajo de N = 300 o los errores superan el 20%, abortando preventivamente la "
        "ejecución del pipeline)."
    )
    doc.add_paragraph(
        "La segunda compuerta, ModelHealthGate (src/analytics/model_health.py), se sitúa en la transición "
        "Silver -> Gold inmediatamente antes de ejecutar la descomposición en valores singulares del Análisis "
        "de Componentes Principales. Su propósito es impedir que se extraigan factores latentes sobre una "
        "matriz de datos numéricamente mal condicionada o carente de estructura de covarianza significativa. "
        "Para otorgar el veredicto HEALTHY, ModelHealthGate exige superar simultáneamente cuatro pruebas "
        "matemáticas: (1) un tamaño muestral efectivo N >= 300 observaciones (superado casi seis veces en "
        f"nuestra cohorte real con N = {hr.sample_size}); (2) un índice global de adecuación muestral de "
        f"Kaiser-Meyer-Olkin KMO >= 0,70 (alcanzando {hr.kmo_global:.4f} en la muestra europea); (3) un "
        "p-valor inferior a 0,05 en la prueba de esfericidad de Bartlett que rechace la hipótesis nula de que "
        f"la matriz de correlaciones es una matriz identidad (obteniendo Chi-cuadrado = {hr.bartlett_chi2:,.2f}, "
        f"p < 10^-16); y (4) un número de condición espectral kappa(R) < 30,0 que descarte colinealidad "
        f"perfecta o singularidad matricial (registrando kappa = {hr.condition_number:.2f})."
    )

    add_v6_figure(
        doc=doc,
        figure_number="3.4",
        title="Diagrama de Secuencia de las Compuertas Deterministas de Gobernanza MLOps: IngestionGate (JSON Schema) y ModelHealthGate (KMO y Bartlett).",
        image_path=figures_dir / "fig04_governance_gates_sequence.png",
        source_note="Elaboración propia a partir de la arquitectura de validación implementada en data_contracts.py y model_health.py.",
    )

    add_v6_table(
        doc=doc,
        table_number="3.2",
        title="Diccionario de las 15 métricas técnico-tácticas por 90 minutos, ajuste contextual de posesión y variables financieras del Contrato de Datos.",
        headers=[
            "Código de Variable",
            "Bloque Funcional",
            "Fórmula de Normalización Base",
            "Ajuste Posesión (50%)",
            "Transformación Pre-ACP",
        ],
        rows=[
            ["goals_per90", "Ofensivo / Finalización", "(Goles / Minutos) * 90", "No (Acción con balón)", "Yeo-Johnson + Z-Score"],
            ["expected_goals_xg_per90", "Ofensivo / Finalización", "(xG Acumulado / Minutos) * 90", "No (Acción con balón)", "Yeo-Johnson + Z-Score"],
            ["shots_on_target_per90", "Ofensivo / Finalización", "(Tiros a Puerta / Minutos) * 90", "No (Acción con balón)", "Yeo-Johnson + Z-Score"],
            ["assists_per90", "Creativo / Asociativo", "(Asistencias / Minutos) * 90", "No (Acción con balón)", "Yeo-Johnson + Z-Score"],
            ["expected_assists_xa_per90", "Creativo / Asociativo", "(xA Acumulado / Minutos) * 90", "No (Acción con balón)", "Yeo-Johnson + Z-Score"],
            ["key_passes_per90", "Creativo / Asociativo", "(Pases Clave / Minutos) * 90", "No (Acción con balón)", "Yeo-Johnson + Z-Score"],
            ["progressive_passes_per90", "Progresión Territorial", "(Pases Progresivos / Minutos) * 90", "No (Acción con balón)", "Yeo-Johnson + Z-Score"],
            ["progressive_carries_per90", "Progresión Territorial", "(Conducciones Prog. / Minutos) * 90", "No (Acción con balón)", "Yeo-Johnson + Z-Score"],
            ["successful_dribbles_per90", "Desequilibrio 1v1", "(Regates Exitosos / Minutos) * 90", "No (Acción con balón)", "Yeo-Johnson + Z-Score"],
            ["aerial_duels_won_per90", "Disputa Aérea", "(Duelos Aéreos Gan. / Minutos) * 90", "No (Disputa neutra)", "Yeo-Johnson + Z-Score"],
            ["tackles_p90_adj", "Defensivo / Recuperación", "(Entradas / Minutos) * 90", "Sí: M_p90 * (50 / Pos_Club)", "Yeo-Johnson + Z-Score"],
            ["interceptions_p90_adj", "Defensivo / Recuperación", "(Intercepciones / Minutos) * 90", "Sí: M_p90 * (50 / Pos_Club)", "Yeo-Johnson + Z-Score"],
            ["duels_won_p90_adj", "Defensivo / Recuperación", "(Duelos Totales Gan. / Minutos) * 90", "Sí: M_p90 * (50 / Pos_Club)", "Yeo-Johnson + Z-Score"],
            ["blocks_p90_adj", "Defensivo / Recuperación", "(Bloqueos Defensivos / Minutos) * 90", "Sí: M_p90 * (50 / Pos_Club)", "Yeo-Johnson + Z-Score"],
            ["recoveries_p90_adj", "Defensivo / Recuperación", "(Recuperaciones / Minutos) * 90", "Sí: M_p90 * (50 / Pos_Club)", "Yeo-Johnson + Z-Score"],
            ["market_value_eur", "Financiero (CAPEX)", "Tasación Hedónica en Euros (Transfermarkt)", "No aplica", "Yeo-Johnson -> 0,60 * Z_MV"],
            ["annual_gross_salary_eur", "Financiero (OPEX)", "Salario Bruto Anual en Euros (Capology)", "No aplica", "Yeo-Johnson -> 0,40 * Z_Sal"],
        ],
        source_note="Elaboración propia a partir del esquema config/data_contract_schema.json y del módulo src/processing/feature_engineering.py.",
    )

    # =========================================================================
    # 3.6. FORMULACIÓN MATEMÁTICA Y ESTADÍSTICA DE LOS MODELOS
    # =========================================================================
    doc.add_heading("3.6. Formulación Matemática y Estadística de los Modelos Analíticos", level=2)

    doc.add_heading(
        "3.6.1. Relativización por 90 minutos y Ajuste Contextual por Posesión para mitigar la Paradoja de Sobiech",
        level=3,
    )
    doc.add_paragraph(
        "Sea X_{i,j} el conteo bruto acumulado de la acción técnico-táctica j por el futbolista i a lo largo de "
        "los M_i minutos disputados durante la temporada oficial (con la restricción de admisibilidad M_i >= 600 "
        "minutos para evitar varianzas espurias en muestras de baja exposición). En una primera etapa, toda "
        "métrica de volumen se transforma en una tasa relativizada por partido completo estándar de 90 minutos:"
    )
    doc.add_paragraph(
        "    M_per90(i, j) = (X_{i,j} / M_i) * 90,0"
    )
    doc.add_paragraph(
        "Sin embargo, como demostró Sven Mislintat al formular la Paradoja de Sobiech en la Bundesliga "
        "(Biermann, 2019; Pappalardo et al., 2019), las cinco métricas defensivas reactivas —entradas "
        "(tackles), intercepciones (interceptions), duelos ganados (duels_won), bloqueos (blocks) y "
        "recuperaciones de balón (recoveries)— dependen inversamente del porcentaje medio de posesión de balón "
        "P_{c(i)} del club c(i) en el que milita el jugador. Un defensor cuyo equipo retiene el 66% de la "
        "posesión dispone de la mitad de tiempo de exposición defensiva sin balón que un defensor cuyo club "
        "promedia un 38% de posesión. Para neutralizar este sesgo contextual y evaluar a todos los jugadores "
        "bajo un escenario táctico neutral del 50% de posesión, se aplica el factor de corrección:"
    )
    doc.add_paragraph(
        "    M_p90_adj(i, j) = M_per90(i, j) * (50,0 / Posesion_Equipo(c(i)))"
    )
    doc.add_paragraph(
        "Este ajuste reescala al alza la intensidad defensiva por minuto sin balón de los futbolistas que "
        "defienden en bloques altos de equipos dominadores y corrige la inflación artificial por volumen de "
        "los defensores pertenecientes a clubes asediados en bloque bajo (Tabla 3.2)."
    )

    doc.add_heading(
        "3.6.2. Transformación paramétrica de potencia de Yeo-Johnson (2000), filtrado OLS y estandarización Z-Score",
        level=3,
    )
    doc.add_paragraph(
        "Las distribuciones empíricas tanto de las tasas deportivas M_per90 y M_p90_adj como de las magnitudes "
        "monetarias (Valor de Mercado y Salario Bruto) violan severamente el supuesto de normalidad gaussiana, "
        "presentando coeficientes de asimetría positiva elevados y valores exactamente iguales a cero (por "
        "ejemplo, defensores centrales con 0,00 goles/90). Dado que la transformación logarítmica simple ln(y) "
        "y la transformación clásica de Box y Cox (1964) son matemáticamente indefinidas para y = 0, el módulo "
        "SportsFeatureEngineer implementa la familia paramétrica continua de transformaciones de potencia de "
        "Yeo y Johnson (2000), definida para todo número real y en R mediante la función por tramos:"
    )
    doc.add_paragraph(
        "    psi(y; lambda) = ((y + 1)^lambda - 1) / lambda                  si y >= 0 y lambda != 0\n"
        "    psi(y; lambda) = ln(y + 1)                                      si y >= 0 y lambda = 0\n"
        "    psi(y; lambda) = -((-y + 1)^(2 - lambda) - 1) / (2 - lambda)    si y < 0  y lambda != 2\n"
        "    psi(y; lambda) = -ln(-y + 1)                                    si y < 0  y lambda = 2"
    )
    doc.add_paragraph(
        "Para cada variable j en {1, ..., p}, el exponente óptimo lambda_j se estima de forma exacta mediante "
        "Máxima Verosimilitud (Maximum Likelihood Estimation, MLE) maximizando la log-verosimilitud perfilada "
        "de la muestra transformada. Posteriormente, cada variable transformada se estandariza a puntuación "
        "típica Z-Score con media muestral nula (mu_j = 0) y varianza unitaria (sigma_j^2 = 1):"
    )
    doc.add_paragraph(
        "    Z_{i,j} = (psi(Y_{i,j}; lambda_j) - mu_psi_j) / sigma_psi_j"
    )
    doc.add_paragraph(
        "Adicionalmente, para garantizar que ninguna variable táctica carezca de relevancia económica o "
        "introduzca ruido blanco ortogonal, se verifica mediante regresión de Mínimos Cuadrados Ordinarios "
        "(OLS) y pruebas F marginales que las 15 métricas seleccionadas presenten asociación estadísticamente "
        "significativa al nivel p < 0,10 respecto al vector compuesto de rendimiento y valoración."
    )

    doc.add_heading(
        "3.6.3. Análisis de Componentes Principales (ACP - Jolliffe & Cadima, 2016): autovalores, Criterio de Kaiser y varianza acumulada",
        level=3,
    )
    doc.add_paragraph(
        "Sea Z la matriz de datos deportivos estandarizados de dimensión N x p (con N = 1.777 jugadores y "
        "p = 15 variables), y sea R = (1 / (N - 1)) * Z^T * Z su matriz de correlaciones muestrales de Pearson. "
        "Tras superar la compuerta ModelHealthGate (estadístico KMO de Kaiser, 1974, y test de esfericidad de "
        "Bartlett, 1950), se procede a diagonalizar R mediante Descomposición en Valores Singulares (SVD; "
        "Jolliffe & Cadima, 2016):"
    )
    doc.add_paragraph(
        "    R * v_k = lambda_k * v_k,    con lambda_1 >= lambda_2 >= ... >= lambda_p >= 0"
    )
    doc.add_paragraph(
        "donde v_k representa el k-ésimo autovector ortonormal (vector de cargas factoriales o loadings) y "
        "lambda_k su autovalor asociado, el cual cuantifica la cantidad de varianza de las p variables "
        "originales capturada por la k-ésima Componente Principal. Para determinar el número óptimo d de "
        "componentes a retener, se articula una regla de decisión conjunta que combina el Criterio de Kaiser "
        "(1960) —retener componentes con autovalor superior a la unidad o que aporten estructura factorial "
        "interpretable— con la condición de explicar al menos el 75,0% de la varianza total acumulada:"
    )
    doc.add_paragraph(
        "    Varianza_Acumulada(d) = (Sum_{k=1}^d lambda_k) / p >= 0,75"
    )
    doc.add_paragraph(
        "En la cohorte real de las seis ligas europeas, esta formulación retiene d = 4 Componentes Principales "
        "ortogonales (PC1, PC2, PC3 y PC4) que sintetizan el 82,34% de la varianza total de las 15 métricas "
        "originales, eliminando por completo la multicolinealidad antes de calcular distancias geométricas."
    )

    doc.add_heading(
        "3.6.4. Clustering Jerárquico (Método de Ward) y Particional (K-Means): validación multicriterio y concordancia por ARI >= 0,70",
        level=3,
    )
    doc.add_paragraph(
        "Sobre la matriz de puntuaciones latentes ortogonales Y = Z * V_d (de dimensión N x d), se aplican de "
        "forma paralela e independiente dos paradigmas de aprendizaje no supervisado con el objetivo de "
        "descubrir una taxonomía objetiva de arquetipos tácticos:"
    )
    doc.add_paragraph(
        "Por un lado, el algoritmo particional K-Means con inicialización probabilística K-Means++ (MacQueen, "
        "1967; Arthur & Vassilvitskii, 2007) busca dividir los N futbolistas en K clústeres disjuntos "
        "C = {C_1, ..., C_K} minimizando la suma de cuadrados intra-clúster (Within-Cluster Sum of Squares, WCSS):"
    )
    doc.add_paragraph(
        "    WCSS(C) = Sum_{k=1}^K Sum_{y_i in C_k} || y_i - mu_k ||_2^2"
    )
    doc.add_paragraph(
        "Por otro lado, el Agrupamiento Jerárquico Aglomerativo mediante el Método de Mínima Varianza de Ward "
        "(1963) construye un árbol jerárquico ascendente (dendrograma) fusionando en cada iteración el par de "
        "clústeres (C_a, C_b) que produce el menor incremento marginal Delta(C_a, C_b) en la varianza total "
        "intra-grupo, gobernado por la distancia ponderada:"
    )
    doc.add_paragraph(
        "    Delta(C_a, C_b) = ((|C_a| * |C_b|) / (|C_a| + |C_b|)) * || mu_a - mu_b ||_2^2"
    )
    doc.add_paragraph(
        "Para evaluar la calidad geométrica intrínseca de cada partición candidata K en [3, 8], el validador "
        "src/analytics/clustering_validator.py computa simultáneamente tres índices internos complementarios: "
        "(i) el Coeficiente Medio de Silueta s(i) = (b(i) - a(i)) / max{a(i), b(i)} de Rousseeuw (1987), acotado "
        "en [-1, 1] y a maximizar; (ii) el Índice de Varianza entre Razones de Caliński y Harabasz (1974), a "
        "maximizar; y (iii) el Índice de Separación de Davies y Bouldin (1979), a minimizar. Adicionalmente, "
        "para certificar que los arquetipos descubiertos no son un artefacto algorítmico espurio, se cuantifica "
        "la concordancia topológica entre la partición de K-Means (U) y la partición de Ward (V) mediante el "
        "Índice de Rand Ajustado por el azar (Adjusted Rand Index, ARI; Hubert & Arabie, 1985):"
    )
    doc.add_paragraph(
        "    ARI(U, V) = (Indice_Observado - Indice_Esperado_Azar) / (Indice_Maximo - Indice_Esperado_Azar) >= 0,70"
    )

    doc.add_heading(
        "3.6.5. Algoritmo k-Nearest Neighbors (k-NN) para búsqueda de clones tácticos y formulación del Net Value",
        level=3,
    )
    doc.add_paragraph(
        "Para resolver el problema de sustitución de talento (identificar el reemplazo táctico más cercano a "
        "un jugador objetivo i* que abandona el club o cuyo fichaje resulta financieramente inviable), el motor "
        "indexa un árbol espacial k-Nearest Neighbors (k-NN; Cover & Hart, 1967) sobre el espacio de las "
        "Componentes Principales ponderadas por sus respectivos ratios de varianza explicada w_m = lambda_m / "
        "Sum(lambda). La distancia táctica euclídea ponderada d_ACP(i*, j) y el porcentaje de similitud "
        "acotado en [0%, 100%] mediante un núcleo exponencial radial se definen como:"
    )
    doc.add_paragraph(
        "    d_ACP(i*, j) = sqrt( Sum_{m=1}^d w_m * (Y_{i*,m} - Y_{j,m})^2 )    ==>    Similitud(i*, j) = 100 * exp(-0,45 * d_ACP(i*, j))"
    )
    doc.add_paragraph(
        "Finalmente, para acoplar el Valor de Uso deportivo con la exigencia económica del activo (Franceschi "
        "et al., 2024), se construye el índice sintético de rendimiento técnico-táctico estandarizado "
        "Z_ACP_Rendimiento(i) (combinando las puntuaciones factoriales ponderadas por su contribución positiva "
        "al juego) y el índice compuesto de coste financiero estandarizado Z_Coste_Financiero(i) = "
        " Estandarizar(0,60 * Z_Valor_Mercado(i) + 0,40 * Z_Salario_Bruto(i)). El diferencial de eficiencia "
        "económica Net Value se define entonces como el residuo ortogonal:"
    )
    doc.add_paragraph(
        "    Net_Value(i) = Z_ACP_Rendimiento(i) - Z_Coste_Financiero(i)"
    )
    doc.add_paragraph(
        "Un valor Net_Value(i) > 0 indica que el futbolista genera un rendimiento deportivo medido en "
        "desviaciones típicas superior a su coste relativo en el mercado europeo. Cruzando el signo de ambos "
        "ejes ortogonales (Z_ACP_Rendimiento y Z_Coste_Financiero), el universo de jugadores queda particionado "
        "en cuatro cuadrantes estratégicos: Cuadrante I ('Gangas Tácticas / Oportunidades de Mercado': "
        "Z_ACP >= 0 y Z_Coste < 0), Cuadrante II ('Estrellas Consolidadas': Z_ACP >= 0 y Z_Coste >= 0), "
        "Cuadrante III ('Ineficientes / Sobrevalorados': Z_ACP < 0 y Z_Coste >= 0) y Cuadrante IV ('Cantera / "
        "Rotación en Desarrollo': Z_ACP < 0 y Z_Coste < 0)."
    )


def write_chapter_4_marco_normativo(doc: Document) -> None:
    """Redacta de forma exhaustiva el Capítulo 4 (Marco Normativo — Págs. 32-35)."""
    doc.add_heading("CAPÍTULO 4. MARCO NORMATIVO, ÉTICO Y DE PROPIEDAD INTELECTUAL", level=1)

    doc.add_heading(
        "4.1. Protección de Datos Personales: Cumplimiento del RGPD (Reglamento UE 2016/679) y LOPD-GDD (Ley Orgánica 3/2018)",
        level=2,
    )
    doc.add_paragraph(
        "Dado que los registros procesados por el prototipo identifican a personas físicas vivas (futbolistas "
        "profesionales en activo de las seis ligas europeas), el tratamiento de la información se encuentra "
        "sujeto a las disposiciones del Reglamento (UE) 2016/679 del Parlamento Europeo y del Consejo, de 27 "
        "de abril de 2016, relativo a la protección de las personas físicas en lo que respecta al tratamiento "
        "de datos personales (RGPD), así como a la Ley Orgánica 3/2018, de 5 de diciembre, de Protección de "
        "Datos Personales y garantía de los derechos digitales (LOPD-GDD) vigente en el ordenamiento jurídico "
        "español."
    )
    doc.add_paragraph(
        "La base jurídica que legitima el tratamiento en el marco del presente Trabajo Fin de Máster reside "
        "en el artículo 6.1.f) del RGPD (interés legítimo del responsable del tratamiento para fines de "
        "investigación científica y docencia universitaria sin ánimo de lucro ni explotación comercial), en "
        "concordancia con el régimen específico de garantías para la investigación científica estatuido en el "
        "artículo 89 del RGPD y en la Disposición Adicional Decimoséptima de la LOPD-GDD. Esta ponderación de "
        "interés legítimo resulta plenamente favorable a los derechos de los interesados por cuanto la totalidad "
        "de las métricas tratadas constituyen datos de desempeño profesional públicamente notorios generados en "
        "espectáculos deportivos de retransmisión abierta, unidos a estimaciones económicas de dominio público "
        "académico (Herm et al., 2014)."
    )
    doc.add_paragraph(
        "En estricto cumplimiento de los principios de limitación de la finalidad y minimización de datos "
        "(artículos 5.1.b y 5.1.c del RGPD), así como de la protección reforzada de las categorías especiales "
        "de datos personales (artículo 9 del RGPD), el diseño del esquema contractual config/data_contract_schema.json "
        "excluye de manera absoluta cualquier dato relativo a la salud física o mental del deportista (historiales "
        "clínicos de lesiones, partes médicos, pruebas biométricas invasivas, cargas internas de GPS o "
        "parámetros hematológicos), así como datos de geolocalización privada, domicilios particulares, "
        "afiliación sindical, creencias religiosas o vida familiar. Asimismo, desde la perspectiva de la "
        "privacidad desde el diseño y por defecto (artículo 25 del RGPD), el prototipo opera en un entorno "
        "local aislado (localhost) gobernado por variables de entorno privadas (.env) excluidas del control "
        "de versiones mediante reglas .gitignore."
    )

    doc.add_heading(
        "4.2. Propiedad Intelectual y Términos de Servicio de APIs: Licenciamiento de API-Football REST v3 y datasets de Transfermarkt/Capology",
        level=2,
    )
    doc.add_paragraph(
        "El uso de catálogos estructurados de eventos deportivos y valoraciones económicas exige observar las "
        "normas sobre propiedad intelectual y protección jurídica de las bases de datos establecidas en la "
        "Directiva 96/9/CE del Parlamento Europeo y del Consejo (que consagra el derecho sui generis del "
        "fabricante de una base de datos frente a la extracción o reutilización sustancial no autorizada) "
        "y su transposición al Texto Refundido de la Ley de Propiedad Intelectual española (Real Decreto "
        "Legislativo 1/1996)."
    )
    doc.add_paragraph(
        "Para garantizar la plena licitud en la adquisición de los datos deportivos, el proyecto prescinde "
        "de técnicas intrusivas de raspado web (web scraping agresivo) sobre portales protegidos y utiliza "
        "exclusivamente la interfaz de programación de aplicaciones oficial API-Football REST v3 (operada "
        "por API-Sports) mediante una clave de suscripción nominativa legítima. El extractor desarrollado "
        "(src/ingestion/live_extractor.py) respeta escrupulosamente los Términos de Servicio (Terms of Service, "
        "ToS) del proveedor: limita el volumen de consultas al cupo autorizado del plan de suscripción "
        "(100 peticiones diarias), impone una pausa determinista de 6,5 segundos entre llamadas consecutivas "
        "(inferior al límite máximo de 10 peticiones por minuto) y almacena las respuestas en caché local "
        "para evitar consultas redundantes. En lo que respecta a la agregación de registros de referencia de "
        "Transfermarkt y Capology con fines estrictamente académicos y de validación estadística, el proyecto "
        "se acoge a la excepción obligatoria de minería de textos y datos (Text and Data Mining, TDM) para "
        "fines de investigación científica consagrada en el artículo 3 de la Directiva (UE) 2019/790 sobre "
        "los derechos de autor en el mercado único digital (transpuesta en España mediante el Real Decreto-ley "
        "24/2021), citando en todo momento las fuentes primarias conforme a la normativa APA 7.ª edición."
    )

    doc.add_heading(
        "4.3. Declaración de Transparencia de Inteligencia Artificial: Cumplimiento de los artículos 6, 8 y 9 del Manual de Uso de IA de UNIR",
        level=2,
    )
    doc.add_paragraph(
        "En cumplimiento del Reglamento Europeo de Inteligencia Artificial —Reglamento (UE) 2024/1689 (EU AI "
        "Act)—, del artículo 22 del RGPD relativo a las decisiones individuales automatizadas y, de manera "
        "específica, de lo dispuesto en los artículos 6, 8 y 9 del Manual de Uso de Inteligencia Artificial "
        "en los Trabajos Fin de Estudios de la Universidad Internacional de La Rioja (UNIR), se formula la "
        "presente declaración expresa de transparencia algorítmica y académica:"
    )
    doc.add_paragraph(
        "Desde el punto de vista del funcionamiento del sistema desarrollado (EU AI Act, artículo 14 sobre "
        "supervisión humana o Human-in-the-Loop), el prototipo DSS de scouting no constituye un sistema "
        "autónomo de contratación o descarte laboral vinculante, sino una herramienta de asistencia "
        "cuantitativa explicable (White-Box Analytics). A diferencia de los modelos de caja negra profunda, "
        "cada recomendación emitida por el módulo Next Best Action (NBA) es 100% trazable matemáticamente a "
        "través de las cargas factoriales explícitas del ACP, los percentiles posicionales ajustados por "
        "posesión y la distancia euclídea exacta respecto a los vecinos k-NN, reservando siempre el juicio "
        "decisorio final al comité técnico humano."
    )
    doc.add_paragraph(
        "Asimismo, conforme a los artículos 6 (Principios de uso ético y responsable), 8 (Obligación de "
        "declaración y trazabilidad) y 9 (Responsabilidad e integridad académica del estudiante) del Manual "
        "de Uso de IA de la UNIR, el autor declara que el diseño arquitectónico del sistema, la formulación "
        "matemática, la ejecución real de los lotes de extracción en API-Football v3, la validación empírica "
        "sobre los 1.777 futbolistas europeos y la interpretación crítica de los resultados son obra intelectual "
        "propia del estudiante. Las herramientas de asistencia de inteligencia artificial generativa se han "
        "empleado exclusivamente como soporte instrumental de apoyo a la depuración sintáctica de código "
        "Python, formateo de plantillas de estilos y verificación ortotipográfica, habiendo sido la totalidad "
        "del código fuente y del texto académico auditada, ejecutada y validada personalmente por el autor "
        "(Tabla 4.1)."
    )

    add_v6_table(
        doc=doc,
        table_number="4.1",
        title="Matriz de cumplimiento normativo en protección de datos (RGPD/LOPD-GDD), propiedad intelectual y transparencia de IA.",
        headers=[
            "Ámbito Normativo",
            "Instrumento Legal / Artículo Aplicable",
            "Riesgo Identificado en Scouting Deportivo",
            "Medida Técnica y Organizativa Implementada en el TFM",
        ],
        rows=[
            [
                "Protección de Datos Personales",
                "RGPD (UE 2016/679) Arts. 5.1.c, 6.1.f, 9 y 89; LOPD-GDD (LO 3/2018).",
                "Tratamiento indebido de datos clínicos de lesiones o vida privada de futbolistas.",
                "Minimización estricta en JSON Schema: uso exclusivo de métricas públicas de partido y exclusión total de datos médicos.",
            ],
            [
                "Decisiones Automatizadas e IA",
                "RGPD Art. 22; Reglamento (UE) 2024/1689 (EU AI Act) Art. 14.",
                "Sesgo algorítmico opaco en la valoración laboral o descarte automático de jugadores.",
                "Paradigma Human-in-the-Loop y modelos White-Box explicables (cargas ACP, distancias k-NN y aviso consultivo en UI).",
            ],
            [
                "Propiedad Intelectual y APIs",
                "Directiva 96/9/CE (Derecho sui generis); Directiva (UE) 2019/790 Art. 3 (TDM).",
                "Extracción abusiva o sobrecarga de servidores de proveedores estadísticos.",
                "Consumo oficial autenticado de API-Football v3 con Rate Limiting (6,5 s/req, <= 100 req/día) y excepción científica TDM.",
            ],
            [
                "Integridad Académica e IA",
                "Manual de Uso de IA de UNIR (Arts. 6, 8 y 9); Reglamento TFE UNIR (Arts. 2.8 y 8.3).",
                "Falta de trazabilidad sobre el uso de asistentes generativos o datos sintéticos no declarados.",
                "Declaración explícita de uso instrumental, autoría intelectual única y verificación empírica real sobre 6 ligas (N = 1.777).",
            ],
        ],
        source_note="Elaboración propia a partir del marco jurídico europeo y de la normativa académica de la Universidad Internacional de La Rioja (UNIR).",
    )
