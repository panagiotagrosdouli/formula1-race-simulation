from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.express as px

INCIDENT_TYPES = [
    "Track Limits",
    "Collision",
    "Unsafe Release",
    "Mechanical Issue",
    "Puncture",
    "Spin",
    "Debris",
]

PENALTY_MAP = {
    "Track Limits": "5-second penalty",
    "Collision": "10-second penalty",
    "Unsafe Release": "5-second penalty",
    "Mechanical Issue": "No penalty",
    "Puncture": "No penalty",
    "Spin": "No penalty",
    "Debris": "No penalty",
}

FLAG_MAP = {
    "Track Limits": "Black/White Warning",
    "Collision": "Yellow Flag",
    "Unsafe Release": "Investigation",
    "Mechanical Issue": "Virtual Safety Car",
    "Puncture": "Yellow Flag",
    "Spin": "Yellow Flag",
    "Debris": "Safety Car",
}


def generate_race_director_log(
    timeline: pd.DataFrame,
    random_state: int = 42,
    incident_rate: float = 0.055,
) -> pd.DataFrame:
    """Generate simulated race-control incidents and steward decisions."""
    rng = np.random.default_rng(random_state)
    drivers = sorted(timeline["Driver"].astype(str).unique())
    laps = sorted(timeline["Lap"].unique())
    rows = []

    for lap in laps:
        if rng.random() > incident_rate:
            continue

        incident = rng.choice(INCIDENT_TYPES)
        driver = rng.choice(drivers)
        opponent = None
        if incident in {"Collision", "Unsafe Release"} and len(drivers) > 1:
            choices = [d for d in drivers if d != driver]
            opponent = rng.choice(choices)

        severity = float(rng.uniform(0.15, 1.0))
        flag = FLAG_MAP[incident]
        penalty = PENALTY_MAP[incident]

        if incident == "Collision" and severity > 0.75:
            flag = "Safety Car"
        if incident == "Debris" and severity > 0.85:
            flag = "Red Flag"
        if incident == "Mechanical Issue" and severity > 0.70:
            penalty = "Retirement risk increased"

        rows.append(
            {
                "Lap": int(lap),
                "Incident": incident,
                "Driver": driver,
                "Opponent": opponent,
                "Severity": round(severity, 3),
                "Flag": flag,
                "Decision": penalty,
                "Message": _decision_message(lap, incident, driver, opponent, flag, penalty),
            }
        )

    return pd.DataFrame(rows)


def _decision_message(lap, incident, driver, opponent, flag, penalty) -> str:
    opponent_text = f" involving {opponent}" if opponent else ""
    return f"Lap {lap}: {incident} for {driver}{opponent_text}. {flag}. Decision: {penalty}."


def apply_director_time_penalties(final_order: pd.DataFrame, director_log: pd.DataFrame) -> pd.DataFrame:
    """Apply time penalties to final classification using GapToLeader as a proxy."""
    result = final_order.copy()
    if result.empty or director_log.empty or "Driver" not in result.columns:
        return result

    penalty_seconds = {}
    for _, row in director_log.iterrows():
        decision = str(row.get("Decision", ""))
        driver = row.get("Driver")
        if "5-second" in decision:
            penalty_seconds[driver] = penalty_seconds.get(driver, 0.0) + 5.0
        elif "10-second" in decision:
            penalty_seconds[driver] = penalty_seconds.get(driver, 0.0) + 10.0

    result["PenaltySeconds"] = result["Driver"].map(penalty_seconds).fillna(0.0)
    if "GapToLeader" in result.columns:
        result["AdjustedGapToLeader"] = result["GapToLeader"].astype(float) + result["PenaltySeconds"]
        result = result.sort_values(["DNF", "AdjustedGapToLeader"]).reset_index(drop=True)
        result["AdjustedRacePosition"] = np.arange(1, len(result) + 1)
    return result


def plot_race_director_timeline(director_log: pd.DataFrame):
    if director_log.empty:
        return px.scatter(title="Race director timeline: no incidents")
    return px.scatter(
        director_log,
        x="Lap",
        y="Driver",
        color="Incident",
        size="Severity",
        hover_data=["Opponent", "Flag", "Decision", "Message"],
        title="Race director incident timeline",
    )


def build_steward_summary(director_log: pd.DataFrame) -> pd.DataFrame:
    if director_log.empty:
        return pd.DataFrame(columns=["Metric", "Value"])
    return pd.DataFrame(
        [
            {"Metric": "Total incidents", "Value": len(director_log)},
            {"Metric": "Penalties", "Value": int(director_log["Decision"].astype(str).str.contains("penalty", case=False).sum())},
            {"Metric": "Safety Car / VSC / Red Flag", "Value": int(director_log["Flag"].astype(str).str.contains("Safety Car|Virtual Safety Car|Red Flag", case=False).sum())},
            {"Metric": "Investigations", "Value": int(director_log["Flag"].astype(str).str.contains("Investigation", case=False).sum())},
        ]
    )
