
# F1 AI Predictor

Machine learning-driven Formula 1 race prediction and motorsport analytics platform built with Python, telemetry data, Monte Carlo simulation, and interactive dashboards.

---


## Live Application

https://formula1-race-simulation-x8ajjwdsvf6igouiu4hwf3.streamlit.app/

---

## Overview

F1 AI Predictor is a complete data science and simulation project focused on predicting Formula 1 race outcomes using:

* machine learning
* race simulation
* telemetry analytics
* tire degradation modeling
* probabilistic forecasting
* strategy optimization

The system combines motorsport engineering concepts with modern ML workflows to estimate:

* finishing order
* podium probabilities
* win probabilities
* race pace evolution
* optimal tire strategies

---

## Core Features

### Race Prediction Engine

Predicts finishing positions using:

* qualifying pace
* grid position
* long-run pace
* team strength
* driver rating
* recent form

Built using:

* Random Forest Regression
* feature engineering
* cross-validation
* ranking analysis

---

### Monte Carlo Simulation

Runs thousands of simulated races to estimate:

* win probability
* podium probability
* top-10 probability
* expected finishing position

The simulation introduces uncertainty through:

* pace variation
* race randomness
* degradation variability

---

### Telemetry Analysis

Uses FastF1 telemetry to compare drivers directly.

Includes:

* speed traces
* distance-based telemetry
* fastest lap comparison
* sector performance analysis

Example:

* Verstappen vs Leclerc telemetry comparison

---

### Tire Degradation Modeling

Models tire wear and lap-time evolution over a stint.

Includes:

* degradation slope estimation
* tire cliff behavior
* compound comparison
* pace decay visualization

---

### Race Strategy Optimizer

Simulates complete race strategies.

Supports:

* one-stop strategies
* two-stop strategies
* undercut analysis
* pit-loss simulation

The optimizer evaluates:

* total race time
* compound effectiveness
* ideal pit windows

---

### Interactive Dashboard

Built with Streamlit.

Features:

* prediction tables
* probability visualization
* telemetry charts
* race simulation output
* interactive analytics

---

## Technology Stack

| Category        | Tools                 |
| --------------- | --------------------- |
| Language        | Python                |
| ML              | scikit-learn, XGBoost |
| Telemetry       | FastF1                |
| Data Processing | pandas, numpy         |
| Visualization   | matplotlib, plotly    |
| Dashboard       | Streamlit             |
| Simulation      | Monte Carlo methods   |

---

## Project Structure

```text
f1_ai_predictor/
│
├── app/
│   └── dashboard.py
│
├── assets/
│
├── cache/
│
├── src/
│   └── f1predictor/
│       ├── data_loader.py
│       ├── features.py
│       ├── model.py
│       ├── simulation.py
│       ├── visualization.py
│       ├── strategy_optimizer.py
│       └── telemetry/
│           ├── compare_drivers.py
│           └── tire_degradation.py
│
├── tests/
│
├── requirements.txt
├── run_all.py
└── README.md
```

---

## Installation

Clone the repository:

```bash
git clone https://github.com/YOUR_USERNAME/f1_ai_predictor.git
cd f1_ai_predictor
```

Create virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Running the Project

### Main Prediction Pipeline

```bash
python run_all.py
```

---

### Interactive Dashboard

```bash
streamlit run app/dashboard.py
```

---

### Telemetry Comparison

```bash
PYTHONPATH=src python src/f1predictor/telemetry/compare_drivers.py
```

---

### Tire Degradation Analysis

```bash
PYTHONPATH=src python src/f1predictor/telemetry/tire_degradation.py
```

---

### Strategy Optimization

```bash
PYTHONPATH=src python src/f1predictor/strategy_optimizer.py
```

---

## Example Outputs

The project generates:

* predicted finishing order
* Monte Carlo probability tables
* telemetry comparison plots
* tire degradation graphs
* race strategy simulations

Add screenshots inside:

```text
assets/
```

and reference them here.

---

## Machine Learning Workflow

The pipeline follows a standard ML workflow:

1. Data ingestion
2. Feature engineering
3. Model training
4. Cross-validation
5. Prediction generation
6. Monte Carlo simulation
7. Visualization

---

## Future Improvements

Planned upgrades:

* live telemetry ingestion
* weather intelligence
* reinforcement learning for pit strategy
* Bayesian race simulation
* safety car probability model
* neural-network-based race forecasting
* real-time live race prediction
* PostgreSQL telemetry database
* cloud deployment




