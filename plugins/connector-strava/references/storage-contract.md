# Connector Storage Contract

Connectors own ingestion and storage for workout-day artifacts.

## Folder structure

Use:

`coaching/athletes/<athlete>/workouts/YYYY-MM-DD/activity-<id>/`

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
2. `activity.json`
3. `laps.json`
4. `streams.json`
5. Optional `zones.json` when available
6. Optional `gear.json` when a gear assignment exists
7. Optional `route.json`, `route.gpx`, and `route.tcx` when a route is attached and exportable
8. `sync.json`

## Notes

- Connector writes data; coach plugins read and analyze.
- v1 Strava sync does not promise raw FIT or GPX export for arbitrary historical activities.
- Sync is idempotent at the activity-folder level and rewrites the same artifacts for the same activity id.
