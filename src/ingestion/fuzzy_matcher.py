"""Motor de Resolución de Entidades (Fuzzy Record Linkage) entre fuentes deportivas y financieras.

Resuelve la ausencia de claves foráneas compartidas entre API-Football v3 y los
repositorios financieros (Capology y Transfermarkt) mediante normalización canónica
Unicode NFKD, bloqueo por cohorte de año de nacimiento (Blocking Strategy) y distancia
de edición normalizada de Levenshtein (Yujian & Bo, 2007) implementada en C++ vía
`RapidFuzz`, exigiendo un umbral mínimo de similitud de nombre >= 0.85.

Referencias Académicas:
    - Christen, P. (2012). Data Matching: Concepts and Techniques for Record Linkage,
      Entity Resolution, and Duplicate Detection. Springer.
    - Fellegi, I. P., & Sunter, A. B. (1969). A theory for record linkage. Journal of
      the American Statistical Association, 64(328), 1183-1210.
    - Levenshtein, V. I. (1966). Binary codes capable of correcting deletions,
      insertions, and reversals. Soviet Physics Doklady, 10(8), 707-710.
    - Yujian, L., & Bo, L. (2007). A normalized Levenshtein distance metric. IEEE
      Transactions on Pattern Analysis and Machine Intelligence, 29(6), 1091-1095.
"""

from dataclasses import dataclass
import logging
import re
import unicodedata
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
from rapidfuzz.distance import Levenshtein

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class EntityMatchResult:
    """Resultado auditable del emparejamiento de un futbolista entre dos fuentes."""

    player_id: int
    sport_name: str
    financial_name: str
    name_similarity: float
    club_similarity: float
    birth_year_match: bool
    composite_score: float
    matched: bool


class FuzzyEntityMatcher:
    """Motor de enlace de registros basado en distancia de Levenshtein normalizada."""

    def __init__(
        self,
        similarity_threshold: float = 0.85,
        weight_name: float = 0.65,
        weight_birth_year: float = 0.20,
        weight_club: float = 0.15,
        require_exact_birth_year_on_ambiguity: bool = True,
    ) -> None:
        """Inicializa el emparejador difuso con pesos y umbral auditables."""
        if not 0.0 < similarity_threshold <= 1.0:
            raise ValueError("El umbral similarity_threshold debe pertenecer a (0.0, 1.0].")

        self.similarity_threshold = similarity_threshold
        self.weight_name = weight_name
        self.weight_birth_year = weight_birth_year
        self.weight_club = weight_club
        self.require_exact_birth_year_on_ambiguity = require_exact_birth_year_on_ambiguity

    @staticmethod
    def normalize_string(text: str) -> str:
        """Aplica normalización canónica Unicode NFKD, elimina diacríticos y signos no alfanuméricos."""
        if not text:
            return ""
        nfkd_form = unicodedata.normalize("NFKD", str(text))
        ascii_str = "".join(c for c in nfkd_form if not unicodedata.combining(c))
        cleaned = re.sub(r"[^a-zA-Z0-9\s#]", " ", ascii_str).lower()
        return re.sub(r"\s+", " ", cleaned).strip()

    @classmethod
    def normalized_levenshtein_similarity(cls, str_a: str, str_b: str) -> float:
        """Calcula la similitud de Levenshtein normalizada en el intervalo $[0, 1]$."""
        norm_a = cls.normalize_string(str_a)
        norm_b = cls.normalize_string(str_b)
        if not norm_a and not norm_b:
            return 1.0
        if not norm_a or not norm_b:
            return 0.0
        return float(Levenshtein.normalized_similarity(norm_a, norm_b))

    def match_records(
        self,
        sport_records: List[Dict[str, Any]],
        financial_records: List[Dict[str, Any]],
    ) -> Tuple[pd.DataFrame, List[EntityMatchResult]]:
        """Cruza la colección deportiva con la financiera aplicando bloqueo y umbral >= 0.85."""
        fin_by_year: Dict[int, List[Dict[str, Any]]] = {}
        for fin_doc in financial_records:
            byear = int(fin_doc.get("birth_year", 0))
            fin_by_year.setdefault(byear, []).append(fin_doc)

        merged_rows: List[Dict[str, Any]] = []
        audit_results: List[EntityMatchResult] = []

        for s_doc in sport_records:
            player_id = int(s_doc["player_id"])
            s_name = str(s_doc.get("player_name", ""))
            s_club = str(s_doc.get("club_name", ""))
            s_year = int(s_doc.get("birth_year", 0))

            candidates = list(fin_by_year.get(s_year, []))
            if not candidates:
                candidates = (
                    fin_by_year.get(s_year - 1, [])
                    + fin_by_year.get(s_year + 1, [])
                    + financial_records
                )

            best_candidate: Optional[Dict[str, Any]] = None
            best_name_sim = 0.0
            best_club_sim = 0.0
            best_composite = -1.0
            best_year_match = False

            for f_doc in candidates:
                f_name = str(f_doc.get("player_name_raw", ""))
                f_club = str(f_doc.get("club_name_raw", ""))
                f_year = int(f_doc.get("birth_year", -1))

                name_sim = self.normalized_levenshtein_similarity(s_name, f_name)
                if name_sim < self.similarity_threshold:
                    continue

                year_exact = s_year == f_year
                if (
                    self.require_exact_birth_year_on_ambiguity
                    and name_sim < 0.95
                    and not year_exact
                ):
                    continue

                club_sim = self.normalized_levenshtein_similarity(s_club, f_club)
                year_score = 1.0 if year_exact else 0.0
                composite = (
                    self.weight_name * name_sim
                    + self.weight_birth_year * year_score
                    + self.weight_club * club_sim
                )

                if composite > best_composite:
                    best_composite = composite
                    best_candidate = f_doc
                    best_name_sim = name_sim
                    best_club_sim = club_sim
                    best_year_match = year_exact

            if best_candidate is not None and best_name_sim >= self.similarity_threshold:
                merged_row = {
                    **s_doc,
                    "market_value_eur": float(best_candidate["market_value_eur"]),
                    "annual_gross_salary_eur": float(best_candidate["annual_gross_salary_eur"]),
                    "contract_expiration_year": best_candidate.get("contract_expiration_year"),
                    "fuzzy_match_score": round(best_name_sim, 4),
                    "composite_match_score": round(best_composite, 4),
                }
                merged_rows.append(merged_row)
                audit_results.append(
                    EntityMatchResult(
                        player_id=player_id,
                        sport_name=s_name,
                        financial_name=str(best_candidate.get("player_name_raw", "")),
                        name_similarity=round(best_name_sim, 4),
                        club_similarity=round(best_club_sim, 4),
                        birth_year_match=best_year_match,
                        composite_score=round(best_composite, 4),
                        matched=True,
                    )
                )
            else:
                audit_results.append(
                    EntityMatchResult(
                        player_id=player_id,
                        sport_name=s_name,
                        financial_name="",
                        name_similarity=round(best_name_sim, 4),
                        club_similarity=0.0,
                        birth_year_match=False,
                        composite_score=0.0,
                        matched=False,
                    )
                )

        return pd.DataFrame(merged_rows), audit_results
