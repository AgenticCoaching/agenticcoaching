# AgenticCoaching Marketplace

Claude Marketplace-style multi-plugin monorepo for coaching + fitness automation.

## Initial plugin set

- Connector: Strava
- Connector: Garmin
- Automation: Daily Check-in
- Workout Analysis
- Coach: Nutrition
- Coach: Running
- Coach: Cycling
- Coach: Strength

## Repository layout

```text
plugins/
  connector-strava/
  connector-garmin/
  automation-daily-checkin/
  workout-analysis/
  coach-nutrition/
  coach-running/
  coach-cycling/
  coach-strength/
registry/
  plugins.json
schemas/
  plugin.schema.json
```

## How this works

Each plugin folder contains:

- `plugin.json` — plugin metadata and capabilities
- `README.md` — plugin behavior and contract
- `prompts/` — system/task prompts (where relevant)
- `openapi.yaml` (optional) — if plugin exposes API actions

## Next build steps

1. Implement auth/token vault + refresh strategy for Strava/Garmin.
2. Add unified athlete profile and data contracts.
3. Implement automation runner for Daily Check-in.
4. Add workout analysis pipeline (ingest -> features -> coach summary).
5. Add coach engines (nutrition/running/cycling/strength) using shared context.
6. Add CI validation for plugin manifests against schema.
