from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


DRS_THRESHOLD_SECONDS = 1.0


def add_track_coordinates(timeline: pd.DataFrame) -> pd.DataFrame:
    """Create abstract track-map coordinates for every car at every lap."""
    df = timeline.copy()
    max_lap = max(int(df["Lap"].max()), 1)
    position_offset = df["RacePosition"].astype(float) * 0.028
    progress = df["Lap"].astype(float) / max_lap

    df["TrackProgress"] = progress
    df["TrackX"] = np.cos(2 * np.pi * progress - position_offset)
    df["TrackY"] = np.sin(2 * np.pi * progress - position_offset)
    return df


def plot_track_map_animation(timeline: pd.DataFrame):
    """Animated abstract track map with all cars moving lap-by-lap."""
    df = add_track_coordinates(timeline)
    fig = px.scatter(
        df,
        x="TrackX",
        y="TrackY",
        animation_frame="Lap",
        text="Driver",
        color="Compound",
        size="RacePosition",
        hover_data=["RacePosition", "GapToLeader", "TyreAge", "PitStops", "DNF", "Event"],
        title="Live track map animation",
        range_x=[-1.25, 1.25],
        range_y=[-1.25, 1.25],
    )
    fig.update_traces(marker_size=20, textposition="top center")
    fig.update_layout(
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        height=700,
    )
    return fig


def estimate_sector_times(timeline: pd.DataFrame) -> pd.DataFrame:
    """Estimate sector timing from gap and position dynamics.

    This is a synthetic timing model intended for simulation dashboards. It does
    not claim to reproduce official FIA timing data.
    """
    df = timeline.copy().sort_values(["Driver", "Lap"])
    df["GapDelta"] = df.groupby("Driver")["GapToLeader"].diff().fillna(0.0)
    df["BaseLapTime"] = 88.0 + df["RacePosition"].astype(float) * 0.06 + df["GapDelta"].clip(-2, 2) * 0.35
    df["S1"] = (df["BaseLapTime"] * 0.322).round(3)
    df["S2"] = (df["BaseLapTime"] * 0.347).round(3)
    df["S3"] = (df["BaseLapTime"] * 0.331).round(3)
    df["EstimatedLapTime"] = (df["S1"] + df["S2"] + df["S3"]).round(3)
    return df


def detect_drs_and_overtake_alerts(timeline: pd.DataFrame) -> pd.DataFrame:
    """Detect DRS range and likely overtake alerts from consecutive race positions."""
    df = timeline.copy().sort_values(["Lap", "RacePosition"])
    alerts = []

    for lap, lap_df in df.groupby("Lap"):
        lap_df = lap_df.sort_values("RacePosition").reset_index(drop=True)
        previous_lap = df[df["Lap"] == lap - 1]

        for i in range(1, len(lap_df)):
            row = lap_df.iloc[i]
            car_ahead = lap_df.iloc[i - 1]
            gap_to_car_ahead = float(row["GapToLeader"] - car_ahead["GapToLeader"])
            in_drs = 0 <= gap_to_car_ahead <= DRS_THRESHOLD_SECONDS and not bool(row.get("DNF", False))

            if in_drs:
                alerts.append(
                    {
                        "Lap": int(lap),
                        "Type": "DRS",
                        "Driver": row["Driver"],
                        "Target": car_ahead["Driver"],
                        "Message": f"{row['Driver']} is within DRS range of {car_ahead['Driver']} ({gap_to_car_ahead:.2f}s).",
                    }
                )

            if not previous_lap.empty:
                prev_driver = previous_lap[previous_lap["Driver"] == row["Driver"]]
                if not prev_driver.empty:
                    gained = int(prev_driver.iloc[0]["RacePosition"] - row["RacePosition"])
                    if gained > 0:
                        alerts.append(
                            {
                                "Lap": int(lap),
                                "Type": "Overtake",
                                "Driver": row["Driver"],
                                "Target": None,
                                "Message": f"{row['Driver']} gained {gained} position(s) on lap {lap}.",
                            }
                        )

    return pd.DataFrame(alerts)


