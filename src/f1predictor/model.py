import joblib
import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.model_selection import GroupShuffleSplit
from sklearn.pipeline import Pipeline

from .config import MODEL_PATH, PREDICTIONS_PATH
from .features import add_fallback_features, get_feature_columns, make_preprocessor


def build_model(random_state: int = 42) -> Pipeline:
    regressor = RandomForestRegressor(
        n_estimators=400,
        max_depth=8,
        min_samples_leaf=2,
        random_state=random_state,
        n_jobs=-1,
    )

    return Pipeline(
        steps=[
            ("preprocessor", make_preprocessor()),
            ("regressor", regressor),
        ]
    )


def train_model(df: pd.DataFrame) -> tuple[Pipeline, dict, pd.DataFrame]:
    df = add_fallback_features(df)

    X = df[get_feature_columns()]
    y = df["FinishPosition"].astype(float)

    groups = df["Round"] if "Round" in df else None

    if groups is not None and df["Round"].nunique() >= 4:
        splitter = GroupShuffleSplit(n_splits=1, test_size=0.25, random_state=42)
        train_idx, test_idx = next(splitter.split(X, y, groups))
    else:
        # Fallback split for tiny datasets.
        split = int(len(df) * 0.75)
        train_idx = np.arange(split)
        test_idx = np.arange(split, len(df))

    model = build_model()
    model.fit(X.iloc[train_idx], y.iloc[train_idx])

    pred = model.predict(X.iloc[test_idx])

    mae = mean_absolute_error(y.iloc[test_idx], pred)
    rmse = mean_squared_error(y.iloc[test_idx], pred) ** 0.5
    rho = spearmanr(y.iloc[test_idx], pred).correlation

    metrics = {
        "MAE": round(float(mae), 3),
        "RMSE": round(float(rmse), 3),
        "SpearmanRankCorrelation": round(float(rho), 3) if not np.isnan(rho) else None,
        "TrainRows": int(len(train_idx)),
        "TestRows": int(len(test_idx)),
    }

    full_pred = model.predict(X)
    predictions = df.copy()
    predictions["PredictedFinishPosition"] = full_pred
    predictions["PredictedRank"] = (
        predictions.groupby("GrandPrix")["PredictedFinishPosition"]
        .rank(method="first")
        .astype(int)
    )

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    predictions.to_csv(PREDICTIONS_PATH, index=False)

    return model, metrics, predictions


def load_model() -> Pipeline:
    return joblib.load(MODEL_PATH)


def predict_next_race(model: Pipeline, race_df: pd.DataFrame) -> pd.DataFrame:
    race_df = add_fallback_features(race_df)
    X = race_df[get_feature_columns()]
    out = race_df.copy()
    out["PredictedFinishPosition"] = model.predict(X)
    out = out.sort_values("PredictedFinishPosition").reset_index(drop=True)
    out["PredictedRank"] = np.arange(1, len(out) + 1)
    return out
