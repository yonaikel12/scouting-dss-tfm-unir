"""Módulo Parte 2 (V6 — 40 a 45 páginas): Capítulo 2 completo y consolidado
(Contexto y Estado del Arte — Págs. 10 a 19) con prosa científica continua,
citas APA 7.ª edición, Tabla 2.1 (Ontologías Financieras) y Tabla 2.2 (Estado del Arte).
"""

from __future__ import annotations

from docx import Document

from entrega2_v6_part1 import add_v6_table


def write_chapter_2_estado_del_arte(doc: Document) -> None:
    """Redacta íntegramente el Capítulo 2 (Contexto y Estado del Arte — 100% cerrado)."""
    doc.add_heading("CAPÍTULO 2. CONTEXTO Y ESTADO DEL ARTE", level=1)

    # =========================================================================
    # 2.1. EVOLUCIÓN DEL SCOUTING DEPORTIVO Y SABERMETRÍA
    # =========================================================================
    doc.add_heading(
        "2.1. Evolución del Scouting Deportivo y Sabermetría: De Moneyball a la analítica de eventos y la Teoría del Eslabón Débil",
        level=2,
    )
    doc.add_paragraph(
        "El origen epistemológico de la analítica deportiva moderna se remonta a la revolución sabermétrica "
        "iniciada en el béisbol norteamericano por Bill James durante la década de 1970 y consolidada "
        "institucionalmente por Billy Beane en la franquicia Oakland Athletics a principios del siglo XXI, "
        "hito ampliamente documentado por Lewis (2003) y formalizado en el ámbito de la inteligencia de negocios "
        "por Davenport (2007) y Davenport y Harris (2007). La premisa axiomática de Moneyball demostró que los "
        "mercados laborales deportivos, pese a operar con información públicamente observable y elevados incentivos "
        "monetarios, presentaban severas ineficiencias de valoración derivadas de la dependencia de los ojeadores "
        "tradicionales hacia métricas aparentes pero estadísticamente espurias —como el promedio de bateo simple "
        "o la morfología atlética del jugador— en detrimento de indicadores de eficiencia marginal real como el "
        "porcentaje de embasado (On-Base Percentage, OBP) y el porcentaje de slugging (SLG). Al adquirir activos "
        "sistemáticamente infravalorados por el consenso de la industria, entidades con presupuestos salariales "
        "situados en el cuartil inferior lograron competir en igualdad de condiciones estadísticas frente a las "
        "corporaciones más ricas de su competición."
    )
    doc.add_paragraph(
        "No obstante, la traslación directa de los principios sabermétricos desde un deporte discreto, secuencial "
        "y estático como el béisbol hacia un deporte de invasión continuo, fluido, de baja puntuación y alta "
        "interdependencia espacio-temporal como el fútbol presentó durante años barreras matemáticas sustanciales "
        "(Sumpter, 2016; Biermann, 2019). Mientras que en el béisbol cada lanzamiento constituye un ensayo "
        "cuasi-independiente donde la responsabilidad individual está nítidamente delimitada, en el fútbol once "
        "jugadores interactúan simultáneamente en un espacio continuo de aproximadamente siete mil metros "
        "cuadrados donde un mismo futbolista participa en menos del dos por ciento del tiempo total con el balón "
        "en los pies (Rein & Memmert, 2016; Gudmundsson & Horton, 2017). A ello se añade el carácter estocástico "
        "del marcador en el fútbol: al anotarse una media cercana a 2,6 goles por encuentro en las ligas europeas, "
        "el resultado final de un partido aislado está fuertemente contaminado por la varianza muestral a corto "
        "plazo, lo que invalida cualquier evaluación de talento basada exclusivamente en goles o victorias brutas "
        "(Anderson & Sally, 2013)."
    )
    doc.add_paragraph(
        "La superación de este obstáculo requirió dos avances fundamentales en el estado del arte. Desde una "
        "perspectiva microeconómica y organizacional, Anderson y Sally (2013) formularon la Teoría del Eslabón "
        "Débil (Weak-Link Theory) aplicada al fútbol profesional. A diferencia del baloncesto —que opera como un "
        "juego de eslabón fuerte (Strong-Link Game) donde la contratación de una única superestrella domina la "
        "probabilidad de victoria—, el fútbol constituye estructuralmente una cadena de eslabón débil en la que "
        "el rendimiento global del colectivo está desproporcionadamente condicionado por la fiabilidad táctica "
        "de su décimo o undécimo titular sobre el césped. Un único error de posicionamiento defensivo, una pérdida "
        "en salida de balón bajo presión o un déficit sistemático en la cobertura de duelos individuales anula la "
        "producción ofensiva de los jugadores franquicia. En consecuencia, para los clubes con restricciones "
        "presupuestarias, la asignación óptima del capital deportivo no consiste en concentrar la masa salarial "
        "en un único fichaje mediático sobrevalorado, sino en elevar la calidad mínima de los eslabones "
        "intermedios de la plantilla mediante la identificación de especialistas tácticos eficientes en relación "
        "con su coste (Anderson & Sally, 2013; Biermann, 2019)."
    )
    doc.add_paragraph(
        "En paralelo, desde una perspectiva de ingeniería de datos y modelado estocástico, la consolidación de "
        "los registros estructurados de eventos en el campo (Event Data) estandarizados por proveedores como Opta, "
        "StatsBomb, Wyscout y API-Football permitió descomponer cada partido en aproximadamente 3.000 eventos "
        "discretos georreferenciados y etiquetados temporalmente (Pappalardo et al., 2019; Decroos et al., 2019). "
        "Sobre esta granularidad emergió la segunda generación de métricas avanzadas de fútbol (Sumpter, 2016; "
        "Delgado, 2025): los modelos probabilísticos de Goles Esperados (Expected Goals, xG) y Asistencias "
        "Esperadas (Expected Assists, xA), que cuantifican la probabilidad condicional de que un disparo o un pase "
        "clave culmine en gol en función de la geometría del tiro, el ángulo a portería y la presión defensiva; "
        "así como las métricas de progresión territorial (pases progresivos y conducciones progresivas que acercan "
        "el balón al menos diez metros hacia la línea de fondo rival) y las métricas de recuperación defensiva "
        "ajustadas por el volumen de posesión del equipo, piedra angular del sistema Diamantensuge (Ojo de "
        "Diamante) implementado por Sven Mislintat en el Borussia Dortmund y el Arsenal FC (Biermann, 2019)."
    )

    # =========================================================================
    # 2.2. ECONOMÍA DEL FÚTBOL Y MODELOS DE VALORACIÓN
    # =========================================================================
    doc.add_heading("2.2. Economía del Fútbol y Modelos de Valoración de Activos Deportivos", level=2)

    doc.add_heading(
        "2.2.1. Distinción conceptual y econométrica entre Valor de Uso, Valor de Mercado y Precio de Traspaso (Franceschi et al., 2024)",
        level=3,
    )
    doc.add_paragraph(
        "Uno de los errores metodológicos más extendidos en la literatura empírica sobre analítica deportiva "
        "consiste en tratar como sinónimos intercambiables la utilidad deportiva de un jugador, su valoración de "
        "mercado estimada y el precio monetario efectivo de su transferencia. En su revisión metodológica "
        "seminal sobre la valoración de futbolistas, Franceschi et al. (2024) establecen una taxonomía "
        "ontológica rigurosa que distingue tres magnitudes económicas conceptualmente disjuntas cuya confusión "
        "introduce sesgos severos de endogeneidad en los modelos de apoyo a la decisión:"
    )
    doc.add_paragraph(
        "En primer lugar, el Valor de Uso (Use Value o Sporting Utility) representa la contribución productiva "
        "intrínseca que un futbolista aporta al rendimiento competitivo de una plantilla dentro de un sistema "
        "táctico determinado. Esta dimensión es estrictamente no monetaria y se manifiesta en el espacio "
        "multidimensional de sus acciones sobre el terreno de juego (capacidad de finalización por encima de "
        "lo esperado, generación de peligro asociativo, progresión vertical superando líneas de presión y "
        "recuperación defensiva ajustada por exposición). En nuestro prototipo DSS, el Valor de Uso se formaliza "
        "matemáticamente a través del índice sintético ortogonal Z_ACP_Rendimiento extraído mediante el Análisis "
        "de Componentes Principales sobre quince métricas relativizadas por noventa minutos."
    )
    doc.add_paragraph(
        "En segundo lugar, el Valor de Mercado (Market Value) constituye una estimación teórica y continua del "
        "valor económico de los derechos federativos del jugador en condiciones normales de competencia, "
        "independientemente de que exista o no una transacción inminente (Herm et al., 2014; Franceschi et al., "
        "2024). Siguiendo la teoría de precios hedónicos de Rosen (1974) y la economía de las superestrellas de "
        "Rosen (1981), el Valor de Mercado integra no solo el rendimiento pasado del jugador, sino también su "
        "tasa de depreciación biológica asociada a la edad (alcanzando su máximo estadístico entre los 24 y 26 "
        "años), su notoriedad comercial o mediática y el prestigio macroeconómico de la liga en la que compite."
    )
    doc.add_paragraph(
        "En tercer lugar, el Precio de Traspaso (Transfer Price o Exchange Fee) es una variable discreta y "
        "contingente que únicamente se materializa cuando dos clubes alcanzan un acuerdo bilateral de compraventa "
        "(Müller et al., 2017; Peeters, 2018). A diferencia del Valor de Mercado, el Precio de Traspaso está "
        "fuertemente distorsionado por el poder de negociación asimétrico de las partes, la duración remanente "
        "del contrato laboral tras la Sentencia Bosman de 1995 (un jugador en su último año de contrato se "
        "transfiere con un descuento sustancial o a coste cero como agente libre), la existencia de cláusulas de "
        "rescisión unilaterales y las urgencias financieras de tesorería del club vendedor. Por su parte, el "
        "Salario Bruto Anual (Annual Gross Salary) refleja el flujo de caja recurrente que el club empleador "
        "debe desembolsar cada ejercicio fiscal para retener los servicios del jugador. Como sintetiza la "
        "Tabla 2.1, un sistema de apoyo a la decisión robusto no puede depender de precios de traspaso "
        "históricos incompletos, sino que debe modelizar conjuntamente el Valor de Mercado (Transfermarkt) y "
        "el Salario Bruto Anual (Capology) frente al Valor de Uso técnico-táctico."
    )

    add_v6_table(
        doc=doc,
        table_number="2.1",
        title="Comparativa ontológica y econométrica entre dimensiones financieras en el fútbol profesional.",
        headers=[
            "Dimensión Económica",
            "Naturaleza Conceptual (Franceschi et al., 2024)",
            "Fuente Primaria de Referencia",
            "Determinantes Estructurales Principales",
            "Rol en el Prototipo DSS (scouting_dss_tfm)",
        ],
        rows=[
            [
                "Valor de Uso (Use Value)",
                "Utilidad técnico-táctica intrínseca aportada al sistema colectivo de juego.",
                "API-Football REST v3 (Event Data agregados por 90 minutos).",
                "Producción ofensiva (xG, goles), progresión asociativa (xA, pases clave) y defensa ajustada al 50% de posesión.",
                "Cuantificado mediante el vector latente ortogonal Z_ACP_Rendimiento (4 Componentes Principales = 82,34% var.).",
            ],
            [
                "Valor de Mercado (Market Value)",
                "Estimación hedónica continua del valor teórico del derecho federativo en el mercado.",
                "Transfermarkt (Sabiduría de las Multitudes / Wisdom of Crowds).",
                "Edad biológica (curva cuadrática), minutos jugados, nivel de la liga, estatus internacional y repercusión mediática.",
                "Integrado al 60% en el índice compuesto Z_Coste_Financiero tras transformación Yeo-Johnson.",
            ],
            [
                "Salario Bruto Anual (Annual Gross Salary)",
                "Coste laboral recurrente anualizado asumido en la cuenta de pérdidas y ganancias del club.",
                "Capology (Contratos Verificados y Estimaciones Algorítmicas).",
                "Jerarquía en la plantilla, historial de carrera, poder de negociación del agente y presión fiscal de la liga.",
                "Integrado al 40% en el índice Z_Coste_Financiero y empleado para auditar sostenibilidad salarial.",
            ],
            [
                "Precio de Traspaso (Transfer Fee)",
                "Precio de equilibrio bilateral puntual observado únicamente cuando ocurre un traspaso.",
                "Informes FIFA TMS / Comunicados bursátiles de clubes cotizados.",
                "Años restantes de contrato (efecto Bosman), cláusulas de rescisión, urgencia de liquidez e inflación coyuntural.",
                "Excluido como variable base por truncamiento muestral; sustituido por el par continuo (Valor Mercado, Salario).",
            ],
        ],
        source_note="Elaboración propia a partir de la taxonomía de Franceschi et al. (2024), Herm et al. (2014) y Szymanski (2015).",
    )

    doc.add_heading(
        "2.2.2. Validación científica de la valoración colectiva de Transfermarkt vía Wisdom of Crowds (Herm et al., 2014; Müller et al., 2017; Peeters, 2018)",
        level=3,
    )
    doc.add_paragraph(
        "Dado que los derechos federativos de los futbolistas no cotizan en un mercado bursátil líquido con "
        "formación continua de precios, la comunidad científica y los propios departamentos financieros de los "
        "clubes europeos han recurrido sistemáticamente a las valoraciones publicadas por la plataforma "
        "Transfermarkt. Su mecanismo de tasación constituye una aplicación paradigmática del principio de la "
        "Sabiduría de las Multitudes (Wisdom of Crowds) postulado por Surowiecki (2004), bajo el cual la "
        "agregación estructurada de juicios independientes emitidos por una comunidad diversa de expertos y "
        "observadores converge hacia estimaciones más precisas que las de cualquier tasador individual aislado."
    )
    doc.add_paragraph(
        "No obstante, como demostraron empíricamente Herm et al. (2014) en su estudio fundacional publicado en "
        "el European Journal of Operational Research, Transfermarkt no opera mediante una media aritmética "
        "democrática no filtrada —la cual sería vulnerable a manipulaciones interesadas o sesgos de afición—, "
        "sino a través de un modelo de gobierno jerárquico de multitud ponderada por jueces (Judge-Weighted "
        "Crowd). En este proceso deliberativo, miles de usuarios registrados proponen y justifican ajustes de "
        "valoración en foros segmentados por competición, pero un cuerpo restringido de moderadores seniors y "
        "coordinadores de datos regionales audita los argumentos, pondera la reputación histórica de cada "
        "evaluador y fija el valor oficial de mercado semestralmente. Herm et al. (2014) comprobaron mediante "
        "regresiones econométricas que las estimaciones de esta comunidad explican más del 80% de la varianza "
        "de los precios reales de traspaso posteriormente observados en el mercado."
    )
    doc.add_paragraph(
        "Investigaciones posteriores han profundizado en las propiedades estadísticas y los límites de este "
        "mecanismo colectivo. Müller et al. (2017) desarrollaron un modelo multinivel de aprendizaje automático "
        "sobre múltiples temporadas de las cinco grandes ligas europeas, concluyendo que las valoraciones de "
        "Transfermarkt constituyen el regresor individual con mayor poder predictivo sobre las tasas de "
        "transferencia reales, si bien tienden a presentar cierta inercia conservadora en los extremos de la "
        "distribución (subestimando ligeramente la inflación repentina de jóvenes promesas emergentes y "
        "sobreestimando temporalmente a veteranos de renombre en declive físico). Por su parte, Peeters (2018) "
        "y Coates y Parshakov (2022) demostraron que la información agregada por la multitud de Transfermarkt "
        "incorpora expectativas tácticas y de mercado que superan incluso a modelos econométricos paramétricos "
        "complejos en la predicción de resultados internacionales, validando plenamente su empleo académico como "
        "proxy estándar del coste de adquisición de capital deportivo."
    )

    doc.add_heading(
        "2.2.3. La masa salarial como determinante de la posición competitiva (Szymanski) y estructura salarial de Capology",
        level=3,
    )
    doc.add_paragraph(
        "Si bien el Valor de Mercado aproxima el desembolso de inversión inicial (CAPEX) requerido para adquirir "
        "los derechos de un futbolista, la literatura económica del deporte ha establecido de forma concluyente "
        "que el verdadero indicador de la capacidad competitiva a largo plazo y de la carga financiera real de "
        "un club es su gasto corriente en salarios (OPEX). En sus estudios clásicos sobre la economía del fútbol "
        "europeo, Szymanski (2015) y Kuper y Szymanski (2018) demostraron empíricamente que la masa salarial "
        "agregada de una plantilla explica entre el 85% y el 92% de la varianza en la clasificación final de las "
        "ligas nacionales a lo largo de ciclos plurianuales, mientras que el gasto neto en traspasos aislado "
        "posee una capacidad explicativa sustancialmente menor debido a la frecuente sobrepagación de activos "
        "mediáticos."
    )
    doc.add_paragraph(
        "El mercado salarial refleja una eficiencia informacional superior al mercado de traspasos porque las "
        "renovaciones y renegociaciones contractuales incorporan información privada del club sobre el "
        "rendimiento diario del futbolista, su profesionalidad y su impacto real en el colectivo (Szymanski, "
        "2015). Por esta razón, la evaluación financiera en el scouting moderno exige integrar los datos de "
        "remuneración salarial bruta anual proporcionados por la plataforma especializada Capology. Desde una "
        "perspectiva de calidad del dato, Capology estructura sus registros en dos niveles de certidumbre "
        "documental: los salarios verificados (Verified Salaries), que han sido contrastados directamente con "
        "balances auditados de clubes cotizados, registros oficiales de ligas o al menos dos fuentes "
        "periodísticas financieras independientes; y los salarios estimados algorítmicamente (Estimated "
        "Salaries), inferidos mediante modelos de imputación estratificados por el presupuesto salarial total "
        "declarado del club, la edad, la posición y los minutos disputados por el jugador. La combinación "
        "ponderada del Valor de Mercado de Transfermarkt (60%) y del Salario Bruto Anual de Capology (40%), "
        "previa normalización de potencia de Yeo-Johnson, dota a nuestro prototipo DSS de un estimador compuesto "
        "(Z_Coste_Financiero) robusto tanto frente a la volatilidad especulativa del traspaso como frente a las "
        "rigideces contractuales de la nómina."
    )

    # =========================================================================
    # 2.3. VISUAL ANALYTICS Y SISTEMAS DE APOYO A LA DECISIÓN (DSS)
    # =========================================================================
    doc.add_heading(
        "2.3. Visual Analytics y Sistemas de Apoyo a la Decisión (DSS): reducción de sobrecarga cognitiva en interfaces ejecutivas",
        level=2,
    )
    doc.add_paragraph(
        "La eficacia operativa de un modelo matemático avanzado en un departamento de scouting depende "
        "críticamente de la arquitectura visual mediante la cual sus resultados son comunicados al decisor "
        "humano (el director deportivo, el secretario técnico o el entrenador). Como establecieron Keim et al. "
        "(2008) y Thomas y Cook (2005), la disciplina de Visual Analytics se define como la ciencia del "
        "razonamiento analítico facilitado por interfaces visuales interactivas, cuyo propósito no es meramente "
        "decorativo, sino acoplar la capacidad de cómputo masivo del aprendizaje estadístico con la flexibilidad "
        "heurística y el conocimiento contextual del experto humano."
    )
    doc.add_paragraph(
        "En el diseño de cuadros de mando ejecutivos (Dashboards) para Sistemas de Apoyo a la Decisión (DSS), "
        "Stephen Few (2006, 2012) advierte que el fracaso de la mayoría de las herramientas analíticas corporativas "
        "radica en la fragmentación visual y la saturación de la memoria de trabajo a corto plazo del usuario "
        "(limitada cognitivamente a retener entre cuatro y siete fragmentos de información simultáneos). Siguiendo "
        "el principio de maximización de la ratio tinta-datos (Data-Ink Ratio) de Tufte (2001), Few (2006) "
        "establece que toda interfaz de soporte a la decisión debe suprimir el ruido gráfico no informativo "
        "(chartjunk, rejillas tridimensionales superfluas y degradados ornamentales) y emplear atributos "
        "preatentivos de percepción visual —tales como la posición espacial en un plano cartesiano 2D, la "
        "longitud radial en coordenadas polares y la codificación cromática semántica— que son procesados por "
        "la corteza visual primaria en menos de 200 milisegundos antes de requerir atención consciente."
    )
    doc.add_paragraph(
        "Para estructurar metodológicamente la arquitectura de visualización del prototipo, se adopta el Modelo "
        "Anidado de Diseño y Validación de Visualizaciones (Nested Model for Visualization Design and Validation) "
        "formulado por Tamara Munzner (2009, 2014). Munzner descompone el diseño visual en cuatro niveles "
        "jerárquicos acoplados: (1) la caracterización del problema del dominio (identificar futbolistas "
        "infravalorados y sustitutos tácticos bajo restricción presupuestaria); (2) la abstracción de datos y "
        "tareas (transformar 15 variables colineales y 2 variables monetarias asimétricas en puntuaciones "
        "ortogonales Z, percentiles posicionales P1-P99 y distancias euclídeas k-NN); (3) el diseño de "
        "codificaciones visuales y mecanismos de interacción (aplicando el mantra de búsqueda visual de "
        "Shneiderman, 1996: visión global primero, zoom y filtrado, y detalles bajo demanda); y (4) la "
        "implementación algorítmica eficiente."
    )
    doc.add_paragraph(
        "Asimismo, la narrativa visual del cuadro de mando incorpora los principios de comunicación con datos "
        "de Cole Nussbaumer Knaflic (2015) y el paradigma del arte funcional de Alberto Cairo (2012, 2016). "
        "Knaflic (2015) enfatiza el uso estratégico del contraste cromático focalizado y las anotaciones "
        "contextuales directas sobre el lienzo gráfico (como las líneas divisorias de los cuatro cuadrantes "
        "de Net Value y los vectores direccionales que conectan a una estrella cara con su clon estadístico "
        "económico) para dirigir inmediatamente la atención del directivo hacia la anomalía de mercado. A su "
        "vez, Cairo (2012) sostiene que las visualizaciones polares multivariantes —como las rosetas de "
        "percentiles o Pizza Charts y los radares comparativos Head-to-Head (H2H)— resultan óptimas cuando los "
        "ejes perimetrales se agrupan funcionalmente por dimensiones tácticas coherentes (bloque ofensivo, "
        "bloque creativo-progresivo y bloque defensivo ajustado por posesión) y se colorean mediante la paleta "
        "universalmente accesible para daltónicos de Okabe e Ito (2008)."
    )

    # =========================================================================
    # 2.4. REVISIÓN SISTEMÁTICA DE LA LITERATURA
    # =========================================================================
    doc.add_heading(
        "2.4. Revisión Sistemática de la Literatura: Análisis de modelos multivariantes recientes en fútbol (Ribeiro et al., 2025)",
        level=2,
    )
    doc.add_paragraph(
        "Con el propósito de situar con rigor la contribución científica del presente Trabajo Fin de Máster "
        "dentro del panorama académico actual, se ha llevado a cabo una revisión sistemática de la literatura "
        "sobre aprendizaje no supervisado, reducción de dimensionalidad y valoración económica aplicada al "
        "scouting de fútbol profesional. Recientemente, Ribeiro et al. (2025) publicaron una revisión "
        "sistemática exhaustiva sobre la aplicación de técnicas estadísticas multivariantes y algoritmos de "
        "inteligencia artificial en la identificación de talento y perfilado táctico en el fútbol moderno. "
        "El metaanálisis de Ribeiro et al. (2025) revela tres carencias estructurales recurrentes en los "
        "estudios publicados hasta la fecha:"
    )
    doc.add_paragraph(
        "En primer lugar, la mayoría de los trabajos que aplican Análisis de Componentes Principales (ACP) o "
        "Análisis Factorial sobre estadísticas de partido (como las propuestas exploratorias de agrupamiento "
        "posicional) omiten verificar formalmente los supuestos psicométricos previos de adecuación muestral "
        "(índice Kaiser-Meyer-Olkin, KMO) y no esfericidad de la matriz de correlaciones (contraste de Bartlett), "
        "así como tampoco corrigen previamente la asimetría positiva extrema de las tasas por 90 minutos mediante "
        "transformaciones paramétricas de potencia que admitan valores nulos como la familia de Yeo-Johnson "
        "(2000). En segundo lugar, en el ámbito del agrupamiento no supervisado (Clustering), la literatura "
        "tiende a emplear un único paradigma algorítmico de forma aislada —habitualmente K-Means por su "
        "eficiencia computacional— sin contrastar la estabilidad topológica de la partición obtenida frente a "
        "métodos jerárquicos aglomerativos como el criterio de mínima varianza de Ward (1963) mediante métricas "
        "de concordancia ajustadas por el azar como el Índice de Rand Ajustado (ARI; Hubert & Arabie, 1985)."
    )
    doc.add_paragraph(
        "En tercer lugar, existe una disociación persistente entre los artículos centrados exclusivamente en la "
        "taxonomía táctica de eventos (Pappalardo et al., 2019; Decroos et al., 2019) y los estudios "
        "econométricos orientados a explicar los determinantes del valor de mercado o del salario (Herm et al., "
        "2014; Müller et al., 2017; Franceschi et al., 2024). Como demuestra el cuadro comparativo de la "
        "Tabla 2.2, nuestra propuesta cubre este vacío investigador integrando en un mismo pipeline auditable "
        "el ajuste contextual de posesión al 50%, la normalización de Yeo-Johnson, las compuertas deterministas "
        "de gobernanza (IngestionGate y ModelHealthGate), la validación cruzada K-Means vs. Ward con ARI >= 0,70, "
        "la recuperación de clones por k-NN y la formulación del diferencial econométrico Net Value en un DSS "
        "interactivo validado sobre las seis principales ligas europeas (N = 1.777 jugadores)."
    )

    add_v6_table(
        doc=doc,
        table_number="2.2",
        title="Cuadro comparativo del Estado del Arte sobre modelos multivariantes, valoración económica y DSS en fútbol.",
        headers=[
            "Autor(es) y Año",
            "Enfoque Metodológico y Algorítmico",
            "Ajuste Posesión y Yeo-Johnson",
            "Validación Cruzada Clustering (ARI)",
            "Integración Financiera y DSS Visual",
        ],
        rows=[
            [
                "Herm et al. (2014)",
                "Regresión econométrica hedónica y modelo Judge-Weighted Crowd (Transfermarkt).",
                "No (métricas brutas agregadas sin ajuste por posesión).",
                "No aplica agrupamiento táctico no supervisado.",
                "Alta en valoración de mercado; sin interfaz DSS interactiva de scouting.",
            ],
            [
                "Müller et al. (2017)",
                "Modelos multinivel de regresión para estimación de precios de traspaso en las 5 grandes ligas.",
                "Transformación logarítmica monetaria; sin Yeo-Johnson en eventos.",
                "No evalúa estabilidad de clústeres tácticos.",
                "Integra Transfermarkt, pero carece de búsqueda de clones k-NN y cuadros polares.",
            ],
            [
                "Pappalardo et al. (2019)",
                "Framework PlayeRank basado en aprendizaje supervisado y pesos lineales sobre Event Data.",
                "Contextualización zonal, sin transformación paramétrica Yeo-Johnson.",
                "Clasificación de roles fija sin contraste K-Means vs. Ward (ARI).",
                "Exclusivamente deportivo (Valor de Uso); omite salarios y valores de mercado.",
            ],
            [
                "Franceschi et al. (2024)",
                "Revisión sistemática e identificación de determinantes econométricos del valor de futbolistas.",
                "Distingue variables de volumen y eficiencia; recomienda normalización.",
                "No implementa pipeline de clustering ni compuertas MLOps.",
                "Marco teórico fundamental (Valor de Uso vs. Mercado vs. Precio); sin software DSS.",
            ],
            [
                "Ribeiro et al. (2025)",
                "Revisión sistemática de ACP, clustering y aprendizaje automático en scouting de fútbol.",
                "Identifica como brecha frecuente la omisión de KMO, Bartlett y asimetría.",
                "Señala la falta de validación cruzada entre algoritmos particionales y jerárquicos.",
                "Demanda sistemas DSS integrados que combinen rendimiento táctico y coste.",
            ],
            [
                "Propuesta Propia (TFM UNIR, 2026)",
                "Arquitectura Medallion (MongoDB, Parquet, DuckDB) + ACP SVD + K-Means/Ward + k-NN + Net Value.",
                "Sí: Ajuste al 50% de posesión (Sobiech) + Yeo-Johnson MLE + Z-Score.",
                "Sí: ModelHealthGate (KMO=0,7889) + K-Means vs. Ward (ARI=0,7235 >= 0,70).",
                "Sí: Entity Matching en 3 niveles (Transfermarkt+Capology) + 5 vistas Streamlit + NBA.",
            ],
        ],
        source_note="Elaboración propia a partir de la revisión sistemática de la literatura científica (2014–2026).",
    )
