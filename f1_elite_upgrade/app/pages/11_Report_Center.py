from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = ROOT.parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(REPO_ROOT))

import pandas as pd
import streamlit as st

from theme import apply_theme, hero, panel
from f1sim.data.config import load_race_config
from f1sim.simulation.engine import RaceSimulation

CONFIG_DIR = REPO_ROOT / "configs" / "experiments"

st.set_page_config(page_title="Report Center", page_icon="F1", layout="wide")
apply_theme()

hero(
    "Engineering Report Center",
    "Generate reproducible race-engineering reports with configuration, assumptions, metrics, classification, tyre strategy and limitations.",
    ["Reports", "CSV", "Markdown", "Reproducibility"],
)

configs = [str(p.relative_to(REPO_ROOT)) for p in sorted(CONFIG_DIR.glob("*.yml"))]
if not configs:
    st.error("No experiment configs found.")
    st.stop()

config_path = st.selectbox("Scenario", configs)
seed = st.number_input("Seed", min_value=1, max_value=999999, value=42)
config = load_race_config(REPO_ROOT / config_path).model_copy(update={"seed": int(seed)})
result = RaceSimulation(config).run()

lead_time = result.classification[0].total_time_s
classification = pd.DataFrame([
    {"Position": d.position, "Driver": d.driver_id, "Race time [s]": round(d.total_time_s, 3), "Gap [s]": round(d.total_time_s - lead_time, 3), "Pit stops": d.pit_stops, "Final tyre": d.compound}
    for d in result.classification
])
lap_history = pd.DataFrame(result.lap_history)

metrics = result.metrics
report = f"""# F1Sim Pro Engineering Report

## Scenario

- Config: `{config_path}`
- Seed: `{seed}`
- Race laps: `{config.laps}`
- Pit loss: `{config.pit_loss_s:.2f}s`

## Headline result

- Winner: `{result.classification[0].driver_id}`
- Total race time: `{metrics.total_race_time_s:.3f}s`
- Pit stop count: `{metrics.pit_stop_count}`
- Stint lengths: `{metrics.stint_lengths}`
- Tyre sequence: `{' - '.join(metrics.compound_sequence)}`

## Engineering metrics

- Degradation rate: `{metrics.degradation_rate_s_per_lap:.4f}s/lap`
- Traffic loss: `{metrics.traffic_loss_s:.3f}s`
- Pit loss: `{metrics.pit_loss_s:.3f}s`
- Undercut delta: `{metrics.undercut_delta_s:.3f}s`
- Overcut delta: `{metrics.overcut_delta_s:.3f}s`
- Risk percentile: `{metrics.risk_percentile:.1f}`

## Limitations

This report uses transparent open simulation models and example YAML configurations. It does not include official Formula 1 team telemetry, private strategy data, or licensed F1 Fantasy data.
"""

c1, c2, c3 = st.columns(3)
c1.download_button("Download report", report, "f1sim_report.md", "text/markdown")
c2.download_button("Download classification CSV", classification.to_csv(index=False), "classification.csv", "text/csv")
c3.download_button("Download lap history CSV", lap_history.to_csv(index=False), "lap_history.csv", "text/csv")

st.subheader("Classification")
st.dataframe(classification, use_container_width=True, hide_index=True)

st.subheader("Report preview")
st.markdown(report)
panel("Reproducibility", "The report records the config path and seed so results can be regenerated and compared after model changes.")
