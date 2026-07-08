# Ultimate F1 Fantasy and Race Management Platform Blueprint

## Product vision

Build an interactive Formula 1 command platform that combines fantasy roster management, race strategy simulation, telemetry intelligence, dynamic market economics and community competition. The system should feel like a premium F1 digital product while remaining honest about data provenance.

This repository must not claim access to official Formula 1 Fantasy Game data unless a licensed integration exists. Until then, official game integration remains planned, while public-data scaffolds and synthetic examples are clearly labelled.

## Core pillars

| Pillar | Product capability | Current status |
|---|---|---|
| Race intelligence | Lap-by-lap simulation, tyre/fuel/weather/SC models, strategy ranking | Implemented / Prototype |
| Fantasy roster | 5 drivers + 1 constructor, 100M cost cap, dynamic values, contracts | Prototype |
| Live strategy | Pit-call predictions, compound switches, SC/VSC reaction calls | Prototype |
| Telemetry | CSV upload, public FastF1/OpenF1 scaffolds, driver pace estimation | Prototype |
| AI predictions | Monte Carlo race outcomes and projected points | Implemented / Prototype |
| Leagues | Global, private, head-to-head draft, constructor championships | Planned |
| Community | Shareable lineup cards, discussion hooks, FanAmp-style integration | Planned |

## Data integration policy

- Official F1 Fantasy data: planned only; requires licensed/authorized access.
- FastF1: public timing-data integration scaffold, optional dependency.
- OpenF1: public API scaffold, not yet a full live backend.
- CSV upload: implemented for user-supplied lap-time data.
- Synthetic examples: allowed only when explicitly labelled as demo/synthetic.

## Roster and budget economics

### Roster rules

| Rule | Value |
|---|---:|
| Cost cap | 100M |
| Drivers | 5 |
| Constructors | 1 |
| Contract types | Race-by-race, 3-race, 6-race |
| Transfer windows | Pre-weekend, post-qualifying, emergency wildcard |
| Risk mechanics | Buyout fee, form volatility, injury/penalty exposure scaffold |

### Dynamic pricing model

Base value is adjusted after each race-weekend phase:

```text
market_value_next = base_value
  + form_weight * recent_points_delta
  + quali_weight * qualifying_position_delta
  + practice_weight * long_run_pace_delta
  + upgrade_weight * upgrade_signal
  + demand_weight * transfer_demand_index
  - risk_weight * dnf_penalty_risk
```

All coefficients must be calibrated from historical/public data before being presented as predictive truth.

## Scoring matrix

| Event | Points |
|---|---:|
| Win | +25 |
| Podium | +15 |
| Top 10 finish | +6 |
| Position gained | +1 per place |
| Position lost | -1 per place |
| Fastest lap | +5 |
| Beats teammate | +4 |
| Clean race, no penalties | +3 |
| DNF mechanical | -8 |
| DNF crash | -12 |
| Penalty | -2 to -10 |
| Correct pit window call | +8 |
| Correct tyre switch call | +6 |
| Correct SC/VSC reaction | +10 |

## Live strategy phase

Managers act as race strategists during the Grand Prix:

1. Predict pit window.
2. Select target compound.
3. Decide undercut, overcut or track-position hold.
4. React to safety car or VSC.
5. Lock race engineer call before a countdown expires.

Calls score points only when the real or simulated outcome validates the decision.

## Chips and boosters

| Booster | Effect | Balance rule |
|---|---|---|
| Autopilot | Applies boost to highest scorer | Once per season |
| Triple Crown | Triples one driver score | Cannot stack with No Negative |
| No Negative | Floors roster negative score at zero | Two-race cooldown |
| Wet Weather Master | Bonus for wet-weather prediction accuracy | Only when rain probability threshold met |
| Cost Cap Breach | Temporary +5M budget | Heavy next-race buyout penalty |

## Platform architecture

```text
Streamlit frontend
  -> f1sim simulation engine
  -> fantasy economy module
  -> telemetry processing
  -> Monte Carlo prediction service
  -> report/export layer

Future production architecture:
  CDN + web app
  API gateway
  WebSocket live timing service
  Redis cache
  PostgreSQL fantasy state
  object storage for reports
  model workers for Monte Carlo simulations
```

## UX direction

The app should feel like a Formula 1 command center:

- Landing page with race-weekend status.
- Prediction leaderboard.
- Roster builder with budget and contract pressure.
- Live timing wall with strategy windows.
- Telemetry workstation.
- Strategy room.
- League hub.
- Engineering report center.

## Limitations

- No private or official team data is available.
- Official fantasy-game integration is not implemented.
- Live telemetry requires a real data provider and backend streaming architecture.
- Current Streamlit experience is a high-quality prototype, not a millions-user production deployment.
