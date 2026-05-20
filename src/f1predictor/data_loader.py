import warnings
from dataclasses import dataclass
from typing import Iterable, List

import numpy as np
import pandas as pd

from .config import CACHE_DIR

warnings.filterwarnings("ignore")


@dataclass
class RaceRequest:
    year: int
    grand_prix: str


def build_demo_dataset() -> pd.DataFrame:
    """Create a small built-in dataset so the whole project works immediately.

    The values are synthetic but realistic enough for demonstrating the ML pipeline.
    For scientific use, replace this with real historical FastF1 data.
    """
    rng = np.random.default_rng(42)

    drivers = [
        "VER", "PER", "HAM", "RUS", "LEC", "SAI", "NOR", "PIA", "ALO", "STR",
        "OCO", "GAS", "ALB", "SAR", "BOT", "ZHO", "MAG", "HUL", "TSU", "RIC"
    ]

    teams = {
        "VER": "Red Bull", "PER": "Red Bull", "HAM": "Mercedes", "RUS": "Mercedes",
        "LEC": "Ferrari", "SAI": "Ferrari", "NOR": "McLaren", "PIA": "McLaren",
        "ALO": "Aston Martin", "STR": "Aston Martin", "OCO": "Alpine", "GAS": "Alpine",
        "ALB": "Williams", "SAR": "Williams", "BOT": "Kick Sauber", "ZHO": "Kick Sauber",
        "MAG": "Haas", "HUL": "Haas", "TSU": "RB", "RIC": "RB"
    }

    base_strength = {
        "Red Bull": 0.95, "Ferrari": 0.86, "Mercedes": 0.84, "McLaren": 0.87,
        "Aston Martin": 0.73, "Alpine": 0.55, "Williams": 0.45, "RB": 0.50,
        "Haas": 0.42, "Kick Sauber": 0.34,
    }

    driver_skill = {
        "VER": 0.98, "HAM": 0.93, "LEC": 0.91, "NOR": 0.90, "ALO": 0.89,
        "RUS": 0.86, "SAI": 0.85, "PIA": 0.84, "PER": 0.78, "GAS": 0.73,
        "OCO": 0.71, "TSU": 0.67, "RIC": 0.66, "ALB": 0.66, "HUL": 0.64,
        "BOT": 0.62, "MAG": 0.58, "STR": 0.55, "ZHO": 0.51, "SAR": 0.40,
    }

    rows = []
    races = [
        "Bahrain", "Saudi Arabia", "Australia", "Japan", "China", "Miami",
        "Imola", "Monaco", "Canada", "Spain", "Austria", "Silverstone"
    ]

    for race_idx, race in enumerate(races, start=1):
        track_noise = rng.normal(0, 0.04)
        quali_scores = []

        for drv in drivers:
            team = teams[drv]
            strength = 0.60 * base_strength[team] + 0.40 * driver_skill[drv]
            latent_pace = strength + track_noise + rng.normal(0, 0.035)
            quali_time = 90.0 - 2.2 * latent_pace + rng.normal(0, 0.25)
            long_run_pace = 92.5 - 2.0 * latent_pace + rng.normal(0, 0.35)
            quali_scores.append((drv, team, latent_pace, quali_time, long_run_pace))

        quali_sorted = sorted(quali_scores, key=lambda x: x[3])
        grid = {drv: pos for pos, (drv, *_rest) in enumerate(quali_sorted, start=1)}
        pole_time = min(x[3] for x in quali_scores)

        race_scores = []
        for drv, team, latent_pace, quali_time, long_run_pace in quali_scores:
            reliability = rng.uniform(0.90, 0.995)
            pit_loss = rng.normal(22.0, 1.4)
            chaos = rng.normal(0, 0.9)
            race_score = (
                grid[drv] * 0.30
                + long_run_pace * 0.45
                - base_strength[team] * 3.0
                - driver_skill[drv] * 1.8
                + pit_loss * 0.05
                + chaos
                + (1 - reliability) * 10
            )
            race_scores.append((drv, race_score))

        classified = sorted(race_scores, key=lambda x: x[1])
        finish_pos = {drv: pos for pos, (drv, _score) in enumerate(classified, start=1)}

        for drv, team, latent_pace, quali_time, long_run_pace in quali_scores:
            rows.append({
                "Year": 2024,
                "Round": race_idx,
                "GrandPrix": race,
                "Driver": drv,
                "Team": team,
                "QualiTime_s": round(quali_time, 3),
                "QualiGapToPole_s": round(quali_time - pole_time, 3),
                "GridPosition": grid[drv],
                "LongRunPace_s": round(long_run_pace, 3),
                "TeamStrength": base_strength[team],
                "DriverRating": driver_skill[drv],
                "RecentForm": np.nan,
                "FinishPosition": finish_pos[drv],
            })

    df = pd.DataFrame(rows)
    df["RecentForm"] = (
        df.sort_values(["Driver", "Round"])
        .groupby("Driver")["FinishPosition"]
        .transform(lambda s: s.shift().rolling(3, min_periods=1).mean())
    )
    df["RecentForm"] = df["RecentForm"].fillna(df["FinishPosition"].median())
    return df


