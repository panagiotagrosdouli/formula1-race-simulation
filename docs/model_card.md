# F1 AI Predictor Model Card

## Intended use

This project estimates Formula 1 race finishing order and finishing-position probabilities for exploratory motorsport analytics, portfolio demonstration, and research-style experimentation.

It should not be treated as a betting system, a source of official Formula 1 results, or a calibrated production forecasting model without additional validation on real historical race data.

## Data

The repository includes a synthetic demo data generator so the full pipeline can run without external services. Synthetic data is useful for software validation, but it is not sufficient evidence of real-world predictive skill.

For scientific or production use, train and evaluate on historical FastF1-derived race data with a clear split by race weekend or season.

## Target

The current supervised-learning target is `FinishPosition`. The model predicts a continuous finishing-position score and converts that score into race rankings.

## Features

The model currently uses qualifying pace, grid position, long-run pace estimates, team/driver strength proxies, recent form, Elo-style features, DNF rate, weather features, and categorical identifiers for driver, team, and Grand Prix.

## Validation protocol

Recommended validation:

1. Split by race event or season, never by random driver rows from the same event.
2. Report MAE and RMSE for finishing-position score error.
3. Report ranking metrics such as Spearman correlation, top-3 recall, and winner accuracy.
4. Compare against simple baselines: grid order, previous-race form, and constructor-strength-only models.
5. Run calibration checks for Monte Carlo outputs, especially win/podium/top-10 probabilities.

## Known limitations

- Synthetic demo data can overstate model quality.
- Race outcomes depend on low-frequency events such as DNFs, safety cars, weather shifts, pit-stop execution, and penalties.
- Driver/team strength features can leak future information unless they are computed using only data available before the target race.
- Probability outputs are simulation-derived and should be calibrated against held-out historical races before high-stakes use.

## Reproducibility

The simulation code uses explicit random seeds. Keep random states fixed when comparing experiments, and vary seeds only when estimating uncertainty across runs.
