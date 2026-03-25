# Workout Analysis Skill

Analyze each completed workout day and produce nutrition-relevant notes.

## Required input location

Use one folder per athlete/day:

`coaching/athletes/<athlete>/workouts/YYYY-MM-DD/`

Connector must store:
- `source.json` (source system, activity id, URL/reference)
- raw `*.fit` or `*.gpx` file
- optional streams (HR, cadence, power)

## Output

Write `notes.nutrition.md` with:
- fueling/hydration implications from session load
- carb timing recommendation for next 24h
- GI-risk notes and gut-training suggestion
- confidence and missing-data caveats

Keep notes practical and athlete-safe.
