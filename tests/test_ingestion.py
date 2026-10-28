"""Suite de pruebas unitarias para la Capa de Ingesta (API Client, Mongo Loader, Financial Ingestor y Fuzzy Matcher)."""

from pathlib import Path
from tempfile import TemporaryDirectory

from src.ingestion.api_client import APIFootballClient
from src.ingestion.financial_ingestor import FinancialDataIngestor
from src.ingestion.fuzzy_matcher import FuzzyEntityMatcher
from src.ingestion.mongo_loader import BronzeMongoRepository


def test_levenshtein_diacritics_and_threshold() -> None:
    """Verifica que nombres con diacríticos ('Dušan Vlahović') alcancen similitud >= 0.85."""
    matcher = FuzzyEntityMatcher(similarity_threshold=0.85)
    sim_exact = matcher.normalized_levenshtein_similarity("Dušan Vlahović", "Dusan Vlahovic")
    assert sim_exact == 1.0

    sim_close = matcher.normalized_levenshtein_similarity("Gonçalo Inácio", "Goncalo Inacio")
    assert sim_close >= 0.85

    sim_different = matcher.normalized_levenshtein_similarity("Kylian Mbappé", "Erling Haaland")
    assert sim_different < 0.40


def test_monetary_parser_capology_and_transfermarkt_formats() -> None:
    """Verifica la conversión exacta de formatos monetarios de Transfermarkt y Capology a Euros."""
    assert FinancialDataIngestor.parse_monetary_string_to_eur("€45.00m") == 45_000_000.0
    assert FinancialDataIngestor.parse_monetary_string_to_eur("12,50 mill. €") == 12_500_000.0
    assert FinancialDataIngestor.parse_monetary_string_to_eur("€850k") == 850_000.0
    assert FinancialDataIngestor.parse_monetary_string_to_eur("€5,200,000") == 5_200_000.0


def test_entity_matching_blocks_wrong_birth_year_on_ambiguity() -> None:
    """Verifica que dos jugadores con nombre parecido pero distinto año de nacimiento no se crucen erróneamente."""
    matcher = FuzzyEntityMatcher(
        similarity_threshold=0.85, require_exact_birth_year_on_ambiguity=True
    )
    sport_docs = [
        {
            "player_id": 101,
            "player_name": "Alex Garcia",
            "birth_year": 1997,
            "club_name": "Girona FC",
        }
    ]
    fin_docs = [
        {
            "financial_record_id": "FIN-1",
            "player_name_raw": "Alex Garciax",
            "birth_year": 2003,
            "club_name_raw": "Girona FC",
            "market_value_eur": 15_000_000.0,
            "annual_gross_salary_eur": 2_000_000.0,
        }
    ]
    df_merged, results = matcher.match_records(sport_docs, fin_docs)
    assert len(df_merged) == 0
    assert results[0].matched is False


def test_bronze_repository_fallback_persistence() -> None:
    """Comprueba la persistencia idempotente en Bronze cuando MongoDB opera en modo JSONL local."""
    sport_records, fin_records = APIFootballClient.generate_calibrated_cohort(
        n_players=25, random_seed=42
    )
    with TemporaryDirectory() as tmp_dir:
        repo = BronzeMongoRepository(
            mongo_uri="mongodb://invalid-host:27017/",
            fallback_dir=Path(tmp_dir),
            server_selection_timeout_ms=100,
        )
        res_sport = repo.upsert_sport_records(sport_records)
        res_fin = repo.upsert_financial_records(fin_records)

        assert res_sport["inserted_or_updated"] == 25
        assert res_fin["inserted_or_updated"] == 25

        loaded_sport = repo.load_collection("raw_api_football_players")
        assert len(loaded_sport) == 25
        assert "payload_sha256" in loaded_sport[0]
