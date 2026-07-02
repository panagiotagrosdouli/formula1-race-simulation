from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go

APP_TITLE = "F1 Race Engineering Intelligence"
FERRARI_RED = "#dc2626"
FERRARI_DARK_RED = "#991b1b"
TEXT = "#f9fafb"
BORDER = "rgba(255,255,255,0.12)"
PLOT_PALETTE = [
    FERRARI_RED,
    "#ef4444",
    "#f97316",
    "#f59e0b",
    "#22c55e",
    "#06b6d4",
    "#3b82f6",
]

RACE_OPTIONS_2026 = [
    "Australian Grand Prix 2026",
    "Chinese Grand Prix 2026",
    "Japanese Grand Prix 2026",
    "Bahrain Grand Prix 2026",
    "Saudi Arabian Grand Prix 2026",
    "Miami Grand Prix 2026",
    "Monaco Grand Prix 2026",
    "Canadian Grand Prix 2026",
    "Spanish Grand Prix 2026",
    "Austrian Grand Prix 2026",
    "British Grand Prix 2026",
    "Belgian Grand Prix 2026",
    "Hungarian Grand Prix 2026",
    "Italian Grand Prix 2026",
    "Singapore Grand Prix 2026",
    "United States Grand Prix 2026",
    "Mexico City Grand Prix 2026",
    "São Paulo Grand Prix 2026",
    "Las Vegas Grand Prix 2026",
    "Qatar Grand Prix 2026",
    "Abu Dhabi Grand Prix 2026",
]

PAGES = [
    "Command Centre",
    "Race Forecast",
    "Model Lab",
    "Season Simulator",
    "FastF1 Training",
    "Telemetry",
    "Tyre Strategy",
    "Diagnostics",
]

PREDICTION_COLUMNS = [
    "PredictedRank",
    "Driver",
    "Team",
    "PredictedFinishPosition",
    "GridPosition",
    "QualiGapToPole_s",
    "LongRunPace_s",
    "TeamStrength",
    "DriverRating",
    "RecentForm",
    "RainProbability",
    "SafetyCarProbability",
    "DNFRisk",
    "RiskAdjustment",
]

PROBABILITY_COLUMNS = ["WinProbability", "PodiumProbability", "Top10Probability"]


def apply_plot_theme(fig: go.Figure) -> go.Figure:
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(5, 7, 13, 0)",
        plot_bgcolor="rgba(17, 24, 39, 0.92)",
        font={"color": TEXT, "family": "Arial, sans-serif"},
        title={"font": {"color": TEXT, "size": 18}},
        margin={"l": 20, "r": 20, "t": 55, "b": 35},
        colorway=PLOT_PALETTE,
    )
    fig.update_xaxes(
        gridcolor="rgba(255,255,255,0.08)",
        zerolinecolor=BORDER,
        linecolor="rgba(255,255,255,0.18)",
    )
    fig.update_yaxes(
        gridcolor="rgba(255,255,255,0.08)",
        zerolinecolor=BORDER,
        linecolor="rgba(255,255,255,0.18)",
    )
    return fig


def select_existing(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    selected = [col for col in columns if col in df.columns]
    return df[selected].copy() if selected else df.copy()


def prediction_view(df: pd.DataFrame) -> pd.DataFrame:
    return select_existing(df, PREDICTION_COLUMNS)


def probability_view(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for col in PROBABILITY_COLUMNS:
        if col in out.columns:
            out[col] = (pd.to_numeric(out[col], errors="coerce") * 100).round(2)
    return out
