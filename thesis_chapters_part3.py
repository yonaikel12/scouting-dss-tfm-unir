"""Desarrollo matemático profundo, casos de estudio empíricos y Anexo III para `memoria_TFM_UNIR.docx`."""

from pathlib import Path
from docx import Document
import pandas as pd

from src.analytics.multivariate_engine import MultivariateModelArtifacts
from thesis_chapters_part1 import add_academic_table


def write_deep_mathematical_and_empirical_annex(
    doc: Document, artifacts: MultivariateModelArtifacts, gold_parquet_path: Path
) -> None:
    """Añade el desarrollo formal de formulación matemática, casos de estudio y tablas de auditoría Gold."""
    doc.add_heading("ANEXO III. FORMULACIÓN MATEMÁTICA EXHAUSTIVA Y AUDITORÍA EMPÍRICA DE LA COHORTE GOLD", level=1)

    doc.add_heading("A.3.1. Demostración de la Métrica de Distancia de Edición Normalizada (Yujian & Bo, 2007)", level=2)
    doc.add_paragraph(
        "Sea Sigma un alfabeto finito de caracteres ASCII normalizados tras la descomposición canónica Unicode "
        "NFKD. Dadas dos cadenas de texto A y B pertenecientes a Sigma*, la distancia de Levenshtein elemental "
        "d_L(A, B) se define como el número mínimo de operaciones de inserción, borrado y sustitución necesarias "
        "para transformar A en B. Sin embargo, como demostraron Yujian y Bo (2007) en IEEE Transactions on Pattern "
        "Analysis and Machine Intelligence, el cociente ingenuo d_L(A, B) / max(|A|, |B|) puede violar la "
        "desigualdad triangular en espacios métricos discretos. Por ello, en el módulo src/ingestion/fuzzy_matcher.py "
        "se adopta la formulación métrica normalizada:"
    )
    doc.add_paragraph(
        "    d_N(A, B) = (2 * d_L(A, B)) / (|A| + |B| + d_L(A, B))    ==>    s_N(A, B) = 1 - d_N(A, B)"
    )
    doc.add_paragraph(
        "Combinada de forma convexa con el operador invariante al orden de tokens token_sort_ratio (que ordena "
        "lexicográficamente los lexemas antes de computar la distancia de edición), esta función garantiza que "
        "inversiones frecuentes entre API-Football y Transfermarkt/Capology (p. ej., 'M. Odegaard' frente a "
        "'Martin Odegaard' o 'Lucas Paqueta' frente a 'Paqueta Lucas') alcancen puntuaciones superiores al "
        "umbral de corte estricto tau = 0,85, mientras que el bloqueo determinístico previo por año de nacimiento "
        "(birth_year) reduce la complejidad computacional de O(N * M) a O(N * M / B), siendo B el número de "
        "bloques biométricos disjuntos (Christen, 2012)."
    )

    doc.add_heading("A.3.2. Formulación del Ajuste Contextual de Posesión y Familia de Potencia de Yeo-Johnson (2000)", level=2)
    doc.add_paragraph(
        "Para neutralizar el sesgo de exposición defensiva ('Paradoja de Sobiech'; Biermann, 2019; Pappalardo "
        "et al., 2019), toda variable defensiva de volumen X_i,j (entradas, intercepciones, duelos ganados, "
        "bloqueos y recuperaciones por 90 minutos) de un jugador i perteneciente al club c se pondera hacia "
        "un escenario neutral del 50% de posesión mediante el factor de ajuste contextual:"
    )
    doc.add_paragraph(
        "    M_p90_adj(i, j) = M_per90(i, j) * (50,0 / Posesión_Media_Club(c))"
    )
    doc.add_paragraph(
        "Dado que las tasas por 90 minutos contienen valores exactamente iguales a cero (p. ej., defensores "
        "centrales con 0,00 goles/90) y muestran asimetría positiva severa, la transformación de Box-Cox "
        "(1964) resulta matemáticamente inaplicable al exigir soporte estrictamente positivo (y > 0). Por "
        "consiguiente, el módulo src/processing/feature_engineering.py implementa la familia uniparamétrica "
        "continua de Yeo y Johnson (2000) definida en toda la recta real:"
    )
    doc.add_paragraph(
        "    psi(y; lambda) = ((y + 1)^lambda - 1) / lambda                  si y >= 0, lambda != 0\n"
        "    psi(y; lambda) = ln(y + 1)                                      si y >= 0, lambda = 0\n"
        "    psi(y; lambda) = -((-y + 1)^(2 - lambda) - 1) / (2 - lambda)    si y < 0,  lambda != 2\n"
        "    psi(y; lambda) = -ln(-y + 1)                                    si y < 0,  lambda = 2"
    )
    doc.add_paragraph(
        "El parámetro óptimo lambda_j de cada una de las 15 variables deportivas y de las 2 variables "
        "financieras se estima maximizando la función de log-verosimilitud perfilada (Profile Log-Likelihood) "
        "bajo el supuesto de normalidad gaussiana en el espacio transformado, aplicando posteriormente una "
        "estandarización Z-Score exacta (media mu = 0 y desviación típica sigma = 1)."
    )

    doc.add_heading("A.3.3. Adecuación Psicométrica (KMO y Bartlett), SVD del ACP y Criterio de Ward", level=2)
    doc.add_paragraph(
        "Sea R = (1 / (N - 1)) * Z^T * Z la matriz de correlaciones muestrales de dimensión p x p (con p = 15) "
        "y sea P = (p_jk) la matriz de correlaciones parciales anti-imagen obtenida a partir de la inversa "
        "R^(-1). El estadístico global de Kaiser-Meyer-Olkin (Kaiser, 1974) se define como:"
    )
    doc.add_paragraph(
        "    KMO = (Sum_{j != k} r_jk^2) / (Sum_{j != k} r_jk^2 + Sum_{j != k} p_jk^2)"
    )
    doc.add_paragraph(
        "A su vez, el contraste de esfericidad de Bartlett (1950) evalúa la hipótesis nula H0: R = I_p mediante "
        "el estadístico asintóticamente distribuido según una Chi-cuadrado con p(p - 1)/2 grados de libertad:"
    )
    doc.add_paragraph(
        "    Chi^2_Bartlett = -(N - 1 - (2p + 5)/6) * ln(det(R))"
    )
    doc.add_paragraph(
        "Una vez verificadas las condiciones N >= 300, KMO >= 0,70 y p_Bartlett < 0,05 en ModelHealthGate, "
        "la factorización SVD de la matriz Z = U * Sigma * V^T proyecta las observaciones sobre los d "
        "autovectores principales Y = Z * V_d. Sobre este subespacio ortogonal se comparan las particiones "
        "generadas por K-Means y por el método jerárquico de mínima varianza de Ward (1963), cuya distancia "
        "de fusión entre dos clústeres C_a y C_b responde a la recurrencia de Lance-Williams:"
    )
    doc.add_paragraph(
        "    Delta(C_a, C_b) = ((|C_a| * |C_b|) / (|C_a| + |C_b|)) * || mu_a - mu_b ||_2^2"
    )

    if gold_parquet_path.exists():
        df_gold = pd.read_parquet(gold_parquet_path)
        top_opps = df_gold.sort_values(by="net_value", ascending=False).head(15)
        opp_rows = []
        for _, r in top_opps.iterrows():
            opp_rows.append(
                [
                    str(r["player_name"]),
                    str(r["club_name"]),
                    str(r["position_group"]),
                    f"{float(r['market_value_eur'])/1e6:.2f} M€",
                    f"{float(r['annual_gross_salary_eur'])/1e6:.2f} M€",
                    f"{float(r['z_acp_performance']):+.2f}",
                    f"{float(r['z_financial_cost']):+.2f}",
                    f"{float(r['net_value']):+.2f}",
                ]
            )
        add_academic_table(
            doc=doc,
            table_number="A.2",
            title="Top 15 Oportunidades de Mercado (Cuadrante I — Gangas Tácticas) identificadas por el modelo Net Value en la cohorte Gold.",
            headers=[
                "Jugador",
                "Club Origen",
                "Posición",
                "Valor Mercado",
                "Salario Bruto",
                "Z_ACP Rend.",
                "Z_Coste Fin.",
                "Net Value",
            ],
            rows=opp_rows,
            source_note="Elaboración propia a partir de la tabla analítica gold_players en DuckDB (N = 420).",
        )
