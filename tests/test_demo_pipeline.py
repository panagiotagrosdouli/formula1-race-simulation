from src.f1predictor.data_loader import build_demo_dataset
from src.f1predictor.model import train_model
from src.f1predictor.simulation import monte_carlo_race


def test_demo_pipeline_runs():
    df = build_demo_dataset()
    model, metrics, predictions = train_model(df)
    sim = monte_carlo_race(predictions, n_simulations=100)
    assert not df.empty
    assert "MAE" in metrics
    assert not predictions.empty
    assert not sim.empty
