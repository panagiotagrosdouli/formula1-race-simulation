"""Telemetry and public-data integration scaffolds."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

REQUIRED_LAP_COLUMNS = {"driver_id", "lap", "lap_time_s"}


def load_lap_csv(path: str | Path) -> pd.DataFrame:
    """Load validated lap-time CSV input."""

    frame = pd.read_csv(path)
    missing = REQUIRED_LAP_COLUMNS.difference(frame.columns)
    if missing:
        raise ValueError(f"Missing required lap CSV columns: {sorted(missing)}")
    return frame


def normalize_lap_times(frame: pd.DataFrame) -> pd.DataFrame:
    """Normalize lap times by each driver's median clean pace."""

    output = frame.copy()
    medians = output.groupby("driver_id")["lap_time_s"].transform("median")
    output["normalized_lap_time_s"] = output["lap_time_s"] - medians
    return output


def estimate_driver_pace(frame: pd.DataFrame) -> pd.DataFrame:
    """Estimate driver pace from public or user-provided lap data."""

    normalized = normalize_lap_times(frame)
    return (
        normalized.groupby("driver_id", as_index=False)
        .agg(base_pace_s=("lap_time_s", "median"), pace_spread_s=("normalized_lap_time_s", "std"))
        .fillna({"pace_spread_s": 0.0})
    )


class FastF1Loader:
    """FastF1 integration scaffold.

    This class intentionally does not fabricate data. Users must enable FastF1 and accept its
    availability/cache limitations before loading public timing sessions.
    """

    def load_session(self, year: int, event: str, session: str):  # pragma: no cover - optional dep
        try:
            import fastf1  # type: ignore
        except ImportError as exc:
            raise RuntimeError("Install f1sim[telemetry] to use FastF1 integration") from exc
        f1_session = fastf1.get_session(year, event, session)
        f1_session.load()
        return f1_session


class OpenF1Loader:
    """OpenF1 integration scaffold for future HTTP-backed loaders."""

    base_url = "https://api.openf1.org/v1"

    def describe(self) -> str:
        """Return a transparent integration status."""

        return "OpenF1 loader scaffold: implement endpoint-specific retrieval with source citation."
