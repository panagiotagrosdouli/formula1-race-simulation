"""Run a configured F1Sim experiment and export results."""

from __future__ import annotations

import argparse
from pathlib import Path

from f1sim.data.config import load_race_config
from f1sim.simulation.engine import RaceSimulation
from f1sim.simulation.monte_carlo import MonteCarloSimulation
from f1sim.visualization.plots import plot_lap_times, plot_positions


def main() -> None:
    """CLI entrypoint."""

    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    parser.add_argument("--monte-carlo-runs", type=int, default=0)
    args = parser.parse_args()

    config = load_race_config(args.config)
    output_dir = Path(config.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    result = RaceSimulation(config).run()
    result.to_csv(output_dir / "lap_history.csv")
    plot_lap_times(result.lap_history, output_dir / "figures" / "lap_times.png")
    plot_positions(result.lap_history, output_dir / "figures" / "positions.png")

    metrics_path = output_dir / "metrics.txt"
    metrics_path.write_text(str(result.metrics), encoding="utf-8")
    if args.monte_carlo_runs:
        summary = MonteCarloSimulation(config, runs=args.monte_carlo_runs).run()
        (output_dir / "monte_carlo_summary.txt").write_text(str(summary), encoding="utf-8")


if __name__ == "__main__":
    main()
