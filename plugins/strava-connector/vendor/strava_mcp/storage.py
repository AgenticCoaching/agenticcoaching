from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def default_storage_root(explicit_root: Optional[str] = None) -> Path:
    if explicit_root:
        return Path(explicit_root).expanduser().resolve()

    env_root = os.getenv("STRAVA_STORAGE_ROOT")
    if env_root:
        return Path(env_root).expanduser().resolve()

    return (Path.cwd() / "coaching").resolve()


def default_athlete_slug(explicit_slug: Optional[str] = None) -> str:
    slug = explicit_slug or os.getenv("STRAVA_ATHLETE_SLUG") or "default-athlete"
    return slug.strip().lower().replace(" ", "-")


def workout_date_for_activity(activity: Dict[str, Any]) -> str:
    for key in ("start_date_local", "start_date"):
        value = activity.get(key)
        if value:
            return value[:10]
    return _utc_now_iso()[:10]


def workout_directory(storage_root: Path, athlete_slug: str, activity: Dict[str, Any]) -> Path:
    activity_id = activity["id"]
    workout_date = workout_date_for_activity(activity)
    return storage_root / "athletes" / athlete_slug / "workouts" / workout_date / f"activity-{activity_id}"


def _write_text(path: Path, contents: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(contents, encoding="utf-8")


def _write_json(path: Path, payload: Any) -> None:
    _write_text(path, json.dumps(payload, indent=2, sort_keys=True) + "\n")


def persist_workout_bundle(
    bundle: Dict[str, Any],
    storage_root: Path,
    athlete_slug: str,
) -> Dict[str, Any]:
    activity = bundle["activity"]
    directory = workout_directory(storage_root, athlete_slug, activity)
    files: List[str] = []

    source_payload = {
        "provider": "strava",
        "activity_id": str(activity["id"]),
        "activity_url": f"https://www.strava.com/activities/{activity['id']}",
        "captured_at": _utc_now_iso(),
        "sport": activity.get("sport_type") or activity.get("type") or "other",
    }
    source_path = directory / "source.json"
    _write_json(source_path, source_payload)
    files.append(str(source_path))

    activity_path = directory / "activity.json"
    _write_json(activity_path, activity)
    files.append(str(activity_path))

    laps = bundle.get("laps")
    if laps is not None:
        laps_path = directory / "laps.json"
        _write_json(laps_path, laps)
        files.append(str(laps_path))

    zones = bundle.get("zones")
    if zones is not None:
        zones_path = directory / "zones.json"
        _write_json(zones_path, zones)
        files.append(str(zones_path))

    streams = bundle.get("streams")
    if streams is not None:
        streams_path = directory / "streams.json"
        _write_json(streams_path, streams)
        files.append(str(streams_path))

    gear = bundle.get("gear")
    if gear is not None:
        gear_path = directory / "gear.json"
        _write_json(gear_path, gear)
        files.append(str(gear_path))

    route = bundle.get("route")
    if route is not None:
        route_path = directory / "route.json"
        _write_json(route_path, route)
        files.append(str(route_path))

    route_gpx = bundle.get("route_gpx")
    if route_gpx is not None:
        route_gpx_path = directory / "route.gpx"
        _write_text(route_gpx_path, route_gpx)
        files.append(str(route_gpx_path))

    route_tcx = bundle.get("route_tcx")
    if route_tcx is not None:
        route_tcx_path = directory / "route.tcx"
        _write_text(route_tcx_path, route_tcx)
        files.append(str(route_tcx_path))

    sync_path = directory / "sync.json"
    _write_json(
        sync_path,
        {
            "synced_at": _utc_now_iso(),
            "tool": "strava_workouts_sync_recent",
            "warnings": bundle.get("warnings", []),
        },
    )
    files.append(str(sync_path))

    return {
        "activity_id": activity["id"],
        "activity_dir": str(directory),
        "files": files,
    }


def list_relative_paths(root: Path) -> List[str]:
    return sorted(str(path.relative_to(root)) for path in root.rglob("*") if path.is_file())
