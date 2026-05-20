# F1 AI Predictor

A complete Formula 1 prediction project using real session data, feature engineering, machine learning, Monte Carlo simulation, and a Streamlit dashboard.

## What this project does

The project can:

1. Download real F1 session data using FastF1.
2. Build a race-prediction dataset from qualifying and race results.
3. Engineer useful motorsport features such as qualifying gap, grid position, team strength, and recent race form.
4. Train a machine learning model to predict race finishing position.
5. Simulate thousands of races with Monte Carlo uncertainty.
6. Show win, podium, and top-10 probabilities in a dashboard.

## Project structure

```text
f1_ai_predictor/
├── app/
│   └── dashboard.py
├── data/
│   ├── raw/
│   └── processed/
├── notebooks/
├── src/
│   └── f1predictor/
│       ├── __init__.py
│       ├── config.py
│       ├── data_loader.py
│       ├── features.py
│       ├── model.py
│       ├── simulation.py
│       ├── visualization.py
│       └── cli.py
├── tests/
├── requirements.txt
├── .env.example
└── README.md
```

## Setup

```bash
cd f1_ai_predictor
python -m venv venv
```

### Windows

```bash
venv\Scripts\activate
```

### macOS / Linux

```bash
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Quick start

Build a demo dataset:

```bash
python -m src.f1predictor.cli build-demo-data
```

Train model:

```bash
python -m src.f1predictor.cli train
```

Run Monte Carlo simulation:

```bash
python -m src.f1predictor.cli simulate
```

Run dashboard:

```bash
streamlit run app/dashboard.py
```

## Using real FastF1 data

You can build a dataset from real historical races:

```bash
python -m src.f1predictor.cli build-fastf1-data --year 2024
```

FastF1 downloads data the first time, so the first run may take longer.

## Scientific notes

The model is not claiming deterministic prediction. Race outcomes are stochastic because of safety cars, weather, strategy, pit-stop variance, incidents, and reliability. For that reason, the project predicts a baseline finishing score and then uses Monte Carlo simulation to estimate probability distributions.

Important metrics:

- MAE: average absolute finishing-position error.
- Spearman correlation: whether the predicted ranking is directionally correct.
- Win probability: share of simulations where a driver finishes P1.
- Podium probability: share of simulations where a driver finishes P1-P3.
- Top-10 probability: share of simulations where a driver finishes P1-P10.

## Next improvements

- Add tire degradation models.
- Add sector-specific telemetry features.
- Add weather API integration.
- Add pit-stop strategy optimizer.
- Add team upgrade trend factor.
- Add driver-specific wet-weather and street-track ratings.
