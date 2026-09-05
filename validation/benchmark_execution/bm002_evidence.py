"""Browser evidence capture for BM-002 — E-001..E-014 derived artifacts."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

import yaml

from validation.benchmark_execution.bm002_analysis import (
    analyze_implementation,
    build_3d_quality_review,
    build_camera_progression_log,
    build_responsive_3d_composition_check,
    build_responsive_review_bm002,
    build_scene_state_captures,
    build_visual_review_bm002,
)
from validation.benchmark_execution.evidence_capture import (
    capture_viewport_evidence,
    write_viewport_config,
)

REPO = Path(__file__).resolve().parents[2]
BROWSER_ROOT = REPO / "tools" / "browser"
INTERACTION_SCRIPT = BROWSER_ROOT / "scripts" / "capture-interaction.mjs"
BM002_ROOT = REPO / "benchmarks" / "BM-002"
EVIDENCE_ROOT = BM002_ROOT / "execution" / "evidence"
IMPL_DIR = BM002_ROOT / "execution" / "implementation"


def _run_node(script: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["node", str(script), *args],
        cwd=REPO,
        capture_output=True,
        text=True,
        check=False,
    )


def capture_interaction_and_performance(target: Path, output_dir: Path) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    rel_target = target.relative_to(REPO).as_posix()
    proc = _run_node(
        INTERACTION_SCRIPT,
        "--target",
        f"../../{rel_target}",
        "--output",
        str(output_dir),
        "--mode",
        "bm002",
    )
    if proc.returncode != 0:
        return {"status": "error", "stderr": proc.stderr}
    interaction_path = output_dir / "interaction_log.json"
    performance_path = output_dir / "performance_metrics.json"
    scene_path = output_dir / "scene_progression.json"
    interaction = json.loads(interaction_path.read_text(encoding="utf-8")) if interaction_path.is_file() else {}
    performance = json.loads(performance_path.read_text(encoding="utf-8")) if performance_path.is_file() else {}
    scene_log = json.loads(scene_path.read_text(encoding="utf-8")) if scene_path.is_file() else {}
    return {
        "status": "complete",
        "interaction": interaction,
        "performance": performance,
        "scene_log": scene_log,
        "interaction_path": str(interaction_path),
        "performance_path": str(performance_path),
        "scene_path": str(scene_path),
    }


def produce_derived_evidence(
    *,
    viewport_result: dict[str, Any],
    reduced_result: dict[str, Any],
    interaction_result: dict[str, Any],
    analysis: dict[str, Any],
) -> dict[str, Any]:
    bundle: dict[str, Any] = {}
    manifest = viewport_result.get("manifest") or {}
    captures = manifest.get("captures") or []
    viewports = sorted({c.get("viewport", {}).get("name") for c in captures if c.get("viewport")})
    runtime_healthy = bool(manifest.get("runtime_healthy"))
    console_errors = sum(len(c.get("console_errors") or []) for c in captures)
    network_failures: list[str] = []
    for c in captures:
        network_failures.extend(c.get("network_failures") or [])

    console_log: list[Any] = []
    console_path = EVIDENCE_ROOT / "E-001" / "console_log.json"
    if console_path.is_file():
        console_log = json.loads(console_path.read_text(encoding="utf-8"))

    e005_dir = EVIDENCE_ROOT / "E-005"
    e005_dir.mkdir(parents=True, exist_ok=True)
    (e005_dir / "console_log.json").write_text(json.dumps(console_log, indent=2), encoding="utf-8")

    e009_dir = EVIDENCE_ROOT / "E-009"
    e009_dir.mkdir(parents=True, exist_ok=True)
    perf = interaction_result.get("performance") or {}
    (e009_dir / "performance_metrics.json").write_text(json.dumps(perf, indent=2), encoding="utf-8")

    e003_dir = EVIDENCE_ROOT / "E-003"
    e003_dir.mkdir(parents=True, exist_ok=True)
    visual = build_visual_review_bm002(analysis, evidence_refs=["evidence/E-001/manifest.yaml"])
    (e003_dir / "visual_consistency_review.json").write_text(json.dumps(visual, indent=2), encoding="utf-8")
    bundle["E-003"] = visual

    e004_dir = EVIDENCE_ROOT / "E-004"
    e004_dir.mkdir(parents=True, exist_ok=True)
    responsive = build_responsive_review_bm002(
        viewports_captured=viewports,
        analysis=analysis,
        evidence_refs=["evidence/E-001/manifest.yaml"],
    )
    (e004_dir / "responsive_behavior_check.json").write_text(json.dumps(responsive, indent=2), encoding="utf-8")
    bundle["E-004"] = responsive

    e006_dir = EVIDENCE_ROOT / "E-006"
    e006_dir.mkdir(parents=True, exist_ok=True)
    network_log = {"network_failures": network_failures, "failure_count": len(network_failures), "source": "evidence/E-001/manifest.yaml"}
    (e006_dir / "network_request_log.json").write_text(json.dumps(network_log, indent=2), encoding="utf-8")
    bundle["E-006"] = network_log

    e002_dir = EVIDENCE_ROOT / "E-002"
    e002_dir.mkdir(parents=True, exist_ok=True)
    impl_files = [p.name for p in IMPL_DIR.iterdir() if p.is_file()] if IMPL_DIR.is_dir() else []
    impl_check = {
        "functional": bool(impl_files) and "index.html" in impl_files,
        "real_time_webgl_three_d_scene_present": analysis.get("three_js") and analysis.get("webgl_canvas"),
        "not_static_render_embedded_only": not analysis.get("model_viewer"),
        "not_model_viewer_only": not analysis.get("model_viewer"),
        "files": impl_files,
        "interactive_js": "main.js" in impl_files,
    }
    (e002_dir / "implementation_check.json").write_text(json.dumps(impl_check, indent=2), encoding="utf-8")
    bundle["E-002"] = impl_check

    scene_log = interaction_result.get("scene_log") or {}

    e011_dir = EVIDENCE_ROOT / "E-011"
    e011_dir.mkdir(parents=True, exist_ok=True)
    review_3d = build_3d_quality_review(analysis, evidence_refs=["evidence/E-002/implementation_check.json", "evidence/E-001/manifest.yaml"])
    (e011_dir / "3d_quality_review.json").write_text(json.dumps(review_3d, indent=2), encoding="utf-8")
    bundle["E-011"] = review_3d

    e012_dir = EVIDENCE_ROOT / "E-012"
    e012_dir.mkdir(parents=True, exist_ok=True)
    scene_states = build_scene_state_captures(scene_log=scene_log, evidence_refs=["evidence/E-007/interaction_log.json"])
    (e012_dir / "scene_state_captures.json").write_text(json.dumps(scene_states, indent=2), encoding="utf-8")
    bundle["E-012"] = scene_states

    e013_dir = EVIDENCE_ROOT / "E-013"
    e013_dir.mkdir(parents=True, exist_ok=True)
    camera_log = build_camera_progression_log(scene_log=scene_log, evidence_refs=["evidence/E-007/interaction_log.json"])
    (e013_dir / "camera_scene_progression_log.json").write_text(json.dumps(camera_log, indent=2), encoding="utf-8")
    bundle["E-013"] = camera_log

    e014_dir = EVIDENCE_ROOT / "E-014"
    e014_dir.mkdir(parents=True, exist_ok=True)
    r3d = build_responsive_3d_composition_check(
        viewports_captured=viewports,
        analysis=analysis,
        scene_log=scene_log,
        evidence_refs=["evidence/E-001/manifest.yaml"],
    )
    (e014_dir / "responsive_3d_composition_check.json").write_text(json.dumps(r3d, indent=2), encoding="utf-8")
    bundle["E-014"] = r3d

    reduced_manifest = reduced_result.get("manifest") or {}
    reduced_captures = reduced_manifest.get("captures") or []
    reduced_errors = sum(len(c.get("console_errors") or []) for c in reduced_captures)
    bundle["E-008_meta"] = {"console_errors_during_capture": reduced_errors}
    bundle["E-009"] = perf
    bundle["E-007"] = interaction_result.get("interaction") or {}
    bundle["scene_log"] = scene_log
    bundle["runtime_healthy"] = runtime_healthy
    bundle["console_error_count"] = console_errors
    bundle["network_failure_count"] = len(network_failures)
    bundle["viewports_captured"] = viewports
    return bundle
