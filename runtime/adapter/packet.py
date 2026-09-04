"""Build adapter-ready task packets from routing output."""

from __future__ import annotations

from typing import Any

from runtime.common.registry_loader import skill_path_for_id


def build_adapter_packet(
    intake: dict[str, Any],
    routing: dict[str, Any],
    *,
    adapter_target: str = "local",
) -> dict[str, Any]:
    activated_skills = []
    activations = {a["skill_id"]: a for a in routing.get("skill_activations", []) if isinstance(a, dict)}
    for skill_id in routing.get("activated_skill_ids", []):
        activated_skills.append(
            {
                "skill_id": skill_id,
                "skill_path": skill_path_for_id(skill_id),
                "load_level": "L2",
                "activation_reason": activations.get(skill_id, {}).get("activation_reason", ""),
            }
        )

    caps = intake.get("runtime_capabilities") or {}
    allowed_tools = [
        {"family": family, "status": caps.get(family, "UNKNOWN")}
        for family in ("browser", "blender", "git", "shell", "filesystem")
    ]

    routing_status = "ok"
    if routing.get("status") != "ROUTED":
        routing_status = routing.get("status", "insufficient_routing_input").lower()

    return {
        "acos_version": "1.2",
        "task_id": intake["task_id"],
        "adapter_target": adapter_target,
        "routing": {
            "source": "phase_f_router",
            "routing_id": routing.get("routing_id"),
            "activated_skill_ids": routing.get("activated_skill_ids", []),
            "routing_evidence_ref": routing.get("routing_id"),
            "status": routing_status,
            "decision_reasons": routing.get("decision_reasons", []),
        },
        "activated_skills": activated_skills,
        "allowed_tools": allowed_tools,
        "memory_refs": routing.get("memory_refs", []),
        "evidence_requirements": [
            a.get("evidence_required", []) for a in routing.get("skill_activations", []) if isinstance(a, dict)
        ],
        "stage": {"id": routing.get("stage", ""), "design_gate": routing.get("design_gate_state")},
        "output_contract": {"deliverables": intake.get("deliverables", [])},
    }
