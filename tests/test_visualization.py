import pandas as pd

from src.f1predictor.visualization import plot_predicted_order, plot_probabilities


def test_plot_predicted_order_uses_expected_layout():
    predictions = pd.DataFrame(
        {
            "Driver": ["LEC", "HAM", "VER"],
            "Team": ["Ferrari", "Ferrari", "Red Bull Racing"],
            "PredictedRank": [1, 2, 3],
            "PredictedFinishPosition": [1.4, 2.1, 3.0],
            "GridPosition": [1, 2, 3],
            "QualiGapToPole_s": [0.0, 0.1, 0.2],
        }
    )

    fig = plot_predicted_order(predictions)

    assert fig.layout.template is not None
    assert fig.layout.plot_bgcolor == "rgba(17, 24, 39, 0.92)"
    assert fig.data[0].x.tolist() == ["LEC", "HAM", "VER"]


def test_plot_probabilities_handles_probability_table():
    simulation = pd.DataFrame(
        {
            "Driver": ["LEC", "HAM", "VER"],
            "Team": ["Ferrari", "Ferrari", "Red Bull Racing"],
            "ExpectedFinish": [1.7, 2.5, 4.0],
            "MedianFinish": [1, 2, 4],
            "WinProbability": [0.45, 0.35, 0.20],
            "PodiumProbability": [0.82, 0.78, 0.45],
        }
    )

    fig = plot_probabilities(simulation, "WinProbability")

    assert fig.layout.template is not None
    assert fig.layout.plot_bgcolor == "rgba(17, 24, 39, 0.92)"
    assert fig.data[0].x.tolist() == ["LEC", "HAM", "VER"]
