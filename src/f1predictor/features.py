import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from .forecast_features import add_rolling_forecast_features

NUMERIC_FEATURES = [
    "QualiTime_s",
    "QualiGapToPole_s",
    "GridPosition",
    "LongRunPace_s",
    "TeamStrength",
    "DriverRating",
    "RecentForm",

    # Forecasting features
    "DriverElo",
    "TeamElo",
    "DNFRate",
    "AvgFinishLast5",
    "AvgQualiLast5",
    "PointsLast5",
]

CATEGORICAL_FEATURES = [
    "Driver",
    "Team",
    "GrandPrix",
]


def add_fallback_features(df: pd.DataFrame) -> pd.DataFrame:
    """Fill scientifically reasonable fallback features if unavailable.

    Real telemetry is often incomplete. We avoid dropping rows and instead impute
    missing values, while keeping the feature meanings transparent.
    """
    out = df.copy()


    if "FinishPosition" in out.columns and out["FinishPosition"].notna().any():
    try:
        out = add_rolling_forecast_features(out)
    except Exception:
        pass
        
    if "TeamStrength" not in out or out["TeamStrength"].isna().all():
        team_avg = out.groupby("Team")["FinishPosition"].transform("mean")
        out["TeamStrength"] = 1 - (team_avg - team_avg.min()) / max(team_avg.max() - team_avg.min(), 1)

    if "DriverRating" not in out or out["DriverRating"].isna().all():
        driver_avg = out.groupby("Driver")["FinishPosition"].transform("mean")
        out["DriverRating"] = 1 - (driver_avg - driver_avg.min()) / max(driver_avg.max() - driver_avg.min(), 1)

    if "LongRunPace_s" not in out or out["LongRunPace_s"].isna().all():
        # Approximation: race pace tends to be slower than qualifying pace.
        out["LongRunPace_s"] = out["QualiTime_s"] + 2.5 + out["QualiGapToPole_s"] * 0.15

    if "RecentForm" not in out or out["RecentForm"].isna().all():
        out["RecentForm"] = (
            out.sort_values(["Driver", "Round"])
            .groupby("Driver")["FinishPosition"]
            .transform(lambda s: s.shift().rolling(3, min_periods=1).mean())
        )
        out["RecentForm"] = out["RecentForm"].fillna(out["FinishPosition"].median())

    return out

defaults = {
    "DriverElo": 1500.0,
    "TeamElo": 1500.0,
    "DNFRate": 0.0,
    "AvgFinishLast5": out["RecentForm"].median() if "RecentForm" in out else 10.5,
    "AvgQualiLast5": out["GridPosition"].median() if "GridPosition" in out else 10.5,
    "PointsLast5": 0.0,
}

for col, value in defaults.items():
    if col not in out:
        out[col] = value

    out[col] = out[col].fillna(value)



def make_preprocessor() -> ColumnTransformer:
    numeric_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
        ]
    )

    categorical_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore")),
        ]
    )

    return ColumnTransformer(
        transformers=[
            ("num", numeric_pipeline, NUMERIC_FEATURES),
            ("cat", categorical_pipeline, CATEGORICAL_FEATURES),
        ]
    )


def get_feature_columns() -> list[str]:
    return NUMERIC_FEATURES + CATEGORICAL_FEATURES
