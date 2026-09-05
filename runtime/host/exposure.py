"""Ensure native skill discovery exists before a host session starts."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
SYNC = REPO / "tools" / "skill_exposure" / "sync_native_skills.py"
VALIDATE = REPO / "validation" / "validate_native_skill_exposure.py"


def ensure_native_skill_exposure() -> dict[str, Any]:
    if not SYNC.is_file():
        raise SystemExit("Missing tools/skill_exposure/sync_native_skills.py — cannot expose native skills")
    cmd = [sys.executable, str(SYNC)]
    parent = REPO.parent
    if parent != REPO:
        cmd.extend(["--extra-root", str(parent)])
    synced = subprocess.run(cmd, cwd=str(REPO), capture_output=True, text=True)
    if synced.returncode != 0:
        detail = (synced.stderr or synced.stdout or "").strip()
        raise SystemExit(
            "Native skill exposure sync failed. Host cannot discover routed skills.\n"
            f"{detail}\n"
            "Remediation: python tools/skill_exposure/sync_native_skills.py"
        )
    checked = subprocess.run([sys.executable, str(VALIDATE)], cwd=str(REPO), capture_output=True, text=True)
    if checked.returncode != 0:
        detail = (checked.stderr or checked.stdout or "").strip()
        raise SystemExit(
            "Native skill exposure is missing or stale after sync. Stopping before routing.\n"
            f"{detail}\n"
            "Remediation: python tools/skill_exposure/sync_native_skills.py"
        )
    return {"ok": True, "sync": "applied", "validated": True}
