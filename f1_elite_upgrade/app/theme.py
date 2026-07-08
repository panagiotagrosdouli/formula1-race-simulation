from __future__ import annotations

import html

import plotly.graph_objects as go
import streamlit as st

PRIMARY = "#e10600"
PRIMARY_DARK = "#8b0000"
BG = "#07080d"
SURFACE = "#111827"
SURFACE_SOFT = "#1f2937"
TEXT = "#f9fafb"
MUTED = "#9ca3af"
GRID = "rgba(255,255,255,0.08)"
BORDER = "rgba(255,255,255,0.10)"
BRAND_BORDER = "rgba(225, 6, 0, 0.34)"
PLOT_PALETTE = [PRIMARY, "#ff4d4d", "#f97316", "#facc15", "#38bdf8", "#60a5fa", "#a78bfa"]
FERRARI_RED = PRIMARY


def apply_theme() -> None:
    st.markdown(
        f"""
        <style>
        :root {{
            --elite-primary: {PRIMARY};
            --elite-primary-dark: {PRIMARY_DARK};
            --elite-bg: {BG};
            --elite-surface: {SURFACE};
            --elite-surface-soft: {SURFACE_SOFT};
            --elite-text: {TEXT};
            --elite-muted: {MUTED};
            --elite-border: {BORDER};
        }}

        .stApp {{
            background:
                radial-gradient(circle at 50% -10%, rgba(225, 6, 0, 0.16), transparent 34%),
                linear-gradient(135deg, #030407 0%, var(--elite-bg) 46%, #0c111b 100%);
            color: var(--elite-text);
        }}

        [data-testid="stHeader"] {{
            background: rgba(7, 8, 13, 0.72);
            backdrop-filter: blur(18px);
            border-bottom: 1px solid rgba(255,255,255,0.06);
        }}

        [data-testid="stSidebar"] {{
            background:
                linear-gradient(180deg, rgba(8, 10, 16, 0.98), rgba(12, 17, 27, 0.98));
            border-right: 1px solid {BRAND_BORDER};
        }}

        .block-container {{
            max-width: 1500px;
            padding-top: 1.15rem;
            padding-bottom: 2.3rem;
        }}

        h1, h2, h3 {{
            color: #ffffff;
            letter-spacing: -0.04em;
        }}

        .elite-hero {{
            border: 1px solid {BRAND_BORDER};
            border-radius: 26px;
            padding: 26px 30px;
            background:
                linear-gradient(135deg, rgba(225, 6, 0, 0.20), rgba(17, 24, 39, 0.94)),
                radial-gradient(circle at 88% 12%, rgba(225, 6, 0, 0.14), transparent 20rem);
            box-shadow: 0 24px 72px rgba(0,0,0,0.32), inset 0 1px 0 rgba(255,255,255,0.05);
            margin-bottom: 1.15rem;
        }}

        .elite-hero h1 {{
            margin: 0;
            font-size: clamp(2rem, 3.4vw, 2.85rem);
            line-height: 1.05;
        }}

        .elite-hero p {{
            color: #d1d5db;
            max-width: 1050px;
            margin: 0.7rem 0 0 0;
            line-height: 1.62;
            font-size: 1.01rem;
        }}

        .elite-pill {{
            display: inline-block;
            padding: 0.34rem 0.76rem;
            margin: 0.85rem 0.35rem 0 0;
            border-radius: 999px;
            background: rgba(225, 6, 0, 0.15);
            border: 1px solid rgba(255, 100, 95, 0.36);
            color: #fecaca;
            font-weight: 800;
            font-size: 0.76rem;
            letter-spacing: 0.05em;
            text-transform: uppercase;
        }}

        .elite-panel {{
            border: 1px solid var(--elite-border);
            border-left: 4px solid var(--elite-primary);
            border-radius: 18px;
            padding: 17px 19px;
            background: rgba(17, 24, 39, 0.78);
            margin: 0.8rem 0 1rem 0;
            box-shadow: 0 16px 42px rgba(0,0,0,0.18);
        }}

        .elite-panel h3 {{
            margin-top: 0;
            margin-bottom: 0.45rem;
        }}

        .elite-panel p {{
            color: #d1d5db;
            line-height: 1.56;
            margin-bottom: 0;
        }}

        .status-grid {{
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: 0.85rem;
            margin: 1rem 0 1.15rem;
        }}

        .status-card {{
            border: 1px solid var(--elite-border);
            border-radius: 20px;
            padding: 1rem 1.05rem;
            background: linear-gradient(180deg, rgba(31, 41, 55, 0.92), rgba(17, 24, 39, 0.86));
            box-shadow: 0 18px 50px rgba(0,0,0,0.22), inset 0 1px 0 rgba(255,255,255,0.05);
        }}

        .status-card .label {{
            color: var(--elite-muted);
            font-size: 0.72rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            font-weight: 850;
        }}

        .status-card .value {{
            margin-top: 0.24rem;
            color: #ffffff;
            font-size: 1.55rem;
            font-weight: 900;
            letter-spacing: -0.04em;
        }}

        .status-card .caption {{
            margin-top: 0.35rem;
            color: #cbd5e1;
            line-height: 1.45;
            font-size: 0.84rem;
        }}

        .workflow-card {{
            border: 1px solid rgba(225, 6, 0, 0.28);
            border-radius: 22px;
            padding: 1rem 1.1rem;
            background: rgba(7,8,13,0.60);
        }}

        .workflow-step {{
            border-left: 3px solid rgba(225,6,0,0.9);
            padding: 0.4rem 0 0.4rem 0.9rem;
            margin: 0.55rem 0;
            color: #d1d5db;
        }}

        div[data-testid="stMetric"] {{
            border: 1px solid var(--elite-border);
            border-radius: 18px;
            padding: 15px 17px;
            background:
                linear-gradient(180deg, rgba(31, 41, 55, 0.90), rgba(17, 24, 39, 0.84));
            box-shadow: inset 0 1px 0 rgba(255,255,255,0.05);
        }}

        div[data-testid="stMetricLabel"] {{ color: var(--elite-muted); }}
        div[data-testid="stMetricValue"] {{ color: #ffffff; }}

        .stButton > button, .stDownloadButton > button {{
            border-radius: 999px;
            border: 1px solid rgba(255, 100, 95, 0.50);
            background: linear-gradient(135deg, var(--elite-primary), var(--elite-primary-dark));
            color: #ffffff;
            font-weight: 850;
            box-shadow: 0 12px 28px rgba(225, 6, 0, 0.20);
        }}

        .stButton > button:hover, .stDownloadButton > button:hover {{
            border-color: rgba(255, 160, 155, 0.90);
            filter: brightness(1.07);
        }}

        [data-testid="stDataFrame"] {{
            border: 1px solid var(--elite-border);
            border-radius: 16px;
            overflow: hidden;
            background: rgba(17, 24, 39, 0.72);
        }}

        div[data-baseweb="select"] > div,
        input,
        textarea {{
            background-color: rgba(17, 24, 39, 0.96) !important;
            color: var(--elite-text) !important;
            border-color: rgba(255,255,255,0.14) !important;
        }}

        .stAlert {{
            border-radius: 16px;
        }}

        @media (max-width: 1050px) {{
            .status-grid {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
        }}
        @media (max-width: 650px) {{
            .status-grid {{ grid-template-columns: 1fr; }}
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def hero(title: str, subtitle: str, pills: list[str] | None = None) -> None:
    pill_html = "".join(f"<span class='elite-pill'>{html.escape(pill)}</span>" for pill in (pills or []))
    st.markdown(
        f"""
        <div class="elite-hero">
            <h1>{html.escape(title)}</h1>
            <p>{html.escape(subtitle)}</p>
            {pill_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def panel(title: str, body: str) -> None:
    st.markdown(
        f"<div class='elite-panel'><h3>{html.escape(title)}</h3><p>{html.escape(body)}</p></div>",
        unsafe_allow_html=True,
    )


def status_cards(items: list[tuple[str, str, str]]) -> None:
    cards = "".join(
        "<div class='status-card'>"
        f"<div class='label'>{html.escape(label)}</div>"
        f"<div class='value'>{html.escape(value)}</div>"
        f"<div class='caption'>{html.escape(caption)}</div>"
        "</div>"
        for label, value, caption in items
    )
    st.markdown(f"<div class='status-grid'>{cards}</div>", unsafe_allow_html=True)


def workflow_steps(steps: list[tuple[str, str]]) -> None:
    content = "".join(
        f"<div class='workflow-step'><b>{html.escape(title)}</b> — {html.escape(body)}</div>"
        for title, body in steps
    )
    st.markdown(f"<div class='workflow-card'>{content}</div>", unsafe_allow_html=True)


def theme_fig(fig: go.Figure) -> go.Figure:
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(7, 8, 13, 0)",
        plot_bgcolor="rgba(17, 24, 39, 0.94)",
        font={"color": TEXT, "family": "Inter, Arial, sans-serif"},
        title={"font": {"color": TEXT, "size": 18}},
        margin={"l": 18, "r": 18, "t": 52, "b": 34},
        colorway=PLOT_PALETTE,
        legend={
            "bgcolor": "rgba(17,24,39,0.55)",
            "bordercolor": "rgba(255,255,255,0.10)",
            "borderwidth": 1,
        },
    )
    fig.update_xaxes(gridcolor=GRID, zerolinecolor=GRID, linecolor="rgba(255,255,255,0.18)")
    fig.update_yaxes(gridcolor=GRID, zerolinecolor=GRID, linecolor="rgba(255,255,255,0.18)")
    return fig


def chart(fig: go.Figure) -> None:
    st.plotly_chart(theme_fig(fig), use_container_width=True)
