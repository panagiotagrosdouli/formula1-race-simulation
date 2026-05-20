import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline


NUMERIC_FEATURES = [
    "QualiTime_s",
    "QualiGapToPole_s",
    "GridPosition",
    "LongRunPace_s",
    "TeamStrength",
    "DriverRating",
    "RecentForm",
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
