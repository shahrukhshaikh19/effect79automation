"""Design Gate and workflow transition guards."""

from __future__ import annotations

from typing import Any

from runtime.common.registry_loader import load_routing_policy


def _design_gate_required_stages() -> list[str]:
    policy = load_routing_policy()
    dg = policy.get("design_gate", {})
    return list(dg.get("required_before_stages", ["PRODUCTION", "SPECIALIST_ROUTING"]))


def authoritative_design_gate(
    execution_state: dict[str, Any],
    routing_decision: dict[str, Any] | None = None,
) -> str:
    """
    Execution-state gate is authoritative over historical routing snapshots.
    Routing snapshot used only when execution state has no gate value yet.
    """
    gate_states = execution_state.get("gate_states") or {}
    if "design_gate" in gate_states and gate_states["design_gate"] is not None:
        return str(gate_states["design_gate"])
    if routing_decision and routing_decision.get("design_gate_state") is not None:
        return str(routing_decision["design_gate_state"])
    return "NOT_APPLICABLE"


def design_gate_applies(design_gate_state: str) -> bool:
    return design_gate_state not in ("NOT_APPLICABLE",)


def can_transition(
    execution_state: dict[str, Any],
    target_stage: str,
    routing_decision: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Runtime guard — production/specialist stages blocked until Design Gate APPROVED.
    Current execution-state gate always wins over stale routing_decision.design_gate_state.
    """
    gate = authoritative_design_gate(execution_state, routing_decision)

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


def bind_routing_to_execution(
    execution_state: dict[str, Any],
    routing_decision: dict[str, Any],
) -> dict[str, Any]:
    """Attach routing provenance to execution state without rerouting."""
    execution_state["routing_id"] = routing_decision.get("routing_id")
    execution_state["planned_skill_ids"] = list(
        routing_decision.get("planned_skill_ids") or routing_decision.get("activated_skill_ids") or []
    )
    if routing_decision.get("design_gate_state") is not None:
        if execution_state.get("gate_states", {}).get("design_gate") in (None, "NOT_APPLICABLE"):
            execution_state.setdefault("gate_states", {})["design_gate"] = routing_decision["design_gate_state"]
    return refresh_executable_activations(execution_state, routing_decision)


def refresh_executable_activations(
    execution_state: dict[str, Any],
    routing_decision: dict[str, Any],
) -> dict[str, Any]:
    """
    Recalculate active_skill_ids from planned route + current authoritative gate state.
    Does not reroute or discover new skills.
    """
    planned = list(
        execution_state.get("planned_skill_ids")
        or routing_decision.get("planned_skill_ids")
        or routing_decision.get("activated_skill_ids")
        or []
    )
    planned_set = set(planned)
    activations = [
        a
        for a in routing_decision.get("skill_activations", [])
        if isinstance(a, dict) and a.get("skill_id") in planned_set
    ]
    gate = authoritative_design_gate(execution_state, routing_decision)
    _, executable = split_executable_skills(activations, gate)
    executable = sorted(s for s in executable if s in planned_set)

    execution_state["planned_skill_ids"] = sorted(planned_set)
    execution_state["active_skill_ids"] = executable
    return execution_state


def unlock_planned_skills(
    execution_state: dict[str, Any],
    routing_decision: dict[str, Any],
) -> dict[str, Any]:
    """Refresh executable activations after gate state change (e.g. approval)."""
    return refresh_executable_activations(execution_state, routing_decision)


def validate_active_skills_subset(
    execution_state: dict[str, Any],
    skill_ids: list[str],
) -> None:
    """Reject activation of skills not present in the original planned route."""
    planned = set(execution_state.get("planned_skill_ids", []))
    extra = set(skill_ids) - planned
    if extra:
        raise ValueError(f"Cannot activate skills not in planned_skill_ids: {sorted(extra)}")
