# New Athlete Onboarding

Run a structured onboarding and create the correct workspace model.

## Select operation mode

- `solo-athlete`
- `household-multi-athlete`
- `coach-with-clients`

## Required data to collect

- person name + preferred name
- timezone
- sport focus (running/cycling/strength/other)
- event goals (date + priority)
- known injury/risk notes
- weekly schedule constraints
- check-in preferences (morning/evening cadence)
- nutrition preferences/restrictions

## Files to initialize

For each athlete:

- `coaching/athletes/<athlete>/profile/profile.md`
- `coaching/athletes/<athlete>/plans/`
- `coaching/athletes/<athlete>/workouts/`
- `coaching/athletes/<athlete>/nutrition/daily/`
- `coaching/athletes/<athlete>/checkins/daily.json`

## Mode specifics

### solo-athlete

Create one athlete profile and set direct coaching defaults.

### household-multi-athlete

Create one folder per athlete under `coaching/athletes/`.
Ensure plans and notes remain athlete-scoped.

### coach-with-clients

Create one folder per client under `coaching/athletes/`.
Require client-safe separation in summaries and messaging.
Support coach-level overview file at `coaching/coach/clients-index.json`.

## Output

Write onboarding summary with:
- selected mode
- created paths
- missing fields
- recommended first 7-day setup steps
