import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "app"))

import pandas as pd
import streamlit as st
from f1predictor.strategy.advanced_strategy import make_pit_window_figure, make_strategy_figure, simulate_strategy
from theme import apply_theme, chart, hero, panel

st.set_page_config(page_title="Strategy Lab", page_icon="🧠", layout="wide")
apply_theme()
hero(
    "🧠 F1 Strategy Lab",
    "Compare candidate tyre strategies, pit-loss sensitivity and one-stop pit windows using a simple race-time simulation model.",
    ["Pit windows", "Tyre strategy", "Race time", "Decision support"],
)

with st.sidebar:
    st.header("Strategy controls")
    total_laps = st.slider("Race laps", 30, 78, 53)
    pit_loss = st.slider("Pit loss (s)", 15.0, 35.0, 22.5, 0.5)
    st.caption("Pit loss has a strong effect on whether one-stop or two-stop strategies become optimal.")

strategies = {
    "S-M": [("SOFT", 16), ("MEDIUM", total_laps - 16)],
    "M-H": [("MEDIUM", 25), ("HARD", total_laps - 25)],
    "S-H": [("SOFT", 14), ("HARD", total_laps - 14)],
    "S-M-M": [("SOFT", 12), ("MEDIUM", 20), ("MEDIUM", total_laps - 32)],
}

rows = []
for name, strat in strategies.items():
    total, _ = simulate_strategy(strat, pit_loss=pit_loss)
    rows.append({"Strategy": name, "Stops": len(strat) - 1, "TotalRaceTime_s": round(total, 3)})

strategy_df = pd.DataFrame(rows).sort_values("TotalRaceTime_s").reset_index(drop=True)
best = strategy_df.iloc[0]

col1, col2, col3, col4 = st.columns(4)
col1.metric("Best strategy", best["Strategy"])
col2.metric("Projected race time", f"{best['TotalRaceTime_s']:.3f}s")
col3.metric("Stops", int(best["Stops"]))
col4.metric("Pit loss", f"{pit_loss:.1f}s")

panel(
    "Strategy interpretation",
    "The lowest total race time is the baseline recommendation, but race engineers should also consider track position, safety-car probability, tyre cliff risk and undercut opportunities.",
)

left, right = st.columns([1, 1.35])
with left:
    st.subheader("Candidate strategies")
    st.dataframe(strategy_df, use_container_width=True, hide_index=True)
with right:
    st.subheader("Stint structure")
    chart(make_strategy_figure(strategies))

st.subheader("One-stop pit window search")
results, fig = make_pit_window_figure(total_laps)
chart(fig)
st.dataframe(results.head(10), use_container_width=True, hide_index=True)
