from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

try:
    import fastf1
except ImportError:  # pragma: no cover - optional telemetry dependency
    fastf1 = None

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

    if fastf1 is None:
        raise RuntimeError("FastF1 is not installed. Install fastf1 to load public telemetry.")
    cache_dir.mkdir(parents=True, exist_ok=True)
    fastf1.Cache.enable_cache(str(cache_dir))


def _lap_time_to_seconds(value) -> float | None:
    if pd.isna(value):
        return None
    try:
        return float(value.total_seconds())
    except AttributeError:
        return None


def _demo_telemetry(driver: str) -> DriverTelemetry:
    distance = list(range(0, 5200, 100))
    offset = (sum(ord(char) for char in driver) % 7) * 0.7
    telemetry = pd.DataFrame(
        {
            "Distance": distance,
            "Speed": [285 - 35 * ((idx % 13) / 13) + offset for idx, _ in enumerate(distance)],
            "Throttle": [100 if idx % 9 > 2 else 48 for idx, _ in enumerate(distance)],
            "Brake": [idx % 9 <= 2 for idx, _ in enumerate(distance)],
            "nGear": [max(1, min(8, 3 + (idx % 8))) for idx, _ in enumerate(distance)],
            "DRS": [idx % 17 > 11 for idx, _ in enumerate(distance)],
            "RPM": [10500 + (idx % 10) * 220 for idx, _ in enumerate(distance)],
        }
    )
    return DriverTelemetry(driver=driver, lap_time_seconds=91.2 + offset / 10, compound="DEMO", telemetry=telemetry)


def load_fastest_lap_telemetry(
    year: int,
    grand_prix: str,
    session_type: str,
    driver: str,
) -> DriverTelemetry:
    """Load fastest-lap telemetry from FastF1 or return a labelled demo fallback.

    FastF1 is optional so importing dashboard modules remains lightweight in CI and Streamlit
    Cloud. The fallback is synthetic and must not be interpreted as official telemetry.
    """

    if fastf1 is None:
        return _demo_telemetry(driver)

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
    telemetry = telemetry[
        [column for column in ["Distance", "Speed", "Throttle", "Brake", "nGear", "DRS", "RPM"] if column in telemetry.columns]
    ].copy()

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
