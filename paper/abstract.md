# Abstract

We present F1Sim, an open and reproducible Formula 1 race simulation platform for strategy analysis under tyre, weather, traffic, safety-car and driver-pace uncertainty. The platform is designed for motorsport engineering education, data-science experimentation and transparent decision-support research. It provides a lap-by-lap simulation engine, configurable tyre and fuel models, stochastic weather and neutralisation models, candidate pit-stop strategies, Monte Carlo risk analysis, telemetry-loader scaffolds, plotting utilities and dashboard prototypes. The system intentionally separates implemented functionality from prototype and planned components, and does not claim access to private team data.

# Contributions

1. A modular Python architecture for race strategy simulation.
2. YAML-driven deterministic experiments with seed control.
3. Transparent tyre, fuel, weather and safety-car model components.
4. Strategy comparison and Monte Carlo uncertainty analysis.
5. Documentation and dashboard scaffolds for engineering education.

# Future work

Future work includes calibration against public historical data, richer traffic modelling, penalty and reliability event models, Bayesian and genetic optimisation, multi-objective Pareto reporting and validated telemetry-driven pace estimation.
