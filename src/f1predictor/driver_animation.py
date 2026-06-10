from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def build_driver_animation_frame(timeline: pd.DataFrame, driver: str) -> pd.DataFrame:
    """Prepare a driver-focused animation dataframe from lap-by-lap timeline output."""
    driver = driver.upper()
    df = timeline.copy()
    df["Driver"] = df["Driver"].astype(str).str.upper()

    selected = df[df["Driver"] == driver].copy()
    if selected.empty:
        raise ValueError(f"Driver {driver} was not found in the simulation timeline.")

    selected = selected.sort_values("Lap").reset_index(drop=True)
    selected["Progress"] = selected["Lap"] / selected["Lap"].max()
    selected["TrackX"] = np.cos(2 * np.pi * selected["Progress"])
    selected["TrackY"] = np.sin(2 * np.pi * selected["Progress"])
    selected["PositionLabel"] = "P" + selected["RacePosition"].astype(str)
    selected["Status"] = np.where(selected["DNF"], "DNF", "RUNNING")
    return selected


def plot_single_driver_track_animation(timeline: pd.DataFrame, driver: str):
    """Animated single-driver track trace."""
    selected = build_driver_animation_frame(timeline, driver)

    fig = px.scatter(
        selected,
        x="TrackX",
        y="TrackY",
        animation_frame="Lap",
        text="Driver",
        color="Compound",
        size="RacePosition",
        hover_data=["RacePosition", "GapToLeader", "TyreAge", "PitStops", "Event", "Status"],
        title=f"{driver.upper()} individual race animation",
        range_x=[-1.25, 1.25],
        range_y=[-1.25, 1.25],
    )
    fig.update_traces(marker_size=28, textposition="top center")
    fig.update_layout(
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        height=650,
    )
    return fig


def plot_driver_position_animation(timeline: pd.DataFrame, driver: str):
    """Animated position-over-lap view for one driver."""
    selected = build_driver_animation_frame(timeline, driver)

    fig = px.scatter(
        selected,
        x="Lap",
        y="RacePosition",
        animation_frame="Lap",
        color="Compound",
        size="TyreAge",
        hover_data=["GapToLeader", "PitStops", "Event", "Status"],
        title=f"{driver.upper()} live position animation",
    )
    fig.update_layout(
        yaxis_autorange="reversed",
        xaxis_title="Lap",
        yaxis_title="Race position",
        height=550,
    )
    return fig


def plot_driver_race_story(timeline: pd.DataFrame, driver: str):
    """Static race story chart: position and gap evolution for one driver."""
    selected = build_driver_animation_frame(timeline, driver)

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=selected["Lap"],
            y=selected["RacePosition"],
            mode="lines+markers",
            name="Race position",
            yaxis="y1",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=selected["Lap"],
            y=selected["GapToLeader"],
            mode="lines+markers",
            name="Gap to leader",
            yaxis="y2",
        )
    )
    fig.update_layout(
        title=f"{driver.upper()} race story",
        xaxis_title="Lap",
        yaxis=dict(title="Race position", autorange="reversed"),
        yaxis2=dict(title="Gap to leader (s)", overlaying="y", side="right"),
        hovermode="x unified",
        height=600,
    )
    return fig


def driver_event_summary(timeline: pd.DataFrame, pitstops: pd.DataFrame, driver: str) -> pd.DataFrame:
    """Return driver-specific event/pit summary."""
    driver = driver.upper()
    driver_laps = timeline[timeline["Driver"].astype(str).str.upper() == driver].copy()
    rows = []

    for _, row in driver_laps.iterrows():
        if row.get("Event") != "GREEN":
            rows.append({
                "Lap": int(row["Lap"]),
                "Type": "Race Control",
                "Detail": row.get("Event"),
            })

    if pitstops is not None and not pitstops.empty and "Driver" in pitstops.columns:
        driver_pits = pitstops[pitstops["Driver"].astype(str).str.upper() == driver]
        for _, row in driver_pits.iterrows():
            rows.append({
                "Lap": int(row["Lap"]),
                "Type": "Pit Stop",
                "Detail": f"{row.get('OldCompound')} → {row.get('NewCompound')} ({row.get('PitLoss')}s)",
            })

    if not rows:
        return pd.DataFrame(columns=["Lap", "Type", "Detail"])

    return pd.DataFrame(rows).sort_values("Lap").reset_index(drop=True)
