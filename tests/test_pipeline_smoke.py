import numpy as np

from src.f1predictor.data_loader import build_demo_dataset
from src.f1predictor.features import add_fallback_features, get_feature_columns
from src.f1predictor.model import predict_next_race, train_model
from src.f1predictor.simulation import lap_by_lap_race_simulation, monte_carlo_race


def test_demo_dataset_has_expected_schema():
    df = build_demo_dataset()

    required_columns = {
        "Year",
        "Round",
        "GrandPrix",
        "Driver",
        "Team",
        "QualiTime_s",
        "GridPosition",
        "FinishPosition",
    }

    assert required_columns.issubset(df.columns)
    assert len(df) >= 200
    assert df["FinishPosition"].between(1, 20).all()


def test_fallback_features_produce_model_columns_without_missing_values():
    df = build_demo_dataset().head(20).copy()
    df = df.drop(columns=["TeamStrength", "DriverRating", "RecentForm"])

    featured = add_fallback_features(df)

    for column in get_feature_columns():
        assert column in featured.columns
        assert featured[column].notna().all()


def test_training_prediction_and_monte_carlo_are_reproducible():
    df = build_demo_dataset()
    model, metrics, predictions = train_model(df)

    assert metrics["TrainRows"] > metrics["TestRows"] > 0
    assert np.isfinite(metrics["MAE"])
    assert {"PredictedFinishPosition", "PredictedRank"}.issubset(predictions.columns)

    latest_gp = predictions["GrandPrix"].iloc[-1]
    race_predictions = predictions[predictions["GrandPrix"] == latest_gp]
    predicted_next = predict_next_race(model, race_predictions)
    assert predicted_next["PredictedRank"].is_monotonic_increasing

    sim_a = monte_carlo_race(race_predictions, n_simulations=200, random_state=123)
    sim_b = monte_carlo_race(race_predictions, n_simulations=200, random_state=123)

    assert sim_a.equals(sim_b)
    assert sim_a["WinProbability"].between(0, 1).all()
    assert sim_a["PodiumProbability"].between(0, 1).all()
    assert sim_a["Top10Probability"].between(0, 1).all()


def test_lap_by_lap_simulation_outputs_consistent_tables():
    df = build_demo_dataset()
    _, _, predictions = train_model(df)
    latest_gp = predictions["GrandPrix"].iloc[-1]
    race_predictions = predictions[predictions["GrandPrix"] == latest_gp]

    result = lap_by_lap_race_simulation(
        race_predictions,
        total_laps=5,
        rain_probability=0.15,
        random_state=7,
    )

    assert set(result) == {"timeline", "final_order", "events", "pitstops"}
    assert len(result["timeline"]) == len(race_predictions) * 5
    assert len(result["final_order"]) == len(race_predictions)
    assert result["final_order"]["RacePosition"].is_monotonic_increasing
