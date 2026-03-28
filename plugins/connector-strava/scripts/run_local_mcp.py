#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path


def _candidate_roots(script_path: Path):
    plugin_root = script_path.resolve().parents[1]
    yield plugin_root / "vendor"
    yield plugin_root / "vendor" / "src"
    yield plugin_root.parents[2] / "strava-mcp" / "src"


def main() -> None:
    script_path = Path(__file__)
    for candidate in _candidate_roots(script_path):
        if candidate.exists():
            sys.path.insert(0, str(candidate))

    from strava_mcp.__main__ import main as run_server

    run_server()


if __name__ == "__main__":
    main()
