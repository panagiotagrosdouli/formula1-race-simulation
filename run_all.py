from src.f1predictor.data_loader import build_demo_dataset
from src.f1predictor.config import TRAINING_DATA_PATH
from src.f1predictor.model import train_model
from src.f1predictor.simulation import monte_carlo_race

df = build_demo_dataset()
df.to_csv(TRAINING_DATA_PATH, index=False)

model, metrics, predictions = train_model(df)
sim = monte_carlo_race(predictions, n_simulations=10000)

print("Metrics:")
print(metrics)

print("\nPredicted order:")
latest_gp = predictions["GrandPrix"].iloc[-1]
print(predictions[predictions["GrandPrix"] == latest_gp].sort_values("PredictedRank")[
    ["PredictedRank", "Driver", "Team", "PredictedFinishPosition"]
])

print("\nMonte Carlo probabilities:")
print(sim)
