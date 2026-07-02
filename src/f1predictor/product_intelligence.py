"""Product-facing race intelligence helpers.

These functions sit between the modelling layer and the Streamlit UI. They turn
raw prediction/simulation tables into fan-friendly explanations, storylines,
shareable summaries, and engineer-facing uncertainty diagnostics.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class Storyline:
    """A compact narrative item shown in the fan-facing UI."""

    title: str
    driver: str
    detail: str


def _num(value: object, default: float = 0.0) -> float:
    try:
        converted = pd.to_numeric(value, errors="coerce")
        if pd.isna(converted):
            return default
        return float(converted)
    except Exception:
        return default


def _percent(value: object) -> str:
    return f"{_num(value) * 100:.1f}%"


def prepare_driver_cards(forecast: pd.DataFrame, simulation: pd.DataFrame, limit: int = 8) -> pd.DataFrame:
    """Merge forecast and simulation output into a UI-ready driver card table.

    The function is defensive: missing columns are filled with neutral defaults so
    the app can still render when a future data source is incomplete.
    """

    if forecast.empty:
        return pd.DataFrame()

    base_cols = [col for col in ["Driver", "Team", "PredictedRank", "PredictedFinishPosition", "GridPosition"] if col in forecast.columns]
    cards = forecast[base_cols].copy()
    if "Driver" not in cards.columns:
        return pd.DataFrame()

    probability_cols = [
        col
        for col in ["Driver", "WinProbability", "PodiumProbability", "Top10Probability", "ExpectedFinish", "MedianFinish"]
        if col in simulation.columns
    ]
    if probability_cols:
        cards = cards.merge(simulation[probability_cols], on="Driver", how="left")

    for col in ["WinProbability", "PodiumProbability", "Top10Probability"]:
        cards[col] = pd.to_numeric(cards.get(col, 0.0), errors="coerce").fillna(0.0)

    if "PredictedRank" in cards.columns:
        cards = cards.sort_values("PredictedRank")
    elif "WinProbability" in cards.columns:
        cards = cards.sort_values("WinProbability", ascending=False)

    cards["FanSummary"] = cards.apply(why_prediction, axis=1)
    return cards.head(limit).reset_index(drop=True)


def why_prediction(row: pd.Series) -> str:
    """Create a short human explanation for a driver's forecast."""

    driver = str(row.get("Driver", "This driver"))
    rank = _num(row.get("PredictedRank", row.get("PredictedFinishPosition", 0)), 0)
    win = _num(row.get("WinProbability", 0))
    podium = _num(row.get("PodiumProbability", 0))
    top10 = _num(row.get("Top10Probability", 0))
    grid = row.get("GridPosition", None)

    if win >= 0.25:
        reason = "has one of the strongest win profiles in the simulation"
    elif podium >= 0.55:
        reason = "looks like a serious podium contender"
    elif top10 >= 0.75:
        reason = "has a stable points-scoring profile"
    else:
        reason = "needs race chaos, strategy or reliability swings to move forward"

    grid_text = ""
    if grid is not None and not pd.isna(grid):
        grid_text = f" Starting around P{int(_num(grid, 0))} shapes the expected race path."

    rank_text = f"P{int(rank)}" if rank > 0 else "the projected order"
    return f"{driver} is projected near {rank_text} because the model {reason}.{grid_text}"


