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
    df["MarkerSize"] = np.clip(26 - df["RacePosition"].astype(float), 8, 24)
    return df


def add_safety_car_marker(track_df: pd.DataFrame) -> pd.DataFrame:
    """Add a synthetic Safety Car marker whenever the simulated race is under SC.

    The marker is placed slightly ahead of the lap leader on the abstract track map.
    This mirrors the replay concept used by desktop race-replay tools while keeping
    the Streamlit platform fully self-contained and data-frame based.
    """
    if track_df.empty or "Event" not in track_df.columns:
        return track_df

    rows = []
    max_lap = max(int(track_df["Lap"].max()), 1)
    for lap, lap_df in track_df.groupby("Lap"):
        if "SC" not in set(lap_df["Event"].astype(str)):
            continue
        leader = lap_df.sort_values("RacePosition").iloc[0]
        progress = min(0.995, float(lap) / max_lap + 0.065)
        rows.append(
            {
                "Lap": int(lap),
                "Driver": "SC",
                "Team": "Race Control",
                "RacePosition": 0,
                "Compound": "SAFETY CAR",
                "TyreAge": 0,
                "PitStops": 0,
                "DNF": False,
                "GapToLeader": -0.5,
                "Event": "SC",
                "TrackProgress": progress,
                "TrackX": np.cos(2 * np.pi * progress - 0.028),
                "TrackY": np.sin(2 * np.pi * progress - 0.028),
                "MarkerSize": 34,
                "ReferenceLeader": leader.get("Driver", "Leader"),
            }
        )

    if not rows:
        return track_df
    return pd.concat([track_df, pd.DataFrame(rows)], ignore_index=True, sort=False)


def plot_track_map_animation(timeline: pd.DataFrame):
    """Animated abstract track map with all cars moving lap-by-lap."""
    df = add_safety_car_marker(add_track_coordinates(timeline))
    fig = px.scatter(
        df,
        x="TrackX",
        y="TrackY",
        animation_frame="Lap",
        text="Driver",
        color="Compound",
        size="MarkerSize",
        hover_data=["RacePosition", "GapToLeader", "TyreAge", "PitStops", "DNF", "Event"],
        title="Live track map animation",
        range_x=[-1.25, 1.25],
        range_y=[-1.25, 1.25],
    )
    fig.update_traces(textposition="top center")
    fig.update_layout(
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        height=700,
    )
    return fig


def plot_selected_lap_track_map(timeline: pd.DataFrame, lap: int):
    """Static replay frame for the selected lap, including Safety Car marker."""
    df = add_safety_car_marker(add_track_coordinates(timeline))
    lap_df = df[df["Lap"] == int(lap)].copy()
    if lap_df.empty:
        return go.Figure()

    fig = px.scatter(
        lap_df,
        x="TrackX",
        y="TrackY",
        text="Driver",
        color="Compound",
        size="MarkerSize",
        hover_data=["Team", "RacePosition", "GapToLeader", "TyreAge", "PitStops", "DNF", "Event"],
        title=f"Race replay frame — Lap {lap}",
        range_x=[-1.25, 1.25],
        range_y=[-1.25, 1.25],
    )
    fig.update_traces(textposition="top center")
    fig.add_shape(type="circle", x0=-1.08, y0=-1.08, x1=1.08, y1=1.08, line=dict(width=2))
    fig.update_layout(xaxis=dict(visible=False), yaxis=dict(visible=False), height=520)
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


