#!/usr/bin/env python3
"""ACOS host stage loop for Cursor / Claude Code / Codex.

This is a Phase F caller, not a second router.
"""

from __future__ import annotations

import argparse
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

from runtime.adapter.host_brief import HOST_DIR, build_host_brief, write_host_brief
from runtime.host.artifact_contract import (
    CRITIC_FILES,
    has_implementation,
    is_flagship,
    load_yaml,
    pixel_evidence,
    validate_critic_artifacts,
    validate_flagship_evidence,
    validate_flagship_production,
)
from runtime.host.audit import audit_session, ensure_roles, mechanical_gate_report
from runtime.host.exposure import ensure_native_skill_exposure
from runtime.host.independence import (
    classify_host_context,
    host_context_identity,
    implementation_fingerprint,
)
from runtime.host.product_form import (
    evaluate_product_form_gate,
    next_stage_after_design_gate,
    requires_industrial_form,
    validate_clay_evidence,
    validate_form_critic,
    validate_form_model,
    validate_product_design,
)
from runtime.host.visual_class import validate_lookdev_evidence, validate_visual_class
from runtime.host.capabilities import (
    USER_WAIT_MESSAGE,
    blender_readiness,
    host_capabilities,
    write_mcp_stamp,
)
from runtime.host.design_gate import evaluate_host_design_gate
from runtime.host.ops import run_capture, start_serve
from runtime.host.prompt_intake import intake_from_prompt
from runtime.intake.validate import validate_intake
from runtime.routing.engine import route_task, validate_routing_decision
from runtime.state.execution import append_event, create_execution_state, persist_state
from runtime.state.transitions import bind_routing_to_execution, set_design_gate_state, unlock_planned_skills

SESSION = HOST_DIR / "CURRENT_SESSION.json"


