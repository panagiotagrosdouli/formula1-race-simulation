"""Main Streamlit entrypoint for the deployed F1 AI Analytics Platform.

Run with:
    streamlit run app/f1_analytics_platform.py

The deployed Streamlit Cloud app points here. This file loads the HUD command
center and applies the visible Base44-style live branding before execution.
"""

from pathlib import Path


HUD_APP = Path(__file__).with_name("f1_hud_platform.py")
hud_source = HUD_APP.read_text(encoding="utf-8")

BASE44_GLOBAL_CSS = """
<style>
:root {
    --b44-bg: #07080d;
    --b44-surface: #101722;
    --b44-surface-2: #151f2e;
    --b44-border: rgba(255, 255, 255, 0.10);
    --b44-primary: #e10600;
    --b44-primary-soft: #ff4d4d;
    --b44-text: #f9fafb;
    --b44-muted: #9ca3af;
}

.stApp {
    background:
        radial-gradient(circle at 50% -15%, rgba(225, 6, 0, 0.18), transparent 34%),
        linear-gradient(135deg, #030407 0%, var(--b44-bg) 48%, #0c111b 100%) !important;
    color: var(--b44-text) !important;
}

[data-testid="stHeader"] {
    background: rgba(7, 8, 13, 0.78) !important;
    backdrop-filter: blur(18px) !important;
    border-bottom: 1px solid rgba(255,255,255,0.06) !important;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #07080d 0%, #0f172a 100%) !important;
    border-right: 1px solid rgba(225, 6, 0, 0.30) !important;
}

.block-container {
    max-width: 1680px !important;
    padding-top: 1.15rem !important;
}

h1, h2, h3 {
    letter-spacing: -0.04em !important;
    color: #ffffff !important;
}

.hud-title {
    border: 1px solid rgba(225, 6, 0, 0.34) !important;
    border-radius: 28px !important;
    background:
        linear-gradient(135deg, rgba(225, 6, 0, 0.20), rgba(16, 23, 34, 0.96)),
        radial-gradient(circle at 90% 10%, rgba(225, 6, 0, 0.15), transparent 20rem) !important;
    box-shadow: 0 26px 80px rgba(0,0,0,0.35), inset 0 1px 0 rgba(255,255,255,0.05) !important;
}

.hud-title h1 {
    font-size: clamp(2.15rem, 3.2vw, 3.15rem) !important;
    font-weight: 900 !important;
}

.hud-title p {
    color: #fecaca !important;
    font-weight: 850 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.055em !important;
}

.hud-title .hud-caption {
    color: #d1d5db !important;
    line-height: 1.6 !important;
}

.hud-card, div[data-testid="stMetric"] {
    background: linear-gradient(180deg, rgba(21, 31, 46, 0.96), rgba(16, 23, 34, 0.92)) !important;
    border: 1px solid var(--b44-border) !important;
    border-top: 2px solid var(--b44-primary) !important;
    border-radius: 20px !important;
    box-shadow: 0 18px 45px rgba(0,0,0,0.26), inset 0 1px 0 rgba(255,255,255,0.04) !important;
}

.hud-card h3, div[data-testid="stMetricLabel"] {
    color: var(--b44-muted) !important;
    font-weight: 800 !important;
    letter-spacing: 0.07em !important;
    text-transform: uppercase !important;
}

.hud-value, div[data-testid="stMetricValue"] {
    color: #ffffff !important;
    font-weight: 900 !important;
}

.hud-sub {
    color: var(--b44-muted) !important;
}

.hud-feed, .replay-panel {
    background: rgba(16, 23, 34, 0.86) !important;
    border: 1px solid var(--b44-border) !important;
    border-left: 3px solid var(--b44-primary) !important;
    border-radius: 16px !important;
    box-shadow: 0 14px 34px rgba(0,0,0,0.22) !important;
}

.hud-badge {
    background: rgba(225, 6, 0, 0.16) !important;
    border: 1px solid rgba(225, 6, 0, 0.42) !important;
    color: #fecaca !important;
    border-radius: 999px !important;
}

[data-testid="stDataFrame"] {
    border: 1px solid var(--b44-border) !important;
    border-radius: 18px !important;
    overflow: hidden !important;
    background: rgba(16, 23, 34, 0.72) !important;
}

.stButton > button, .stDownloadButton > button {
    border-radius: 999px !important;
    border: 1px solid rgba(255, 100, 95, 0.50) !important;
    background: linear-gradient(135deg, var(--b44-primary), #8b0000) !important;
    color: #ffffff !important;
    font-weight: 900 !important;
    box-shadow: 0 12px 28px rgba(225, 6, 0, 0.20) !important;
}

.stButton > button:hover, .stDownloadButton > button:hover {
    border-color: rgba(255, 160, 155, 0.90) !important;
    filter: brightness(1.08) !important;
}

div[data-baseweb="select"] > div,
input,
textarea {
    background-color: rgba(16, 23, 34, 0.96) !important;
    color: var(--b44-text) !important;
    border-color: rgba(255,255,255,0.14) !important;
    border-radius: 14px !important;
}

section[data-testid="stTabs"] button {
    color: #f8fafc !important;
    font-weight: 850 !important;
}

.stAlert {
    border-radius: 16px !important;
}
</style>
"""

# Visible deployment marker: if this text appears, Streamlit is running the
# current main-branch entrypoint and not an older cached app.
hud_source = hud_source.replace(
    "F1 Race Engineering Command Center",
    "F1 Base44 Elite Race Engineering",
)
hud_source = hud_source.replace(
    "Live Race Control • Strategy Intelligence • Telemetry • Weather Radar • Replay Pro",
    "BASE44 ELITE LIVE BUILD • Race Control • Strategy Intelligence • Telemetry • Replay Pro",
)
hud_source = hud_source.replace(
    "A professional HUD for simulated race-state analysis: leaderboard, track map, weather evolution,\n            team radio, race director decisions, driver telemetry and AI race briefing in one cockpit.",
    "A unified Base44-style Formula 1 analytics cockpit with clean cards, consistent dark theme,\n            live race simulation, strategy intelligence, telemetry, weather radar and AI race briefing.",
)
hud_source = hud_source.replace(
    "st.markdown(HUD_CSS, unsafe_allow_html=True)",
    "st.markdown(HUD_CSS + BASE44_GLOBAL_CSS, unsafe_allow_html=True)",
)
hud_source = hud_source.replace(
    'plot_bgcolor="rgba(7, 10, 16, 0.96)"',
    'plot_bgcolor="rgba(16, 23, 34, 0.94)"',
)
hud_source = hud_source.replace(
    'font={"color": TEXT, "family": "Arial, sans-serif"}',
    'font={"color": TEXT, "family": "Inter, Arial, sans-serif"}',
)

exec(hud_source, globals())
