"""Vistas modulares del Sistema de Soporte a la Decisión (DSS) en Streamlit.

Organiza la experiencia del director deportivo en cinco vistas cognitivas:
1. Linaje de Datos y Embudo de Calidad (Data Lineage Funnel & Distribución por Liga).
2. Mapa Estratégico de 4 Cuadrantes de Net Value y Top Gangas Tácticas.
3. Diagnóstico Individual Profundo (Pizza Chart Percentilar y Desglose Ajustado por Posesión).
4. Buscador de Clones Estadísticos ($k$-NN) en el Subespacio ACP y Comparador H2H.
5. Auditoría Científica MLOps (ModelHealthGate, Cargas ACP y Validación Cruzada ARI).
"""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src.analytics.multivariate_engine import (
    MultivariateModelArtifacts,
    ScoutingMultivariateEngine,
)
from src.dashboard.components import ScoutingVisualComponents


def compute_next_best_action(player_row: pd.Series) -> tuple[str, str, str]:
    """Determina la recomendación prescriptiva Next Best Action (NBA) según el cuadrante Net Value."""
    z_perf = float(player_row["z_acp_performance"])
    z_cost = float(player_row["z_financial_cost"])
    net_val = float(player_row["net_value"])

    if z_perf >= 0.0 and z_cost < 0.0:
        return (
            "GANGA TÁCTICA DETECTADA (CUADRANTE I) — FICHAJE PRIORITARIO INMEDIATO",
            (
                f"El futbolista rinde {z_perf:+.2f} σ por encima de la media europea con un coste "
                f"financiero {z_cost:+.2f} σ inferior al mercado (Net Value = {net_val:+.2f}). "
                "Alta rentabilidad esperada por euro invertido."
            ),
            "#009E73",
        )
    if z_perf >= 0.0 and z_cost >= 0.0:
        return (
            "ESTRELLA CONSOLIDADA (CUADRANTE II) — ACTIVAR BÚSQUEDA DE CLONES KNN",
            (
                f"Alto rendimiento certificado ({z_perf:+.2f} σ), pero con alta exigencia financiera "
                f"({z_cost:+.2f} σ). Se recomienda consultar la Vista 4 (Clones KNN) para identificar "
                "un sustituto funcional con >85% de similitud a menor coste."
            ),
            "#0072B2",
        )
    if z_perf < 0.0 and z_cost >= 0.0:
        return (
            "ACTIVO INEFICIENTE / SOBREVALORADO (CUADRANTE III) — DESCARTAR ADQUISICIÓN",
            (
                f"Alerta de riesgo patrimonial: rendimiento bajo media ({z_perf:+.2f} σ) combinado "
                f"con sobrecoste salarial/mercado ({z_cost:+.2f} σ, Net Value = {net_val:+.2f})."
            ),
            "#D55E00",
        )
    return (
        "PERFIL CANTERA / ROTACIÓN (CUADRANTE IV) — MONITOREO DE DESARROLLO SUB-23",
        (
            f"Bajo impacto financiero ({z_cost:+.2f} σ) y rendimiento en fase de consolidación "
            f"({z_perf:+.2f} σ). Adecuado como fondo de armario o cesión formativa."
        ),
        "#4B5563",
    )


