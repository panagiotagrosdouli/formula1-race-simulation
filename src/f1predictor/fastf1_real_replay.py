from __future__ import annotations

from pathlib import Path

import pandas as pd


def load_fastf1_session_summary(
    year: int,
    gp: str | int,
    session_name: str = "R",
) -> dict[str, pd.DataFrame | str]:
    """
    Load a real FastF1 session safely.

    This version:
    - creates the FastF1 cache folder automatically
    - loads laps first
    - avoids telemetry/weather/messages until the basic loader works
    - fails gracefully on Streamlit Cloud
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
        cache_dir = Path.home() / ".fastf1-cache"
        cache_dir.mkdir(parents=True, exist_ok=True)

        fastf1.Cache.enable_cache(str(cache_dir))

        session = fastf1.get_session(
            int(year),
            gp,
            session_name,
        )

        session.load(
            laps=True,
            telemetry=False,
            weather=False,
            messages=False,
        )

        laps = session.laps.copy()

        try:
            results = session.results.copy()
        except Exception:
            results = pd.DataFrame()

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
            col for col in columns
            if col in laps.columns
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
            "status": "Loaded real FastF1 laps successfully",
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
