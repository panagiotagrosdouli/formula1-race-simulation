from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import fastf1
import pandas as pd
import plotly.graph_objects as go

CACHE_DIR = Path("cache")


@dataclass(frozen=True)
class DriverTelemetry:
    """Container for one driver's fastest-lap telemetry."""

    driver: str
    lap_time_seconds: float | None
    compound: str | None
    telemetry: pd.DataFrame


def enable_fastf1_cache(cache_dir: Path = CACHE_DIR) -> None:
    """Enable FastF1 caching in a repository-local folder."""

    cache_dir.mkdir(parents=True, exist_ok=True)
    fastf1.Cache.enable_cache(str(cache_dir))


def _lap_time_to_seconds(value) -> float | None:
    if pd.isna(value):
        return None
    try:
        return float(value.total_seconds())
    except AttributeError:
        return None


def load_fastest_lap_telemetry(
    year: int,
    grand_prix: str,
    session_type: str,
    driver: str,
) -> DriverTelemetry:
    """Load fastest-lap telemetry for a selected driver and session.

    Parameters
    ----------
    year:
        Formula 1 season year.
    grand_prix:
        Event name accepted by FastF1, e.g. "Monza" or "British Grand Prix".
    session_type:
        FastF1 session code, usually "Q", "R", "S", or "SQ".
    driver:
        Three-letter driver abbreviation, e.g. "VER".
    """

    enable_fastf1_cache()
    session = fastf1.get_session(year, grand_prix, session_type)
    session.load(laps=True, telemetry=True, weather=False, messages=False)

    laps = session.laps.pick_drivers(driver)
    if laps.empty:
        raise ValueError(f"No laps found for driver {driver} in {grand_prix} {year} {session_type}.")

    fastest_lap = laps.pick_fastest()
    if fastest_lap is None:
        raise ValueError(f"Could not identify fastest lap for driver {driver}.")

    telemetry = fastest_lap.get_car_data().add_distance()
    telemetry = telemetry[[c for c in ["Distance", "Speed", "Throttle", "Brake", "nGear", "DRS", "RPM"] if c in telemetry.columns]].copy()

    return DriverTelemetry(
        driver=driver,
        lap_time_seconds=_lap_time_to_seconds(fastest_lap.get("LapTime")),
        compound=fastest_lap.get("Compound") if "Compound" in fastest_lap.index else None,
        telemetry=telemetry,
    )


def compare_driver_speed_trace(driver_a: DriverTelemetry, driver_b: DriverTelemetry) -> go.Figure:
    """Build an interactive speed-over-distance comparison chart."""

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=driver_a.telemetry["Distance"],
            y=driver_a.telemetry["Speed"],
            mode="lines",
            name=driver_a.driver,
        )
    )
    fig.add_trace(
        go.Scatter(
            x=driver_b.telemetry["Distance"],
            y=driver_b.telemetry["Speed"],
            mode="lines",
            name=driver_b.driver,
        )
    )
    fig.update_layout(
        title="Fastest-lap speed trace comparison",
        xaxis_title="Distance (m)",
        yaxis_title="Speed (km/h)",
        hovermode="x unified",
    )
    return fig


def compare_driver_controls(driver_a: DriverTelemetry, driver_b: DriverTelemetry, channel: str) -> go.Figure:
    """Build an interactive comparison chart for throttle, brake, gear, DRS, or RPM."""

    if channel not in driver_a.telemetry.columns or channel not in driver_b.telemetry.columns:
        raise ValueError(f"Telemetry channel '{channel}' is not available for both drivers.")

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=driver_a.telemetry["Distance"],
            y=driver_a.telemetry[channel],
            mode="lines",
            name=f"{driver_a.driver} {channel}",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=driver_b.telemetry["Distance"],
            y=driver_b.telemetry[channel],
            mode="lines",
            name=f"{driver_b.driver} {channel}",
        )
    )
    fig.update_layout(
        title=f"{channel} comparison over lap distance",
        xaxis_title="Distance (m)",
        yaxis_title=channel,
        hovermode="x unified",
    )
    return fig
