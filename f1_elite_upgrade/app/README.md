# F1Sim Pro Multipage Streamlit App

This directory contains the primary Streamlit product experience for the repository.

## Entry points

Direct multipage app entrypoint:

```bash
streamlit run f1_elite_upgrade/app/Home.py
```

For Streamlit Community Cloud, use:

```text
Main file path: f1_elite_upgrade/app/Home.py
```

The repository-root `streamlit_app.py` is kept as a compatibility fallback, but the direct entrypoint above is preferred because Streamlit discovers the adjacent `pages/` directory.

## Product direction

F1Sim Pro is designed as a Formula 1-style AI engineering and race intelligence platform, not a simple demo dashboard. The app is organized as a race-weekend command center with dedicated workspaces for replay, circuit intelligence, prediction, simulation, strategy, telemetry, tyres, weather, drivers, teams, tracks, championship scenarios, model performance and reports.

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
- `12_Weather_Center.py` — weather uncertainty and track-evolution workspace
- `13_Monte_Carlo_Lab.py` — uncertainty, confidence interval and risk analysis
- `14_Fantasy_Roster_Manager.py` — prototype roster, budget and contract workspace
- `15_Reproducibility_Settings.py` — seeds, configs, data policy and roadmap
- `16_Championship_Center.py` — driver and constructor title scenario workspace
- `17_Model_Performance.py` — validation, calibration and explainability workspace
- `18_Race_Replay_Studio.py` — replay-style circuit visualizer, timing wall, tyre status and safety-car state
- `19_Circuit_Viewer.py` — circuit profile, DRS zones, pit markers, tyre stress and strategy implications

## Data honesty

The app never claims private Formula 1 team data. Synthetic examples are labelled as prototype/demo values. Public data integrations such as FastF1/OpenF1 are scaffolds unless explicitly configured and cited. The Race Replay Studio currently derives car positions from simulation state and gap progression; public positional telemetry can be connected in a later phase when available and permitted. Circuit Viewer maps are stylized profiles until calibrated public track geometry is added.

## Engineering standards

- Keep UI separate from simulation and data logic.
- Prefer deterministic seeds for simulation outputs.
- Use weekend-aware evaluation where possible.
- Do not present prototype probabilities as calibrated truth.
- Document every limitation that affects interpretation.

## Next build phases

1. Add real public-data adapters where terms allow it.
2. Add richer race-weekend state and session selector.
3. Add driver, team and track profiles calibrated from public history.
4. Add report figure exports and cross-scenario comparison.
5. Add automated UI smoke tests for every page.
