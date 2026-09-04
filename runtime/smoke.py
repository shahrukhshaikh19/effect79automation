#!/usr/bin/env python3
"""Domain-neutral Phase F runtime smoke flow."""

from __future__ import annotations

import json
import sys
import uuid
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from runtime.adapter.packet import build_adapter_packet
from runtime.correction.budget import create_correction_request
from runtime.evidence.register import register_evidence
from runtime.handoff.validate import build_handoff, validate_handoff
from runtime.intake.normalize import normalize_intake
from runtime.intake.validate import validate_intake
from runtime.memory.records import create_memory_observation
from runtime.quality.gate import evaluate_gate, validate_producer_independence
from runtime.routing.engine import route_task, validate_routing_decision
from runtime.state.execution import (
    append_event,
    create_execution_state,
    persist_state,
    resume_execution,
)
from runtime.state.transitions import (
    bind_routing_to_execution,
    can_transition,
    set_design_gate_state,
    unlock_planned_skills,
)

SMOKE_DIR = REPO / "validation" / "evidence" / "runtime" / "smoke"


def run_design_gate_lifecycle_probe() -> dict:
    """Visual synthetic intake → gate pending → approve → unlock → packet update."""
    task_id = f"task-dg-{uuid.uuid4().hex[:8]}"
    intake = normalize_intake(
        {
            "task_id": task_id,
            "request": "Deliver bounded visual layout module.",
            "normalized_goal": "Create responsive visual layout with art direction.",
            "deliverables": ["layout", "visual_evidence"],
            "constraints": ["domain_neutral"],
            "task_signals": {
                "deliverable_profile": "visual_experience",
                "requires_visual_output": True,
                "requires_creative_direction": True,
                "requires_responsive": True,
            },
            "runtime_capabilities": {"browser": "AVAILABLE", "blender": "RESTRICTED"},
        }
    )
    routing = route_task(intake)
    state = create_execution_state(task_id)
    bind_routing_to_execution(state, routing)
    routing_id = routing["routing_id"]

    blocked_before = can_transition(state, "PRODUCTION", routing)
    packet_before = build_adapter_packet(intake, routing, execution_state=state)

    set_design_gate_state(state, "APPROVED")
    append_event(state, "DESIGN_GATE_APPROVED", routing_id)
    unlock_planned_skills(state, routing)
    append_event(state, "EXECUTABLE_SKILLS_REFRESHED", routing_id)

    allowed_after = can_transition(state, "PRODUCTION", routing)
    packet_after = build_adapter_packet(intake, routing, execution_state=state)

    return {
        "task_id": task_id,
        "routing_id": routing_id,
        "routing_id_unchanged": packet_after["routing"]["routing_id"] == routing_id,
        "design_gate_before": "PENDING",
        "production_blocked_before": not blocked_before["allowed"],
        "acos_08_planned": "ACOS-08" in state["planned_skill_ids"],
        "acos_08_inactive_before": "ACOS-08" not in packet_before["routing"]["activated_skill_ids"],
        "acos_08_active_after": "ACOS-08" in state["active_skill_ids"],
        "acos_08_in_packet_after": "ACOS-08" in packet_after["routing"]["activated_skill_ids"],
        "production_allowed_after": allowed_after["allowed"],
    }