def build_weather_radar(timeline: pd.DataFrame, base_rain_probability: float = 0.20) -> pd.DataFrame:
    """Create synthetic live weather radar and track evolution series."""
    laps = sorted(timeline["Lap"].unique())
    rows = []
    wetness = 0.0

    for lap in laps:
        lap_events = timeline[timeline["Lap"] == lap]["Event"].astype(str).unique()
        rain_event = "RAIN" in lap_events
        rain_intensity = min(1.0, base_rain_probability + (0.45 if rain_event else 0.0))
        wetness = min(1.0, wetness + rain_intensity * 0.12) if rain_event else max(0.0, wetness - 0.035)
        grip = max(0.35, 1.0 - wetness * 0.55)

        rows.append(
            {
                "Lap": int(lap),
                "RainIntensity": round(float(rain_intensity if rain_event else base_rain_probability * 0.35), 3),
                "TrackWetness": round(float(wetness), 3),
                "TrackGrip": round(float(grip), 3),
            }
        )

    return pd.DataFrame(rows)


def plot_weather_radar(weather_df: pd.DataFrame):
    fig = go.Figure()
    for col in ["RainIntensity", "TrackWetness", "TrackGrip"]:
        fig.add_trace(go.Scatter(x=weather_df["Lap"], y=weather_df[col], mode="lines+markers", name=col))
    fig.update_layout(
        title="Live weather radar and track evolution",
        xaxis_title="Lap",
        yaxis_title="Intensity / grip index",
        hovermode="x unified",
    )
    return fig


def generate_team_radio(timeline: pd.DataFrame, pitstops: pd.DataFrame, alerts: pd.DataFrame) -> pd.DataFrame:
    """Generate automatic team-radio style messages."""
    rows = []

    for _, row in timeline.iterrows():
        if row.get("Event") == "SC":
            rows.append({"Lap": int(row["Lap"]), "Driver": row["Driver"], "Channel": "Race Engineer", "Message": "Safety Car deployed. Keep delta positive."})
        elif row.get("Event") == "VSC":
            rows.append({"Lap": int(row["Lap"]), "Driver": row["Driver"], "Channel": "Race Engineer", "Message": "Virtual Safety Car. Manage tyres and battery."})
        elif row.get("Event") == "RAIN":
            rows.append({"Lap": int(row["Lap"]), "Driver": row["Driver"], "Channel": "Race Engineer", "Message": "Rain reported. Watch the kerbs and manage traction."})

        if int(row.get("TyreAge", 0)) >= 24 and not bool(row.get("DNF", False)):
            rows.append({"Lap": int(row["Lap"]), "Driver": row["Driver"], "Channel": "Pit Wall", "Message": "Tyres are dropping. Box this lap if gap allows."})

        if float(row.get("GapToLeader", 0)) < 2.0 and int(row.get("RacePosition", 99)) <= 3:
            rows.append({"Lap": int(row["Lap"]), "Driver": row["Driver"], "Channel": "Race Engineer", "Message": "Push now. You are fighting for track position."})

    if pitstops is not None and not pitstops.empty:
        for _, row in pitstops.iterrows():
            rows.append({"Lap": int(row["Lap"]), "Driver": row["Driver"], "Channel": "Pit Wall", "Message": f"Box confirmed. Switching {row.get('OldCompound')} to {row.get('NewCompound')}."})

    if alerts is not None and not alerts.empty:
        for _, row in alerts.iterrows():
            if row["Type"] == "DRS":
                rows.append({"Lap": int(row["Lap"]), "Driver": row["Driver"], "Channel": "Race Engineer", "Message": f"DRS available on {row.get('Target')}. Use overtake mode."})

    if not rows:
        return pd.DataFrame(columns=["Lap", "Driver", "Channel", "Message"])

    return pd.DataFrame(rows).drop_duplicates().sort_values(["Lap", "Driver"]).reset_index(drop=True)


def generate_tv_commentary(timeline: pd.DataFrame, alerts: pd.DataFrame, pitstops: pd.DataFrame) -> pd.DataFrame:
    """Generate virtual TV broadcast commentary from race state."""
    rows = []

    for lap, lap_df in timeline.groupby("Lap"):
        lap_df = lap_df.sort_values("RacePosition")
        leader = lap_df.iloc[0]["Driver"]
        rows.append({"Lap": int(lap), "Commentary": f"Lap {lap}: {leader} leads the race."})

    if alerts is not None and not alerts.empty:
        for _, row in alerts.iterrows():
            rows.append({"Lap": int(row["Lap"]), "Commentary": row["Message"]})

    if pitstops is not None and not pitstops.empty:
        for _, row in pitstops.iterrows():
            rows.append({"Lap": int(row["Lap"]), "Commentary": f"{row['Driver']} pits for {row.get('NewCompound')} tyres."})

    return pd.DataFrame(rows).drop_duplicates().sort_values("Lap").reset_index(drop=True)
