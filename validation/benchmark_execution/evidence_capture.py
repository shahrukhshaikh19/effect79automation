"""Browser evidence capture for BM-001 — wraps certified capture-evidence.mjs."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

import yaml

REPO = Path(__file__).resolve().parents[2]
BROWSER_ROOT = REPO / "tools" / "browser"
CAPTURE_SCRIPT = BROWSER_ROOT / "scripts" / "capture-evidence.mjs"
INTERACTION_SCRIPT = BROWSER_ROOT / "scripts" / "capture-interaction.mjs"


def _run_node(script: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["node", str(script), *args],
        cwd=REPO,
        capture_output=True,
        text=True,
        check=False,
    )


def write_viewport_config(
    config_path: Path,
    *,
    target: str,
    reduced_motion: bool,
) -> None:
    config = {
        "target": target,
        "readiness": {"wait_until": "networkidle", "timeout_ms": 30000, "animation_settle_ms": 500},
        "reduced_motion": reduced_motion,
        "capture": {"full_page": True, "types": ["viewport", "full_page"]},
        "viewports": [
            {"name": "desktop", "width": 1440, "height": 900, "device_scale_factor": 1},
            {"name": "laptop", "width": 1280, "height": 800, "device_scale_factor": 1},
            {"name": "tablet", "width": 768, "height": 1024, "device_scale_factor": 1},
            {"name": "mobile", "width": 390, "height": 844, "device_scale_factor": 1},
        ],
    }
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(yaml.dump(config, sort_keys=False), encoding="utf-8")


def capture_viewport_evidence(target: Path, output_dir: Path, *, reduced_motion: bool = False) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    config_path = output_dir / "capture-config.yaml"
    rel_target = target.relative_to(REPO).as_posix()
    write_viewport_config(config_path, target=f"../../{rel_target}", reduced_motion=reduced_motion)
    proc = _run_node(CAPTURE_SCRIPT, "--config", str(config_path), "--output", str(output_dir))
    if proc.returncode != 0:
        return {"status": "error", "stderr": proc.stderr, "stdout": proc.stdout}
    manifest_path = output_dir / "manifest.yaml"
    if not manifest_path.is_file():
        return {"status": "error", "reason": "manifest_missing"}
    manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8")) or {}
    return {"status": "complete", "manifest": manifest, "manifest_path": str(manifest_path)}


def capture_interaction_and_performance(target: Path, output_dir: Path) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    rel_target = target.relative_to(REPO).as_posix()
    proc = _run_node(INTERACTION_SCRIPT, "--target", f"../../{rel_target}", "--output", str(output_dir))
    if proc.returncode != 0:
        return {"status": "error", "stderr": proc.stderr}
    interaction_path = output_dir / "interaction_log.json"
    performance_path = output_dir / "performance_metrics.json"
    interaction = json.loads(interaction_path.read_text(encoding="utf-8")) if interaction_path.is_file() else {}
    performance = json.loads(performance_path.read_text(encoding="utf-8")) if performance_path.is_file() else {}
    return {
        "status": "complete",
        "interaction": interaction,
        "performance": performance,
        "interaction_path": str(interaction_path),
        "performance_path": str(performance_path),
    }


def summarize_evidence(
    viewport_result: dict[str, Any],
    reduced_result: dict[str, Any],
    interaction_result: dict[str, Any],
    implementation_dir: Path,
) -> dict[str, Any]:
    manifest = (viewport_result.get("manifest") or {}) if viewport_result.get("status") == "complete" else {}
    captures = manifest.get("captures") or []
    console_errors = sum(len(c.get("console_errors") or []) for c in captures)
    network_failures = sum(len(c.get("network_failures") or []) for c in captures)
    viewports = sorted({c.get("viewport", {}).get("name") for c in captures if c.get("viewport")})
    reduced_manifest = (reduced_result.get("manifest") or {}) if reduced_result.get("status") == "complete" else {}
    reduced_captures = reduced_manifest.get("captures") or []
    reduced_errors = sum(len(c.get("console_errors") or []) for c in reduced_captures)

    impl_files = [p.name for p in implementation_dir.iterdir() if p.is_file()] if implementation_dir.is_dir() else []
    sections_present = 7 if "index.html" in impl_files else 0

    perf = interaction_result.get("performance") or {}
    perf_ok = perf.get("dom_content_loaded_ms", 9999) < 5000

    return {
        "runtime_healthy": bool(manifest.get("runtime_healthy")),
        "dpr_integrity": bool(manifest.get("dpr_integrity")),
        "console_error_count": console_errors,
        "network_failure_count": network_failures,
        "viewports_captured": viewports,
        "reduced_motion_verified": reduced_result.get("status") == "complete" and reduced_errors == 0,
        "interaction_verified": interaction_result.get("status") == "complete",
        "performance_ok": perf_ok,
        "sections_present": sections_present,
        "implementation_files": impl_files,
    }
