"""Shared Base44-style visual theme and UI helpers for the Streamlit application."""

from __future__ import annotations

import html

import plotly.graph_objects as go
import streamlit as st

PRIMARY = "#e10600"
PRIMARY_DARK = "#8b0000"
TEXT = "#f9fafb"
MUTED = "#9ca3af"
GRID = "rgba(255,255,255,0.08)"
PALETTE = [PRIMARY, "#ff4d4d", "#f97316", "#facc15", "#38bdf8", "#60a5fa", "#a78bfa"]

APP_CSS = f"""
<style>
:root {{
    --f1-accent: {PRIMARY};
    --f1-accent-dark: {PRIMARY_DARK};
    --f1-accent-soft: #fecaca;
    --f1-bg: #07080d;
    --f1-bg-soft: #0f172a;
    --f1-panel: rgba(17, 24, 39, 0.86);
    --f1-panel-strong: rgba(21, 31, 46, 0.94);
    --f1-border: rgba(255, 255, 255, 0.10);
    --f1-muted: {MUTED};
    --f1-text: {TEXT};
    --f1-heading: #ffffff;
}}

.stApp {{
    background:
        radial-gradient(circle at 50% -12%, rgba(225, 6, 0, 0.18), transparent 34%),
        linear-gradient(135deg, #030407 0%, var(--f1-bg) 48%, #0c111b 100%);
    color: var(--f1-text);
}}

[data-testid="stHeader"] {{
    background: rgba(7, 8, 13, 0.78);
    backdrop-filter: blur(18px);
    border-bottom: 1px solid rgba(255,255,255,0.06);
}}

[data-testid="stSidebar"] {{
    background: linear-gradient(180deg, #07080d 0%, #0f172a 100%);
    border-right: 1px solid rgba(225, 6, 0, 0.30);
}}

.block-container {{
    max-width: 1540px;
    padding-top: 1.15rem;
    padding-bottom: 2.3rem;
}}

h1, h2, h3 {{
    color: var(--f1-heading);
    letter-spacing: -0.04em;
}}

.f1-hero {{
    padding: 2rem 2.15rem;
    border-radius: 1.85rem;
    background:
        linear-gradient(135deg, rgba(225, 6, 0, 0.20), rgba(17, 24, 39, 0.96)),
        radial-gradient(circle at 90% 10%, rgba(225, 6, 0, 0.16), transparent 20rem);
    border: 1px solid rgba(225, 6, 0, 0.34);
    box-shadow: 0 28px 90px rgba(0, 0, 0, 0.36), inset 0 1px 0 rgba(255,255,255,0.05);
    margin-bottom: 1.15rem;
}}

.f1-eyebrow {{
    color: #fecaca;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    font-size: 0.76rem;
    font-weight: 850;
    margin-bottom: 0.65rem;
}}

.f1-hero h1 {{
    color: var(--f1-heading);
    font-size: clamp(2.25rem, 4vw, 3.85rem);
    line-height: 1.02;
    font-weight: 950;
    margin: 0 0 0.8rem 0;
}}

.f1-hero p {{
    color: #d1d5db;
    font-size: 1.04rem;
    line-height: 1.68;
    max-width: 1080px;
    margin: 0;
}}

.f1-card, .f1-metric-card, div[data-testid="stMetric"] {{
    border-radius: 1.35rem;
    background: linear-gradient(180deg, rgba(21, 31, 46, 0.96), rgba(16, 23, 34, 0.92));
    border: 1px solid var(--f1-border);
    border-top: 2px solid var(--f1-accent);
    box-shadow: 0 18px 45px rgba(0, 0, 0, 0.26), inset 0 1px 0 rgba(255,255,255,0.04);
}}

.f1-card {{
    padding: 1.2rem 1.25rem;
    min-height: 148px;
}}

.f1-card h3 {{
    color: var(--f1-heading);
    margin: 0 0 0.55rem 0;
    font-size: 1.05rem;
    font-weight: 850;
}}

.f1-card p {{
    color: #d1d5db;
    line-height: 1.58;
    margin: 0;
}}

.f1-metric-card {{
    padding: 1.05rem 1.15rem;
    min-height: 112px;
}}

.f1-metric-label, div[data-testid="stMetricLabel"] {{
    color: var(--f1-muted);
    font-size: 0.78rem;
    text-transform: uppercase;
    letter-spacing: 0.07em;
    font-weight: 850;
    margin-bottom: 0.38rem;
}}

.f1-metric-value, div[data-testid="stMetricValue"] {{
    color: var(--f1-heading);
    font-size: 1.65rem;
    font-weight: 950;
    line-height: 1.06;
}}

.f1-metric-caption {{
    color: var(--f1-muted);
    margin-top: 0.38rem;
    font-size: 0.86rem;
}}

.f1-feed-line {{
    padding: 0.9rem 1rem;
    border-radius: 1rem;
    background: rgba(16, 23, 34, 0.86);
    border: 1px solid var(--f1-border);
    border-left: 3px solid var(--f1-accent);
    color: #dbe4ef;
    margin: 0.65rem 0;
    box-shadow: 0 14px 34px rgba(0,0,0,0.20);
}}

.f1-badge {{
    display: inline-block;
    padding: 0.26rem 0.58rem;
    border-radius: 999px;
    background: rgba(225, 6, 0, 0.16);
    border: 1px solid rgba(225, 6, 0, 0.42);
    color: #fecaca;
    font-size: 0.74rem;
    font-weight: 850;
    margin-right: 0.5rem;
}}

[data-testid="stDataFrame"] {{
    border: 1px solid var(--f1-border);
    border-radius: 1.1rem;
    overflow: hidden;
    background: rgba(16, 23, 34, 0.72);
}}

.stButton > button, .stDownloadButton > button {{
    border-radius: 999px;
    border: 1px solid rgba(255, 100, 95, 0.50);
    background: linear-gradient(135deg, var(--f1-accent), var(--f1-accent-dark));
    color: #ffffff;
    font-weight: 900;
    box-shadow: 0 12px 28px rgba(225, 6, 0, 0.20);
}}

.stButton > button:hover, .stDownloadButton > button:hover {{
    border-color: rgba(255, 160, 155, 0.90);
    filter: brightness(1.08);
}}

div[data-baseweb="select"] > div,
input,
textarea {{
    background-color: rgba(16, 23, 34, 0.96) !important;
    color: var(--f1-text) !important;
    border-color: rgba(255,255,255,0.14) !important;
    border-radius: 14px !important;
}}

section[data-testid="stTabs"] button {{
    color: #f8fafc !important;
    font-weight: 850 !important;
}}

.stAlert {{ border-radius: 16px; }}
</style>
"""


