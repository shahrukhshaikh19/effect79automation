#!/usr/bin/env python3
"""ACOS Phase D Blender MCP tool health check."""

from __future__ import annotations

import json
import re
import shutil
import socket
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
DEFAULT_MCP_HOST = "localhost"
DEFAULT_MCP_PORT = 9876

WINDOWS_BLENDER_GLOBS = [
    Path(r"C:\Program Files\Blender Foundation"),
    Path(r"C:\Program Files (x86)\Blender Foundation"),
]


def discover_blender_executable() -> str | None:
    found = shutil.which("blender")
    if found:
        return found
    if sys.platform != "win32":
        return None
    for base in WINDOWS_BLENDER_GLOBS:
        if not base.is_dir():
            continue
        for exe in sorted(base.glob("*/blender.exe"), reverse=True):
            if exe.is_file():
                return str(exe)
    return None


def blender_version_text(exe: str) -> str | None:
    try:
        proc = subprocess.run(
            [exe, "--version"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if proc.returncode == 0 and proc.stdout:
            return proc.stdout.splitlines()[0]
    except (OSError, subprocess.TimeoutExpired):
        return None
    return None


def tcp_socket_probe(host: str, port: int) -> bool:
    try:
        with socket.create_connection((host, port), timeout=2.0):
            return True
    except OSError:
        return False


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

    blender_exe = discover_blender_executable()
    blender_version = blender_version_text(blender_exe) if blender_exe else None
    tcp_reachable = tcp_socket_probe(DEFAULT_MCP_HOST, DEFAULT_MCP_PORT)
    on_path = shutil.which("blender") is not None

    if blender_exe and tcp_reachable:
        runtime = "RESTRICTED"
        runtime_reason = (
            "Blender executable found; TCP socket reachable on "
            f"{DEFAULT_MCP_HOST}:{DEFAULT_MCP_PORT} — MCP protocol handshake not verified by this script"
        )
    elif blender_exe:
        runtime = "RESTRICTED"
        runtime_reason = (
            "Blender executable found but MCP TCP socket not reachable — "
            "start MCP Server in Blender (addon must be enabled)"
        )
    else:
        runtime = "BLOCKED"
        runtime_reason = "Blender executable not found on PATH or standard install locations"

    print(json.dumps({
        "tool": "TOOL-BLENDER-01",
        "structural": "CONFIGURED",
        "runtime": runtime,
        "upstream_commit": sha,
        "upstream_version": upstream.get("upstream", {}).get("package_version"),
        "security_review_status": review_status,
        "blender_executable": blender_exe,
        "blender_on_path": on_path,
        "blender_version": blender_version,
        "tcp_socket_probe_attempted": True,
        "tcp_socket_reachable": tcp_reachable,
        "host": DEFAULT_MCP_HOST,
        "port": DEFAULT_MCP_PORT,
        "protocol_handshake_attempted": False,
        "protocol_handshake_verified": False,
        "addon_runtime_verified": False,
        "reason": runtime_reason,
        "notes": "TCP reachability is not MCP protocol verification; use live MCP client for handshake evidence",
    }))
    return 0


if __name__ == "__main__":
    if yaml is None:
        print("PyYAML required", file=sys.stderr)
        sys.exit(1)
    sys.exit(main())