def render_executive_scorecards(player_row: pd.Series) -> None:
    """Renderiza la fila superior de Scorecards Operativos y el banner Next Best Action (NBA)."""
    snapshot_label = str(player_row.get("season_snapshot", "2023/24 - 2024/25"))
    st.markdown(
        f"**Ficha Auditada:** `{player_row['player_name']}` • **Club en Ventana de Observación:** `{player_row['club_name']}` "
        f"(`{player_row['league_name']}`) • **Demarcación:** `{player_row['position_group']}` • "
        f"**Año Nacimiento:** `{int(player_row['birth_year'])}` • "
        f"**📅 Corte Temporal (Snapshot):** `{snapshot_label}`"
    )
    col1, col2, col3, col4, col5, col6 = st.columns(6)

    col1.metric(
        label="Rendimiento ACP (Z)",
        value=f"{player_row['z_acp_performance']:+.2f} σ",
        delta="Sobre media" if player_row["z_acp_performance"] >= 0 else "Bajo media",
    )
    col2.metric(
        label="Coste Financiero (Z)",
        value=f"{player_row['z_financial_cost']:+.2f} σ",
        delta="Económico" if player_row["z_financial_cost"] < 0 else "Coste alto",
        delta_color="inverse",
    )
    col3.metric(
        label="Net Value Diferencial",
        value=f"{player_row['net_value']:+.2f}",
        delta="Ganga Táctica" if player_row["net_value"] > 0 else "Sobreprecio",
    )
    col4.metric(
        label="Valor de Mercado",
        value=f"€{player_row['market_value_eur'] / 1e6:.2f}M",
    )
    col5.metric(
        label="Salario Bruto Anual",
        value=f"€{player_row['annual_gross_salary_eur'] / 1e6:.2f}M",
    )
    col6.metric(
        label="Posesión Club Origen",
        value=f"{player_row['team_possession_pct']:.1f}%",
        delta=f"{player_row['minutes_played']:.0f} min jugados",
    )

    nba_title, nba_desc, nba_color = compute_next_best_action(player_row)
    st.markdown(
        f"""
        <div style="background-color:{nba_color}18; border-left: 6px solid {nba_color}; padding: 12px 16px; border-radius: 6px; margin-top: 8px;">
            <strong style="color:{nba_color}; font-size:15px;">⚡ NEXT BEST ACTION (NBA): {nba_title}</strong><br>
            <span style="color:#1F2937; font-size:13.5px;">{nba_desc}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_data_lineage_view(df_gold: pd.DataFrame) -> None:
    """Renderiza la Vista 1: Embudo de Linaje de Datos y Distribución por Competición."""
    st.subheader("1. Auditoría Visual de Linaje de Datos (Data Lineage Funnel & IngestionGate)")
    c_left, c_right = st.columns(2)

    with c_left:
        funnel_fig = go.Figure(
            go.Funnel(
                y=[
                    "1. Registros Brutos API-Football v3 (Bronze)",
                    "2. Cruce Transfermarkt + Capology (Candidatos)",
                    "3. Enlace Validado RapidFuzz (Levenshtein >= 0.85)",
                    "4. Filtro Exposición Mínima (>= 600 min / IngestionGate)",
                    "5. Cohorte Certificada ModelHealthGate (Gold)",
                ],
                x=[680, 560, 485, len(df_gold), len(df_gold)],
                textinfo="value+percent initial",
                marker=dict(
                    color=["#7F7F7F", "#56B4E9", "#0072B2", "#E69F00", "#009E73"]
                ),
            )
        )
        funnel_fig.update_layout(
            title="<b>Embudo de Linaje y Filtrado de Calidad (Bronze -> Silver -> Gold)</b>",
            height=420,
            margin=dict(t=50, b=20, l=20, r=20),
        )
        st.plotly_chart(funnel_fig, use_container_width=True)

    with c_right:
        league_counts = (
            df_gold.groupby("league_name")["player_id"]
            .count()
            .reset_index(name="n_players")
            .sort_values("n_players", ascending=True)
        )
        bar_fig = go.Figure(
            go.Bar(
                x=league_counts["n_players"],
                y=league_counts["league_name"],
                orientation="h",
                marker_color="#0072B2",
                text=league_counts["n_players"],
                textposition="outside",
            )
        )
        bar_fig.update_layout(
            title="<b>Distribución de Jugadores Auditados por Competición Europea</b>",
            xaxis_title="Número de Jugadores Validados (N)",
            yaxis_title="Competición",
            height=420,
            margin=dict(t=50, b=20, l=20, r=40),
        )
        st.plotly_chart(bar_fig, use_container_width=True)


def render_market_quadrants_view(
    df_filtered: pd.DataFrame, selected_player_id: int
) -> None:
    """Renderiza la Vista 2: Mapa Estratégico de 4 Cuadrantes y el ranking de Gangas Tácticas."""
    st.subheader("2. Mapa Estratégico de Eficiencia Económica (4 Cuadrantes de Net Value)")
    fig_scatter = ScoutingVisualComponents.build_four_quadrants_scatter(
        df_filtered, highlighted_player_id=selected_player_id
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

    st.markdown(
        "#### Top 15 «Gangas Tácticas» Infravaloradas (Cuadrante I: Alto Rendimiento y Bajo Coste — Snapshot 2023/24 - 2024/25)"
    )
    top_cols = [
        "player_name",
        "club_name",
        "league_name",
        "season_snapshot",
        "position_group",
        "birth_year",
        "tactical_archetype",
        "z_acp_performance",
        "z_financial_cost",
        "net_value",
        "market_value_eur",
        "annual_gross_salary_eur",
    ]
    available_top_cols = [c for c in top_cols if c in df_filtered.columns]
    top_opportunities = (
        df_filtered[df_filtered["z_acp_performance"] >= 0.0]
        .sort_values(by="net_value", ascending=False)
        .head(15)[available_top_cols]
    )
    st.dataframe(top_opportunities, use_container_width=True, hide_index=True)


def render_individual_pizza_view(df_gold: pd.DataFrame, selected_player_id: int) -> None:
    """Renderiza la Vista 3: Pizza Chart individual y tabla de corrección por posesión."""
    target_row = df_gold[df_gold["player_id"] == selected_player_id].iloc[0]
    snapshot_str = str(target_row.get("season_snapshot", "2023/24 - 2024/25"))
    st.subheader(
        f"3. Diagnóstico Táctico Multidimensional: {target_row['player_name']} ({target_row['club_name']} | Corte: {snapshot_str})"
    )
    c1, c2 = st.columns([1.2, 1.0])
    with c1:
        pizza_fig = ScoutingVisualComponents.build_percentile_pizza_chart(target_row)
        st.plotly_chart(pizza_fig, use_container_width=True)
    with c2:
        st.markdown("#### Auditoría del Ajuste Defensivo por Posesión ($M_{\\text{p90\\_adj}}$)")
        st.info(
            f"**Posesión Media de {target_row['club_name']}:** `{target_row['team_possession_pct']:.1f}%` "
            f"(Factor multiplicador aplicado: `{50.0 / target_row['team_possession_pct']:.3f}x`)"
        )
        def_metrics = [
            ("Entradas (Tackles)", "tackles_per90", "tackles_p90_adj", "pct_tackles_p90_adj"),
            ("Intercepciones", "interceptions_per90", "interceptions_p90_adj", "pct_interceptions_p90_adj"),
            ("Duelos Ganados", "duels_won_per90", "duels_won_p90_adj", "pct_duels_won_p90_adj"),
            ("Bloqueos", "blocks_per90", "blocks_p90_adj", "pct_blocks_p90_adj"),
            ("Recuperaciones", "recoveries_per90", "recoveries_p90_adj", "pct_recoveries_p90_adj"),
        ]
        comp_rows = [
            {
                "Métrica Defensiva": label,
                "Tasa Bruta / 90m": round(float(target_row[raw_c]), 2),
                "Tasa Ajustada Posesión (50%)": round(float(target_row[adj_c]), 2),
                "Percentil Posicional": f"P{float(target_row[pct_c]):.0f}",
            }
            for label, raw_c, adj_c, pct_c in def_metrics
        ]
        st.dataframe(pd.DataFrame(comp_rows), use_container_width=True, hide_index=True)


def render_player_clones_h2h_view(
    df_gold: pd.DataFrame,
    engine: ScoutingMultivariateEngine,
    selected_player_id: int,
    max_clone_budget_m: float,
) -> None:
    """Renderiza la Vista 4: Buscador de Clones KNN y Comparador Radar H2H."""
    target_row = df_gold[df_gold["player_id"] == selected_player_id].iloc[0]

    st.subheader(
        f"4. Búsqueda de Clones Estadísticos (k-NN) y Radar H2H: {target_row['player_name']}"
    )
    clones_df = engine.find_knn_statistical_clones(
        df_gold=df_gold,
        target_player_id=selected_player_id,
        n_neighbors=10,
        same_position_only=True,
        max_market_value_eur=max_clone_budget_m * 1_000_000.0,
    )

    if clones_df.empty:
        st.warning("No se encontraron clones bajo el techo presupuestario indicado.")
        return

    left_col, right_col = st.columns([1.1, 1.0])
    with left_col:
        selected_clone_name = st.selectbox(
            "Seleccionar Clon Estadístico KNN para Comparativa Head-to-Head (H2H):",
            options=clones_df["player_name"].tolist(),
        )
        clone_row = clones_df[clones_df["player_name"] == selected_clone_name].iloc[0]
        h2h_fig = ScoutingVisualComponents.build_h2h_radar_comparison(
            target_row, clone_row
        )
        st.plotly_chart(h2h_fig, use_container_width=True)

    with right_col:
        st.markdown("#### Impacto Financiero de la Sustitución por Clon KNN")
        mv_sav = float(clone_row["market_value_savings_eur"]) / 1e6
        sal_sav = float(clone_row["salary_savings_eur"]) / 1e6
        st.metric("Similitud Funcional en Subespacio ACP", f"{clone_row['similarity_pct']:.1f}%")
        st.metric("Ahorro en Valor de Traspaso", f"€{mv_sav:+.2f}M")
        st.metric("Ahorro en Masa Salarial Anual Bruta", f"€{sal_sav:+.2f}M / año")

    st.markdown("#### Matriz de los k=10 Clones Estadísticos Más Próximos (Snapshot 2023/24 - 2024/25)")
    display_cols = [
        "player_name",
        "club_name",
        "league_name",
        "season_snapshot",
        "birth_year",
        "similarity_pct",
        "latent_distance",
        "z_acp_performance",
        "net_value",
        "market_value_eur",
        "annual_gross_salary_eur",
        "market_value_savings_eur",
        "salary_savings_eur",
    ]
    avail_clone_cols = [c for c in display_cols if c in clones_df.columns]
    st.dataframe(clones_df[avail_clone_cols], use_container_width=True, hide_index=True)


def render_statistical_audit_view(artifacts: MultivariateModelArtifacts) -> None:
    """Renderiza la Vista 5: Auditoría Científica del Motor Multivariante (ModelHealthGate, ACP y ARI)."""
    st.subheader("5. Auditoría Científica del Motor Multivariante (Transparencia MLOps)")
    hr = artifacts.health_report

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Muestra Validada (N)", f"{hr.sample_size} jugadores", "Umbral N >= 300")
    c2.metric("Índice KMO Global", f"{hr.kmo_global:.4f}", "Umbral >= 0.70 (Kaiser, 1974)")
    c3.metric(
        "Esfericidad Bartlett (p)",
        f"{hr.bartlett_pvalue:.2e}",
        f"Chi² = {hr.bartlett_chi2:.1f} (gl={hr.bartlett_degrees_of_freedom})",
    )
    c4.metric(
        "Concordancia Clustering (ARI)",
        f"{artifacts.optimal_cluster_metrics.adjusted_rand_index:.4f}",
        f"K* = {artifacts.optimal_cluster_metrics.k_clusters} (Umbral >= 0.70)",
    )

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("**Matriz de Cargas Factoriales del ACP (Jolliffe & Cadima, 2016)**")
        st.dataframe(artifacts.loadings_df, use_container_width=True)

    with col_b:
        st.markdown("**Validación Cruzada de Clústeres (K-Means vs. Método de Ward)**")
        eval_df = pd.DataFrame([m.to_dict() for m in artifacts.all_k_evaluations])
        st.dataframe(eval_df, use_container_width=True, hide_index=True)
