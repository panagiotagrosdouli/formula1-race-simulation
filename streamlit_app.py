"""Streamlit Cloud entrypoint.

Streamlit Community Cloud commonly looks for `streamlit_app.py` at the repository root.
This wrapper keeps the deployed entrypoint stable while the main app lives under `app/`.
"""

from __future__ import annotations

from app.f1_analytics_platform import main


main()
