from __future__ import annotations

import plotly.graph_objects as go
import streamlit as st

FERRARI_RED = "#e10600"
FERRARI_DARK_RED = "#8b0000"
CARBON = "#05070d"
PANEL = "#111827"
TEXT = "#f9fafb"
MUTED = "#9ca3af"
GRID = "rgba(255,255,255,0.08)"
BORDER = "rgba(225, 6, 0, 0.34)"
PLOT_PALETTE = [FERRARI_RED, "#ff4d4d", "#f97316", "#facc15", "#38bdf8", "#60a5fa", "#a78bfa"]


def apply_theme() -> None:
    st.markdown(
        f"""
        <style>
        .stApp {{
            background:
                radial-gradient(circle at 50% 0%, rgba(225, 6, 0, 0.16), transparent 32%),
                linear-gradient(135deg, #020203 0%, #05070d 52%, #0b0f14 100%);
            color: {TEXT};
        }}
        [data-testid="stHeader"] {{
            background: rgba(5, 7, 13, 0.68);
            backdrop-filter: blur(14px);
        }}
        [data-testid="stSidebar"] {{
            background: linear-gradient(180deg, #050505, #0a0d12 55%, #050505);
            border-right: 1px solid {BORDER};
        }}
        .block-container {{
            max-width: 1500px;
            padding-top: 1.2rem;
            padding-bottom: 2.2rem;
        }}
        h1, h2, h3 {{
            letter-spacing: -0.035em;
            color: #ffffff;
        }}
        .elite-hero {{
            border: 1px solid {BORDER};
            border-radius: 24px;
            padding: 24px 28px;
            background: linear-gradient(135deg, rgba(225, 6, 0, 0.22), rgba(17, 24, 39, 0.94));
            box-shadow: 0 24px 72px rgba(0,0,0,0.34), inset 0 1px 0 rgba(255,255,255,0.05);
            margin-bottom: 1.1rem;
        }}
        .elite-hero h1 {{
            margin: 0;
            font-size: clamp(2rem, 3.4vw, 2.75rem);
        }}
        .elite-hero p {{
            color: #d1d5db;
            max-width: 1000px;
            margin: 0.65rem 0 0 0;
            line-height: 1.6;
        }}
        .elite-pill {{
            display: inline-block;
            padding: 0.3rem 0.7rem;
            margin: 0.75rem 0.35rem 0 0;
            border-radius: 999px;
            background: rgba(225, 6, 0, 0.16);
            border: 1px solid rgba(255, 100, 95, 0.36);
            color: #fecaca;
            font-weight: 800;
            font-size: 0.78rem;
            letter-spacing: 0.04em;
            text-transform: uppercase;
        }}
        .elite-panel {{
            border: 1px solid rgba(255,255,255,0.10);
            border-left: 4px solid {FERRARI_RED};
            border-radius: 18px;
            padding: 16px 18px;
            background: rgba(17, 24, 39, 0.78);
            margin: 0.8rem 0 1rem 0;
        }}
        .elite-panel p {{
            color: #d1d5db;
            line-height: 1.55;
            margin-bottom: 0;
        }}
        div[data-testid="stMetric"] {{
            border: 1px solid rgba(255,255,255,0.10);
            border-radius: 16px;
            padding: 14px 16px;
            background: linear-gradient(180deg, rgba(31, 41, 55, 0.88), rgba(17, 24, 39, 0.82));
        }}
        .stButton > button {{
            border-radius: 999px;
            border: 1px solid rgba(255, 100, 95, 0.5);
            background: linear-gradient(135deg, {FERRARI_RED}, {FERRARI_DARK_RED});
            color: white;
            font-weight: 800;
        }}
        [data-testid="stDataFrame"] {{
            border: 1px solid rgba(255,255,255,0.10);
            border-radius: 14px;
            overflow: hidden;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def hero(title: str, subtitle: str, pills: list[str] | None = None) -> None:
    pill_html = "".join(f"<span class='elite-pill'>{pill}</span>" for pill in (pills or []))
    st.markdown(
        f"""
        <div class="elite-hero">
            <h1>{title}</h1>
            <p>{subtitle}</p>
            {pill_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def panel(title: str, body: str) -> None:
    st.markdown(f"<div class='elite-panel'><h3>{title}</h3><p>{body}</p></div>", unsafe_allow_html=True)


def theme_fig(fig: go.Figure) -> go.Figure:
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(5, 7, 13, 0)",
        plot_bgcolor="rgba(17, 24, 39, 0.94)",
        font={"color": TEXT, "family": "Arial, sans-serif"},
        title={"font": {"color": TEXT, "size": 18}},
        margin={"l": 18, "r": 18, "t": 52, "b": 34},
        colorway=PLOT_PALETTE,
        legend={"bgcolor": "rgba(17,24,39,0.55)", "bordercolor": "rgba(255,255,255,0.10)", "borderwidth": 1},
    )
    fig.update_xaxes(gridcolor=GRID, zerolinecolor=GRID, linecolor="rgba(255,255,255,0.18)")
    fig.update_yaxes(gridcolor=GRID, zerolinecolor=GRID, linecolor="rgba(255,255,255,0.18)")
    return fig


def chart(fig: go.Figure) -> None:
    st.plotly_chart(theme_fig(fig), use_container_width=True)
