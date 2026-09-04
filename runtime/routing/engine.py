"""Phase F routing engine — canonical owner of activated_skill_ids."""

from __future__ import annotations

import uuid
from typing import Any

from runtime.common.constants import LICENSE_RESTRICTED_SKILLS, OPERATIONAL_RESTRICTED_SKILLS
from runtime.common.registry_loader import (
    is_skill_known,
    load_routing_policy,
    skill_path_for_id,
    skill_restrictions,
)
from runtime.intake.validate import has_sufficient_routing_input


def _signal_true(signals: dict[str, Any], key: str) -> bool:
    return bool(signals.get(key))


def _rule_matches(rule: dict[str, Any], signals: dict[str, Any]) -> bool:
    when = rule.get("when")
    if not isinstance(when, dict):
        return False
    for key, expected in when.items():
        actual = signals.get(key)
        if actual != expected:
            return False
    return True


def _should_activate(item: dict[str, Any], signals: dict[str, Any], *, always_on: bool) -> bool:
    condition = item.get("if")
    if condition == "always_on_completion":
        return always_on
    if condition and condition.startswith("requires_"):
        return _signal_true(signals, condition)
    return True


def _design_gate_state(signals: dict[str, Any]) -> str:
    if _signal_true(signals, "requires_creative_direction") or _signal_true(signals, "requires_visual_output"):
        return "PENDING"
    return "NOT_APPLICABLE"


def _append_completion_skills(
    activated: dict[str, dict[str, Any]], reasons: list[str], policy: dict[str, Any]
) -> None:
    for item in (
        {"skill_id": "ACOS-13", "reason": "quality gate mandatory for ship/no-ship decision"},
        {"skill_id": "ACOS-14", "reason": "failure-learning for memory candidate creation post-gate"},
    ):
        skill_id = item["skill_id"]
        if skill_id in activated or not is_skill_known(skill_id):
            continue
        meta = (policy.get("skill_domains") or {}).get(skill_id, {})
        activated[skill_id] = {
            "skill_id": skill_id,
            "activation_reason": item["reason"],
            "stage": meta.get("stage", "QUALITY_GATE"),
            "required_inputs": [],
            "expected_output": f"Output per skills/ registry for {skill_id}",
            "allowed_tools": [],
            "evidence_required": ["gate_report"] if skill_id == "ACOS-13" else ["learning_record"],
            "handoff_target": "MEMORY_CANDIDATES" if skill_id == "ACOS-14" else "OUTPUT",
        }
        reasons.append(f"{skill_id}: {item['reason']}")


def _check_tool_requirements(
    signals: dict[str, Any], capabilities: dict[str, str]
) -> tuple[list[str], list[str], str | None]:
    policy = load_routing_policy()
    reqs = policy.get("tool_family_requirements", {})
    blocked: list[str] = []
    required: list[str] = []
    status: str | None = None

    profile = signals.get("deliverable_profile")
    if profile == "authored_3d_asset":
        spec = reqs.get("authored_3d_asset", {})
        for family in spec.get("required", []):
            required.append(family)
            state = capabilities.get(family, "UNKNOWN")
            if state in ("BLOCKED", "UNAVAILABLE"):
                blocked.append(family)
                status = "ROUTING_BLOCKED_CAPABILITY"
    elif profile == "interactive_3d":
        spec = reqs.get("interactive_3d", {})
        for family in spec.get("required", []):
            required.append(family)
            state = capabilities.get(family, "UNKNOWN")
            if state in ("BLOCKED", "UNAVAILABLE"):
                blocked.append(family)
                status = "ROUTING_BLOCKED_CAPABILITY"
    return required, blocked, status


