# F1 AI Forecasting Platform

Machine learning-driven Formula 1 forecasting and motorsport analytics platform built with Python, FastF1 telemetry, weather intelligence, Monte Carlo simulation, and interactive dashboards.

---

## Live Application
[https://formula1-race-simulation-zedxdrtifuxjybsngqxhg9.streamlit.app/](https://formula1-race-simulation-drx5rdypbfuhkzmrxeit4e.streamlit.app/)
---

## Overview

F1 AI Forecasting Platform is a complete motorsport data science project focused on forecasting Formula 1 race outcomes and championship standings using:

* machine learning
* Monte Carlo simulation
* weather intelligence
* telemetry analytics
* risk modeling
* championship forecasting
* interactive visualization

The system combines motorsport engineering concepts with modern ML workflows to estimate:

* finishing order
* win probabilities
* podium probabilities
* top-10 probabilities
* championship standings
* race risk
* weather impact

---

## Core Features

### Historical Race Prediction

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

### Future Race Forecasting

Forecasts races that have not yet occurred using:

* Driver Elo ratings
* Team Elo ratings
* rolling performance metrics
* recent form
* 2026 driver/team priors
* weather conditions

Outputs:

* predicted finishing order
* expected finishing position
* future race outlook

---

### Monte Carlo Simulation

Runs thousands of simulated races to estimate:

* win probability
* podium probability
* top-10 probability
* expected finish position
* median finish position

The simulation introduces uncertainty through:

* pace variation
* race randomness
* weather variability
* risk modeling

---

### Driver and Team Elo Ratings

Dynamic ranking system used to estimate competitive strength.

Metrics include:

* DriverElo
* TeamElo

The ratings evolve according to historical performance and are used for future race forecasting.

---

### Weather Intelligence

Integrates weather information using Open-Meteo.

Weather variables:

* air temperature
* humidity
* wind speed
* rain probability

Weather impacts:

* forecast uncertainty
* race volatility
* Monte Carlo variability
* race risk estimation

---

### Safety Car & DNF Risk Modeling

Estimates race risk using:

* circuit characteristics
* weather conditions
* team reliability
* rookie status
* historical retirement rates

Outputs:

* Safety Car probability
* DNF risk
* risk adjustment score

---

### Telemetry Analysis

Uses FastF1 telemetry data for driver comparison.

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

### Race Strategy Optimization

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

### AI Race Analyst

Automatically generates race reports including:

* projected winner
* podium outlook
* weather summary
* risk assessment
* probability analysis

The goal is to provide human-readable explanations alongside numerical forecasts.

---

### 2026 Championship Simulator

Simulates the entire Formula 1 season.

Outputs:

#### Drivers Championship

* expected points
* projected championship position

#### Constructors Championship

* constructor points
* projected championship position

---

### Real FastF1 Training

Train the platform using real Formula 1 sessions.

Supported data:

* qualifying sessions
* race sessions
* official timing information
* driver performance data

This allows the model to move beyond synthetic demonstration data and use real motorsport datasets.

---

## Technology Stack

| Category             | Tools                 |
| -------------------- | --------------------- |
| Language             | Python                |
| Machine Learning     | Scikit-Learn, XGBoost |
| Telemetry            | FastF1                |
| Data Processing      | Pandas, NumPy         |
| Visualization        | Plotly, Matplotlib    |
| Dashboard            | Streamlit             |
| Weather Intelligence | Open-Meteo            |
| Simulation           | Monte Carlo Methods   |

---

## Project Structure

```text
formula1-race-simulation/

app/
└── dashboard.py

src/
└── f1predictor/
    ├── data_loader.py
    ├── features.py
    ├── model.py
    ├── simulation.py
    ├── future_race_predictor.py
    ├── season_simulator.py
    ├── weather.py
    ├── race_risk.py
    ├── race_analyst.py
    ├── priors_2026.py
    ├── visualization.py
    ├── strategy_optimizer.py
    └── telemetry/
        ├── compare_drivers.py
        └── tire_degradation.py

tests/

requirements.txt
run_all.py
README.md
```

---

## Installation

Clone the repository:

```bash
git clone https://github.com/panagiotagrosdouli/formula1-race-simulation.git
cd formula1-race-simulation
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

### Streamlit Dashboard

```bash
streamlit run app/dashboard.py
```

### Telemetry Comparison

```bash
PYTHONPATH=src python src/f1predictor/telemetry/compare_drivers.py
```

### Tire Degradation Analysis

```bash
PYTHONPATH=src python src/f1predictor/telemetry/tire_degradation.py
```

### Strategy Optimization

```bash
PYTHONPATH=src python src/f1predictor/strategy_optimizer.py
```

---

## Dashboard Capabilities

The Streamlit dashboard includes:

### Historical Prediction

* model training
* race prediction
* probability analysis

### Future Race Forecast

* weather-aware forecasting
* risk modeling
* AI race analyst
* race probability estimation

### Championship Simulator

* drivers standings
* constructors standings
* season projections

### FastF1 Training

* real Formula 1 datasets
* historical model training

---

## Machine Learning Workflow

The pipeline follows a standard ML workflow:

1. Data ingestion
2. Feature engineering
3. Historical model training
4. Cross-validation
5. Future race forecasting
6. Risk modeling
7. Monte Carlo simulation
8. Championship projection
9. Visualization

---

## Academic Scope

This project combines concepts from:

* Machine Learning
* Probability Theory
* Monte Carlo Methods
* Statistical Modeling
* Data Science
* Motorsport Analytics
* Engineering Decision Systems

The platform serves as an applied forecasting and analytics framework for Formula 1 race prediction and championship simulation.

---

## Future Improvements

Planned upgrades:

* XGBoost model comparison
* neural-network forecasting
* Bayesian race simulation
* reinforcement learning strategy optimization
* live telemetry ingestion
* safety car event simulation
* tire strategy optimization
* real-time race prediction
* PostgreSQL telemetry database
* cloud-scale deployment

---

## Author

Panagiota Grosdouli

Electrical and Computer Engineering
