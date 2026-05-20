import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

import streamlit as st
from f1predictor.strategy.advanced_strategy import make_pit_window_figure, make_strategy_figure, simulate_strategy

st.set_page_config(page_title="Strategy Lab", layout="wide")
st.title("F1 Strategy Lab")
st.caption("Pit-window optimization, tire degradation and race-time simulation.")

total_laps = st.sidebar.slider("Race laps", 30, 78, 53)
pit_loss = st.sidebar.slider("Pit loss (s)", 15.0, 35.0, 22.5, 0.5)

strategies = {
    "S-M": [("SOFT", 16), ("MEDIUM", total_laps - 16)],
    "M-H": [("MEDIUM", 25), ("HARD", total_laps - 25)],
    "S-H": [("SOFT", 14), ("HARD", total_laps - 14)],
    "S-M-M": [("SOFT", 12), ("MEDIUM", 20), ("MEDIUM", total_laps - 32)],
}

rows = []
for name, strat in strategies.items():
    total, _ = simulate_strategy(strat, pit_loss=pit_loss)
    rows.append({"Strategy": name, "TotalRaceTime_s": round(total, 3)})

st.subheader("Candidate strategies")
st.dataframe(rows, width="stretch")
st.plotly_chart(make_strategy_figure(strategies), width="stretch")

st.subheader("One-stop pit window search")
results, fig = make_pit_window_figure(total_laps)
st.plotly_chart(fig, width="stretch")
st.dataframe(results.head(10), width="stretch")