def run_smoke() -> dict:
    task_id = f"task-smoke-{uuid.uuid4().hex[:8]}"
    intake = normalize_intake(
        {
            "task_id": task_id,
            "request": "Implement bounded data-display module with validation.",
            "normalized_goal": "Deliver validated data-display module with accessibility checks.",
            "deliverables": ["module", "validation_evidence"],
            "constraints": ["domain_neutral", "evidence_required"],
            "task_signals": {
                "deliverable_profile": "standard_application",
                "requires_frontend": True,
                "requires_accessibility": True,
                "requires_3d": False,
                "requires_visual_output": False,
                "requires_creative_direction": False,
            },
            "runtime_capabilities": {
                "browser": "AVAILABLE",
                "blender": "RESTRICTED",
                "git": "AVAILABLE",
                "shell": "AVAILABLE",
                "filesystem": "AVAILABLE",
            },
        }
    )
    validate_intake(intake)
    state = create_execution_state(task_id)
    append_event(state, "TASK_NORMALIZED", task_id)

    routing = route_task(intake)
    validate_routing_decision(routing)
    append_event(state, "ROUTING_CREATED", routing["routing_id"])
    bind_routing_to_execution(state, routing)
    dg_probe = can_transition(state, "PRODUCTION", routing)

    handoff = build_handoff(
        task_id=task_id,
        from_stage="INTAKE",
        to_stage="PRODUCTION",
        producer_skill_id="router",
        consumer_skill_ids=state["active_skill_ids"][:3],
        artifact_refs=[f"artifact://{task_id}/plan"],
        evidence_refs=[],
        constraints_preserved=intake.get("constraints", []),
    )
    validate_handoff(handoff)
    append_event(state, "HANDOFF_CREATED", handoff["handoff_id"])

    evidence = register_evidence(
        evidence_id=f"EV-{task_id[:8]}",
        evidence_type="test_result",
        producer="validation-smoke",
        artifact_ref=str(SMOKE_DIR / "test-output.json"),
        source="runtime/smoke.py",
        integrity_verified=True,
    )
    state["evidence_refs"].append(evidence["evidence_id"])
    append_event(state, "EVIDENCE_REGISTERED", evidence["evidence_id"])

    gate_report = {
        "gate_report": {
            "status": "APPROVED",
            "decisions": {
                "hard_reject_triggered": False,
                "evidence_blocker_triggered": False,
                "hard_reject_ids": [],
                "evidence_blocker_ids": [],
            },
            "hard_rejects": [{"id": f"HR-{i:02d}", "triggered": False} for i in range(1, 11)],
            "evidence_blockers": [{"id": "EB-01", "triggered": False}],
            "evidence": [{"id": evidence["evidence_id"], "ref": evidence["artifact_ref"]}],
            "scores": {"engineering_quality": 8},
        }
    }
    gate_result = evaluate_gate(gate_report)
    validate_producer_independence(producer_skill_id="EXT-A11Y-01", critic_skill_id="ACOS-10")
    state["gate_states"]["quality_gate"] = gate_result["status"]
    append_event(state, "GATE_APPROVED", gate_result["status"])

    memory = create_memory_observation(
        memory_id=f"mem-obs-{task_id[:8]}",
        category="projects",
        scope="project",
        statement="Validation module pattern succeeded under bounded constraints.",
        source_task_id=task_id,
        evidence_refs=[evidence["evidence_id"]],
        subject_key="validation.module_pattern",
        value="bounded_success",
    )
    state["memory_candidates"].append(memory["memory_id"])
    append_event(state, "MEMORY_CANDIDATE_CREATED", memory["memory_id"])

    packet = build_adapter_packet(intake, routing, execution_state=state)
    correction = create_correction_request(
        task_id=task_id,
        source_gate_or_critic="ACOS-13",
        defect_ids=["sample"],
        severity="minor",
        responsible_skill_ids=["EXT-A11Y-01"],
        retry_number=1,
    )

    state["completed_stages"] = ["INTAKE", "ROUTING", "PRODUCTION", "QUALITY_GATE"]
    state["current_stage"] = "MEMORY_CANDIDATES"
    state["status"] = "COMPLETED"
    path = persist_state(state)
    resumed = resume_execution(task_id)

    dg_lifecycle = run_design_gate_lifecycle_probe()

    result = {
        "task_id": task_id,
        "routing_status": routing["status"],
        "gate_status": gate_result["status"],
        "active_skills": state["active_skill_ids"],
        "planned_skills": state["planned_skill_ids"],
        "design_gate_probe": dg_probe,
        "design_gate_lifecycle": dg_lifecycle,
        "adapter_packet_routing_source": packet["routing"]["source"],
        "correction_status": correction["status"],
        "state_path": str(path.relative_to(REPO)),
        "resume_stage": resumed["current_stage"],
        "events_count": len(resumed["events"]),
    }
    SMOKE_DIR.mkdir(parents=True, exist_ok=True)
    (SMOKE_DIR / "last-run.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result


if __name__ == "__main__":
    out = run_smoke()
    print(json.dumps(out, indent=2))
