from __future__ import annotations

import json
import sys
import traceback
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional

from .storage import default_athlete_slug, default_storage_root, persist_workout_bundle
from .strava_api import DEFAULT_STREAM_KEYS, StravaApiClient, StravaApiError


JsonDict = Dict[str, Any]


def _json_schema(
    properties: Dict[str, Any],
    required: Optional[List[str]] = None,
    additional_properties: bool = False,
) -> JsonDict:
    schema: JsonDict = {
        "type": "object",
        "properties": properties,
        "additionalProperties": additional_properties,
    }
    if required:
        schema["required"] = required
    return schema


@dataclass
class ToolSpec:
    name: str
    description: str
    input_schema: JsonDict
    handler: Callable[[JsonDict], JsonDict]


class StravaCoachMCPServer:
    protocol_version = "2024-11-05"

    def __init__(self, api_client: Optional[StravaApiClient] = None) -> None:
        self.api_client = api_client or StravaApiClient()
        self.tools: Dict[str, ToolSpec] = {}
        self._register_tools()

    def _register(self, spec: ToolSpec) -> None:
        self.tools[spec.name] = spec

    def _register_tools(self) -> None:
        self._register(
            ToolSpec(
                name="strava_athlete_get_profile",
                description="Fetch the authenticated athlete profile for coaching context.",
                input_schema=_json_schema({}),
                handler=lambda _args: {"athlete": self.api_client.get_profile()},
            )
        )
        self._register(
            ToolSpec(
                name="strava_athlete_get_zones",
                description="Fetch heart rate and power zones for the authenticated athlete.",
                input_schema=_json_schema({}),
                handler=lambda _args: {"zones": self.api_client.get_zones()},
            )
        )
        self._register(
            ToolSpec(
                name="strava_athlete_get_stats",
                description="Fetch aggregate athlete stats for the authenticated athlete or a matching athlete id.",
                input_schema=_json_schema(
                    {"athlete_id": {"type": "integer", "description": "Optional athlete id. Defaults to the authenticated athlete."}}
                ),
                handler=self._handle_athlete_get_stats,
            )
        )
        self._register(
            ToolSpec(
                name="strava_athlete_update",
                description="Update athlete profile fields supported by Strava.",
                input_schema=_json_schema(
                    {
                        "weight": {"type": "number", "description": "Athlete weight in kilograms."},
                    }
                ),
                handler=self._handle_athlete_update,
            )
        )
        self._register(
            ToolSpec(
                name="strava_activities_list",
                description="List recent or date-ranged athlete activities.",
                input_schema=_json_schema(
                    {
                        "before": {"type": "integer", "description": "Epoch timestamp upper bound."},
                        "after": {"type": "integer", "description": "Epoch timestamp lower bound."},
                        "page": {"type": "integer"},
                        "per_page": {"type": "integer"},
                    }
                ),
                handler=self._handle_activities_list,
            )
        )
        self._register(
            ToolSpec(
                name="strava_activity_get",
                description="Fetch detailed metadata for one activity.",
                input_schema=_json_schema(
                    {
                        "activity_id": {"type": "integer"},
                        "include_all_efforts": {"type": "boolean"},
                    },
                    required=["activity_id"],
                ),
                handler=self._handle_activity_get,
            )
        )
        self._register(
            ToolSpec(
                name="strava_activity_get_laps",
                description="Fetch lap and split data for one activity.",
                input_schema=_json_schema({"activity_id": {"type": "integer"}}, required=["activity_id"]),
                handler=lambda args: {"activity_id": args["activity_id"], "laps": self.api_client.get_activity_laps(args["activity_id"])},
            )
        )
        self._register(
            ToolSpec(
                name="strava_activity_get_zones",
                description="Fetch activity zones when available.",
                input_schema=_json_schema({"activity_id": {"type": "integer"}}, required=["activity_id"]),
                handler=lambda args: {"activity_id": args["activity_id"], "zones": self.api_client.get_activity_zones(args["activity_id"])},
            )
        )
        self._register(
            ToolSpec(
                name="strava_activity_get_streams",
                description="Fetch activity streams for coaching metrics such as heartrate, power, cadence, temperature, and position.",
                input_schema=_json_schema(
                    {
                        "activity_id": {"type": "integer"},
                        "stream_keys": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Defaults to the coaching-focused stream key set.",
                        },
                    },
                    required=["activity_id"],
                ),
                handler=self._handle_activity_get_streams,
            )
        )
        self._register(
            ToolSpec(
                name="strava_activity_update",
                description="Update coaching-relevant activity metadata, including description and assigned gear.",
                input_schema=_json_schema(
                    {
                        "activity_id": {"type": "integer"},
                        "description": {"type": "string"},
                        "name": {"type": "string"},
                        "commute": {"type": "boolean"},
                        "trainer": {"type": "boolean"},
                        "hide_from_home": {"type": "boolean"},
                        "sport_type": {"type": "string"},
                        "gear_id": {"type": "string", "description": "Use 'none' to clear gear."},
                    },
                    required=["activity_id"],
                ),
                handler=self._handle_activity_update,
            )
        )
        self._register(
            ToolSpec(
                name="strava_gear_get",
                description="Fetch gear metadata and distance.",
                input_schema=_json_schema({"gear_id": {"type": "string"}}, required=["gear_id"]),
                handler=lambda args: {"gear": self.api_client.get_gear(args["gear_id"])},
            )
        )
        self._register(
            ToolSpec(
                name="strava_routes_list",
                description="List athlete routes available for export or delivery.",
                input_schema=_json_schema(
                    {
                        "athlete_id": {"type": "integer", "description": "Optional athlete id. Defaults to the authenticated athlete."},
                        "page": {"type": "integer"},
                        "per_page": {"type": "integer"},
                    }
                ),
                handler=self._handle_routes_list,
            )
        )
        self._register(
            ToolSpec(
                name="strava_route_get",
                description="Fetch route metadata by route id.",
                input_schema=_json_schema({"route_id": {"type": "integer"}}, required=["route_id"]),
                handler=lambda args: {"route": self.api_client.get_route(args["route_id"])},
            )
        )
        self._register(
            ToolSpec(
                name="strava_route_download_gpx",
                description="Download a route GPX export.",
                input_schema=_json_schema(
                    {"route_id": {"type": "integer"}, "output_path": {"type": "string"}},
                    required=["route_id"],
                ),
                handler=lambda args: self._handle_route_download(args, export_format="gpx"),
            )
        )
        self._register(
            ToolSpec(
                name="strava_route_download_tcx",
                description="Download a route TCX export.",
                input_schema=_json_schema(
                    {"route_id": {"type": "integer"}, "output_path": {"type": "string"}},
                    required=["route_id"],
                ),
                handler=lambda args: self._handle_route_download(args, export_format="tcx"),
            )
        )
        self._register(
            ToolSpec(
                name="strava_workout_get_bundle",
                description="Fetch one coaching-ready workout bundle with activity detail, laps, zones, streams, and optional gear and route data.",
                input_schema=_json_schema(
                    {
                        "activity_id": {"type": "integer"},
                        "stream_keys": {"type": "array", "items": {"type": "string"}},
                        "include_route_files": {"type": "boolean"},
                    },
                    required=["activity_id"],
                ),
                handler=self._handle_workout_get_bundle,
            )
        )
        self._register(
            ToolSpec(
                name="strava_workouts_sync_recent",
                description="List recent activities, hydrate each workout bundle, and persist them into the AgenticCoaching workout-day structure.",
                input_schema=_json_schema(
                    {
                        "before": {"type": "integer"},
                        "after": {"type": "integer"},
                        "page": {"type": "integer"},
                        "per_page": {"type": "integer"},
                        "stream_keys": {"type": "array", "items": {"type": "string"}},
                        "storage_root": {"type": "string", "description": "Defaults to STRAVA_STORAGE_ROOT or ./coaching in the current working directory."},
                        "athlete_slug": {"type": "string", "description": "Defaults to STRAVA_ATHLETE_SLUG or default-athlete."},
                        "include_route_files": {"type": "boolean"},
                    }
                ),
                handler=self._handle_workouts_sync_recent,
            )
        )

    def _resolve_authenticated_athlete_id(self, requested_id: Optional[int] = None) -> int:
        profile = self.api_client.get_profile()
        athlete_id = profile["id"]
        if requested_id is not None and requested_id != athlete_id:
            raise ValueError("athlete_id must match the authenticated athlete for this server instance.")
        return athlete_id

    def _safe_optional(self, fetcher: Callable[[], Any], label: str, warnings: List[str]) -> Any:
        try:
            return fetcher()
        except StravaApiError as exc:
            if exc.status in {403, 404}:
                warnings.append(f"{label} unavailable: HTTP {exc.status}")
                return None
            raise

    def _build_bundle(
        self,
        *,
        activity_id: int,
        stream_keys: Optional[List[str]] = None,
        include_route_files: bool = False,
    ) -> JsonDict:
        warnings: List[str] = []
        activity = self.api_client.get_activity(activity_id)
        laps = self.api_client.get_activity_laps(activity_id)
        zones = self._safe_optional(lambda: self.api_client.get_activity_zones(activity_id), "activity_zones", warnings)
        streams = self.api_client.get_activity_streams(activity_id, stream_keys or DEFAULT_STREAM_KEYS)

        gear = None
        gear_id = activity.get("gear_id")
        if gear_id:
            gear = self._safe_optional(lambda: self.api_client.get_gear(str(gear_id)), "gear", warnings)

        route = None
        route_gpx = None
        route_tcx = None
        route_id = activity.get("route_id")
        if route_id:
            route = self._safe_optional(lambda: self.api_client.get_route(int(route_id)), "route", warnings)
            if include_route_files:
                route_gpx = self._safe_optional(lambda: self.api_client.download_route_gpx(int(route_id)), "route_gpx", warnings)
                route_tcx = self._safe_optional(lambda: self.api_client.download_route_tcx(int(route_id)), "route_tcx", warnings)

        return {
            "activity": activity,
            "laps": laps,
            "zones": zones,
            "streams": streams,
            "gear": gear,
            "route": route,
            "route_gpx": route_gpx,
            "route_tcx": route_tcx,
            "warnings": warnings,
        }

    def _handle_athlete_get_stats(self, args: JsonDict) -> JsonDict:
        athlete_id = self._resolve_authenticated_athlete_id(args.get("athlete_id"))
        return {"athlete_id": athlete_id, "stats": self.api_client.get_stats(athlete_id)}

    def _handle_athlete_update(self, args: JsonDict) -> JsonDict:
        payload = {key: value for key, value in args.items() if key in {"weight"} and value is not None}
        if not payload:
            raise ValueError("strava_athlete_update requires: weight.")
        athlete = self.api_client.update_athlete(payload)
        return {
            "athlete": athlete,
            "applied_updates": payload,
        }

    def _handle_activities_list(self, args: JsonDict) -> JsonDict:
        activities = self.api_client.list_activities(
            before=args.get("before"),
            after=args.get("after"),
            page=args.get("page"),
            per_page=args.get("per_page"),
        )
        return {"activities": activities, "count": len(activities)}

    def _handle_activity_get(self, args: JsonDict) -> JsonDict:
        activity = self.api_client.get_activity(args["activity_id"], bool(args.get("include_all_efforts", False)))
        return {"activity": activity}

    def _handle_activity_get_streams(self, args: JsonDict) -> JsonDict:
        streams = self.api_client.get_activity_streams(args["activity_id"], args.get("stream_keys") or DEFAULT_STREAM_KEYS)
        return {"activity_id": args["activity_id"], "stream_keys": args.get("stream_keys") or DEFAULT_STREAM_KEYS, "streams": streams}

    def _handle_activity_update(self, args: JsonDict) -> JsonDict:
        allowed_fields = {
            "description",
            "name",
            "commute",
            "trainer",
            "hide_from_home",
            "sport_type",
            "gear_id",
        }
        payload = {key: value for key, value in args.items() if key in allowed_fields and value is not None}
        if not payload:
            raise ValueError("strava_activity_update requires at least one update field in addition to activity_id.")
        updated = self.api_client.update_activity(args["activity_id"], payload)
        return {"activity": updated, "applied_updates": payload}

    def _handle_routes_list(self, args: JsonDict) -> JsonDict:
        athlete_id = self._resolve_authenticated_athlete_id(args.get("athlete_id"))
        routes = self.api_client.list_routes(athlete_id, page=args.get("page"), per_page=args.get("per_page"))
        return {"athlete_id": athlete_id, "routes": routes, "count": len(routes)}

    def _handle_route_download(self, args: JsonDict, export_format: str) -> JsonDict:
        route_id = args["route_id"]
        contents = (
            self.api_client.download_route_gpx(route_id)
            if export_format == "gpx"
            else self.api_client.download_route_tcx(route_id)
        )
        output_path = args.get("output_path")
        if output_path:
            from pathlib import Path

            path = Path(output_path).expanduser().resolve()
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(contents, encoding="utf-8")
            return {"route_id": route_id, "format": export_format, "output_path": str(path)}

        return {"route_id": route_id, "format": export_format, "contents": contents}

    def _handle_workout_get_bundle(self, args: JsonDict) -> JsonDict:
        return self._build_bundle(
            activity_id=args["activity_id"],
            stream_keys=args.get("stream_keys") or DEFAULT_STREAM_KEYS,
            include_route_files=bool(args.get("include_route_files", False)),
        )

    def _handle_workouts_sync_recent(self, args: JsonDict) -> JsonDict:
        activities = self.api_client.list_activities(
            before=args.get("before"),
            after=args.get("after"),
            page=args.get("page"),
            per_page=args.get("per_page"),
        )
        storage_root = default_storage_root(args.get("storage_root"))
        athlete_slug = default_athlete_slug(args.get("athlete_slug"))
        synced = []

        for activity in activities:
            bundle = self._build_bundle(
                activity_id=activity["id"],
                stream_keys=args.get("stream_keys") or DEFAULT_STREAM_KEYS,
                include_route_files=bool(args.get("include_route_files", True)),
            )
            synced.append(persist_workout_bundle(bundle, storage_root=storage_root, athlete_slug=athlete_slug))

        return {
            "athlete_slug": athlete_slug,
            "storage_root": str(storage_root),
            "synced_count": len(synced),
            "activities": synced,
        }

    def _tool_result(self, payload: JsonDict) -> JsonDict:
        return {
            "content": [{"type": "text", "text": json.dumps(payload, indent=2, sort_keys=True)}],
            "structuredContent": payload,
        }

    def handle_request(self, message: JsonDict) -> Optional[JsonDict]:
        method = message.get("method")
        request_id = message.get("id")

        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "protocolVersion": self.protocol_version,
                    "capabilities": {"tools": {"listChanged": False}},
                    "serverInfo": {"name": "strava-mcp", "version": "0.1.0"},
                },
            }

        if method == "notifications/initialized":
            return None

        if method == "tools/list":
            result = {
                "tools": [
                    {
                        "name": spec.name,
                        "description": spec.description,
                        "inputSchema": spec.input_schema,
                    }
                    for spec in self.tools.values()
                ]
            }
            return {"jsonrpc": "2.0", "id": request_id, "result": result}

        if method == "tools/call":
            params = message.get("params", {})
            name = params.get("name")
            arguments = params.get("arguments", {}) or {}
            spec = self.tools.get(name)
            if spec is None:
                return self._error_response(request_id, -32601, f"Unknown tool: {name}")
            try:
                payload = spec.handler(arguments)
            except (ValueError, StravaApiError) as exc:
                data = exc.payload if isinstance(exc, StravaApiError) else None
                code = -32001 if isinstance(exc, StravaApiError) else -32602
                return self._error_response(request_id, code, str(exc), data=data)
            except Exception as exc:  # pragma: no cover
                traceback.print_exc(file=sys.stderr)
                return self._error_response(request_id, -32099, f"Unexpected server error: {exc}")
            return {"jsonrpc": "2.0", "id": request_id, "result": self._tool_result(payload)}

        if method == "ping":
            return {"jsonrpc": "2.0", "id": request_id, "result": {}}

        return self._error_response(request_id, -32601, f"Unknown method: {method}")

    def _error_response(self, request_id: Any, code: int, message: str, data: Any = None) -> JsonDict:
        error: JsonDict = {"code": code, "message": message}
        if data is not None:
            error["data"] = data
        return {"jsonrpc": "2.0", "id": request_id, "error": error}

    def serve(self) -> None:
        for raw_line in sys.stdin:
            raw_line = raw_line.strip()
            if not raw_line:
                continue
            try:
                message = json.loads(raw_line)
            except json.JSONDecodeError:
                continue

            response = self.handle_request(message)
            if response is not None:
                sys.stdout.write(json.dumps(response) + "\n")
                sys.stdout.flush()
