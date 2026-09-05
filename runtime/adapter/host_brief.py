"""Emit a host-consumable brief: Phase F IDs + native skill names + gate lock."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from runtime.adapter.native import describe_skill
from runtime.adapter.packet import build_adapter_packet
from runtime.common.registry_loader import skill_name_map
from runtime.host.artifact_contract import is_flagship
from runtime.host.skill_execution import binding_for

REPO = Path(__file__).resolve().parent.parent.parent
HOST_DIR = REPO / "runtime" / "host"
BRIEF_MD = HOST_DIR / "CURRENT_HOST_BRIEF.md"
BRIEF_YAML = HOST_DIR / "CURRENT_HOST_BRIEF.yaml"

CREATIVE_STAGES = {"REFERENCE_ANALYSIS", "CREATIVE_DIRECTION", "DESIGN_EXPERIENCE"}
PRODUCTION_STAGES = {"PRODUCTION", "SPECIALIST_ROUTING"}
CRITIC_STAGES = {"INDEPENDENT_CRITICS"}
GATE_STAGES = {"QUALITY_GATE", "MEMORY_CANDIDATES"}


def _rows(skill_ids: list[str], activations: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for skill_id in skill_ids:
        row = {**describe_skill(skill_id), **binding_for(skill_id)}
        row["activation_reason"] = activations.get(skill_id, {}).get("activation_reason", "")
        row["stage"] = activations.get(skill_id, {}).get("stage", "")
        rows.append(row)
    return rows


def _ids_for_stages(planned: list[str], activations: dict[str, dict[str, Any]], stages: set[str]) -> list[str]:
    return [sid for sid in planned if activations.get(sid, {}).get("stage") in stages]


def select_invoke_ids(
    planned: list[str],
    activations: dict[str, dict[str, Any]],
    *,
    workflow_stage: str,
    design_gate: str,
) -> tuple[list[str], str]:
    if workflow_stage in {"SHIP", "REJECTED"}:
        return [], workflow_stage.lower()
    if workflow_stage == "WAITING_BLENDER":
        return [], "waiting_blender"
    if workflow_stage in {"INTAKE", "CREATIVE", "DESIGN_GATE"} or (
        design_gate == "PENDING" and workflow_stage not in {"PRODUCTION", "EVIDENCE", "CRITICS", "QUALITY_GATE"}
    ):
        return _ids_for_stages(planned, activations, CREATIVE_STAGES), "creative_and_design_gate"
    if workflow_stage == "PRODUCTION":
        return _ids_for_stages(planned, activations, PRODUCTION_STAGES), "specialist_production"
    if workflow_stage == "EVIDENCE":
        return [], "browser_evidence"
    if workflow_stage == "CRITICS":
        return _ids_for_stages(planned, activations, CRITIC_STAGES), "independent_critics"
    if workflow_stage == "QUALITY_GATE":
        return _ids_for_stages(planned, activations, GATE_STAGES), "quality_gate"
    if design_gate == "APPROVED":
        return _ids_for_stages(planned, activations, PRODUCTION_STAGES), "specialist_production"
    return _ids_for_stages(planned, activations, CREATIVE_STAGES), "creative_and_design_gate"


def build_host_brief(
    intake: dict[str, Any],
    routing: dict[str, Any],
    *,
    execution_state: dict[str, Any] | None = None,
    adapter_target: str = "cursor",
    project_dir: str | None = None,
) -> dict[str, Any]:
    packet = build_adapter_packet(
        intake, routing, execution_state=execution_state, adapter_target=adapter_target
    )
    activations = {a["skill_id"]: a for a in routing.get("skill_activations", []) if isinstance(a, dict)}
    planned = list(packet["routing"]["planned_skill_ids"])
    workflow_stage = str((execution_state or {}).get("current_stage") or "CREATIVE")
    design_gate = str(packet["routing"]["design_gate_state"] or "PENDING")
    invoke_ids, focus = select_invoke_ids(
        planned, activations, workflow_stage=workflow_stage, design_gate=design_gate
    )
    locked = [sid for sid in planned if sid not in invoke_ids]
    names = skill_name_map()
    do_not_invoke = [name for sid, name in sorted(names.items()) if sid not in invoke_ids]

    brief = {
        "acos_version": "1.2",
        "purpose": "host_skill_activation_packet",
        "adapter_target": adapter_target,
        "task_id": intake.get("task_id"),
        "routing_id": routing.get("routing_id"),
        "workflow_stage": workflow_stage,
        "design_gate_state": design_gate,
        "current_workflow_focus": focus,
        "project_dir": project_dir,
        "invoke_now": _rows(invoke_ids, activations),
        "planned_locked_until_current_stage": _rows(locked, activations),
        "do_not_invoke": do_not_invoke,
        "rules": [
            "Availability is not activation.",
            "Invoke only invoke_now skills. Read each listed SKILL.md (L2) before producing that stage.",
            "Do not Agent-Decide or slash-activate the rest of the discovered catalog.",
            "Critics and quality gate are a later stage — do not run them during creative or production.",
            "If design_gate_state is not APPROVED, do not implement frontend/Three.js/GSAP/Blender.",
            "Write artifacts under project_dir. Copy skill_id + skill_md_sha256 from invoke_now. Fill procedure_evidence for every required_procedure key. A boolean or producer name is not proof.",
            "After artifacts exist, run: python tools/host_driver/run_stage.py advance",
        ],
    }
    if is_flagship(intake.get("task_signals")):
        brief["rules"].extend(
            [
                "Flagship lock: Blender authors the hero asset. Do not skip it because a primitive is easier.",
                "Flagship lock: load the exported GLB in Three.js. Lathe/cube/model-viewer is not complete.",
                "Flagship lock: if Blender MCP/app is down, tell the user, wait, confirm after connect, then start. Never skip.",
                "Contract: docs/FLAGSHIP_PREMIUM_WORKFLOW.md",
            ]
        )
    return brief


def render_host_brief_md(brief: dict[str, Any]) -> str:
    lines = [
        "# ACOS Host Brief",
        "",
        "This file is the active packet for Cursor, Claude Code, and Codex.",
        "Do not treat the Skills slash catalog as permission to load every skill.",
        "",
        f"- task: `{brief.get('task_id')}`",
        f"- routing: `{brief.get('routing_id')}`",
        f"- stage: **{brief.get('workflow_stage')}**",
        f"- design_gate: **{brief.get('design_gate_state')}**",
        f"- focus: `{brief.get('current_workflow_focus')}`",
        f"- host: `{brief.get('adapter_target')}`",
        f"- project: `{brief.get('project_dir')}`",
        "",
        "## Invoke now",
        "",
    ]
    invoke_now = brief.get("invoke_now") or []
    if not invoke_now:
        lines.append("_No skills this stage — follow CURRENT_HOST_TODO.md (evidence / tools)._")
        lines.append("")
    for row in invoke_now:
        lines.append(
            f"- `{row.get('invoke')}` (`{row.get('skill_id')}`) — {row.get('skill_path')} — sha256 `{row.get('skill_md_sha256') or 'unbound'}` — {row.get('activation_reason')}"
        )
        required = row.get("required_procedure") or []
        if required:
            lines.append(f"  procedure_evidence required: {', '.join(required)}")
    lines.extend(["", "## Locked this stage", ""])
    locked = brief.get("planned_locked_until_current_stage") or []
    if not locked:
        lines.append("_None._")
        lines.append("")
    for row in locked:
        lines.append(
            f"- `{row.get('invoke')}` (`{row.get('skill_id')}`) — stage `{row.get('stage')}`"
        )
    lines.extend(["", "## Do not invoke", "", "Every other discovered project skill.", ""])
    lines.extend(["", "## Rules", ""])
    for rule in brief.get("rules") or []:
        lines.append(f"- {rule}")
    lines.append("")
    return "\n".join(lines)


def write_host_brief(brief: dict[str, Any], *, host_dir: Path | None = None) -> dict[str, Path]:
    directory = host_dir or HOST_DIR
    directory.mkdir(parents=True, exist_ok=True)
    md_path = directory / "CURRENT_HOST_BRIEF.md"
    yaml_path = directory / "CURRENT_HOST_BRIEF.yaml"
    md_path.write_text(render_host_brief_md(brief), encoding="utf-8")
    yaml_path.write_text(yaml.dump(brief, sort_keys=False), encoding="utf-8")
    return {"md": md_path, "yaml": yaml_path}
