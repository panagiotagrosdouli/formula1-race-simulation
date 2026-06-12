from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

POINTS = np.array([25, 18, 15, 12, 10, 8, 6, 4, 2, 1] + [0] * 20, dtype=float)


def bayesian_forecast_intervals(simulation: pd.DataFrame) -> pd.DataFrame:
    if simulation is None or simulation.empty:
        return pd.DataFrame()
    df = simulation.copy()
    expected = pd.to_numeric(df.get("ExpectedFinish"), errors="coerce").fillna(10.5)
    spread = np.clip(2.0 + expected * 0.12, 1.5, 5.0)
    df["FinishLow95"] = np.clip(np.floor(expected - 1.96 * spread / 2.0), 1, 20).astype(int)
    df["FinishHigh95"] = np.clip(np.ceil(expected + 1.96 * spread / 2.0), 1, 20).astype(int)
    df["CredibleInterval"] = "P" + df["FinishLow95"].astype(str) + "-P" + df["FinishHigh95"].astype(str)
    df["UncertaintyIndex"] = (df["FinishHigh95"] - df["FinishLow95"]).astype(float)
    return df


def plot_bayesian_intervals(intervals: pd.DataFrame):
    if intervals.empty:
        return go.Figure()
    df = intervals.sort_values("ExpectedFinish").head(12)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["Driver"], y=df["ExpectedFinish"], error_y=dict(type="data", symmetric=False, array=(df["FinishHigh95"] - df["ExpectedFinish"]).clip(lower=0), arrayminus=(df["ExpectedFinish"] - df["FinishLow95"]).clip(lower=0)), mode="markers", name="Expected finish with 95% interval"))
    fig.update_layout(title="Bayesian-style finish uncertainty intervals", yaxis_title="Finishing position", xaxis_title="Driver", yaxis=dict(autorange="reversed"), height=450)
    return fig


