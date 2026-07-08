# System Architecture

```text
configs -> f1sim.data -> f1sim.core -> f1sim.models
                                  -> f1sim.weather
                                  -> f1sim.safety_car
                                  -> f1sim.strategy
                                  -> f1sim.simulation
                                  -> f1sim.evaluation / visualization / dashboard
```

The architecture keeps simulation logic in Python modules, not notebooks. Dashboards and scripts call the package API.

## Design principles

1. Configuration-driven experiments.
2. Deterministic seeds for reproducibility.
3. Clear implemented/prototype/planned separation.
4. No fake official data.
5. Small testable model components.

## Data flow

A YAML config defines drivers, race length, pit loss, weather risk and strategies. The simulation engine advances all drivers lap by lap, applies tyre/fuel/weather/SC models, reorders classification by race clock and exports metrics/history.
