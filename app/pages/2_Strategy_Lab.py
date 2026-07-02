import sys
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.append(str(ROOT))

from app.components.theme import card, chart, hero, inject_theme, metric_card
from f1predictor.strategy.advanced_strategy import make_pit_window_figure, make_strategy_figure, simulate_strategy

st.set_page_config(page_title="Strategy Lab", layout="wide")
inject_theme()

hero(
    eyebrow="Race strategy decision support",
    title="Strategy Lab",
    body=(
        "Compare tyre strategy candidates, pit-lane loss sensitivity, and one-stop pit windows. "
        "The goal is not only to find the fastest theoretical plan, but to explain the strategic trade-off clearly."
    ),
)

with st.sidebar:
    st.header("Strategy configuration")
    total_laps = st.slider("Race laps", 30, 78, 53)
    pit_loss = st.slider("Pit loss (s)", 15.0, 35.0, 22.5, 0.5)

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

results_df = pd.DataFrame(rows).sort_values("TotalRaceTime_s").reset_index(drop=True)
best = results_df.iloc[0]

m1, m2, m3, m4 = st.columns(4)
with m1:
    metric_card("Best strategy", str(best["Strategy"]), "lowest simulated race time")
with m2:
    metric_card("Projected time", f"{best['TotalRaceTime_s']:.3f}s", "total race-time estimate")
with m3:
    metric_card("Stops", str(int(best["Stops"])), "planned pit stops")
with m4:
    metric_card("Pit loss", f"{pit_loss:.1f}s", "assumed lane penalty")

st.markdown("## Strategy workspace")
w1, w2, w3 = st.columns(3)
with w1:
    card("Tyre plan comparison", "Compare candidate stint structures and total race-time estimates.")
with w2:
    card("Pit window sensitivity", "Search one-stop windows to understand where pit timing becomes attractive.")
with w3:
    card("Engineering interpretation", "Use the fastest plan as a baseline, then consider track position, safety cars and tyre cliff risk.")

left, right = st.columns([1, 1.25])
with left:
    st.subheader("Candidate strategies")
    st.dataframe(results_df, use_container_width=True, hide_index=True)
with right:
    st.subheader("Stint structure")
    chart(make_strategy_figure(strategies))

st.subheader("One-stop pit window search")
window_results, fig = make_pit_window_figure(total_laps)
chart(fig)
st.dataframe(window_results.head(10), use_container_width=True, hide_index=True)
