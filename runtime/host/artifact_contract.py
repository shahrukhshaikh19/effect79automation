"""Required host artifacts per workflow stage. Presence is not quality."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from runtime.host.independence import classify_host_context, implementation_fingerprint
from runtime.host.craft_lock import (
    validate_brief_honesty,
    validate_craft_artifacts,
    validate_hero_primitives,
)
from runtime.host.skill_execution import (
    validate_artifact_execution,
    validate_contracted_artifacts,
    write_execution_receipt,
)

PIXEL_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".webm", ".mp4"}
SAME_SESSION_INDEPENDENCE = "same_host_session_as_producer"

CREATIVE_FILES = {
    "ACOS-01": "direction/creative_direction.yaml",
    "ACOS-03": "direction/anti_generic_review.yaml",
    "ACOS-04": "direction/art_direction.yaml",
    "ACOS-05": "direction/experience_direction.yaml",
    "ACOS-02": "direction/reference_analysis.yaml",
}
PRODUCTION_MARKERS = (
    "implementation/index.html",
    "implementation/src/main.tsx",
    "implementation/src/main.js",
    "implementation/main.js",
)
CRITIC_FILES = {
    "ACOS-10": "critics/visual_critic.yaml",
    "ACOS-11": "critics/creative_critic.yaml",
    "ACOS-12": "critics/3d_critic.yaml",
}
HERO_ASSET_SUFFIXES = {".glb", ".gltf"}
FLAGSHIP_PRODUCTION_FILES = {
    "EXT-3DWEB-02": "direction/threejs_materials.yaml",
    "EXT-3DWEB-03": "direction/threejs_lighting.yaml",
    "EXT-3DWEB-04": "direction/threejs_camera.yaml",
    "EXT-BLD-12": "direction/blender_export.yaml",
}


def load_yaml(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}


def required_creative_files(planned_ids: list[str]) -> list[str]:
    return [CREATIVE_FILES[sid] for sid in planned_ids if sid in CREATIVE_FILES]


def validate_creative_artifacts(project_dir: Path, planned_ids: list[str]) -> dict[str, Any]:
    creative_ids = [sid for sid in planned_ids if sid in CREATIVE_FILES]
    result = validate_contracted_artifacts(project_dir, creative_ids, write_receipts=True)
    invalid = list(result["invalid"])
    for sid in creative_ids:
        rel = CREATIVE_FILES[sid]
        path = project_dir / rel
        if not path.is_file():
            continue
        data = load_yaml(path)
        if "bm002_direction" in str(data.get("producer", "")) or data.get("decision_provenance") == "hardcoded":
            invalid.append(f"{rel}: runner-authored placeholder, not a skill output")
    return {"missing": result["missing"], "invalid": invalid, "ok": not result["missing"] and not invalid}


def has_implementation(project_dir: Path) -> bool:
    return any((project_dir / rel).is_file() for rel in PRODUCTION_MARKERS)


def is_flagship(signals: dict[str, Any] | None) -> bool:
    data = signals or {}
    return str(data.get("quality_bar") or "") == "flagship" or str(data.get("reconstruction_path") or "") == "blender_authoring"


def hero_assets(project_dir: Path) -> list[str]:
    found: list[str] = []
    for root in (project_dir / "implementation", project_dir / "assets"):
        if not root.is_dir():
            continue
        for path in root.rglob("*"):
            if path.is_file() and path.suffix.lower() in HERO_ASSET_SUFFIXES and path.stat().st_size > 32:
                found.append(str(path.relative_to(project_dir)).replace("\\", "/"))
    return sorted(found)


def validate_flagship_production(
    project_dir: Path,
    planned_ids: list[str],
    signals: dict[str, Any] | None,
    request: str = "",
) -> dict[str, Any]:
    if not is_flagship(signals):
        return {"ok": True, "missing": [], "invalid": []}
    missing: list[str] = []
    invalid: list[str] = []
    assets = hero_assets(project_dir)
    if not assets:
        missing.append("implementation/ hero GLB/GLTF from Blender — lathe/primitive is not a flagship hero")
    export = project_dir / "direction" / "blender_export.yaml"
    if not export.is_file() or export.stat().st_size < 40:
        missing.append("direction/blender_export.yaml")
    else:
        data = load_yaml(export)
        if data.get("blender_used") is not True:
            invalid.append("direction/blender_export.yaml: blender_used must be true")
        producer = str(data.get("producer") or "")
        if producer in {"threejs-core", "gsap-core"} or producer.startswith("threejs"):
            invalid.append("direction/blender_export.yaml: producer must be a Blender/export skill, not threejs-core")
        export_issues = validate_artifact_execution(data, "EXT-BLD-12")
        invalid.extend(export_issues)
        if data.get("blender_used") is True and not export_issues:
            write_execution_receipt(project_dir, "EXT-BLD-12", "direction/blender_export.yaml")
    for sid, rel in FLAGSHIP_PRODUCTION_FILES.items():
        if sid == "EXT-BLD-12":
            continue
        path = project_dir / rel
        if not path.is_file() or path.stat().st_size < 40:
            missing.append(rel)
            continue
        data = load_yaml(path)
        issues = validate_artifact_execution(data, sid)
        invalid.extend(issues)
        if not issues:
            write_execution_receipt(project_dir, sid, rel)
    notes = project_dir / "direction" / "production_notes.yaml"
    if notes.is_file():
        data = load_yaml(notes)
        if data.get("blender_used") is False:
            invalid.append("production_notes: flagship cannot skip Blender for convenience")
    craft = validate_craft_artifacts(project_dir, signals, planned_ids)
    missing.extend(craft["missing"])
    invalid.extend(craft["invalid"])
    invalid.extend(validate_brief_honesty(project_dir))
    if assets:
        invalid.extend(validate_hero_primitives(project_dir))
    from runtime.host.product_form import form_gate_approved, requires_industrial_form

    if requires_industrial_form(signals, request) and not form_gate_approved(project_dir):
        invalid.append(
            "product form gate is not APPROVED — lookdev, production GLB, and web cannot complete"
        )
    return {"missing": missing, "invalid": invalid, "ok": not missing and not invalid}


def validate_flagship_evidence(project_dir: Path, signals: dict[str, Any] | None, request: str = "") -> dict[str, Any]:
    if not is_flagship(signals):
        return {"ok": True, "missing": [], "invalid": []}
    text = request.lower()
    named_beats = sum(word in text for word in ("bench", "charge", "rise", "coil", "catch")) >= 3
    multi = named_beats or "scroll states" in text or "this order" in text
    if not multi:
        return {"ok": True, "missing": [], "invalid": []}
    states = project_dir / "evidence" / "states"
    shots = pixel_evidence(project_dir)
    state_shots = [p for p in shots if "/states/" in p.replace("\\", "/")]
    if len(state_shots) < 2:
        return {
            "ok": False,
            "missing": ["evidence/states/ — at least two beat captures, not only the first viewport"],
            "invalid": [],
        }
    return {"ok": True, "missing": [], "invalid": []}


def evidence_files(project_dir: Path) -> list[str]:
    """Rendered pixel/video evidence only. Capture scripts and YAML are not evidence."""
    return pixel_evidence(project_dir)


def pixel_evidence(project_dir: Path) -> list[str]:
    root = project_dir / "evidence"
    if not root.is_dir():
        return []
    found: list[str] = []
    for path in root.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in PIXEL_SUFFIXES:
            continue
        if path.stat().st_size < 32:
            continue
        found.append(str(path.relative_to(project_dir)).replace("\\", "/"))
    return sorted(found)


def viewport_manifest(project_dir: Path) -> dict[str, Any] | None:
    path = project_dir / "evidence" / "viewports" / "manifest.yaml"
    if not path.is_file():
        return None
    data = load_yaml(path)
    return data or None


def validate_critic_independence(
    project_dir: Path,
    planned_ids: list[str],
    *,
    critic_pass_id: str | None,
    attested: bool = False,
    roles: dict[str, Any] | None = None,
) -> dict[str, Any]:
    roles = roles or {}
    issues: list[str] = []
    producer_ctx = roles.get("producer_host_context_id")
    critic_ctx = roles.get("critic_host_context_id")
    context = str(roles.get("independent_host_context") or classify_host_context(producer_ctx, critic_ctx))
    if context != "DISTINCT":
        issues.append(
            f"independent_host_context is {context} — a CLI boolean or same-host flag is not proof. "
            "Set a distinct ACOS_HOST_CONTEXT_ID in the critic chat, then re-run critic-pass."
        )
    if context == "SAME_CONTEXT":
        issues.append("critic host context equals producer host context")
    if attested and context != "DISTINCT":
        issues.append("independence_claim was attested but host context is not DISTINCT")
    if not critic_pass_id:
        issues.append("no critic_pass_id on session")
    frozen = str(roles.get("critic_frozen_implementation_sha256") or "")
    if frozen and frozen != implementation_fingerprint(project_dir):
        issues.append("implementation changed after critic-pass opened")
    for sid, rel in CRITIC_FILES.items():
        if sid not in planned_ids:
            continue
        path = project_dir / rel
        if not path.is_file():
            continue
        data = load_yaml(path)
        independence = str(data.get("independence") or "")
        if independence == SAME_SESSION_INDEPENDENCE:
            issues.append(f"{rel}: independence is {SAME_SESSION_INDEPENDENCE}")
        stamped = data.get("critic_pass_id")
        if critic_pass_id and stamped != critic_pass_id:
            issues.append(f"{rel}: critic_pass_id does not match the open critic pass")
        if not stamped:
            issues.append(f"{rel}: missing critic_pass_id")
    return {
        "ok": not issues,
        "issues": issues,
        "independent_host_context": context,
        "independence_claim": roles.get("independence_claim") or ("attested" if attested else "none"),
    }


def validate_critic_artifacts(project_dir: Path, planned_ids: list[str]) -> dict[str, Any]:
    missing: list[str] = []
    invalid: list[str] = []
    for sid, rel in CRITIC_FILES.items():
        if sid not in planned_ids:
            continue
        path = project_dir / rel
        if not path.is_file():
            missing.append(rel)
            continue
        data = load_yaml(path)
        findings = data.get("findings")
        if not isinstance(findings, list) or not findings:
            invalid.append(f"{rel}: critic must include findings[] from rendered evidence")
        if data.get("inspected_rendered_output") is not True:
            invalid.append(f"{rel}: inspected_rendered_output must be true")
        issues = validate_artifact_execution(data, sid)
        invalid.extend(issues)
        if not issues:
            write_execution_receipt(project_dir, sid, rel)
    return {"missing": missing, "invalid": invalid, "ok": not missing and not invalid}
