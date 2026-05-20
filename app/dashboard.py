import sys
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from src.f1predictor.config import TRAINING_DATA_PATH, PREDICTIONS_PATH, SIMULATION_PATH
from src.f1predictor.data_loader import build_demo_dataset
from src.f1predictor.model import train_model
from src.f1predictor.simulation import monte_carlo_race
from src.f1predictor.visualization import plot_predicted_order, plot_probabilities


st.set_page_config(page_title="F1 AI Predictor", layout="wide")

st.title("🏎️ F1 AI Predictor")
st.write(
    "Machine learning race prediction with feature engineering and Monte Carlo simulation."
)

with st.sidebar:
    st.header("Controls")
    n_simulations = st.slider("Monte Carlo simulations", 1000, 50000, 10000, step=1000)
    noise_std = st.slider("Race uncertainty", 0.5, 5.0, 2.0, step=0.1)

    run_demo = st.button("Build demo data + train + simulate")

if run_demo or not PREDICTIONS_PATH.exists() or not SIMULATION_PATH.exists():
    df = build_demo_dataset()
    TRAINING_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(TRAINING_DATA_PATH, index=False)

    model, metrics, predictions = train_model(df)
    sim = monte_carlo_race(predictions, n_simulations=n_simulations, noise_std=noise_std)

    st.success("Pipeline completed.")
    st.json(metrics)
else:
    predictions = pd.read_csv(PREDICTIONS_PATH)
    sim = pd.read_csv(SIMULATION_PATH)

latest_gp = predictions["GrandPrix"].iloc[-1]
latest_predictions = predictions[predictions["GrandPrix"] == latest_gp].sort_values("PredictedRank")

st.subheader(f"Predicted order — {latest_gp}")
st.dataframe(
    latest_predictions[
        ["PredictedRank", "Driver", "Team", "GridPosition", "QualiGapToPole_s", "PredictedFinishPosition"]
    ],
    use_container_width=True,
)

st.plotly_chart(plot_predicted_order(latest_predictions), use_container_width=True)

st.subheader("Monte Carlo probabilities")
st.dataframe(sim, use_container_width=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.plotly_chart(plot_probabilities(sim, "WinProbability"), use_container_width=True)

with col2:
    st.plotly_chart(plot_probabilities(sim, "PodiumProbability"), use_container_width=True)

with col3:
    st.plotly_chart(plot_probabilities(sim, "Top10Probability"), use_container_width=True)
