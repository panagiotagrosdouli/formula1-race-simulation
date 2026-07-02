# F1  Race Engineering

A premium Formula 1 AI forecasting and motorsport analytics platform built with Python, Streamlit, FastF1-style telemetry, weather intelligence, Monte Carlo simulation, ML predictions, race-risk modelling, tyre strategy, and fan-friendly race storytelling.

**Live app:** https://formula1-race-simulation-injvb6zyfjh7kbs6nr4mh5.streamlit.app/

---

## Why this project matters

Formula 1 prediction is not only about guessing the winner. A credible racing intelligence product must combine pace, grid position, driver/team strength, uncertainty, weather, safety-car volatility, tyre degradation, pit strategy, telemetry and model limitations. This project is designed to be useful for two audiences at once:

- **F1 fans** who want beautiful race predictions, driver cards, race drama, simple explanations and shareable summaries.
- **Engineers/data people** who want probability distributions, assumptions, model diagnostics, telemetry context and transparent uncertainty.

The app is intentionally honest: every forecast is an estimate, not a guarantee.

---

## Product experience

The main Streamlit app is a modern F1 command-center style workspace with:

- **Fan Mode** — driver cards, storylines, simple-language explanations, shareable prediction summary.
- **Engineer Mode** — forecast tables, uncertainty diagnostics, assumptions, model/race limitations.
- **Race Control** — lap-by-lap race state, classification, track map and Monte Carlo probability chart.
- **Strategy Lab** — tyre plans, pit-lane loss sensitivity and pit-window analysis.
- **Telemetry Lab** — FastF1-style speed, delta, controls and track-map comparison workflows.
- **AI Race Analyst** — human-readable race brief and explainable recommendation layer.

### Screenshot / GIF placeholders

Add final media here after deployment:

```text
assets/screenshots/home.png
assets/screenshots/fan_mode_driver_cards.png
assets/screenshots/engineer_mode_uncertainty.png
assets/demo/f1_base44_elite_walkthrough.gif
```

---

## Core capabilities

### Race Predictor

Predicts finishing order and expected finish using historical/demo data plus future-race priors. Outputs are converted into win, podium and top-10 probabilities through simulation.

### Monte Carlo simulation

Runs repeated race simulations to estimate:

- win probability
- podium probability
- top-10 probability
- expected finish
- median finish
- uncertainty / approximate finish interval

### Fan storylines

The product intelligence layer generates:

- title battle pulse
- teammate battle
- dark horse
- biggest risk
- weather chaos factor
- “Why this prediction?” explanations
- copyable/downloadable prediction summary

### Engineering diagnostics

Engineer Mode surfaces:

- forecast table
- risk columns where available
- safety-car / DNF assumptions
- Monte Carlo probability table
- approximate finish intervals
- simulation limitations
- weather and pit-loss sensitivity notes

### Telemetry and strategy modules

The repository includes FastF1-style telemetry workflows, tyre degradation dashboards, strategy optimisation, pit-window simulation and live timing demos.

---

## Architecture

```text
formula1-race-simulation/
├── app/
│   ├── f1_analytics_platform.py      # Streamlit Cloud entrypoint
│   ├── components/theme.py           # shared Base44-style UI theme
│   └── pages/                        # Streamlit multipage workspaces
├── src/f1predictor/
│   ├── data_loader.py
│   ├── model.py
│   ├── simulation.py
│   ├── future_race_predictor.py
│   ├── product_intelligence.py       # fan/engineer product layer
│   ├── race_analyst.py
│   ├── race_risk.py
│   ├── season_simulator.py
│   ├── strategy_optimizer.py
│   ├── weather.py
│   └── telemetry/
├── tests/
├── docs/
├── requirements.txt
└── README.md
```

---

## Installation

```bash
git clone https://github.com/panagiotagrosdouli/formula1-race-simulation.git
cd formula1-race-simulation
python -m venv venv
source venv/bin/activate  # Windows: venv\\Scripts\\activate
pip install -r requirements.txt
```

---

## Run locally

Main deployed app:

```bash
streamlit run app/f1_analytics_platform.py
```

Original dashboard / extended workflows:

```bash
streamlit run app/dashboard.py
```

Pipeline:

```bash
python run_all.py
```

Tests:

```bash
pytest
```

---

## Streamlit Cloud deployment

Use:

```text
Repository: panagiotagrosdouli/formula1-race-simulation
Branch: main
Main file path: app/f1_analytics_platform.py
```

If the UI does not update after a commit, reboot the Streamlit app and hard-refresh the browser.

---

## Methodology

The project combines:

- ML-based finishing-position forecasting
- driver/team prior strength
- grid and pace features
- Monte Carlo uncertainty
- weather and race risk adjustments
- safety-car / DNF considerations
- tyre strategy modelling
- telemetry comparison
- product-layer explanation generation

The app separates **prediction**, **uncertainty**, **interpretation**, and **limitations** so the interface stays visually engaging but scientifically honest.

---

## Current limitations

- Demo/future races depend on priors and assumptions; they are not guarantees.
- FastF1 availability can fail because of network/cache/session support.
- Weather data can be unavailable or uncertain for future dates.
- Real F1 performance changes with upgrades, reliability, penalties, setup and race incidents.
- Approximate confidence intervals are UI diagnostics, not formal Bayesian posterior intervals yet.

---

## Roadmap

### Product

- Add official screenshot/GIF assets.
- Add exportable PNG/PDF race cards.
- Add share links for prediction summaries.
- Add mobile-first condensed views.

### Data science

- Add calibration plots and Brier/log-loss metrics.
- Add backtesting by race and by season.
- Add proper uncertainty intervals from simulation samples.
- Add richer feature importance / SHAP-style explanations.
- Add stronger safeguards for missing FastF1/weather data.

### Engineering

- Consolidate duplicated Streamlit pages.
- Move UI components into one design-system module.
- Improve tests around product intelligence and app imports.
- Add reproducible data snapshots for CI.

---

## Recruiter / portfolio notes

This repository demonstrates:

- applied ML and Monte Carlo simulation
- motorsport analytics domain modelling
- Streamlit product design and deployment
- Python package architecture
- user-facing explanation design
- fan/engineer dual-mode product thinking

---

## Author

Panagiota Grosdouli  
Electrical and Computer Engineering