def inject_theme() -> None:
    st.markdown(APP_CSS, unsafe_allow_html=True)


def hero(eyebrow: str, title: str, body: str) -> None:
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
    st.markdown(
        f"""
        <div class="f1-feed-line">
            <span class="f1-badge">{html.escape(label)}</span>{html.escape(text)}
        </div>
        """,
        unsafe_allow_html=True,
    )


def theme_fig(fig: go.Figure) -> go.Figure:
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(7,8,13,0)",
        plot_bgcolor="rgba(16,23,34,.94)",
        font={"color": TEXT, "family": "Inter, Arial, sans-serif"},
        title={"font": {"color": TEXT, "size": 18}},
        margin={"l": 18, "r": 18, "t": 52, "b": 34},
        colorway=PALETTE,
        legend={"bgcolor": "rgba(17,24,39,.55)", "bordercolor": "rgba(255,255,255,.10)", "borderwidth": 1},
    )
    fig.update_xaxes(gridcolor=GRID, zerolinecolor=GRID, linecolor="rgba(255,255,255,.18)")
    fig.update_yaxes(gridcolor=GRID, zerolinecolor=GRID, linecolor="rgba(255,255,255,.18)")
    return fig


def chart(fig: go.Figure) -> None:
    st.plotly_chart(theme_fig(fig), use_container_width=True)
