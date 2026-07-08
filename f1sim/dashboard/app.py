"""Streamlit dashboard for F1 race strategy simulation."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from f1sim.data.config import load_race_config
from f1sim.simulation.engine import RaceSimulation
from f1sim.simulation.monte_carlo import MonteCarloSimulation


def render_dashboard(default_config: str = "configs/experiments/dry_race.yml") -> None:
    """Render the interactive dashboard."""

    st.set_page_config(page_title="F1Sim Race Engineering", layout="wide")
    st.title("F1Sim Race Engineering Platform")
    st.caption("Open simulation-based decision support for tyre, weather, SC and pace uncertainty.")
    config_path = st.sidebar.text_input("Config path", default_config)
    runs = st.sidebar.slider("Monte Carlo runs", 10, 1000, 100, step=10)
    config = load_race_config(config_path)

    result = RaceSimulation(config).run()
    frame = pd.DataFrame(result.lap_history)
    leader = result.classification[0]
    st.metric("Winning simulated race time [s]", f"{leader.total_time_s:.2f}")
    st.metric("Pit stops", leader.pit_stops)
    st.line_chart(frame.pivot_table(index="lap", columns="driver_id", values="lap_time_s"))
    st.line_chart(frame.pivot_table(index="lap", columns="driver_id", values="position"))

    if st.button("Run Monte Carlo"):
        summary = MonteCarloSimulation(config, runs=runs).run()
        st.json(summary.__dict__)


if __name__ == "__main__":  # pragma: no cover
    render_dashboard()
