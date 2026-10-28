r"""Motor Multivariante de la Capa Gold: ACP, Clustering Híbrido, KNN y Modelo Net Value.

Integra el flujo matemático completo de apoyo a la decisión (DSS):
1. Verificación previa mediante `ModelHealthGate` (KMO >= 0.70, Bartlett p < 0.05).
2. Reducción de dimensionalidad por Análisis de Componentes Principales (Jolliffe & Cadima, 2016).
3. Descubrimiento de arquetipos tácticos confrontando K-Means (MacQueen, 1967) y el
   método jerárquico de Ward (Ward, 1963), auditados con ARI >= 0.70 (Hubert & Arabie, 1985).
4. Búsqueda de clones estadísticos mediante k-Nearest Neighbors (Cover & Hart, 1967) en
   el espacio latente ponderado.
5. Cálculo del diferencial económico $\text{Net Value} = Z_{\text{ACP\_Rendimiento}} - Z_{\text{Coste\_Financiero}}$.

Referencias Académicas:
    - Cover, T., & Hart, P. (1967). Nearest neighbor pattern classification. IEEE
      Transactions on Information Theory, 13(1), 21-27.
    - Hubert, L., & Arabie, P. (1985). Comparing partitions. Journal of Classification,
      2(1), 193-218.
    - Jolliffe, I. T., & Cadima, J. (2016). Principal component analysis: a review and
      recent developments. Philosophical Transactions of the Royal Society A, 374(2065),
      20150202.
    - MacQueen, J. (1967). Some methods for classification and analysis of multivariate
      observations. In Proc. 5th Berkeley Symposium on Math. Stat. and Prob. (pp. 281-297).
    - Ward, J. H., Jr. (1963). Hierarchical grouping to optimize an objective function.
      Journal of the American Statistical Association, 58(301), 236-244.
"""

from dataclasses import dataclass
import logging
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from sklearn.cluster import AgglomerativeClustering, KMeans
from sklearn.decomposition import PCA
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import PowerTransformer, StandardScaler

from src.analytics.cluster_validation import (
    ClusterValidationMetrics,
    ClusterValidator,
)
from src.analytics.model_health import ModelHealthGate, ModelHealthReport
from src.processing.feature_engineering import SportsFeatureEngineer

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class MultivariateModelArtifacts:
    """Artefactos matemáticos generados durante el entrenamiento del motor Gold."""

    health_report: ModelHealthReport
    n_components_retained: int
    explained_variance_ratio: List[float]
    cumulative_variance: float
    loadings_df: pd.DataFrame
    optimal_cluster_metrics: ClusterValidationMetrics
    all_k_evaluations: List[ClusterValidationMetrics]


