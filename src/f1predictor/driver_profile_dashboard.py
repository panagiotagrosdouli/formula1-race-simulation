from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from .driver_skill_model import get_driver_skill


def build_driver_profile(driver: str, timeline: pd.DataFrame | None = None) -> pd.DataFrame:
    """Build a one-row driver profile with skill attributes and optional race stats."""
    driver = driver.upper()
    skill = get_driver_skill(driver)

    row = {
        "Driver": driver,
        "Qualifying": skill.qualifying,
        "RacePace": skill.race_pace,
        "Overtaking": skill.overtaking,
        "Defending": skill.defending,
        "TyreManagement": skill.tyre_management,
        "WetWeather": skill.wet_weather,
    }

    if timeline is not None and not timeline.empty:
        df = timeline[timeline["Driver"].astype(str).str.upper() == driver].copy()
        if not df.empty:
            row.update(
                {
                    "StartPosition": int(df.sort_values("Lap").iloc[0]["RacePosition"]),
                    "FinalPosition": int(df.sort_values("Lap").iloc[-1]["RacePosition"]),
                    "BestPosition": int(df["RacePosition"].min()),
                    "WorstPosition": int(df["RacePosition"].max()),
                    "PitStops": int(df.sort_values("Lap").iloc[-1].get("PitStops", 0)),
                    "DNF": bool(df.sort_values("Lap").iloc[-1].get("DNF", False)),
                    "AverageGapToLeader": round(float(df["GapToLeader"].mean()), 3),
                }
            )

    return pd.DataFrame([row])


def build_all_driver_profiles(timeline: pd.DataFrame) -> pd.DataFrame:
    """Build profile cards for every driver in a race timeline."""
    drivers = sorted(timeline["Driver"].astype(str).str.upper().unique())
    return pd.concat([build_driver_profile(driver, timeline) for driver in drivers], ignore_index=True)


def plot_driver_skill_radar(driver: str):
    """Radar chart for driver skill attributes."""
    profile = build_driver_profile(driver)
    categories = ["Qualifying", "RacePace", "Overtaking", "Defending", "TyreManagement", "WetWeather"]
    values = [float(profile.iloc[0][c]) for c in categories]

    fig = go.Figure()
    fig.add_trace(
        go.Scatterpolar(
            r=values + [values[0]],
            theta=categories + [categories[0]],
            fill="toself",
            name=driver.upper(),
        )
    )
    fig.update_layout(
        title=f"{driver.upper()} driver characteristics",
        polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
        showlegend=False,
    )
    return fig


def build_driver_race_status_animation(timeline: pd.DataFrame, driver: str) -> pd.DataFrame:
    """Prepare animated status data showing how a driver evolves through the race."""
    driver = driver.upper()
    df = timeline[timeline["Driver"].astype(str).str.upper() == driver].copy()
    if df.empty:
        raise ValueError(f"Driver {driver} not found in timeline.")

    df = df.sort_values("Lap").reset_index(drop=True)
    df["DriverLabel"] = df["Driver"] + " P" + df["RacePosition"].astype(str)
    df["PerformanceIndex"] = (1 / df["RacePosition"].astype(float)).round(4)
    df["TyreLoad"] = df["TyreAge"].astype(float)
    df["Status"] = df["DNF"].map({True: "DNF", False: "Running"})
    return df


def plot_driver_status_animation(timeline: pd.DataFrame, driver: str):
    """Animated profile card showing position, tyre age and gap lap by lap."""
    df = build_driver_race_status_animation(timeline, driver)
    fig = px.scatter(
        df,
        x="GapToLeader",
        y="RacePosition",
        animation_frame="Lap",
        color="Compound",
        size="TyreLoad",
        text="DriverLabel",
        hover_data=["Team", "PitStops", "TyreAge", "Event", "Status"],
        title=f"{driver.upper()} animated race status",
    )
    fig.update_traces(textposition="top center")
    fig.update_layout(
        yaxis_autorange="reversed",
        xaxis_title="Gap to leader (s)",
        yaxis_title="Race position",
        height=600,
    )
    return fig


def plot_driver_position_by_race(driver_race_table: pd.DataFrame, driver: str):
    """Plot a driver's projected position across races/seasons when season simulation data is available."""
    driver = driver.upper()
    df = driver_race_table.copy()
    if "Driver" not in df.columns:
        raise ValueError("driver_race_table must include a Driver column.")

    df = df[df["Driver"].astype(str).str.upper() == driver].copy()
    if df.empty:
        raise ValueError(f"Driver {driver} not found in race table.")

    x_col = "Race" if "Race" in df.columns else "GrandPrix" if "GrandPrix" in df.columns else df.columns[0]
    y_candidates = ["ProjectedPosition", "ExpectedFinish", "PredictedRank", "RacePosition"]
    y_col = next((c for c in y_candidates if c in df.columns), None)
    if y_col is None:
        raise ValueError("No position column found in driver race table.")

    fig = px.line(
        df,
        x=x_col,
        y=y_col,
        markers=True,
        title=f"{driver} position by race",
        hover_data=[c for c in ["Team", "ExpectedPoints", "Points"] if c in df.columns],
    )
    fig.update_layout(yaxis_autorange="reversed", xaxis_title="Race", yaxis_title="Position")
    return fig


def plot_all_driver_profile_matrix(profiles: pd.DataFrame):
    """Compare all drivers across characteristic dimensions."""
    skill_cols = ["Qualifying", "RacePace", "Overtaking", "Defending", "TyreManagement", "WetWeather"]
    long_df = profiles.melt(id_vars=["Driver"], value_vars=skill_cols, var_name="Attribute", value_name="Score")
    fig = px.bar(
        long_df,
        x="Driver",
        y="Score",
        color="Attribute",
        barmode="group",
        title="Driver characteristic matrix",
    )
    fig.update_layout(yaxis_range=[0, 1])
    return fig
