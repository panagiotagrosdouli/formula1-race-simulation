"""Main Streamlit entrypoint for the F1 AI Analytics Platform.

Run with:
    streamlit run app/f1_analytics_platform.py

The main app now loads the HUD-style command center interface.
"""

from pathlib import Path


HUD_APP = Path(__file__).with_name("f1_hud_platform.py")

exec(HUD_APP.read_text(encoding="utf-8"), globals())
