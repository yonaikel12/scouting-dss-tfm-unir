"""Script Maestro de Construcción de la ENTREGA 2 (Borrador Intermedio - Semana 10)
bajo la especificación V6 (Expansión a 40-45 páginas y máxima riqueza gráfica).

Construye y sincroniza:
- `borrador segunda entrega/Segunda_entrega_TFM.docx`
- `Segunda_entrega_TFM.docx` (raíz del workspace)
- `scouting_dss_tfm/docs/Segunda_entrega_TFM.docx`
sobre la estructura física de `plantillas y reglamento/plantilla_individual (1).docx`.
"""

from __future__ import annotations

from pathlib import Path
import sys

from docx import Document

PROJECT_ROOT = Path(__file__).resolve().parent
WORKSPACE_ROOT = PROJECT_ROOT.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from entrega2_v6_part1 import (
    configure_unir_v6_styles,
    populate_cover_and_front_matter,
    write_chapter_1_introduccion,
)
from entrega2_v6_part2 import write_chapter_2_estado_del_arte
from entrega2_v6_part3 import (
    write_chapter_3_metodologia,
    write_chapter_4_marco_normativo,
)
from entrega2_v6_part4 import write_chapters_5_to_8_and_references
import duckdb
from src.analytics.multivariate_engine import ScoutingMultivariateEngine
from run_real_pipeline import run_pipeline


def build_entrega2_v6() -> None:
    """Ejecuta el motor multivariante sobre la capa Silver real y ensambla el documento Word de la Entrega 2 (V6)."""
    duckdb_path = PROJECT_ROOT / "data" / "processed" / "scouting_gold.duckdb"
    if duckdb_path.exists():
        with duckdb.connect(str(duckdb_path)) as conn:
            df_silver = conn.execute("SELECT * FROM silver_players").df()
        engine = ScoutingMultivariateEngine(
            min_explained_variance=0.75, k_min=3, k_max=8, min_ari=0.70, random_seed=42
        )
        df_gold, artifacts = engine.fit_transform_gold(df_silver)
    else:
        artifacts, df_gold = run_pipeline()

    template_path = WORKSPACE_ROOT / "plantillas y reglamento" / "plantilla_individual (1).docx"
    figures_dir = PROJECT_ROOT / "docs" / "figures"

    target_borrador = WORKSPACE_ROOT / "borrador segunda entrega" / "Segunda_entrega_TFM.docx"
    target_root = WORKSPACE_ROOT / "Segunda_entrega_TFM.docx"
    target_docs = PROJECT_ROOT / "docs" / "Segunda_entrega_TFM.docx"

    doc = Document(str(template_path)) if template_path.exists() else Document()
    configure_unir_v6_styles(doc)
    populate_cover_and_front_matter(doc)
    write_chapter_1_introduccion(doc)
    write_chapter_2_estado_del_arte(doc)
    write_chapter_3_metodologia(doc, artifacts, figures_dir)
    write_chapter_4_marco_normativo(doc)
    write_chapters_5_to_8_and_references(doc, artifacts, df_gold, figures_dir)

    for out_path in [target_borrador, target_root, target_docs]:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            doc.save(str(out_path))
            print(f"[OK] Guardado exitosamente en: {out_path} ({out_path.stat().st_size:,} bytes)")
        except PermissionError as exc:
            print(f"[WARN] No se pudo sobrescribir {out_path} (archivo abierto): {exc}")

    # Auditoría cuantitativa de páginas y palabras
    para_words = sum(len(p.text.split()) for p in doc.paragraphs)
    table_words = sum(
        len(cell.text.split())
        for t in doc.tables
        for row in t.rows
        for cell in row.cells
    )
    total_words = para_words + table_words
    n_figs = len(doc.inline_shapes)
    n_tables = len(doc.tables)
    print("====================================================================")
    print("AUDITORÍA CUANTITATIVA DEL DOCUMENTO GENERADO (ENTREGA 2 - V6)")
    print("====================================================================")
    print(f"Total párrafos: {len(doc.paragraphs)}")
    print(f"Palabras en prosa y títulos: {para_words:,}")
    print(f"Palabras en tablas estructuradas: {table_words:,}")
    print(f"Total palabras del documento: {total_words:,}")
    print(f"Total figuras embebidas a 300 DPI: {n_figs}")
    print(f"Total tablas académicas: {n_tables}")


if __name__ == "__main__":
    build_entrega2_v6()
