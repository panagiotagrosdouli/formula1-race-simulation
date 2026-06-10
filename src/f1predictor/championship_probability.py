import pandas as pd


def calculate_title_probabilities(driver_standings: pd.DataFrame) -> pd.DataFrame:
    standings = driver_standings.copy()

    total_points = standings['ExpectedPoints'].sum()
    if total_points <= 0:
        standings['ChampionshipProbability'] = 0.0
        return standings

    standings['ChampionshipProbability'] = (
        standings['ExpectedPoints'] / total_points * 100
    ).round(2)

    standings = standings.sort_values(
        'ChampionshipProbability',
        ascending=False
    ).reset_index(drop=True)

    return standings


def calculate_constructor_title_probabilities(constructor_standings: pd.DataFrame) -> pd.DataFrame:
    standings = constructor_standings.copy()

    total_points = standings['ConstructorExpectedPoints'].sum()
    if total_points <= 0:
        standings['ChampionshipProbability'] = 0.0
        return standings

    standings['ChampionshipProbability'] = (
        standings['ConstructorExpectedPoints'] / total_points * 100
    ).round(2)

    standings = standings.sort_values(
        'ChampionshipProbability',
        ascending=False
    ).reset_index(drop=True)

    return standings
