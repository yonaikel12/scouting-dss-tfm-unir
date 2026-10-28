"""Módulo de extracción, limpieza monetaria e ingesta de datos financieros (Capology y Transfermarkt).

Resuelve la adquisición de variables económicas críticas:
1. Valor de Mercado en Euros (`market_value_eur`) procedente de Transfermarkt.
2. Salario Anual Bruto en Euros (`annual_gross_salary_eur`) y año de expiración
   contractual (`contract_expiration_year`) procedentes de Capology.

Referencias Académicas:
    - Coates, D., & Parshakov, P. (2022). The wisdom of crowds and transfer market
      values. European Journal of Operational Research, 301(2), 523-534.
    - Herm, S., Callsen-Bracker, H.-M., & Kreis, H. (2014). When the crowd evaluates
      soccer players' market values: Accuracy and evaluation attributes of an online
      community. Sport Management Review, 17(4), 484-492.
    - Müller, O., Simons, A., & Weinmann, M. (2017). Beyond crowd judgments: Data-driven
      estimation of market value in association football. European Journal of Operational
      Research, 263(2), 611-624.
"""

from io import StringIO
import logging
from pathlib import Path
import re
import time
from typing import Any, Dict, List, Optional

import pandas as pd
import requests

from src.ingestion.fuzzy_matcher import FuzzyEntityMatcher

logger = logging.getLogger(__name__)


class FinancialDataIngestor:
    """Extractor y normalizador de registros salariales (Capology) y tasaciones (Transfermarkt)."""

    CURRENCY_RATES_TO_EUR: Dict[str, float] = {
        "EUR": 1.0,
        "€": 1.0,
        "GBP": 1.17,
        "£": 1.17,
        "USD": 0.92,
        "$": 0.92,
    }

    def __init__(
        self,
        raw_financial_dir: Path = Path("data/raw/financials"),
        request_delay_seconds: float = 4.0,
    ) -> None:
        """Inicializa el ingestor financiero."""
        self.raw_financial_dir = raw_financial_dir
        self.raw_financial_dir.mkdir(parents=True, exist_ok=True)
        self.request_delay_seconds = request_delay_seconds

    @classmethod
    def parse_monetary_string_to_eur(cls, raw_value: Any) -> float:
        """Convierte cadenas monetarias heterogéneas de Transfermarkt/Capology a Euros (float)."""
        if raw_value is None or (isinstance(raw_value, float) and pd.isna(raw_value)):
            return 0.0
        if isinstance(raw_value, (int, float)):
            return float(raw_value)

        text = str(raw_value).strip()
        if not text or text in ("-", "?", "N/A", "nan"):
            return 0.0

        fx_rate = 1.0
        for symbol, rate in cls.CURRENCY_RATES_TO_EUR.items():
            if symbol in text:
                fx_rate = rate
                break

        lower_text = text.lower()
        multiplier = 1.0
        if any(tok in lower_text for tok in ("mill", "mio", "m€", "m ", "bn")):
            multiplier = 1_000_000.0 if "bn" not in lower_text else 1_000_000_000.0
        elif re.search(r"\d+(\.\d+)?m\b", lower_text):
            multiplier = 1_000_000.0
        elif any(tok in lower_text for tok in ("mil", "tsd", "k€", "k ")):
            multiplier = 1_000.0
        elif re.search(r"\d+(\.\d+)?k\b", lower_text):
            multiplier = 1_000.0

        cleaned = re.sub(r"[^0-9,\.]", "", lower_text).strip(".,")
        if not cleaned:
            return 0.0

        if multiplier > 1.0:
            cleaned = cleaned.replace(",", ".")
        else:
            if cleaned.count(",") >= 1 and cleaned.count(".") == 0:
                parts = cleaned.split(",")
                cleaned = "".join(parts) if len(parts[-1]) == 3 else ".".join(parts)
            elif cleaned.count(".") > 1:
                cleaned = cleaned.replace(".", "")
            elif cleaned.count(",") >= 1 and cleaned.count(".") == 1:
                cleaned = cleaned.replace(",", "")

        try:
            numeric_val = float(cleaned)
        except ValueError:
            return 0.0

        return round(numeric_val * multiplier * fx_rate, 2)

    def load_from_csv_exports(
        self,
        capology_csv_path: Path,
        transfermarkt_csv_path: Optional[Path] = None,
    ) -> List[Dict[str, Any]]:
        """Carga y fusiona archivos CSV de salarios (Capology) y valores de mercado (Transfermarkt)."""
        if not capology_csv_path.exists():
            raise FileNotFoundError(f"Archivo Capology no encontrado: {capology_csv_path}")

        df_cap = pd.read_csv(capology_csv_path)
        records: List[Dict[str, Any]] = []

        tm_lookup: Dict[str, float] = {}
        if transfermarkt_csv_path is not None and transfermarkt_csv_path.exists():
            df_tm = pd.read_csv(transfermarkt_csv_path)
            for _, row in df_tm.iterrows():
                p_name = FuzzyEntityMatcher.normalize_string(
                    str(row.get("player_name", row.get("Player", "")))
                )
                m_val = self.parse_monetary_string_to_eur(
                    row.get("market_value_eur", row.get("Market Value", 0.0))
                )
                if p_name and m_val > 0:
                    tm_lookup[p_name] = m_val

        for idx, row in df_cap.iterrows():
            raw_name = str(
                row.get("player_name_raw", row.get("player_name", row.get("Player", "")))
            ).strip()
            raw_club = str(
                row.get("club_name_raw", row.get("club_name", row.get("Club", "Unknown Club")))
            ).strip()
            birth_year = int(row.get("birth_year", row.get("Birth Year", 1998)))

            salary_eur = self.parse_monetary_string_to_eur(
                row.get(
                    "annual_gross_salary_eur",
                    row.get("Gross P/Y (EUR)", row.get("Annual Gross", 0.0)),
                )
            )
            market_val_eur = self.parse_monetary_string_to_eur(
                row.get("market_value_eur", row.get("Market Value", 0.0))
            )

            if market_val_eur <= 0.0 and tm_lookup:
                norm_key = FuzzyEntityMatcher.normalize_string(raw_name)
                market_val_eur = tm_lookup.get(norm_key, 0.0)

            contract_exp = row.get("contract_expiration_year", row.get("Expiration", 2026))
            try:
                contract_year = int(str(contract_exp)[:4])
            except ValueError:
                contract_year = 2026

            if raw_name and salary_eur > 0 and market_val_eur > 0:
                records.append(
                    {
                        "financial_record_id": f"FIN-CSV-{idx + 1:05d}",
                        "player_name_raw": raw_name,
                        "birth_year": birth_year,
                        "club_name_raw": raw_club,
                        "market_value_eur": market_val_eur,
                        "annual_gross_salary_eur": salary_eur,
                        "contract_expiration_year": contract_year,
                        "source": "Capology_Transfermarkt_CSV",
                    }
                )

        return records

    def fetch_html_salary_table(self, url: str) -> pd.DataFrame:
        """Extrae de forma ética una tabla HTML pública de salarios/tasaciones con control de cadencia."""
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
            ),
            "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
        }
        time.sleep(self.request_delay_seconds)
        resp = requests.get(url, headers=headers, timeout=30)
        resp.raise_for_status()
        tables = pd.read_html(StringIO(resp.text))
        if not tables:
            raise ValueError(f"No se encontraron tablas HTML en la URL proporcionada: {url}")
        return tables[0]
