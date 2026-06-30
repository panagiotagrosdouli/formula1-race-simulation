import sys
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT))

from app.components.theme import card, hero, inject_theme, metric_card
from src.f1predictor.config import PREDICTIONS_PATH, SIMULATION_PATH
from src.f1predictor.data_loader import build_demo_dataset
from src.f1predictor.model import train_model
from src.f1predictor.simulation import monte_carlo_race
from src.f1predictor.visualization import plot_probabilities

st.set_page_config(page_title="Simulation Workspace", layout="wide")
inject_theme()

hero(
    eyebrow="Monte Carlo uncertainty workspace",
    title="Simulation Workspace",
    body=(
        "Evaluate race outcome uncertainty through Monte Carlo simulation. This page focuses on probability "
        "distributions, expected outcomes, and communication of uncertainty rather than a single deterministic order."
    ),
)

with st.sidebar:
    st.header("Simulation controls")
    n_simulations = st.slider("Simulation runs", 1000, 50000, 10000, step=1000)
    noise_std = st.slider("Race uncertainty", 0.5, 5.0, 2.0, step=0.1)
    rebuild_inputs = st.checkbox("Rebuild demo forecast inputs", value=False)
    run_simulation = st.button("Run simulation", type="primary")

st.markdown("## Simulation capabilities")
cap_1, cap_2, cap_3 = st.columns(3)
with cap_1:
    card(
        "Probability-first analysis",
        "Monte Carlo outputs estimate win, podium, and top-10 probability rather than presenting one race order as certain.",
    )
with cap_2:
    card(
        "Uncertainty control",
        "The race uncertainty parameter controls stochastic variation around the model forecast and helps evaluate race volatility.",
    )
with cap_3:
    card(
        "Decision support",
        "Simulation tables and charts help identify robust contenders, high-upside drivers, and unstable forecast outcomes.",
    )

if run_simulation or rebuild_inputs or not SIMULATION_PATH.exists() or not PREDICTIONS_PATH.exists():
    with st.spinner("Preparing forecast inputs and running Monte Carlo simulation..."):
        history = build_demo_dataset()
        _, metrics, predictions = train_model(history)
        simulation = monte_carlo_race(
            predictions,
            n_simulations=int(n_simulations),
            noise_std=float(noise_std),
        )
    st.success("Simulation completed.")
    with st.expander("Model training metrics from generated input data"):
        st.json(metrics)
else:
    predictions = pd.read_csv(PREDICTIONS_PATH)
    simulation = pd.read_csv(SIMULATION_PATH)

if simulation.empty:
    st.warning("No simulation rows are available.")
    st.stop()

leader_win = simulation.sort_values("WinProbability", ascending=False).iloc[0]
leader_podium = simulation.sort_values("PodiumProbability", ascending=False).iloc[0]
leader_top10 = simulation.sort_values("Top10Probability", ascending=False).iloc[0]
mean_win = simulation["WinProbability"].mean() if "WinProbability" in simulation else 0

k1, k2, k3, k4 = st.columns(4)
with k1:
    metric_card("Win probability leader", str(leader_win["Driver"]), f"{leader_win['WinProbability'] * 100:.1f}%")
with k2:
    metric_card("Podium probability leader", str(leader_podium["Driver"]), f"{leader_podium['PodiumProbability'] * 100:.1f}%")
with k3:
    metric_card("Top-10 stability leader", str(leader_top10["Driver"]), f"{leader_top10['Top10Probability'] * 100:.1f}%")
with k4:
    metric_card("Average win probability", f"{mean_win * 100:.1f}%", "Across simulated field")

st.markdown("## Probability table")
ordered_cols = [
    column
    for column in ["Driver", "Team", "WinProbability", "PodiumProbability", "Top10Probability"]
    if column in simulation.columns
]
st.dataframe(simulation[ordered_cols] if ordered_cols else simulation, use_container_width=True, hide_index=True)

st.markdown("## Probability views")
chart_1, chart_2, chart_3 = st.columns(3)
with chart_1:
    st.plotly_chart(plot_probabilities(simulation, "WinProbability"), use_container_width=True)
with chart_2:
    st.plotly_chart(plot_probabilities(simulation, "PodiumProbability"), use_container_width=True)
with chart_3:
    st.plotly_chart(plot_probabilities(simulation, "Top10Probability"), use_container_width=True)

st.markdown("## Engineering interpretation")
st.write(
    "The simulation layer should be interpreted as an uncertainty model around the forecast inputs. "
    "Large gaps between win, podium, and top-10 probability indicate different types of race risk: a driver can be "
    "a strong top-10 candidate without being a strong win candidate, while high podium probability with lower win probability "
    "suggests consistency without dominant upside."
)

st.caption(
    "Simulation results are probabilistic estimates generated from the current model inputs. They are not guaranteed race outcomes."
)
