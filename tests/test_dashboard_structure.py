import importlib

import pandas as pd


def test_dashboard_import_exposes_pages_without_running_app():
    dashboard = importlib.import_module("app.dashboard")

    assert "Command Centre" in dashboard.PAGES
    assert "Race Forecast" in dashboard.PAGES
    assert callable(dashboard.main)


def test_prediction_view_keeps_available_priority_columns():
    dashboard = importlib.import_module("app.dashboard")
    df = pd.DataFrame(
        {
            "Driver": ["LEC"],
            "Team": ["Ferrari"],
            "PredictedRank": [1],
            "UnknownExtraColumn": [123],
        }
    )

    view = dashboard.prediction_view(df)

    assert view.columns.tolist() == ["PredictedRank", "Driver", "Team"]
