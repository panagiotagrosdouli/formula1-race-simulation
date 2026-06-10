from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


TEAM_BASELINES = {
    "Red Bull": {"Reliability": 0.93, "Strategy": 0.90, "PitCrew": 0.94, "Development": 0.91},
    "McLaren": {"Reliability": 0.91, "Strategy": 0.88, "PitCrew": 0.90, "Development": 0.94},
    "Ferrari": {"Reliability": 0.87, "Strategy": 0.82, "PitCrew": 0.88, "Development": 0.90},
    "Mercedes": {"Reliability": 0.89, "Strategy": 0.86, "PitCrew": 0.87, "Development": 0.88},
    "Aston Martin": {"Reliability": 0.84, "Strategy": 0.80, "PitCrew": 0.82, "Development": 0.83},
    "Alpine": {"Reliability": 0.78, "Strategy": 0.77, "PitCrew": 0.79, "Development": 0.76},
    "Williams": {"Reliability": 0.80, "Strategy": 0.76, "PitCrew": 0.78, "Development": 0.81},
    "RB": {"Reliability": 0.79, "Strategy": 0.75, "PitCrew": 0.76, "Development": 0.77},
    "Sauber": {"Reliability": 0.76, "Strategy": 0.73, "PitCrew": 0.74, "Development": 0.75},
    "Haas": {"Reliability": 0.77, "Strategy": 0.74, "PitCrew": 0.75, "Development": 0.74},
}


def build_team_profile(team: str, timeline: pd.DataFrame | None = None) -> pd.DataFrame:
    metrics = TEAM_BASELINES.get(team, {"Reliability": 0.80, "Strategy": 0.78, "PitCrew": 0.78, "Development": 0.78})
    row = {"Team": team, **metrics}
    row["Overall"] = round(sum(metrics.values()) / len(metrics), 3)

    if timeline is not None and not timeline.empty and "Team" in timeline.columns:
        df = timeline[timeline["Team"] == team].copy()
        if not df.empty:
            final_lap = df["Lap"].max()
            final = df[df["Lap"] == final_lap]
            row.update(
                {
                    "AverageFinish": round(float(final["RacePosition"].mean()), 2),
                    "BestFinish": int(final["RacePosition"].min()),
                    "DNFs": int(final["DNF"].sum()) if "DNF" in final else 0,
                    "PitStops": int(final["PitStops"].sum()) if "PitStops" in final else 0,
                    "AverageGap": round(float(final["GapToLeader"].mean()), 3) if "GapToLeader" in final else 0.0,
                }
            )
    return pd.DataFrame([row])


def build_all_team_profiles(timeline: pd.DataFrame) -> pd.DataFrame:
    teams = sorted(timeline["Team"].dropna().unique()) if "Team" in timeline.columns else []
    if not teams:
        return pd.DataFrame()
    return pd.concat([build_team_profile(team, timeline) for team in teams], ignore_index=True)


def plot_team_radar(team: str):
    profile = build_team_profile(team)
    categories = ["Reliability", "Strategy", "PitCrew", "Development"]
    values = [float(profile.iloc[0][c]) for c in categories]
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=values + [values[0]], theta=categories + [categories[0]], fill="toself", name=team))
    fig.update_layout(title=f"{team} team profile", polar=dict(radialaxis=dict(visible=True, range=[0, 1])), showlegend=False)
    return fig


def plot_team_comparison(profiles: pd.DataFrame):
    cols = ["Reliability", "Strategy", "PitCrew", "Development", "Overall"]
    available = [c for c in cols if c in profiles.columns]
    long_df = profiles.melt(id_vars=["Team"], value_vars=available, var_name="Metric", value_name="Score")
    fig = px.bar(long_df, x="Team", y="Score", color="Metric", barmode="group", title="Team performance matrix")
    fig.update_layout(yaxis_range=[0, 1])
    return fig


def plot_team_race_positions(timeline: pd.DataFrame, team: str):
    df = timeline[timeline["Team"] == team].copy()
    if df.empty:
        raise ValueError(f"No timeline rows found for team {team}.")
    fig = px.line(df, x="Lap", y="RacePosition", color="Driver", markers=True, title=f"{team} race position evolution")
    fig.update_layout(yaxis_autorange="reversed")
    return fig
