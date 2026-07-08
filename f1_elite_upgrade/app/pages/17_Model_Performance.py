from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import pandas as pd
import plotly.express as px
import streamlit as st

from theme import apply_theme, chart, hero, panel, status_cards

st.set_page_config(page_title="Model Performance", page_icon="F1", layout="wide")
apply_theme()

hero(
    "Model Performance",
    "AI model governance workspace for validation, calibration, feature importance, leakage control and scientific limitations.",
    ["Validation", "Calibration", "Feature engineering", "Explainability"],
)

metrics = pd.DataFrame(
    [
        ["Winner classification", "Top-1 accuracy", 0.42, "Prototype baseline"],
        ["Podium probability", "Brier score", 0.182, "Needs calibration"],
        ["Finish position", "MAE", 2.85, "Synthetic benchmark"],
        ["DNF risk", "Log loss", 0.441, "Sparse event model"],
        ["Weather impact", "Sensitivity drift", 0.118, "Scenario test"],
    ],
    columns=["Model target", "Metric", "Value", "Status"],
)
features = pd.DataFrame(
    [
        ["Qualifying position", 0.24],
        ["Long-run pace", 0.21],
        ["Team performance index", 0.17],
        ["Tyre degradation index", 0.13],
        ["Weather risk", 0.09],
        ["Safety-car exposure", 0.07],
        ["Reliability signal", 0.05],
        ["Track fit", 0.04],
    ],
    columns=["Feature", "Importance"],
)

status_cards(
    [
        ("Validation split", "Weekend-aware", "Prefer race-weekend or season split over random rows."),
        ("Leakage policy", "Strict", "Avoid features unavailable before prediction lock."),
        ("Calibration", "Required", "Probabilities need calibration before real claims."),
        ("Explainability", "Planned", "SHAP-style analysis is a future enhancement."),
    ]
)

left, right = st.columns([1.0, 1.0])
with left:
    st.subheader("Evaluation metrics")
    st.dataframe(metrics, use_container_width=True, hide_index=True)
    chart(px.bar(metrics, x="Model target", y="Value", color="Status", title="Prototype model metric board"))
with right:
    st.subheader("Feature importance scaffold")
    chart(px.bar(features.sort_values("Importance"), x="Importance", y="Feature", orientation="h", title="Prediction factor importance"))
    st.dataframe(features, use_container_width=True, hide_index=True)

panel("Scientific integrity", "This page intentionally separates prototype metrics from validated production claims. Model evaluation should use time-aware splits, documented feature availability and calibration diagnostics.")
