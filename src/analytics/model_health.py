"""Módulo de auditoría matemática pre-modelado (ModelHealthGate).

Verifica formalmente los supuestos psicométricos y algebraicos requeridos antes de
autorizar la reducción de dimensionalidad mediante Análisis de Componentes Principales (ACP):
1. Suficiencia muestral: N >= 300 (Comrey & Lee, 1992; Tabachnick & Fidell, 2019).
2. Índice de Adecuación Muestral de Kaiser-Meyer-Olkin: KMO >= 0.70 (Kaiser, 1974).
3. Prueba de Esfericidad de Bartlett: p-valor < 0.05 sobre H0: R = I (Bartlett, 1950).
4. Ausencia de colinealidad perfecta / singularidad en la matriz de correlación.

Referencias Académicas:
    - Bartlett, M. S. (1950). Tests of significance in factor analysis. British Journal
      of Statistical Psychology, 3(2), 77-85.
    - Kaiser, H. F. (1974). An index of factorial simplicity. Psychometrika, 39(1), 31-36.
    - Jolliffe, I. T., & Cadima, J. (2016). Principal component analysis: a review and
      recent developments. Philosophical Transactions of the Royal Society A, 374(2065),
      20150202.
"""

from dataclasses import dataclass, field
import logging
import math
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
from scipy import stats

logger = logging.getLogger(__name__)


class StatisticalHealthError(RuntimeError):
    """Excepción lanzada cuando la matriz de datos no supera el ModelHealthGate."""


@dataclass(frozen=True)
class ModelHealthReport:
    """Resultado auditable de las pruebas psicométricas y matriciales pre-ACP."""

    passed: bool
    sample_size: int
    n_features: int
    kmo_global: float
    kmo_per_variable: Dict[str, float]
    bartlett_chi2: float
    bartlett_degrees_of_freedom: int
    bartlett_pvalue: float
    condition_number: float
    diagnostics: List[str] = field(default_factory=list)


class ModelHealthGate:
    """Puerta de salud estadística previa a la reducción dimensional mediante ACP."""

    def __init__(
        self,
        min_sample_size: int = 300,
        min_kmo_global: float = 0.70,
        max_bartlett_pvalue: float = 0.05,
    ) -> None:
        """Configura los umbrales estadísticos del ModelHealthGate."""
        self.min_sample_size = min_sample_size
        self.min_kmo_global = min_kmo_global
        self.max_bartlett_pvalue = max_bartlett_pvalue

    @staticmethod
    def compute_kmo(data: np.ndarray, feature_names: List[str]) -> Tuple[float, Dict[str, float]]:
        """Calcula el índice Kaiser-Meyer-Olkin (KMO) global y por variable de forma exacta."""
        corr_matrix = np.corrcoef(data, rowvar=False)
        inv_corr = np.linalg.pinv(corr_matrix)

        diag_inv = np.diag(inv_corr)
        denom_matrix = np.sqrt(np.outer(diag_inv, diag_inv))
        partial_corr = -inv_corr / denom_matrix

        np.fill_diagonal(corr_matrix, 0.0)
        np.fill_diagonal(partial_corr, 0.0)

        r2_sum_total = float(np.sum(corr_matrix**2))
        q2_sum_total = float(np.sum(partial_corr**2))

        kmo_global = (
            r2_sum_total / (r2_sum_total + q2_sum_total)
            if (r2_sum_total + q2_sum_total) > 0
            else 0.0
        )

        r2_per_var = np.sum(corr_matrix**2, axis=0)
        q2_per_var = np.sum(partial_corr**2, axis=0)
        msa_values = r2_per_var / (r2_per_var + q2_per_var)

        kmo_per_variable = {
            name: round(float(val), 4) for name, val in zip(feature_names, msa_values)
        }
        return round(kmo_global, 4), kmo_per_variable

    @staticmethod
    def compute_bartlett_sphericity(data: np.ndarray) -> Tuple[float, int, float]:
        """Ejecuta la Prueba de Esfericidad de Bartlett sobre la matriz de correlaciones."""
        n_samples, n_features = data.shape
        corr_matrix = np.corrcoef(data, rowvar=False)
        sign, logdet = np.linalg.slogdet(corr_matrix)

        if sign <= 0:
            logdet = -1e-12

        chi_square = -((n_samples - 1.0) - (2.0 * n_features + 5.0) / 6.0) * float(logdet)
        chi_square = max(0.0, chi_square)
        dof = int(n_features * (n_features - 1) // 2)
        p_value = float(stats.chi2.sf(chi_square, dof))
        return round(chi_square, 4), dof, p_value

    def evaluate(
        self, df_features: pd.DataFrame, raise_on_failure: bool = True
    ) -> ModelHealthReport:
        """Ejecuta la batería completa de pruebas de adecuación estadística."""
        clean_df = df_features.dropna(axis=0, how="any")
        n_samples, n_features = clean_df.shape
        feature_names = list(clean_df.columns)
        matrix = clean_df.to_numpy(dtype=np.float64)

        diagnostics: List[str] = []
        passed = True

        if n_samples < self.min_sample_size:
            passed = False
            diagnostics.append(
                f"[FALLO MUESTRAL] Tamaño muestral N={n_samples} inferior al umbral "
                f"mínimo exigido N>={self.min_sample_size}."
            )
        else:
            diagnostics.append(
                f"[OK MUESTRAL] Tamaño muestral N={n_samples} supera el umbral N>={self.min_sample_size}."
            )

        kmo_global, kmo_per_var = self.compute_kmo(matrix, feature_names)
        if kmo_global < self.min_kmo_global:
            passed = False
            diagnostics.append(
                f"[FALLO KMO] Índice KMO global ({kmo_global:.4f}) inferior al mínimo "
                f"aceptable ({self.min_kmo_global:.2f})."
            )
        else:
            diagnostics.append(
                f"[OK KMO] Índice KMO global = {kmo_global:.4f} >= {self.min_kmo_global:.2f}."
            )

        chi2, dof, p_val = self.compute_bartlett_sphericity(matrix)
        if p_val >= self.max_bartlett_pvalue or math.isnan(p_val):
            passed = False
            diagnostics.append(
                f"[FALLO BARTLETT] No se puede rechazar H0: R = I (p-valor = {p_val:.4e})."
            )
        else:
            diagnostics.append(
                f"[OK BARTLETT] Esfericidad rechazada con éxito (Chi2={chi2:.2f}, gl={dof}, p={p_val:.4e})."
            )

        corr_matrix = np.corrcoef(matrix, rowvar=False)
        eigenvalues = np.linalg.eigvalsh(corr_matrix)
        max_eig = float(np.max(np.abs(eigenvalues)))
        min_eig = float(max(np.min(np.abs(eigenvalues)), 1e-12))
        cond_number = round(math.sqrt(max_eig / min_eig), 4)

        report = ModelHealthReport(
            passed=passed,
            sample_size=n_samples,
            n_features=n_features,
            kmo_global=kmo_global,
            kmo_per_variable=kmo_per_var,
            bartlett_chi2=chi2,
            bartlett_degrees_of_freedom=dof,
            bartlett_pvalue=p_val,
            condition_number=cond_number,
            diagnostics=diagnostics,
        )

        if not passed and raise_on_failure:
            raise StatisticalHealthError(
                "El conjunto de datos fue rechazado por ModelHealthGate: "
                + " | ".join(diagnostics)
            )

        return report
