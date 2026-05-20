"""Advanced race strategy simulator with undercut/overcut analysis."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
import plotly.graph_objects as go


@dataclass(frozen=True)
class TireModel:
    base_lap_time: float
    linear_deg: float
    quadratic_deg: float
    cliff_lap: int
    cliff_penalty: float
    max_life: int


TIRE_MODELS: Dict[str, TireModel] = {
    "SOFT": TireModel(88.20, 0.070, 0.0018, 16, 0.30, 22),
    "MEDIUM": TireModel(88.85, 0.045, 0.0010, 28, 0.18, 36),
    "HARD": TireModel(89.45, 0.027, 0.0006, 40, 0.12, 52),
}


def lap_time(compound: str, tire_age: int, fuel_lap: int, fuel_effect: float = 0.035) -> float:
    t = TIRE_MODELS[compound]
    deg = t.linear_deg * tire_age + t.quadratic_deg * (tire_age ** 2)
    cliff = max(0, tire_age - t.cliff_lap) * t.cliff_penalty
    fuel_gain = fuel_effect * fuel_lap
    return t.base_lap_time + deg + cliff - fuel_gain


def simulate_strategy(strategy: List[Tuple[str, int]], pit_loss: float = 22.5) -> Tuple[float, pd.DataFrame]:
    rows = []
    global_lap = 1
    for stint_idx, (compound, stint_laps) in enumerate(strategy, start=1):
        for tire_age in range(stint_laps):
            rows.append({
                "Lap": global_lap,
                "Stint": stint_idx,
                "Compound": compound,
                "TireAge": tire_age,
                "LapTime": lap_time(compound, tire_age, global_lap),
            })
            global_lap += 1
    df = pd.DataFrame(rows)
    total = df["LapTime"].sum() + (len(strategy) - 1) * pit_loss
    return float(total), df


def enumerate_one_stop(total_laps: int = 53) -> pd.DataFrame:
    rows = []
    for c1, c2 in product(TIRE_MODELS.keys(), repeat=2):
        if c1 == c2:
            continue
        for pit_lap in range(8, total_laps - 8):
            strat = [(c1, pit_lap), (c2, total_laps - pit_lap)]
            total, _ = simulate_strategy(strat)
            rows.append({"Strategy": f"{c1}-{c2}", "PitLap": pit_lap, "TotalRaceTime": total})
    return pd.DataFrame(rows).sort_values("TotalRaceTime")


def undercut_gain(old_compound: str, new_compound: str, old_tire_age: int, outlap_penalty: float = 1.5) -> float:
    old_next = lap_time(old_compound, old_tire_age + 1, fuel_lap=25)
    fresh_next = lap_time(new_compound, 1, fuel_lap=25) + outlap_penalty
    return old_next - fresh_next


def make_strategy_figure(strategies: Dict[str, List[Tuple[str, int]]]) -> go.Figure:
    fig = go.Figure()
    for name, strat in strategies.items():
        _, df = simulate_strategy(strat)
        fig.add_trace(go.Scatter(x=df["Lap"], y=df["LapTime"], mode="lines", name=name))
    fig.update_layout(title="Race strategy lap-time evolution", xaxis_title="Lap", yaxis_title="Lap time (s)")
    return fig


def make_pit_window_figure(total_laps: int = 53) -> Tuple[pd.DataFrame, go.Figure]:
    results = enumerate_one_stop(total_laps)
    fig = go.Figure()
    for strategy in results["Strategy"].unique():
        sub = results[results["Strategy"] == strategy]
        fig.add_trace(go.Scatter(x=sub["PitLap"], y=sub["TotalRaceTime"], mode="lines", name=strategy))
    fig.update_layout(title="One-stop pit window optimizer", xaxis_title="Pit lap", yaxis_title="Total race time (s)")
    return results, fig
