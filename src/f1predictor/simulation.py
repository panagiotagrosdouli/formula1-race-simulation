from __future__ import annotations

import numpy as np
import pandas as pd

from .config import SIMULATION_PATH


COMPOUND_MODELS = {
    "SOFT": {"base_delta": -0.30, "degradation": 0.090, "life": 18},
    "MEDIUM": {"base_delta": 0.00, "degradation": 0.060, "life": 28},
    "HARD": {"base_delta": 0.35, "degradation": 0.040, "life": 40},
}


def _initial_compound(grid_position: int) -> str:
    if grid_position <= 8:
        return "SOFT"
    if grid_position <= 16:
        return "MEDIUM"
    return "HARD"


def _next_compound(current: str) -> str:
    if current == "SOFT":
        return "MEDIUM"
    if current == "MEDIUM":
        return "HARD"
    return "MEDIUM"


def _event_for_lap(lap: int, rng: np.random.Generator, rain_probability: float) -> str:
    if rng.random() < 0.018:
        return "SC"
    if rng.random() < 0.025:
        return "VSC"
    if rng.random() < rain_probability * 0.030:
        return "RAIN"
    return "GREEN"


def monte_carlo_race(
    predictions: pd.DataFrame,
    n_simulations: int = 10000,
    noise_std: float = 2.0,
    reliability_std: float = 1.0,
    random_state: int = 42,
) -> pd.DataFrame:
    """Convert baseline predictions into finishing probability distributions.

    The model gives a central estimate. Simulation adds random variation to model:
    - incidents
    - strategy variance
    - pit-stop variance
    - reliability shocks
    - safety-car timing effects
    """
    rng = np.random.default_rng(random_state)

    df = predictions.copy()
    latest_gp = df["GrandPrix"].iloc[-1] if "GrandPrix" in df.columns else "Race"
    if "GrandPrix" in df.columns and df["GrandPrix"].nunique() > 1:
        df = df[df["GrandPrix"] == latest_gp].copy()

    if "PredictedFinishPosition" not in df.columns:
        raise ValueError("predictions must include PredictedFinishPosition")

    drivers = df["Driver"].to_numpy()
    base = df["PredictedFinishPosition"].to_numpy(dtype=float)
    team_strength = df.get("TeamStrength", pd.Series(0.5, index=df.index)).fillna(0.5).to_numpy(dtype=float)

    finishing_positions = {drv: [] for drv in drivers}

    for _ in range(n_simulations):
        model_noise = rng.normal(0, noise_std, size=len(df))
        reliability_shock = rng.exponential(reliability_std, size=len(df)) * (1 - np.clip(team_strength, 0, 1))
        chaos = rng.normal(0, 0.35, size=len(df))

        simulated_score = base + model_noise + reliability_shock + chaos
        order = np.argsort(simulated_score)

        for pos, idx in enumerate(order, start=1):
            finishing_positions[drivers[idx]].append(pos)

    rows = []
    for drv in drivers:
        positions = np.array(finishing_positions[drv])
        rows.append({
            "Driver": drv,
            "Team": df.loc[df["Driver"] == drv, "Team"].iloc[0] if "Team" in df else "",
            "ExpectedFinish": round(float(positions.mean()), 2),
            "MedianFinish": int(np.median(positions)),
            "WinProbability": round(float(np.mean(positions == 1)), 4),
            "PodiumProbability": round(float(np.mean(positions <= 3)), 4),
            "Top10Probability": round(float(np.mean(positions <= 10)), 4),
        })

    result = pd.DataFrame(rows).sort_values("ExpectedFinish").reset_index(drop=True)
    result.to_csv(SIMULATION_PATH, index=False)
    return result


