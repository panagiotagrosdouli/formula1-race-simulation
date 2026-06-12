import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT))

from src.f1predictor.data_loader import build_demo_dataset
from src.f1predictor.future_race_predictor import forecast_future_race
from src.f1predictor.model_evaluation import (
    build_driver_error_table,
    build_feature_importance,
    build_monte_carlo_summary,
    build_team_error_table,
    compute_race_accuracy_metrics,
    compute_regression_metrics,
    plot_driver_error,
    plot_error_distribution,
    plot_feature_importance,
    plot_predicted_vs_actual,
    plot_team_error,
    prepare_prediction_evaluation,
)

st.set_page_config(page_title="Model Evaluation Center", layout="wide")

st.title("📊 Model Evaluation Center")
st.caption(
    "Research-style diagnostics for the F1 forecasting pipeline: regression quality, ranking accuracy, driver/team error analysis, feature importance, and Monte Carlo validation."
)

RACES_2026 = [
    "Australian Grand Prix 2026", "Chinese Grand Prix 2026", "Japanese Grand Prix 2026",
    "Bahrain Grand Prix 2026", "Saudi Arabian Grand Prix 2026", "Miami Grand Prix 2026",
    "Monaco Grand Prix 2026", "Canadian Grand Prix 2026", "Spanish Grand Prix 2026",
    "Austrian Grand Prix 2026", "British Grand Prix 2026", "Belgian Grand Prix 2026",
    "Hungarian Grand Prix 2026", "Italian Grand Prix 2026", "Singapore Grand Prix 2026",
    "United States Grand Prix 2026", "Mexico City Grand Prix 2026", "São Paulo Grand Prix 2026",
    "Las Vegas Grand Prix 2026", "Qatar Grand Prix 2026", "Abu Dhabi Grand Prix 2026",
]


@st.cache_data(show_spinner=False)
def load_history():
    return build_demo_dataset()


@st.cache_data(show_spinner=True)
def build_evaluation_state(race_name: str, n_simulations: int, noise_std: float):
    return forecast_future_race(
        history_df=load_history(),
        race_name=race_name,
        year=2026,
        round_no=12,
        n_simulations=n_simulations,
        noise_std=noise_std,
        use_2026_grid=True,
    )


with st.sidebar:
    st.header("Evaluation Controls")
    race_name = st.selectbox("Forecast race for Monte Carlo validation", RACES_2026, index=11)
    n_simulations = st.slider("Monte Carlo simulations", 500, 10000, 2500, step=500)
    noise_std = st.slider("Simulation noise", 0.5, 5.0, 2.0, step=0.25)
    rebuild = st.button("RUN EVALUATION", type="primary")

if rebuild or "evaluation_state" not in st.session_state:
    st.session_state["evaluation_state"] = build_evaluation_state(race_name, int(n_simulations), float(noise_std))

state = st.session_state["evaluation_state"]
model = state["model"]
model_metrics = state["metrics"]
historical_predictions = state["historical_predictions"]
simulation = state["simulation"]
forecast = state["forecast"]

try:
    eval_df = prepare_prediction_evaluation(historical_predictions)
    regression_metrics = compute_regression_metrics(eval_df)
    race_metrics = compute_race_accuracy_metrics(eval_df)
    driver_errors = build_driver_error_table(eval_df)
    team_errors = build_team_error_table(eval_df)
    feature_importance = build_feature_importance(model, historical_predictions)
    monte_carlo_summary = build_monte_carlo_summary(simulation)
except Exception as exc:
    st.error(f"Evaluation Center could not be built: {exc}")
    st.stop()