def build_replay_event_stream(
    timeline: pd.DataFrame,
    pitstops: pd.DataFrame,
    events: pd.DataFrame,
    alerts: pd.DataFrame,
    lap: int,
    window: int = 2,
) -> pd.DataFrame:
    """Build a compact race-replay event stream around the selected lap."""
    rows: list[dict[str, object]] = []
    lap_min = max(1, int(lap) - int(window))
    lap_max = int(lap)

    if events is not None and not events.empty:
        for _, row in events[(events["Lap"] >= lap_min) & (events["Lap"] <= lap_max)].iterrows():
            rows.append({"Lap": int(row["Lap"]), "Source": "Race Control", "Message": f"{row.get('Event', 'EVENT')} event logged."})

    if pitstops is not None and not pitstops.empty:
        for _, row in pitstops[(pitstops["Lap"] >= lap_min) & (pitstops["Lap"] <= lap_max)].iterrows():
            rows.append({"Lap": int(row["Lap"]), "Source": "Pit Wall", "Message": f"{row['Driver']} boxed: {row.get('OldCompound')} → {row.get('NewCompound')}."})

    if alerts is not None and not alerts.empty:
        for _, row in alerts[(alerts["Lap"] >= lap_min) & (alerts["Lap"] <= lap_max)].iterrows():
            rows.append({"Lap": int(row["Lap"]), "Source": str(row.get("Type", "Alert")), "Message": str(row.get("Message", ""))})

    lap_df = timeline[timeline["Lap"] == int(lap)].sort_values("RacePosition")
    if not lap_df.empty:
        leader = lap_df.iloc[0]["Driver"]
        rows.append({"Lap": int(lap), "Source": "Replay", "Message": f"{leader} leads; {len(lap_df[lap_df['DNF'] == True])} cars marked DNF."})

    if not rows:
        return pd.DataFrame(columns=["Lap", "Source", "Message"])
    return pd.DataFrame(rows).drop_duplicates().sort_values(["Lap", "Source"]).reset_index(drop=True)


def build_driver_telemetry_snapshot(driver: str, timeline: pd.DataFrame, sectors: pd.DataFrame, lap: int) -> pd.DataFrame:
    """Create a driver-focused telemetry snapshot for the selected replay lap."""
    current = timeline[(timeline["Driver"] == driver) & (timeline["Lap"] == int(lap))]
    sector_row = sectors[(sectors["Driver"] == driver) & (sectors["Lap"] == int(lap))] if sectors is not None else pd.DataFrame()
    if current.empty:
        return pd.DataFrame(columns=["Metric", "Value"])

    row = current.iloc[0]
    gap = float(row.get("GapToLeader", 0.0))
    position = int(row.get("RacePosition", 0))
    tyre_age = int(row.get("TyreAge", 0))
    compound = str(row.get("Compound", "MEDIUM"))

    compound_speed_bonus = {"SOFT": 5.0, "MEDIUM": 2.0, "HARD": 0.0}.get(compound, 1.0)
    estimated_speed = max(160.0, 326.0 - position * 1.8 - tyre_age * 0.35 - gap * 0.08 + compound_speed_bonus)
    gear = int(np.clip(round(estimated_speed / 45.0), 1, 8))
    drs = "Enabled" if gap <= 1.0 and position > 1 and not bool(row.get("DNF", False)) else "Disabled"
    lap_time = float(sector_row.iloc[0]["EstimatedLapTime"]) if not sector_row.empty else np.nan

    return pd.DataFrame(
        [
            {"Metric": "Race position", "Value": f"P{position}"},
            {"Metric": "Estimated speed", "Value": f"{estimated_speed:.1f} km/h"},
            {"Metric": "Gear", "Value": gear},
            {"Metric": "DRS", "Value": drs},
            {"Metric": "Compound", "Value": compound},
            {"Metric": "Tyre age", "Value": f"{tyre_age} laps"},
            {"Metric": "Gap to leader", "Value": f"{gap:.3f}s"},
            {"Metric": "Estimated lap time", "Value": "N/A" if np.isnan(lap_time) else f"{lap_time:.3f}s"},
        ]
    )


def plot_driver_telemetry_trace(sectors: pd.DataFrame, timeline: pd.DataFrame, driver: str, lap: int):
    """Plot recent sector and lap-time evolution for a selected driver."""
    if sectors is None or sectors.empty:
        return go.Figure()
    df = sectors[(sectors["Driver"] == driver) & (sectors["Lap"] <= int(lap))].tail(12).copy()
    if df.empty:
        return go.Figure()

    fig = go.Figure()
    for col in ["S1", "S2", "S3"]:
        fig.add_trace(go.Scatter(x=df["Lap"], y=df[col], mode="lines+markers", name=col))
    fig.add_trace(go.Scatter(x=df["Lap"], y=df["EstimatedLapTime"], mode="lines+markers", name="Lap Time", yaxis="y2"))
    fig.update_layout(
        title=f"{driver} telemetry trace",
        xaxis_title="Lap",
        yaxis_title="Sector time",
        yaxis2=dict(title="Lap time", overlaying="y", side="right", showgrid=False),
        hovermode="x unified",
        height=360,
    )
    return fig
