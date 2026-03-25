# Connector Storage Contract

Connectors own ingestion and storage for workout-day artifacts.

## Folder structure

Use:

`coaching/athletes/<athlete>/workouts/YYYY-MM-DD/`

## Required artifacts

1. `source.json`
```json
{
  "provider": "strava|garmin",
  "activity_id": "string",
  "activity_url": "https://...",
  "captured_at": "ISO-8601",
  "sport": "run|ride|strength|other"
}
```
2. Raw workout file: `activity-<id>.fit` or `activity-<id>.gpx`
3. Optional stream files (`*-streams-*.json`) when available

## Notes

- Connector writes data; coach plugins read and analyze.
- Preserve raw files; do not overwrite without versioning.
