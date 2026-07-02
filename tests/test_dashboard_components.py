import pandas as pd
import plotly.graph_objects as go

from app.dashboard_components import (
    PAGES,
    apply_plot_theme,
    prediction_view,
    probability_view,
)


def test_pages_include_core_dashboard_sections():
    assert PAGES == [
        "Command Centre",
        "Race Forecast",
        "Model Lab",
        "Season Simulator",
        "FastF1 Training",
        "Telemetry",
        "Tyre Strategy",
        "Diagnostics",
    ]


def test_prediction_view_filters_to_priority_columns():
    df = pd.DataFrame(
        {
            "Driver": ["LEC"],
            "Team": ["Ferrari"],
            "PredictedRank": [1],
            "UnknownExtraColumn": [123],
        }
    )

    view = prediction_view(df)

    assert view.columns.tolist() == ["PredictedRank", "Driver", "Team"]


def test_probability_view_converts_probabilities_to_percentages():
    df = pd.DataFrame(
        {
            "Driver": ["LEC"],
            "WinProbability": [0.42123],
            "PodiumProbability": [0.81234],
            "Top10Probability": [0.99123],
        }
    )

    view = probability_view(df)

    assert view.loc[0, "WinProbability"] == 42.12
    assert view.loc[0, "PodiumProbability"] == 81.23
    assert view.loc[0, "Top10Probability"] == 99.12


def test_apply_plot_theme_sets_ferrari_dark_layout():
    fig = apply_plot_theme(go.Figure())

    assert fig.layout.plot_bgcolor == "rgba(17, 24, 39, 0.92)"
    assert fig.layout.paper_bgcolor == "rgba(5, 7, 13, 0)"
