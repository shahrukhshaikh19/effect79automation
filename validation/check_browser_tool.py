#!/usr/bin/env python3
"""ACOS Phase D browser tool health check — structural + optional runtime."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
BROWSER = REPO / "tools" / "browser"


def main() -> int:
    required = [
        BROWSER / "package.json",
        BROWSER / "schemas" / "browser-evidence.schema.yaml",
        BROWSER / "scripts" / "capture-evidence.mjs",
        BROWSER / "scripts" / "health-check.mjs",
        BROWSER / "fixtures" / "blank.html",
    ]
    missing = [str(p.relative_to(REPO)) for p in required if not p.is_file()]
    if missing:
        print(json.dumps({
            "tool": "TOOL-BROWSER-01",
            "structural": "BLOCKED",
            "runtime": "BLOCKED",
            "missing": missing,
        }))
        return 1

    pkg = (BROWSER / "package.json").read_text(encoding="utf-8")
    if '"playwright": "1.49.1"' not in pkg:
        print(json.dumps({
            "tool": "TOOL-BROWSER-01",
            "structural": "BLOCKED",
            "runtime": "BLOCKED",
            "reason": "Playwright pin missing or changed",
        }))
        return 1

    print(json.dumps({
        "tool": "TOOL-BROWSER-01",
        "structural": "CONFIGURED",
        "runtime": "UNKNOWN",
        "playwright_pin": "1.49.1",
        "message": "Structural configuration valid",
    }))

    node_modules = BROWSER / "node_modules" / "playwright"
    if not node_modules.is_dir():
        print(json.dumps({
            "tool": "TOOL-BROWSER-01",
            "structural": "CONFIGURED",
            "runtime": "BLOCKED",
            "reason": "node_modules/playwright not installed — run npm ci in tools/browser",
        }))
        return 0

    result = subprocess.run(
        ["node", "scripts/health-check.mjs"],
        cwd=BROWSER,
        capture_output=True,
        text=True,
    )
    if result.stdout.strip():
        print(result.stdout.strip())
    if result.returncode != 0 and result.stderr:
        print(result.stderr, file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
