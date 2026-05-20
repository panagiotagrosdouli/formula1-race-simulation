import argparse
import json

import pandas as pd

from .config import DEMO_DATA_PATH, TRAINING_DATA_PATH, PREDICTIONS_PATH, SIMULATION_PATH
from .data_loader import build_demo_dataset, build_fastf1_dataset
from .model import train_model
from .simulation import monte_carlo_race


def build_demo_data_command(args):
    df = build_demo_dataset()
    df.to_csv(TRAINING_DATA_PATH, index=False)
    df.to_csv(DEMO_DATA_PATH, index=False)
    print(f"Saved demo dataset to {TRAINING_DATA_PATH}")
    print(df.head())


def build_fastf1_data_command(args):
    gps = args.grand_prix if args.grand_prix else None
    df = build_fastf1_dataset(year=args.year, grand_prix_names=gps)
    df.to_csv(TRAINING_DATA_PATH, index=False)
    print(f"Saved FastF1 dataset to {TRAINING_DATA_PATH}")
    print(df.head())


def train_command(args):
    if not TRAINING_DATA_PATH.exists():
        print("No training dataset found. Building demo dataset first.")
        df = build_demo_dataset()
        df.to_csv(TRAINING_DATA_PATH, index=False)

    df = pd.read_csv(TRAINING_DATA_PATH)
    _model, metrics, predictions = train_model(df)
    print("Training complete.")
    print(json.dumps(metrics, indent=2))
    print(f"Predictions saved to {PREDICTIONS_PATH}")
    print(predictions.sort_values(["GrandPrix", "PredictedRank"]).head(20))


def simulate_command(args):
    if not PREDICTIONS_PATH.exists():
        print("No predictions found. Training model first.")
        train_command(args)

    predictions = pd.read_csv(PREDICTIONS_PATH)
    results = monte_carlo_race(
        predictions,
        n_simulations=args.n_simulations,
        noise_std=args.noise_std,
    )
    print(f"Simulation saved to {SIMULATION_PATH}")
    print(results)


def main():
    parser = argparse.ArgumentParser(description="F1 AI Predictor CLI")
    subparsers = parser.add_subparsers(required=True)

    demo = subparsers.add_parser("build-demo-data")
    demo.set_defaults(func=build_demo_data_command)

    fastf1 = subparsers.add_parser("build-fastf1-data")
    fastf1.add_argument("--year", type=int, required=True)
    fastf1.add_argument("--grand-prix", nargs="*", default=None)
    fastf1.set_defaults(func=build_fastf1_data_command)

    train = subparsers.add_parser("train")
    train.set_defaults(func=train_command)

    simulate = subparsers.add_parser("simulate")
    simulate.add_argument("--n-simulations", type=int, default=10000)
    simulate.add_argument("--noise-std", type=float, default=2.0)
    simulate.set_defaults(func=simulate_command)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
