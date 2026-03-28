# Strava Connector

Local coaching-focused Strava MCP for athlete profile, workout data, routes, and scheduled polling sync.

## Status

Implemented as a local Python MCP server plus Claude Code and Codex plugin wiring.

## Public MCP tools

- `strava_athlete_get_profile`
- `strava_athlete_get_zones`
- `strava_athlete_get_stats`
- `strava_activities_list`
- `strava_activity_get`
- `strava_activity_get_laps`
- `strava_activity_get_zones`
- `strava_activity_get_streams`
- `strava_activity_update`
- `strava_gear_get`
- `strava_routes_list`
- `strava_route_get`
- `strava_route_download_gpx`
- `strava_route_download_tcx`
- `strava_workout_get_bundle`
- `strava_workouts_sync_recent`

## Setup

The local server uses environment variables for Strava auth in v1.

Required:

- `STRAVA_ACCESS_TOKEN`

Optional:

- `STRAVA_ACCESS_TOKEN_EXPIRES_AT`
- `STRAVA_REFRESH_TOKEN`
- `STRAVA_CLIENT_ID`
- `STRAVA_CLIENT_SECRET`
- `STRAVA_STORAGE_ROOT`
- `STRAVA_ATHLETE_SLUG`

If client id, client secret, and refresh token are present, the server refreshes the access token in memory while it is running.

## Sync behavior

- v1 uses scheduled polling, not webhooks
- `strava_workouts_sync_recent` writes into `coaching/athletes/<athlete>/workouts/YYYY-MM-DD/activity-<id>/`
- sync is idempotent and rewrites the same file set for the same activity

## References

- `references/storage-contract.md` — required athlete/day folder ingestion contract.
- `skills/setup-strava-connector/SKILL.md` — local setup flow
- `skills/sync-recent-workouts/SKILL.md` — scheduled polling sync flow
