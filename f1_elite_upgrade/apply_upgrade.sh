#!/usr/bin/env bash
set -e
mkdir -p app/pages src/f1predictor/telemetry src/f1predictor/strategy src/f1predictor/race_engineer src/f1predictor/live assets
cp -r app/pages/* ./app/pages/
cp -r src/f1predictor/telemetry/* ./src/f1predictor/telemetry/
cp -r src/f1predictor/strategy/* ./src/f1predictor/strategy/
cp -r src/f1predictor/race_engineer/* ./src/f1predictor/race_engineer/
cp -r src/f1predictor/live/* ./src/f1predictor/live/
if ! grep -q "F1 Intelligence Platform Upgrade" README.md 2>/dev/null; then
  cat ELITE_README_SECTION.md >> README.md
fi
printf "\nUpgrade applied. Run: streamlit run app/dashboard.py\n"
