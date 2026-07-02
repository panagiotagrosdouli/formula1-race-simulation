import pandas as pd

from src.f1predictor.product_intelligence import (
    build_storylines,
    prepare_driver_cards,
    shareable_summary,
    uncertainty_table,
)


def test_prepare_driver_cards_adds_fan_summary_and_probabilities():
    forecast = pd.DataFrame(
        {
            "Driver": ["LEC", "HAM"],
            "Team": ["Ferrari", "Ferrari"],
            "PredictedRank": [1, 2],
            "GridPosition": [1, 3],
        }
    )
    simulation = pd.DataFrame(
        {
            "Driver": ["LEC", "HAM"],
            "WinProbability": [0.42, 0.25],
            "PodiumProbability": [0.81, 0.72],
            "Top10Probability": [0.98, 0.96],
        }
    )

    cards = prepare_driver_cards(forecast, simulation)

    assert cards.loc[0, "Driver"] == "LEC"
    assert cards.loc[0, "WinProbability"] == 0.42
    assert "LEC" in cards.loc[0, "FanSummary"]


def test_storylines_and_shareable_summary_are_generated():
    forecast = pd.DataFrame(
        {
            "Driver": ["LEC", "HAM", "VER"],
            "Team": ["Ferrari", "Ferrari", "Red Bull"],
            "PredictedRank": [1, 2, 3],
            "DNFRisk": [0.02, 0.03, 0.12],
        }
    )
    simulation = pd.DataFrame(
        {
            "Driver": ["LEC", "HAM", "VER"],
            "WinProbability": [0.45, 0.30, 0.12],
            "PodiumProbability": [0.82, 0.75, 0.50],
            "Top10Probability": [0.99, 0.97, 0.90],
        }
    )

    cards = prepare_driver_cards(forecast, simulation)
    storylines = build_storylines(forecast, simulation, rain_probability=0.4)
    summary = shareable_summary("Belgian Grand Prix 2026", cards, storylines)

    assert len(storylines) >= 4
    assert "Belgian Grand Prix 2026" in summary
    assert "Estimates, not guarantees" in summary


def test_uncertainty_table_adds_interval_when_expected_finish_exists():
    simulation = pd.DataFrame(
        {
            "Driver": ["LEC"],
            "ExpectedFinish": [1.8],
            "MedianFinish": [2],
            "Top10Probability": [0.95],
        }
    )

    table = uncertainty_table(simulation)

    assert "ApproxFinishInterval" in table.columns
    assert table.loc[0, "Driver"] == "LEC"
