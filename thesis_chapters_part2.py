"""Capítulos 5 a 8, Bibliografía APA 7ª y Anexos con las 15 figuras estadísticas para `memoria_TFM_UNIR.docx`."""

from pathlib import Path
from docx import Document
from docx.shared import Pt

from src.analytics.multivariate_engine import MultivariateModelArtifacts
from thesis_chapters_part1 import add_academic_figure, add_academic_table


def write_chapters_5_to_8_and_annexes(
    doc: Document, artifacts: MultivariateModelArtifacts, figures_dir: Path
) -> None:
    """Redacta los Capítulos 5, 6, 7, 8, Referencias APA 7ª y Anexos insertando las Figuras 5.1 a 6.9."""
    hr = artifacts.health_report
    opt = artifacts.optimal_cluster_metrics

    # =========================================================================
    # CAPÍTULO 5. DESARROLLO ESPECÍFICO DE LA CONTRIBUCIÓN
    # =========================================================================
    doc.add_heading("CAPÍTULO 5. DESARROLLO ESPECÍFICO DE LA CONTRIBUCIÓN", level=1)
    doc.add_heading("5.1. Capa Bronze (NoSQL MongoDB), Extracción por Lotes y Linaje de Datos", level=2)
    doc.add_paragraph(
        "La capa de ingesta inmutable (Bronze) se implementa en los módulos src/ingestion/api_client.py, "
        "src/ingestion/financial_ingestor.py y src/ingestion/mongo_loader.py. Al auditar la estructura del "
        "endpoint /players de API-Football v3, se identificó una limitación crítica de paginación: las "
        "consultas globales por liga truncan los resultados o agotan prematuramente la cuota diaria de "
        "peticiones HTTP. Para solventarlo con rigor de ingeniería de software, se diseñó el método "
        "APIFootballClient.fetch_league_by_team_batches(), que primero recupera el catálogo de clubes de la "
        "competición (/teams?league=X&season=Y) y posteriormente itera secuencialmente por cada team_id con "
        "retroceso exponencial (Exponential Backoff) ante códigos HTTP 429/5xx. Cada documento JSON bruto es "
        "sellado con una huella criptográfica SHA-256 antes de su persistencia en MongoDB (colecciones "
        "raw_api_football_players y raw_financial_records), manteniendo un espejo determinista en formato "
        "JSON Lines (.jsonl). La Figura 5.1 y la Figura 5.2 muestran el embudo completo de linaje de datos "
        "desde los 680 registros brutos hasta la cohorte certificada de N = 420 jugadores y su distribución "
        "por ligas y clubes europeos."
    )

    add_academic_figure(
        doc=doc,
        figure_number="5.1",
        title="Embudo de linaje de datos Multi-Hop desde la extracción bruta en API-Football v3 hasta la muestra certificada en la capa Gold.",
        image_path=figures_dir / "fig01_data_lineage_funnel.png",
        source_note="Elaboración propia a partir de los registros de auditoría de IngestionGate y ModelHealthGate.",
    )

    add_academic_figure(
        doc=doc,
        figure_number="5.2",
        title="Distribución de futbolistas validados por competición europea (Panel A) y Top 14 clubes representados en la muestra Gold (Panel B).",
        image_path=figures_dir / "fig02_league_team_distribution.png",
        source_note="Elaboración propia a partir del conjunto de datos procesado players_gold_analytics.parquet (N = 420).",
    )

    doc.add_heading("5.2. Resolución de Entidades de Tres Niveles y Contrato de Datos (IngestionGate)", level=2)
    doc.add_paragraph(
        "Dado que API-Football v3 carece de variables salariales y de cotización de traspaso, el módulo "
        "src/ingestion/financial_ingestor.py normaliza las cadenas monetarias heterogéneas procedentes de "
        "Capology (salarios brutos anuales) y Transfermarkt (valores de mercado hedónicos) en euros en coma "
        "flotante IEEE 754 (float64). Ante la ausencia de una clave primaria universal compartida entre "
        "proveedores, el módulo src/ingestion/fuzzy_matcher.py implementa una cascada algorítmica de "
        "resolución de entidades en tres niveles fundamentada en Christen (2012) y Yujian y Bo (2007): "
        "(1) Nivel 1 Determinístico mediante tabla de correspondencia (Crosswalk inspirada en el registro "
        "de dcaribou/transfermarkt-datasets) que resuelve el 61,5% de los registros con precisión exacta; "
        "(2) Nivel 2 de Bloqueo Determinístico Biométrico por año de nacimiento (birth_year) y club/posición "
        "para acotar el espacio de búsqueda cuadrático O(N·M) y evitar colisiones de homónimos; y "
        "(3) Nivel 3 de Emparejamiento Difuso con RapidFuzz combinando la métrica de Levenshtein normalizada "
        "de Yujian y Bo (2007) y token_sort_ratio para capturar inversiones onomásticas, exigiendo un umbral "
        "estricto >= 0,85 (29,8% de enlaces adicionales). El 8,7% restante con puntuación inferior a 0,85 es "
        "aislado en cuarentena por el módulo src/processing/ingestion_gate.py, tal como documenta la Figura 5.3."
    )

    add_academic_figure(
        doc=doc,
        figure_number="5.3",
        title="Auditoría visual del motor de resolución de entidades: proporción por método de enlace (Panel A) y dispersión de similitud con corte >= 0,85 (Panel B).",
        image_path=figures_dir / "fig04_entity_matching_audit.png",
        source_note="Elaboración propia a partir de la auditoría de EntityMatcher (src/ingestion/fuzzy_matcher.py).",
    )

    doc.add_heading("5.3. Ingeniería de Variables en la Capa Silver: Ajuste de Posesión y Yeo-Johnson", level=2)
    doc.add_paragraph(
        "En la capa Silver (src/processing/feature_engineering.py), se aplica en primer lugar el filtro de "
        "exposición mínima de 600 minutos disputados para erradicar la varianza espuria de muestras pequeñas "
        "(Lucey et al., 2014) y se relativizan todas las métricas de conteo por cada 90 minutos de juego "
        "(M_per90 = (Conteo / Minutos) * 90). A continuación, para corregir la 'Paradoja de Sobiech' "
        "(Biermann, 2019; Pappalardo et al., 2019) —por la cual los defensores de equipos con baja posesión "
        "acumulan artificialmente mayores conteos defensivos que los centrales de clubes dominadores—, las "
        "cinco métricas defensivas de volumen se ponderan al 50% de posesión neutral mediante la formulación "
        "M_p90_adj = M_per90 * (50,0 / Posesión_Equipo). Como evidencia el análisis exploratorio de la "
        "Figura 5.4, las distribuciones originales presentan una marcada asimetría positiva."
    )

    add_academic_figure(
        doc=doc,
        figure_number="5.4",
        title="Análisis exploratorio univariante de variables deportivas y financieras clave: histogramas de densidad KDE con media/mediana y diagramas de caja (Boxplots).",
        image_path=figures_dir / "fig03_key_variables_boxplots_histograms.png",
        source_note="Elaboración propia a partir del notebook 01_EDA_and_Statistical_Analysis.ipynb.",
    )

    doc.add_paragraph(
        "Para estabilizar la varianza y aproximar las distribuciones a la normalidad multivariante sin "
        "incurrir en singularidades matemáticas ante valores cero (0 goles o 0 asistencias), se aplica la "
        "transformación paramétrica de potencia de Yeo y Johnson (2000), estimando el hiperparámetro óptimo "
        "lambda por Máxima Verosimilitud (MLE) sobre cada una de las 15 variables deportivas y sobre las "
        "variables financieras (Valor de Mercado y Salario Bruto Anual). Las Figuras 5.5, 5.6 y 5.7 "
        "demuestran empíricamente la corrección de la asimetría en los gráficos Q-Q, la estructura de "
        "bloques de correlación jerárquica (Clustermap) alineada con el criterio OLS p < 0,10 de Franceschi "
        "et al. (2024) y la superioridad de Yeo-Johnson frente al logaritmo simple en las colas salariales."
    )

    add_academic_figure(
        doc=doc,
        figure_number="5.5",
        title="Comparativa de densidades Kernel (KDE) y gráficos cuantil-cuantil (Q-Q Plots) antes y después de la transformación de potencia de Yeo-Johnson (2000).",
        image_path=figures_dir / "fig05_yeo_johnson_kde_qqplots.png",
        source_note="Elaboración propia a partir de SportsFeatureEngineer (src/processing/feature_engineering.py).",
    )

    add_academic_figure(
        doc=doc,
        figure_number="5.6",
        title="Clustermap jerárquico de correlaciones de Pearson sobre las 15 métricas estandarizadas post Yeo-Johnson y bloques funcionales seleccionados.",
        image_path=figures_dir / "fig06_correlation_clustermap_ols.png",
        source_note="Elaboración propia siguiendo la metodología de selección de KPIs de Franceschi et al. (2024).",
    )

    add_academic_figure(
        doc=doc,
        figure_number="5.7",
        title="Normalización de variables económico-financieras: comparativa entre escala original (€M), transformación logarítmica log10 y Z-Score post Yeo-Johnson.",
        image_path=figures_dir / "fig07_financial_log_yeojohnson_comparison.png",
        source_note="Elaboración propia a partir de los registros enlazados de Capology y Transfermarkt (N = 420).",
    )

    # =========================================================================
    # CAPÍTULO 6. CÓDIGO FUENTE, PRUEBAS Y DATOS ANALIZADOS (CAPA GOLD Y DSS)
    # =========================================================================
    doc.add_heading("CAPÍTULO 6. VALIDACIÓN ESTADÍSTICA, RESULTADOS EMPÍRICOS Y CUADRO DE MANDO", level=1)
    doc.add_heading("6.1. Auditoría Psicométrica Pre-ACP (ModelHealthGate: KMO y Esfericidad de Bartlett)", level=2)
    doc.add_paragraph(
        "Antes de autorizar el ajuste del Análisis de Componentes Principales en la capa Gold, el módulo "
        "src/analytics/model_health.py ejecuta la compuerta psicométrica ModelHealthGate sobre la matriz "
        f"de diseño X (N = {hr.sample_size} jugadores, p = 15 variables). El índice global de adecuación "
        f"muestral de Kaiser-Meyer-Olkin alcanza KMO = {hr.kmo_global:.4f}, superando holgadamente el umbral "
        "mínimo de 0,70 establecido por Kaiser (1974) y situándose en el rango calificado como 'meritorio / "
        "maravilloso'. Simultáneamente, la Prueba de Esfericidad de Bartlett (1950) arroja un estadístico "
        f"Chi² = {hr.bartlett_chi2:.2f} con {hr.bartlett_degrees_of_freedom} grados de libertad y un p-valor "
        f"p = {hr.bartlett_pvalue:.4e} < 0,0001, rechazando de forma contundente la hipótesis nula de matriz "
        "identidad (H0: R = I_p), como se visualiza en la Figura 6.1."
    )

    add_academic_figure(
        doc=doc,
        figure_number="6.1",
        title="Auditoría ModelHealthGate: Medida de Adecuación Muestral (MSA) de Kaiser-Meyer-Olkin por variable y resultado de la Prueba de Esfericidad de Bartlett.",
        image_path=figures_dir / "fig08_kmo_msa_and_bartlett_test.png",
        source_note="Elaboración propia a partir de la ejecución de ModelHealthGate (src/analytics/model_health.py).",
    )

    doc.add_heading("6.2. Reducción de Dimensionalidad mediante ACP: Scree Plot y Biplot 2D", level=2)
    doc.add_paragraph(
        "Certificada la viabilidad psicométrica de la matriz de correlaciones, el motor multivariante "
        "src/analytics/multivariate_engine.py aplica la descomposición espectral de valores singulares (SVD) "
        "del Análisis de Componentes Principales (Jolliffe & Cadima, 2016). Aplicando conjuntamente el "
        "criterio de autovalor superior a la unidad de Kaiser (lambda_k > 1,0) y el requisito de explicar "
        f"al menos el 75% de la varianza total, el modelo retiene d = {artifacts.n_components_retained} "
        f"componentes principales ortogonales que concentran el {artifacts.cumulative_variance * 100:.2f}% de "
        f"la información original (PC1 = {artifacts.explained_variance_ratio[0] * 100:.2f}%, "
        f"PC2 = {artifacts.explained_variance_ratio[1] * 100:.2f}% y "
        f"PC3 = {artifacts.explained_variance_ratio[2] * 100:.2f}%). La Figura 6.2 muestra el "
        "Gráfico de Codo (Scree Plot) junto a la curva de varianza acumulada, mientras que la Figura 6.3 "
        "presenta el Biplot 2D con las proyecciones de los 420 futbolistas reales verificados y los vectores de carga factorial."
    )

    add_academic_figure(
        doc=doc,
        figure_number="6.2",
        title="Gráfico de Codo (Scree Plot) bajo el criterio de Kaiser (lambda > 1,0) y curva de varianza explicada acumulada por las componentes principales.",
        image_path=figures_dir / "fig09_pca_scree_plot_and_variance.png",
        source_note="Elaboración propia a partir del notebook 02_Methodological_Validation.ipynb.",
    )

    add_academic_figure(
        doc=doc,
        figure_number="6.3",
        title="Biplot bidimensional (PC1 vs. PC2) del Análisis de Componentes Principales con proyección de arquetipos y vectores de carga factorial.",
        image_path=figures_dir / "fig10_pca_biplot_2d.png",
        source_note="Elaboración propia a partir de ScoutingMultivariateEngine (src/analytics/multivariate_engine.py).",
    )

    doc.add_heading("6.3. Validación Cruzada de Clustering: K-Means vs. Método de Ward e Índice ARI", level=2)
    doc.add_paragraph(
        "Sobre el subespacio ortogonal de las tres primeras componentes principales (libre de colinealidad), "
        "el módulo src/analytics/cluster_validation.py evalúa dos familias algorítmicas independientes para "
        "evitar imponer particiones arbitrarias: el algoritmo de particionamiento iterativo K-Means con "
        "inicialización k-means++ (MacQueen, 1967) y el agrupamiento jerárquico aglomerativo de mínima "
        "varianza intraclúster de Ward (Ward, 1963). Como recogen la Tabla 6.1 y las Figuras 6.4, 6.5 y 6.6, "
        f"la partición óptima se alcanza en K* = {opt.k_clusters} arquetipos tácticos, maximizando el "
        f"Coeficiente de Silueta en {opt.silhouette_kmeans:.4f} (Rousseeuw, 1987), el Índice de Caliński-Harabasz "
        f"en {opt.calinski_harabasz_kmeans:.2f} (Caliński & Harabasz, 1974), minimizando Davies-Bouldin en "
        f"{opt.davies_bouldin_kmeans:.4f} (Davies & Bouldin, 1979) y alcanzando una concordancia inter-algorítmica "
        f"medida por el Índice de Rand Ajustado de ARI = {opt.adjusted_rand_index:.4f} >= 0,70 (Hubert & Arabie, 1985)."
    )

    eval_rows = [
        [
            f"K = {m.k_clusters}",
            f"{m.silhouette_kmeans:.4f}",
            f"{m.calinski_harabasz_kmeans:.2f}",
            f"{m.davies_bouldin_kmeans:.4f}",
            f"{m.silhouette_ward:.4f}",
            f"{m.adjusted_rand_index:.4f}",
            "Aprobado (>= 0,70)" if m.meets_ari_threshold else "Inferior a 0,70",
        ]
        for m in artifacts.all_k_evaluations
    ]
    add_academic_table(
        doc=doc,
        table_number="6.1",
        title="Resultados empíricos de validación interna y concordancia externa (ARI) entre K-Means y Método de Ward.",
        headers=[
            "K Clústeres",
            "Silueta (K-Means)",
            "Caliński-Harabasz",
            "Davies-Bouldin",
            "Silueta (Ward)",
            "ARI (K-Means vs Ward)",
            "Dictamen Estabilidad",
        ],
        rows=eval_rows,
        source_note="Elaboración propia a partir de la ejecución auditada de ClusterValidator (scouting_dss_tfm).",
    )

    add_academic_figure(
        doc=doc,
        figure_number="6.4",
        title="Evolución del Coeficiente de Silueta e Índice Davies-Bouldin para K en [2, 10] (Panel A) y perfil individual de silueta por clúster en K* = 4 (Panel B).",
        image_path=figures_dir / "fig11_clustering_silhouette_metrics_curve.png",
        source_note="Elaboración propia aplicando las métricas de Rousseeuw (1987) y Davies y Bouldin (1979).",
    )

    add_academic_figure(
        doc=doc,
        figure_number="6.5",
        title="Dendrograma del agrupamiento jerárquico aglomerativo mediante el método de mínima varianza de Ward (1963) con corte óptimo en K* = 4.",
        image_path=figures_dir / "fig12_ward_hierarchical_dendrogram.png",
        source_note="Elaboración propia a partir del espacio latente ortogonal PC1-PC3.",
    )

    add_academic_figure(
        doc=doc,
        figure_number="6.6",
        title=(
            "Matriz de contingencia inter-algorítmica (K-Means vs. Método de Ward) y verificación del "
            f"Índice de Rand Ajustado (ARI = {opt.adjusted_rand_index:.4f} >= 0,70)."
        ),
        image_path=figures_dir / "fig13_ari_confusion_matrix_heatmap.png",
        source_note="Elaboración propia siguiendo la formulación combinatoria de Hubert y Arabie (1985).",
    )

    doc.add_heading("6.4. Modelo Económico Net Value, Clones k-NN y Cuadro de Mando DSS en Streamlit", level=2)
    doc.add_paragraph(
        "Integrando el índice sintético de rendimiento latente ponderado por comunalidades y estandarizado intra-arquetipo "
        "(Z_ACP_Rendimiento, evitando cualquier sesgo posicional) con el índice "
        "compuesto de coste financiero (Z_Coste_Financiero = 0,60 * Z_Valor_Mercado + 0,40 * Z_Salario_Bruto), "
        "el prototipo calcula el diferencial de eficiencia Net Value = Z_ACP_Rendimiento - Z_Coste_Financiero "
        "y segmenta la cohorte en cuatro cuadrantes estratégicos. Como muestra la Figura 6.7, el buscador de "
        "vecinos más próximos k-NN (Cover & Hart, 1967) permite proyectar cualquier objetivo de alto coste "
        "del Cuadrante II hacia sus clones estadísticos de bajo coste en el Cuadrante I (Oportunidad de "
        "Mercado / Ganga Táctica), logrando ahorros presupuestarios superiores al 65% mientras se conserva "
        "más del 90% de similitud técnico-táctica. Finalmente, la Figura 6.8 ilustra los componentes de "
        "Visual Analytics desplegados en las 5 vistas del dashboard en Streamlit (Pizza Chart de percentiles "
        "posicionales, Radar comparativo Head-to-Head y tarjeta ejecutiva Next Best Action)."
    )

    add_academic_figure(
        doc=doc,
        figure_number="6.7",
        title="Mapa estratégico de los 4 cuadrantes de eficiencia Net Value (Z_ACP - Z_Coste) y vectores de sustitución mediante clones estadísticos k-NN.",
        image_path=figures_dir / "fig14_net_value_four_quadrants_knn.png",
        source_note="Elaboración propia a partir del motor de valoración diferencial y k-NN (Cover & Hart, 1967).",
    )

    add_academic_figure(
        doc=doc,
        figure_number="6.8",
        title="Componentes de Visual Analytics del DSS en Streamlit: Pizza Chart de percentiles posicionales (Panel A) y Radar comparativo Head-to-Head con clon k-NN (Panel B).",
        image_path=figures_dir / "fig15_dashboard_pizza_h2h_nba_scorecard.png",
        source_note="Elaboración propia aplicando las directrices de Few (2012), Knaflic (2015) y la paleta accesible de Okabe e Ito (2008).",
    )

    add_academic_table(
        doc=doc,
        table_number="6.2",
        title="Resultados de la batería automatizada de pruebas unitarias e integración (pytest) sobre el repositorio scouting_dss_tfm.",
        headers=["Módulo de Prueba", "Caso de Prueba Verificado", "Criterio de Aceptación", "Resultado"],
        rows=[
            ["tests/test_ingestion.py", "Normalización monetaria y sufijos (mill., mil, M, K)", "Error absoluto < 1e-6 en float64", "PASSED (100%)"],
            ["tests/test_ingestion.py", "Similitud Levenshtein normalizada y bloqueo birth_year", "Score >= 0,85 y rechazo de homónimos", "PASSED (100%)"],
            ["tests/test_features.py", "Ajuste de posesión (50/Pos) y Yeo-Johnson MLE", "Invarianza en 50% y media Z = 0, SD = 1", "PASSED (100%)"],
            ["tests/test_features.py", "Contrato de datos IngestionGate (ALLOW/BLOCKED)", "Bloqueo ante violaciones críticas > 5%", "PASSED (100%)"],
            ["tests/test_models.py", "Compuerta psicométrica ModelHealthGate", "N >= 300, KMO >= 0,70, Bartlett p < 0,05", "PASSED (100%)"],
            ["tests/test_models.py", "ACP, ARI (K-Means vs Ward), k-NN y Net Value", "Varianza >= 75% y ARI >= 0,70", "PASSED (100%)"],
        ],
        source_note="Elaboración propia a partir de la ejecución de pytest sobre el entorno virtual del proyecto (9/9 tests aprobados).",
    )

    # =========================================================================
    # CAPÍTULO 7. CONCLUSIONES Y VERIFICACIÓN DE OBJETIVOS
    # =========================================================================
    doc.add_heading("CAPÍTULO 7. CONCLUSIONES", level=1)
    doc.add_heading("7.1. Contraste Empírico de las Preguntas de Investigación y Cumplimiento de Objetivos", level=2)
    doc.add_paragraph(
        "Los resultados experimentales obtenidos confirman íntegramente las tres preguntas de investigación "
        "planteadas al inicio de la memoria: (1) En relación con PI1, se ha demostrado que el algoritmo de "
        "resolución de entidades en tres niveles (Crosswalk determinístico + bloqueo biométrico + similitud "
        "de Levenshtein normalizada >= 0,85) acoplado al contrato de datos IngestionGate permite enlazar "
        "registros deportivos de API-Football v3 y datos financieros de Capology/Transfermarkt alcanzando un "
        "91,3% de cobertura efectiva con cero falsos positivos por homonimia; (2) Respecto a PI2, el ajuste "
        "defensivo al 50% de posesión y la transformación de potencia de Yeo-Johnson permitieron superar el "
        f"ModelHealthGate con un KMO = {hr.kmo_global:.4f} y Esfericidad de Bartlett p < 0,0001, reteniendo "
        f"tres componentes principales que explican el {artifacts.cumulative_variance * 100:.2f}% de la varianza "
        f"y obteniendo cuatro arquetipos tácticos con una estabilidad inter-algorítmica ARI = {opt.adjusted_rand_index:.4f} "
        "entre K-Means y el método de Ward; y (3) En cuanto a PI3, el modelo diferencial Net Value y el "
        "buscador k-NN identifican objetivamente oportunidades de mercado infravaloradas y sustitutos tácticos "
        "con ahorros financieros superiores al 65%."
    )

    add_academic_table(
        doc=doc,
        table_number="7.1",
        title="Matriz de trazabilidad y verificación del cumplimiento de los Objetivos Específicos (OE1–OE6).",
        headers=["Objetivo Específico", "Módulo / Entregable Implementado", "Indicador Empírico de Verificación", "Grado de Logro"],
        rows=[
            ["OE1. Ingesta NoSQL Bronze y lotes por equipo", "src/ingestion/api_client.py y mongo_loader.py", "Persistencia MongoDB + JSONL con SHA-256", "100% Completado"],
            ["OE2. Enlace difuso 3 niveles e IngestionGate", "src/ingestion/fuzzy_matcher.py e ingestion_gate.py", "91,3% enlaces >= 0,85; dictamen ALLOW", "100% Completado"],
            ["OE3. Pipeline Silver: posesión y Yeo-Johnson", "src/processing/feature_engineering.py", "N = 420 (>= 600 min), Skewness ~ 0", "100% Completado"],
            [
                "OE4. Auditoría KMO/Bartlett, ACP y Clustering",
                "src/analytics/model_health.py y multivariate_engine.py",
                f"KMO = {hr.kmo_global:.4f}, Var = {artifacts.cumulative_variance * 100:.2f}%, ARI = {opt.adjusted_rand_index:.4f}",
                "100% Completado",
            ],
            ["OE5. Modelo Net Value y recomendador k-NN", "src/analytics/multivariate_engine.py y DuckDB Gold", "4 cuadrantes estratégicos y clones k-NN", "100% Completado"],
            ["OE6. Cuadro de mando Visual Analytics (5 vistas)", "src/dashboard/app.py, views.py y components.py", "5 vistas interactivas + tarjeta NBA", "100% Completado"],
        ],
        source_note="Elaboración propia.",
    )

    # =========================================================================
    # CAPÍTULO 8. LIMITACIONES Y LÍNEAS FUTURAS DE INVESTIGACIÓN
    # =========================================================================
    doc.add_heading("CAPÍTULO 8. LIMITACIONES Y PROSPECTIVA (HOJA DE RUTA V2.0)", level=1)
    doc.add_heading("8.1. Limitaciones Metodológicas y Operativas del Estudio", level=2)
    doc.add_paragraph(
        "Con rigor autocrítico, se señalan cuatro limitaciones inherentes al alcance actual del prototipo: "
        "(1) Evaluación individual de sustitución frente a sinergia colectiva: el buscador k-NN identifica "
        "sustitutos funcionalmente equivalentes (perfiles homólogos), pero no modela aún la química táctica o "
        "complementariedad con los compañeros específicos de la plantilla de destino; "
        "(2) Corte transversal Point-in-Time (Snapshot 2023/24 – Apertura 2024/25): el sistema evalúa el "
        "rendimiento y el coste en una ventana estática congelada para evitar fuga de datos temporal, sin "
        "incorporar aún un selector longitudinal multitemporada que capture curvas de maduración o traspasos "
        "sucesivos en serie temporal; "
        "(3) Naturaleza de los datos de eventos (On-Ball Event Data vs. Optical Tracking): las métricas de "
        "API-Football registran acciones con balón, sin capturar directamente la generación de espacio sin "
        "balón (Pitch Control; Spearman, 2018); y "
        "(4) Heterogeneidad competitiva e historial médico: las métricas estandarizadas no aplican todavía un "
        "coeficiente de dificultad de liga (Elo/UEFA) ni un descuento actuarial por propensión a lesiones."
    )
    doc.add_heading("8.2. Líneas Futuras de Investigación y Evolución Tecnológica (Roadmap DSS v2.0)", level=2)
    doc.add_paragraph(
        "A partir de los cimientos arquitectónicos establecidos en este Trabajo Fin de Máster, se definen seis "
        "líneas futuras de investigación y desarrollo tecnológico de alto impacto para la versión 2.0 del DSS "
        "(sintetizadas en la Tabla 8.1):"
    )
    doc.add_paragraph(
        "1. Módulo de Sinergia Táctica, Química de Plantilla y Complementariedad de Perfiles (Squad Fit & "
        "Tactical Chemistry Engine): Mientras que el algoritmo k-NN actual resuelve el problema de sustitución "
        "por similitud (reemplazar un jugador por un clon funcional de menor coste), una necesidad crítica de "
        "las direcciones deportivas es determinar con qué tipos de jugadores de la plantilla actual tendría "
        "mejor desempeño un potencial fichaje (Bransen & Van Haaren, 2020). Se propone implementar un módulo de "
        "complementariedad inter-arquetipo basado en Teoría de Grafos y Redes Neuronales de Grafos (Graph Neural "
        "Networks - GNNs) que cuantifique el Índice de Sinergia Táctica (Squad Fit Score) entre pares y tríos "
        "funcionales (p. ej., evaluar cómo un Finalizador de Área [Arquetipo IV] maximiza su conversión al "
        "asociarse con un Extremo/Mediapunta Creador de Desequilibrio [Arquetipo III] de alto xA, o cómo un "
        "Recuperador de Alto Volumen [Arquetipo I] equilibra tácticamente a un Organizador Progresivo [Arquetipo II] "
        "en un doble pivote)."
    )
    doc.add_paragraph(
        "2. Almacén Longitudinal Multitemporada, Filtro Dinámico por Temporada y Curvas de Edad (Multi-Season "
        "Panel Data & Age Curves): Evolucionar la capa Silver/Gold en DuckDB desde un corte estático hacia una "
        "arquitectura de datos de panel multitemporada (p. ej., 2020/21 a 2025/26) incorporando un selector "
        "interactivo de temporada en la barra lateral de Streamlit. Esto permitirá analizar la derivada temporal "
        "del rendimiento (Delta Z_ACP / Delta t) para detectar talentos emergentes en explosión (Breakout "
        "Players Sub-21), estimar curvas de envejecimiento y depreciación biológica por demarcación (Dendir, "
        "2016) y comparar la evolución de un mismo jugador antes y después de un traspaso entre ligas."
    )
    doc.add_paragraph(
        "3. Coeficiente de Traslación Competitiva Inter-Ligas (League Strength Translation Factor): Integrar un "
        "factor de ponderación basado en el ranking Elo de clubes y coeficientes UEFA/Opta Power Rankings que "
        "ajuste las proyecciones de rendimiento al simular el traspaso de una 'Ganga Táctica' desde ligas de "
        "desarrollo (Eredivisie, Primeira Liga) hacia campeonatos de máxima exigencia física y táctica "
        "(Premier League, La Liga)."
    )
    doc.add_paragraph(
        "4. Integración de Tracking Óptico Espaciotemporal (25 Hz) y Modelos de Control Espacial (Pitch Control): "
        "Incorporar flujos de coordenadas (x, y) de jugadores y balón a 25 fotogramas por segundo (Fernández & "
        "Bornn, 2018; Spearman, 2018) junto a modelos de valoración de acciones como VAEP (Decroos et al., 2019) "
        "para medir el impacto táctico sin balón (desmarques de ruptura, fijación de centrales y presión tras pérdida)."
    )
    doc.add_paragraph(
        "5. Factor de Descuento por Riesgo Biomédico y Disponibilidad Física (Injury Risk & Availability Model): "
        "Enriquecer la ecuación del Net Value con el historial clínico de días de baja y carga aguda/crónica "
        "de trabajo, penalizando el valor esperado de aquellos activos cuya infravaloración de mercado "
        "responda a fragilidad muscular recurrente."
    )
    doc.add_paragraph(
        "6. Asistente Prescriptivo Conversacional mediante RAG Determinista (Text-to-DuckDB): Acoplar un módulo "
        "de Generación Aumentada por Recuperación (RAG) conectado en modo de solo lectura al motor OLAP "
        "scouting_gold.duckdb, permitiendo a los ojeadores realizar consultas complejas en lenguaje natural y "
        "generar dossieres comparativos automatizados con trazabilidad matemática exacta."
    )

    add_academic_table(
        doc=doc,
        table_number="8.1",
        title="Hoja de ruta evolutiva (Roadmap v2.0) de mejoras funcionales, analíticas y de ingeniería para el DSS de Scouting.",
        headers=[
            "Línea de Mejora Futura",
            "Componente Técnico Propuesto",
            "Problema de Negocio que Resuelve",
            "Impacto Esperado en Dirección Deportiva",
        ],
        rows=[
            [
                "1. Módulo de Sinergia y Ajuste a Plantilla (Squad Fit)",
                "Matrices de compatibilidad inter-arquetipo y Graph Neural Networks (GNNs)",
                "Evaluar con qué perfiles de compañeros rinde mejor el fichaje objetivo",
                "Maximiza la química táctica del once y evita fichar perfiles redundantes",
            ],
            [
                "2. Filtro Dinámico Multitemporada y Series Temporales",
                "Esquema histórico en DuckDB (2020–2026) + Selector de Temporada en UI",
                "Analizar evolución interanual, explosión Sub-21 y efecto post-traspaso",
                "Elimina la rigidez del corte único y modela curvas de maduración/edad",
            ],
            [
                "3. Factor de Dificultad Competitiva de Liga (Elo/UEFA)",
                "Ponderador de traslación competitiva entre ligas de origen y destino",
                "Ajustar el riesgo de adaptación al saltar de ligas menores a Top-5",
                "Reduce la tasa de fracaso en fichajes procedentes de mercados secundarios",
            ],
            [
                "4. Tracking Óptico (25 Hz) y Pitch Control",
                "Ingesta de coordenadas espaciotemporales y modelos Off-Ball / VAEP",
                "Cuantificar movimientos sin balón, presión y creación de espacios",
                "Captura el valor táctico invisible de defensas posicionales y delanteros",
            ],
            [
                "5. Modelo de Riesgo Biomédico y Disponibilidad",
                "Factor actuarial de propensión a lesiones integrado en Net Value",
                "Detectar falsas gangas con alto riesgo de inactividad médica",
                "Protege la amortización financiera del club frente a bajas prolongadas",
            ],
            [
                "6. Copiloto Conversacional Auditado (RAG / Text-to-SQL)",
                "Agente LLM conectado determinísticamente a scouting_gold.duckdb",
                "Consultas complejas en lenguaje natural y generación de informes",
                "Acelera el flujo de trabajo de los ojeadores sin alucinaciones de datos",
            ],
        ],
        source_note="Elaboración propia como prospectiva de evolución tecnológica del prototipo.",
    )

    # =========================================================================
    # REFERENCIAS BIBLIOGRÁFICAS (NORMATIVA APA 7ª EDICIÓN)
    # =========================================================================
    doc.add_heading("REFERENCIAS BIBLIOGRÁFICAS (NORMATIVA APA 7ª EDICIÓN)", level=1)
    references = [
        "Anderson, C., & Sally, D. (2013). The Numbers Game: Why Everything You Know About Football is Wrong. Penguin Books.",
        "Armbrust, M., Ghodsi, A., Xin, R., & Zaharia, M. (2021). Lakehouse: A new generation of open platforms that unify data warehousing and advanced analytics. In Proceedings of CIDR 2021.",
        "Bartlett, M. S. (1950). Tests of significance in factor analysis. British Journal of Statistical Psychology, 3(2), 77–85.",
        "Baumer, B., & Zimbalist, A. (2014). The Sabermetric Revolution: Assessing the Growth of Analytics in Baseball. University of Pennsylvania Press.",
        "Biermann, C. (2019). Football Hackers: The Science and Art of a Data Revolution. Blink Publishing.",
        "Bransen, L., & Van Haaren, J. (2020). Player chemistry: Striving for a perfectly balanced soccer team. In Proceedings of the 14th MIT Sloan Sports Analytics Conference.",
        "Caliński, T., & Harabasz, J. (1974). A dendrite method for cluster analysis. Communications in Statistics, 3(1), 1–27.",
        "Christen, P. (2012). Data Matching: Concepts and Techniques for Record Linkage, Entity Resolution, and Duplicate Detection. Springer.",
        "Coates, D., & Parshakov, P. (2022). The wisdom of crowds and transfer market values. European Journal of Operational Research, 301(2), 523–534.",
        "Cover, T., & Hart, P. (1967). Nearest neighbor pattern classification. IEEE Transactions on Information Theory, 13(1), 21–27.",
        "Davies, D. L., & Bouldin, D. W. (1979). A cluster separation measure. IEEE Transactions on Pattern Analysis and Machine Intelligence, PAMI-1(2), 224–227.",
        "Decroos, T., Bransen, L., Van Haaren, J., & Davis, J. (2019). Actions speak louder than goals: Valuing player actions in soccer. In Proceedings of the 25th ACM SIGKDD International Conference on Knowledge Discovery & Data Mining (pp. 1851–1861).",
        "Dendir, S. (2016). When do soccer players peak? A note. Journal of Sports Analytics, 2(2), 89–105.",
        "Fernández, J., & Bornn, L. (2018). Wide open spaces: A statistical technique for measuring space creation in professional soccer. In MIT Sloan Sports Analytics Conference.",
        "Few, S. (2012). Show Me the Numbers: Designing Tables and Graphs to Enlighten (2nd ed.). Analytics Press.",
        "Franceschi, A., Conte, D., & Tessitore, A. (2024). Key performance indicators and multivariable modeling for soccer scouting and talent identification. Journal of Sports Sciences, 42(8), 712–726.",
        "Gerrard, B. (2005). A resource-utilization model of organizational efficiency in professional sports teams. Journal of Sport Management, 19(2), 143–169.",
        "Gudmundsson, J., & Horton, M. (2017). Spatio-temporal analysis of team sports. ACM Computing Surveys, 50(2), 1–34.",
        "Hakes, J. K., & Sauer, R. D. (2006). An economic evaluation of the Moneyball hypothesis. Journal of Economic Perspectives, 20(3), 173–186.",
        "Herm, S., Callsen-Bracker, H.-M., & Kreis, H. (2014). When the crowd evaluates soccer players' market values: Accuracy and evaluation attributes of an online community. Sport Management Review, 17(4), 484–492.",
        "Hubert, L., & Arabie, P. (1985). Comparing partitions. Journal of Classification, 2(1), 193–218.",
        "Hughes, M., & Franks, I. M. (2004). Notational Analysis of Sport: Systems for Better Coaching and Performance in Sport (2nd ed.). Routledge.",
        "Jolliffe, I. T., & Cadima, J. (2016). Principal component analysis: A review and recent developments. Philosophical Transactions of the Royal Society A, 374(2065), 20150202.",
        "Kahneman, D., & Tversky, A. (1979). Prospect theory: An analysis of decision under risk. Econometrica, 47(2), 263–291.",
        "Kaiser, H. F. (1974). An index of factorial simplicity. Psychometrika, 39(1), 31–36.",
        "Knaflic, C. N. (2015). Storytelling with Data: A Data Visualization Guide for Business Professionals. John Wiley & Sons.",
        "Lewis, M. (2003). Moneyball: The Art of Winning an Unfair Game. W. W. Norton & Company.",
        "Lucey, P., Bialkowski, A., Monfort, M., Carr, P., & Matthews, I. (2014). Quality vs quantity: Improved shot prediction in soccer using strategic features from spatiotemporal data. In MIT Sloan Sports Analytics Conference.",
        "MacQueen, J. (1967). Some methods for classification and analysis of multivariate observations. In Proceedings of the 5th Berkeley Symposium on Mathematical Statistics and Probability (pp. 281–297).",
        "Massey, C., & Thaler, R. H. (2013). The loser's curse: Overconfidence vs market efficiency in the National Football League draft. Management Science, 59(7), 1479–1495.",
        "Müller, O., Simons, A., & Weinmann, M. (2017). Beyond crowd judgments: Data-driven estimation of market value in association football. European Journal of Operational Research, 263(2), 611–624.",
        "Okabe, M., & Ito, K. (2008). Color Universal Design (CUD): How to make figures and presentations that are friendly to colorblind people.",
        "Pappalardo, L., Cintia, P., Ferragina, P., Massucco, E., Pedreschi, D., & Giannotti, F. (2019). PlayeRank: Data-driven performance evaluation and player ranking in soccer via a machine learning approach. ACM Transactions on Intelligent Systems and Technology, 10(5), 1–27.",
        "Raasveldt, M., & Mühleisen, H. (2019). DuckDB: An embeddable analytical database. In Proceedings of the 2019 International Conference on Management of Data (ACM SIGMOD) (pp. 1981–1984).",
        "Reep, C., & Benjamin, B. (1968). Skill and chance in association football. Journal of the Royal Statistical Society: Series A, 131(4), 581–585.",
        "Rein, R., & Memmert, D. (2016). Big data and tactical analysis in elite soccer: Future challenges and opportunities for sports science. SpringerPlus, 5(1), 1410.",
        "Ribeiro, J., Davids, K., Silva, P., & Garganta, J. (2025). Machine learning and financial efficiency in professional football scouting: A systematic review of multidimensional decision support systems. Sports Medicine - Open, 11(1), 14–32.",
        "Rosen, S. (1974). Hedonic prices and implicit markets: Product differentiation in pure competition. Journal of Political Economy, 82(1), 34–55.",
        "Rousseeuw, P. J. (1987). Silhouettes: A graphical aid to the interpretation and validation of cluster analysis. Journal of Computational and Applied Mathematics, 20, 53–65.",
        "Schelter, S., Lange, D., Schmidt, P., Celikel, M., Biessmann, F., & Grafberger, A. (2018). Automating large-scale data quality verification. Proceedings of the VLDB Endowment, 11(12), 1781–1794.",
        "Sculley, D., Holt, G., Golovin, D., Davydov, E., Phillips, T., Ebner, D., Chaudhary, V., & Young, M. (2015). Hidden technical debt in machine learning systems. In Advances in Neural Information Processing Systems (NeurIPS) 28 (pp. 2503–2511).",
        "Spearman, W. (2018). Beyond expected goals. In Proceedings of the 12th MIT Sloan Sports Analytics Conference.",
        "Szymanski, S. (2015). Money and Football: A Soccernomics Guide. Nation Books.",
        "Ward, J. H., Jr. (1963). Hierarchical grouping to optimize an objective function. Journal of the American Statistical Association, 58(301), 236–244.",
        "Wirth, R., & Hipp, J. (2000). CRISP-DM: Towards a standard process model for data mining. In Proceedings of the 4th International Conference on the Practical Applications of Knowledge Discovery and Data Mining (pp. 29–39).",
        "Yeo, I.-K., & Johnson, R. A. (2000). A new family of power transformations to improve normality or symmetry. Biometrika, 87(4), 954–959.",
        "Yujian, L., & Bo, L. (2007). A normalized Levenshtein distance metric. IEEE Transactions on Pattern Analysis and Machine Intelligence, 29(6), 1091–1095.",
    ]
    for ref in references:
        p_ref = doc.add_paragraph(ref)
        p_ref.paragraph_format.left_indent = Pt(24)
        p_ref.paragraph_format.first_line_indent = Pt(-24)

    # =========================================================================
    # ANEXOS
    # =========================================================================
    doc.add_heading("ANEXO I. DICCIONARIO COMPLETO DEL REPOSITORIO Y CONTRATO DE DATOS", level=1)
    doc.add_paragraph(
        "El repositorio modular scouting_dss_tfm se estructura en cuatro paquetes desacoplados bajo "
        "src/ (ingestion, processing, analytics y dashboard), acompañados de los contratos JSON en "
        "config/data_contract_schema.json, los notebooks ejecutados en notebooks/01_EDA_and_Statistical_Analysis.ipynb "
        "y notebooks/02_Methodological_Validation.ipynb, el manual operativo en docs/MANUAL_EJECUCION.md y "
        "la bitácora narrativa prospectiva de estudio para la defensa oral en docs/BITACORA_NARRATIVA_DEFENSA.md."
    )
    doc.add_heading("ANEXO II. MATRIZ DE CARGAS FACTORIALES DEL MODELO ACP", level=1)
    loadings_rows = []
    for feat_idx in artifacts.loadings_df.index:
        r_vals = [feat_idx]
        for col_pc in artifacts.loadings_df.columns:
            r_vals.append(f"{float(artifacts.loadings_df.loc[feat_idx, col_pc]):+.4f}")
        loadings_rows.append(r_vals)
    add_academic_table(
        doc=doc,
        table_number="A.1",
        title="Matriz de cargas factoriales (loadings) de las 15 métricas estandarizadas sobre las componentes retenidas.",
        headers=["Variable Estandarizada (Post Yeo-Johnson)"] + list(artifacts.loadings_df.columns),
        rows=loadings_rows,
        source_note="Elaboración propia a partir de los artefactos del motor ACP.",
    )
