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

CONFIG_DIR = REPO_ROOT / "configs" / "experiments"

st.set_page_config(page_title="Reproducibility Settings", page_icon="F1", layout="wide")
apply_theme()

hero(
    "Reproducibility and Data Policy",
    "Configuration, deterministic seeds, public-data boundaries, model limitations and roadmap for turning the prototype into a calibrated research platform.",
    ["Seeds", "Configs", "Data honesty", "Roadmap"],
)

configs = [str(p.relative_to(REPO_ROOT)) for p in sorted(CONFIG_DIR.glob("*.yml"))] if CONFIG_DIR.exists() else []

c1, c2, c3 = st.columns(3)
c1.metric("YAML experiments", len(configs))
c2.metric("Primary app", "Multipage Streamlit")
c3.metric("Data policy", "No fabricated team data")

st.subheader("Available experiment configs")
st.dataframe(pd.DataFrame({"Config": configs}), use_container_width=True, hide_index=True)

panel(
    "Deterministic seeds",
    "Every scenario should define a seed. This makes stochastic weather, safety-car events, traffic scaffolds and Monte Carlo outputs reproducible for research and debugging.",
)
panel(
    "Data-source boundary",
    "Public-data integrations such as FastF1 or OpenF1 must be cited and must respect their terms. Synthetic examples are allowed only when clearly labelled as demo or prototype values.",
)
panel(
    "Known limitations",
    "Traffic, penalties, reliability, restart tyre temperature, live timing ingestion and official fantasy-game data are not production-calibrated. They remain prototype or planned until implemented with validated data.",
)

roadmap = pd.DataFrame(
    [
        ["Public data adapters", "FastF1/OpenF1 loaders with provenance", "Prototype"],
        ["Live race weekend state", "Session selector and live timing ingestion", "Planned"],
        ["Calibrated driver database", "Historical pace, wet performance and tyre management", "Planned"],
        ["Team and track calibration", "Reliability, pit loss, degradation, SC history", "Planned"],
        ["Report exports", "Figures, markdown, CSV and scenario comparison", "Prototype"],
    ],
    columns=["Area", "Goal", "Status"],
)
st.subheader("Roadmap")
st.dataframe(roadmap, use_container_width=True, hide_index=True)
