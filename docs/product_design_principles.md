# Product Design Principles

This project should feel like a professional Formula 1 decision-support platform, not a game-style dashboard.

## Target experience

The interface should be clear enough for students and portfolio reviewers, but credible enough for motorsport engineers, data scientists, and technical recruiters.

## Visual direction

- Use calm, professional colors.
- Prefer slate, navy, blue-gray, and neutral tones.
- Use accent colors sparingly.
- Avoid excessive red, neon effects, and aggressive racing-game styling.
- Prioritize readability over visual drama.
- Use consistent spacing, borders, and typography.

## Language

Prefer professional product language:

- Forecast, not prediction.
- Validation metrics, not accuracy.
- Predictive model, not AI magic.
- Engineering assessment, not chatbot.
- Execute forecast, not generate.
- Run simulation, not go.

## Components

Use shared components from `app/components/theme.py` whenever possible:

- `inject_theme()`
- `hero()`
- `card()`
- `metric_card()`
- `feed_line()`

Avoid page-local CSS unless a page has a specific, justified layout need.

## Product standard

Every UI change should answer at least one of these questions:

1. Does this help the user understand a forecast?
2. Does this communicate uncertainty more clearly?
3. Does this make the app easier for non-experts to use?
4. Does this make the project feel more credible and professional?

If the answer is no, the change should not be implemented.
