#!/usr/bin/env python3
"""ACOS Phase D git tool health check."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


def main() -> int:
    policy = REPO / "tools" / "git" / "git-policy.yaml"
    contract = REPO / "tools" / "git" / "CONTRACT.md"
    if not policy.is_file() or not contract.is_file():
        print(json.dumps({
            "tool": "TOOL-GIT-01",
            "structural": "BLOCKED",
            "runtime": "BLOCKED",
            "missing": "git contract files",
        }))
        return 1

    git_exe = shutil.which("git")
    if not git_exe:
        print(json.dumps({
            "tool": "TOOL-GIT-01",
            "structural": "CONFIGURED",
            "runtime": "BLOCKED",
            "reason": "git executable not on PATH",
        }))
        return 0

    try:
        proc = subprocess.run(
            [git_exe, "rev-parse", "--is-inside-work-tree"],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=15,
        )
        inside = proc.stdout.strip() == "true"
    except (OSError, subprocess.TimeoutExpired) as exc:
        print(json.dumps({
            "tool": "TOOL-GIT-01",
            "structural": "CONFIGURED",
            "runtime": "BLOCKED",
            "reason": str(exc),
        }))
        return 0

    version_proc = subprocess.run(
        [git_exe, "--version"],
        capture_output=True,
        text=True,
        timeout=15,
    )
    print(json.dumps({
        "tool": "TOOL-GIT-01",
        "structural": "CONFIGURED",
        "runtime": "AVAILABLE" if inside else "RESTRICTED",
        "git_executable": git_exe,
        "git_version": version_proc.stdout.strip(),
        "inside_work_tree": inside,
        "destructive_ops_normalized": False,
    }))
    return 0


if __name__ == "__main__":
    sys.exit(main())
