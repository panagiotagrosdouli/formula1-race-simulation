# APEX Race Engineering Frontend

This directory contains the experimental React/Vite frontend for the Formula 1 Race Engineering Platform.

It is intentionally isolated from the existing Streamlit app so the current deployment remains stable while the new interface is developed.

## Location

```text
apps/frontend
```

## Stack

- React
- Vite
- TailwindCSS
- TanStack Query
- React Router
- Lucide icons

## Local development

From the repository root:

```bash
cd apps/frontend
npm install
npm run dev
```

By default, the frontend expects the FastAPI backend at:

```text
http://127.0.0.1:8000
```

Start the backend from the repository root:

```bash
uvicorn backend.app.main:app --reload
```

Then open the Vite URL printed in the terminal.

## Backend configuration

To point the frontend to another backend URL, create:

```text
apps/frontend/.env.local
```

with:

```bash
VITE_API_BASE_URL=http://127.0.0.1:8000
```

## Current backend integrations

The frontend currently uses these FastAPI endpoints:

```text
GET  /api/v1/health
POST /api/v1/strategy/preview
POST /api/v1/simulations/monte-carlo
```

## Current pages

- Home: backend health indicator and executive overview
- Race Predictor: Monte Carlo probability preview
- Strategy Lab: pit-window preview
- Telemetry Lab: placeholder for FastF1 telemetry workflows
- Live Race Control: placeholder for race-state monitoring
- Championship: placeholder for championship probability workflows
- AI Race Engineer: placeholder for explanation/chat workflows
- Reports: placeholder for report generation

## Development principle

This frontend should not duplicate or replace the Python simulation logic. It should consume typed backend endpoints and present the engineering outputs with a professional race-engineering user experience.

The existing Streamlit application remains the stable legacy interface until the React frontend is complete.
