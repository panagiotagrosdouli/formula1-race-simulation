"""Interactive telemetry utilities for the F1 Intelligence Platform.

This module uses FastF1 when available and falls back to synthetic telemetry so
that the project remains runnable offline or when session data cannot be fetched.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Tuple

import numpy as np
import pandas as pd
import plotly.graph_objects as go


CACHE_DIR = Path("cache")
CACHE_DIR.mkdir(exist_ok=True)


@dataclass
class TelemetryRequest:
    year: int = 2024
    grand_prix: str = "Monza"
    session_type: str = "Q"
    driver_a: str = "VER"
    driver_b: str = "LEC"


def _synthetic_driver_trace(driver: str, seed: int = 1) -> pd.DataFrame:
    rng = np.random.default_rng(abs(hash(driver)) % (2**32) + seed)
    distance = np.linspace(0, 5800, 700)
    corner_wave = 55 * np.maximum(0, np.sin(distance / 290))
    speed = 315 - corner_wave + rng.normal(0, 2.0, distance.size)
    throttle = np.clip(100 - 1.2 * corner_wave + rng.normal(0, 3.0, distance.size), 0, 100)
    brake = np.clip(corner_wave * 1.3 + rng.normal(0, 4.0, distance.size), 0, 100)
    gear = np.clip(np.round(speed / 45), 1, 8).astype(int)
    x = distance
    y = 450 * np.sin(distance / 620) + 150 * np.sin(distance / 180)
    return pd.DataFrame({
        "Driver": driver,
        "Distance": distance,
        "Speed": speed,
        "Throttle": throttle,
        "Brake": brake,
        "nGear": gear,
        "X": x,
        "Y": y,
    })


def load_fastf1_telemetry(req: TelemetryRequest) -> Tuple[pd.DataFrame, pd.DataFrame, str]:
    """Load fastest-lap car telemetry for two drivers.

    Returns two dataframes and a source label. If FastF1/session loading fails,
    synthetic telemetry is returned so that dashboards remain demoable.
    """
    try:
        import fastf1

        fastf1.Cache.enable_cache(str(CACHE_DIR))
        session = fastf1.get_session(req.year, req.grand_prix, req.session_type)
        session.load(laps=True, telemetry=True, weather=False, messages=False)
        lap_a = session.laps.pick_drivers(req.driver_a).pick_fastest()
        lap_b = session.laps.pick_drivers(req.driver_b).pick_fastest()
        tel_a = lap_a.get_car_data().add_distance()
        tel_b = lap_b.get_car_data().add_distance()
        tel_a["Driver"] = req.driver_a
        tel_b["Driver"] = req.driver_b

        # Position data is not always available in car_data; merge if possible.
        try:
            pos_a = lap_a.get_pos_data().add_distance()[["Distance", "X", "Y"]]
            pos_b = lap_b.get_pos_data().add_distance()[["Distance", "X", "Y"]]
            tel_a = pd.merge_asof(tel_a.sort_values("Distance"), pos_a.sort_values("Distance"), on="Distance")
            tel_b = pd.merge_asof(tel_b.sort_values("Distance"), pos_b.sort_values("Distance"), on="Distance")
        except Exception:
            tel_a["X"] = tel_a["Distance"]
            tel_a["Y"] = np.sin(tel_a["Distance"] / 500) * 100
            tel_b["X"] = tel_b["Distance"]
            tel_b["Y"] = np.sin(tel_b["Distance"] / 500) * 100

        return tel_a, tel_b, "FastF1"
    except Exception:
        return _synthetic_driver_trace(req.driver_a), _synthetic_driver_trace(req.driver_b), "Synthetic demo fallback"


def make_speed_trace(tel_a: pd.DataFrame, tel_b: pd.DataFrame, driver_a: str, driver_b: str) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=tel_a["Distance"], y=tel_a["Speed"], mode="lines", name=f"{driver_a} speed"))
    fig.add_trace(go.Scatter(x=tel_b["Distance"], y=tel_b["Speed"], mode="lines", name=f"{driver_b} speed"))
    fig.update_layout(title="Speed trace comparison", xaxis_title="Distance (m)", yaxis_title="Speed (km/h)")
    return fig


def make_controls_trace(tel: pd.DataFrame, driver: str) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=tel["Distance"], y=tel["Throttle"], mode="lines", name="Throttle %"))
    fig.add_trace(go.Scatter(x=tel["Distance"], y=tel["Brake"], mode="lines", name="Brake %"))
    fig.add_trace(go.Scatter(x=tel["Distance"], y=tel["nGear"] * 12.5, mode="lines", name="Gear scaled"))
    fig.update_layout(title=f"Driver controls — {driver}", xaxis_title="Distance (m)", yaxis_title="Scaled value")
    return fig


def make_delta_trace(tel_a: pd.DataFrame, tel_b: pd.DataFrame, driver_a: str, driver_b: str) -> go.Figure:
    grid = np.linspace(0, min(tel_a["Distance"].max(), tel_b["Distance"].max()), 600)
    sp_a = np.interp(grid, tel_a["Distance"], tel_a["Speed"])
    sp_b = np.interp(grid, tel_b["Distance"], tel_b["Speed"])
    delta_proxy = np.cumsum((1 / np.maximum(sp_a, 1) - 1 / np.maximum(sp_b, 1))) * np.mean(np.diff(grid)) * 3.6
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=grid, y=delta_proxy, mode="lines", name=f"{driver_a} vs {driver_b}"))
    fig.update_layout(title="Delta-time proxy from speed traces", xaxis_title="Distance (m)", yaxis_title="Approx. delta (s)")
    return fig


def make_track_map(tel_a: pd.DataFrame, driver: str) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=tel_a["X"], y=tel_a["Y"], mode="markers",
        marker={"size": 5, "color": tel_a["Speed"], "colorscale": "Viridis", "showscale": True, "colorbar": {"title": "km/h"}},
        name=driver,
    ))
    fig.update_layout(title=f"Track map speed heatmap — {driver}", xaxis_title="X", yaxis_title="Y", yaxis_scaleanchor="x")
    return fig
