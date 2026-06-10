from __future__ import annotations

import pandas as pd


def _safe_top(df: pd.DataFrame, column: str, n: int = 3) -> pd.DataFrame:
    if df is None or df.empty or column not in df.columns:
        return pd.DataFrame()
    return df.sort_values(column).head(n)


def build_race_intro(race_name: str, forecast: pd.DataFrame | None = None, weather=None) -> str:
    lines = [f"Welcome to the AI race presentation for {race_name}."]

    if weather is not None:
        condition = getattr(weather, "condition", "unknown")
        rain = getattr(weather, "rain_probability", None)
        temp = getattr(weather, "air_temperature", None)
        if rain is not None and temp is not None:
            lines.append(f"Weather conditions are {condition}, with rain probability at {rain * 100:.1f}% and air temperature around {temp:.1f}°C.")
        else:
            lines.append(f"Weather condition: {condition}.")

    if forecast is not None and not forecast.empty:
        leader_col = "PredictedRank" if "PredictedRank" in forecast.columns else "PredictedFinishPosition"
        top = _safe_top(forecast, leader_col, 3)
        if not top.empty:
            podium = ", ".join(top["Driver"].astype(str).tolist())
            lines.append(f"The projected leading group is {podium}.")

    return " ".join(lines)


def build_live_lap_presentation(timeline: pd.DataFrame, lap: int, events: pd.DataFrame | None = None, alerts: pd.DataFrame | None = None, pitstops: pd.DataFrame | None = None) -> str:
    lap_df = timeline[timeline["Lap"] == lap].sort_values("RacePosition") if timeline is not None and not timeline.empty else pd.DataFrame()
    if lap_df.empty:
        return f"Lap {lap}: no timing data is available."

    leader = lap_df.iloc[0]["Driver"]
    p2 = lap_df.iloc[1]["Driver"] if len(lap_df) > 1 else "unknown"
    gap = lap_df.iloc[1]["GapToLeader"] if len(lap_df) > 1 and "GapToLeader" in lap_df.columns else None

    lines = [f"Lap {lap}: {leader} leads the race."]
    if gap is not None:
        lines.append(f"{p2} is second, {float(gap):.2f} seconds behind.")

    if events is not None and not events.empty and "Lap" in events.columns:
        lap_events = events[events["Lap"] == lap]
        for _, event in lap_events.iterrows():
            driver = event.get("Driver", "")
            driver_text = f" for {driver}" if pd.notna(driver) and driver else ""
            lines.append(f"Race control reports {event.get('Event', 'an event')}{driver_text}.")

    if pitstops is not None and not pitstops.empty and "Lap" in pitstops.columns:
        lap_pits = pitstops[pitstops["Lap"] == lap]
        for _, pit in lap_pits.iterrows():
            lines.append(f"{pit.get('Driver')} pits, switching from {pit.get('OldCompound')} to {pit.get('NewCompound')} tyres.")

    if alerts is not None and not alerts.empty and "Lap" in alerts.columns:
        lap_alerts = alerts[alerts["Lap"] == lap]
        for _, alert in lap_alerts.head(3).iterrows():
            lines.append(str(alert.get("Message", "A race alert has been detected.")))

    return " ".join(lines)


def build_driver_spotlight(timeline: pd.DataFrame, driver: str, driver_profile: pd.DataFrame | None = None) -> str:
    driver = driver.upper()
    df = timeline[timeline["Driver"].astype(str).str.upper() == driver].copy() if timeline is not None and not timeline.empty else pd.DataFrame()
    if df.empty:
        return f"Driver spotlight: no race data is available for {driver}."

    df = df.sort_values("Lap")
    start = int(df.iloc[0]["RacePosition"])
    finish = int(df.iloc[-1]["RacePosition"])
    best = int(df["RacePosition"].min())
    pits = int(df.iloc[-1].get("PitStops", 0))
    dnf = bool(df.iloc[-1].get("DNF", False))

    direction = "gained" if finish < start else "lost" if finish > start else "held"
    delta = abs(finish - start)
    status = "retired from the race" if dnf else f"finished P{finish}"

    lines = [f"Driver spotlight for {driver}: started P{start} and {status}."]
    if direction == "held":
        lines.append("The driver maintained the starting position across the simulation.")
    else:
        lines.append(f"The driver {direction} {delta} position(s), with a best race position of P{best}.")
    lines.append(f"Pit stop count: {pits}.")

    if driver_profile is not None and not driver_profile.empty:
        skill_cols = ["Qualifying", "RacePace", "Overtaking", "Defending", "TyreManagement", "WetWeather"]
        available = [c for c in skill_cols if c in driver_profile.columns]
        if available:
            strongest = max(available, key=lambda c: float(driver_profile.iloc[0][c]))
            lines.append(f"The strongest simulated attribute is {strongest}.")

    return " ".join(lines)


