# APEX Race Engineering Frontend

This directory contains the React/Vite frontend for the Formula 1 Race Engineering Platform.

This is the main visual product interface you built. It is separate from the Streamlit app and should be deployed from this directory when you want people to see the polished APEX Race Engineering UI.

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

Then open the Vite URL printed in the terminal.

## Demo mode

The frontend now includes safe demo API fallbacks. That means the page is visible even if the FastAPI backend is not running.

When the backend is offline, the UI still shows:

- home dashboard status
- race predictor demo probabilities
- strategy preview demo recommendation
- all route/page shells

## Backend configuration

To connect to the FastAPI backend, create:

```text
apps/frontend/.env.local
```

with:

```bash
VITE_API_BASE_URL=http://127.0.0.1:8000
```

Start the backend from the repository root:

```bash
uvicorn backend.app.main:app --reload
```

## Deploy on Vercel

Use these settings:

```text
Root Directory: apps/frontend
Build Command: npm run build
Output Directory: dist
Install Command: npm install
```

The included `vercel.json` handles SPA fallback routing.

## Deploy on Netlify

Use these settings:

```text
Base directory: apps/frontend
Build command: npm run build
Publish directory: apps/frontend/dist
```

The included `netlify.toml` handles SPA fallback routing.

## Current pages

- Home: backend/demo health indicator and executive overview
- Race Predictor: Monte Carlo probability preview
- Strategy Lab: pit-window preview
- Telemetry Lab: placeholder for FastF1 telemetry workflows
- Live Race Control: placeholder for race-state monitoring
- Championship: placeholder for championship probability workflows
- AI Race Engineer: placeholder for explanation/chat workflows
- Reports: placeholder for report generation

## Development principle

This frontend should not duplicate or replace the Python simulation logic. It should consume typed backend endpoints and present the engineering outputs with a professional race-engineering user experience.
