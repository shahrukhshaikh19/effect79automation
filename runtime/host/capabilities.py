"""Truthful runtime capability probes. Do not hardcode Blender as RESTRICTED."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from runtime.adapter.host_brief import HOST_DIR

_WIN_BLENDER_ROOTS = (
    Path(r"C:\Program Files\Blender Foundation"),
    Path(r"C:\Program Files (x86)\Blender Foundation"),
)
MCP_STAMP = HOST_DIR / "BLENDER_MCP.json"
USER_WAIT_MESSAGE = (
    "Blender MCP/app band hai. Main skip nahi karunga. "
    "Blender kholo, MCP connect karo. Connect hone ke baad confirm karo — tabhi start hoga."
)


def blender_binary_available() -> bool:
    override = (os.environ.get("ACOS_BLENDER_CAPABILITY") or "").strip().upper()
    if override == "UNAVAILABLE":
        return False
    explicit = os.environ.get("ACOS_BLENDER_BIN") or os.environ.get("BLENDER_BIN")
    if explicit and Path(explicit).is_file():
        return True
    if shutil.which("blender"):
        return True
    if os.name == "nt":
        for root in _WIN_BLENDER_ROOTS:
            if not root.is_dir():
                continue
            if any(root.glob("Blender */blender.exe")) or (root / "blender.exe").is_file():
                return True
    return False


def blender_app_running() -> bool:
    try:
        if os.name == "nt":
            result = subprocess.run(
                ["tasklist", "/FI", "IMAGENAME eq blender.exe"],
                capture_output=True,
                text=True,
                check=False,
            )
            return "blender.exe" in (result.stdout or "").lower()
        result = subprocess.run(["pgrep", "-x", "blender"], capture_output=True, check=False)
        return result.returncode == 0
    except OSError:
        return False


def load_mcp_stamp() -> dict[str, Any]:
    if not MCP_STAMP.is_file():
        return {"connected": False}
    try:
        data = json.loads(MCP_STAMP.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"connected": False}
    return data if isinstance(data, dict) else {"connected": False}


def write_mcp_stamp(*, connected: bool, addon_ok: bool = False, source: str = "confirm-blender") -> dict[str, Any]:
    data = {
        "connected": connected,
        "addon_ok": addon_ok,
        "source": source,
        "checked_at": datetime.now(timezone.utc).isoformat(),
    }
    MCP_STAMP.parent.mkdir(parents=True, exist_ok=True)
    MCP_STAMP.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return data


def blender_readiness() -> dict[str, Any]:
    override = (os.environ.get("ACOS_BLENDER_CAPABILITY") or "").strip().upper()
    stamp = load_mcp_stamp()
    app = blender_app_running()
    binary = blender_binary_available()
    mcp = bool(stamp.get("connected"))
    if override == "AVAILABLE":
        ready = True
    elif override in {"UNAVAILABLE", "BLOCKED", "RESTRICTED"}:
        ready = False
    else:
        ready = mcp and (app or bool(stamp.get("addon_ok")))
    return {
        "binary_installed": binary,
        "app_running": app,
        "mcp_connected": mcp,
        "addon_ok": bool(stamp.get("addon_ok")),
        "ready": ready,
        "message": None if ready else USER_WAIT_MESSAGE,
    }


def probe_blender() -> str:
    return "AVAILABLE" if blender_readiness()["ready"] else "UNAVAILABLE"


def host_capabilities() -> dict[str, str]:
    return {
        "browser": "AVAILABLE",
        "blender": probe_blender(),
        "git": "AVAILABLE",
        "shell": "AVAILABLE",
        "filesystem": "AVAILABLE",
    }
