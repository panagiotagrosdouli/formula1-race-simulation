from __future__ import annotations

import pandas as pd


def load_fastf1_session_summary(year: int, gp: str | int, session_name: str = "R") -> dict[str, pd.DataFrame | str]:
    """Load a real FastF1 session if FastF1 is installed.

    The function is intentionally defensive so Streamlit Cloud can still run when
    FastF1 cache/network access is unavailable. It returns either real dataframes
    or an explanatory fallback message.
    """
    try:
        import fastf1
    except Exception as exc:
        return {"status": f"FastF1 unavailable: {exc}", "laps": pd.DataFrame(), "results": pd.DataFrame(), "telemetry": pd.DataFrame()}

    try:
        fastf1.Cache.enable_cache(".fastf1-cache")
        session = fastf1.get_session(int(year), gp, session_name)
        session.load(laps=True, telemetry=True, weather=True, messages=True)
        laps = session.laps.copy()
        results = session.results.copy() if getattr(session, "results", None) is not None else pd.DataFrame()
        cols = [c for c in ["Driver", "LapNumber", "LapTime", "Sector1Time", "Sector2Time", "Sector3Time", "Compound", "TyreLife", "Stint", "PitOutTime", "PitInTime"] if c in laps.columns]
        lap_summary = laps[cols].copy() if cols else pd.DataFrame()
        for col in ["LapTime", "Sector1Time", "Sector2Time", "Sector3Time", "PitOutTime", "PitInTime"]:
            if col in lap_summary.columns:
                lap_summary[col] = lap_summary[col].astype(str)
        return {"status": "Loaded real FastF1 session", "laps": lap_summary, "results": results, "telemetry": pd.DataFrame()}
    except Exception as exc:
        return {"status": f"FastF1 load failed: {exc}", "laps": pd.DataFrame(), "results": pd.DataFrame(), "telemetry": pd.DataFrame()}
