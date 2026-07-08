# F1Sim Pro Design System

## Product identity

F1Sim Pro should feel like a professional motorsport race-intelligence system, not a generic Streamlit dashboard. The interface should communicate precision, speed, technical trust and scientific honesty.

## Visual principles

| Principle | Direction |
|---|---|
| Dark cockpit | Use a deep carbon background with subtle red and blue light gradients. |
| Engineering density | Show meaningful information, but keep hierarchy clear. |
| Formula-inspired | Use red accents, timing-wall structures and technical panels without copying official Formula 1 branding. |
| Scientific restraint | Avoid fake certainty, inflated claims or decorative noise. |
| Consistency | Use shared `theme.py` components rather than per-page custom styling. |

## Core components

### Hero

Use `hero(title, subtitle, pills)` at the top of every major page. The hero explains the engineering problem the page solves.

### Status cards

Use `status_cards(...)` for four high-level KPIs. Every page should answer: what is the state, what changed, what should the user notice?

### Section headers

Use `section_header(kicker, title, body)` for major content areas where visual hierarchy matters.

### Panels

Use `panel(title, body)` for limitations, interpretation and data provenance. This is important for scientific integrity.

### Workflow steps

Use `workflow_steps(...)` when explaining race-weekend logic or engineering decision flow.

## Chart design

- Use Plotly charts through `chart(fig)` so styling is consistent.
- Prefer line charts for timelines and pace evolution.
- Prefer bar charts for rankings and model metrics.
- Prefer scatter charts for trade-offs, such as value versus projected points.
- Avoid charts without interpretation.

## Page UX rules

Each page should contain:

1. A hero explaining the page mission.
2. A small KPI/status area.
3. One primary interaction.
4. One or two core charts.
5. A table for detailed inspection.
6. A limitations/provenance panel.

## Data honesty

- Synthetic values must be labelled as prototype/demo values.
- Public data sources must be cited when connected.
- Official F1, team, or F1 Fantasy data must not be implied unless licensed and verified.
- Prediction outputs must include uncertainty and interpretation.

## Navigation philosophy

The app should feel like a race-weekend operating system:

- Command Center
- Race Control
- Prediction Center
- Strategy Lab
- Telemetry Lab
- Tyre Lab
- Weather Center
- Monte Carlo Lab
- Driver Database
- Team Database
- Track Database
- Championship Center
- Model Performance
- Report Center
- Reproducibility Settings

## Long-term design target

The platform should resemble a blend of:

- race timing wall,
- telemetry workstation,
- strategy room,
- AI model governance dashboard,
- engineering report generator.

It should not look like a student assignment or a simple analytics demo.
