---
name: sync-recent-workouts
description: Poll recent Strava activities, hydrate each workout bundle with coaching metrics, and persist them into the AgenticCoaching workout-day structure.
---

# Sync Recent Workouts

Use this skill when the user wants to ingest recent Strava workouts into the local AgenticCoaching storage layout.

## Default behavior

- Use `strava_workouts_sync_recent`
- Prefer scheduled polling multiple times per day
- Default stream set:
  - `time`
  - `distance`
  - `latlng`
  - `altitude`
  - `velocity_smooth`
  - `grade_smooth`
  - `heartrate`
  - `cadence`
  - `watts`
  - `temp`
  - `moving`

## Storage contract

The tool writes to:

`coaching/athletes/<athlete>/workouts/YYYY-MM-DD/activity-<id>/`

and persists:

- `source.json`
- `activity.json`
- `laps.json`
- `streams.json`
- optional `zones.json`
- optional `gear.json`
- optional `route.json`
- optional `route.gpx`
- optional `route.tcx`
- `sync.json`

## Usage guidance

- Prefer passing a bounded `after` timestamp for routine syncs.
- Let the tool use its idempotent rewrite behavior rather than inventing duplicate-avoidance filenames.
- After sync, summarize:
  - synced activity count
  - athlete slug
  - storage root
  - any warnings such as missing zones or unavailable route exports
