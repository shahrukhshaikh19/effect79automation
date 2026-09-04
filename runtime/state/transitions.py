"""Design Gate and workflow transition guards."""

from __future__ import annotations

from typing import Any

from runtime.common.registry_loader import load_routing_policy


def _design_gate_required_stages() -> list[str]:
    policy = load_routing_policy()
    dg = policy.get("design_gate", {})
    return list(dg.get("required_before_stages", ["PRODUCTION", "SPECIALIST_ROUTING"]))


def design_gate_applies(design_gate_state: str) -> bool:
    return design_gate_state not in ("NOT_APPLICABLE",)


def can_transition(
    execution_state: dict[str, Any],
    target_stage: str,
    routing_decision: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Runtime guard — production/specialist stages blocked until Design Gate APPROVED.
    Policy-driven stage list from registry/ROUTING_POLICY.yaml.
    """
    gate = execution_state.get("gate_states", {}).get("design_gate", "NOT_APPLICABLE")
    if routing_decision and routing_decision.get("design_gate_state"):
        gate = routing_decision["design_gate_state"]

    required_before = _design_gate_required_stages()
    if target_stage not in required_before:
        return {"allowed": True, "reason": "stage_not_gated_by_design_gate"}

    if gate == "NOT_APPLICABLE":
        return {"allowed": True, "reason": "design_gate_not_applicable"}

    if gate == "APPROVED":
        return {"allowed": True, "reason": "design_gate_approved"}

    if gate == "REJECTED":
        return {
            "allowed": False,
            "reason": "TRANSITION_BLOCKED_DESIGN_GATE_REJECTED",
            "route_correction_upstream": True,
        }

    if gate == "BLOCKED_INSUFFICIENT_EVIDENCE":
        return {
            "allowed": False,
            "reason": "TRANSITION_BLOCKED_DESIGN_GATE_INSUFFICIENT_EVIDENCE",
            "collect_evidence": True,
        }

    return {"allowed": False, "reason": "TRANSITION_BLOCKED_DESIGN_GATE"}


def split_executable_skills(
    skill_activations: list[dict[str, Any]],
    design_gate_state: str,
) -> tuple[list[str], list[str]]:
    """Return (planned_skill_ids, executable_active_skill_ids)."""
    planned = sorted({a["skill_id"] for a in skill_activations if isinstance(a, dict) and a.get("skill_id")})
    if design_gate_state in ("NOT_APPLICABLE", "APPROVED"):
        return planned, planned

    gated_stages = set(_design_gate_required_stages())
    executable: list[str] = []
    for activation in skill_activations:
        if not isinstance(activation, dict):
            continue
        stage = activation.get("stage", "")
        skill_id = activation.get("skill_id")
        if skill_id and stage not in gated_stages:
            executable.append(skill_id)
    return planned, sorted(set(executable))


def set_design_gate_state(execution_state: dict[str, Any], new_state: str) -> dict[str, Any]:
    valid = {
        "NOT_APPLICABLE",
        "PENDING",
        "APPROVED",
        "REJECTED",
        "BLOCKED_INSUFFICIENT_EVIDENCE",
    }
    if new_state not in valid:
        raise ValueError(f"Invalid design gate state: {new_state}")
    execution_state.setdefault("gate_states", {})["design_gate"] = new_state
    return execution_state