def build_fastf1_dataset(year: int, grand_prix_names: Iterable[str] | None = None) -> pd.DataFrame:
    """Build a training table from real FastF1 qualifying and race sessions.

    This is intentionally conservative: it uses features available from qualifying
    and target positions from the race result.

    Parameters
    ----------
    year:
        Formula 1 season year.
    grand_prix_names:
        Optional iterable of GP names, e.g. ["Bahrain", "Australia"].
        If omitted, it tries all completed races in the event schedule.
    """
    import fastf1

    fastf1.Cache.enable_cache(str(CACHE_DIR))

    schedule = fastf1.get_event_schedule(year, include_testing=False)

    if grand_prix_names:
        wanted = set(grand_prix_names)
        schedule = schedule[schedule["EventName"].isin(wanted) | schedule["Country"].isin(wanted)]

    rows: List[dict] = []

    for _, event in schedule.iterrows():
        event_name = event["EventName"]
        round_no = int(event["RoundNumber"])

        try:
            quali = fastf1.get_session(year, event_name, "Q")
            race = fastf1.get_session(year, event_name, "R")
            quali.load()
            race.load()
        except Exception as exc:
            print(f"Skipping {event_name}: {exc}")
            continue

        try:
            q_laps = quali.laps.pick_quicklaps()
            fastest = q_laps.loc[q_laps.groupby("Driver")["LapTime"].idxmin()].copy()
            fastest["QualiTime_s"] = fastest["LapTime"].dt.total_seconds()
            pole = fastest["QualiTime_s"].min()
            fastest["QualiGapToPole_s"] = fastest["QualiTime_s"] - pole

            race_results = race.results[["Abbreviation", "ClassifiedPosition", "GridPosition", "TeamName"]].copy()
            race_results["FinishPosition"] = pd.to_numeric(
                race_results["ClassifiedPosition"].replace({"R": np.nan, "W": np.nan, "D": np.nan, "E": np.nan}),
                errors="coerce"
            )
            race_results["FinishPosition"] = race_results["FinishPosition"].fillna(20)

            merged = fastest.merge(
                race_results,
                left_on="Driver",
                right_on="Abbreviation",
                how="inner"
            )

            for _, r in merged.iterrows():
                rows.append({
                    "Year": year,
                    "Round": round_no,
                    "GrandPrix": event_name,
                    "Driver": r["Driver"],
                    "Team": r.get("Team", r.get("TeamName", "")),
                    "QualiTime_s": float(r["QualiTime_s"]),
                    "QualiGapToPole_s": float(r["QualiGapToPole_s"]),
                    "GridPosition": int(r["GridPosition"]) if pd.notna(r["GridPosition"]) else np.nan,
                    "LongRunPace_s": np.nan,
                    "TeamStrength": np.nan,
                    "DriverRating": np.nan,
                    "RecentForm": np.nan,
                    "FinishPosition": int(r["FinishPosition"]),
                })
        except Exception as exc:
            print(f"Could not process {event_name}: {exc}")

    df = pd.DataFrame(rows)
    if df.empty:
        raise RuntimeError("No FastF1 data was collected. Try a completed season or use build-demo-data.")

    df = df.sort_values(["Round", "Driver"]).reset_index(drop=True)
    return df
