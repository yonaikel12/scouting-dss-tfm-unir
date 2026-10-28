"""Capítulos 1 a 4 y utilidades de inserción de figuras UNIR para `memoria_TFM_UNIR.docx`."""

from pathlib import Path
from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt

from src.analytics.multivariate_engine import MultivariateModelArtifacts


def add_academic_figure(
    doc: Document,
    figure_number: str,
    title: str,
    image_path: Path,
    source_note: str,
    width_inches: float = 6.0,
) -> None:
    """Inserta una figura PNG a 300 DPI con título superior en cursiva y fuente inferior en Calibri 9.5 pt."""
    if not image_path.exists():
        return

    p_caption = doc.add_paragraph()
    p_caption.paragraph_format.space_before = Pt(12)
    p_caption.paragraph_format.space_after = Pt(4)
    p_caption.alignment = WD_ALIGN_PARAGRAPH.LEFT
    r_num = p_caption.add_run(f"Figura {figure_number}. ")
    r_num.font.name = "Calibri"
    r_num.font.size = Pt(10)
    r_num.font.bold = True

    r_title = p_caption.add_run(title)
    r_title.font.name = "Calibri"
    r_title.font.size = Pt(10)
    r_title.font.italic = True

    p_img = doc.add_paragraph()
    p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_img.paragraph_format.space_before = Pt(2)
    p_img.paragraph_format.space_after = Pt(2)
    run_img = p_img.add_run()
    run_img.add_picture(str(image_path), width=Inches(width_inches))

    p_source = doc.add_paragraph()
    p_source.paragraph_format.space_before = Pt(2)
    p_source.paragraph_format.space_after = Pt(12)
    p_source.alignment = WD_ALIGN_PARAGRAPH.LEFT
    r_src_lbl = p_source.add_run("Fuente: ")
    r_src_lbl.font.name = "Calibri"
    r_src_lbl.font.size = Pt(9.5)
    r_src_lbl.font.italic = True

    r_src_txt = p_source.add_run(source_note)
    r_src_txt.font.name = "Calibri"
    r_src_txt.font.size = Pt(9.5)


