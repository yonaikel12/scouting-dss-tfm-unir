"""Suite de pruebas unitarias para Ingeniería de Variables (Silver) e IngestionGate."""

import json
from pathlib import Path
from tempfile import TemporaryDirectory

import numpy as np
import pandas as pd
import pytest

from src.ingestion.api_client import APIFootballClient
from src.ingestion.fuzzy_matcher import FuzzyEntityMatcher
from src.processing.feature_engineering import SportsFeatureEngineer
from src.processing.ingestion_gate import (
    DataContractViolationError,
    GateStatus,
    IngestionGate,
)


def test_possession_adjustment_formula_exactness() -> None:
    """Comprueba que un jugador con 62.5% de posesión escale exactamente por 50/P."""
    engineer = SportsFeatureEngineer()
    df_input = pd.DataFrame(
        [
            {
                "player_id": 1,
                "position_group": "DF",
                "minutes_played": 900.0,
                "team_possession_pct": 62.5,
                "goals": 1.0,
                "assists": 1.0,
                "expected_goals_xg": 0.9,
                "expected_assists_xa": 0.8,
                "key_passes": 5.0,
                "progressive_passes": 40.0,
                "progressive_carries": 20.0,
                "successful_dribbles": 5.0,
                "shots_on_target": 3.0,
                "aerial_duels_won": 25.0,
                "tackles": 20.0,
                "interceptions": 15.0,
                "duels_won": 50.0,
                "blocks": 10.0,
                "recoveries": 60.0,
            }
        ]
    )
    df_out = engineer.compute_per90_and_possession_adjusted(df_input)
    assert np.isclose(df_out.loc[0, "tackles_per90"], 2.0)
    assert np.isclose(df_out.loc[0, "tackles_p90_adj"], 1.6)


def test_yeo_johnson_standardization_and_skewness_reduction() -> None:
    """Comprueba que la transformación de Yeo-Johnson centre las variables en media 0 y varianza 1."""
    sport_docs, fin_docs = APIFootballClient.generate_calibrated_cohort(
        n_players=320, random_seed=42
    )
    matcher = FuzzyEntityMatcher(similarity_threshold=0.85)
    merged_df, _ = matcher.match_records(sport_docs, fin_docs)

    engineer = SportsFeatureEngineer()
    silver_df, metadata = engineer.transform_full_silver(merged_df)

    for col in engineer.get_model_feature_columns():
        yj_col = f"yj_{col}"
        assert yj_col in silver_df.columns
        assert np.isclose(silver_df[yj_col].mean(), 0.0, atol=1e-5)
        assert np.isclose(silver_df[yj_col].std(ddof=0), 1.0, atol=1e-5)
        assert col in metadata.lambdas_mle


def test_ingestion_gate_allow_and_blocked_states() -> None:
    """Verifica que `IngestionGate` autorice cohortes limpias (ALLOW) y bloquee lotes corruptos (BLOCKED)."""
    sport_docs, fin_docs = APIFootballClient.generate_calibrated_cohort(
        n_players=340, random_seed=42
    )
    matcher = FuzzyEntityMatcher(similarity_threshold=0.85)
    merged_df, _ = matcher.match_records(sport_docs, fin_docs)

    minimal_schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "object",
        "required": ["player_id", "player_name", "minutes_played", "market_value_eur"],
        "properties": {
            "player_id": {"type": "integer", "minimum": 1},
            "player_name": {"type": "string", "minLength": 2},
            "minutes_played": {"type": "number", "minimum": 0},
            "market_value_eur": {"type": "number", "exclusiveMinimum": 0},
        },
    }

    with TemporaryDirectory() as tmp_dir:
        schema_path = Path(tmp_dir) / "schema.json"
        schema_path.write_text(json.dumps(minimal_schema), encoding="utf-8")

        gate = IngestionGate(
            schema_path=schema_path,
            minimum_valid_records=300,
            minimum_minutes_played=450.0,
        )
        valid_df, report = gate.validate_dataframe(merged_df, raise_on_block=True)
        assert report.status == GateStatus.ALLOW
        assert len(valid_df) >= 300

        corrupted_df = merged_df.copy()
        corrupted_df.loc[:120, "market_value_eur"] = -5000.0
        with pytest.raises(DataContractViolationError):
            gate.validate_dataframe(corrupted_df, raise_on_block=True)
