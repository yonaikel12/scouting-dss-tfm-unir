"""Componentes gráficos de Visual Analytics para el DSS en Streamlit.

Implementa visualizaciones de alta relación tinta-datos (Data-Ink Ratio; Tufte, 2001)
y codificación preatentiva (Few, 2012; Knaflic, 2015) con la paleta accesible para
daltonismo de Okabe e Ito (2008):
1. Pizza Chart de Percentiles ($P_{1-99}$) agrupado por bloque táctico.
2. Scatter Plot Estratégico de 4 Cuadrantes de Net Value ($Z_{\text{ACP}}$ vs $Z_{\text{Coste}}$).
3. Gráfico Radar / Polar Comparativo Head-to-Head (H2H) entre Jugador Objetivo y Clon KNN.
"""

from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
import plotly.graph_objects as go


class ScoutingVisualComponents:
    """Factoría de gráficos interactivos Plotly diseñados bajo principios perceptivos."""

    PALETTE: Dict[str, str] = {
        "primary_blue": "#0072B2",
        "emerald_green": "#009E73",
        "vermilion_red": "#D55E00",
        "reddish_purple": "#CC79A7",
        "amber_gold": "#E69F00",
        "neutral_grey": "#7F7F7F",
        "light_grid": "#E5E7EB",
    }

    METRIC_LABELS_ES: List[Tuple[str, str, str]] = [
        ("pct_goals_per90", "Goles / 90", "Ataque y Finalización"),
        ("pct_expected_goals_xg_per90", "xG Esperados / 90", "Ataque y Finalización"),
        ("pct_shots_on_target_per90", "Tiros a Puerta / 90", "Ataque y Finalización"),
        ("pct_assists_per90", "Asistencias / 90", "Ataque y Finalización"),
        ("pct_expected_assists_xa_per90", "xA Esperadas / 90", "Creación y Progresión"),
        ("pct_key_passes_per90", "Pases Clave / 90", "Creación y Progresión"),
        ("pct_progressive_passes_per90", "Pases Progresivos / 90", "Creación y Progresión"),
        ("pct_progressive_carries_per90", "Conducciones Prog. / 90", "Creación y Progresión"),
        ("pct_successful_dribbles_per90", "Regates Exitosos / 90", "Creación y Progresión"),
        ("pct_aerial_duels_won_per90", "Duelos Aéreos / 90", "Defensa Ajustada Posesión"),
        ("pct_tackles_p90_adj", "Entradas (Adj. Pos.)", "Defensa Ajustada Posesión"),
        ("pct_interceptions_p90_adj", "Intercepciones (Adj. Pos.)", "Defensa Ajustada Posesión"),
        ("pct_duels_won_p90_adj", "Duelos Ganados (Adj. Pos.)", "Defensa Ajustada Posesión"),
        ("pct_blocks_p90_adj", "Bloqueos (Adj. Pos.)", "Defensa Ajustada Posesión"),
        ("pct_recoveries_p90_adj", "Recuperaciones (Adj. Pos.)", "Defensa Ajustada Posesión"),
    ]

    @classmethod
    def build_percentile_pizza_chart(cls, player_row: pd.Series) -> go.Figure:
        """Construye un Pizza Chart (Barpolar) de percentiles condicionados por posición."""
        categories = [label for _, label, _ in cls.METRIC_LABELS_ES]
        values = [float(player_row.get(col, 50.0)) for col, _, _ in cls.METRIC_LABELS_ES]
        groups = [grp for _, _, grp in cls.METRIC_LABELS_ES]

        color_map = {
            "Ataque y Finalización": cls.PALETTE["emerald_green"],
            "Creación y Progresión": cls.PALETTE["primary_blue"],
            "Defensa Ajustada Posesión": cls.PALETTE["vermilion_red"],
        }
        bar_colors = [color_map[g] for g in groups]

        fig = go.Figure()
        fig.add_trace(
            go.Barpolar(
                r=values,
                theta=categories,
                marker_color=bar_colors,
                marker_line_color="#FFFFFF",
                marker_line_width=1.5,
                opacity=0.88,
                hovertemplate="<b>%{theta}</b><br>Percentil Posicional: P%{r:.0f}<extra></extra>",
            )
        )

        player_name = str(player_row.get("player_name", "Jugador"))
        pos_group = str(player_row.get("position_group", ""))
        club = str(player_row.get("club_name", ""))
        snap = str(player_row.get("season_snapshot", "2023/24 - 2024/25"))

        fig.update_layout(
            title={
                "text": (
                    f"<b>Perfil Percentilar Multidimensional (Pizza Chart)</b><br>"
                    f"<span style='font-size:12px;color:#4B5563'>{player_name} ({club} | Posición: {pos_group} | Corte: {snap})</span>"
                ),
                "x": 0.02,
            },
            polar=dict(
                radialaxis=dict(
                    range=[0, 100],
                    showticklabels=True,
                    tickvals=[25, 50, 75, 95],
                    gridcolor=cls.PALETTE["light_grid"],
                ),
                angularaxis=dict(
                    direction="clockwise",
                    period=len(categories),
                    gridcolor=cls.PALETTE["light_grid"],
                ),
            ),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(t=75, b=35, l=45, r=45),
            height=500,
        )
        return fig

    @classmethod
    def build_four_quadrants_scatter(
        cls, df_gold: pd.DataFrame, highlighted_player_id: int | None = None
    ) -> go.Figure:
        """Construye el Mapa Estratégico de 4 Cuadrantes (Rendimiento ACP vs Coste Financiero)."""
        quad_colors = {
            "Cuadrante I: Oportunidad de Mercado (Alto Rendimiento / Bajo Coste)": cls.PALETTE["emerald_green"],
            "Cuadrante II: Élite Consolidada (Alto Rendimiento / Alto Coste)": cls.PALETTE["amber_gold"],
            "Cuadrante III: Sobrevalorado / Riesgo Financiero (Bajo Rendimiento / Alto Coste)": cls.PALETTE["vermilion_red"],
            "Cuadrante IV: Rotación / Desarrollo (Bajo Rendimiento / Bajo Coste)": cls.PALETTE["neutral_grey"],
        }

        fig = go.Figure()

        for quad_label, color_hex in quad_colors.items():
            sub_df = df_gold[df_gold["strategic_quadrant"] == quad_label]
            if sub_df.empty:
                continue

            fig.add_trace(
                go.Scatter(
                    x=sub_df["z_financial_cost"],
                    y=sub_df["z_acp_performance"],
                    mode="markers",
                    name=quad_label.split(":")[0],
                    marker=dict(
                        size=9,
                        color=color_hex,
                        opacity=0.78,
                        line=dict(width=0.6, color="#FFFFFF"),
                    ),
                    customdata=np.stack(
                        [
                            sub_df["player_name"],
                            sub_df["club_name"],
                            sub_df["position_group"],
                            sub_df["net_value"],
                            sub_df["market_value_eur"] / 1e6,
                            sub_df["annual_gross_salary_eur"] / 1e6,
                        ],
                        axis=-1,
                    ),
                    hovertemplate=(
                        "<b>%{customdata[0]}</b> (%{customdata[1]} - %{customdata[2]})<br>"
                        "Corte Temporal (Snapshot): 2023/24 - 2024/25<br>"
                        "Z-Rendimiento ACP: %{y:.2f} | Z-Coste Financiero: %{x:.2f}<br>"
                        "<b>Net Value: %{customdata[3]:+.2f}</b><br>"
                        "Valor Mercado: €%{customdata[4]:.1f}M | Salario Bruto: €%{customdata[5]:.2f}M/año"
                        "<extra></extra>"
                    ),
                )
            )

        if highlighted_player_id is not None:
            sel_df = df_gold[df_gold["player_id"] == highlighted_player_id]
            if not sel_df.empty:
                row = sel_df.iloc[0]
                fig.add_trace(
                    go.Scatter(
                        x=[row["z_financial_cost"]],
                        y=[row["z_acp_performance"]],
                        mode="markers+text",
                        name="Jugador Seleccionado",
                        text=[f"★ {row['player_name']}"],
                        textposition="top center",
                        marker=dict(
                            size=16,
                            color=cls.PALETTE["primary_blue"],
                            symbol="diamond",
                            line=dict(width=2.5, color="#111827"),
                        ),
                    )
                )

        fig.add_hline(y=0.0, line_dash="dash", line_color="#374151", line_width=1.2)
        fig.add_vline(x=0.0, line_dash="dash", line_color="#374151", line_width=1.2)
        fig.add_shape(
            type="line",
            x0=-3.0,
            y0=-3.0,
            x1=3.0,
            y1=3.0,
            line=dict(color="#9CA3AF", width=1.0, dash="dot"),
        )

        fig.update_layout(
            title={
                "text": (
                    "<b>Mapa Estratégico de 4 Cuadrantes: Rendimiento Latente (Z_ACP) vs. Coste Financiero (Z_Coste)</b><br>"
                    "<span style='font-size:12px;color:#4B5563'>Corte Temporal de Datos (Snapshot Estático): Temporada 2023/24 – Apertura 2024/25</span>"
                ),
                "x": 0.01,
            },
            xaxis_title="Z_Coste_Financiero (60% Valor Mercado + 40% Salario Anual Bruto Estandarizado)",
            yaxis_title="Z_ACP_Rendimiento (Índice Sintético Multivariante Ponderado)",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="#FAFAFA",
            height=540,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1.0),
        )
        return fig

    @classmethod
    def build_h2h_radar_comparison(
        cls, target_row: pd.Series, clone_row: pd.Series
    ) -> go.Figure:
        """Construye un gráfico polar superpuesto Head-to-Head (Jugador Objetivo vs Clon KNN)."""
        categories = [label for _, label, _ in cls.METRIC_LABELS_ES]
        categories_closed = categories + [categories[0]]

        target_vals = [float(target_row.get(col, 50.0)) for col, _, _ in cls.METRIC_LABELS_ES]
        target_vals_closed = target_vals + [target_vals[0]]

        clone_vals = [float(clone_row.get(col, 50.0)) for col, _, _ in cls.METRIC_LABELS_ES]
        clone_vals_closed = clone_vals + [clone_vals[0]]

        fig = go.Figure()
        fig.add_trace(
            go.Scatterpolar(
                r=target_vals_closed,
                theta=categories_closed,
                fill="toself",
                name=f"Objetivo: {target_row['player_name']} (€{target_row['market_value_eur']/1e6:.1f}M)",
                line=dict(color=cls.PALETTE["primary_blue"], width=2.5),
                fillcolor="rgba(0, 114, 178, 0.22)",
            )
        )
        fig.add_trace(
            go.Scatterpolar(
                r=clone_vals_closed,
                theta=categories_closed,
                fill="toself",
                name=f"Clon KNN: {clone_row['player_name']} (€{clone_row['market_value_eur']/1e6:.1f}M)",
                line=dict(color=cls.PALETTE["reddish_purple"], width=2.5, dash="solid"),
                fillcolor="rgba(204, 121, 167, 0.22)",
            )
        )

        fig.update_layout(
            title={
                "text": (
                    f"<b>Comparativa Head-to-Head (H2H) en Percentiles Posicionales</b><br>"
                    f"<span style='font-size:12px;color:#4B5563'>"
                    f"{target_row['player_name']} ({target_row['club_name']}) vs. Sustituto KNN {clone_row['player_name']} ({clone_row['club_name']}) | Corte: 2023/24 - 2024/25</span>"
                ),
                "x": 0.02,
            },
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 100], tickvals=[20, 40, 60, 80, 100])
            ),
            paper_bgcolor="rgba(0,0,0,0)",
            height=500,
            legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5),
        )
        return fig
