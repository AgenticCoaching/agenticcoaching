# AgenticCoaching Marketplace

Claude Marketplace-style multi-plugin monorepo for coaching + fitness automation.

## Initial plugin set

- Setup
- Connector: Strava
- Connector: Garmin
- Automation: Daily Check-in
- Coach: Nutrition
- Coach: Running
- Coach: Cycling
- Coach: Strength

## Repository layout

```text
plugins/
  setup/
  connector-strava/
  connector-garmin/
  automation-daily-checkin/
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

Workout analysis is embedded in each coach plugin (running/cycling/strength/nutrition), not a separate marketplace plugin.


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


## Deployment models

- **Solo athlete**: one user, one athlete profile.
- **Household host**: one workspace with multiple athlete profiles.
- **Coach with clients**: one coach workspace managing many client athlete profiles.
