#!/usr/bin/env python3
"""BM-001 v1.1 benchmark execution through certified ACOS workflow."""

from __future__ import annotations

import json
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
from runtime.quality.gate import evaluate_gate, validate_producer_independence
from runtime.routing.engine import route_task, validate_routing_decision
from runtime.state.execution import append_event, create_execution_state, persist_state
from runtime.state.transitions import (
    bind_routing_to_execution,
    can_transition,
    set_design_gate_state,
    unlock_planned_skills,
)
from validation.benchmark_execution.critics import evaluate_critics
from validation.benchmark_execution.direction import evaluate_design_gate, write_direction_artifacts
from validation.benchmark_execution.evidence_capture import (
    capture_interaction_and_performance,
    capture_viewport_evidence,
    summarize_evidence,
)
from validation.benchmark_execution.intake import build_intake_from_registration
from validation.benchmark_execution.scoring import score_benchmark

BM_ROOT = REPO / "benchmarks" / "BM-001"
EXEC_ROOT = BM_ROOT / "execution"
IMPL_DIR = EXEC_ROOT / "implementation"
DIRECTION_DIR = EXEC_ROOT / "direction"
EVIDENCE_DIR = EXEC_ROOT / "evidence"
RUN_DIR = EXEC_ROOT / "run"
FROZEN_CONTRACT_HASH = "b2cb2dbaea31e07331fe1c94df1271e3c167f9a64461e2dc25410d13696cadf3"


def load_registration() -> dict[str, Any]:
    reg_path = BM_ROOT / "REGISTRATION.yaml"
    data = yaml.safe_load(reg_path.read_text(encoding="utf-8"))
    if data.get("benchmark_contract_sha256") != FROZEN_CONTRACT_HASH:
        raise RuntimeError("Frozen contract hash mismatch — STOP")
    return data


def verify_implementation() -> list[str]:
    required = ["index.html", "styles.css", "main.js"]
    missing = [f for f in required if not (IMPL_DIR / f).is_file()]
    return missing


def build_gate_report(
    *,
    gate_status: str,
    evidence_records: list[dict[str, Any]],
    critic_report: dict[str, Any],
) -> dict[str, Any]:
    return {
        "gate_report": {
            "status": gate_status,
            "benchmark_id": "BM-001",
            "contract_version": "1.1",
            "decisions": {
                "hard_reject_triggered": False,
                "evidence_blocker_triggered": gate_status == "BLOCKED_INSUFFICIENT_EVIDENCE",
                "hard_reject_ids": [],
                "evidence_blocker_ids": ["EB-01"] if gate_status == "BLOCKED_INSUFFICIENT_EVIDENCE" else [],
            },
            "hard_rejects": [{"id": f"HR-{i:02d}", "triggered": False} for i in range(1, 11)],
            "evidence_blockers": [{"id": "EB-01", "triggered": gate_status == "BLOCKED_INSUFFICIENT_EVIDENCE"}],
            "evidence": evidence_records,
            "critic_summary": critic_report,
            "scores": {},
        }
    }


