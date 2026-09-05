"""Browser evidence capture for BM-001 — wraps certified capture-evidence.mjs."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

import yaml

from validation.benchmark_execution.artifact_analysis import (
    analyze_implementation,
    build_responsive_behavior_check,
    build_visual_consistency_review,
)

REPO = Path(__file__).resolve().parents[2]
BROWSER_ROOT = REPO / "tools" / "browser"
CAPTURE_SCRIPT = BROWSER_ROOT / "scripts" / "capture-evidence.mjs"
INTERACTION_SCRIPT = BROWSER_ROOT / "scripts" / "capture-interaction.mjs"
EVIDENCE_ROOT = REPO / "benchmarks" / "BM-001" / "execution" / "evidence"
IMPL_DIR = REPO / "benchmarks" / "BM-001" / "execution" / "implementation"


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


def _extract_console_and_network(manifest: dict[str, Any]) -> tuple[list[Any], list[Any]]:
    console_log: list[Any] = []
    network_failures: list[Any] = []
    for capture in manifest.get("captures") or []:
        network_failures.extend(capture.get("network_failures") or [])
    console_path = manifest.get("console_log_json")
    if console_path:
        full = EVIDENCE_ROOT / "E-001" / console_path if not Path(console_path).is_absolute() else Path(console_path)
        if full.is_file():
            console_log = json.loads(full.read_text(encoding="utf-8"))
    return console_log, network_failures


def produce_derived_evidence(
    *,
    viewport_result: dict[str, Any],
    reduced_result: dict[str, Any],
    interaction_result: dict[str, Any],
    analysis: dict[str, Any],
) -> dict[str, Any]:
    """Generate E-003, E-004, E-005, E-006 artifacts from captures + analysis."""
    bundle: dict[str, Any] = {}

    manifest = viewport_result.get("manifest") or {}
    captures = manifest.get("captures") or []
    viewports = sorted({c.get("viewport", {}).get("name") for c in captures if c.get("viewport")})
    runtime_healthy = bool(manifest.get("runtime_healthy"))
    console_errors = sum(len(c.get("console_errors") or []) for c in captures)
    network_failures: list[str] = []
    for c in captures:
        network_failures.extend(c.get("network_failures") or [])

    console_log, _ = _extract_console_and_network(manifest)

    e005_dir = EVIDENCE_ROOT / "E-005"
    e005_dir.mkdir(parents=True, exist_ok=True)
    (e005_dir / "console_log.json").write_text(json.dumps(console_log, indent=2), encoding="utf-8")

    e009_dir = EVIDENCE_ROOT / "E-009"
    e009_dir.mkdir(parents=True, exist_ok=True)
    perf = interaction_result.get("performance") or {}
    (e009_dir / "performance_metrics.json").write_text(json.dumps(perf, indent=2), encoding="utf-8")

    e003_dir = EVIDENCE_ROOT / "E-003"
    e003_dir.mkdir(parents=True, exist_ok=True)
    visual = build_visual_consistency_review(analysis, evidence_refs=["evidence/E-001/manifest.yaml"])
    (e003_dir / "visual_consistency_review.json").write_text(json.dumps(visual, indent=2), encoding="utf-8")
    bundle["E-003"] = visual

    e004_dir = EVIDENCE_ROOT / "E-004"
    e004_dir.mkdir(parents=True, exist_ok=True)
    responsive = build_responsive_behavior_check(
        viewports_captured=viewports,
        analysis=analysis,
        evidence_refs=["evidence/E-001/manifest.yaml"],
    )
    (e004_dir / "responsive_behavior_check.json").write_text(json.dumps(responsive, indent=2), encoding="utf-8")
    bundle["E-004"] = responsive

    e006_dir = EVIDENCE_ROOT / "E-006"
    e006_dir.mkdir(parents=True, exist_ok=True)
    network_log = {
        "network_failures": network_failures,
        "failure_count": len(network_failures),
        "source": "evidence/E-001/manifest.yaml",
    }
    (e006_dir / "network_request_log.json").write_text(json.dumps(network_log, indent=2), encoding="utf-8")
    bundle["E-006"] = network_log

    e002_dir = EVIDENCE_ROOT / "E-002"
    e002_dir.mkdir(parents=True, exist_ok=True)
    impl_files = [p.name for p in IMPL_DIR.iterdir() if p.is_file()] if IMPL_DIR.is_dir() else []
    impl_check = {
        "functional": bool(impl_files) and "index.html" in impl_files,
        "files": impl_files,
        "interactive_js": "main.js" in impl_files,
        "styles": "styles.css" in impl_files,
    }
    (e002_dir / "implementation_check.json").write_text(json.dumps(impl_check, indent=2), encoding="utf-8")
    bundle["E-002"] = impl_check

    reduced_manifest = reduced_result.get("manifest") or {}
    reduced_captures = reduced_manifest.get("captures") or []
    reduced_errors = sum(len(c.get("console_errors") or []) for c in reduced_captures)
    bundle["E-008_meta"] = {"console_errors_during_capture": reduced_errors}

    bundle["E-009"] = perf
    bundle["E-007"] = interaction_result.get("interaction") or {}
    bundle["runtime_healthy"] = runtime_healthy
    bundle["console_error_count"] = console_errors
    bundle["network_failure_count"] = len(network_failures)
    bundle["viewports_captured"] = viewports

    return bundle