def build_team_spotlight(team_profile: pd.DataFrame) -> str:
    if team_profile is None or team_profile.empty:
        return "Team spotlight: no team profile is available."

    row = team_profile.iloc[0]
    team = row.get("Team", "Unknown team")
    overall = row.get("Overall", None)
    best = row.get("BestFinish", None)
    avg = row.get("AverageFinish", None)
    dnfs = row.get("DNFs", None)

    lines = [f"Team spotlight for {team}."]
    if overall is not None:
        lines.append(f"Overall operational rating is {float(overall) * 100:.1f} out of 100.")
    if best is not None and avg is not None:
        lines.append(f"Best classified position is P{int(best)}, with average finish P{float(avg):.2f}.")
    if dnfs is not None:
        lines.append(f"DNF count: {int(dnfs)}.")
    return " ".join(lines)


def build_race_director_presentation(director_log: pd.DataFrame, adjusted_final: pd.DataFrame | None = None) -> str:
    if director_log is None or director_log.empty:
        return "Race Director report: the race was clean, with no major steward interventions."

    incidents = len(director_log)
    penalties = int(director_log["Decision"].astype(str).str.contains("penalty", case=False).sum()) if "Decision" in director_log.columns else 0
    major_flags = int(director_log["Flag"].astype(str).str.contains("Safety Car|Virtual Safety Car|Red Flag", case=False).sum()) if "Flag" in director_log.columns else 0

    lines = [f"Race Director report: {incidents} incident(s) were reviewed."]
    lines.append(f"There were {penalties} penalty decision(s) and {major_flags} major race-control intervention(s).")

    first = director_log.sort_values("Lap").iloc[0]
    lines.append(f"The first notable case came on lap {int(first['Lap'])}: {first.get('Message', first.get('Incident', 'incident'))}")

    if adjusted_final is not None and not adjusted_final.empty and "AdjustedRacePosition" in adjusted_final.columns:
        winner = adjusted_final.sort_values("AdjustedRacePosition").iloc[0]["Driver"]
        lines.append(f"After steward adjustments, the classified winner is {winner}.")

    return " ".join(lines)


def build_full_ai_presentation(state: dict, race_name: str = "selected Grand Prix", lap: int | None = None, driver: str | None = None, team: str | None = None) -> dict[str, str]:
    """Build a complete set of AI presenter scripts from the unified app state."""
    forecast = state.get("forecast")
    weather = state.get("weather")
    timeline = state.get("timeline")
    events = state.get("events")
    pitstops = state.get("pitstops")
    alerts = state.get("alerts")
    director_log = state.get("director_log")
    adjusted_final = state.get("adjusted_final")

    scripts = {
        "Race Intro": build_race_intro(race_name, forecast, weather),
        "Race Director": build_race_director_presentation(director_log, adjusted_final),
    }

    if lap is not None and timeline is not None:
        scripts[f"Lap {lap} Live Presentation"] = build_live_lap_presentation(timeline, lap, events, alerts, pitstops)

    if driver is not None and timeline is not None:
        driver_profiles = state.get("driver_profiles")
        driver_profile = None
        if driver_profiles is not None and not driver_profiles.empty:
            driver_profile = driver_profiles[driver_profiles["Driver"].astype(str).str.upper() == driver.upper()]
        scripts[f"{driver.upper()} Driver Spotlight"] = build_driver_spotlight(timeline, driver, driver_profile)

    if team is not None:
        team_profiles = state.get("team_profiles")
        team_profile = None
        if team_profiles is not None and not team_profiles.empty:
            team_profile = team_profiles[team_profiles["Team"] == team]
        scripts[f"{team} Team Spotlight"] = build_team_spotlight(team_profile)

    return scripts
