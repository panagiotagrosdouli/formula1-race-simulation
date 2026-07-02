# Backend API Guide

The backend is the first enterprise service layer for the Formula 1 Race Engineering Platform. It is intentionally separate from the Streamlit UI so simulation logic can be reused by future frontends, batch jobs and reporting tools.

Run locally:

```bash
uvicorn backend.app.main:app --reload
```

OpenAPI documentation is available at:

```text
http://127.0.0.1:8000/docs
```

---

## Health Check

```http
GET /api/v1/health
```

Example response:

```json
{
  "status": "ok",
  "service": "f1-race-engineering-backend"
}
```

---

## Strategy Preview

```http
POST /api/v1/strategy/preview
```

Purpose: return a deterministic pit-window recommendation from circuit, tyre and weather state.

Minimal request:

```json
{}
```

Example response:

```json
{
  "recommended_window_start": 27,
  "recommended_window_end": 31,
  "risk_label": "medium",
  "explanation": "Medium tyre age is 12 laps..."
}
```

Scientific note: this endpoint is a transparent baseline model. It is not a replacement for a full race strategy optimizer.

---

## Monte Carlo Simulation Preview

```http
POST /api/v1/simulations/monte-carlo
```

Purpose: run repeated deterministic race simulations using explicit seed offsets and probability inputs.

Minimal request:

```json
{}
```

Example request with two drivers:

```json
{
  "runs": 25,
  "random_seed": 42,
  "current_lap": 12,
  "base_lap_time_s": 92.0,
  "safety_car_probability": 0.02,
  "virtual_safety_car_probability": 0.01,
  "mechanical_failure_probability": 0.005,
  "drivers": [
    {
      "id": "LEC",
      "code": "LEC",
      "full_name": "Charles Leclerc",
      "team_id": "ferrari",
      "race_pace": 0.88,
      "qualifying_pace": 0.86,
      "tyre_management": 0.82,
      "wet_skill": 0.75,
      "overtaking": 0.76,
      "defending": 0.74,
      "consistency": 0.87,
      "aggression": 0.60,
      "reaction_time": 0.83,
      "pressure_handling": 0.84,
      "mechanical_sympathy": 0.80
    },
    {
      "id": "HAM",
      "code": "HAM",
      "full_name": "Lewis Hamilton",
      "team_id": "ferrari",
      "race_pace": 0.87,
      "qualifying_pace": 0.85,
      "tyre_management": 0.84,
      "wet_skill": 0.82,
      "overtaking": 0.80,
      "defending": 0.78,
      "consistency": 0.86,
      "aggression": 0.58,
      "reaction_time": 0.82,
      "pressure_handling": 0.88,
      "mechanical_sympathy": 0.82
    }
  ],
  "cars": [
    {"driver_id": "LEC"},
    {"driver_id": "HAM"}
  ]
}
```

Example response:

```json
{
  "runs": 25,
  "winner_counts": {
    "LEC": 14,
    "HAM": 11
  },
  "average_finish_position": {
    "LEC": 1.44,
    "HAM": 1.56
  },
  "assumptions": [
    "Monte Carlo samples are produced by deterministic race runs with controlled seed offsets.",
    "Probability inputs are explicit and should be calibrated against historical data."
  ]
}
```

---

## Engineering Assumptions

- Randomness is controlled through deterministic seed offsets.
- Probability inputs are explicit and should eventually be calibrated with historical race data.
- Driver and car inputs are normalized engineering priors in `[0, 1]`.
- This API layer is currently a preview service, not a complete race wall replacement.

---

## Next Backend Milestones

1. Add API tests for the Monte Carlo endpoint.
2. Add calibration documentation for probability inputs.
3. Add richer race state output for frontend dashboards.
4. Add WebSocket streaming for lap-by-lap race evolution.
5. Add persistence for simulation runs.
