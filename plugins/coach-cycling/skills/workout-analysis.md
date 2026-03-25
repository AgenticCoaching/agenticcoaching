# Workout Analysis Skill

Analyze each completed workout day and produce coach-specific notes.

## Required input location

Use one folder per athlete/day:

`coaching/athletes/<athlete>/workouts/YYYY-MM-DD/`

Connector must store:
- `source.json` (source system, activity id, URL/reference)
- raw `*.fit` or `*.gpx` file
- optional streams (HR, cadence, power)

## Output

Write `notes.coach.md` with:
- session summary and execution quality
- load/intensity interpretation for this sport
- readiness/risk flags for next session
- concrete next-step recommendation
- confidence and missing-data caveats

Keep notes specific, concise, and actionable.
