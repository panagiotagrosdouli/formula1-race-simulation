"""Main Streamlit entrypoint for the deployed F1 AI Analytics Platform.

Run with:
    streamlit run app/f1_analytics_platform.py

The deployed Streamlit Cloud app points here. This file loads the HUD command
center and applies the visible Base44-style live branding before execution.
"""

from pathlib import Path


HUD_APP = Path(__file__).with_name("f1_hud_platform.py")
hud_source = HUD_APP.read_text(encoding="utf-8")

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

exec(hud_source, globals())
