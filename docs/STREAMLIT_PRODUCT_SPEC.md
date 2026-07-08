# Streamlit Product Specification

## Product goal

The primary user experience is `streamlit_app.py`: a dark, premium Formula 1 race strategy engineering cockpit. It is designed for students, analysts, data scientists, simulation researchers and race strategy engineers who need transparent, reproducible race-strategy analysis.

## Visual direction

- Dark technical interface with Ferrari-red accent colour.
- Wide layout optimized for laptop and desktop screens.
- Sidebar navigation organized by engineering workflow.
- Metric cards for headline race intelligence.
- Plotly charts styled consistently with dark engineering panels.
- Clear separation between implemented models, prototypes and planned research extensions.
- No claims of official team usage or private telemetry access.

## Main sections

1. Platform Overview
   - Mission, system architecture, simulation pipeline and implementation status.
2. Race Simulation Dashboard
   - YAML experiment selection, deterministic seed, driver table, strategy table, race timeline, lap times, positions, gaps, tyres, pit stops and classification.
3. Tyre Engineering
   - Compound degradation, cliff behaviour, wetness and track-temperature sensitivity.
4. Fuel Model
   - Fuel mass, burn rate, lap-time effect and safety margin scaffold.
5. Weather Model
   - Rain probability, wetness transition, temperature and wind scaffold.
6. Safety Car / VSC
   - Neutralisation probability, lap-time multiplier, pit-loss reduction and restart limitation.
7. Strategy Lab
   - One-, two- and three-stop candidates, pit exposure, tyre loss, risk score, undercut and overcut deltas.
8. Monte Carlo Lab
   - Repeated seeded simulation, expected result, confidence interval and risk profile.
9. Telemetry & Data
   - CSV validation, lap-time normalization, driver pace estimation and data honesty warning.
10. Engineering Report
   - Markdown, CSV exports and assumptions.
11. About / Reproducibility
   - Deterministic seeds, data-source policy, limitations and roadmap.

## Data honesty policy

Synthetic examples are allowed only when clearly labelled. The platform must not fabricate official Formula 1 data, team telemetry, real strategy calls, or professional team usage.

## Quality bar

The Streamlit app should feel like an engineering platform, not a notebook demo. Every chart and metric should answer a race-strategy question: pace, degradation, pit-loss exposure, uncertainty, track position, or risk.
