---
name: openclaw-strava-mcp
description: Use the AgenticCoaching Strava Python MCP from OpenClaw. Trigger when users ask to fetch Strava profile/activities, sync recent workouts into coaching/athletes/<athlete>/workouts, or update Strava activity metadata (description, name, gear, commute/trainer flags).
---

# OpenClaw Strava MCP

Use this skill to call the Strava MCP toolset shipped in `plugins/strava-connector`.

## Required env

- `STRAVA_CLIENT_ID`
- `STRAVA_CLIENT_SECRET`
- `STRAVA_REFRESH_TOKEN`

One of:
- `STRAVA_ACCESS_TOKEN`, or
- token file with `access_token` at `~/.config/openclaw/strava/token.json`

## Wrapper script

Run:

```bash
python3 scripts/call_mcp_tool.py <tool_name> --args '<json-object>'
```

Example:

```bash
python3 scripts/call_mcp_tool.py strava_activities_list --args '{"per_page":10}'
python3 scripts/call_mcp_tool.py strava_workouts_sync_recent --args '{"athlete_slug":"arne","per_page":10}'
python3 scripts/call_mcp_tool.py strava_activity_update --args '{"activity_id":123456789,"description":"Easy aerobic"}'
```

## High-value tools

- `strava_athlete_get_profile`
- `strava_activities_list`
- `strava_activity_get`
- `strava_activity_update`
- `strava_workout_get_bundle`
- `strava_workouts_sync_recent`

## Storage behavior

`strava_workouts_sync_recent` writes to:

- `coaching/athletes/<athlete>/workouts/YYYY-MM-DD/activity-<id>/`

including `source.json`, `activity.json`, streams/laps/zones when available, and sync metadata.