st.markdown("## Core Model KPIs")
metric_cols = st.columns(5)
metric_cols[0].metric("MAE", regression_metrics.get("MAE", model_metrics.get("MAE", "N/A")))
metric_cols[1].metric("RMSE", regression_metrics.get("RMSE", model_metrics.get("RMSE", "N/A")))
metric_cols[2].metric("Median AE", regression_metrics.get("MedianAE", "N/A"))
metric_cols[3].metric("Bias", regression_metrics.get("Bias", "N/A"))
metric_cols[4].metric("Spearman", model_metrics.get("SpearmanRankCorrelation", "N/A"))

st.markdown("## Race Ranking Metrics")
rank_cols = st.columns(5)
rank_cols[0].metric("Races", race_metrics.get("Races", "N/A"))
rank_cols[1].metric("Winner Accuracy", race_metrics.get("WinnerAccuracy", "N/A"))
rank_cols[2].metric("Podium Overlap", race_metrics.get("PodiumOverlap", "N/A"))
rank_cols[3].metric("Top-5 Overlap", race_metrics.get("Top5Overlap", "N/A"))
rank_cols[4].metric("Top-10 Overlap", race_metrics.get("Top10Overlap", "N/A"))

left, right = st.columns([1.25, 1.0])
with left:
    st.markdown("## Predicted vs Actual Finish")
    st.plotly_chart(plot_predicted_vs_actual(eval_df), use_container_width=True)

    st.markdown("## Driver Error Analysis")
    st.dataframe(driver_errors, use_container_width=True, hide_index=True)
    st.plotly_chart(plot_driver_error(driver_errors), use_container_width=True)

with right:
    st.markdown("## Error Distribution")
    st.plotly_chart(plot_error_distribution(eval_df), use_container_width=True)

    st.markdown("## Team Error Analysis")
    st.dataframe(team_errors, use_container_width=True, hide_index=True)
    st.plotly_chart(plot_team_error(team_errors), use_container_width=True)

research_left, research_right = st.columns([1.0, 1.0])
with research_left:
    st.markdown("## Random Forest Feature Importance")
    if feature_importance.empty:
        st.info("Feature importance is unavailable for the current model/preprocessor combination.")
    else:
        st.dataframe(feature_importance, use_container_width=True, hide_index=True)
        st.plotly_chart(plot_feature_importance(feature_importance), use_container_width=True)

with research_right:
    st.markdown("## Monte Carlo Validation View")
    st.dataframe(monte_carlo_summary, use_container_width=True, hide_index=True)
    if "WinProbability" in monte_carlo_summary.columns:
        st.plotly_chart(
            px.bar(monte_carlo_summary.head(10), x="Driver", y="WinProbability", title="Win probability distribution"),
            use_container_width=True,
        )
    if "PodiumProbability" in monte_carlo_summary.columns:
        st.plotly_chart(
            px.bar(monte_carlo_summary.head(10), x="Driver", y="PodiumProbability", title="Podium probability distribution"),
            use_container_width=True,
        )

st.markdown("## Forecast Table Used by the Monte Carlo Simulator")
forecast_cols = [
    c for c in [
        "PredictedRank", "Driver", "Team", "PredictedFinishPosition", "GridPosition",
        "DriverElo", "TeamElo", "RecentForm", "TeamStrength", "RainProbability", "RaceRiskScore",
    ] if c in forecast.columns
]
st.dataframe(forecast[forecast_cols], use_container_width=True, hide_index=True)

st.markdown("## Dataset and Split Summary")
summary_rows = [
    {"Metric": "Historical prediction rows", "Value": int(len(eval_df))},
    {"Metric": "Train rows", "Value": model_metrics.get("TrainRows", "N/A")},
    {"Metric": "Test rows", "Value": model_metrics.get("TestRows", "N/A")},
    {"Metric": "Unique drivers", "Value": int(eval_df["Driver"].nunique()) if "Driver" in eval_df else 0},
    {"Metric": "Unique races", "Value": int(eval_df["GrandPrix"].nunique()) if "GrandPrix" in eval_df else 0},
]
st.dataframe(pd.DataFrame(summary_rows), use_container_width=True, hide_index=True)
