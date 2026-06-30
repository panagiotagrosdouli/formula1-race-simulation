"""Shared visual theme and UI helpers for the Streamlit application.

This module keeps presentation code in one place so pages can move toward a
single premium product experience without copy-pasting large CSS blocks.
"""

from __future__ import annotations

import html

import streamlit as st

APP_CSS = """
<style>
:root {
    --f1-red: #e10600;
    --f1-red-soft: #ff4d4d;
    --f1-bg: #050505;
    --f1-panel: rgba(16, 18, 24, 0.86);
    --f1-panel-strong: rgba(23, 26, 34, 0.94);
    --f1-border: rgba(255, 255, 255, 0.12);
    --f1-muted: #9aa4af;
    --f1-text: #f5f5f5;
}

.stApp {
    background:
        radial-gradient(circle at top left, rgba(225, 6, 0, 0.22), transparent 28%),
        radial-gradient(circle at top right, rgba(255, 255, 255, 0.08), transparent 22%),
        linear-gradient(135deg, #030303 0%, #080808 52%, #111111 100%);
    color: var(--f1-text);
}

[data-testid="stHeader"] { background: rgba(0, 0, 0, 0); }
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #050505 0%, #101010 100%);
    border-right: 1px solid rgba(225, 6, 0, 0.32);
}

.block-container {
    max-width: 1680px;
    padding-top: 1.4rem;
}

.f1-hero {
    padding: 2.4rem;
    border-radius: 1.6rem;
    background: linear-gradient(135deg, rgba(120, 0, 0, 0.92), rgba(8, 8, 10, 0.96));
    border: 1px solid rgba(255, 78, 78, 0.35);
    box-shadow: 0 22px 70px rgba(0, 0, 0, 0.38), 0 0 34px rgba(225, 6, 0, 0.10);
    margin-bottom: 1.2rem;
}

.f1-eyebrow {
    color: #ffb3b3;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    font-size: 0.78rem;
    font-weight: 800;
    margin-bottom: 0.55rem;
}

.f1-hero h1 {
    color: #ffffff;
    font-size: 3.3rem;
    line-height: 1;
    font-weight: 900;
    margin: 0 0 0.75rem 0;
}

.f1-hero p {
    color: #f3dada;
    font-size: 1.08rem;
    line-height: 1.72;
    max-width: 980px;
    margin: 0;
}

.f1-card {
    padding: 1.15rem 1.2rem;
    border-radius: 1.1rem;
    background: var(--f1-panel);
    border: 1px solid var(--f1-border);
    min-height: 145px;
    box-shadow: 0 14px 38px rgba(0, 0, 0, 0.24);
}

.f1-card h3 {
    color: var(--f1-red-soft);
    margin: 0 0 0.45rem 0;
    font-size: 1.05rem;
}

.f1-card p {
    color: #e8e8e8;
    line-height: 1.55;
    margin: 0;
}

.f1-metric-card {
    padding: 1rem 1.1rem;
    border-radius: 1rem;
    background: var(--f1-panel-strong);
    border: 1px solid var(--f1-border);
    border-top: 2px solid var(--f1-red);
    min-height: 105px;
}

.f1-metric-label {
    color: var(--f1-muted);
    font-size: 0.82rem;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin-bottom: 0.35rem;
}

.f1-metric-value {
    color: #ffffff;
    font-size: 1.65rem;
    font-weight: 850;
    line-height: 1.05;
}

.f1-metric-caption {
    color: #b9c0c8;
    margin-top: 0.35rem;
    font-size: 0.86rem;
}

.f1-feed-line {
    padding: 0.85rem 1rem;
    border-radius: 0.85rem;
    background: rgba(255, 255, 255, 0.055);
    border-left: 4px solid var(--f1-red);
    color: #f2f2f2;
    margin: 0.65rem 0;
}

.f1-badge {
    display: inline-block;
    padding: 0.26rem 0.58rem;
    border-radius: 999px;
    background: rgba(225, 6, 0, 0.16);
    border: 1px solid rgba(225, 6, 0, 0.48);
    color: #ff6b6b;
    font-size: 0.76rem;
    font-weight: 800;
    margin-right: 0.45rem;
}
</style>
"""


def inject_theme() -> None:
    """Inject the shared application theme into the current Streamlit page."""
    st.markdown(APP_CSS, unsafe_allow_html=True)


def hero(eyebrow: str, title: str, body: str) -> None:
    """Render a premium hero block."""
    st.markdown(
        f"""
        <div class="f1-hero">
            <div class="f1-eyebrow">{html.escape(eyebrow)}</div>
            <h1>{html.escape(title)}</h1>
            <p>{html.escape(body)}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def card(title: str, body: str) -> None:
    """Render a reusable content card."""
    st.markdown(
        f"""
        <div class="f1-card">
            <h3>{html.escape(title)}</h3>
            <p>{html.escape(body)}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def metric_card(label: str, value: str, caption: str = "") -> None:
    """Render a reusable metric card."""
    st.markdown(
        f"""
        <div class="f1-metric-card">
            <div class="f1-metric-label">{html.escape(label)}</div>
            <div class="f1-metric-value">{html.escape(value)}</div>
            <div class="f1-metric-caption">{html.escape(caption)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def feed_line(label: str, text: str) -> None:
    """Render a short race-control style line."""
    st.markdown(
        f"""
        <div class="f1-feed-line">
            <span class="f1-badge">{html.escape(label)}</span>{html.escape(text)}
        </div>
        """,
        unsafe_allow_html=True,
    )
