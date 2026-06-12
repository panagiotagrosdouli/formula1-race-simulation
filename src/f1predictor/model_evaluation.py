from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def prepare_prediction_evaluation(predictions: pd.DataFrame) -> pd.DataFrame:
    """Return historical predictions with error columns for model diagnostics."""
    required = {"Driver", "GrandPrix", "FinishPosition", "PredictedFinishPosition"}
    missing = required.difference(predictions.columns)
    if missing:
        raise ValueError(f"predictions missing required columns: {sorted(missing)}")

    df = predictions.copy()
    df = df[df["FinishPosition"].notna() & df["PredictedFinishPosition"].notna()].copy()
    df["ActualFinish"] = pd.to_numeric(df["FinishPosition"], errors="coerce")
    df["PredictedFinish"] = pd.to_numeric(df["PredictedFinishPosition"], errors="coerce")
    df = df[df["ActualFinish"].notna() & df["PredictedFinish"].notna()].copy()
    df["PredictionError"] = df["PredictedFinish"] - df["ActualFinish"]
    df["AbsoluteError"] = df["PredictionError"].abs()
    df["PredictedRank"] = df.groupby("GrandPrix")["PredictedFinish"].rank(method="first").astype(int)
    df["ActualRank"] = df.groupby("GrandPrix")["ActualFinish"].rank(method="first").astype(int)
    return df


def compute_regression_metrics(eval_df: pd.DataFrame) -> dict[str, float | int | None]:
    """Compute regression and rank-quality metrics."""
    if eval_df.empty:
        return {"MAE": None, "RMSE": None, "MedianAE": None, "Bias": None, "Rows": 0}

    err = eval_df["PredictionError"].to_numpy(dtype=float)
    ae = np.abs(err)
    return {
        "MAE": round(float(ae.mean()), 3),
        "RMSE": round(float(np.sqrt(np.mean(err**2))), 3),
        "MedianAE": round(float(np.median(ae)), 3),
        "Bias": round(float(err.mean()), 3),
        "Rows": int(len(eval_df)),
    }


def compute_race_accuracy_metrics(eval_df: pd.DataFrame) -> dict[str, float | int | None]:
    """Compute winner, podium, top-5 and top-10 ranking accuracy per race."""
    if eval_df.empty or "GrandPrix" not in eval_df.columns:
        return {"WinnerAccuracy": None, "PodiumOverlap": None, "Top5Overlap": None, "Top10Overlap": None, "Races": 0}

    rows = []
    for gp, race in eval_df.groupby("GrandPrix"):
        actual = race.sort_values("ActualRank")
        predicted = race.sort_values("PredictedRank")
        if actual.empty or predicted.empty:
            continue
        actual_winner = actual.iloc[0]["Driver"]
        predicted_winner = predicted.iloc[0]["Driver"]
        rows.append(
            {
                "GrandPrix": gp,
                "WinnerCorrect": float(actual_winner == predicted_winner),
                "PodiumOverlap": len(set(actual.head(3)["Driver"]) & set(predicted.head(3)["Driver"])) / max(1, min(3, len(actual))),
                "Top5Overlap": len(set(actual.head(5)["Driver"]) & set(predicted.head(5)["Driver"])) / max(1, min(5, len(actual))),
                "Top10Overlap": len(set(actual.head(10)["Driver"]) & set(predicted.head(10)["Driver"])) / max(1, min(10, len(actual))),
            }
        )

    if not rows:
        return {"WinnerAccuracy": None, "PodiumOverlap": None, "Top5Overlap": None, "Top10Overlap": None, "Races": 0}

    summary = pd.DataFrame(rows)
    return {
        "WinnerAccuracy": round(float(summary["WinnerCorrect"].mean()), 3),
        "PodiumOverlap": round(float(summary["PodiumOverlap"].mean()), 3),
        "Top5Overlap": round(float(summary["Top5Overlap"].mean()), 3),
        "Top10Overlap": round(float(summary["Top10Overlap"].mean()), 3),
        "Races": int(len(summary)),
    }


def build_driver_error_table(eval_df: pd.DataFrame) -> pd.DataFrame:
    if eval_df.empty:
        return pd.DataFrame(columns=["Driver", "MAE", "MeanError", "StdError", "Samples"])
    return (
        eval_df.groupby("Driver")
        .agg(
            MAE=("AbsoluteError", "mean"),
            MeanError=("PredictionError", "mean"),
            StdError=("PredictionError", "std"),
            Samples=("PredictionError", "size"),
        )
        .reset_index()
        .assign(MAE=lambda d: d["MAE"].round(3), MeanError=lambda d: d["MeanError"].round(3), StdError=lambda d: d["StdError"].fillna(0).round(3))
        .sort_values(["MAE", "Samples"], ascending=[True, False])
    )


