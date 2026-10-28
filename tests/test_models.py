"""Suite de pruebas unitarias e integrales para ModelHealthGate y ScoutingMultivariateEngine."""

import numpy as np
import pandas as pd
import pytest

from src.analytics.model_health import ModelHealthGate, StatisticalHealthError
from src.analytics.multivariate_engine import ScoutingMultivariateEngine
from src.ingestion.api_client import APIFootballClient
from src.ingestion.fuzzy_matcher import FuzzyEntityMatcher
from src.processing.feature_engineering import SportsFeatureEngineer


def test_model_health_gate_rejects_orthogonal_white_noise() -> None:
    """Verifica que una matriz de variables independientes (R = I) sea bloqueada por KMO/Bartlett."""
    rng = np.random.default_rng(123)
    noise_df = pd.DataFrame(
        rng.normal(0.0, 1.0, size=(350, 10)),
        columns=[f"var_{i}" for i in range(10)],
    )
    gate = ModelHealthGate(min_sample_size=300, min_kmo_global=0.70, max_bartlett_pvalue=0.05)
    with pytest.raises(StatisticalHealthError):
        gate.evaluate(noise_df, raise_on_failure=True)


def test_full_multivariate_engine_kmo_bartlett_ari_and_net_value() -> None:
    """Verifica el flujo completo Silver -> Gold (KMO >= 0.70, Varianza ACP >= 0.75, ARI >= 0.70 y KNN)."""
    sport_docs, fin_docs = APIFootballClient.generate_calibrated_cohort(
        n_players=420, random_seed=42
    )
    matcher = FuzzyEntityMatcher(similarity_threshold=0.85)
    merged_df, _ = matcher.match_records(sport_docs, fin_docs)

    engineer = SportsFeatureEngineer()
    silver_df, _ = engineer.transform_full_silver(merged_df)

    engine = ScoutingMultivariateEngine(
        min_explained_variance=0.75, k_min=3, k_max=6, min_ari=0.70, random_seed=42
    )
    gold_df, artifacts = engine.fit_transform_gold(silver_df)

    assert artifacts.health_report.passed is True
    assert artifacts.health_report.sample_size >= 300
    assert artifacts.health_report.kmo_global >= 0.70
    assert artifacts.health_report.bartlett_pvalue < 0.05
    assert artifacts.cumulative_variance >= 0.75
    assert artifacts.optimal_cluster_metrics.adjusted_rand_index >= 0.70

    diff = gold_df["z_acp_performance"] - gold_df["z_financial_cost"]
    assert np.allclose(gold_df["net_value"], diff, atol=1e-3)

    sample_id = int(gold_df.iloc[0]["player_id"])
    clones = engine.find_knn_statistical_clones(
        gold_df, target_player_id=sample_id, n_neighbors=5, same_position_only=True
    )
    assert len(clones) == 5
    assert sample_id not in clones["player_id"].values
    assert np.all(np.diff(clones["latent_distance"].to_numpy()) >= -1e-6)
