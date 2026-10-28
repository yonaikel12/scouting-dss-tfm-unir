r"""Módulo de Ingeniería de Variables Deportivas y Normalización Multivariante (Capa Silver).

Implementa las transformaciones matemáticas exigidas para eliminar sesgos de exposición
temporal, sesgos tácticos del club de origen y asimetrías distribucionales antes del
Análisis de Componentes Principales (ACP):
1. Tasas por 90 minutos reglamentarios ($M_{\text{per90}}$).
2. Métricas defensivas ajustadas al 50% de posesión ($M_{\text{p90\_adj}}$; Pappalardo et al., 2019).
3. Transformación paramétrica de potencia de Yeo-Johnson por Máxima Verosimilitud
   ($\psi(\lambda, y)$; Yeo & Johnson, 2000) con estandarización Z-Score.
4. Cálculo de percentiles condicionados por demarcación táctica ($P_{1-99}$) para
   visualización polar en Pizza Charts.

Referencias Académicas:
    - Decroos, T., Bransen, L., Van Haaren, J., & Davis, J. (2019). Actions speak louder
      than goals: Valuing player actions in soccer. In Proceedings of ACM SIGKDD (pp. 1851-1861).
    - Pappalardo, L., Cintia, P., Ferragina, P., Massucco, E., Pedreschi, D., &
      Giannotti, F. (2019). PlayeRank: Data-driven performance evaluation and player
      ranking in soccer via a machine learning approach. ACM TIST, 10(5), 1-27.
    - Yeo, I.-K., & Johnson, R. A. (2000). A new family of power transformations to
      improve normality or symmetry. Biometrika, 87(4), 954-959.
"""

from dataclasses import dataclass
import logging
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
from sklearn.preprocessing import PowerTransformer

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class FeatureTransformationMetadata:
    """Metadatos auditables de la transformación de potencia de Yeo-Johnson."""

    feature_names: List[str]
    lambdas_mle: Dict[str, float]
    skewness_before: Dict[str, float]
    skewness_after: Dict[str, float]


class SportsFeatureEngineer:
    """Motor de transformaciones deportivas y normalización estadística (Capa Silver)."""

    RAW_OFFENSIVE_PROGRESSION_METRICS: List[str] = [
        "goals",
        "assists",
        "expected_goals_xg",
        "expected_assists_xa",
        "key_passes",
        "progressive_passes",
        "progressive_carries",
        "successful_dribbles",
        "shots_on_target",
        "aerial_duels_won",
    ]

    RAW_DEFENSIVE_POSSESSION_METRICS: List[str] = [
        "tackles",
        "interceptions",
        "duels_won",
        "blocks",
        "recoveries",
    ]

    def __init__(
        self,
        standard_match_minutes: float = 90.0,
        neutral_possession_pct: float = 50.0,
        min_possession_bound: float = 30.0,
        max_possession_bound: float = 75.0,
    ) -> None:
        """Inicializa los hiperparámetros físicos y tácticos de normalización."""
        self.standard_match_minutes = standard_match_minutes
        self.neutral_possession_pct = neutral_possession_pct
        self.min_possession_bound = min_possession_bound
        self.max_possession_bound = max_possession_bound
        self._power_transformer: PowerTransformer = PowerTransformer(
            method="yeo-johnson", standardize=True
        )

    def compute_per90_and_possession_adjusted(self, df: pd.DataFrame) -> pd.DataFrame:
        r"""Calcula todas las tasas $M_{\text{per90}}$ y ajusta las defensivas por posesión $M_{\text{p90\_adj}}$."""
        out_df = df.copy()
        minutes = np.maximum(out_df["minutes_played"].to_numpy(dtype=np.float64), 1.0)
        factor_90 = self.standard_match_minutes / minutes

        for col in self.RAW_OFFENSIVE_PROGRESSION_METRICS:
            per90_col = f"{col}_per90"
            out_df[per90_col] = np.round(
                out_df[col].to_numpy(dtype=np.float64) * factor_90, 4
            )

        clipped_poss = np.clip(
            out_df["team_possession_pct"].to_numpy(dtype=np.float64),
            self.min_possession_bound,
            self.max_possession_bound,
        )
        possession_factor = self.neutral_possession_pct / clipped_poss

        for col in self.RAW_DEFENSIVE_POSSESSION_METRICS:
            per90_col = f"{col}_per90"
            adj_col = f"{col}_p90_adj"
            per90_vals = out_df[col].to_numpy(dtype=np.float64) * factor_90
            out_df[per90_col] = np.round(per90_vals, 4)
            out_df[adj_col] = np.round(per90_vals * possession_factor, 4)

        return out_df

    @classmethod
    def get_model_feature_columns(cls) -> List[str]:
        """Devuelve la lista canónica de 15 variables que alimentan el motor ACP."""
        offensive_cols = [f"{c}_per90" for c in cls.RAW_OFFENSIVE_PROGRESSION_METRICS]
        defensive_adj_cols = [f"{c}_p90_adj" for c in cls.RAW_DEFENSIVE_POSSESSION_METRICS]
        return offensive_cols + defensive_adj_cols

    def apply_yeo_johnson(
        self, df: pd.DataFrame
    ) -> Tuple[pd.DataFrame, FeatureTransformationMetadata]:
        """Aplica la transformación de potencia de Yeo-Johnson y estandarización Z-Score."""
        out_df = df.copy()
        feature_cols = self.get_model_feature_columns()

        raw_matrix = out_df[feature_cols].to_numpy(dtype=np.float64)
        skew_before = {
            col: round(float(pd.Series(out_df[col]).skew()), 4) for col in feature_cols
        }

        transformed_matrix = self._power_transformer.fit_transform(raw_matrix)
        lambdas = {
            col: round(float(lmb), 4)
            for col, lmb in zip(feature_cols, self._power_transformer.lambdas_)
        }

        skew_after: Dict[str, float] = {}
        for idx, col in enumerate(feature_cols):
            yj_col = f"yj_{col}"
            out_df[yj_col] = np.round(transformed_matrix[:, idx], 6)
            skew_after[col] = round(float(pd.Series(out_df[yj_col]).skew()), 4)

        metadata = FeatureTransformationMetadata(
            feature_names=feature_cols,
            lambdas_mle=lambdas,
            skewness_before=skew_before,
            skewness_after=skew_after,
        )
        return out_df, metadata

    def compute_position_percentiles(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calcula los rangos percentilares [1, 99] condicionados por demarcación (`position_group`)."""
        out_df = df.copy()
        feature_cols = self.get_model_feature_columns()

        for col in feature_cols:
            pct_col = f"pct_{col}"
            out_df[pct_col] = (
                out_df.groupby("position_group")[col]
                .rank(pct=True, method="average")
                .mul(98.0)
                .add(1.0)
                .round(1)
            )

        return out_df

    def transform_full_silver(
        self, df: pd.DataFrame
    ) -> Tuple[pd.DataFrame, FeatureTransformationMetadata]:
        """Ejecuta la secuencia completa de ingeniería de variables de la Capa Silver."""
        df_rates = self.compute_per90_and_possession_adjusted(df)
        df_yj, metadata = self.apply_yeo_johnson(df_rates)
        df_silver = self.compute_position_percentiles(df_yj)
        return df_silver, metadata