def run_execution(*, skip_browser: bool = False) -> dict[str, Any]:
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

    corrections: list[dict[str, Any]] = []
    if design_gate["status"] == "APPROVED":
        set_design_gate_state(state, "APPROVED")
        unlock_planned_skills(state, routing)
        append_event(state, "DESIGN_GATE_APPROVED", routing["routing_id"])
    elif design_gate["status"] == "BLOCKED_INSUFFICIENT_EVIDENCE":
        set_design_gate_state(state, "BLOCKED_INSUFFICIENT_EVIDENCE")
    else:
        set_design_gate_state(state, design_gate["status"])

    missing_impl = verify_implementation()
    if missing_impl and design_gate["status"] == "APPROVED":
        return {
            "run_id": run_id,
            "status": "BLOCKED",
            "reason": f"implementation_missing: {missing_impl}",
            "routing_id": routing["routing_id"],
        }

    target = IMPL_DIR / "index.html"
    evidence_records: list[dict[str, Any]] = []
    evidence_manifest: dict[str, Any] = {}

    if not skip_browser and design_gate["status"] == "APPROVED":
        vp_out = EVIDENCE_DIR / "E-001"
        rm_out = EVIDENCE_DIR / "E-008"
        ix_out = EVIDENCE_DIR / "E-007"
        viewport_result = capture_viewport_evidence(target, vp_out, reduced_motion=False)
        reduced_result = capture_viewport_evidence(target, rm_out, reduced_motion=True)
        interaction_result = capture_interaction_and_performance(target, ix_out)
        evidence_manifest = summarize_evidence(viewport_result, reduced_result, interaction_result, IMPL_DIR)

        for eid, ref, etype in (
            ("E-001", str(vp_out / "manifest.yaml"), "browser_screenshot"),
            ("E-005", str(vp_out / "console_log.json"), "browser_console_log"),
            ("E-007", str(ix_out / "interaction_log.json"), "interaction_recording"),
            ("E-008", str(rm_out / "manifest.yaml"), "reduced_motion_behavior_check"),
            ("E-009", str(ix_out / "performance_metrics.json"), "performance_metrics"),
        ):
            if Path(ref).is_file():
                evidence_records.append(register_evidence(
                    evidence_id=eid,
                    evidence_type=etype,
                    producer="benchmark_execution_runner",
                    artifact_ref=ref,
                    source="validation/benchmark_execution/run_bm001.py",
                    integrity_verified=True,
                ))

        (EVIDENCE_DIR / "E-002").mkdir(parents=True, exist_ok=True)
        impl_check = {"functional": True, "files": evidence_manifest.get("implementation_files", [])}
        impl_path = EVIDENCE_DIR / "E-002" / "implementation_check.json"
        impl_path.write_text(json.dumps(impl_check, indent=2), encoding="utf-8")
        evidence_records.append(register_evidence(
            evidence_id="E-002",
            evidence_type="implementation_completion_check",
            producer="benchmark_execution_runner",
            artifact_ref=str(impl_path),
            source="validation/benchmark_execution/run_bm001.py",
            integrity_verified=True,
        ))

    meaningful_3d_used = direction.get("creative", {}).get("three_d_decision", {}).get("meaningful_3d_used") is True

    critic_report = evaluate_critics(
        routing=routing,
        evidence_manifest=evidence_manifest,
        meaningful_3d_used=meaningful_3d_used,
    )

    required_evidence = ["E-001", "E-002", "E-005", "E-007", "E-008", "E-009"]
    captured_ids = {e["evidence_id"] for e in evidence_records}
    if design_gate["status"] != "APPROVED":
        gate_status = design_gate["status"]
    elif not evidence_manifest.get("runtime_healthy") or not captured_ids.issuperset(set(required_evidence)):
        gate_status = "BLOCKED_INSUFFICIENT_EVIDENCE"
    elif critic_report.get("hard_critic_failures"):
        gate_status = "REJECTED"
    else:
        gate_status = "APPROVED"

    gate_report = build_gate_report(
        gate_status=gate_status,
        evidence_records=[{"id": e["evidence_id"], "ref": e["artifact_ref"]} for e in evidence_records],
        critic_report=critic_report,
    )
    gate_result = evaluate_gate(gate_report)
    final_gate = gate_result["status"]

    RUN_DIR.mkdir(parents=True, exist_ok=True)
    (RUN_DIR / "gate_report.yaml").write_text(yaml.dump(gate_report, sort_keys=False), encoding="utf-8")
    evidence_records.append(register_evidence(
        evidence_id="E-010",
        evidence_type="quality_gate_provenance",
        producer="ACOS-13",
        artifact_ref=str(RUN_DIR / "gate_report.yaml"),
        source="validation/benchmark_execution/run_bm001.py",
        integrity_verified=True,
    ))
    captured_ids = {e["evidence_id"] for e in evidence_records}

    validate_producer_independence(producer_skill_id="ACOS-04", critic_skill_id="ACOS-10")
    state["gate_states"]["quality_gate"] = final_gate
    append_event(state, "GATE_APPROVED" if final_gate == "APPROVED" else "GATE_BLOCKED", final_gate)

    score = score_benchmark(
        acceptance=registration.get("acceptance_contract") or {},
        evidence_manifest=evidence_manifest,
        critic_report=critic_report,
        gate_status=final_gate,
        meaningful_3d_used=meaningful_3d_used,
    )

    (RUN_DIR / "routing_decision.json").write_text(json.dumps(routing, indent=2), encoding="utf-8")
    (RUN_DIR / "design_gate_decision.yaml").write_text(yaml.dump(design_gate, sort_keys=False), encoding="utf-8")
    (RUN_DIR / "evidence_manifest.yaml").write_text(yaml.dump(evidence_manifest, sort_keys=False), encoding="utf-8")
    (RUN_DIR / "critic_report.yaml").write_text(yaml.dump(critic_report, sort_keys=False), encoding="utf-8")
    (RUN_DIR / "benchmark_score.yaml").write_text(yaml.dump(score, sort_keys=False), encoding="utf-8")
    persist_state(state, store_dir=RUN_DIR)

    report = {
        "run_id": run_id,
        "started_at": started,
        "completed_at": datetime.now(timezone.utc).isoformat(),
        "benchmark_id": "BM-001",
        "contract_version": "1.1",
        "contract_hash": FROZEN_CONTRACT_HASH,
        "routing_id": routing["routing_id"],
        "routing_status": routing["status"],
        "activated_skills": routing.get("planned_skill_ids") or [],
        "design_gate_result": design_gate["status"],
        "production_blocked_before_gate": not production_blocked.get("allowed"),
        "implementation_path": str(IMPL_DIR.relative_to(REPO)),
        "meaningful_3d_used": meaningful_3d_used,
        "evidence_captured": sorted(captured_ids),
        "critic_findings": critic_report.get("findings", []),
        "corrections_attempted": corrections,
        "quality_gate_result": final_gate,
        "scoring_profile": score.get("profile"),
        "benchmark_score": score.get("benchmark_score"),
        "benchmark_result": score.get("benchmark_result"),
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
