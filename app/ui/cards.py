"""Reusable card primitives for the F1 Base44 Elite UI."""

from __future__ import annotations

import html

import pandas as pd
import streamlit as st


def kpi_card(label: str, value: str, caption: str = "") -> None:
    """Render a premium KPI card."""

    st.markdown(
        f"""
        <div class="f1-card">
            <div class="f1-label">{html.escape(label)}</div>
            <div class="f1-value">{html.escape(value)}</div>
            <div class="f1-sub">{html.escape(caption)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def panel(title: str, body: str) -> None:
    """Render an explanatory panel."""

    st.markdown(
        f"""
        <div class="f1-panel">
            <h3>{html.escape(title)}</h3>
            <p>{html.escape(body)}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def feed_line(label: str, text: str) -> None:
    """Render a race-control style feed item."""

    st.markdown(
        f"<div class='f1-feed'><b>{html.escape(label)}</b>{html.escape(text)}</div>",
        unsafe_allow_html=True,
    )


def driver_prediction_card(row: pd.Series) -> None:
    """Render a fan-friendly driver prediction card."""

    team = str(row.get("Team", "Team unknown"))
    rank = row.get("PredictedRank", row.get("PredictedFinishPosition", "—"))
    try:
        rank_text = f"P{int(float(rank))}"
    except Exception:
        rank_text = str(rank)

    win = float(row.get("WinProbability", 0) or 0) * 100
    podium = float(row.get("PodiumProbability", 0) or 0) * 100
    top10 = float(row.get("Top10Probability", 0) or 0) * 100
    driver = str(row.get("Driver", "Driver"))
    why = str(row.get("FanSummary", "Prediction explanation unavailable."))

    st.markdown(
        f"""
        <div class="f1-driver-card">
            <div class="f1-label">{html.escape(team)}</div>
            <div class="f1-value">{html.escape(driver)} · {html.escape(rank_text)}</div>
            <div class="f1-prob-row">
                <span class="f1-prob-pill">Win {win:.1f}%</span>
                <span class="f1-prob-pill">Podium {podium:.1f}%</span>
                <span class="f1-prob-pill">Top 10 {top10:.1f}%</span>
            </div>
            <div class="f1-why">{html.escape(why)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
