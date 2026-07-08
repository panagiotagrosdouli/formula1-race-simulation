# Streamlit Deployment Guide

## Primary entrypoint

Use the repository-root entrypoint:

```bash
streamlit run streamlit_app.py
```

For Streamlit Community Cloud, set:

```text
Main file path: streamlit_app.py
```

## Recommended Python setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## What should appear

The deployed app should open as a dark Formula 1 engineering cockpit with sidebar navigation and these sections:

- Platform Overview
- Race Simulation Dashboard
- Tyre Engineering
- Fuel Model
- Weather Model
- Safety Car / VSC
- Strategy Lab
- Monte Carlo Lab
- Telemetry & Data
- Engineering Report
- About / Reproducibility

## Data and telemetry behaviour

The core Streamlit app does not require private or official F1 team data. YAML experiments are synthetic/example scenarios. CSV upload supports user-provided lap-time data. FastF1/OpenF1 are integration scaffolds and must be treated as public-data sources when enabled.

## Troubleshooting

### ImportError: fastf1

FastF1 is optional for CI and lightweight app startup. Legacy telemetry modules now use synthetic fallbacks when FastF1 is not installed. If real public session telemetry is needed, install FastF1 explicitly.

### No YAML configs found

Ensure `configs/experiments/` exists and contains `.yml` experiment files.

### App looks plain

Confirm `.streamlit/config.toml` is committed and Streamlit is launching from the repository root.

## Quality target

The app should feel like a serious race engineering interface: dark, fast, technical, reproducible and transparent about uncertainty and limitations.
