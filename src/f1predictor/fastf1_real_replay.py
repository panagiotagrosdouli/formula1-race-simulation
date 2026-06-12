from __future__ import annotations

from pathlib import Path

import pandas as pd


def load_fastf1_session_summary(
    year: int,
    gp: str | int,
    session_name: str = "R"
) -> dict[str, pd.DataFrame | str]:
    """
    Load a real FastF1 session if FastF1 is available.

    Works both locally and on Streamlit Cloud by automatically
    creating a cache directory if it does not exist.
    """

    try:
        import fastf1
    except Exception as exc:
        return {
            "status": f"FastF1 unavailable: {exc}",
            "laps": pd.DataFrame(),
            "results": pd.DataFrame(),
            "telemetry": pd.DataFrame(),
        }

    try:
        # Create cache folder automatically
        cache_dir = Path.home() / ".fastf1-cache"
        cache_dir.mkdir(parents=True, exist_ok=True)

        fastf1.Cache.enable_cache(str(cache_dir))

        session = fastf1.get_session(
            int(year),
            gp,
            session_name
        )

        session.load(
            laps=True,
            telemetry=True,
            weather=True,
            messages=True
        )

        laps = session.laps.copy()

        results = (
            session.results.copy()
            if getattr(session, "results", None) is not None
            else pd.DataFrame()
        )

        columns = [
            "Driver",
            "LapNumber",
            "LapTime",
            "Sector1Time",
            "Sector2Time",
            "Sector3Time",
            "Compound",
            "TyreLife",
            "Stint",
            "PitOutTime",
            "PitInTime",
        ]

        available_columns = [
            c for c in columns
            if c in laps.columns
        ]

        lap_summary = (
            laps[available_columns].copy()
            if available_columns
            else pd.DataFrame()
        )

        time_columns = [
            "LapTime",
            "Sector1Time",
            "Sector2Time",
            "Sector3Time",
            "PitOutTime",
            "PitInTime",
        ]

        for col in time_columns:
            if col in lap_summary.columns:
                lap_summary[col] = lap_summary[col].astype(str)

        return {
            "status": "Loaded real FastF1 session",
            "laps": lap_summary,
            "results": results,
            "telemetry": pd.DataFrame(),
        }

    except Exception as exc:
        return {
            "status": f"FastF1 load failed: {exc}",
            "laps": pd.DataFrame(),
            "results": pd.DataFrame(),
            "telemetry": pd.DataFrame(),
        }
