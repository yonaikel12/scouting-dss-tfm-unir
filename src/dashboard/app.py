"""Punto de entrada principal del Sistema de Soporte a la Decisión (DSS) en Streamlit.

Despliega las 5 vistas interactivas del sistema con Scorecards prescriptivos Next Best Action (NBA).

Ejecución desde terminal:
    streamlit run scouting_dss_tfm/src/dashboard/app.py
"""

from pathlib import Path
import sys
from typing import Tuple

import pandas as pd
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.analytics.multivariate_engine import (
    MultivariateModelArtifacts,
    ScoutingMultivariateEngine,
)
from src.dashboard.views import (
    render_data_lineage_view,
    render_executive_scorecards,
    render_individual_pizza_view,
    render_market_quadrants_view,
    render_player_clones_h2h_view,
    render_statistical_audit_view,
)
from src.ingestion.api_client import APIFootballClient
from src.processing.clean_pipeline import SilverETLPipeline


@st.cache_data(show_spinner="Ejecutando Pipeline Medallion (Bronze -> Silver -> Gold)...")
def load_and_compute_gold_data() -> Tuple[pd.DataFrame, MultivariateModelArtifacts]:
    """Carga o genera la cohorte validada y ejecuta el motor multivariante Gold."""
    schema_path = PROJECT_ROOT / "config" / "data_contract_schema.json"
    settings_path = PROJECT_ROOT / "config" / "settings.yaml"
    silver_parquet = PROJECT_ROOT / "data" / "interim" / "players_silver.parquet"
    duckdb_path = PROJECT_ROOT / "data" / "processed" / "scouting_gold.duckdb"

    sport_records, fin_records = APIFootballClient.generate_calibrated_cohort(
        n_players=420, random_seed=42
    )
    silver_pipeline = SilverETLPipeline(
        schema_path=schema_path,
        silver_parquet_path=silver_parquet,
        duckdb_path=duckdb_path,
        settings_path=settings_path,
    )
    df_silver, _, _ = silver_pipeline.run_bronze_to_silver(sport_records, fin_records)

    engine = ScoutingMultivariateEngine(
        min_explained_variance=0.75, k_min=3, k_max=8, min_ari=0.70, random_seed=42
    )
    df_gold, artifacts = engine.fit_transform_gold(df_silver)
    return df_gold, artifacts


def main() -> None:
    """Inicializa la configuración de página y renderiza las 5 vistas del DSS."""
    st.set_page_config(
        page_title="Scouting DSS | Rendimiento y Coste (UNIR TFM)",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    st.title("⚽ Sistema de Soporte a la Decisión (DSS) de Scouting: Rendimiento y Coste")
    st.caption(
        "Trabajo Fin de Máster — Máster Universitario en Análisis y Visualización de Datos Masivos (UNIR) | "
        "Arquitectura Medallion (MongoDB • Parquet/DuckDB • ACP • Clustering Híbrido K-Means/Ward • KNN) | "
        "📅 Corte Temporal de Datos (Snapshot Estático): Temporada 2023/24 – Apertura 2024/25"
    )
    st.info(
        "📅 **Alcance Temporal de la Cohorte (Point-in-Time Snapshot: Temporada 2023/2024 – Apertura 2024/2025):** "
        "Los registros deportivos y financieros corresponden a un **corte estático congelado** (no en tiempo real) "
        "para garantizar la reproducibilidad científica (`random_seed=42`) y evitar la fuga de datos temporal (*Data Leakage*). "
        "Cada futbolista figura vinculado al club y competición donde disputó los minutos auditados ($\\ge 600\\text{ min}$) "
        "y donde se midió la posesión de equipo ($50/\\text{Pos}_{\\text{equipo}}$) durante la ventana de observación "
        "(p. ej., *Leny Yoro* en *LOSC Lille* previo a su traspaso al *Manchester United*, o *Robin Le Normand* / *Mikel Merino* en *Real Sociedad*)."
    )

    df_gold, artifacts = load_and_compute_gold_data()
    engine = ScoutingMultivariateEngine()

    with st.sidebar:
        st.header("🎛️ Filtros de Dirección Deportiva")
        st.markdown(
            "<div style='background-color:#EFF6FF; border-left:4px solid #0072B2; padding:8px 10px; "
            "border-radius:4px; margin-bottom:12px; font-size:12.5px; color:#1E3A8A;'>"
            "<strong>📅 Ventana de Datos (Snapshot):</strong><br>"
            "Temporada 2023/24 – Apertura 2024/25<br>"
            "<em>Corte estático Point-in-Time (N = 420)</em>"
            "</div>",
            unsafe_allow_html=True,
        )
        positions = ["Todas"] + sorted(df_gold["position_group"].unique().tolist())
        selected_pos = st.selectbox("Demarcación Táctica (`position_group`):", options=positions)

        leagues = ["Todas"] + sorted(df_gold["league_name"].unique().tolist())
        selected_league = st.selectbox("Competición Europea:", options=leagues)

        max_age_year = st.slider(
            "Año mínimo de nacimiento (Filtro Sub-Edad):",
            min_value=int(df_gold["birth_year"].min()),
            max_value=int(df_gold["birth_year"].max()),
            value=int(df_gold["birth_year"].min()),
        )

        max_clone_budget_m = st.slider(
            "Presupuesto Máximo para Clones KNN (€ Millones):",
            min_value=1.0,
            max_value=100.0,
            value=35.0,
            step=1.0,
        )

    df_filtered = df_gold[df_gold["birth_year"] >= max_age_year].copy()
    if selected_pos != "Todas":
        df_filtered = df_filtered[df_filtered["position_group"] == selected_pos].copy()
    if selected_league != "Todas":
        df_filtered = df_filtered[df_filtered["league_name"] == selected_league].copy()

    if df_filtered.empty:
        st.error("Ningún jugador cumple los filtros seleccionados.")
        return

    player_options = df_filtered.sort_values(by="net_value", ascending=False)
    selected_player_name = st.selectbox(
        "🔍 Seleccionar Jugador Objetivo para Diagnóstico, Next Best Action y Clones KNN:",
        options=player_options["player_name"].tolist(),
    )
    selected_row = player_options[player_options["player_name"] == selected_player_name].iloc[0]
    selected_player_id = int(selected_row["player_id"])

    render_executive_scorecards(selected_row)
    st.divider()

    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        [
            "🚰 1. Linaje y Calidad de Datos",
            "📊 2. Mapa 4 Cuadrantes (Net Value)",
            "🍕 3. Perfil Individual (Pizza Chart)",
            "🧬 4. Buscador de Clones KNN (Radar H2H)",
            "🔬 5. Auditoría MLOps (KMO, ACP y ARI)",
        ]
    )

    with tab1:
        render_data_lineage_view(df_gold)
    with tab2:
        render_market_quadrants_view(df_filtered, selected_player_id=selected_player_id)
    with tab3:
        render_individual_pizza_view(df_gold, selected_player_id=selected_player_id)
    with tab4:
        render_player_clones_h2h_view(
            df_gold=df_gold,
            engine=engine,
            selected_player_id=selected_player_id,
            max_clone_budget_m=max_clone_budget_m,
        )
    with tab5:
        render_statistical_audit_view(artifacts)


if __name__ == "__main__":
    main()
