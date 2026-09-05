"""Mechanical host-pipeline audit. This is not visual QA and cannot SHIP alone."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from runtime.host.artifact_contract import (
    CRITIC_FILES,
    has_implementation,
    load_yaml,
    pixel_evidence,
    validate_creative_artifacts,
    validate_critic_artifacts,
    validate_critic_independence,
    viewport_manifest,
)
from runtime.host.design_gate import evaluate_host_design_gate
from runtime.host.product_form import form_gate_approved, requires_industrial_form
from runtime.host.visual_class import validate_visual_class


def ensure_roles(session: dict[str, Any]) -> dict[str, Any]:
    roles = session.setdefault("roles", {})
    task_id = str((session.get("intake") or {}).get("task_id") or "")
    roles.setdefault("producer_session_id", task_id)
    roles.setdefault("critic_pass_id", None)
    roles.setdefault("form_critic_pass_id", None)
    roles.setdefault("form_critic_host_context_id", None)
    roles.setdefault("independent_attestation", False)
    roles.setdefault("independence_claim", "none")
    roles.setdefault("independent_host_context", "UNVERIFIED")
    roles.setdefault("producer_host_context_id", None)
    roles.setdefault("critic_host_context_id", None)
    return roles


def audit_session(session: dict[str, Any], project_dir: Path) -> dict[str, Any]:
    ensure_roles(session)
    state = session.get("state") or {}
    routing = session.get("routing") or {}
    planned = list(state.get("planned_skill_ids") or routing.get("planned_skill_ids") or [])
    stage = str(state.get("current_stage") or "")
    design = evaluate_host_design_gate(project_dir, planned, routing.get("routing_id"))
    creative = validate_creative_artifacts(project_dir, planned)
    impl = has_implementation(project_dir)
    pixels = pixel_evidence(project_dir)
    manifest = viewport_manifest(project_dir)
    critics = validate_critic_artifacts(project_dir, planned)
    roles = session["roles"]
    independence = validate_critic_independence(
        project_dir,
        planned,
        critic_pass_id=roles.get("critic_pass_id"),
        attested=str(roles.get("independence_claim") or "") == "operator_attested"
        or bool(roles.get("independent_attestation")),
        roles=roles,
    )
    runtime_healthy = None if manifest is None else bool(manifest.get("runtime_healthy"))
    visual = validate_visual_class(project_dir, (session.get("intake") or {}).get("task_signals"))

    blockers: list[str] = []
    if not creative["ok"]:
        blockers.extend([f"missing {m}" for m in creative["missing"]])
        blockers.extend(creative["invalid"])
    if design["status"] != "APPROVED" and stage not in {"INTAKE", "CREATIVE", "DESIGN_GATE"}:
        blockers.append(f"design_gate is {design['status']}")
    if stage in {"PRODUCTION", "EVIDENCE", "CRITICS", "QUALITY_GATE", "SHIP"} and not impl:
        blockers.append("implementation missing")
    intake = session.get("intake") or {}
    industrial = requires_industrial_form(intake.get("task_signals"), intake.get("request") or "")
    if industrial and stage in {"PRODUCTION", "EVIDENCE", "CRITICS", "QUALITY_GATE", "SHIP"} and not form_gate_approved(project_dir):
        blockers.append("product form gate is not APPROVED")
    if stage in {"CRITICS", "QUALITY_GATE", "SHIP"} and len(pixels) < 2:
        blockers.append("need at least two rendered evidence images under evidence/")
    if runtime_healthy is False:
        blockers.append("viewport manifest runtime_healthy is false")
    if stage in {"CRITICS", "QUALITY_GATE", "SHIP"} and not visual["ok"]:
        blockers.extend(visual["issues"])
    if stage in {"QUALITY_GATE", "SHIP"} and not critics["ok"]:
        blockers.extend(critics["missing"] + critics["invalid"])
    if stage in {"QUALITY_GATE", "SHIP"} and not independence["ok"]:
        blockers.extend(independence["issues"])

    ship_allowed = (
        design["status"] == "APPROVED"
        and impl
        and len(pixels) >= 2
        and runtime_healthy is not False
        and critics["ok"]
        and independence["ok"]
        and visual["ok"]
        and (not industrial or form_gate_approved(project_dir))
    )

    return {
        "task_id": (session.get("intake") or {}).get("task_id"),
        "stage": stage,
        "design_gate": design["status"],
        "product_form_gate": (state.get("gate_states") or {}).get("product_form_gate"),
        "quality_gate": (state.get("gate_states") or {}).get("quality_gate"),
        "implementation": impl,
        "pixel_evidence": pixels,
        "pixel_count": len(pixels),
        "runtime_healthy": runtime_healthy,
        "critics_present": critics["ok"],
        "independence": independence,
        "ship_allowed": ship_allowed,
        "blockers": blockers,
        "next_command": _next_command(stage, impl, pixels, critics, independence, ship_allowed),
        "critic_files": [rel for sid, rel in CRITIC_FILES.items() if sid in planned],
    }


def _next_command(
    stage: str,
    impl: bool,
    pixels: list[str],
    critics: dict[str, Any],
    independence: dict[str, Any],
    ship_allowed: bool,
) -> str:
    if stage == "SHIP":
        return "none — session is SHIP"
    if stage == "WAITING_BLENDER":
        return "tell the user Blender MCP/app is down; after they connect: python tools/host_driver/run_stage.py confirm-blender --mcp-live"
    if stage in {"INTAKE", "CREATIVE", "DESIGN_GATE"}:
        return "write direction artifacts, then: python tools/host_driver/run_stage.py advance"
    if stage == "PRODUCT_DESIGN":
        return "write direction/product_design.yaml + form_specification.yaml, then: python tools/host_driver/run_stage.py advance"
    if stage == "FORM_AUTHORING":
        return "write form_model.yaml and clay views, then: python tools/host_driver/run_stage.py advance"
    if stage == "FORM_EVIDENCE":
        return "confirm evidence/form-clay/ views, then: python tools/host_driver/run_stage.py advance"
    if stage == "FORM_CRITICS":
        return "new chat with a distinct ACOS_HOST_CONTEXT_ID: python tools/host_driver/run_stage.py form-critic-pass"
    if stage == "PRODUCT_FORM_GATE":
        return "python tools/host_driver/run_stage.py advance"
    if stage == "PRODUCTION" and not impl:
        return "build implementation/, then: python tools/host_driver/run_stage.py advance"
    if stage == "PRODUCTION":
        return "python tools/host_driver/run_stage.py advance"
    if stage == "EVIDENCE" and len(pixels) < 2:
        return "python tools/host_driver/run_stage.py capture"
    if stage == "EVIDENCE":
        return "python tools/host_driver/run_stage.py advance"
    if stage == "CRITICS" and not critics["ok"]:
        return "write critics/*.yaml from rendered pixels, then: python tools/host_driver/run_stage.py advance"
    if stage == "CRITICS":
        return "python tools/host_driver/run_stage.py advance"
    if stage == "QUALITY_GATE" and not independence["ok"]:
        return (
            "new chat with a distinct ACOS_HOST_CONTEXT_ID: "
            "python tools/host_driver/run_stage.py critic-pass"
        )
    if stage == "QUALITY_GATE" and ship_allowed:
        return "python tools/host_driver/run_stage.py advance"
    if stage == "QUALITY_GATE":
        return "write gate/quality_gate.yaml, then: python tools/host_driver/run_stage.py advance"
    return "python tools/host_driver/run_stage.py status"


def mechanical_gate_report(audit: dict[str, Any]) -> dict[str, Any]:
    """Conductor may only emit BLOCKED. APPROVED must come from the quality-gate skill."""
    reasons = list(audit.get("blockers") or ["required evidence or independence missing"])
    return {
        "gate_report": {
            "status": "BLOCKED_INSUFFICIENT_EVIDENCE",
            "producer": "host_mechanical_audit",
            "source": "host_mechanical_audit",
            "note": "Conductor block only. This is not skill execution proof.",
            "independence": audit.get("independence", {}).get("independent_host_context") or "UNVERIFIED",
            "decisions": {
                "evidence_blocker_triggered": True,
                "evidence_blocker_ids": ["EB-01"],
                "hard_reject_triggered": False,
                "hard_reject_ids": [],
            },
            "evidence_blockers": [{"id": "EB-01", "triggered": True, "reason": reason} for reason in reasons],
            "hard_rejects": [],
            "evidence": list(audit.get("pixel_evidence") or []) + list(audit.get("critic_files") or []),
        }
    }
