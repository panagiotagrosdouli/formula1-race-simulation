# Reproducibility

Experiments live under `configs/experiments/` and must include deterministic seeds. Scripts write results under `results/`. Simulation logic lives in importable Python modules, not notebooks, so tests and dashboards share the same execution path.
