# Enterprise F1 Race Strategy Platform Architecture

This document defines the target architecture for evolving the repository from a Streamlit analytics project into a professional Formula 1 race strategy simulator.

The existing Streamlit application remains deployable while the new platform is built in parallel.

---

## Product Goal

Build a race strategy simulator that feels credible to motorsport engineers and polished enough for a commercial product demo.

The simulator must separate:

- domain physics and race state
- simulation policies
- data ingestion
- API contracts
- frontend visualization
- reporting/export

No UI component should contain simulation logic. No simulation model should depend on Streamlit or React.

---

## Target Stack

### Frontend

- Next.js
- React
- TypeScript
- TailwindCSS
- shadcn/ui
- Framer Motion
- Recharts
- TanStack Query
- Zustand
- React Hook Form
- Zod

### Backend

- FastAPI
- Python
- Pydantic
- FastF1
- OpenF1
- WebSockets
- PostgreSQL
- Redis
- Docker

---

## Clean Architecture Layers

```text
apps/
  web/                      # Next.js frontend
  api/                      # FastAPI backend

packages/
  design-system/            # shared frontend components and tokens
  schemas/                  # generated API schemas when introduced

backend/
  app/
    domain/                 # pure F1 domain models and value objects
    application/            # use cases and orchestration
    infrastructure/         # FastF1, OpenF1, database, cache, file adapters
    api/                    # FastAPI routers, DTOs, WebSocket endpoints
    services/               # simulation services and dependency wiring
    tests/                  # backend tests
```

---

## Domain Driven Design Boundaries

### Race Simulation Context

Owns:

- race state
- lap state
- driver state
- car state
- tyre state
- weather state
- event state
- race classification

### Strategy Context

Owns:

- pit window optimization
- undercut/overcut calculation
- traffic prediction
- tyre offset
- fuel strategy
- ERS deployment
- risk analysis

### Telemetry Context

Owns:

- FastF1 sessions
- OpenF1 timing
- speed/throttle/brake traces
- sector analysis
- lap delta
- driver comparison

### Reporting Context

Owns:

- shareable prediction summaries
- markdown reports
- PDF reports
- Excel exports
- assumptions and limitations

---

## Scientific Honesty Rules

1. A model output is never displayed without assumptions.
2. Randomness must be seeded and documented.
3. Monte Carlo variance must be visible to users.
4. Missing live data must produce explicit degraded-mode messages.
5. Future race predictions must be labelled as estimates.
6. Placeholder values must be marked as demo values.
7. Driver/car/circuit parameters must be traceable to data, priors, or documented assumptions.

---

## Initial Migration Plan

### Phase 1 — Domain Foundation

- Add strongly typed Python domain models.
- Add FastAPI health and simulation-preview endpoints.
- Keep Streamlit app running unchanged.

### Phase 2 — Simulation Engine

- Move simulation logic into backend application services.
- Add deterministic seeds.
- Add tyre, weather, car, driver, circuit and event models.

### Phase 3 — API Layer

- Add `/api/v1/simulations` endpoints.
- Add WebSocket event streaming.
- Add typed request/response schemas.

### Phase 4 — Frontend Shell

- Add Next.js app shell.
- Add design system.
- Add race wall dashboard.

### Phase 5 — Data Adapters

- Add FastF1 adapter.
- Add OpenF1 adapter.
- Add CSV/JSON importers.
- Add Redis caching.
- Add PostgreSQL persistence.

### Phase 6 — Production Hardening

- Docker compose.
- CI/CD.
- linting/formatting.
- unit/integration/e2e tests.
- performance profiling.

---

## Non-Negotiable Engineering Standards

- Domain models are strongly typed.
- Simulation services are deterministic by default.
- External data adapters are isolated behind interfaces.
- UI never mutates domain state directly.
- Tests cover domain calculations before UI polish.
- Existing deployment should not break while the new platform is built.