def dynamic_weather_track_evolution(total_laps: int, rain_probability: float, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    wetness = 0.0
    rows = []
    rain_front = float(rain_probability)
    for lap in range(1, int(total_laps) + 1):
        rain_front = float(np.clip(rain_front + rng.normal(0, 0.045), 0, 1))
        rain_event = rng.random() < rain_front * 0.22
        rain_intensity = float(np.clip(rain_front * rng.uniform(0.35, 1.0) if rain_event else rain_front * 0.12, 0, 1))
        wetness = min(1.0, wetness + rain_intensity * 0.18) if rain_event else max(0.0, wetness - 0.045)
        drying_line = float(np.clip(1.0 - wetness + lap / max(1, total_laps) * 0.18, 0, 1))
        grip = float(np.clip(1.0 - wetness * 0.52 + drying_line * 0.08, 0.35, 1.05))
        rows.append({"Lap": lap, "RainFront": round(rain_front, 3), "RainIntensity": round(rain_intensity, 3), "TrackWetness": round(wetness, 3), "DryingLine": round(drying_line, 3), "GripIndex": round(grip, 3)})
    return pd.DataFrame(rows)


def plot_dynamic_weather(weather_df: pd.DataFrame):
    fig = go.Figure()
    for col in ["RainFront", "RainIntensity", "TrackWetness", "DryingLine", "GripIndex"]:
        fig.add_trace(go.Scatter(x=weather_df["Lap"], y=weather_df[col], mode="lines+markers", name=col))
    fig.update_layout(title="Dynamic weather engine", xaxis_title="Lap", yaxis_title="Index", hovermode="x unified", height=460)
    return fig


def race_engineer_recommendations(timeline: pd.DataFrame, weather_df: pd.DataFrame, lap: int) -> pd.DataFrame:
    if timeline is None or timeline.empty:
        return pd.DataFrame()
    lap_df = timeline[timeline["Lap"] == int(lap)].sort_values("RacePosition").copy()
    weather_lap = weather_df[weather_df["Lap"] == int(lap)] if weather_df is not None and not weather_df.empty else pd.DataFrame()
    wetness = float(weather_lap.iloc[0]["TrackWetness"]) if not weather_lap.empty and "TrackWetness" in weather_lap else 0.0
    rows = []
    for _, row in lap_df.head(12).iterrows():
        if bool(row.get("DNF", False)):
            continue
        tyre_age = int(row.get("TyreAge", 0))
        gap = float(row.get("GapToLeader", 0.0))
        pos = int(row.get("RacePosition", 20))
        compound = str(row.get("Compound", "MEDIUM"))
        if wetness > 0.45:
            rec, reason, gain, conf = "BOX FOR INTERS", "Track wetness is high and grip is falling.", 3.2, 0.82
        elif tyre_age >= 27 and pos <= 8:
            rec, reason, gain, conf = "BOX NOW", "Tyre age is beyond the stable window; undercut potential is high.", 2.1, 0.76
        elif gap <= 1.2 and pos > 1:
            rec, reason, gain, conf = "PUSH / DRS ATTACK", "Car is inside attacking range.", 0.8, 0.68
        elif tyre_age < 14 and pos <= 5:
            rec, reason, gain, conf = "EXTEND STINT", "Tyres are efficient and track position is valuable.", 1.0, 0.64
        else:
            rec, reason, gain, conf = "HOLD STRATEGY", "No strong pit or attack trigger detected.", 0.2, 0.55
        rows.append({"Driver": row["Driver"], "Position": pos, "Compound": compound, "TyreAge": tyre_age, "Recommendation": rec, "Reason": reason, "ExpectedGain": round(float(gain), 2), "Confidence": round(float(conf), 2)})
    return pd.DataFrame(rows).sort_values(["Confidence", "ExpectedGain"], ascending=False)


def analyst_explanation(forecast: pd.DataFrame, simulation: pd.DataFrame, driver: str) -> str:
    if forecast is None or forecast.empty:
        return "No forecast data available."
    f = forecast[forecast["Driver"] == driver]
    s = simulation[simulation["Driver"] == driver] if simulation is not None and not simulation.empty else pd.DataFrame()
    if f.empty:
        return f"No forecast row found for {driver}."
    row = f.iloc[0]
    sim = s.iloc[0] if not s.empty else None
    rank = int(row.get("PredictedRank", row.get("PredictedFinishPosition", 0)))
    win = float(sim.get("WinProbability", 0)) if sim is not None else 0.0
    podium = float(sim.get("PodiumProbability", 0)) if sim is not None else 0.0
    team_strength = float(row.get("TeamStrength", 0.5))
    recent = float(row.get("RecentForm", rank))
    risk = float(row.get("RaceRiskScore", row.get("RiskAdjustment", 0.0)))
    lines = [
        f"Why {driver} is projected around P{rank}:",
        f"- Win probability: {win:.1%}; podium probability: {podium:.1%}.",
        f"- Team-strength signal: {team_strength:.2f}.",
        f"- Recent-form index: {recent:.2f}.",
        f"- Race-risk signal: {risk:.2f}.",
    ]
    if podium > 0.35:
        lines.append("Recommendation: high-upside contender; prioritize track position.")
    elif risk > 0.5:
        lines.append("Recommendation: risk-sensitive strategy with Safety-Car flexibility.")
    else:
        lines.append("Recommendation: optimize via undercut timing and tyre management.")
    return "\n".join(lines)


def season_digital_twin(simulation: pd.DataFrame, races_remaining: int = 12, seed: int = 42) -> pd.DataFrame:
    if simulation is None or simulation.empty:
        return pd.DataFrame()
    rng = np.random.default_rng(seed)
    rows = []
    sim = simulation.copy().reset_index(drop=True)
    for _, row in sim.iterrows():
        expected_finish = float(row.get("ExpectedFinish", 10.5))
        win_p = float(row.get("WinProbability", 0.0))
        podium_p = float(row.get("PodiumProbability", 0.0))
        top10_p = float(row.get("Top10Probability", 0.5))
        expected_points_per_race = max(0.0, np.interp(expected_finish, np.arange(1, 21), POINTS[:20]))
        consistency = np.clip(1.0 - expected_finish / 24.0, 0.05, 0.95)
        expected_points = expected_points_per_race * races_remaining
        title_probability = np.clip((win_p * 0.55 + podium_p * 0.25 + consistency * 0.20) ** 2, 0, 1)
        dnf_probability = np.clip(0.015 + (1.0 - top10_p) * 0.035 + rng.normal(0, 0.003), 0.005, 0.15)
        rows.append({"Driver": row["Driver"], "Team": row.get("Team", ""), "ExpectedSeasonPoints": round(float(expected_points), 1), "TitleProbability": round(float(title_probability), 4), "PodiumProbability": round(float(podium_p), 4), "DNFProbability": round(float(dnf_probability), 4), "ConsistencyIndex": round(float(consistency), 3)})
    return pd.DataFrame(rows).sort_values("ExpectedSeasonPoints", ascending=False).reset_index(drop=True)


def plot_season_twin(twin: pd.DataFrame):
    if twin.empty:
        return go.Figure()
    return px.bar(twin.head(12), x="Driver", y="ExpectedSeasonPoints", color="TitleProbability", title="Season Digital Twin", hover_data=["Team", "PodiumProbability", "DNFProbability"])


def strategy_policy_agent(timeline: pd.DataFrame, weather_df: pd.DataFrame, driver: str, seed: int = 42) -> pd.DataFrame:
    if timeline is None or timeline.empty:
        return pd.DataFrame()
    rng = np.random.default_rng(seed)
    rows = []
    driver_df = timeline[timeline["Driver"] == driver].sort_values("Lap")
    for _, row in driver_df.iterrows():
        lap = int(row["Lap"])
        pos = int(row.get("RacePosition", 20))
        tyre_age = int(row.get("TyreAge", 0))
        gap = float(row.get("GapToLeader", 0.0))
        weather_lap = weather_df[weather_df["Lap"] == lap] if weather_df is not None and not weather_df.empty else pd.DataFrame()
        wetness = float(weather_lap.iloc[0]["TrackWetness"]) if not weather_lap.empty and "TrackWetness" in weather_lap else 0.0
        pit_value = tyre_age * 0.16 + wetness * 2.5 - pos * 0.04 - gap * 0.015 + rng.normal(0, 0.05)
        stay_value = 2.2 - tyre_age * 0.07 - wetness * 1.2 + max(0, 6 - pos) * 0.12 + rng.normal(0, 0.05)
        action = "PIT" if pit_value > stay_value else "STAY OUT"
        rows.append({"Lap": lap, "Position": pos, "TyreAge": tyre_age, "GapToLeader": round(gap, 3), "TrackWetness": round(wetness, 3), "PitValue": round(float(pit_value), 3), "StayOutValue": round(float(stay_value), 3), "AgentAction": action, "Advantage": round(float(abs(pit_value - stay_value)), 3)})
    return pd.DataFrame(rows)


def plot_strategy_agent(agent_df: pd.DataFrame):
    if agent_df.empty:
        return go.Figure()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=agent_df["Lap"], y=agent_df["PitValue"], mode="lines+markers", name="Pit value"))
    fig.add_trace(go.Scatter(x=agent_df["Lap"], y=agent_df["StayOutValue"], mode="lines+markers", name="Stay-out value"))
    fig.update_layout(title="Strategy policy agent: pit vs stay-out values", xaxis_title="Lap", yaxis_title="Policy value", hovermode="x unified", height=430)
    return fig
