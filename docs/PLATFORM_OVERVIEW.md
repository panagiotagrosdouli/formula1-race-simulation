# Platform Overview

F1Sim is an open motorsport engineering platform for reproducible race strategy simulation. It models lap-by-lap race evolution under tyre degradation, fuel mass, weather uncertainty, safety-car/VSC events, pit-stop choices and driver pace variation.

## Engineering motivation

Strategy calls are decisions under uncertainty. The platform separates deterministic physics-inspired components from stochastic event models so students and analysts can inspect assumptions, run sensitivity studies and compare strategies without inventing official team data.

## Implemented

- Core state model for drivers, track and pit events.
- Lap-by-lap race simulation engine.
- Tyre, fuel, weather and SC/VSC models.
- Strategy generator, Monte Carlo module and plotting exports.
- YAML-driven experiments and deterministic seeds.

## Prototype

- Traffic loss scaffold.
- Wet/dry transition model.
- Streamlit dashboard.
- CSV, FastF1 and OpenF1 telemetry loaders.

## Planned

- Calibrated public-data validation.
- Multi-car traffic and blue-flag model.
- Bayesian and genetic optimisation.
- Next.js website deployment and richer reports.

## Limitations

Default parameters are transparent modelling assumptions. They are not official FIA, Formula 1 or team data.
