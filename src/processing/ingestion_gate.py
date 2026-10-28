"""Módulo de validación de Contratos de Datos (IngestionGate) para la transición Bronze -> Silver.

Implementa un mecanismo de control de calidad determinista basado en esquemas formales
(JSON Schema Draft 2020-12) y reglas de dominio deportivo-financiero. Previene el
fenómeno de 'deuda técnica oculta' y cascadas de corrupción de datos en sistemas ML
(Sculley et al., 2015; Schelter et al., 2018).

Referencias Académicas:
    - Sculley, D., Holt, G., Golovin, D., Davydov, E., Phillips, T., Ebner, D., ... &
      Young, M. (2015). Hidden technical debt in machine learning systems. In Advances
      in Neural Information Processing Systems (NeurIPS), 28, 2503-2511.
    - Schelter, S., Lange, D., Schmidt, P., Celikel, M., Biessmann, F., & Grafberger, A.
      (2018). Automating large-scale data quality verification. Proceedings of the VLDB
      Endowment, 11(12), 1781-1794.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import jsonschema
import pandas as pd
import yaml

logger = logging.getLogger(__name__)


class GateStatus(str, Enum):
    """Estados operativos posibles de la puerta de control de ingesta."""

    ALLOW = "ALLOW"
    DEGRADED = "DEGRADED"
    BLOCKED = "BLOCKED"


class DataContractViolationError(RuntimeError):
    """Excepción crítica lanzada cuando el lote de datos infringe el umbral BLOCKED."""


@dataclass(frozen=True)
class IngestionAuditReport:
    """Informe inmutable de auditoría emitido por el IngestionGate."""

    status: GateStatus
    timestamp_utc: str
    total_records: int
    valid_records: int
    rejected_records: int
    error_rate: float
    violation_breakdown: Dict[str, int] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Serializa el informe de auditoría a diccionario compatible con JSON/MongoDB."""
        return {
            "status": self.status.value,
            "timestamp_utc": self.timestamp_utc,
            "total_records": self.total_records,
            "valid_records": self.valid_records,
            "rejected_records": self.rejected_records,
            "error_rate": round(self.error_rate, 4),
            "violation_breakdown": self.violation_breakdown,
            "warnings": self.warnings,
        }


class IngestionGate:
    """Puerta de verificación de Contratos de Datos entre la capa Bronze y Silver."""

    def __init__(
        self,
        schema_path: Path,
        settings_path: Optional[Path] = None,
        block_error_rate: float = 0.15,
        degraded_warning_rate: float = 0.05,
        minimum_valid_records: int = 300,
        minimum_minutes_played: float = 450.0,
    ) -> None:
        """Inicializa la puerta de calidad cargando el JSON Schema y los umbrales."""
        if not schema_path.exists():
            raise FileNotFoundError(f"No se encontró el esquema de contrato en: {schema_path}")

        with schema_path.open("r", encoding="utf-8") as f_schema:
            self._schema: Dict[str, Any] = json.load(f_schema)

        self._validator = jsonschema.Draft202012Validator(self._schema)

        self.block_error_rate = block_error_rate
        self.degraded_warning_rate = degraded_warning_rate
        self.minimum_valid_records = minimum_valid_records
        self.minimum_minutes_played = minimum_minutes_played

        if settings_path is not None and settings_path.exists():
            with settings_path.open("r", encoding="utf-8") as f_cfg:
                cfg = yaml.safe_load(f_cfg)
                dc_cfg = cfg.get("data_contract", {})
                thresholds = dc_cfg.get("thresholds", {})
                self.block_error_rate = float(
                    thresholds.get("block_error_rate", self.block_error_rate)
                )
                self.degraded_warning_rate = float(
                    thresholds.get("degraded_warning_rate", self.degraded_warning_rate)
                )
                self.minimum_valid_records = int(
                    thresholds.get("minimum_valid_records", self.minimum_valid_records)
                )
                self.minimum_minutes_played = float(
                    dc_cfg.get("minimum_minutes_played", self.minimum_minutes_played)
                )

    def validate_dataframe(
        self, df: pd.DataFrame, raise_on_block: bool = True
    ) -> Tuple[pd.DataFrame, IngestionAuditReport]:
        """Valida un DataFrame de entrada frente al Contrato de Datos."""
        timestamp_utc = datetime.now(timezone.utc).isoformat()
        total_records = len(df)

        if total_records == 0:
            report = IngestionAuditReport(
                status=GateStatus.BLOCKED,
                timestamp_utc=timestamp_utc,
                total_records=0,
                valid_records=0,
                rejected_records=0,
                error_rate=1.0,
                violation_breakdown={"empty_dataset": 1},
                warnings=["El lote recibido desde la capa Bronze está vacío."],
            )
            if raise_on_block:
                raise DataContractViolationError("Lote bloqueado: DataFrame de entrada vacío.")
            return df.copy(), report

        valid_indices: List[Any] = []
        violation_breakdown: Dict[str, int] = {}
        warnings: List[str] = []

        records = df.to_dict(orient="records")
        for idx, record in zip(df.index, records):
            clean_record = {
                k: (None if pd.isna(v) else v) for k, v in record.items()
            }
            errors = list(self._validator.iter_errors(clean_record))
            if errors:
                for err in errors:
                    field_path = ".".join(str(p) for p in err.path) or err.validator
                    key = f"schema:{field_path}"
                    violation_breakdown[key] = violation_breakdown.get(key, 0) + 1
                continue

            minutes = float(clean_record.get("minutes_played", 0.0))
            if minutes < self.minimum_minutes_played:
                key = f"domain:minutes_below_{int(self.minimum_minutes_played)}"
                violation_breakdown[key] = violation_breakdown.get(key, 0) + 1
                continue

            valid_indices.append(idx)

        valid_df = df.loc[valid_indices].copy()
        valid_count = len(valid_df)
        rejected_count = total_records - valid_count

        schema_errors = sum(
            count for k, count in violation_breakdown.items() if k.startswith("schema:")
        )
        structural_error_rate = schema_errors / total_records

        if structural_error_rate >= self.block_error_rate:
            status = GateStatus.BLOCKED
            warnings.append(
                f"Tasa de error estructural ({structural_error_rate:.2%}) supera el "
                f"límite crítico ({self.block_error_rate:.2%})."
            )
        elif valid_count < self.minimum_valid_records:
            status = GateStatus.BLOCKED
            warnings.append(
                f"Registros válidos restantes ({valid_count}) inferiores al tamaño "
                f"muestral mínimo exigido ({self.minimum_valid_records})."
            )
        elif structural_error_rate >= self.degraded_warning_rate:
            status = GateStatus.DEGRADED
            warnings.append(
                f"Calidad degradada: tasa de error estructural ({structural_error_rate:.2%}) "
                f"supera el umbral de alerta ({self.degraded_warning_rate:.2%})."
            )
        else:
            status = GateStatus.ALLOW

        report = IngestionAuditReport(
            status=status,
            timestamp_utc=timestamp_utc,
            total_records=total_records,
            valid_records=valid_count,
            rejected_records=rejected_count,
            error_rate=structural_error_rate,
            violation_breakdown=violation_breakdown,
            warnings=warnings,
        )

        if status == GateStatus.BLOCKED and raise_on_block:
            raise DataContractViolationError(
                f"Pipeline abortado por IngestionGate: {'; '.join(warnings)}"
            )

        return valid_df, report
