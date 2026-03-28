---
name: setup-strava-connector
description: Set up the local Strava coaching connector, validate credentials, and verify the MCP can read athlete data before any sync workflow runs.
---

# Setup Strava Connector

Use this skill when the user wants to connect Strava locally for coaching workflows.

## What this connector expects

The v1 MCP is local-only and reads Strava credentials from environment variables.

Minimum:

- `STRAVA_ACCESS_TOKEN`

Recommended for long sessions:

- `STRAVA_ACCESS_TOKEN_EXPIRES_AT`
- `STRAVA_REFRESH_TOKEN`
- `STRAVA_CLIENT_ID`
- `STRAVA_CLIENT_SECRET`

Optional quality-of-life variables:

- `STRAVA_STORAGE_ROOT`
- `STRAVA_ATHLETE_SLUG`

## Setup flow

1. Create or open a Strava API app at `https://www.strava.com/settings/api`.
2. Use `localhost` as the callback domain for local development.
3. Request the minimum useful scopes for coaching:
   - `activity:read_all`
   - `activity:write`
   - `profile:read_all`
4. Export the credentials into the current shell or session settings.
5. Start or reload the MCP server.
6. Validate the connection with:
   - `strava_athlete_get_profile`
   - `strava_activities_list`
   - `strava_athlete_get_zones`

## Guardrails

- Do not promise webhook setup in v1.
- Do not claim raw FIT or GPX export for arbitrary historical activities.
- If the user wants multiple athletes, explain that v1 is one authenticated athlete per MCP server process.
