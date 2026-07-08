# F1Sim Pro Multipage Streamlit App

This directory contains the primary Streamlit product experience for the repository.

## Entry points

For local development from the repository root:

```bash
streamlit run streamlit_app.py
```

Direct multipage app entrypoint:

```bash
streamlit run f1_elite_upgrade/app/Home.py
```

For Streamlit Community Cloud, use:

```text
Main file path: streamlit_app.py
```

## Product direction

F1Sim Pro is designed as a Formula 1-style race intelligence platform, not a simple demo dashboard. The app is organized as a race-weekend command center with dedicated workspaces for prediction, strategy, telemetry, tyres, drivers, teams, tracks and reports.

## Pages

- `Home.py` — command center landing page
- `1_Telemetry_Lab.py` — telemetry comparison workspace
- `2_Strategy_Lab.py` — pit-stop and tyre strategy workspace
- `3_Race_Engineer_AI.py` — explainable race engineer recommendation page
- `4_Live_Timing_Demo.py` — live-timing style probability demo
- `5_Race_Control.py` — timing wall, positions, gaps, tyres and pit events
- `6_Prediction_Center.py` — Monte Carlo prediction and risk envelope
- `7_Tyre_Lab.py` — compound degradation and tyre-life analysis
- `8_Driver_Database.py` — prototype driver intelligence database
- `9_Team_Database.py` — prototype constructor intelligence database
- `10_Track_Database.py` — prototype circuit intelligence database
- `11_Report_Center.py` — reproducible Markdown and CSV report exports

## Data honesty

The app never claims private Formula 1 team data. Synthetic examples are labelled as prototype/demo values. Public data integrations such as FastF1/OpenF1 are scaffolds unless explicitly configured and cited.

## Next build phases

1. Add real public-data adapters where terms allow it.
2. Add richer race-weekend state and session selector.
3. Add driver, team and track profiles calibrated from public history.
4. Add report figure exports and cross-scenario comparison.
5. Add automated UI smoke tests for every page.
