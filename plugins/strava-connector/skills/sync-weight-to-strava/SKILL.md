---
name: sync-weight-to-strava
description: Optionally keep Strava athlete weight up to date from user-provided body-weight check-ins. Use when a user gives a new weight and wants Strava updated automatically through the Strava MCP. Scheduling is user-defined (no fixed time in this skill).
---

# Sync Weight to Strava

Use this optional skill with the Strava connector plugin.

## Purpose

Whenever the user provides a new body weight, update Strava via MCP using `strava_athlete_update`.

Do not hardcode schedule timing in this skill. The user decides when check-ins run.

## Input

- New user weight in kg (e.g. `65.2`)

## Flow

1. Validate weight is a plausible numeric kg value.
2. Update Strava:

```bash
python3 skills/openclaw-strava-mcp/scripts/call_mcp_tool.py strava_athlete_update --args '{"weight": 65.2}'
```

3. Confirm update succeeded and echo applied weight.
4. Optionally persist local metrics history in athlete files if your coaching setup tracks body composition.

## Guardrails

- Do not invent missing weight values.
- If no new value is provided, ask for the weight first.
- Keep this skill schedule-agnostic; do not embed fixed cron times.