def build_storylines(forecast: pd.DataFrame, simulation: pd.DataFrame, rain_probability: float = 0.0) -> list[Storyline]:
    """Generate fan-friendly race narratives from forecast and probability output."""

    cards = prepare_driver_cards(forecast, simulation, limit=20)
    if cards.empty:
        return []

    by_win = cards.sort_values("WinProbability", ascending=False)
    by_podium = cards.sort_values("PodiumProbability", ascending=False)
    by_risk = forecast.copy()
    if "DNFRisk" in by_risk.columns:
        by_risk["DNFRisk"] = pd.to_numeric(by_risk["DNFRisk"], errors="coerce").fillna(0)
        risk_row = by_risk.sort_values("DNFRisk", ascending=False).iloc[0]
    else:
        risk_row = cards.iloc[-1]

    leader = by_win.iloc[0]
    dark_horse = by_podium[by_podium["WinProbability"] < by_podium["WinProbability"].max()].head(1)
    if dark_horse.empty:
        dark_horse_row = by_podium.iloc[min(1, len(by_podium) - 1)]
    else:
        dark_horse_row = dark_horse.iloc[0]

    team_battle = cards[cards["Team"].notna()] if "Team" in cards.columns else pd.DataFrame()
    teammate_detail = "No clear teammate battle found yet."
    teammate_driver = str(dark_horse_row.get("Driver", "Field"))
    if not team_battle.empty:
        counts = team_battle["Team"].value_counts()
        multi_team = counts[counts >= 2]
        if not multi_team.empty:
            team = multi_team.index[0]
            teammates = team_battle[team_battle["Team"] == team].head(2)
            teammate_driver = str(teammates.iloc[0]["Driver"])
            teammate_detail = f"{team} has an intra-team reference point: {', '.join(teammates['Driver'].astype(str).tolist())}."

    chaos = "Low"
    if rain_probability >= 0.55:
        chaos = "High"
    elif rain_probability >= 0.25:
        chaos = "Medium"

    return [
        Storyline("Title battle pulse", str(leader.get("Driver", "Leader")), f"Highest win signal at {_percent(leader.get('WinProbability', 0))}."),
        Storyline("Dark horse", str(dark_horse_row.get("Driver", "Field")), f"Podium chance {_percent(dark_horse_row.get('PodiumProbability', 0))} without being the win favourite."),
        Storyline("Teammate battle", teammate_driver, teammate_detail),
        Storyline("Biggest risk", str(risk_row.get("Driver", "Field")), f"Reliability/risk model flags this driver as one to monitor."),
        Storyline("Weather chaos factor", chaos, f"Rain probability is {rain_probability * 100:.1f}%, so strategy volatility is {chaos.lower()}.")
    ]


def shareable_summary(race_name: str, cards: pd.DataFrame, storylines: list[Storyline]) -> str:
    """Build a compact text summary that fans can copy/share."""

    if cards.empty:
        return f"{race_name}: no prediction table available yet."

    top = cards.head(3)
    podium_text = ", ".join(
        f"{row.Driver} ({_percent(row.WinProbability)} win)" for row in top.itertuples(index=False)
    )
    storyline_text = " | ".join(f"{s.title}: {s.driver}" for s in storylines[:3])
    return f"🏎️ {race_name} prediction: {podium_text}. {storyline_text}. Estimates, not guarantees."


def uncertainty_table(simulation: pd.DataFrame) -> pd.DataFrame:
    """Create engineer-facing probability/interval diagnostics.

    This is intentionally simple and transparent: it uses available Monte Carlo
    columns and derives a rough expected finish interval when median/expected
    finish are present.
    """

    if simulation.empty:
        return pd.DataFrame()

    cols = [col for col in ["Driver", "Team", "ExpectedFinish", "MedianFinish", "WinProbability", "PodiumProbability", "Top10Probability"] if col in simulation.columns]
    out = simulation[cols].copy()
    for col in ["ExpectedFinish", "MedianFinish", "WinProbability", "PodiumProbability", "Top10Probability"]:
        if col in out.columns:
            out[col] = pd.to_numeric(out[col], errors="coerce")

    if "ExpectedFinish" in out.columns:
        spread = (1.5 + (1 - out.get("Top10Probability", 0).fillna(0)) * 4).round(2)
        out["ApproxFinishInterval"] = out["ExpectedFinish"].round(2).astype(str) + " ± " + spread.astype(str)

    return out