def route_task(intake: dict[str, Any]) -> dict[str, Any]:
    task_id = intake["task_id"]
    signals = intake.get("task_signals") or {}
    capabilities = intake.get("runtime_capabilities") or {}
    routing_id = f"route-{uuid.uuid4().hex[:12]}"

    if not has_sufficient_routing_input(intake):
        return {
            "routing_id": routing_id,
            "task_id": task_id,
            "stage": "ROUTING",
            "activated_skill_ids": [],
            "skill_activations": [],
            "rejected_candidate_skill_ids": [],
            "required_tool_families": [],
            "required_critic_ids": [],
            "quality_gate_required": False,
            "decision_reasons": ["Insufficient normalized goal or deliverable profile"],
            "evidence_refs": [],
            "memory_refs": intake.get("prior_memory_refs", []),
            "capability_constraints": {},
            "fallbacks": [],
            "design_gate_state": "NOT_APPLICABLE",
            "status": "ROUTING_BLOCKED_INSUFFICIENT_INPUT",
        }

    required_tools, blocked_tools, cap_status = _check_tool_requirements(signals, capabilities)
    if cap_status == "ROUTING_BLOCKED_CAPABILITY":
        return {
            "routing_id": routing_id,
            "task_id": task_id,
            "stage": "ROUTING",
            "activated_skill_ids": [],
            "skill_activations": [],
            "rejected_candidate_skill_ids": [],
            "required_tool_families": required_tools,
            "required_critic_ids": [],
            "quality_gate_required": False,
            "decision_reasons": [f"Required tool families unavailable: {blocked_tools}"],
            "evidence_refs": [],
            "memory_refs": intake.get("prior_memory_refs", []),
            "capability_constraints": {"blocked_tools": blocked_tools},
            "fallbacks": [{"condition": "tool_unavailable", "action": "ROUTING_BLOCKED_CAPABILITY"}],
            "design_gate_state": _design_gate_state(signals),
            "status": "ROUTING_BLOCKED_CAPABILITY",
        }

    policy = load_routing_policy()
    rules = policy.get("routing_rules", [])
    activated: dict[str, dict[str, Any]] = {}
    rejected: list[dict[str, str]] = []
    reasons: list[str] = []
    always_on = True

    exclude_domains: set[str] = set()
    for rule in rules:
        if rule.get("when_missing"):
            continue
        if not _rule_matches(rule, signals):
            continue
        for domain in rule.get("exclude_domains", []):
            exclude_domains.add(domain)
        for item in rule.get("activate", []):
            if not isinstance(item, dict):
                continue
            if not _should_activate(item, signals, always_on=always_on):
                continue
            skill_id = item.get("skill_id", "")
            reason = item.get("reason", "")
            if not skill_id:
                continue
            if not is_skill_known(skill_id):
                rejected.append({"skill_id": skill_id, "reason": "unknown_skill_id"})
                continue
            restrictions = skill_restrictions(skill_id)
            if skill_id in LICENSE_RESTRICTED_SKILLS:
                if not signals.get("license_review_acknowledged"):
                    rejected.append(
                        {
                            "skill_id": skill_id,
                            "reason": "LICENSE_REVIEW_REQUIRED — blocked_pending_license_review",
                        }
                    )
                    continue
            if skill_id in OPERATIONAL_RESTRICTED_SKILLS:
                if signals.get("reconstruction_path") != "procedural_browser":
                    rejected.append(
                        {
                            "skill_id": skill_id,
                            "reason": "img2threejs restricted — requires explicit procedural_browser path",
                        }
                    )
                    continue
            meta = (policy.get("skill_domains") or {}).get(skill_id, {})
            domains = meta.get("domains", [])
            if exclude_domains and any(d in exclude_domains for d in domains):
                rejected.append({"skill_id": skill_id, "reason": f"excluded domain for profile: {domains}"})
                continue
            activated[skill_id] = {
                "skill_id": skill_id,
                "activation_reason": reason,
                "stage": meta.get("stage", "SPECIALIST_ROUTING"),
                "required_inputs": [],
                "expected_output": f"Output per skills/ registry for {skill_id}",
                "allowed_tools": [],
                "evidence_required": ["stage_appropriate_evidence"],
                "handoff_target": "next_workflow_stage",
            }
            reasons.append(f"{skill_id}: {reason}")

    critic_reqs = policy.get("critic_requirements", {})
    required_critics: list[str] = []
    if _signal_true(signals, "requires_visual_output"):
        required_critics.extend(critic_reqs.get("visual_output", []))
    if _signal_true(signals, "requires_creative_direction"):
        required_critics.extend(critic_reqs.get("creative_concept", []))
    if _signal_true(signals, "requires_3d"):
        required_critics.extend(critic_reqs.get("meaningful_3d", []))

    for critic_id in required_critics:
        if critic_id not in activated and is_skill_known(critic_id):
            meta = (policy.get("skill_domains") or {}).get(critic_id, {})
            activated[critic_id] = {
                "skill_id": critic_id,
                "activation_reason": "Independent critic required for task signals",
                "stage": meta.get("stage", "INDEPENDENT_CRITICS"),
                "required_inputs": ["producer_artifacts", "evidence_refs"],
                "expected_output": "critic_report",
                "allowed_tools": [],
                "evidence_required": ["critic_report"],
                "handoff_target": "QUALITY_GATE",
            }
            reasons.append(f"{critic_id}: independent critic requirement")

    if activated or _signal_true(signals, "requires_frontend") or signals.get("deliverable_profile"):
        _append_completion_skills(activated, reasons, policy)

    activated_ids = sorted(activated.keys())
    license_blocked = [s for s in LICENSE_RESTRICTED_SKILLS if s not in activated_ids]
    restricted = [s for s in OPERATIONAL_RESTRICTED_SKILLS if s not in activated_ids]

    return {
        "routing_id": routing_id,
        "task_id": task_id,
        "stage": "SPECIALIST_ROUTING" if activated_ids else "ROUTING",
        "activated_skill_ids": activated_ids,
        "skill_activations": list(activated.values()),
        "rejected_candidate_skill_ids": rejected,
        "required_tool_families": required_tools,
        "required_critic_ids": [c for c in required_critics if c in activated_ids],
        "quality_gate_required": "ACOS-13" in activated_ids,
        "decision_reasons": reasons,
        "evidence_refs": list(intake.get("prior_evidence_refs", [])),
        "memory_refs": list(intake.get("prior_memory_refs", [])),
        "capability_constraints": {
            "blocked_tools": blocked_tools,
            "restricted_skills": restricted,
            "license_blocked_skills": list(license_blocked),
        },
        "fallbacks": [],
        "design_gate_state": _design_gate_state(signals),
        "status": "ROUTED" if activated_ids else "ROUTING_REQUIRES_HUMAN_DECISION",
    }


def validate_routing_decision(decision: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for skill_id in decision.get("activated_skill_ids", []):
        if not is_skill_known(skill_id):
            errors.append(f"Unknown activated skill: {skill_id}")
    activations = {a["skill_id"]: a for a in decision.get("skill_activations", []) if isinstance(a, dict)}
    for skill_id in decision.get("activated_skill_ids", []):
        if skill_id not in activations:
            errors.append(f"Missing activation record for {skill_id}")
        elif not activations[skill_id].get("activation_reason"):
            errors.append(f"Missing activation_reason for {skill_id}")
    return errors
