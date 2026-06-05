import pandas as pd

from .future_race_predictor import forecast_future_race


DEFAULT_2026_RACES = [
    "Australian Grand Prix 2026",
    "Chinese Grand Prix 2026",
    "Japanese Grand Prix 2026",
    "Bahrain Grand Prix 2026",
    "Saudi Arabian Grand Prix 2026",
    "Miami Grand Prix 2026",
    "Monaco Grand Prix 2026",
    "Canadian Grand Prix 2026",
    "Spanish Grand Prix 2026",
    "Austrian Grand Prix 2026",
    "British Grand Prix 2026",
    "Belgian Grand Prix 2026",
    "Hungarian Grand Prix 2026",
    "Italian Grand Prix 2026",
    "Singapore Grand Prix 2026",
    "United States Grand Prix 2026",
    "Mexico City Grand Prix 2026",
    "São Paulo Grand Prix 2026",
    "Las Vegas Grand Prix 2026",
    "Qatar Grand Prix 2026",
    "Abu Dhabi Grand Prix 2026",
]


def smooth_expected_points(row) -> float:
    ef = float(row["ExpectedFinish"])
    win = float(row.get("WinProbability", 0))
    podium = float(row.get("PodiumProbability", 0))
    top10 = float(row.get("Top10Probability", 0))

    base = max(0.0, 11.0 - ef) * 1.2
    bonus = 10.0 * win + 5.0 * podium + 2.0 * top10

    return round(base + bonus, 2)


def simulate_2026_season(
    history_df: pd.DataFrame,
    races: list[str] | None = None,
    start_round: int = 1,
    n_simulations: int = 3000,
    noise_std: float = 2.0,
):
    if races is None:
        races = DEFAULT_2026_RACES

    all_driver_rows = []
    all_constructor_rows = []

    for i, race_name in enumerate(races, start=start_round):
        result = forecast_future_race(
            history_df=history_df,
            race_name=race_name,
            year=2026,
            round_no=i,
            n_simulations=n_simulations,
            noise_std=noise_std,
            use_2026_grid=True,
        )

        sim = result["simulation"].copy()
        sim["GrandPrix"] = race_name
        sim["Round"] = i
        sim["ExpectedPoints"] = sim.apply(smooth_expected_points, axis=1)

        all_driver_rows.append(sim)

        constructors = (
            sim.groupby("Team", as_index=False)["ExpectedPoints"]
            .sum()
            .rename(columns={"ExpectedPoints": "ConstructorExpectedPoints"})
        )
        constructors["GrandPrix"] = race_name
        constructors["Round"] = i
        all_constructor_rows.append(constructors)

    driver_race_table = pd.concat(all_driver_rows, ignore_index=True)
    constructor_race_table = pd.concat(all_constructor_rows, ignore_index=True)

    driver_standings = (
        driver_race_table.groupby(["Driver", "Team"], as_index=False)["ExpectedPoints"]
        .sum()
        .sort_values("ExpectedPoints", ascending=False)
        .reset_index(drop=True)
    )
    driver_standings["ProjectedPosition"] = range(1, len(driver_standings) + 1)

    constructor_standings = (
        constructor_race_table.groupby("Team", as_index=False)["ConstructorExpectedPoints"]
        .sum()
        .sort_values("ConstructorExpectedPoints", ascending=False)
        .reset_index(drop=True)
    )
    constructor_standings["ProjectedPosition"] = range(1, len(constructor_standings) + 1)

    return {
        "driver_race_table": driver_race_table,
        "constructor_race_table": constructor_race_table,
        "driver_standings": driver_standings,
        "constructor_standings": constructor_standings,
    }