class ScoutingMultivariateEngine:
    """Motor analítico central para extracción de factores, clustering, KNN y Net Value."""

    ARCHETYPE_LABELS: Dict[int, str] = {
        0: "Arquetipo I: Recuperador / Ancla Defensiva de Alto Volumen",
        1: "Arquetipo II: Organizador Progresivo / Creador Asociativo",
        2: "Arquetipo III: Creador y Extremo de Desequilibrio",
        3: "Arquetipo IV: Finalizador y Referencia de Área",
        4: "Arquetipo V: Especialista de Área y Duelo Aéreo",
        5: "Arquetipo VI: Conector de Posesión de Bajo Riesgo",
        6: "Arquetipo VII: Extremo Profundo de Conducción",
        7: "Arquetipo VIII: Perfil Mixto de Rotación",
    }

    def __init__(
        self,
        min_explained_variance: float = 0.75,
        k_min: int = 3,
        k_max: int = 8,
        min_ari: float = 0.70,
        market_value_weight: float = 0.60,
        annual_salary_weight: float = 0.40,
        random_seed: int = 42,
    ) -> None:
        """Inicializa el motor multivariante parametrizado."""
        self.min_explained_variance = min_explained_variance
        self.k_min = k_min
        self.k_max = k_max
        self.market_value_weight = market_value_weight
        self.annual_salary_weight = annual_salary_weight
        self.random_seed = random_seed

        self.health_gate = ModelHealthGate(
            min_sample_size=300, min_kmo_global=0.70, max_bartlett_pvalue=0.05
        )
        self.cluster_validator = ClusterValidator(min_adjusted_rand_index=min_ari)
        self._pca: Optional[PCA] = None
        self._retained_d: int = 3

    @staticmethod
    def _classify_quadrant(z_perf: float, z_cost: float) -> str:
        """Clasifica un jugador en uno de los 4 cuadrantes estratégicos de Net Value."""
        if z_perf >= 0.0 and z_cost < 0.0:
            return "Cuadrante I: Oportunidad de Mercado (Alto Rendimiento / Bajo Coste)"
        if z_perf >= 0.0 and z_cost >= 0.0:
            return "Cuadrante II: Élite Consolidada (Alto Rendimiento / Alto Coste)"
        if z_perf < 0.0 and z_cost >= 0.0:
            return "Cuadrante III: Sobrevalorado / Riesgo Financiero (Bajo Rendimiento / Alto Coste)"
        return "Cuadrante IV: Rotación / Desarrollo (Bajo Rendimiento / Bajo Coste)"

    def fit_transform_gold(
        self, df_silver: pd.DataFrame
    ) -> Tuple[pd.DataFrame, MultivariateModelArtifacts]:
        """Ejecuta el pipeline matemático completo de la Capa Gold sobre el DataFrame Silver."""
        out_df = df_silver.copy().reset_index(drop=True)
        base_features = SportsFeatureEngineer.get_model_feature_columns()
        yj_cols = [f"yj_{col}" for col in base_features]

        health_report = self.health_gate.evaluate(out_df[yj_cols], raise_on_failure=True)
        X_matrix = out_df[yj_cols].to_numpy(dtype=np.float64)

        full_pca = PCA(svd_solver="full", random_state=self.random_seed)
        full_pca.fit(X_matrix)
        cum_var = np.cumsum(full_pca.explained_variance_ratio_)
        kaiser_count = int(np.sum(full_pca.explained_variance_ >= 0.85))
        var_count = int(np.searchsorted(cum_var, self.min_explained_variance) + 1)
        n_retained = max(3, kaiser_count, var_count)
        n_retained = min(n_retained, len(yj_cols))
        self._retained_d = n_retained

        self._pca = PCA(
            n_components=n_retained, svd_solver="full", random_state=self.random_seed
        )
        latent_scores = self._pca.fit_transform(X_matrix)

        for k_idx in range(n_retained):
            if np.sum(self._pca.components_[k_idx]) < 0:
                self._pca.components_[k_idx] *= -1.0
                latent_scores[:, k_idx] *= -1.0

        pc_names = [f"PC{k + 1}" for k in range(n_retained)]
        for k_idx, pc_col in enumerate(pc_names):
            out_df[pc_col] = np.round(latent_scores[:, k_idx], 5)

        loadings_df = pd.DataFrame(
            self._pca.components_.T,
            index=base_features,
            columns=pc_names,
        ).round(4)

        evaluations: List[ClusterValidationMetrics] = []
        partitions_cache: Dict[int, Tuple[np.ndarray, np.ndarray]] = {}

        for k_val in range(self.k_min, self.k_max + 1):
            kmeans = KMeans(
                n_clusters=k_val,
                n_init=50,
                max_iter=500,
                random_state=self.random_seed,
            )
            labels_km = kmeans.fit_predict(latent_scores)

            ward = AgglomerativeClustering(
                n_clusters=k_val, metric="euclidean", linkage="ward"
            )
            labels_wd = ward.fit_predict(latent_scores)

            metrics_k = self.cluster_validator.evaluate_partition_pair(
                latent_coords=latent_scores,
                labels_kmeans=labels_km,
                labels_ward=labels_wd,
                k_clusters=k_val,
            )
            evaluations.append(metrics_k)
            partitions_cache[k_val] = (labels_km, labels_wd)

        optimal_metrics = self.cluster_validator.select_optimal_k(evaluations)
        best_k = optimal_metrics.k_clusters
        best_km_labels, best_ward_labels = partitions_cache[best_k]

        # Asignación semántica determinista de los clústeres según el perfil real de sus centroides
        unique_cids = sorted(list(set(int(x) for x in best_km_labels)))
        remaining_cids = set(unique_cids)
        semantic_map: Dict[int, int] = {}

        def _pick_best_cid(cols_check: List[str]) -> int:
            best_c = -1
            best_val = -1e9
            for c_candidate in sorted(remaining_cids):
                mask_c = best_km_labels == c_candidate
                score_c = float(out_df.loc[mask_c, cols_check].mean().mean())
                if score_c > best_val:
                    best_val = score_c
                    best_c = c_candidate
            remaining_cids.remove(best_c)
            return best_c

        if len(unique_cids) >= 4:
            c_def = _pick_best_cid(["yj_tackles_p90_adj", "yj_interceptions_p90_adj", "yj_blocks_p90_adj"])
            c_fin = _pick_best_cid(["yj_goals_per90", "yj_expected_goals_xg_per90", "yj_shots_on_target_per90"])
            c_org = _pick_best_cid(["yj_progressive_passes_per90", "yj_recoveries_p90_adj"])
            c_cre = _pick_best_cid(["yj_successful_dribbles_per90", "yj_progressive_carries_per90", "yj_expected_assists_xa_per90"])
            semantic_map[c_def] = 0
            semantic_map[c_org] = 1
            semantic_map[c_cre] = 2
            semantic_map[c_fin] = 3
            next_idx = 4
            for rem_c in sorted(remaining_cids):
                semantic_map[rem_c] = next_idx
                next_idx += 1
        else:
            for i_c, c_id in enumerate(unique_cids):
                semantic_map[c_id] = i_c

        canonical_km = np.array([semantic_map[int(c)] for c in best_km_labels], dtype=int)

        # Alineamos los IDs de Ward con los IDs semánticos de K-Means por voto mayoritario
        ward_map: Dict[int, int] = {}
        for w_cid in sorted(set(int(x) for x in best_ward_labels)):
            mask_w = best_ward_labels == w_cid
            if np.any(mask_w):
                vals, counts = np.unique(canonical_km[mask_w], return_counts=True)
                ward_map[w_cid] = int(vals[int(np.argmax(counts))])
            else:
                ward_map[w_cid] = w_cid
        canonical_ward = np.array([ward_map[int(w)] for w in best_ward_labels], dtype=int)

        out_df["cluster_kmeans_id"] = canonical_km
        out_df["cluster_ward_id"] = canonical_ward
        out_df["tactical_archetype"] = [
            self.ARCHETYPE_LABELS.get(int(cid), f"Arquetipo Táctico #{cid + 1}")
            for cid in canonical_km
        ]

        # Cálculo de Z_ACP_Rendimiento ponderado por comunalidades factoriales y
        # estandarizado dentro de cada Arquetipo Táctico para evaluar equitativamente cada rol
        communalities = np.sum(self._pca.components_ ** 2, axis=0)
        comm_weights = communalities / np.sum(communalities)
        raw_role_perf = np.dot(X_matrix, comm_weights)
        out_df["_raw_perf"] = raw_role_perf
        z_acp_perf = np.zeros(len(out_df), dtype=np.float64)
        for arch_id, grp_idx in out_df.groupby("cluster_kmeans_id").groups.items():
            vals_arch = out_df.loc[grp_idx, "_raw_perf"].to_numpy(dtype=np.float64).reshape(-1, 1)
            if len(vals_arch) > 1 and float(np.std(vals_arch)) > 1e-8:
                z_acp_perf[grp_idx] = StandardScaler().fit_transform(vals_arch).ravel()
            else:
                z_acp_perf[grp_idx] = 0.0
        out_df = out_df.drop(columns=["_raw_perf"])
        out_df["z_acp_performance"] = np.round(z_acp_perf, 4)

        fin_transformer = PowerTransformer(method="yeo-johnson", standardize=True)
        fin_matrix = out_df[["market_value_eur", "annual_gross_salary_eur"]].to_numpy(
            dtype=np.float64
        )
        fin_yj = fin_transformer.fit_transform(fin_matrix)
        z_market_val = fin_yj[:, 0]
        z_annual_sal = fin_yj[:, 1]

        weighted_cost = (
            self.market_value_weight * z_market_val
            + self.annual_salary_weight * z_annual_sal
        )
        z_fin_cost = StandardScaler().fit_transform(weighted_cost.reshape(-1, 1)).ravel()

        out_df["z_market_value"] = np.round(z_market_val, 4)
        out_df["z_annual_salary"] = np.round(z_annual_sal, 4)
        out_df["z_financial_cost"] = np.round(z_fin_cost, 4)
        out_df["net_value"] = np.round(
            out_df["z_acp_performance"] - out_df["z_financial_cost"], 4
        )
        out_df["strategic_quadrant"] = [
            self._classify_quadrant(zp, zc)
            for zp, zc in zip(out_df["z_acp_performance"], out_df["z_financial_cost"])
        ]

        artifacts = MultivariateModelArtifacts(
            health_report=health_report,
            n_components_retained=n_retained,
            explained_variance_ratio=[
                round(float(v), 4) for v in self._pca.explained_variance_ratio_
            ],
            cumulative_variance=round(
                float(np.sum(self._pca.explained_variance_ratio_)), 4
            ),
            loadings_df=loadings_df,
            optimal_cluster_metrics=optimal_metrics,
            all_k_evaluations=evaluations,
        )
        return out_df, artifacts

    def find_knn_statistical_clones(
        self,
        df_gold: pd.DataFrame,
        target_player_id: int,
        n_neighbors: int = 10,
        same_position_only: bool = True,
        max_market_value_eur: Optional[float] = None,
    ) -> pd.DataFrame:
        """Encuentra los $k$ clones estadísticos más cercanos en el subespacio latente del ACP."""
        target_rows = df_gold[df_gold["player_id"] == target_player_id]
        if target_rows.empty:
            raise ValueError(f"Jugador objetivo player_id={target_player_id} no encontrado.")

        target_row = target_rows.iloc[0]
        pc_cols = [c for c in df_gold.columns if c.startswith("PC") and c[2:].isdigit()]

        candidate_df = df_gold.copy()
        if same_position_only:
            candidate_df = candidate_df[
                candidate_df["position_group"] == target_row["position_group"]
            ].copy()

        if max_market_value_eur is not None:
            candidate_df = candidate_df[
                (candidate_df["market_value_eur"] <= max_market_value_eur)
                | (candidate_df["player_id"] == target_player_id)
            ].copy()

        candidate_df = candidate_df.reset_index(drop=True)
        coords = candidate_df[pc_cols].to_numpy(dtype=np.float64)
        target_vec = target_row[pc_cols].to_numpy(dtype=np.float64).reshape(1, -1)

        k_eff = min(len(candidate_df), n_neighbors + 1)
        nn_model = NearestNeighbors(n_neighbors=k_eff, metric="euclidean")
        nn_model.fit(coords)
        distances, indices = nn_model.kneighbors(target_vec)

        clones_df = candidate_df.iloc[indices[0]].copy()
        clones_df["latent_distance"] = np.round(distances[0], 4)
        clones_df["similarity_pct"] = np.round(100.0 * np.exp(-0.35 * distances[0]), 2)

        target_mv = float(target_row["market_value_eur"])
        target_sal = float(target_row["annual_gross_salary_eur"])
        clones_df["market_value_savings_eur"] = np.round(
            target_mv - clones_df["market_value_eur"], 0
        )
        clones_df["salary_savings_eur"] = np.round(
            target_sal - clones_df["annual_gross_salary_eur"], 0
        )

        clones_df = clones_df[clones_df["player_id"] != target_player_id].head(n_neighbors)
        return clones_df.reset_index(drop=True)
