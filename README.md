# Formula 1 Race Simulation Engineering Platform

[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/) [![CI](https://github.com/panagiotagrosdouli/formula1-race-simulation/actions/workflows/ci.yml/badge.svg)](https://github.com/panagiotagrosdouli/formula1-race-simulation/actions) [![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

An open, reproducible, data-driven Formula 1 race simulation and strategy engineering platform built around a premium Streamlit dashboard.

> Research question: **How can we build an open, reproducible, data-driven Formula 1 race simulation platform for race strategy analysis under tyre, weather, traffic, safety-car, and pace uncertainty?**

This repository is not an official Formula 1 team tool and does not include fabricated team data. Public/open data integrations are separated from clearly labelled synthetic scenarios used for testing, education and reproducible experiments.

---

## Motivation

Race strategy is an uncertainty-management problem. Engineers evaluate tyre degradation, fuel mass, traffic, pit-loss, weather transitions, neutralisations and driver pace variability before choosing a strategy. This project turns those concepts into transparent Python modules, repeatable YAML experiments, a Streamlit engineering dashboard and exportable reports.

## Engineering problem

Given a race configuration, driver pace model, tyre model and stochastic event model, estimate:

- total race time and expected finishing position
- pit-stop count, stint lengths and compound sequence
- lap-time evolution, degradation rate and fuel effect
- traffic loss, pit loss, undercut delta and overcut delta
- safety-car/weather exposure and risk percentiles
- confidence intervals and probability of beating a target driver

---

## System architecture

```text
configs/                    deterministic YAML experiments
f1sim/core/                 entities, config facades and result objects
f1sim/models/               tyre, fuel and driver pace models
f1sim/weather/              wetness and weather uncertainty
f1sim/safety_car/           SC/VSC neutralisation models
f1sim/strategy/             stint plans, pit windows, ranking and analysis
f1sim/simulation/           lap-by-lap and Monte Carlo engines
f1sim/telemetry/            CSV + FastF1/OpenF1 integration scaffolds
f1sim/evaluation/           engineering metric summaries
f1sim/optimization/         grid search and optimisation scaffolds
f1sim/visualization/        publication-style plots
f1sim/dashboard/            Streamlit engineering dashboard
scripts/                    reproducible runs and GIF/video generation
docs/                       engineering documentation
paper/                      abstract, contributions and future work
streamlit_app.py            Streamlit Cloud entrypoint
```

## Race simulation pipeline

```text
YAML config or dashboard controls
  -> driver, track, weather and strategy state
  -> lap-by-lap simulation loop
  -> tyre + fuel + weather + SC/VSC + traffic scaffolds
  -> classification, metrics, plots, reports and Monte Carlo summaries
```

---

## Quick start

```bash
git clone https://github.com/panagiotagrosdouli/formula1-race-simulation.git
cd formula1-race-simulation
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
streamlit run streamlit_app.py
```

Run tests:

```bash
pytest tests/test_f1sim_core.py
```

Run a deterministic dry-race experiment:

```bash
python scripts/run_experiment.py --config configs/experiments/dry_race.yml
```

Generate the code-built demo animation:

```bash
python scripts/make_demo_gif.py
```

---

## Streamlit dashboard

The Streamlit app is the primary product interface and includes:

- Platform overview and architecture
- Race simulation dashboard
- Tyre engineering lab
- Fuel model lab
- Weather model lab
- Safety car / VSC lab
- Strategy lab
- Monte Carlo lab
- Telemetry and data lab
- Engineering report export
- About and reproducibility section

```bash
streamlit run streamlit_app.py
```

![Demo animation](assets/demo.gif)

---

## Examples

### Race simulation

```python
from f1sim.simulation.engine import RaceSimulation
from f1sim.data.config import load_race_config

config = load_race_config("configs/experiments/dry_race.yml")
result = RaceSimulation(config).run()
print(result.metrics.total_race_time_s)
```

### Pit-stop strategy comparison

```python
from f1sim.strategy.strategies import generate_candidate_strategies, rank_strategies

strategies = generate_candidate_strategies(race_laps=58)
ranking = rank_strategies(strategies, objective="race_time")
```

### Monte Carlo run

```python
from f1sim.simulation.monte_carlo import MonteCarloSimulation

mc = MonteCarloSimulation(config, runs=1000, seed=42)
summary = mc.run(target_driver_id="NOR")
print(summary.confidence_interval_s)
```

---

## Implementation status

| Area | Status | Notes |
|---|---:|---|
| Lap-by-lap race engine | Implemented | Deterministic race loop, race clock, gaps, pit events and metrics. |
| Tyre wear/degradation | Implemented | Compound parameters, age, cliff and track-temperature sensitivity. |
| Fuel effect | Implemented | Fuel burn and lap-time improvement as fuel mass decreases. |
| Weather uncertainty | Prototype | Dry/wet transitions, wetness, rain probability and temperature. |
| Safety car/VSC | Prototype | Event probability, neutralisation and reduced pit-loss model. |
| Strategy generation | Implemented | One-, two- and three-stop candidates with ranking. |
| Undercut/overcut analysis | Prototype | Delta scaffolds based on tyre offset and track position assumptions. |
| Monte Carlo simulation | Implemented | Seeded stochastic weather, SC/VSC and traffic variation. |
| Telemetry integration | Prototype | CSV support plus FastF1/OpenF1 loader scaffolds; no fake official data. |
| Optimization | Prototype | Grid search implemented; Bayesian/GA hooks planned. |
| Visualization | Implemented | Plot exports and dashboard figures. |
| Streamlit dashboard | Implemented | Complete multipage engineering dashboard via `streamlit_app.py`. |

---

## Metrics reported

The platform reports total race time, expected finishing position, pit-stop count, stint lengths, compound sequence, lap-time evolution, degradation rate, traffic loss, pit loss, undercut delta, overcut delta, risk percentile, strategy confidence interval and probability of beating a target driver when configured.

## Reproducible experiments

YAML configs in `configs/experiments/` cover dry race, wet race, mixed conditions, high/low degradation, early/late safety car, one-stop versus two-stop, undercut/overcut, Monte Carlo strategy comparison, driver pace uncertainty and tyre degradation sensitivity. Each experiment uses deterministic seeds and writes outputs to `results/`.

## Limitations

- This is an open research/education platform, not a verified professional team strategy system.
- Default configs are illustrative and must not be interpreted as official team performance data.
- Public telemetry availability depends on third-party data access and caching.
- Traffic, penalties, reliability and restart effects are intentionally scaffolded before calibration.
- Confidence intervals are simulation intervals, not automatically validated Bayesian posteriors.

## Roadmap

1. Calibrate tyre/fuel/weather parameters against public historical data.
2. Add richer traffic interaction and blue-flag modelling.
3. Add restart, penalty and retirement event models.
4. Add Bayesian optimisation and multi-objective Pareto reporting.
5. Expand engineering report export and experiment comparison.
6. Add validation notebooks and backtesting protocols.

## Citation

If this repository supports your research or coursework, cite it using `CITATION.cff`.

## Contributing

Contributions should keep models transparent, cite data sources, avoid invented official data, add tests for new logic and document limitations. Run `ruff`, `black` and `pytest` before opening a pull request.

## License

MIT License. See [LICENSE](LICENSE).
