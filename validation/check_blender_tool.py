#!/usr/bin/env python3
"""ACOS Phase D Blender MCP tool health check."""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore[assignment]

REPO = Path(__file__).resolve().parent.parent
BLENDER_TOOL = REPO / "tools" / "blender-mcp"
SHA_RE = re.compile(r"^[0-9a-f]{40}$")


def main() -> int:
    required = [
        BLENDER_TOOL / "UPSTREAM.yaml",
        BLENDER_TOOL / "capabilities.yaml",
        BLENDER_TOOL / "destructive-action-policy.yaml",
        BLENDER_TOOL / "security-review.yaml",
        BLENDER_TOOL / "schemas" / "blender-evidence.schema.yaml",
    ]
    missing = [str(p.relative_to(REPO)) for p in required if not p.is_file()]
    if missing:
        print(json.dumps({
            "tool": "TOOL-BLENDER-01",
            "structural": "BLOCKED",
            "runtime": "BLOCKED",
            "missing": missing,
        }))
        return 1

    upstream = yaml.safe_load((BLENDER_TOOL / "UPSTREAM.yaml").read_text(encoding="utf-8"))
    sha = upstream.get("upstream", {}).get("commit_sha", "")
    if not SHA_RE.fullmatch(sha):
        print(json.dumps({
            "tool": "TOOL-BLENDER-01",
            "structural": "BLOCKED",
            "reason": f"Invalid pinned commit SHA: {sha}",
        }))
        return 1

    review = yaml.safe_load((BLENDER_TOOL / "security-review.yaml").read_text(encoding="utf-8"))
    review_status = review.get("review_status", "UNKNOWN")

    blender_exe = shutil.which("blender")
    runtime = "BLOCKED"
    runtime_reason = "Blender executable not found on PATH"
    blender_version = None

    if blender_exe:
        try:
            proc = subprocess.run(
                [blender_exe, "--version"],
                capture_output=True,
                text=True,
                timeout=30,
            )
            if proc.returncode == 0:
                blender_version = proc.stdout.splitlines()[0] if proc.stdout else "unknown"
                runtime = "RESTRICTED"
                runtime_reason = (
                    "Blender executable available; MCP server connection not verified in this check"
                )
        except (OSError, subprocess.TimeoutExpired) as exc:
            runtime_reason = str(exc)

    print(json.dumps({
        "tool": "TOOL-BLENDER-01",
        "structural": "CONFIGURED",
        "runtime": runtime,
        "upstream_commit": sha,
        "upstream_version": upstream.get("upstream", {}).get("package_version"),
        "security_review_status": review_status,
        "blender_executable": blender_exe,
        "blender_version": blender_version,
        "mcp_connection_tested": False,
        "reason": runtime_reason,
        "notes": "MCP connectivity requires Blender running with addon — not auto-tested here",
    }))
    return 0


if __name__ == "__main__":
    if yaml is None:
        print("PyYAML required", file=sys.stderr)
        sys.exit(1)
    sys.exit(main())