def _dump(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.suffix == ".json":
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    else:
        path.write_text(yaml.dump(data, sort_keys=False), encoding="utf-8")


def _load_session() -> dict[str, Any]:
    if not SESSION.is_file():
        raise SystemExit("No active host session. Run: python tools/host_driver/run_stage.py init --prompt \"...\"")
    return json.loads(SESSION.read_text(encoding="utf-8"))


def _write_todo(session: dict[str, Any], brief: dict[str, Any], extra: list[str] | None = None) -> Path:
    project = session["project_dir"]
    stage = session["state"]["current_stage"]
    lines = [
        "# ACOS Host TODO",
        "",
        f"Stage: **{stage}**",
        f"Project: `{project}`",
        "",
        "1. Read `runtime/host/CURRENT_HOST_BRIEF.md`.",
        "2. For every **Invoke now** skill: read that `SKILL.md`, then write its artifact under the project dir.",
        "3. Do not implement production until Design Gate is APPROVED.",
        "4. When this stage's artifacts exist, run:",
        "",
        "```text",
        "python tools/host_driver/run_stage.py advance",
        "```",
        "",
        "## This stage expects",
        "",
    ]
    if stage == "WAITING_BLENDER":
        lines.extend(
            [
                "- STOP. Tell the user: Blender MCP/app band hai. Skip nahi hoga.",
                "- Do not start creative or production. Do not model a lathe/cube instead.",
                "- After the user connects Blender + MCP, verify with the Blender MCP `get_addon_status` tool.",
                "- Then run: `python tools/host_driver/run_stage.py confirm-blender --mcp-live`",
                "- Only after that confirmation may the workflow start.",
                "",
            ]
        )
    elif stage in {"INTAKE", "CREATIVE", "DESIGN_GATE"}:
        lines.extend(
            [
                "- `direction/creative_direction.yaml` (if ACOS-01 planned)",
                "- `direction/anti_generic_review.yaml` (if ACOS-03 planned)",
                "- `direction/art_direction.yaml` (if ACOS-04 planned)",
                "- `direction/experience_direction.yaml` (if ACOS-05 planned)",
                "- Each file must copy `skill_id` + `skill_md_sha256` from the brief and fill `procedure_evidence`.",
                "- `skill_procedure_executed: true` or a producer name is not proof.",
                "",
            ]
        )
    elif stage == "PRODUCT_DESIGN":
        lines.extend(
            [
                "- Invoke `/acos-industrial-product-designer` only.",
                "- Write `direction/product_design.yaml` and `direction/form_specification.yaml`.",
                "- Adjectives are not a spec. Name parts, envelope, and at least two form directions.",
                "- Do not model, lookdev, export GLB, or build the website.",
                "",
            ]
        )
    elif stage == "FORM_AUTHORING":
        lines.extend(
            [
                "- Invoke `/acos-product-form-modeler` plus listed Blender director/modeler/hard-surface skills.",
                "- Clay only. Neutral grey. No beauty lookdev. No production GLB. No `implementation/`.",
                "- Write `direction/form_model.yaml` and `evidence/form-clay/{front,profile,rear,front34,rear34,proportion}.png`.",
                "- Add `joint.png` if mechanics are not none. Add `top.png` if the envelope needs plan.",
                "",
            ]
        )
    elif stage == "FORM_EVIDENCE":
        lines.extend(
            [
                "- No skills this stage. Confirm the clay set exists under `evidence/form-clay/`.",
                "- Beauty / lookdev / crushed studio frames are not clay.",
                "- Then: `python tools/host_driver/run_stage.py advance`",
                "",
            ]
        )
    elif stage == "FORM_CRITICS":
        lines.extend(
            [
                "- Independent form critic only. New chat with a distinct `ACOS_HOST_CONTEXT_ID`.",
                "- Open the pass: `python tools/host_driver/run_stage.py form-critic-pass`",
                "- Invoke `/acos-industrial-design-critic`. Inspect clay pixels. Write `critics/industrial_design.yaml`.",
                "- Do not edit meshes or implementation. Do not run ship critics or quality gate.",
                "",
            ]
        )
    elif stage == "PRODUCT_FORM_GATE":
        lines.extend(
            [
                "- No skills. Run `python tools/host_driver/run_stage.py advance`.",
                "- Product Form Gate is not Quality Gate and cannot SHIP.",
                "- APPROVED unlocks lookdev / production GLB / web. REJECTED returns to form.",
                "",
            ]
        )
    elif stage == "PRODUCTION":
        lines.extend(
            [
                "- Read unlocked production / cinematic / motion skills from the brief.",
                "- Build the real experience under `implementation/`.",
                "- Do not mark quality. Do not self-critique.",
                "",
            ]
        )
        if is_flagship((session.get("intake") or {}).get("task_signals")):
            lines.extend(
                [
                    "- Flagship lock: Blender must author the hero. Export GLB/GLTF under `implementation/`.",
                    "- Write `direction/blender_export.yaml` with `blender_used: true`.",
                    "- Execute materials / lighting / camera skills. A lathe or cube is not complete.",
                    "- Flagship lock: write director / modeler / prop-artist / materials / lookdev artifacts with live hashes. Export YAML is not enough.",
                    "- Flagship lock: write at least two lookdev PNGs under evidence/lookdev/ from Blender viewport / browser. YAML is not lookdev.",
                    "- One lookdev shot must be a full hero or full scene. A surface macro is a fail.",
                    "- Do not export a sphere/cylinder/torus/plane kitbash as the hero. Physical products need /hard-surface.",
                    "- Industrial-form tasks: Product Form Gate must already be APPROVED. Do not start lookdev before that.",
                    "- If a mood reference exists, the render class must match (lit water/sky vs night-silhouette is a fail).",
                    "",
                ]
            )
    elif stage == "EVIDENCE":
        lines.extend(
            [
                "- Do not capture `file://` for ES-module pages.",
                "- Run: `python tools/host_driver/run_stage.py capture`",
                "- Confirm at least two PNG/WebP captures under `evidence/`.",
                "- If visual class fails (crushed/dark vs a lit reference), go back to production lookdev. Do not advance to critics.",
                "",
            ]
        )
    elif stage == "CRITICS":
        lines.extend(
            [
                "- Run only critic skills from the brief.",
                "- Inspect rendered evidence, not the producer's YAML.",
                "- Write `critics/*.yaml` with `inspected_rendered_output: true` and `findings:`.",
                "",
            ]
        )
    elif stage == "QUALITY_GATE":
        lines.extend(
            [
                "- Run `/acos-quality-gate` as a gate, not a creator.",
                "- Write `gate/quality_gate.yaml` with APPROVED | REJECTED | BLOCKED_INSUFFICIENT_EVIDENCE.",
                "- This chat cannot APPROVE if it produced the implementation.",
                "- Independent pass: new chat with a distinct ACOS_HOST_CONTEXT_ID, then `python tools/host_driver/run_stage.py critic-pass`",
                "- `--attest-independent` is a claim only. SHIP requires independent_host_context: DISTINCT.",
                "",
            ]
        )
    elif stage == "SHIP":
        lines.append("Release candidate. Do not keep producing unless a new request arrives.")
    if extra:
        lines.extend(["", "## Last advance", ""] + [f"- {item}" for item in extra])
    path = HOST_DIR / "CURRENT_HOST_TODO.md"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def _refresh_brief(session: dict[str, Any]) -> dict[str, Any]:
    brief = build_host_brief(
        session["intake"],
        session["routing"],
        execution_state=session["state"],
        adapter_target=session.get("adapter_target", "cursor"),
        project_dir=session["project_dir"],
    )
    write_host_brief(brief)
    _write_todo(session, brief)
    return brief


def _save(session: dict[str, Any]) -> None:
    ensure_roles(session)
    persist_state(session["state"], HOST_DIR / "state")
    _dump(SESSION, session)
    _dump(HOST_DIR / "CURRENT_INTAKE.json", session["intake"])
    _dump(HOST_DIR / "CURRENT_ROUTING.json", session["routing"])
    _refresh_brief(session)


def _placeholder_routing(task_id: str) -> dict[str, Any]:
    return {
        "routing_id": f"pending-{task_id}",
        "task_id": task_id,
        "stage": "ROUTING",
        "planned_skill_ids": [],
        "executable_active_skill_ids": [],
        "activated_skill_ids": [],
        "skill_activations": [],
        "rejected_candidate_skill_ids": [],
        "required_tool_families": ["blender"],
        "required_critic_ids": [],
        "quality_gate_required": True,
        "decision_reasons": ["Waiting for Blender MCP/app. Do not skip."],
        "evidence_refs": [],
        "memory_refs": [],
        "capability_constraints": {"blocked_tools": ["blender"]},
        "fallbacks": [],
        "design_gate_state": "PENDING",
        "status": "WAITING_BLENDER",
    }


def _start_routed_session(intake: dict[str, Any], routing: dict[str, Any], target: str) -> dict[str, Any]:
    errors = validate_routing_decision(routing)
    if errors:
        raise SystemExit("Routing invalid: " + "; ".join(errors))
    if routing.get("status") == "ROUTING_BLOCKED_CAPABILITY":
        raise SystemExit("Routing blocked: " + "; ".join(routing.get("decision_reasons") or ["capability"]))
    state = create_execution_state(intake["task_id"])
    bind_routing_to_execution(state, routing)
    append_event(state, "TASK_NORMALIZED", intake["task_id"])
    append_event(state, "ROUTING_CREATED", routing["routing_id"])
    if state["gate_states"].get("design_gate") == "PENDING":
        state["current_stage"] = "CREATIVE"
    else:
        state["current_stage"] = "PRODUCTION"
        set_design_gate_state(state, "NOT_APPLICABLE")
        unlock_planned_skills(state, routing)
    project = (HOST_DIR / "projects" / intake["task_id"]).resolve()
    for sub in ("direction", "implementation", "evidence", "evidence/form-clay", "critics", "gate"):
        (project / sub).mkdir(parents=True, exist_ok=True)
    (project / "request.md").write_text(intake.get("request", "") + "\n", encoding="utf-8")
    return {
        "adapter_target": target,
        "project_dir": str(project.relative_to(REPO)).replace("\\", "/"),
        "intake": intake,
        "routing": routing,
        "state": state,
        "roles": _new_roles(intake["task_id"]),
    }


def _new_roles(task_id: str) -> dict[str, Any]:
    context = host_context_identity()
    return {
        "producer_session_id": f"{task_id}-{uuid.uuid4().hex[:8]}",
        "producer_host_context_id": context["id"],
        "producer_host_context_source": context["source"],
        "critic_pass_id": None,
        "critic_host_context_id": None,
        "form_critic_pass_id": None,
        "form_critic_host_context_id": None,
        "independent_attestation": False,
        "independence_claim": "none",
        "independent_host_context": "UNVERIFIED",
        "critic_frozen_implementation_sha256": None,
    }


def cmd_init(args: argparse.Namespace) -> int:
    exposure = ensure_native_skill_exposure()
    print(f"native_skills: synced={exposure['sync']} validated={exposure['validated']}")
    if args.prompt:
        intake = intake_from_prompt(args.prompt)
    elif args.intake:
        raw = Path(args.intake).read_text(encoding="utf-8")
        intake = json.loads(raw) if args.intake.endswith(".json") else yaml.safe_load(raw)
    else:
        raise SystemExit("Provide --prompt or --intake")
    validate_intake(intake)
    if is_flagship(intake.get("task_signals")) and not blender_readiness()["ready"]:
        state = create_execution_state(intake["task_id"])
        state["current_stage"] = "WAITING_BLENDER"
        state["blocked_reasons"] = [USER_WAIT_MESSAGE]
        project = (HOST_DIR / "projects" / intake["task_id"]).resolve()
        for sub in ("direction", "implementation", "evidence", "critics", "gate"):
            (project / sub).mkdir(parents=True, exist_ok=True)
        (project / "request.md").write_text(intake.get("request", "") + "\n", encoding="utf-8")
        session = {
            "adapter_target": args.target,
            "project_dir": str(project.relative_to(REPO)).replace("\\", "/"),
            "intake": intake,
            "routing": _placeholder_routing(intake["task_id"]),
            "state": state,
            "roles": _new_roles(intake["task_id"]),
        }
        _save(session)
        print(f"task: {intake['task_id']}")
        print("stage: WAITING_BLENDER")
        print(USER_WAIT_MESSAGE)
        print("next: python tools/host_driver/run_stage.py confirm-blender --mcp-live")
        return 0
    routing = route_task(intake)
    session = _start_routed_session(intake, routing, args.target)
    _save(session)
    print(f"task: {intake['task_id']}")
    print(f"stage: {session['state']['current_stage']}")
    print(f"design_gate: {session['state']['gate_states']['design_gate']}")
    print(f"project: {session['project_dir']}")
    print("brief: runtime/host/CURRENT_HOST_BRIEF.md")
    print("todo: runtime/host/CURRENT_HOST_TODO.md")
    return 0


def cmd_status(_: argparse.Namespace) -> int:
    session = _load_session()
    state = session["state"]
    brief = _refresh_brief(session)
    audit = audit_session(session, REPO / session["project_dir"])
    print(yaml.dump(
        {
            "task_id": session["intake"]["task_id"],
            "stage": state["current_stage"],
            "design_gate": state["gate_states"].get("design_gate"),
            "product_form_gate": state["gate_states"].get("product_form_gate"),
            "quality_gate": state["gate_states"].get("quality_gate"),
            "project_dir": session["project_dir"],
            "invoke_now": [r.get("invoke") for r in brief.get("invoke_now") or []],
            "ship_allowed": audit["ship_allowed"],
            "next_command": audit["next_command"],
        },
        sort_keys=False,
    ))
    return 0


def cmd_check(_: argparse.Namespace) -> int:
    session = _load_session()
    audit = audit_session(session, REPO / session["project_dir"])
    _save(session)
    print(yaml.dump(audit, sort_keys=False))
    if session["state"]["current_stage"] == "SHIP" and not audit["ship_allowed"]:
        return 1
    return 0


def cmd_advance(_: argparse.Namespace) -> int:
    session = _load_session()
    state = session["state"]
    routing = session["routing"]
    planned = list(state.get("planned_skill_ids") or [])
    project = REPO / session["project_dir"]
    stage = state["current_stage"]
    notes: list[str] = []

    if stage == "WAITING_BLENDER":
        notes.append(USER_WAIT_MESSAGE)
        notes.append("Do not skip. After Blender MCP is connected: python tools/host_driver/run_stage.py confirm-blender --mcp-live")
    elif stage in {"INTAKE", "CREATIVE", "DESIGN_GATE"}:
        gate = evaluate_host_design_gate(project, planned, routing.get("routing_id"))
        _dump(project / "gate" / "design_gate.yaml", gate)
        if gate["status"] == "APPROVED":
            set_design_gate_state(state, "APPROVED")
            unlock_planned_skills(state, routing)
            signals = session["intake"].get("task_signals")
            request = session["intake"].get("request") or ""
            nxt = next_stage_after_design_gate(signals, request)
            state["current_stage"] = nxt
            if nxt == "PRODUCT_DESIGN":
                state["gate_states"]["product_form_gate"] = "PENDING"
                notes.append("Design Gate APPROVED — industrial form path: write the product-design spec next")
            else:
                state["gate_states"]["product_form_gate"] = "NOT_APPLICABLE"
                notes.append("Design Gate APPROVED — production skills unlocked")
            append_event(state, "DESIGN_GATE_APPROVED", routing.get("routing_id") or "")
        elif gate["status"] == "REJECTED":
            set_design_gate_state(state, "REJECTED")
            state["current_stage"] = "CREATIVE"
            notes.extend(gate.get("failures") or ["Design Gate REJECTED"])
        else:
            set_design_gate_state(state, "BLOCKED_INSUFFICIENT_EVIDENCE")
            state["current_stage"] = "CREATIVE"
            notes.extend([f"missing {m}" for m in gate.get("missing_artifacts") or []])
            notes.extend(gate.get("failures") or [])
    elif stage == "PRODUCT_DESIGN":
        notes.extend(_advance_product_design(session, project))
    elif stage == "FORM_AUTHORING":
        notes.extend(_advance_form_authoring(session, project))
    elif stage == "FORM_EVIDENCE":
        notes.extend(_advance_form_evidence(session, project))
    elif stage == "FORM_CRITICS":
        notes.extend(_advance_form_critics(session, project))
    elif stage == "PRODUCT_FORM_GATE":
        notes.extend(_advance_product_form_gate(session, project))
    elif stage == "PRODUCTION":
        if not has_implementation(project):
            notes.append("implementation missing — expected implementation/index.html (or src/main)")
        else:
            flagship = validate_flagship_production(
                project,
                planned,
                session["intake"].get("task_signals"),
                session["intake"].get("request") or "",
            )
            if not flagship["ok"]:
                notes.extend([f"missing {m}" for m in flagship["missing"]])
                notes.extend(flagship["invalid"])
            else:
                lookdev = validate_lookdev_evidence(project, session["intake"].get("task_signals"))
                if not lookdev["ok"]:
                    notes.extend(lookdev["issues"])
                else:
                    state["current_stage"] = "EVIDENCE"
                    session["roles"] = ensure_roles(session)
                    session["roles"]["producer_implementation_sha256"] = implementation_fingerprint(project)
                    notes.append("Implementation + lookdev present — capture real browser evidence next")
    elif stage == "EVIDENCE":
        pixels = pixel_evidence(project)
        beats = validate_flagship_evidence(project, session["intake"].get("task_signals"), session["intake"].get("request") or "")
        if len(pixels) < 2:
            notes.append("Need at least two rendered images under evidence/ — run: python tools/host_driver/run_stage.py capture")
        elif not beats["ok"]:
            notes.extend(beats["missing"] + beats["invalid"])
        else:
            visual = validate_visual_class(project, session["intake"].get("task_signals"))
            if not visual["ok"]:
                state["current_stage"] = "PRODUCTION"
                notes.append("Visual class failed — back to production. GLB/YAML is not a premium result.")
                notes.extend(visual["issues"])
            else:
                state["current_stage"] = "CRITICS"
                notes.append(f"Evidence recorded ({len(pixels)} pixels) — independent critics next")
    elif stage == "CRITICS":
        critics = validate_critic_artifacts(project, planned)
        if not critics["ok"]:
            notes.extend(critics["missing"] + critics["invalid"])
        else:
            state["current_stage"] = "QUALITY_GATE"
            notes.append("Critic reports present — run acos-quality-gate")
    elif stage == "QUALITY_GATE":
            notes.extend(_apply_quality_gate(session, project))
    elif stage == "SHIP":
        notes.append("Already SHIP")
    else:
        notes.append(f"Unknown stage {stage}")

    _save(session)
    print(f"stage: {session['state']['current_stage']}")
    print(f"design_gate: {session['state']['gate_states'].get('design_gate')}")
    print(f"product_form_gate: {session['state']['gate_states'].get('product_form_gate')}")
    for note in notes:
        print(f"- {note}")
    return 0


def _advance_product_design(session: dict[str, Any], project: Path) -> list[str]:
    result = validate_product_design(project)
    if not result["ok"]:
        return [f"missing {m}" for m in result["missing"]] + result["invalid"]
    session["state"]["current_stage"] = "FORM_AUTHORING"
    return ["Product design spec accepted — clay form next"]


def _advance_form_authoring(session: dict[str, Any], project: Path) -> list[str]:
    result = validate_form_model(project)
    if not result["ok"]:
        return [f"missing {m}" for m in result["missing"]] + result["invalid"]
    session["state"]["current_stage"] = "FORM_EVIDENCE"
    return ["Form model recorded — confirm clay multi-view next"]


def _advance_form_evidence(session: dict[str, Any], project: Path) -> list[str]:
    spec = load_yaml(project / "direction" / "form_specification.yaml") if (project / "direction" / "form_specification.yaml").is_file() else {}
    clay = validate_clay_evidence(project, spec)
    if not clay["ok"]:
        return clay["issues"]
    session["state"]["current_stage"] = "FORM_CRITICS"
    return [
        "Clay set present — independent form critic next",
        "New chat with a distinct ACOS_HOST_CONTEXT_ID, then: python tools/host_driver/run_stage.py form-critic-pass",
    ]


def _advance_form_critics(session: dict[str, Any], project: Path) -> list[str]:
    roles = ensure_roles(session)
    critic = validate_form_critic(
        project,
        pass_id=roles.get("form_critic_pass_id"),
        roles=roles,
    )
    if not critic["ok"]:
        notes = [f"missing {m}" for m in critic.get("missing") or []] + (critic.get("invalid") or [])
        if any("industrial_design.yaml" in item for item in notes):
            notes.append(
                "Open an independent form pass: python tools/host_driver/run_stage.py form-critic-pass"
            )
        return notes
    session["state"]["current_stage"] = "PRODUCT_FORM_GATE"
    return ["Form critic present — Product Form Gate next"]


def _advance_product_form_gate(session: dict[str, Any], project: Path) -> list[str]:
    roles = ensure_roles(session)
    report = evaluate_product_form_gate(
        project,
        signals=session["intake"].get("task_signals"),
        request=session["intake"].get("request") or "",
        pass_id=roles.get("form_critic_pass_id"),
        roles=roles,
    )
    _dump(project / "gate" / "product_form_gate.yaml", report)
    status = str(report.get("status") or "").upper()
    state = session["state"]
    issues = list((report.get("form_gate") or {}).get("issues") or [])
    if status == "APPROVED":
        state["gate_states"]["product_form_gate"] = "APPROVED"
        state["current_stage"] = "PRODUCTION"
        append_event(state, "GATE_APPROVED", "product_form_gate")
        return ["Product Form Gate APPROVED — lookdev, production GLB, and web unlocked"]
    if status == "REJECTED":
        state["gate_states"]["product_form_gate"] = "REJECTED"
        blob = " ".join(issues).lower()
        if any(key in blob for key in ("product_design", "form_specification", "part_architecture", "archetype", "form direction", "envelope")):
            state["current_stage"] = "PRODUCT_DESIGN"
            dest = "product design spec"
        else:
            state["current_stage"] = "FORM_AUTHORING"
            dest = "form authoring"
        append_event(state, "GATE_REJECTED", "product_form_gate")
        return [f"Product Form Gate REJECTED — return to {dest}"] + issues[:8]
    state["gate_states"]["product_form_gate"] = "BLOCKED_INSUFFICIENT_EVIDENCE"
    blob = " ".join(issues).lower()
    if any("form-clay" in item or "clay" in item for item in issues):
        state["current_stage"] = "FORM_EVIDENCE"
    elif any("industrial_design" in item or "form critic" in item for item in issues):
        state["current_stage"] = "FORM_CRITICS"
    notes = ["Product Form Gate BLOCKED_INSUFFICIENT_EVIDENCE"] + issues[:8]
    if "form critic" in blob or "industrial_design" in blob:
        notes.append("python tools/host_driver/run_stage.py form-critic-pass")
    return notes


def _apply_quality_gate(session: dict[str, Any], project: Path) -> list[str]:
    state = session["state"]
    audit = audit_session(session, project)
    gate_path = project / "gate" / "quality_gate.yaml"
    report = load_yaml(gate_path) if gate_path.is_file() else {}
    body = report.get("gate_report") or report
    status = str(body.get("status") or "").upper()
    notes: list[str] = []

    if status == "APPROVED" and not audit["ship_allowed"]:
        _dump(gate_path, mechanical_gate_report(audit))
        status = "BLOCKED_INSUFFICIENT_EVIDENCE"
        notes.append("Overrode illegal APPROVED — evidence or critic independence is insufficient")
        notes.extend(audit["blockers"])

    if status == "APPROVED":
        state["gate_states"]["quality_gate"] = "APPROVED"
        state["current_stage"] = "SHIP"
        state["status"] = "COMPLETE"
        append_event(state, "GATE_APPROVED", "quality_gate")
        notes.append("Quality Gate APPROVED — SHIP")
        return notes

    if status == "REJECTED":
        state["gate_states"]["quality_gate"] = "REJECTED"
        state["current_stage"] = "PRODUCTION"
        append_event(state, "GATE_REJECTED", "quality_gate")
        notes.append("REJECTED — correction: return to production with critic findings")
        return notes

    if not gate_path.is_file():
        _dump(gate_path, mechanical_gate_report(audit))
        notes.append("wrote mechanical gate/quality_gate.yaml")
    state["gate_states"]["quality_gate"] = "BLOCKED_INSUFFICIENT_EVIDENCE"
    notes.append("Quality gate BLOCKED_INSUFFICIENT_EVIDENCE")
    notes.extend(audit["blockers"][:6])
    notes.append(audit["next_command"])
    return notes


def cmd_serve(args: argparse.Namespace) -> int:
    session = _load_session()
    served = start_serve(REPO / session["project_dir"], port=args.port)
    print(yaml.dump(served, sort_keys=False))
    return 0


def cmd_capture(args: argparse.Namespace) -> int:
    session = _load_session()
    project = REPO / session["project_dir"]
    if not has_implementation(project):
        raise SystemExit("implementation missing — cannot capture")
    result = run_capture(project, port=args.port)
    pixels = pixel_evidence(project)
    print(yaml.dump({"capture": result, "pixel_count": len(pixels), "pixels": pixels[:12]}, sort_keys=False))
    return 0


def cmd_critic_pass(args: argparse.Namespace) -> int:
    session = _load_session()
    project = REPO / session["project_dir"]
    if not has_implementation(project):
        raise SystemExit("implementation missing — cannot open a critic pass")
    if len(pixel_evidence(project)) < 2:
        raise SystemExit("capture rendered evidence first: python tools/host_driver/run_stage.py capture")

    roles = ensure_roles(session)
    pass_id = uuid.uuid4().hex
    critic_context = host_context_identity()
    roles["critic_pass_id"] = pass_id
    roles["critic_host_context_id"] = critic_context["id"]
    roles["critic_host_context_source"] = critic_context["source"]
    roles["independence_claim"] = "operator_attested" if args.attest_independent else "none"
    roles["independent_attestation"] = False
    roles["independent_host_context"] = classify_host_context(
        roles.get("producer_host_context_id"),
        critic_context["id"],
    )
    roles["critic_frozen_implementation_sha256"] = implementation_fingerprint(project)
    roles["critic_pass_opened_at"] = datetime.now(timezone.utc).isoformat()

    superseded = project / "critics" / "_superseded" / pass_id
    superseded.mkdir(parents=True, exist_ok=True)
    planned = list(session["state"].get("planned_skill_ids") or [])
    moved = 0
    for sid, rel in CRITIC_FILES.items():
        if sid not in planned:
            continue
        path = project / rel
        if not path.is_file():
            continue
        data = load_yaml(path)
        if data.get("critic_pass_id") == pass_id:
            continue
        dest = superseded / path.name
        shutil.move(str(path), str(dest))
        moved += 1

    gate_path = project / "gate" / "quality_gate.yaml"
    if gate_path.is_file():
        gate_dest = project / "gate" / "_superseded"
        gate_dest.mkdir(parents=True, exist_ok=True)
        shutil.move(str(gate_path), str(gate_dest / f"quality_gate-{pass_id[:8]}.yaml"))

    session["state"]["current_stage"] = "CRITICS"
    session["state"]["gate_states"]["quality_gate"] = "NOT_EVALUATED"
    _save(session)

    print(yaml.dump(
        {
            "critic_pass_id": pass_id,
            "attested_independent": bool(args.attest_independent),
            "independence_claim": roles["independence_claim"],
            "independent_host_context": roles["independent_host_context"],
            "superseded_critics": moved,
            "stage": "CRITICS",
            "warning": (
                None
                if roles["independent_host_context"] == "DISTINCT"
                else "APPROVE stays locked: independent_host_context is not DISTINCT. "
                "A boolean flag is not proof. Use a new chat with a different ACOS_HOST_CONTEXT_ID."
            ),
        },
        sort_keys=False,
    ))
    if roles["independent_host_context"] == "DISTINCT":
        print("Distinct host context recorded. This chat must not edit implementation/. Inspect pixels only.")
    return 0


def cmd_form_critic_pass(args: argparse.Namespace) -> int:
    session = _load_session()
    project = REPO / session["project_dir"]
    spec_path = project / "direction" / "form_specification.yaml"
    spec = load_yaml(spec_path) if spec_path.is_file() else {}
    clay = validate_clay_evidence(project, spec)
    if not clay["ok"]:
        raise SystemExit("clay evidence incomplete — write evidence/form-clay/ first: " + "; ".join(clay["issues"][:4]))

    roles = ensure_roles(session)
    pass_id = uuid.uuid4().hex
    critic_context = host_context_identity()
    roles["form_critic_pass_id"] = pass_id
    roles["form_critic_host_context_id"] = critic_context["id"]
    roles["form_critic_host_context_source"] = critic_context["source"]
    roles["form_independence_claim"] = "operator_attested" if args.attest_independent else "none"
    form_context = classify_host_context(
        roles.get("producer_host_context_id"),
        critic_context["id"],
    )
    roles["form_independent_host_context"] = form_context
    roles["form_critic_pass_opened_at"] = datetime.now(timezone.utc).isoformat()

    critic_path = project / "critics" / "industrial_design.yaml"
    if critic_path.is_file():
        superseded = project / "critics" / "_superseded" / f"form-{pass_id[:8]}"
        superseded.mkdir(parents=True, exist_ok=True)
        data = load_yaml(critic_path)
        if data.get("form_critic_pass_id") != pass_id:
            shutil.move(str(critic_path), str(superseded / critic_path.name))

    gate_path = project / "gate" / "product_form_gate.yaml"
    if gate_path.is_file():
        dest = project / "gate" / "_superseded"
        dest.mkdir(parents=True, exist_ok=True)
        shutil.move(str(gate_path), str(dest / f"product_form_gate-{pass_id[:8]}.yaml"))

    session["state"]["current_stage"] = "FORM_CRITICS"
    session["state"]["gate_states"]["product_form_gate"] = "PENDING"
    _save(session)

    print(yaml.dump(
        {
            "form_critic_pass_id": pass_id,
            "attested_independent": bool(args.attest_independent),
            "form_independent_host_context": form_context,
            "stage": "FORM_CRITICS",
            "warning": (
                None
                if form_context == "DISTINCT"
                else "Form critic pass stays locked: form context is not DISTINCT. "
                "Use a new chat with a different ACOS_HOST_CONTEXT_ID."
            ),
        },
        sort_keys=False,
    ))
    if form_context == "DISTINCT":
        print("Distinct form critic context recorded. Inspect clay only. Do not edit meshes or implementation/.")
    return 0


def cmd_blender_status(_: argparse.Namespace) -> int:
    ready = blender_readiness()
    print(yaml.dump(ready, sort_keys=False))
    return 0 if ready["ready"] else 2


def cmd_confirm_blender(args: argparse.Namespace) -> int:
    session = _load_session()
    if not is_flagship((session.get("intake") or {}).get("task_signals")):
        raise SystemExit("Active session is not a flagship 3D prompt — Blender confirm is not required.")
    ready = blender_readiness()
    if not args.mcp_live:
        print(yaml.dump({**ready, "action": "still_waiting", "need": "--mcp-live after a live Blender MCP ping"}, sort_keys=False))
        print(USER_WAIT_MESSAGE)
        return 2
    write_mcp_stamp(connected=True, addon_ok=True, source="confirm-blender --mcp-live")
    intake = session["intake"]
    intake["runtime_capabilities"] = {**host_capabilities(), "blender": "AVAILABLE"}
    routing = route_task(intake)
    started = _start_routed_session(intake, routing, session.get("adapter_target", "cursor"))
    started["roles"] = session.get("roles") or started["roles"]
    started["project_dir"] = session["project_dir"]
    _save(started)
    print(yaml.dump(
        {
            "blender_mcp": "connected",
            "confirmed": True,
            "stage": started["state"]["current_stage"],
            "task_id": intake["task_id"],
            "message": "Blender MCP confirm ho gaya. Workflow start.",
        },
        sort_keys=False,
    ))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)

    init = sub.add_parser("init", help="Intake + route + emit first brief")
    init.add_argument("--prompt", help="Project request text")
    init.add_argument("--intake", help="Existing intake JSON/YAML")
    init.add_argument("--target", default="cursor", choices=["cursor", "claude", "codex", "local"])
    init.set_defaults(func=cmd_init)

    status = sub.add_parser("status", help="Show current host session")
    status.set_defaults(func=cmd_status)

    advance = sub.add_parser("advance", help="Validate current stage artifacts and unlock the next brief")
    advance.set_defaults(func=cmd_advance)

    check = sub.add_parser("check", help="Mechanical audit of the active session")
    check.set_defaults(func=cmd_check)

    serve = sub.add_parser("serve", help="Serve implementation/ over HTTP")
    serve.add_argument("--port", type=int, default=8765)
    serve.set_defaults(func=cmd_serve)

    capture = sub.add_parser("capture", help="Serve + Playwright viewport/state capture")
    capture.add_argument("--port", type=int, default=8765)
    capture.set_defaults(func=cmd_capture)

    critic = sub.add_parser("critic-pass", help="Open an independent critic pass (new chat)")
    critic.add_argument(
        "--attest-independent",
        action="store_true",
        help="Operator claim only. Does not prove a different host chat. SHIP requires DISTINCT host context.",
    )
    critic.set_defaults(func=cmd_critic_pass)

    form_critic = sub.add_parser("form-critic-pass", help="Open an independent industrial-design critic pass on clay")
    form_critic.add_argument(
        "--attest-independent",
        action="store_true",
        help="Operator claim only. Form APPROVE still requires DISTINCT host context.",
    )
    form_critic.set_defaults(func=cmd_form_critic_pass)

    blender_status = sub.add_parser("blender-status", help="Show Blender app/MCP readiness")
    blender_status.set_defaults(func=cmd_blender_status)

    confirm = sub.add_parser("confirm-blender", help="Confirm Blender MCP is live, then start a waiting flagship session")
    confirm.add_argument(
        "--mcp-live",
        action="store_true",
        help="Set only after a live Blender MCP ping (get_addon_status) succeeded in this chat.",
    )
    confirm.set_defaults(func=cmd_confirm_blender)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
