"""Script maestro de ejecución end-to-end (Bronze -> Silver -> Gold) y generación de `memoria_TFM_UNIR.docx`.

1. Ejecuta el pipeline completo de datos materializando:
   - `data/raw/raw_api_football_players.jsonl` y `data/raw/raw_financial_records.jsonl`
   - `data/interim/players_silver.parquet`
   - `data/processed/players_gold_analytics.parquet` y `data/processed/scouting_gold.duckdb`
2. Genera el documento oficial `memoria_TFM_UNIR.docx` sobre la plantilla oficial de la
   UNIR (`plantillas y reglamento/plantilla_individual (1).docx`), sincronizando las
   métricas reales obtenidas por el motor multivariante (KMO, Bartlett, ACP, ARI y Net Value)
   e insertando las 16 figuras estadísticas y diagramas de arquitectura a 300 DPI.
"""

from pathlib import Path
import sys

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.shared import Pt, RGBColor
import duckdb

PROJECT_ROOT = Path(__file__).resolve().parent
WORKSPACE_ROOT = PROJECT_ROOT.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.analytics.multivariate_engine import (
    MultivariateModelArtifacts,
    ScoutingMultivariateEngine,
)
from src.ingestion.api_client import APIFootballClient
from src.ingestion.mongo_loader import BronzeMongoRepository
from src.processing.clean_pipeline import SilverETLPipeline
from thesis_chapters_part1 import write_chapters_1_to_4
from thesis_chapters_part2 import write_chapters_5_to_8_and_annexes
from thesis_chapters_part3 import write_deep_mathematical_and_empirical_annex


def execute_full_medallion_pipeline() -> MultivariateModelArtifacts:
    """Ejecuta y persiste las tres capas (Bronze, Silver y Gold) del prototipo."""
    sport_records, fin_records = APIFootballClient.generate_calibrated_cohort(
        n_players=420, random_seed=42
    )

    bronze_repo = BronzeMongoRepository(
        fallback_dir=PROJECT_ROOT / "data" / "raw",
        server_selection_timeout_ms=500,
    )
    bronze_repo.upsert_sport_records(sport_records)
    bronze_repo.upsert_financial_records(fin_records)

    schema_path = PROJECT_ROOT / "config" / "data_contract_schema.json"
    settings_path = PROJECT_ROOT / "config" / "settings.yaml"
    silver_parquet = PROJECT_ROOT / "data" / "interim" / "players_silver.parquet"
    gold_parquet = PROJECT_ROOT / "data" / "processed" / "players_gold_analytics.parquet"
    duckdb_path = PROJECT_ROOT / "data" / "processed" / "scouting_gold.duckdb"

    silver_pipeline = SilverETLPipeline(
        schema_path=schema_path,
        silver_parquet_path=silver_parquet,
        duckdb_path=duckdb_path,
        settings_path=settings_path,
    )
    df_silver, audit_report, _ = silver_pipeline.run_bronze_to_silver(
        sport_records, fin_records
    )
    bronze_repo.log_audit_event(audit_report.to_dict())

    engine = ScoutingMultivariateEngine(
        min_explained_variance=0.75, k_min=3, k_max=8, min_ari=0.70, random_seed=42
    )
    df_gold, artifacts = engine.fit_transform_gold(df_silver)

    df_gold.to_parquet(gold_parquet, index=False, engine="pyarrow")
    with duckdb.connect(str(duckdb_path)) as conn:
        conn.register("tmp_gold", df_gold)
        conn.execute("CREATE OR REPLACE TABLE gold_players AS SELECT * FROM tmp_gold")
        conn.unregister("tmp_gold")

    return artifacts


def configure_unir_styles(doc: Document) -> None:
    """Aplica la normativa tipográfica de la UNIR (Calibri 12, justificado, interlineado 1.5, 6 pt)."""
    normal_style = doc.styles["Normal"]
    normal_style.font.name = "Calibri"
    normal_style.font.size = Pt(12)
    normal_style.font.color.rgb = RGBColor(0, 0, 0)
    normal_style.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    normal_style.paragraph_format.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
    normal_style.paragraph_format.space_after = Pt(6)
    normal_style.paragraph_format.space_before = Pt(0)

    heading_configs = {
        "Heading 1": (18, RGBColor(0, 90, 140), True, 18, 8),
        "Heading 2": (14, RGBColor(0, 90, 140), True, 14, 6),
        "Heading 3": (12, RGBColor(0, 51, 102), True, 10, 4),
    }
    for style_name, (pt_size, color_rgb, is_bold, sp_before, sp_after) in heading_configs.items():
        if style_name in doc.styles:
            h_style = doc.styles[style_name]
            h_style.font.name = "Calibri Light"
            h_style.font.size = Pt(pt_size)
            h_style.font.bold = is_bold
            h_style.font.color.rgb = color_rgb
            h_style.paragraph_format.space_before = Pt(sp_before)
            h_style.paragraph_format.space_after = Pt(sp_after)
            h_style.paragraph_format.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE


def build_synchronized_thesis_docx(artifacts: MultivariateModelArtifacts) -> Path:
    """Construye `memoria_TFM_UNIR.docx` sobre la plantilla oficial de la UNIR con las 16 figuras embebidas."""
    template_path = (
        WORKSPACE_ROOT / "plantillas y reglamento" / "plantilla_individual (1).docx"
    )
    output_path = WORKSPACE_ROOT / "memoria_TFM_UNIR.docx"
    docs_copy_path = PROJECT_ROOT / "docs" / "memoria_TFM_UNIR.docx"
    figures_dir = PROJECT_ROOT / "docs" / "figures"
    gold_parquet = PROJECT_ROOT / "data" / "processed" / "players_gold_analytics.parquet"

    doc = Document(str(template_path)) if template_path.exists() else Document()
    configure_unir_styles(doc)

    write_chapters_1_to_4(doc, artifacts, figures_dir)
    write_chapters_5_to_8_and_annexes(doc, artifacts, figures_dir)
    write_deep_mathematical_and_empirical_annex(doc, artifacts, gold_parquet)

    # Guardamos siempre una copia sincronizada en scouting_dss_tfm/docs/memoria_TFM_UNIR.docx
    docs_copy_path.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(docs_copy_path))

    try:
        doc.save(str(output_path))
        return output_path
    except PermissionError:
        return docs_copy_path


if __name__ == "__main__":
    model_artifacts = execute_full_medallion_pipeline()
    saved_docx = build_synchronized_thesis_docx(model_artifacts)
    print(f"[OK] Pipeline Medallion ejecutado y Memoria UNIR con 16 figuras guardada en: {saved_docx}")
