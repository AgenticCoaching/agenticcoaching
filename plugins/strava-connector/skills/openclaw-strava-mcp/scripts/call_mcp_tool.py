#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path


def _load_server(skill_scripts_dir: Path):
    plugin_root = skill_scripts_dir.parents[2]  # .../plugins/strava-connector
    vendor = plugin_root / "vendor"
    if not vendor.exists():
        raise SystemExit(f"Missing vendor path: {vendor}")
    sys.path.insert(0, str(vendor))
    from strava_mcp.mcp_server import StravaCoachMCPServer

    return StravaCoachMCPServer


def _bootstrap_access_token(token_path: Path) -> None:
    if os.getenv("STRAVA_ACCESS_TOKEN"):
        return
    if not token_path.exists():
        return
    try:
        payload = json.loads(token_path.read_text())
    except Exception:
        return

    for k_src, k_dst in (
        ("access_token", "STRAVA_ACCESS_TOKEN"),
        ("refresh_token", "STRAVA_REFRESH_TOKEN"),
        ("expires_at", "STRAVA_ACCESS_TOKEN_EXPIRES_AT"),
    ):
        v = payload.get(k_src)
        if v is not None:
            os.environ.setdefault(k_dst, str(v))


def main() -> None:
    parser = argparse.ArgumentParser(description="Call Strava MCP tools")
    parser.add_argument("tool")
    parser.add_argument("--args", default="{}")
    parser.add_argument("--token-path", default="~/.config/openclaw/strava/token.json")
    ns = parser.parse_args()

    tool_args = json.loads(ns.args)
    if not isinstance(tool_args, dict):
        raise SystemExit("--args must be a JSON object")

    _bootstrap_access_token(Path(ns.token_path).expanduser())

    server_cls = _load_server(Path(__file__).resolve().parent)
    server = server_cls()
    spec = server.tools.get(ns.tool)
    if spec is None:
        raise SystemExit(f"Unknown tool: {ns.tool}")

    payload = spec.handler(tool_args)
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
