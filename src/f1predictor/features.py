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
    "DriverElo",
    "TeamElo",
    "DNFRate",
    "AvgFinishLast5",
    "AvgQualiLast5",
    "PointsLast5",
    "AirTemperature",
    "RainProbability",
    "WindSpeed",
    "Humidity",
]

CATEGORICAL_FEATURES = [
    "Driver",
    "Team",
    "GrandPrix",
    "WeatherCondition",
]


def add_fallback_features(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()

    if "FinishPosition" in out.columns and out["FinishPosition"].notna().any():
        try:
            out = add_rolling_forecast_features(out)
        except Exception:
            pass

    if "TeamStrength" not in out or out["TeamStrength"].isna().all():
        if "FinishPosition" in out and out["FinishPosition"].notna().any():
            team_avg = out.groupby("Team")["FinishPosition"].transform("mean")
            denom = max(team_avg.max() - team_avg.min(), 1)
            out["TeamStrength"] = 1 - (team_avg - team_avg.min()) / denom
        else:
            out["TeamStrength"] = 0.5

    if "DriverRating" not in out or out["DriverRating"].isna().all():
        if "FinishPosition" in out and out["FinishPosition"].notna().any():
            driver_avg = out.groupby("Driver")["FinishPosition"].transform("mean")
            denom = max(driver_avg.max() - driver_avg.min(), 1)
            out["DriverRating"] = 1 - (driver_avg - driver_avg.min()) / denom
        else:
            out["DriverRating"] = 0.5

    if "LongRunPace_s" not in out or out["LongRunPace_s"].isna().all():
        out["LongRunPace_s"] = (
            out["QualiTime_s"] + 2.5 + out["QualiGapToPole_s"] * 0.15
        )

    if "RecentForm" not in out or out["RecentForm"].isna().all():
        if "FinishPosition" in out and out["FinishPosition"].notna().any():
            out["RecentForm"] = (
                out.sort_values(["Driver", "Round"])
                .groupby("Driver")["FinishPosition"]
                .transform(lambda s: s.shift().rolling(3, min_periods=1).mean())
            )
            out["RecentForm"] = out["RecentForm"].fillna(out["FinishPosition"].median())
        else:
            out["RecentForm"] = 10.5

    defaults = {
        "DriverElo": 1500.0,
        "TeamElo": 1500.0,
        "DNFRate": 0.0,
        "AvgFinishLast5": out["RecentForm"].median() if "RecentForm" in out else 10.5,
        "AvgQualiLast5": out["GridPosition"].median() if "GridPosition" in out else 10.5,
        "PointsLast5": 0.0,
        "AirTemperature": 24.0,
        "RainProbability": 0.10,
        "WindSpeed": 10.0,
        "Humidity": 50.0,
        "WeatherCondition": "Dry",
    }

    for col, value in defaults.items():
        if col not in out:
            out[col] = value
        out[col] = out[col].fillna(value)

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
