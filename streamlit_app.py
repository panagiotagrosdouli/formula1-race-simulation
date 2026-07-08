"""Root Streamlit Cloud entrypoint for the F1Sim Pro multipage platform."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent
ELITE_HOME = ROOT / "f1_elite_upgrade" / "app" / "Home.py"

exec(ELITE_HOME.read_text(encoding="utf-8"), {"__file__": str(ELITE_HOME), "__name__": "__main__"})
