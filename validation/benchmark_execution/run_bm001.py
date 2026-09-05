#!/usr/bin/env python3
"""BM-001 v1.1 benchmark execution through certified ACOS workflow."""

from __future__ import annotations

import json
import shutil
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from runtime.evidence.register import register_evidence
from runtime.intake.validate import validate_intake
from runtime.quality.gate import validate_producer_independence
from runtime.routing.engine import route_task, validate_routing_decision
from runtime.state.execution import append_event, create_execution_state, persist_state
from runtime.state.transitions import (
    bind_routing_to_execution,
    can_transition,
    set_design_gate_state,
    unlock_planned_skills,
)
from validation.benchmark_execution.artifact_analysis import analyze_implementation
from validation.benchmark_execution.critics import evaluate_critics
from validation.benchmark_execution.direction import evaluate_design_gate, write_direction_artifacts
from validation.benchmark_execution.evidence_capture import (
    capture_interaction_and_performance,
    capture_viewport_evidence,
    produce_derived_evidence,
)
from validation.benchmark_execution.evidence_contract import (
    load_evidence_plan,
    required_evidence_ids,
    validate_required_evidence,
)
from validation.benchmark_execution.gate_evaluation import (
    build_gate_report,
    determine_gate_status,
    evaluate_quality_gate,
)
from validation.benchmark_execution.intake import build_intake_from_registration
from validation.benchmark_execution.scoring import score_benchmark

BM_ROOT = REPO / "benchmarks" / "BM-001"
EXEC_ROOT = BM_ROOT / "execution"
IMPL_DIR = EXEC_ROOT / "implementation"
DIRECTION_DIR = EXEC_ROOT / "direction"
EVIDENCE_DIR = EXEC_ROOT / "evidence"
RUN_DIR = EXEC_ROOT / "run"
RUNS_ARCHIVE = EXEC_ROOT / "runs"
FROZEN_CONTRACT_HASH = "b2cb2dbaea31e07331fe1c94df1271e3c167f9a64461e2dc25410d13696cadf3"
INVALIDATED_RUN_ID = "bm001-run-4bd803dd4125"


def load_registration() -> dict[str, Any]:
    reg_path = BM_ROOT / "REGISTRATION.yaml"
    data = yaml.safe_load(reg_path.read_text(encoding="utf-8"))
    if data.get("benchmark_contract_sha256") != FROZEN_CONTRACT_HASH:
        raise RuntimeError("Frozen contract hash mismatch — STOP")
    return data


def verify_implementation() -> list[str]:
    required = ["index.html", "styles.css", "main.js"]
    return [f for f in required if not (IMPL_DIR / f).is_file()]


def archive_historical_run_if_needed() -> None:
    report = RUN_DIR / "EXECUTION_REPORT.yaml"
    if not report.is_file():
        return
    data = yaml.safe_load(report.read_text(encoding="utf-8")) or {}
    run_id = data.get("run_id", "unknown-run")
    if run_id != INVALIDATED_RUN_ID:
        return
    dest = RUNS_ARCHIVE / run_id
    if dest.exists():
        return
    dest.mkdir(parents=True, exist_ok=True)
    for item in RUN_DIR.iterdir():
        if item.is_file():
            shutil.copy2(item, dest / item.name)
    invalidation = {
        "run_id": run_id,
        "original_result": data.get("benchmark_result"),
        "original_score": data.get("benchmark_score"),
        "original_gate": data.get("quality_gate_result"),
        "invalidated_at": datetime.now(timezone.utc).isoformat(),
        "invalidation_reason": "certification_correction_insufficient_evaluation",
        "details": (
            "Prior PASS/85.5/APPROVED used proxy critics, incomplete evidence contract "
            "(missing E-003/E-004/E-006), and hard-coded HR-01..HR-10=false."
        ),
        "preserved_artifacts": [str(p.relative_to(REPO)) for p in dest.iterdir()],
    }
    (dest / "INVALIDATION_RECORD.yaml").write_text(yaml.dump(invalidation, sort_keys=False), encoding="utf-8")


def _register_evidence_records(evidence_bundle: dict[str, Any]) -> list[dict[str, Any]]:
    mapping = {
        "E-001": (EVIDENCE_DIR / "E-001" / "manifest.yaml", "browser_screenshot"),
        "E-002": (EVIDENCE_DIR / "E-002" / "implementation_check.json", "implementation_completion_check"),
        "E-003": (EVIDENCE_DIR / "E-003" / "visual_consistency_review.json", "visual_consistency_review"),
        "E-004": (EVIDENCE_DIR / "E-004" / "responsive_behavior_check.json", "responsive_behavior_check"),
        "E-005": (EVIDENCE_DIR / "E-005" / "console_log.json", "browser_console_log"),
        "E-006": (EVIDENCE_DIR / "E-006" / "network_request_log.json", "network_request_log"),
        "E-007": (EVIDENCE_DIR / "E-007" / "interaction_log.json", "interaction_recording"),
        "E-008": (EVIDENCE_DIR / "E-008" / "manifest.yaml", "reduced_motion_behavior_check"),
        "E-009": (EVIDENCE_DIR / "E-009" / "performance_metrics.json", "performance_metrics"),
    }
    records: list[dict[str, Any]] = []
    for eid, (path, etype) in mapping.items():
        if path.is_file() and path.stat().st_size > 0:
            records.append(
                register_evidence(
                    evidence_id=eid,
                    evidence_type=etype,
                    producer="benchmark_execution_runner",
                    artifact_ref=str(path),
                    source="validation/benchmark_execution/run_bm001.py",
                    integrity_verified=True,
                )
            )
    return records


