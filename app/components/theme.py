"""Shared visual theme and UI helpers for the Streamlit application.

This module keeps presentation code in one place so pages can move toward a
single calm, professional product experience without copy-pasting large CSS blocks.
"""

from __future__ import annotations

import html

import streamlit as st

APP_CSS = """
<style>
:root {
    --f1-accent: #2563eb;
    --f1-accent-soft: #60a5fa;
    --f1-bg: #0f172a;
    --f1-bg-soft: #111827;
    --f1-panel: rgba(17, 24, 39, 0.88);
    --f1-panel-strong: rgba(30, 41, 59, 0.94);
    --f1-border: rgba(148, 163, 184, 0.22);
    --f1-muted: #94a3b8;
    --f1-text: #e5e7eb;
    --f1-heading: #f8fafc;
    --f1-success: #22c55e;
    --f1-warning: #f59e0b;
}

.stApp {
    background:
        radial-gradient(circle at top left, rgba(37, 99, 235, 0.12), transparent 30%),
        radial-gradient(circle at bottom right, rgba(15, 23, 42, 0.90), transparent 35%),
        linear-gradient(135deg, #0f172a 0%, #111827 55%, #0b1120 100%);
    color: var(--f1-text);
}

[data-testid="stHeader"] { background: rgba(0, 0, 0, 0); }
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0b1120 0%, #111827 100%);
    border-right: 1px solid var(--f1-border);
}

.block-container {
    max-width: 1640px;
    padding-top: 1.5rem;
}

.f1-hero {
    padding: 2.3rem;
    border-radius: 1.25rem;
    background: linear-gradient(135deg, rgba(30, 41, 59, 0.96), rgba(15, 23, 42, 0.96));
    border: 1px solid var(--f1-border);
    box-shadow: 0 20px 55px rgba(0, 0, 0, 0.30);
    margin-bottom: 1.2rem;
}

.f1-eyebrow {
    color: var(--f1-accent-soft);
    letter-spacing: 0.12em;
    text-transform: uppercase;
    font-size: 0.76rem;
    font-weight: 750;
    margin-bottom: 0.55rem;
}

.f1-hero h1 {
    color: var(--f1-heading);
    font-size: 3rem;
    line-height: 1.05;
    font-weight: 840;
    margin: 0 0 0.75rem 0;
}

.f1-hero p {
    color: #cbd5e1;
    font-size: 1.04rem;
    line-height: 1.72;
    max-width: 980px;
    margin: 0;
}

.f1-card {
    padding: 1.15rem 1.2rem;
    border-radius: 1rem;
    background: var(--f1-panel);
    border: 1px solid var(--f1-border);
    min-height: 142px;
    box-shadow: 0 12px 30px rgba(0, 0, 0, 0.22);
}

.f1-card h3 {
    color: var(--f1-heading);
    margin: 0 0 0.5rem 0;
    font-size: 1.02rem;
    font-weight: 750;
}

.f1-card p {
    color: #cbd5e1;
    line-height: 1.56;
    margin: 0;
}

.f1-metric-card {
    padding: 1rem 1.1rem;
    border-radius: 0.95rem;
    background: var(--f1-panel-strong);
    border: 1px solid var(--f1-border);
    border-top: 2px solid var(--f1-accent);
    min-height: 105px;
}

.f1-metric-label {
    color: var(--f1-muted);
    font-size: 0.78rem;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin-bottom: 0.35rem;
}

.f1-metric-value {
    color: var(--f1-heading);
    font-size: 1.55rem;
    font-weight: 780;
    line-height: 1.08;
}

.f1-metric-caption {
    color: #b6c2d1;
    margin-top: 0.35rem;
    font-size: 0.86rem;
}

.f1-feed-line {
    padding: 0.85rem 1rem;
    border-radius: 0.8rem;
    background: rgba(148, 163, 184, 0.075);
    border: 1px solid rgba(148, 163, 184, 0.16);
    border-left: 3px solid var(--f1-accent);
    color: #dbe4ef;
    margin: 0.65rem 0;
}

.f1-badge {
    display: inline-block;
    padding: 0.24rem 0.55rem;
    border-radius: 999px;
    background: rgba(37, 99, 235, 0.14);
    border: 1px solid rgba(96, 165, 250, 0.32);
    color: #93c5fd;
    font-size: 0.74rem;
    font-weight: 760;
    margin-right: 0.45rem;
}

button[kind="primary"] {
    border-radius: 0.7rem;
}
</style>
"""


def inject_theme() -> None:
    """Inject the shared application theme into the current Streamlit page."""
    st.markdown(APP_CSS, unsafe_allow_html=True)


def hero(eyebrow: str, title: str, body: str) -> None:
    """Render a calm product hero block."""
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
    """Render a reusable content panel."""
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
    """Render a reusable metric panel."""
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
    """Render a short operational status line."""
    st.markdown(
        f"""
        <div class="f1-feed-line">
            <span class="f1-badge">{html.escape(label)}</span>{html.escape(text)}
        </div>
        """,
        unsafe_allow_html=True,
    )
