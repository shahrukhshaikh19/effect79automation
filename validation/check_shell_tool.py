#!/usr/bin/env python3
"""ACOS Phase D shell + filesystem tool health check."""

from __future__ import annotations

import json
import platform
import shutil
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


def main() -> int:
    shell_policy = REPO / "tools" / "shell" / "shell-policy.yaml"
    fs_policy = REPO / "tools" / "filesystem" / "filesystem-policy.yaml"
    missing = [
        str(p.relative_to(REPO))
        for p in (shell_policy, fs_policy)
        if not p.is_file()
    ]
    if missing:
        print(json.dumps({
            "tool": "TOOL-SHELL-01/TOOL-FS-01",
            "structural": "BLOCKED",
            "runtime": "BLOCKED",
            "missing": missing,
        }))
        return 1

    shell = shutil.which("powershell") or shutil.which("bash") or shutil.which("sh")
    runtime = "AVAILABLE" if shell else "BLOCKED"

    print(json.dumps({
        "tool": "TOOL-SHELL-01",
        "structural": "CONFIGURED",
        "runtime": runtime,
        "shell_executable": shell,
        "platform": platform.system(),
        "arbitrary_execution_default": False,
    }))
    print(json.dumps({
        "tool": "TOOL-FS-01",
        "structural": "CONFIGURED",
        "runtime": "AVAILABLE",
        "workspace_root": str(REPO),
        "evidence_output_root": "validation/evidence",
    }))
    return 0


if __name__ == "__main__":
    sys.exit(main())
