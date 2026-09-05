"""Derive and validate required evidence from frozen benchmark EVIDENCE_PLAN.yaml."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

REPO = Path(__file__).resolve().parents[2]

DEFAULT_BENCHMARK_ID = "BM-001"


def _benchmark_root(benchmark_id: str) -> Path:
    return REPO / "benchmarks" / benchmark_id


def load_evidence_plan(*, benchmark_id: str = DEFAULT_BENCHMARK_ID) -> list[dict[str, Any]]:
    plan_path = _benchmark_root(benchmark_id) / "EVIDENCE_PLAN.yaml"
    data = yaml.safe_load(plan_path.read_text(encoding="utf-8"))
    plan = data.get("evidence_plan") if isinstance(data, dict) else data
    if not isinstance(plan, list):
        raise ValueError(f"Invalid EVIDENCE_PLAN.yaml structure for {benchmark_id}")
    return plan


def required_evidence_ids(*, benchmark_id: str = DEFAULT_BENCHMARK_ID, meaningful_3d_used: bool) -> list[str]:
    required: list[str] = []
    for item in load_evidence_plan(benchmark_id=benchmark_id):
        eid = str(item.get("evidence_id", ""))
        if not eid:
            continue
        if item.get("required") is True:
            required.append(eid)
            continue
        if item.get("required") == "conditional":
            if meaningful_3d_used and item.get("required_when") == "meaningful_3d_used_in_deliverable":
                required.append(eid)
            elif not meaningful_3d_used and item.get("not_required_when") == "no_meaningful_3d_in_deliverable":
                continue
    return sorted(set(required))


def _artifact_paths(evidence_id: str, *, benchmark_id: str) -> list[Path]:
    base = _benchmark_root(benchmark_id) / "execution" / "evidence" / evidence_id
    mapping: dict[str, list[str]] = {
        "E-001": ["manifest.yaml"],
        "E-002": ["implementation_check.json"],
        "E-003": ["visual_consistency_review.json"],
        "E-004": ["responsive_behavior_check.json"],
        "E-005": ["console_log.json"],
        "E-006": ["network_request_log.json"],
        "E-007": ["interaction_log.json"],
        "E-008": ["manifest.yaml"],
        "E-009": ["performance_metrics.json"],
        "E-010": [],
        "E-011": ["3d_quality_review.json"],
        "E-012": ["scene_state_captures.json"],
        "E-013": ["camera_scene_progression_log.json"],
        "E-014": ["responsive_3d_composition_check.json"],
        "E-015": [],
    }
    names = mapping.get(evidence_id, [])
    paths = [base / name for name in names]
    if evidence_id == "E-001":
        for vp in ("desktop", "laptop", "tablet", "mobile"):
            paths.append(base / vp / "viewport.png")
    return paths


def validate_evidence_artifact(evidence_id: str, path: Path) -> list[str]:
    errors: list[str] = []
    if not path.is_file():
        return [f"{evidence_id}: missing artifact {path.name}"]
    if path.stat().st_size == 0:
        return [f"{evidence_id}: empty artifact {path.name}"]
    if path.suffix in (".json",):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return [f"{evidence_id}: invalid JSON in {path.name}"]
        if payload is None:
            errors.append(f"{evidence_id}: empty JSON payload in {path.name}")
        elif payload == {}:
            errors.append(f"{evidence_id}: empty JSON object in {path.name}")
    if path.suffix in (".yaml", ".yml"):
        try:
            payload = yaml.safe_load(path.read_text(encoding="utf-8"))
        except yaml.YAMLError:
            return [f"{evidence_id}: invalid YAML in {path.name}"]
        if not payload:
            errors.append(f"{evidence_id}: empty YAML payload in {path.name}")
    if path.suffix == ".png" and path.stat().st_size < 1000:
        errors.append(f"{evidence_id}: suspiciously small screenshot {path.name}")
    return errors


def validate_required_evidence(
    *,
    benchmark_id: str = DEFAULT_BENCHMARK_ID,
    meaningful_3d_used: bool,
    evidence_records: dict[str, str],
    gate_report_path: Path | None = None,
    design_gate_path: Path | None = None,
) -> dict[str, Any]:
    """Return completeness report; missing/invalid → blocked."""
    required = required_evidence_ids(benchmark_id=benchmark_id, meaningful_3d_used=meaningful_3d_used)
    missing: list[str] = []
    invalid: list[str] = []
    validated: list[str] = []

    for eid in required:
        if eid == "E-010":
            if gate_report_path and gate_report_path.is_file() and gate_report_path.stat().st_size > 0:
                validated.append(eid)
            else:
                missing.append(eid)
            continue
        if eid == "E-015":
            if design_gate_path and design_gate_path.is_file() and design_gate_path.stat().st_size > 0:
                validated.append(eid)
            else:
                missing.append(eid)
            continue
        if eid not in evidence_records:
            missing.append(eid)
            continue
        artifact_errors: list[str] = []
        paths = _artifact_paths(eid, benchmark_id=benchmark_id)
        existing = [p for p in paths if p.is_file()]
        if not existing and paths:
            missing.append(eid)
            continue
        for path in existing:
            artifact_errors.extend(validate_evidence_artifact(eid, path))
        if artifact_errors:
            invalid.extend(artifact_errors)
        else:
            validated.append(eid)

    sufficient = not missing and not invalid
    return {
        "required_evidence_ids": required,
        "validated": validated,
        "missing": missing,
        "invalid": invalid,
        "sufficient": sufficient,
        "status": "SUFFICIENT" if sufficient else "BLOCKED_INSUFFICIENT_EVIDENCE",
    }