def lap_by_lap_race_simulation(
    predictions: pd.DataFrame,
    total_laps: int = 53,
    pit_loss: float = 22.5,
    rain_probability: float = 0.0,
    random_state: int = 42,
) -> dict[str, pd.DataFrame]:
    """Simulate one full race as a lap-by-lap state model.

    This is a stateful simulation layer designed for replay dashboards. It is kept
    separate from monte_carlo_race so existing probability workflows remain stable.
    """
    rng = np.random.default_rng(random_state)
    df = predictions.copy().reset_index(drop=True)

    if "PredictedFinishPosition" not in df.columns:
        raise ValueError("predictions must include PredictedFinishPosition")

    if "GridPosition" not in df.columns:
        df["GridPosition"] = df.get("PredictedRank", pd.Series(np.arange(1, len(df) + 1))).astype(float)

    df = df.sort_values("GridPosition").reset_index(drop=True)
    df["RacePosition"] = np.arange(1, len(df) + 1)
    df["Compound"] = df["GridPosition"].astype(int).apply(_initial_compound)
    df["TyreAge"] = 0
    df["PitStops"] = 0
    df["DNF"] = False
    df["CumulativeTime"] = 0.0

    if "TeamStrength" not in df.columns:
        df["TeamStrength"] = 0.5

    timeline_rows = []
    event_rows = []
    pit_rows = []

    for lap in range(1, total_laps + 1):
        event = _event_for_lap(lap, rng, float(rain_probability))
        event_multiplier = {"GREEN": 1.0, "VSC": 0.45, "SC": 0.30, "RAIN": 1.30}[event]

        if event != "GREEN":
            event_rows.append({"Lap": lap, "Event": event})

        for idx, row in df.iterrows():
            if bool(row["DNF"]):
                continue

            compound = str(row["Compound"])
            tyre_age = int(row["TyreAge"]) + 1
            model = COMPOUND_MODELS.get(compound, COMPOUND_MODELS["MEDIUM"])

            base_pace = 88.0 + float(row["PredictedFinishPosition"]) * 0.08
            tyre_penalty = model["degradation"] * tyre_age
            cliff_penalty = max(0, tyre_age - model["life"]) * 0.20
            rain_penalty = rng.normal(0.25, 0.12) if event == "RAIN" else 0.0
            lap_noise = rng.normal(0, 0.22)
            lap_time = base_pace + model["base_delta"] + tyre_penalty + cliff_penalty + rain_penalty + lap_noise

            pit_now = (
                lap < total_laps - 5
                and row["PitStops"] < 2
                and tyre_age > model["life"]
                and rng.random() < 0.35
            )

            if pit_now:
                lap_time += pit_loss * event_multiplier
                new_compound = _next_compound(compound)
                df.at[idx, "Compound"] = new_compound
                df.at[idx, "TyreAge"] = 0
                df.at[idx, "PitStops"] = int(row["PitStops"]) + 1
                pit_rows.append({
                    "Lap": lap,
                    "Driver": row["Driver"],
                    "OldCompound": compound,
                    "NewCompound": new_compound,
                    "PitLoss": round(pit_loss * event_multiplier, 3),
                })
            else:
                df.at[idx, "TyreAge"] = tyre_age

            reliability = float(np.clip(row.get("TeamStrength", 0.5), 0.05, 0.95))
            dnf_probability = 0.0008 + (1.0 - reliability) * 0.0018
            if event in {"SC", "RAIN"}:
                dnf_probability *= 1.6

            if rng.random() < dnf_probability:
                df.at[idx, "DNF"] = True
                event_rows.append({"Lap": lap, "Event": "DNF", "Driver": row["Driver"]})

            df.at[idx, "CumulativeTime"] = float(df.at[idx, "CumulativeTime"]) + float(lap_time)

        active = df[~df["DNF"]].sort_values("CumulativeTime").copy()
        inactive = df[df["DNF"]].sort_values("CumulativeTime").copy()
        active["RacePosition"] = np.arange(1, len(active) + 1)
        inactive["RacePosition"] = np.arange(len(active) + 1, len(active) + len(inactive) + 1)
        df = pd.concat([active, inactive], ignore_index=True)

        leader_time = float(active["CumulativeTime"].min()) if not active.empty else 0.0
        for _, row in df.iterrows():
            timeline_rows.append({
                "Lap": lap,
                "Driver": row["Driver"],
                "Team": row["Team"] if "Team" in df.columns else "",
                "RacePosition": int(row["RacePosition"]),
                "Compound": row["Compound"],
                "TyreAge": int(row["TyreAge"]),
                "PitStops": int(row["PitStops"]),
                "DNF": bool(row["DNF"]),
                "GapToLeader": round(float(row["CumulativeTime"] - leader_time), 3),
                "Event": event,
            })

    timeline = pd.DataFrame(timeline_rows)
    final_order = (
        timeline[timeline["Lap"] == total_laps]
        .sort_values("RacePosition")
        .reset_index(drop=True)
    )

    return {
        "timeline": timeline,
        "final_order": final_order,
        "events": pd.DataFrame(event_rows),
        "pitstops": pd.DataFrame(pit_rows),
    }
