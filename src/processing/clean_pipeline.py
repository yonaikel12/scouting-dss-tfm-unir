"""Tubería ETL de limpieza y materialización columnar en Apache Parquet y DuckDB.

Orquesta de forma transaccional y auditable el flujo Bronze -> Silver:
1. Resolución de entidades (API-Football + Capology/Transfermarkt) vía `FuzzyEntityMatcher`.
2. Verificación formal del Contrato de Datos mediante `IngestionGate`.
3. Transformación de variables ($M_{\text{per90}}$, $M_{\text{p90\_adj}}$, Yeo-Johnson y percentiles).
4. Escritura columnar en Apache Parquet y registro de tabla analítica OLAP en DuckDB.

Referencias Académicas:
    - Armbrust, M., Ghodsi, A., Xin, R., & Zaharia, M. (2021). Lakehouse: A new
      generation of open platforms that unify data warehousing and advanced analytics.
      In Proceedings of CIDR 2021.
    - Raasveldt, M., & Mühleisen, H. (2019). DuckDB: an Embeddable Analytical Database.
      In Proceedings of the 2019 International Conference on Management of Data (SIGMOD)
      (pp. 1981-1984). ACM.
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import duckdb
import pandas as pd

from src.ingestion.fuzzy_matcher import FuzzyEntityMatcher
from src.processing.feature_engineering import (
    FeatureTransformationMetadata,
    SportsFeatureEngineer,
)
from src.processing.ingestion_gate import IngestionAuditReport, IngestionGate

logger = logging.getLogger(__name__)


class SilverETLPipeline:
    """Orquestador de la capa Silver con persistencia en Parquet y DuckDB OLAP."""

    def __init__(
        self,
        schema_path: Path,
        silver_parquet_path: Path = Path("data/interim/players_silver.parquet"),
        duckdb_path: Path = Path("data/processed/scouting_gold.duckdb"),
        settings_path: Optional[Path] = None,
    ) -> None:
        """Inicializa los componentes de enlace, auditoría e ingeniería de variables."""
        self.matcher = FuzzyEntityMatcher(similarity_threshold=0.85)
        self.ingestion_gate = IngestionGate(
            schema_path=schema_path, settings_path=settings_path
        )
        self.feature_engineer = SportsFeatureEngineer()
        self.silver_parquet_path = silver_parquet_path
        self.duckdb_path = duckdb_path

        self.silver_parquet_path.parent.mkdir(parents=True, exist_ok=True)
        self.duckdb_path.parent.mkdir(parents=True, exist_ok=True)

    def run_bronze_to_silver(
        self,
        sport_records: List[Dict[str, Any]],
        financial_records: List[Dict[str, Any]],
    ) -> Tuple[pd.DataFrame, IngestionAuditReport, FeatureTransformationMetadata]:
        """Ejecuta el pipeline completo desde registros Bronze hasta la tabla Silver validada."""
        merged_df, _ = self.matcher.match_records(sport_records, financial_records)
        valid_df, audit_report = self.ingestion_gate.validate_dataframe(
            merged_df, raise_on_block=True
        )
        silver_df, feat_metadata = self.feature_engineer.transform_full_silver(valid_df)

        silver_df.to_parquet(self.silver_parquet_path, index=False, engine="pyarrow")
        self._register_in_duckdb(silver_df, table_name="silver_players")
        return silver_df, audit_report, feat_metadata

    def _register_in_duckdb(self, df: pd.DataFrame, table_name: str) -> None:
        """Materializa un DataFrame de Pandas como tabla columnar en DuckDB."""
        with duckdb.connect(str(self.duckdb_path)) as conn:
            conn.register("tmp_df_view", df)
            conn.execute(f"CREATE OR REPLACE TABLE {table_name} AS SELECT * FROM tmp_df_view")
            conn.unregister("tmp_df_view")
