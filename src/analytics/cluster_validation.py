r"""Módulo de validación geométrica interna y concordancia externa de clústeres.

Evalúa simultáneamente:
1. Coeficiente de Silueta (Rousseeuw, 1987) $\in [-1, 1]$ (Maximizar).
2. Índice de Caliński-Harabasz o Variance Ratio Criterion (Caliński & Harabasz, 1974) (Maximizar).
3. Índice de Davies-Bouldin (Davies & Bouldin, 1979) (Minimizar).
4. Concordancia topológica entre K-Means y Método Jerárquico de Ward mediante el
   Índice de Rand Ajustado por el azar (Adjusted Rand Index, ARI >= 0.70; Hubert & Arabie, 1985).

Referencias Académicas:
    - Caliński, T., & Harabasz, J. (1974). A dendrite method for cluster analysis.
      Communications in Statistics, 3(1), 1-27.
    - Davies, D. L., & Bouldin, D. W. (1979). A cluster separation measure. IEEE
      Transactions on Pattern Analysis and Machine Intelligence, PAMI-1(2), 224-227.
    - Hubert, L., & Arabie, P. (1985). Comparing partitions. Journal of Classification,
      2(1), 193-218.
    - Rousseeuw, P. J. (1987). Silhouettes: A graphical aid to the interpretation and
      validation of cluster analysis. Journal of Computational and Applied Mathematics,
      20, 53-65.
"""

from dataclasses import dataclass
import logging
from typing import Dict, List

import numpy as np
from sklearn.metrics import (
    adjusted_rand_score,
    calinski_harabasz_score,
    davies_bouldin_score,
    silhouette_score,
)

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ClusterValidationMetrics:
    """Métricas de calidad para un número candidato de clústeres $K$."""

    k_clusters: int
    silhouette_kmeans: float
    calinski_harabasz_kmeans: float
    davies_bouldin_kmeans: float
    silhouette_ward: float
    adjusted_rand_index: float
    meets_ari_threshold: bool

    def to_dict(self) -> Dict[str, float | int | bool]:
        """Convierte las métricas en diccionario serializable para tablas de la memoria."""
        return {
            "k_clusters": self.k_clusters,
            "silhouette_kmeans": round(self.silhouette_kmeans, 4),
            "calinski_harabasz_kmeans": round(self.calinski_harabasz_kmeans, 2),
            "davies_bouldin_kmeans": round(self.davies_bouldin_kmeans, 4),
            "silhouette_ward": round(self.silhouette_ward, 4),
            "adjusted_rand_index": round(self.adjusted_rand_index, 4),
            "meets_ari_threshold": self.meets_ari_threshold,
        }


class ClusterValidator:
    """Auditor de estabilidad y validez geométrica de particiones no supervisadas."""

    def __init__(
        self,
        min_adjusted_rand_index: float = 0.70,
        min_silhouette_score: float = 0.25,
    ) -> None:
        """Inicializa los umbrales de aceptación científica de clústeres."""
        self.min_adjusted_rand_index = min_adjusted_rand_index
        self.min_silhouette_score = min_silhouette_score

    def evaluate_partition_pair(
        self,
        latent_coords: np.ndarray,
        labels_kmeans: np.ndarray,
        labels_ward: np.ndarray,
        k_clusters: int,
    ) -> ClusterValidationMetrics:
        """Calcula las cuatro métricas de validación sobre el espacio latente del ACP."""
        sil_km = float(silhouette_score(latent_coords, labels_kmeans, metric="euclidean"))
        ch_km = float(calinski_harabasz_score(latent_coords, labels_kmeans))
        db_km = float(davies_bouldin_score(latent_coords, labels_kmeans))
        sil_ward = float(silhouette_score(latent_coords, labels_ward, metric="euclidean"))
        ari = float(adjusted_rand_score(labels_kmeans, labels_ward))

        meets_ari = ari >= self.min_adjusted_rand_index

        return ClusterValidationMetrics(
            k_clusters=k_clusters,
            silhouette_kmeans=sil_km,
            calinski_harabasz_kmeans=ch_km,
            davies_bouldin_kmeans=db_km,
            silhouette_ward=sil_ward,
            adjusted_rand_index=ari,
            meets_ari_threshold=meets_ari,
        )

    def select_optimal_k(
        self, candidates: List[ClusterValidationMetrics]
    ) -> ClusterValidationMetrics:
        """Selecciona el valor óptimo $K^*$ priorizando concordancia ARI >= 0.70 y máxima Silueta."""
        if not candidates:
            raise ValueError("La lista de candidatos de clustering no puede estar vacía.")

        valid_ari_candidates = [c for c in candidates if c.meets_ari_threshold]
        pool = valid_ari_candidates if valid_ari_candidates else candidates

        best_candidate = max(
            pool,
            key=lambda c: (
                0.50 * c.silhouette_kmeans
                + 0.35 * c.adjusted_rand_index
                - 0.15 * c.davies_bouldin_kmeans
            ),
        )
        return best_candidate
