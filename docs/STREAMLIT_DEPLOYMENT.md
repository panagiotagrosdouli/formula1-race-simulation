# Streamlit Deployment Guide

## Primary multipage entrypoint

For the full F1Sim Pro multipage application, use:

```bash
streamlit run f1_elite_upgrade/app/Home.py
```

For Streamlit Community Cloud, set:

```text
Main file path: f1_elite_upgrade/app/Home.py
```

This is the recommended deployment path because Streamlit discovers pages from the `pages/` directory next to `Home.py`.

## Root fallback entrypoint

The repository root also contains:

```bash
streamlit run streamlit_app.py
```

This is kept as a compatibility fallback, but the direct `f1_elite_upgrade/app/Home.py` entrypoint is preferred for full multipage sidebar discovery.

## Recommended Python setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run f1_elite_upgrade/app/Home.py
```

## What should appear

The deployed app should open as a dark Formula 1-style race intelligence platform with sidebar navigation and these workspaces:

- Home command center
- Telemetry Lab
- Strategy Lab
- Race Engineer AI
- Live Timing Demo
- Race Control
- Prediction Center
- Tyre Lab
- Driver Database
- Team Database
- Track Database
- Report Center

## Data and telemetry behaviour

The app does not require private or official Formula 1 team data. YAML experiments are synthetic/example scenarios. CSV upload supports user-provided lap-time data. FastF1/OpenF1 are integration scaffolds and must be treated as public-data sources when enabled.

## Troubleshooting

### Sidebar pages do not appear

Make sure the Streamlit Cloud main file path is:

```text
f1_elite_upgrade/app/Home.py
```

If you deploy `streamlit_app.py`, the app may open but Streamlit may not discover the nested `pages/` directory automatically.

### ImportError: fastf1

FastF1 is optional for CI and lightweight app startup. Legacy telemetry modules use synthetic fallbacks when FastF1 is not installed. If real public session telemetry is needed, install FastF1 explicitly.

### No YAML configs found

Ensure `configs/experiments/` exists and contains `.yml` experiment files.

## Quality target

The app should feel like a serious Formula 1 operating system: dark, fast, technical, reproducible and transparent about uncertainty and limitations.
