from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

try:
    import fastf1
except ImportError:  # pragma: no cover - optional telemetry dependency
    fastf1 = None

import numpy as np
import pandas as pd
import plotly.express as px
from sklearn.linear_model import LinearRegression

CACHE_DIR = Path("cache")


@dataclass(frozen=True)
class TireDegradationResult:
    driver: str
    degradation_rate: float
    compound_summary: pd.DataFrame
    laps: pd.DataFrame


def enable_fastf1_cache(cache_dir: Path = CACHE_DIR) -> None:
    if fastf1 is None:
        raise RuntimeError("FastF1 is not installed. Install fastf1 to load public session telemetry.")
    cache_dir.mkdir(parents=True, exist_ok=True)
    fastf1.Cache.enable_cache(str(cache_dir))


def _demo_tire_degradation(driver: str) -> TireDegradationResult:
    rows = []
    for lap in range(1, 19):
        tyre_life = lap
        compound = "MEDIUM" if lap <= 10 else "HARD"
        base = 91.2 if compound == "MEDIUM" else 91.8
        lap_time = base + 0.045 * tyre_life + 0.0012 * tyre_life**2
        rows.append(
            {
                "Driver": driver,
                "LapNumber": float(lap),
                "LapTimeSeconds": lap_time,
                "TyreLife": float(tyre_life),
                "Compound": compound,
                "Stint": "Demo",
            }
        )
    df = pd.DataFrame(rows)
    model = LinearRegression()
    model.fit(df[["TyreLife"]], df["LapTimeSeconds"])
    df["PredictedLapTimeSeconds"] = model.predict(df[["TyreLife"]])
    compound_summary = (
        df.groupby("Compound", as_index=False)
        .agg(
            Laps=("LapNumber", "count"),
            MeanLapTime=("LapTimeSeconds", "mean"),
            MeanTyreLife=("TyreLife", "mean"),
            BestLapTime=("LapTimeSeconds", "min"),
        )
        .round(3)
    )
    return TireDegradationResult(driver, float(model.coef_[0]), compound_summary, df.reset_index(drop=True))


def load_tire_degradation(
    year: int,
    grand_prix: str,
    session_type: str = "R",
    driver: str = "VER",
) -> TireDegradationResult:
    """Estimate tyre degradation from public FastF1 lap data or a labelled demo fallback.

    The FastF1 path uses public timing data. If FastF1 is not installed, a synthetic demo
    fallback is returned so dashboard imports and smoke tests remain lightweight. The fallback
    is clearly not official team data.
    """

    if fastf1 is None:
        return _demo_tire_degradation(driver)

    enable_fastf1_cache()
    session = fastf1.get_session(year, grand_prix, session_type)
    session.load(laps=True, telemetry=False, weather=False, messages=False)

    laps = session.laps.pick_drivers(driver)
    laps = laps[laps["LapTime"].notna() & laps["TyreLife"].notna()].copy()

    if laps.empty:
        raise ValueError(f"No valid race laps found for {driver} in {grand_prix} {year}.")

    df = pd.DataFrame(
        {
            "Driver": driver,
            "LapNumber": laps["LapNumber"].astype(float),
            "LapTimeSeconds": laps["LapTime"].dt.total_seconds(),
            "TyreLife": laps["TyreLife"].astype(float),
            "Compound": laps["Compound"].astype(str),
            "Stint": laps["Stint"].astype(str) if "Stint" in laps.columns else "Unknown",
        }
    )

    median_lap = df["LapTimeSeconds"].median()
    df = df[df["LapTimeSeconds"] < median_lap + 5].copy()

    if len(df) < 3:
        raise ValueError("Not enough clean laps to estimate degradation.")

    model = LinearRegression()
    model.fit(df[["TyreLife"]], df["LapTimeSeconds"])
    df["PredictedLapTimeSeconds"] = model.predict(df[["TyreLife"]])

    compound_summary = (
        df.groupby("Compound", as_index=False)
        .agg(
            Laps=("LapNumber", "count"),
            MeanLapTime=("LapTimeSeconds", "mean"),
            MeanTyreLife=("TyreLife", "mean"),
            BestLapTime=("LapTimeSeconds", "min"),
        )
        .round(3)
    )

    return TireDegradationResult(
        driver=driver,
        degradation_rate=float(model.coef_[0]),
        compound_summary=compound_summary,
        laps=df.reset_index(drop=True),
    )


def plot_degradation(result: TireDegradationResult):
    fig = px.scatter(
        result.laps,
        x="TyreLife",
        y="LapTimeSeconds",
        color="Compound",
        hover_data=["LapNumber", "Stint"],
        title=f"{result.driver} tyre degradation: {result.degradation_rate:.3f} s/lap",
    )
    fig.add_scatter(
        x=result.laps["TyreLife"],
        y=result.laps["PredictedLapTimeSeconds"],
        mode="lines",
        name="Linear degradation fit",
    )
    fig.update_layout(xaxis_title="Tyre age (laps)", yaxis_title="Lap time (s)")
    return fig


def detect_tire_cliff(result: TireDegradationResult) -> pd.DataFrame:
    """Flag laps where lap time is unusually slower than the model trend."""

    df = result.laps.copy()
    residual = df["LapTimeSeconds"] - df["PredictedLapTimeSeconds"]
    threshold = max(1.0, float(np.nanstd(residual)) * 1.25)
    df["ResidualSeconds"] = residual.round(3)
    df["PotentialCliff"] = df["ResidualSeconds"] > threshold
    return df[
        [
            "LapNumber",
            "Compound",
            "TyreLife",
            "LapTimeSeconds",
            "PredictedLapTimeSeconds",
            "ResidualSeconds",
            "PotentialCliff",
        ]
    ]
