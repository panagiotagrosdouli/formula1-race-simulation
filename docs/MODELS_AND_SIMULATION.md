# Models and Simulation

This document covers the race simulation engine, tyre model, fuel model, weather model, safety-car model, strategy optimisation, Monte Carlo simulation, telemetry integration, dashboard guide, evaluation protocol, roadmap and reproducibility notes.

## Race simulation engine

Implemented in `f1sim/simulation/engine.py`. The loop advances the race clock lap by lap, applies tyre/fuel/weather/SC effects, handles pit-stop events, updates gaps and records history. Traffic, retirement and penalty behaviour are present as scaffolds for further calibration.

## Tyre model

Implemented in `f1sim/models/tyres.py`. Compounds include soft, medium, hard, intermediate and wet. The model includes base compound delta, wear, cliff behaviour, track-temperature sensitivity and wetness sensitivity. Thermal degradation is a scaffold represented by temperature sensitivity.

## Fuel model

Implemented in `f1sim/models/fuel.py`. Fuel mass burns per lap and lap-time delta decreases as the car gets lighter. A configurable safety margin prevents negative fuel.

## Weather model

Implemented in `f1sim/weather/model.py`. The model supports dry/wet transitions, rain probability, track wetness, air temperature, track temperature and wind scaffold.

## Safety car / VSC model

Implemented in `f1sim/safety_car/model.py`. The model samples SC/VSC events, applies race neutralisation lap-time multipliers and reduces pit-loss under neutralisation.

## Strategy optimisation

Implemented/prototype in `f1sim/strategy/` and `f1sim/optimization/`. Baseline one-, two- and three-stop strategies are generated. Grid search is implemented. Bayesian and genetic optimisation remain planned scaffolds.

## Monte Carlo simulation

Implemented in `f1sim/simulation/monte_carlo.py`. Repeated seeded simulations provide expected race time, confidence intervals and risk profile. Stochastic variation currently comes from weather/SC/traffic models and deterministic seed offsets.

## Telemetry integration

Implemented/prototype in `f1sim/telemetry/loaders.py`. CSV lap-time validation is implemented. FastF1 and OpenF1 integrations are explicit scaffolds and do not fabricate missing data.

## Dashboard guide

Run `streamlit run f1sim/dashboard/app.py`. The dashboard loads a YAML config, runs a deterministic simulation, plots lap-time/position traces and can run Monte Carlo simulations.

## Evaluation protocol

Use deterministic seeds, keep configs under `configs/experiments/`, save outputs under `results/`, cite public data sources, and compare simulation outputs against held-out public race data only when licensing allows.

## Roadmap

- Calibrate model parameters against public historical data.
- Add traffic interaction and retirement/penalty event models.
- Add multi-objective optimisation.
- Expand engineering report generation.

## Reproducibility

Every experiment should specify `seed`, `laps`, driver inputs, strategy inputs, weather risk, safety-car risk and output directory. Scripts must write outputs to `results/` and avoid notebook-only logic.
