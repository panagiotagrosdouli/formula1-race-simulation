from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


@dataclass(frozen=True)
class GridSimulationResult:
    starting_grid: pd.DataFrame
    lap_by_lap: pd.DataFrame
    final_order: pd.DataFrame


def build_starting_grid(predictions: pd.DataFrame) -> pd.DataFrame:
    df = predictions.copy()

    if "GridPosition" not in df.columns:
        if "PredictedRank" in df.columns:
            df["GridPosition"] = df["PredictedRank"]
        else:
            df["GridPosition"] = np.arange(1, len(df) + 1)

    grid_cols = [c for c in ["Driver", "Team", "GridPosition", "PredictedRank", "PredictedFinishPosition"] if c in df.columns]
    grid = df[grid_cols].sort_values("GridPosition").reset_index(drop=True)
    grid["GridSlot"] = np.arange(1, len(grid) + 1)
    grid["GridRow"] = ((grid["GridSlot"] - 1) // 2) + 1
    grid["GridSide"] = np.where(grid["GridSlot"] % 2 == 1, "Left", "Right")
    grid["X"] = np.where(grid["GridSide"] == "Left", -0.35, 0.35)
    grid["Y"] = -grid["GridRow"]
    return grid


def simulate_lap_by_lap_order(
    predictions: pd.DataFrame,
    total_laps: int = 20,
    random_state: int = 42,
    volatility: float = 0.18,
) -> GridSimulationResult:
    rng = np.random.default_rng(random_state)
    grid = build_starting_grid(predictions)

    rows = []
    base_order = grid.copy()

    for lap in range(0, total_laps + 1):
        progress = lap / max(total_laps, 1)
        lap_df = base_order.copy()

        target = lap_df.get("PredictedRank", lap_df["GridPosition"]).astype(float)
        start = lap_df["GridPosition"].astype(float)
        noise = rng.normal(0, volatility * (1.0 - progress + 0.2), size=len(lap_df))

        lap_df["RaceScore"] = (1 - progress) * start + progress * target + noise
        lap_df["RacePosition"] = lap_df["RaceScore"].rank(method="first").astype(int)
        lap_df["Lap"] = lap
        lap_df["Progress"] = progress
        lap_df["TrackX"] = np.cos(2 * np.pi * progress - lap_df["RacePosition"] * 0.035)
        lap_df["TrackY"] = np.sin(2 * np.pi * progress - lap_df["RacePosition"] * 0.035)
        lap_df["GapProxy"] = (lap_df["RacePosition"] - 1).astype(float) * 1.2
        rows.append(lap_df)

    lap_by_lap = pd.concat(rows, ignore_index=True)
    final_order = (
        lap_by_lap[lap_by_lap["Lap"] == total_laps]
        .sort_values("RacePosition")
        .reset_index(drop=True)
    )
    return GridSimulationResult(starting_grid=grid, lap_by_lap=lap_by_lap, final_order=final_order)


def plot_starting_grid(grid: pd.DataFrame):
    fig = px.scatter(
        grid,
        x="X",
        y="Y",
        text="Driver",
        hover_data=[c for c in ["Team", "GridPosition", "PredictedRank"] if c in grid.columns],
        title="Starting grid layout",
    )
    fig.update_traces(marker_size=24, textposition="middle center")
    fig.update_layout(
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        showlegend=False,
        height=700,
    )
    return fig


def plot_race_animation(simulation: GridSimulationResult):
    df = simulation.lap_by_lap.copy()
    fig = px.scatter(
        df,
        x="TrackX",
        y="TrackY",
        animation_frame="Lap",
        text="Driver",
        hover_data=[c for c in ["Team", "GridPosition", "RacePosition", "PredictedRank"] if c in df.columns],
        title="Virtual race order simulation",
        range_x=[-1.25, 1.25],
        range_y=[-1.25, 1.25],
    )
    fig.update_traces(marker_size=22, textposition="top center")
    fig.update_layout(
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        height=700,
    )
    return fig


def plot_position_evolution(simulation: GridSimulationResult):
    df = simulation.lap_by_lap.copy()
    fig = go.Figure()

    for driver, driver_df in df.groupby("Driver"):
        fig.add_trace(
            go.Scatter(
                x=driver_df["Lap"],
                y=driver_df["RacePosition"],
                mode="lines+markers",
                name=driver,
            )
        )

    fig.update_layout(
        title="Lap-by-lap position evolution",
        xaxis_title="Lap",
        yaxis_title="Race position",
        yaxis_autorange="reversed",
        hovermode="x unified",
    )
    return fig