def run_execution(*, skip_browser: bool = False, re_evaluate_only: bool = False) -> dict[str, Any]:
    archive_historical_run_if_needed()

    run_id = f"bm001-run-{uuid.uuid4().hex[:12]}"
    started = datetime.now(timezone.utc).isoformat()
    registration = load_registration()
    intake = build_intake_from_registration(registration)
    validate_intake(intake)

    state = create_execution_state(intake["task_id"])
    append_event(state, "TASK_NORMALIZED", intake["task_id"])

    routing = route_task(intake)
    validate_routing_decision(routing)
    bind_routing_to_execution(state, routing)
    append_event(state, "ROUTING_CREATED", routing["routing_id"])

    production_blocked = can_transition(state, "PRODUCTION", routing)
    direction = write_direction_artifacts(DIRECTION_DIR, routing=routing, intake=intake)
    design_gate = evaluate_design_gate(DIRECTION_DIR, routing)

    if design_gate["status"] == "APPROVED":
        set_design_gate_state(state, "APPROVED")
        unlock_planned_skills(state, routing)
        append_event(state, "DESIGN_GATE_APPROVED", routing["routing_id"])
    else:
        set_design_gate_state(state, design_gate["status"])

    missing_impl = verify_implementation()
    if missing_impl and design_gate["status"] == "APPROVED":
        return {
            "run_id": run_id,
            "benchmark_result": "BLOCKED",
            "reason": f"implementation_missing: {missing_impl}",
            "routing_id": routing["routing_id"],
        }

    analysis = analyze_implementation(IMPL_DIR)
    meaningful_3d_used = direction.get("creative", {}).get("three_d_decision", {}).get("meaningful_3d_used") is True
    evidence_bundle: dict[str, Any] = {}
    evidence_records: list[dict[str, Any]] = []

    if not skip_browser and design_gate["status"] == "APPROVED":
        target = IMPL_DIR / "index.html"
        viewport_result = capture_viewport_evidence(target, EVIDENCE_DIR / "E-001", reduced_motion=False)
        reduced_result = capture_viewport_evidence(target, EVIDENCE_DIR / "E-008", reduced_motion=True)
        interaction_result = capture_interaction_and_performance(target, EVIDENCE_DIR / "E-007")
        evidence_bundle = produce_derived_evidence(
            viewport_result=viewport_result,
            reduced_result=reduced_result,
            interaction_result=interaction_result,
            analysis=analysis,
        )
        evidence_records = _register_evidence_records(evidence_bundle)

    # Pre-gate evidence completeness (E-010 excluded — post-gate)
    pre_gate_ids = [e for e in required_evidence_ids(meaningful_3d_used=meaningful_3d_used) if e != "E-010"]
    pre_records = {r["evidence_id"]: r["artifact_ref"] for r in evidence_records}
    evidence_completeness_pre = {
        "required_evidence_ids": pre_gate_ids,
        "validated": [e for e in pre_gate_ids if e in pre_records],
        "missing": [e for e in pre_gate_ids if e not in pre_records],
        "invalid": [],
        "sufficient": set(pre_gate_ids).issubset(pre_records.keys()),
        "status": "SUFFICIENT" if set(pre_gate_ids).issubset(pre_records.keys()) else "BLOCKED_INSUFFICIENT_EVIDENCE",
    }

    critic_report = evaluate_critics(
        routing=routing,
        analysis=analysis,
        evidence_bundle=evidence_bundle,
        direction=direction,
        meaningful_3d_used=meaningful_3d_used,
    )

    gate_status, hard_rejects, decisions = determine_gate_status(
        evidence_completeness=evidence_completeness_pre,
        critic_report=critic_report,
        artifact_analysis=analysis,
        runtime_healthy=evidence_bundle.get("runtime_healthy", False),
        console_error_count=evidence_bundle.get("console_error_count", 0),
    )

    gate_report = build_gate_report(
        gate_status=gate_status,
        hard_rejects=hard_rejects,
        decisions=decisions,
        evidence_records=[{"id": e["evidence_id"], "ref": e["artifact_ref"]} for e in evidence_records],
        critic_report=critic_report,
        dimension_scores=critic_report.get("dimension_scores"),
    )
    gate_eval = evaluate_quality_gate(gate_report)
    final_gate = gate_eval["status"]

    RUN_DIR.mkdir(parents=True, exist_ok=True)
    gate_path = RUN_DIR / "gate_report.yaml"
    gate_path.write_text(yaml.dump(gate_report, sort_keys=False), encoding="utf-8")

    evidence_records.append(
        register_evidence(
            evidence_id="E-010",
            evidence_type="quality_gate_provenance",
            producer="ACOS-13",
            artifact_ref=str(gate_path),
            source="validation/benchmark_execution/run_bm001.py",
            integrity_verified=True,
        )
    )

    post_records = {r["evidence_id"]: r["artifact_ref"] for r in evidence_records}
    evidence_completeness = validate_required_evidence(
        meaningful_3d_used=meaningful_3d_used,
        evidence_records=post_records,
        gate_report_path=gate_path,
    )

    if not evidence_completeness.get("sufficient") and final_gate == "APPROVED":
        final_gate = "BLOCKED_INSUFFICIENT_EVIDENCE"
        gate_report["gate_report"]["status"] = final_gate
        gate_path.write_text(yaml.dump(gate_report, sort_keys=False), encoding="utf-8")

    validate_producer_independence(producer_skill_id="ACOS-04", critic_skill_id="ACOS-10")
    state["gate_states"]["quality_gate"] = final_gate
    append_event(
        state,
        "GATE_APPROVED" if final_gate == "APPROVED" else ("GATE_REJECTED" if final_gate == "REJECTED" else "GATE_BLOCKED"),
        final_gate,
    )

    score = score_benchmark(
        acceptance=registration.get("acceptance_contract") or {},
        gate_status=final_gate,
        critic_report=critic_report,
        evidence_completeness=evidence_completeness,
        meaningful_3d_used=meaningful_3d_used,
    )

    superseded = {
        "invalidated_run_id": INVALIDATED_RUN_ID,
        "invalidated_result": "PASS",
        "invalidated_score": 85.5,
        "invalidation_reason": "certification_correction_insufficient_evaluation",
        "superseded_at": datetime.now(timezone.utc).isoformat(),
    }

    (RUN_DIR / "routing_decision.json").write_text(json.dumps(routing, indent=2), encoding="utf-8")
    (RUN_DIR / "design_gate_decision.yaml").write_text(yaml.dump(design_gate, sort_keys=False), encoding="utf-8")
    (RUN_DIR / "evidence_completeness.yaml").write_text(yaml.dump(evidence_completeness, sort_keys=False), encoding="utf-8")
    (RUN_DIR / "evidence_plan_reference.yaml").write_text(yaml.dump({"evidence_plan": load_evidence_plan()}, sort_keys=False), encoding="utf-8")
    (RUN_DIR / "critic_report.yaml").write_text(yaml.dump(critic_report, sort_keys=False), encoding="utf-8")
    (RUN_DIR / "benchmark_score.yaml").write_text(yaml.dump(score, sort_keys=False), encoding="utf-8")
    (RUN_DIR / "superseded_results.yaml").write_text(yaml.dump(superseded, sort_keys=False), encoding="utf-8")
    persist_state(state, store_dir=RUN_DIR)

    report = {
        "run_id": run_id,
        "started_at": started,
        "completed_at": datetime.now(timezone.utc).isoformat(),
        "benchmark_id": "BM-001",
        "contract_version": "1.1",
        "contract_hash": FROZEN_CONTRACT_HASH,
        "certification_correction": True,
        "supersedes_run": INVALIDATED_RUN_ID,
        "routing_id": routing["routing_id"],
        "routing_status": routing["status"],
        "activated_skills": routing.get("planned_skill_ids") or [],
        "design_gate_result": design_gate["status"],
        "production_blocked_before_gate": not production_blocked.get("allowed"),
        "implementation_path": str(IMPL_DIR.relative_to(REPO)),
        "meaningful_3d_used": meaningful_3d_used,
        "required_evidence_ids": evidence_completeness.get("required_evidence_ids"),
        "evidence_captured": sorted(post_records.keys()),
        "evidence_completeness": evidence_completeness.get("status"),
        "evidence_missing": evidence_completeness.get("missing"),
        "evidence_invalid": evidence_completeness.get("invalid"),
        "critic_findings": critic_report.get("findings", []),
        "hard_rejects_triggered": [hr["id"] for hr in hard_rejects if hr.get("triggered")],
        "corrections_attempted": [],
        "quality_gate_result": final_gate,
        "scoring_profile": score.get("profile"),
        "benchmark_score": score.get("benchmark_score"),
        "benchmark_result": score.get("benchmark_result"),
        "dimension_scores": score.get("dimension_scores"),
        "score_provenance": score.get("provenance"),
        "restrictions": [],
    }
    (RUN_DIR / "EXECUTION_REPORT.yaml").write_text(yaml.dump(report, sort_keys=False), encoding="utf-8")
    return report


def main() -> int:
    skip = "--skip-browser" in sys.argv
    report = run_execution(skip_browser=skip)
    print(yaml.dump(report, sort_keys=False))
    return 0 if report.get("benchmark_result") in ("PASS", "FAIL", "BLOCKED") else 1


if __name__ == "__main__":
    sys.exit(main())
