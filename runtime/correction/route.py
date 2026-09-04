"""Policy-driven defect correction routing."""

from __future__ import annotations

from typing import Any

from runtime.common.registry_loader import is_skill_known, load_routing_policy


def route_defect_to_skill(
    defect_type: str,
    *,
    producer_skill_id: str | None = None,
    activated_skill_ids: list[str] | None = None,
    detector_skill_id: str | None = None,
) -> dict[str, Any]:
    """
    Resolve correction ownership from registry/ROUTING_POLICY.yaml correction_responsibility.
    Critics detect defects — they are not default correction producers.
    """
    policy = load_routing_policy()
    responsibility = policy.get("correction_responsibility", {})
    spec = responsibility.get(defect_type)
    if not isinstance(spec, dict):
        return {
            "status": "CORRECTION_ROUTING_REQUIRES_RESOLUTION",
            "responsible_skill_ids": [],
            "reason": f"unknown defect type: {defect_type}",
        }

    owner_domains = spec.get("owner_domains", [])
    exclude_roles = set(spec.get("exclude_roles", ["critic", "gate", "memory"]))
    skill_domains = policy.get("skill_domains", {})

    candidates: list[str] = []
    for skill_id, meta in skill_domains.items():
        if not is_skill_known(skill_id):
            continue
        if meta.get("role") in exclude_roles:
            continue
        domains = meta.get("domains", [])
        if any(domain in owner_domains for domain in domains):
            candidates.append(skill_id)

    if activated_skill_ids:
        candidates = [c for c in candidates if c in activated_skill_ids] or candidates

    if producer_skill_id and producer_skill_id in candidates:
        chosen = [producer_skill_id]
    elif candidates:
        chosen = [candidates[0]]
    else:
        return {
            "status": "CORRECTION_ROUTING_REQUIRES_RESOLUTION",
            "responsible_skill_ids": [],
            "reason": "no responsible skill resolved from policy domains",
        }

    if detector_skill_id and detector_skill_id in chosen:
        return {
            "status": "CORRECTION_ROUTING_REQUIRES_RESOLUTION",
            "responsible_skill_ids": [],
            "reason": "critic/detector cannot be correction producer",
        }

    return {
        "status": "ROUTED",
        "responsible_skill_ids": chosen,
        "reason": f"policy domains {owner_domains} resolved to {chosen}",
    }