def add_academic_table(
    doc: Document,
    table_number: str,
    title: str,
    headers: list[str],
    rows: list[list[str]],
    source_note: str,
) -> None:
    """Inserta una tabla académica UNIR con título superior en cursiva y nota de fuente inferior."""
    p_caption = doc.add_paragraph()
    p_caption.paragraph_format.space_before = Pt(10)
    p_caption.paragraph_format.space_after = Pt(3)
    run_num = p_caption.add_run(f"Tabla {table_number}. ")
    run_num.font.name = "Calibri"
    run_num.font.size = Pt(10)
    run_num.font.bold = True

    run_title = p_caption.add_run(title)
    run_title.font.name = "Calibri"
    run_title.font.size = Pt(10)
    run_title.font.italic = True

    table = doc.add_table(rows=1 + len(rows), cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.style = "Table Grid"

    hdr_cells = table.rows[0].cells
    for idx, text in enumerate(headers):
        hdr_cells[idx].text = text
        for p in hdr_cells[idx].paragraphs:
            for r in p.runs:
                r.font.name = "Calibri"
                r.font.size = Pt(9.5)
                r.font.bold = True

    for r_idx, row_values in enumerate(rows, start=1):
        row_cells = table.rows[r_idx].cells
        for c_idx, val in enumerate(row_values):
            row_cells[c_idx].text = str(val)
            for p in row_cells[c_idx].paragraphs:
                for r in p.runs:
                    r.font.name = "Calibri"
                    r.font.size = Pt(9.5)

    p_source = doc.add_paragraph()
    p_source.paragraph_format.space_before = Pt(3)
    p_source.paragraph_format.space_after = Pt(10)
    run_src_label = p_source.add_run("Fuente: ")
    run_src_label.font.name = "Calibri"
    run_src_label.font.size = Pt(9.5)
    run_src_label.font.italic = True

    run_src_text = p_source.add_run(source_note)
    run_src_text.font.name = "Calibri"
    run_src_text.font.size = Pt(9.5)


def write_chapters_1_to_4(
    doc: Document, artifacts: MultivariateModelArtifacts, figures_dir: Path
) -> None:
    """Redacta el Resumen, Abstract y los Capítulos 1, 2, 3 y 4 con figuras y tablas integradas."""
    hr = artifacts.health_report
    opt = artifacts.optimal_cluster_metrics

    doc.add_heading("RESUMEN EJECUTIVO / ABSTRACT", level=1)
    doc.add_paragraph(
        "Resumen: La creciente financiarización del fútbol profesional europeo ha transformado la captación "
        "de talento (scouting) en un problema de optimización económica bajo incertidumbre, donde las "
        "direcciones deportivas deben maximizar el rendimiento competitivo sujeto a severas restricciones "
        "salariales y de amortización de traspasos (Szymanski, 2015; Biermann, 2019). El presente Trabajo "
        "Fin de Máster diseña, implementa y valida empíricamente un Sistema de Soporte a la Decisión (DSS) "
        "de scouting basado en una arquitectura Lakehouse Medallion (MongoDB, Apache Parquet, DuckDB y Streamlit) "
        "gobernada por contratos de datos deterministas (IngestionGate; Schelter et al., 2018) y puertas de "
        f"salud estadística (ModelHealthGate: N = {hr.sample_size} >= 300, KMO = {hr.kmo_global:.4f} >= 0,70, "
        f"Esfericidad de Bartlett Chi² = {hr.bartlett_chi2:.2f}, p < 0,0001). El prototipo enlaza registros "
        "de API-Football v3 y Capology/Transfermarkt mediante un algoritmo híbrido de tres niveles (Crosswalk "
        "determinístico, bloqueo biométrico y distancia de Levenshtein normalizada >= 0,85; Christen, 2012; "
        "Yujian & Bo, 2007), ajusta las métricas defensivas al 50% de posesión resolviendo la Paradoja de "
        "Sobiech (Pappalardo et al., 2019; Biermann, 2019), estabiliza la varianza con la transformación de "
        "potencia de Yeo-Johnson (2000), extrae componentes principales reteniendo el "
        f"{artifacts.cumulative_variance * 100:.2f}% de la varianza (Jolliffe & Cadima, 2016), valida cruzadamente "
        f"K-Means y el método de Ward con un Índice de Rand Ajustado ARI = {opt.adjusted_rand_index:.4f} "
        "(Hubert & Arabie, 1985), identifica clones estadísticos vía k-NN y calcula el modelo económico "
        "Net Value = Z_ACP_Rendimiento - Z_Coste_Financiero."
    )
    doc.add_paragraph(
        "Palabras clave: Scouting Deportivo, Sabermetría, Arquitectura Medallion, Resolución de Entidades, "
        "Transformación de Yeo-Johnson, Análisis de Componentes Principales, K-Means, Método de Ward, "
        "Índice de Rand Ajustado, Visual Analytics."
    )
    doc.add_paragraph(
        "Abstract: The increasing financialization of European professional football has transformed talent "
        "identification (scouting) into an economic optimization problem under uncertainty. This Master's "
        "Thesis designs, implements, and empirically validates a Scouting Decision Support System (DSS) "
        "built on a Multi-Hop Medallion Lakehouse architecture (MongoDB, Apache Parquet, DuckDB, and Streamlit) "
        f"governed by automated data contracts (IngestionGate) and psychometric gates (ModelHealthGate: N = {hr.sample_size}, "
        f"KMO = {hr.kmo_global:.4f}, Bartlett Chi² = {hr.bartlett_chi2:.2f}, p < 0.0001). By integrating "
        "API-Football v3 event metrics with Capology and Transfermarkt financial records via three-tier "
        "entity resolution, possession-adjusted defensive metrics, Yeo-Johnson power transformations, PCA "
        f"({artifacts.cumulative_variance * 100:.2f}% explained variance), cross-validated clustering "
        f"(K-Means vs. Ward ARI = {opt.adjusted_rand_index:.4f}), k-NN similarity search, and the Net Value "
        "differential model, the prototype enables objective detection of undervalued market opportunities."
    )

    # CAPÍTULO 1
    doc.add_heading("CAPÍTULO 1. INTRODUCCIÓN Y PLANTEAMIENTO DEL PROBLEMA", level=1)
    doc.add_heading("1.1. Contexto Económico y Motivación en la Industria del Fútbol Profesional", level=2)
    doc.add_paragraph(
        "La industria contemporánea del fútbol profesional europeo ha experimentado durante las últimas dos "
        "décadas una transformación estructural desde una gestión intuitiva hacia una economía altamente "
        "financiarizada e intensiva en datos (Rein & Memmert, 2016; Gudmundsson & Horton, 2017). La entrada "
        "en vigor de las normativas de sostenibilidad financiera de la UEFA (Financial Sustainability Regulations) "
        "y los controles económicos de las ligas nacionales imponen un límite estricto sobre el ratio de coste "
        "de plantilla (salarios brutos anuales más amortización contable de derechos federativos) respecto a los "
        "ingresos operativos ordinarios (Szymanski, 2015). En este ecosistema, la ventaja competitiva sostenible "
        "de clubes de presupuesto medio y medio-bajo reside en su eficiencia asignativa: identificar futbolistas "
        "cuyo rendimiento deportivo latente supere significativamente su coste financiero relativo en el mercado "
        "(Lewis, 2003; Hakes & Sauer, 2006; Gerrard, 2005)."
    )
    doc.add_paragraph(
        "Sin embargo, la adopción de herramientas analíticas en los departamentos de dirección deportiva "
        "frecuentemente se estanca en el denominado 'spreadsheet scouting': hojas de cálculo aisladas con "
        "conteos absolutos de eventos que carecen de gobierno de datos, ajuste por contexto táctico de posesión "
        "y validación psicométrica previa al modelado multivariante (Biermann, 2019; Franceschi et al., 2024). "
        "Esta desconexión entre la ingeniería de datos (MLOps), el análisis estadístico multivariante y la "
        "economía financiera del deporte motiva el desarrollo del presente Trabajo Fin de Máster."
    )

    doc.add_heading("1.2. Formulación del Problema, Sesgos Cognitivos y Preguntas de Investigación", level=2)
    doc.add_paragraph(
        "El proceso tradicional de captación de jugadores adolece de cuatro deficiencias metodológicas y "
        "tecnológicas críticas: (1) fragmentación estructural de las fuentes de datos, dado que las APIs de "
        "rendimiento deportivo (como API-Football v3) omiten las variables salariales y de valor de mercado, "
        "mientras que los portales financieros (Capology y Transfermarkt) carecen de un identificador único "
        "universal que permita cruzarlos directamente (Christen, 2012); (2) sesgo táctico sistemático inducido "
        "por el estilo de posesión del club de origen sobre las métricas defensivas de volumen, fenómeno "
        "conocido en la literatura como la 'Paradoja de Sobiech' (Biermann, 2019; Pappalardo et al., 2019); "
        "(3) asimetría positiva severa, valores extremos y multicolinealidad en las distribuciones tanto "
        "deportivas como salariales (Yeo & Johnson, 2000; Kaiser, 1974; Bartlett, 1950); y (4) vulnerabilidad "
        "de los decisores humanos frente a sesgos cognitivos de disponibilidad, anclaje, recencia y efecto "
        "halo mediático (Kahneman & Tversky, 1979; Massey & Thaler, 2013)."
    )
    doc.add_paragraph(
        "Para dar respuesta científica a esta problemática, se formulan tres Preguntas de Investigación (PI): "
        "PI1: ¿Es posible construir un pipeline de ingeniería de datos con contratos deterministas (IngestionGate) "
        "y enlace de entidades híbrido (Crosswalk + bloqueo biométrico + similitud de Levenshtein >= 0,85) que "
        "unifique estadísticas de eventos y costes financieros sin degradación de integridad? "
        "PI2: ¿Permite la combinación de ajuste por posesión, transformación de Yeo-Johnson y Análisis de "
        "Componentes Principales auditado (KMO >= 0,70, Bartlett p < 0,05) descubrir arquetipos tácticos "
        "estables (ARI >= 0,70 entre K-Means y el método de Ward)? "
        "PI3: ¿Proporciona el diferencial estandarizado Net Value = Z_ACP_Rendimiento - Z_Coste_Financiero, "
        "combinado con búsqueda k-NN, un criterio objetivo para identificar oportunidades de mercado infravaloradas?"
    )

    doc.add_heading("1.3. Delimitación Temporal de la Cohorte y Condición Point-in-Time (Snapshot 2023/24 – Apertura 2024/25)", level=2)
    doc.add_paragraph(
        "En estricto cumplimiento de las buenas prácticas de reproducibilidad en ingeniería de datos MLOps y "
        "prevención de fuga de datos temporal (Temporal Data Leakage), el alcance empírico del presente Trabajo "
        "Fin de Máster se circunscribe a un corte estático congelado (Point-in-Time Snapshot) correspondiente "
        "a la ventana de observación de la temporada europea 2023/2024 y la apertura del curso 2024/2025 "
        "(identificado en el modelo de datos y en la interfaz del DSS mediante el atributo explícito "
        "season_snapshot = '2023/24 - 2024/25'). Cada uno de los N = 420 futbolistas profesionales verificados "
        "en las siete competiciones europeas (La Liga, Premier League, Serie A, Bundesliga, Ligue 1, Primeira Liga "
        "y Eredivisie) figura vinculado al club en el que disputó efectivamente los minutos competitivos auditados "
        "(>= 600 minutos) y en el que se registró el porcentaje medio de posesión de equipo (50 / Posesión_Equipo) "
        "y su valoración salarial y de mercado en dicho punto temporal (p. ej., Leny Yoro registrado en el LOSC "
        "Lille de la Ligue 1 francesa donde acumuló sus métricas previas a su traspaso al Manchester United, o "
        "Robin Le Normand y Mikel Merino en la Real Sociedad). Esta delimitación temporal explícita —visible "
        "permanentemente en el cuadro de mando en Streamlit y en la documentación técnica— impide distorsionar "
        "el ajuste táctico de posesión o el diferencial Net Value con traspasos ocurridos con posterioridad al "
        "periodo de observación de las métricas."
    )

    # CAPÍTULO 2
    doc.add_heading("CAPÍTULO 2. CONTEXTO Y ESTADO DEL ARTE", level=1)
    doc.add_heading("2.1. De la Sabermetría (Moneyball) a la Teoría del Eslabón Débil en el Fútbol", level=2)
    doc.add_paragraph(
        "El paradigma de la Sabermetría, popularizado por Lewis (2003) y formalizado econométricamente por "
        "Hakes y Sauer (2006) y Baumer y Zimbalist (2014), demostró la existencia de ineficiencias de precios "
        "en los mercados laborales deportivos cuando los clubes sobrepagan métricas vistosas pero ruidosas e "
        "infravaloran contribuciones estructurales. No obstante, trasladar este enfoque del béisbol (deporte "
        "discreto y estático) al fútbol asociación exige considerar su naturaleza fluida, continua e "
        "interdependiente (Anderson & Sally, 2013). Anderson y Sally (2013) demostraron empíricamente que el "
        "fútbol es un deporte gobernado por la 'Teoría del Eslabón Débil' (Weak-Link Theory): el resultado "
        "colectivo de un equipo en una temporada regular depende en mayor medida de elevar el nivel del "
        "jugador menos eficiente del once titular (mitigación de fallos sistémicos) que de la contratación "
        "aislada de una superestrella mediática ('Strong-Link')."
    )
    doc.add_heading("2.2. Evolución de las Métricas de Rendimiento y Selección de Variables (Franceschi et al., 2024)", level=2)
    doc.add_paragraph(
        "Desde el análisis notacional pionero de Reep y Benjamin (1968) y su sistematización por Hughes y "
        "Franks (2004), la ciencia de datos deportivos ha evolucionado hacia modelos probabilísticos de valor "
        "esperado como Expected Goals (xG; Lucey et al., 2014; Spearman, 2018), valoración de acciones en "
        "posesión (VAEP; Decroos et al., 2019) y sistemas de ranking multidimensional como PlayeRank "
        "(Pappalardo et al., 2019). En el ámbito específico del scouting profesional —cuyo exponente práctico "
        "más reconocido es el modelo de 'Diamantensuge' implantado por Sven Mislintat en el Borussia Dortmund "
        "y VfB Stuttgart (Biermann, 2019)—, Franceschi et al. (2024) establecieron un marco metodológico "
        "riguroso para la selección de indicadores clave de rendimiento (KPIs): combinación de juicio experto "
        "táctico por demarcación con filtrado econométrico mediante regresión de Mínimos Cuadrados Ordinarios "
        "(OLS) al umbral de significación p < 0,10 y control estricto de colinealidad antes de aplicar "
        "reducción de dimensionalidad."
    )
    doc.add_heading("2.3. Economía del Fútbol: Valoración Hedónica, Crowdsourcing y Eficiencia Financiera", level=2)
    doc.add_paragraph(
        "En la dimensión económica, la teoría de precios hedónicos de Rosen (1974) fundamenta que el salario "
        "y el valor de traspaso de un futbolista reflejan la agregación implícita de sus atributos productivos, "
        "demográficos (edad, perfil de madurez) y contractuales (años restantes de vínculo). Herm et al. (2014) "
        "demostraron mediante el principio de 'sabiduría de las multitudes' (Wisdom of the Crowds) que las "
        "valoraciones agregadas de Transfermarkt explican más del 85% de la varianza de las tasas reales de "
        "traspaso pagadas por los clubes europeos, hallazgo ratificado posteriormente por Müller et al. (2017) "
        "y Coates y Parshakov (2022). Finalmente, Ribeiro et al. (2025) evidenciaron en su revisión sistemática "
        "de ciencia de datos en fútbol que la frontera actual del estado del arte radica en acoplar modelos "
        "no supervisados de perfilado técnico-táctico con métricas de coste financiero estandarizado (salarios "
        "brutos de Capology y amortizaciones de Transfermarkt) bajo arquitecturas reproducibles."
    )

    add_academic_table(
        doc=doc,
        table_number="2.1",
        title="Síntesis comparativa de la literatura científica de referencia y brecha cubierta por el prototipo.",
        headers=["Autor(es) y Año", "Enfoque Metodológico", "Aportación Principal", "Integración en este TFM"],
        rows=[
            ["Hakes & Sauer (2006); Lewis (2003)", "Sabermetría / Econometría Laboral", "Demostración de ineficiencias salariales en mercados deportivos.", "Fundamento del diferencial Net Value."],
            ["Anderson & Sally (2013)", "Economía Conductual y Estadística en Fútbol", "Formulación de la Weak-Link Theory y crítica a conteos brutos.", "Diseño del recomendador de sustitución k-NN."],
            ["Herm et al. (2014); Coates & Parshakov (2022)", "Modelos Hedónicos y Crowdsourcing", "Validación econométrica de valores de mercado de Transfermarkt.", "Ponderación 60% Valor Mercado + 40% Salario."],
            ["Biermann (2019); Pappalardo et al. (2019)", "Ajuste Contextual y PlayeRank", "Resolución de la Paradoja de Sobiech y sesgo de posesión.", "Ajuste sigmoideo/lineal al 50% de posesión."],
            ["Franceschi et al. (2024)", "Selección de KPIs para Scouting", "Filtrado híbrido experto + regresión OLS (p < 0,10).", "Selección de las 15 métricas por 90 minutos."],
            ["Ribeiro et al. (2025)", "Revisión Sistemática ML en Fútbol", "Identificación de la brecha entre ML táctico y finanzas.", "Arquitectura Lakehouse Medallion + DSS integral."],
        ],
        source_note="Elaboración propia a partir de la revisión sistemática de la literatura indexada.",
    )

    # CAPÍTULO 3
    doc.add_heading("CAPÍTULO 3. OBJETIVOS CONCRETOS Y METODOLOGÍA DE TRABAJO", level=1)
    doc.add_heading("3.1. Objetivo General y Objetivos Específicos (OE1–OE6)", level=2)
    doc.add_paragraph(
        "El Objetivo General del presente Trabajo Fin de Máster consiste en diseñar, implementar y validar "
        "empíricamente un Sistema de Soporte a la Decisión (DSS) de scouting deportivo que integre métricas "
        "técnico-tácticas ajustadas por contexto y variables económico-financieras dentro de una arquitectura "
        "Lakehouse Medallion auditable, permitiendo identificar oportunidades de mercado infravaloradas y "
        "clones estadísticos mediante aprendizaje no supervisado y Visual Analytics."
    )
    doc.add_paragraph(
        "Este objetivo general se desglosa en seis Objetivos Específicos (OE): "
        "(OE1) Construir una capa de ingesta NoSQL (Bronze) en MongoDB con auditoría criptográfica SHA-256 "
        "y extracción por lotes de equipos desde API-Football v3; "
        "(OE2) Implementar un motor de resolución de entidades de tres niveles (Crosswalk Reep/dcaribou, "
        "bloqueo biométrico y similitud de Levenshtein >= 0,85 con RapidFuzz) junto a un contrato de datos "
        "automatizado (IngestionGate); "
        "(OE3) Desarrollar el pipeline de ingeniería de variables (Silver) en Apache Parquet aplicando filtrado "
        "de exposición mínima (>= 600 minutos), relativización por 90 minutos, ajuste defensivo al 50% de "
        "posesión y transformación de potencia de Yeo-Johnson; "
        "(OE4) Auditar la adecuación psicométrica (ModelHealthGate: N >= 300, KMO >= 0,70, Bartlett p < 0,05) "
        "y ejecutar el Análisis de Componentes Principales (ACP) y clustering cruzado K-Means vs. Ward "
        "(ARI >= 0,70); "
        "(OE5) Formular el modelo económico Net Value = Z_ACP_Rendimiento - Z_Coste_Financiero y el buscador "
        "de clones estadísticos k-NN sobre DuckDB (Gold); y "
        "(OE6) Desplegar un cuadro de mando interactivo en Streamlit con 5 vistas analíticas y tarjeta de "
        "decisión Next Best Action (NBA)."
    )

    doc.add_heading("3.2. Metodología Híbrida CRISP-DM y Arquitectura Medallion Multi-Hop", level=2)
    doc.add_paragraph(
        "El desarrollo del proyecto articula las seis fases de la metodología estándar CRISP-DM (Cross-Industry "
        "Standard Process for Data Mining; Wirth & Hipp, 2000) con el patrón arquitectónico Lakehouse Medallion "
        "Multi-Hop (Armbrust et al., 2021) y los principios de mitigación de deuda técnica en sistemas de "
        "Machine Learning (Sculley et al., 2015; Schelter et al., 2018). Como se ilustra en la Figura 3.1, "
        "el flujo de datos transita desde la capa Bronze en MongoDB hacia la capa Silver en Apache Parquet y "
        "finalmente hacia la capa Gold en DuckDB (Raasveldt & Mühleisen, 2019), gobernado por dos compuertas "
        "de verificación determinista: IngestionGate y ModelHealthGate."
    )

    add_academic_figure(
        doc=doc,
        figure_number="3.1",
        title="Arquitectura de Ingeniería de Datos Medallion Multi-Hop y puertas de gobernanza MLOps (IngestionGate y ModelHealthGate).",
        image_path=figures_dir / "fig16_medallion_architecture_diagram.png",
        source_note="Elaboración propia a partir del diseño arquitectónico implementado en el repositorio scouting_dss_tfm.",
    )

    # CAPÍTULO 4
    doc.add_heading("CAPÍTULO 4. MARCO NORMATIVO, ÉTICO Y LEGAL", level=1)
    doc.add_heading("4.1. Protección de Datos Personales (RGPD UE 2016/679 y LOPDGDD 3/2018)", level=2)
    doc.add_paragraph(
        "El tratamiento de estadísticas de rendimiento deportivo y estimaciones salariales de futbolistas "
        "profesionales constituye tratamiento de datos personales de personas físicas identificadas conforme "
        "al Artículo 4.1 del Reglamento (UE) 2016/679 (Reglamento General de Protección de Datos, RGPD) y la "
        "Ley Orgánica 3/2018 (LOPDGDD). La base jurídica habilitante del tratamiento reside en el interés "
        "legítimo del responsable (Art. 6.1.f RGPD) para el análisis de rendimiento laboral públicamente "
        "notorio en competiciones profesionales retransmisiones abiertas. En estricto cumplimiento del "
        "principio de minimización de datos (Art. 5.1.c RGPD) y de la prohibición de tratar categorías "
        "especiales de datos (Art. 9 RGPD), el prototipo excluye de forma absoluta cualquier registro clínico, "
        "historial médico de lesiones, biomarcadores fisiológicos invasivos o datos de vida privada."
    )
    doc.add_heading("4.2. Propiedad Intelectual (Directiva 96/9/CE) y Reglamento Europeo de IA (EU AI Act)", level=2)
    doc.add_paragraph(
        "Respecto a la propiedad intelectual sobre bases de datos deportivas y financieras, el proyecto "
        "observa las disposiciones de la Directiva 96/9/CE sobre la protección jurídica de las bases de "
        "datos (derecho sui generis) y se acoge a la excepción de minería de textos y datos con fines de "
        "investigación científica establecida en el Artículo 3 de la Directiva (UE) 2019/790 (DSM Directive), "
        "implementando además mecanismos de limitación de tasa (Rate-Limiting y Exponential Backoff) que "
        "impiden cualquier afectación a la explotación normal de los servidores de origen. Finalmente, en el "
        "marco del Reglamento (UE) 2024/1689 (Reglamento Europeo de Inteligencia Artificial, EU AI Act) y del "
        "Artículo 22 del RGPD sobre decisiones individuales automatizadas, el sistema se diseña expresamente "
        "bajo el paradigma Human-in-the-Loop (Art. 14 EU AI Act): el algoritmo proporciona puntuaciones "
        "explicables (cargas factoriales ACP y distancias euclídeas k-NN) y una recomendación consultiva "
        "Next Best Action (NBA), reservando la decisión contractual final al comité técnico humano."
    )
