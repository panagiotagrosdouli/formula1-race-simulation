import numpy as np
import pandas as pd

from .elo import compute_pre_race_elo


F1_POINTS = {
    1: 25,
    2: 18,
    3: 15,
    4: 12,
    5: 10,
    6: 8,
    7: 6,
    8: 4,
    9: 2,
    10: 1,
}


def _points_from_finish(pos) -> float:
    try:
        pos = int(pos)
    except Exception:
        return 0.0
    return float(F1_POINTS.get(pos, 0))


def add_rolling_forecast_features(df: pd.DataFrame) -> pd.DataFrame:
    out = df.sort_values(["Round", "Driver"]).copy()

    out["RacePoints"] = out["FinishPosition"].apply(_points_from_finish)

    out = compute_pre_race_elo(
        out,
        entity_col="Driver",
        round_col="Round",
        finish_col="FinishPosition",
        rating_col="DriverElo",
        k=16,
        initial_rating=1500,
    )

    out = compute_pre_race_elo(
        out,
        entity_col="Team",
        round_col="Round",
        finish_col="FinishPosition",
        rating_col="TeamElo",
        k=10,
        initial_rating=1500,
    )

    out = out.sort_values(["Driver", "Round"])

    out["AvgFinishLast5"] = (
        out.groupby("Driver")["FinishPosition"]
        .transform(lambda s: s.shift().rolling(5, min_periods=1).mean())
    )

    out["AvgQualiLast5"] = (
        out.groupby("Driver")["GridPosition"]
        .transform(lambda s: s.shift().rolling(5, min_periods=1).mean())
    )

    out["PointsLast5"] = (
        out.groupby("Driver")["RacePoints"]
        .transform(lambda s: s.shift().rolling(5, min_periods=1).sum())
    )

    out["DNFProxy"] = (pd.to_numeric(out["FinishPosition"], errors="coerce") >= 20).astype(float)

    out["DNFRate"] = (
        out.groupby("Driver")["DNFProxy"]
        .transform(lambda s: s.shift().rolling(8, min_periods=1).mean())
    )

    out["AvgFinishLast5"] = out["AvgFinishLast5"].fillna(out["FinishPosition"].median())
    out["AvgQualiLast5"] = out["AvgQualiLast5"].fillna(out["GridPosition"].median())
    out["PointsLast5"] = out["PointsLast5"].fillna(0.0)
    out["DNFRate"] = out["DNFRate"].fillna(0.0)

    return out.sort_values(["Round", "Driver"]).reset_index(drop=True)


def build_future_race_frame(
    history_df: pd.DataFrame,
    race_name: str,
    year: int = 2026,
    round_no: int | None = None,
) -> pd.DataFrame:
    hist = add_rolling_forecast_features(history_df)

    latest = (
        hist.sort_values(["Round", "Driver"])
        .groupby("Driver")
        .tail(1)
        .copy()
        .reset_index(drop=True)
    )

    if round_no is None:
        round_no = int(hist["Round"].max()) + 1

    future = latest.copy()
    future["Year"] = year
    future["Round"] = round_no
    future["GrandPrix"] = race_name
    future["FinishPosition"] = np.nan

    future["GridPosition"] = future["AvgQualiLast5"].round().clip(1, len(future))
    future["QualiGapToPole_s"] = (future["GridPosition"].astype(float) - 1.0) * 0.075

    base_quali = pd.to_numeric(hist["QualiTime_s"], errors="coerce").median()
    future["QualiTime_s"] = base_quali + future["QualiGapToPole_s"]

    base_long_run = pd.to_numeric(hist["LongRunPace_s"], errors="coerce").median()
    future["LongRunPace_s"] = base_long_run + future["QualiGapToPole_s"] * 0.20

    future["RecentForm"] = future["AvgFinishLast5"]

    return future
