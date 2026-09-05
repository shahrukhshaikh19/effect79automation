"""Host operational helpers: HTTP serve and browser evidence capture."""

from __future__ import annotations

import json
import socket
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

import yaml

from runtime.adapter.host_brief import HOST_DIR

REPO = Path(__file__).resolve().parents[2]
SERVE_PATH = HOST_DIR / "CURRENT_SERVE.json"
CAPTURE_SCRIPT = REPO / "tools" / "browser" / "scripts" / "capture-evidence.mjs"
DEFAULT_PORT = 8765


def implementation_dir(project_dir: Path) -> Path:
    impl = project_dir / "implementation"
    return impl if impl.is_dir() else project_dir


def _pid_alive(pid: int) -> bool:
    if pid <= 0:
        return False
    if sys.platform == "win32":
        import ctypes

        handle = ctypes.windll.kernel32.OpenProcess(0x1000, 0, pid)
        if handle:
            ctypes.windll.kernel32.CloseHandle(handle)
            return True
        return False
    import os

    try:
        os.kill(pid, 0)
    except OSError:
        return False
    return True


def _port_open(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.3)
        return sock.connect_ex(("127.0.0.1", port)) == 0


def serve_status() -> dict[str, Any] | None:
    if not SERVE_PATH.is_file():
        return None
    data = json.loads(SERVE_PATH.read_text(encoding="utf-8"))
    pid = int(data.get("pid") or 0)
    port = int(data.get("port") or 0)
    if pid and _pid_alive(pid) and port and _port_open(port):
        return data
    return None


def start_serve(project_dir: Path, port: int = DEFAULT_PORT) -> dict[str, Any]:
    existing = serve_status()
    if existing:
        return existing
    impl = implementation_dir(project_dir)
    if not impl.is_dir():
        raise FileNotFoundError(f"implementation directory missing: {impl}")
    if _port_open(port):
        data = {
            "pid": 0,
            "port": port,
            "url": f"http://127.0.0.1:{port}/",
            "directory": str(impl).replace("\\", "/"),
            "inherited": True,
        }
        SERVE_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")
        return data
    proc = subprocess.Popen(
        [sys.executable, "-m", "http.server", str(port), "--bind", "127.0.0.1", "--directory", str(impl)],
        cwd=str(impl),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    for _ in range(30):
        if _port_open(port):
            break
        time.sleep(0.1)
    else:
        proc.terminate()
        raise RuntimeError(f"HTTP server failed to bind 127.0.0.1:{port}")
    data = {
        "pid": proc.pid,
        "port": port,
        "url": f"http://127.0.0.1:{port}/",
        "directory": str(impl).replace("\\", "/"),
        "inherited": False,
    }
    SERVE_PATH.parent.mkdir(parents=True, exist_ok=True)
    SERVE_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return data


def write_default_capture_config(project_dir: Path, url: str) -> Path:
    path = project_dir / "evidence" / "capture-config.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.is_file():
        config = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        config["target"] = f"{url.rstrip('/')}/index.html"
        path.write_text(yaml.dump(config, sort_keys=False), encoding="utf-8")
        return path
    config = {
        "target": f"{url.rstrip('/')}/index.html",
        "readiness": {"wait_until": "networkidle", "timeout_ms": 45000, "animation_settle_ms": 800},
        "reduced_motion": False,
        "viewports": [
            {"name": "desktop-1440", "width": 1440, "height": 900, "device_scale_factor": 1},
            {"name": "laptop-1280", "width": 1280, "height": 800, "device_scale_factor": 1},
            {"name": "tablet-768", "width": 768, "height": 1024, "device_scale_factor": 1},
            {"name": "mobile-390", "width": 390, "height": 844, "device_scale_factor": 1},
        ],
        "capture": {"full_page": False, "types": ["viewport"]},
    }
    path.write_text(yaml.dump(config, sort_keys=False), encoding="utf-8")
    return path


def run_capture(project_dir: Path, port: int = DEFAULT_PORT) -> dict[str, Any]:
    served = start_serve(project_dir, port=port)
    config = write_default_capture_config(project_dir, served["url"])
    output = project_dir / "evidence" / "viewports"
    output.mkdir(parents=True, exist_ok=True)
    if not CAPTURE_SCRIPT.is_file():
        raise FileNotFoundError(f"missing capture script: {CAPTURE_SCRIPT}")
    result = subprocess.run(
        ["node", str(CAPTURE_SCRIPT), "--config", str(config), "--output", str(output)],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        check=False,
    )
    extra: dict[str, Any] = {"viewport_capture_exit": result.returncode}
    if result.stdout:
        extra["viewport_stdout"] = result.stdout.strip()[-2000:]
    if result.returncode != 0:
        extra["viewport_stderr"] = (result.stderr or "").strip()[-2000:]
        raise RuntimeError(extra.get("viewport_stderr") or "capture-evidence failed")

    states = project_dir / "evidence" / "capture-states.mjs"
    if states.is_file():
        state_run = subprocess.run(
            ["node", str(states)],
            cwd=str(REPO),
            capture_output=True,
            text=True,
            check=False,
        )
        extra["state_capture_exit"] = state_run.returncode
        extra["state_stdout"] = (state_run.stdout or "").strip()[-1000:]
        if state_run.returncode != 0:
            extra["state_stderr"] = (state_run.stderr or "").strip()[-1000:]
    extra["url"] = served["url"]
    extra["config"] = str(config).replace("\\", "/")
    extra["output"] = str(output).replace("\\", "/")
    return extra
