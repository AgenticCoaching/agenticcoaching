#!/usr/bin/env python3
import json
from pathlib import Path
root = Path(__file__).resolve().parents[1]
reg = json.loads((root / 'registry' / 'plugins.json').read_text())
for p in reg['plugins']:
    m = json.loads((root / p['manifest']).read_text())
    print(f"{m['type']:10} {m['id']:30} v{m['version']}  - {m['name']}")
