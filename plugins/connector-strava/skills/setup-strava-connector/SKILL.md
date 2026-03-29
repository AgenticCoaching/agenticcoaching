---
name: setup-strava-connector
description: Set up the local Strava coaching connector, validate credentials, and verify the MCP can read athlete data before any sync workflow runs.
---

# Setup Strava Connector

Use this skill when the user wants to connect Strava locally for coaching workflows.

## What this connector expects

The v1 MCP is local-only.

Minimum durable credentials to store locally:

- `STRAVA_CLIENT_ID`
- `STRAVA_CLIENT_SECRET`
- `STRAVA_REFRESH_TOKEN`

Ephemeral runtime values:

- `STRAVA_ACCESS_TOKEN_EXPIRES_AT`
- `STRAVA_ACCESS_TOKEN`

Optional quality-of-life variables:

- `STRAVA_STORAGE_ROOT`
- `STRAVA_ATHLETE_SLUG`

The access token should be treated as a cache, not durable state. The refresh token is the durable credential that keeps the connection alive without needing the browser again.

## Setup flow

1. Open the existing personal app or create it if it does not exist at `https://www.strava.com/settings/api`.
2. When creating or repairing the personal app, upload the connector logo from:
   - `/Users/arne/Development/AgenticCoaching/agenticcoaching/plugins/connector-strava/assets/AgenticCoachingLogo.png`
3. Use the athlete-specific naming pattern `Agentic Coaching - <athlete-slug>`.
4. Use `localhost` as the callback domain for local development.
5. Check whether the currently granted scopes are sufficient:
   - `activity:read_all`
   - `activity:write`
   - `profile:read_all`
6. If the current app authorization is missing any required scope, re-run Strava authorization for the same app and replace the locally stored refresh token with the newest returned refresh token.
7. If the locally stored refresh token no longer works because it was revoked or rotated on Strava, re-authorize the same app and replace the stored refresh token.
8. Persist only these durable local credentials:
   - `STRAVA_CLIENT_ID`
   - `STRAVA_CLIENT_SECRET`
   - `STRAVA_REFRESH_TOKEN`
9. Start or reload the MCP server. Let it obtain and refresh access tokens at runtime.
10. Validate the connection with:
   - `strava_athlete_get_profile`
   - `strava_activities_list`
   - `strava_athlete_get_zones`

## App creation details

- Use `AgenticCoachingLogo.png` for the app image instead of ad hoc screenshots or generated placeholders.
- If the browser automation flow is used, navigate the file picker directly to:
  - `/Users/arne/Development/AgenticCoaching/agenticcoaching/plugins/connector-strava/assets/AgenticCoachingLogo.png`
- Prefer repairing the existing `My API Application` for the athlete instead of creating a new app unless the app is missing or irreparably misconfigured.
- When Strava returns a new refresh token, overwrite the previously stored refresh token immediately. Older refresh tokens become invalid as soon as a new one is issued.

## Guardrails

- Do not promise webhook setup in v1.
- Do not claim raw FIT or GPX export for arbitrary historical activities.
- If the user wants multiple athletes, explain that v1 is one authenticated athlete per MCP server process.
