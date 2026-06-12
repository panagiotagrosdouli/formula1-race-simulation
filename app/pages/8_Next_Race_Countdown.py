import sys
from datetime import timezone
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT))

from src.f1predictor.f1_calendar import calendar_dataframe, countdown_components, countdown_label, get_next_race, get_previous_race, now_utc

st.set_page_config(page_title="Next Race Countdown", layout="wide")

st.title("⏱️ Next Race Countdown")
st.caption("Automatic next-race detection from the platform calendar, using the current UTC date and time.")

current_time = now_utc()
next_race = get_next_race(current_time)
previous_race = get_previous_race(current_time)

if next_race is None:
    st.success("The stored 2026 calendar has no remaining races. Update src/f1predictor/f1_calendar.py for the next season.")
else:
    countdown = countdown_components(next_race, current_time)
    st.markdown("## Next Grand Prix")
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Grand Prix", next_race.name)
    c2.metric("Round", next_race.round_no)
    c3.metric("Circuit", next_race.circuit)
    c4.metric("Location", next_race.location)
    c5.metric("Countdown", countdown_label(next_race, current_time))

    d1, d2, d3, d4 = st.columns(4)
    d1.metric("Days", countdown["days"])
    d2.metric("Hours", countdown["hours"])
    d3.metric("Minutes", countdown["minutes"])
    d4.metric("Seconds", countdown["seconds"])

    st.markdown("## Race Start")
    start_cols = st.columns(3)
    start_cols[0].metric("UTC", next_race.start_utc.strftime("%Y-%m-%d %H:%M"))
    start_cols[1].metric("Athens Time", next_race.start_local.strftime("%Y-%m-%d %H:%M"))
    start_cols[2].metric("Current UTC", current_time.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"))

    st.progress(min(1.0, max(0.0, 1.0 - countdown["total_seconds"] / (14 * 24 * 3600))))
    st.info("The progress bar is scaled over a two-week race build-up window.")

if previous_race is not None:
    st.markdown("## Previous Race")
    p1, p2, p3 = st.columns(3)
    p1.metric("Grand Prix", previous_race.name)
    p2.metric("Round", previous_race.round_no)
    p3.metric("Circuit", previous_race.circuit)

st.markdown("## 2026 Calendar Tracker")
st.dataframe(calendar_dataframe(current_time), use_container_width=True, hide_index=True)

st.markdown("## Suggested Platform Actions")
st.write(
    "Use this page as the entry point for the next race build-up: run forecasting, open Replay Pro, simulate strategies, and generate the AI race preview."
)