def build_team_error_table(eval_df: pd.DataFrame) -> pd.DataFrame:
    if eval_df.empty or "Team" not in eval_df.columns:
        return pd.DataFrame(columns=["Team", "MAE", "MeanError", "StdError", "Samples"])
    return (
        eval_df.groupby("Team")
        .agg(
            MAE=("AbsoluteError", "mean"),
            MeanError=("PredictionError", "mean"),
            StdError=("PredictionError", "std"),
            Samples=("PredictionError", "size"),
        )
        .reset_index()
        .assign(MAE=lambda d: d["MAE"].round(3), MeanError=lambda d: d["MeanError"].round(3), StdError=lambda d: d["StdError"].fillna(0).round(3))
        .sort_values(["MAE", "Samples"], ascending=[True, False])
    )


def plot_predicted_vs_actual(eval_df: pd.DataFrame):
    fig = px.scatter(
        eval_df,
        x="ActualFinish",
        y="PredictedFinish",
        color="Team" if "Team" in eval_df.columns else None,
        hover_data=[c for c in ["GrandPrix", "Driver", "Team", "PredictionError"] if c in eval_df.columns],
        title="Predicted vs actual finishing position",
    )
    if not eval_df.empty:
        lo = float(min(eval_df["ActualFinish"].min(), eval_df["PredictedFinish"].min()))
        hi = float(max(eval_df["ActualFinish"].max(), eval_df["PredictedFinish"].max()))
        fig.add_trace(go.Scatter(x=[lo, hi], y=[lo, hi], mode="lines", name="Perfect prediction"))
    fig.update_layout(xaxis_title="Actual finish", yaxis_title="Predicted finish", height=480)
    return fig


def plot_error_distribution(eval_df: pd.DataFrame):
    fig = px.histogram(eval_df, x="PredictionError", nbins=30, title="Prediction error distribution")
    fig.add_vline(x=0, line_dash="dash")
    fig.update_layout(xaxis_title="Predicted finish - actual finish", yaxis_title="Count", height=420)
    return fig


def plot_driver_error(driver_table: pd.DataFrame):
    df = driver_table.sort_values("MAE", ascending=False).tail(15)
    return px.bar(df, x="MAE", y="Driver", orientation="h", title="Best-calibrated drivers by MAE", hover_data=["MeanError", "Samples"])


def plot_team_error(team_table: pd.DataFrame):
    df = team_table.sort_values("MAE", ascending=True)
    return px.bar(df, x="Team", y="MAE", title="Team-level prediction MAE", hover_data=["MeanError", "Samples"])


def build_feature_importance(model, predictions: pd.DataFrame | None = None) -> pd.DataFrame:
    """Extract Random Forest feature importances when available.

    If preprocessing expands categorical variables, the exact transformed names may
    not be available across all sklearn versions. In that case, generic feature names
    are used so the dashboard still remains robust.
    """
    try:
        regressor = model.named_steps.get("regressor")
        preprocessor = model.named_steps.get("preprocessor")
        importances = getattr(regressor, "feature_importances_", None)
        if importances is None:
            return pd.DataFrame(columns=["Feature", "Importance"])

        try:
            names = list(preprocessor.get_feature_names_out())
        except Exception:
            names = [f"Feature {i + 1}" for i in range(len(importances))]

        if len(names) != len(importances):
            names = [f"Feature {i + 1}" for i in range(len(importances))]

        return (
            pd.DataFrame({"Feature": names, "Importance": importances})
            .assign(Importance=lambda d: d["Importance"].astype(float))
            .sort_values("Importance", ascending=False)
            .head(20)
            .reset_index(drop=True)
        )
    except Exception:
        return pd.DataFrame(columns=["Feature", "Importance"])


def plot_feature_importance(feature_df: pd.DataFrame):
    if feature_df.empty:
        return go.Figure()
    df = feature_df.sort_values("Importance", ascending=True)
    fig = px.bar(df, x="Importance", y="Feature", orientation="h", title="Random Forest feature importance")
    fig.update_layout(height=520)
    return fig


def build_monte_carlo_summary(simulation: pd.DataFrame) -> pd.DataFrame:
    if simulation is None or simulation.empty:
        return pd.DataFrame()
    cols = [c for c in ["Driver", "Team", "ExpectedFinish", "MedianFinish", "WinProbability", "PodiumProbability", "Top10Probability"] if c in simulation.columns]
    return simulation[cols].copy()
