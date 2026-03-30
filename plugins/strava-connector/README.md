# Strava Connector

Local coaching-focused Strava MCP for athlete profile, workout data, routes, and scheduled polling sync.

In Claude, this plugin requires Claude in Chrome MCP for app setup and scope or token repair flows.

Claude enforces that requirement through the plugin's default agent configuration in `settings.json`, which activates the `strava-connector` agent with `requiredMcpServers: ["Claude in Chrome"]`.

## Status

Implemented as a local Python MCP server plus Claude Code and Codex plugin wiring.

## Public MCP tools

- `strava_athlete_get_profile`
- `strava_athlete_get_zones`
- `strava_athlete_get_stats`
- `strava_athlete_update`
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

The local server uses Strava OAuth credentials in v1.

Claude in Chrome MCP is required in Claude for:

- creating the personal Strava app
- repairing app configuration
- re-authorizing scopes
- recovering from revoked or rotated refresh tokens

In Codex, those setup steps can be done manually in the browser instead.

Required durable credentials:

- `STRAVA_CLIENT_ID`
- `STRAVA_CLIENT_SECRET`
- `STRAVA_REFRESH_TOKEN`

Optional:

- `STRAVA_ACCESS_TOKEN`
- `STRAVA_ACCESS_TOKEN_EXPIRES_AT`
- `STRAVA_STORAGE_ROOT`
- `STRAVA_ATHLETE_SLUG`

The access token is runtime cache only. If client id, client secret, and refresh token are present, the server refreshes the access token in memory while it is running.

Recommended requested Strava scope set for this connector:

- `read`
- `read_all`
- `profile:read_all`
- `profile:write`
- `activity:read`
- `activity:read_all`
- `activity:write`

`strava_athlete_update` currently supports:

- `weight`

## Sync behavior

- v1 uses scheduled polling, not webhooks
- `strava_workouts_sync_recent` writes into `coaching/athletes/<athlete>/workouts/YYYY-MM-DD/activity-<id>/`
- sync is idempotent and rewrites the same file set for the same activity

## References

- `references/storage-contract.md` — required athlete/day folder ingestion contract.
- `skills/setup-strava-connector/SKILL.md` — local setup flow
- `skills/sync-recent-workouts/SKILL.md` — scheduled polling sync flow
- `skills/openclaw-strava-mcp/SKILL.md` — OpenClaw-compatible skill wrapper for this plugin
- `agents/strava-connector.md` — Claude default agent requiring Claude in Chrome MCP
