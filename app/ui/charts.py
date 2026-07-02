"""Plotly chart helpers for the F1 Base44 Elite UI."""

from __future__ import annotations

import plotly.graph_objects as go
import streamlit as st

from app.ui.theme import TOKENS


def theme_fig(fig: go.Figure) -> go.Figure:
    """Apply the product Plotly theme to a figure."""

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(7,8,13,0)",
        plot_bgcolor="rgba(16,23,34,.94)",
        font={"color": TOKENS.text, "family": "Inter, Arial, sans-serif"},
        title={"font": {"color": TOKENS.text, "size": 18}},
        margin={"l": 18, "r": 18, "t": 52, "b": 34},
        colorway=TOKENS.palette,
        legend={"bgcolor": "rgba(17,24,39,.55)", "bordercolor": TOKENS.border, "borderwidth": 1},
    )
    fig.update_xaxes(gridcolor=TOKENS.grid, zerolinecolor=TOKENS.grid, linecolor="rgba(255,255,255,.18)")
    fig.update_yaxes(gridcolor=TOKENS.grid, zerolinecolor=TOKENS.grid, linecolor="rgba(255,255,255,.18)")
    return fig


def plotly_chart(fig: go.Figure) -> None:
    """Render a themed Plotly chart full width."""

    st.plotly_chart(theme_fig(fig), use_container_width=True)
