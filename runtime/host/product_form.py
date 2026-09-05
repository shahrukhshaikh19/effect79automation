"""Industrial form path: spec contracts, clay evidence, Product Form Gate.

This is not lookdev and not the ship Quality Gate.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from runtime.host.craft_lock import inspect_hero_asset, validate_hero_primitives
from runtime.host.independence import classify_host_context
from runtime.host.skill_execution import (
    validate_artifact_execution,
    write_execution_receipt,
)
from runtime.host.visual_class import lookdev_images, png_stats

def _load(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}


CLAY_DIR = "evidence/form-clay"
REQUIRED_CLAY_STEMS = ("front", "profile", "rear", "front34", "rear34", "proportion")
PRODUCT_DESIGN = "direction/product_design.yaml"
FORM_SPEC = "direction/form_specification.yaml"
FORM_MODEL = "direction/form_model.yaml"
ID_CRITIC = "critics/industrial_design.yaml"
FORM_GATE = "gate/product_form_gate.yaml"
SAME_SESSION = "same_host_session_as_producer"

_INDUSTRIAL_HINTS = (
    "physical product",
    "physical instrument",
    "physical device",
    "physical object",
    "consumer electronic",
    "consumer electronics",
    "wearable",
    "appliance",
    "manufacturable",
    "industrial design",
    "hero product",
    "over-ear",
    "headphone",
    "headset",
    "earcup",
    "yoke",
    "in-ear",
    "anodized",
    "watch",
    "camera body",
    "keyboard",
    "automotive",
)


def requires_industrial_form(signals: dict[str, Any] | None, request: str = "") -> bool:
    data = signals or {}
    if data.get("requires_industrial_form") is True:
        return True
    if data.get("requires_physical_product") is True and str(data.get("quality_bar") or "") == "flagship":
        return True
    text = request.lower()
    return any(hint in text for hint in _INDUSTRIAL_HINTS) and str(data.get("quality_bar") or "") == "flagship"


def next_stage_after_design_gate(signals: dict[str, Any] | None, request: str = "") -> str:
    return "PRODUCT_DESIGN" if requires_industrial_form(signals, request) else "PRODUCTION"


def form_gate_status(project_dir: Path) -> str:
    path = project_dir / FORM_GATE
    if not path.is_file():
        return "MISSING"
    data = _load(path)
    body = data.get("form_gate") or data
    return str(body.get("status") or "").upper() or "MISSING"


def form_gate_approved(project_dir: Path) -> bool:
    return form_gate_status(project_dir) == "APPROVED"


def _list_len(value: Any) -> int:
    if isinstance(value, list):
        return len(value)
    if isinstance(value, dict):
        return len(value)
    return 0


def validate_product_design(project_dir: Path) -> dict[str, Any]:
    missing: list[str] = []
    invalid: list[str] = []
    for rel in (PRODUCT_DESIGN, FORM_SPEC):
        path = project_dir / rel
        if not path.is_file() or path.stat().st_size < 40:
            missing.append(rel)
            continue
        data = _load(path)
        if rel == PRODUCT_DESIGN:
            invalid.extend(validate_artifact_execution(data, "ACOS-15"))
            directions = data.get("form_directions") or data.get("rejected_directions")
            if _list_len(data.get("rejected_directions")) < 1 and _list_len(directions) < 2:
                invalid.append(f"{rel}: need at least two form directions and one rejected")
            if len(str(data.get("archetype") or data.get("committed_direction") or "")) < 12:
                invalid.append(f"{rel}: archetype / committed_direction missing")
        if rel == FORM_SPEC:
            parts = data.get("part_architecture") or data.get("parts")
            if _list_len(parts) < 3:
                invalid.append(f"{rel}: part_architecture must name at least three parts")
            envelope = data.get("envelope") or {}
            if not envelope:
                invalid.append(f"{rel}: envelope dimensions missing")
            views = data.get("modeling_views") or []
            if _list_len(views) < 4:
                invalid.append(f"{rel}: modeling_views must list the clay set")
    if not missing and not invalid:
        write_execution_receipt(project_dir, "ACOS-15", PRODUCT_DESIGN)
    return {"ok": not missing and not invalid, "missing": missing, "invalid": invalid}


def validate_form_model(project_dir: Path) -> dict[str, Any]:
    path = project_dir / FORM_MODEL
    if not path.is_file() or path.stat().st_size < 40:
        return {"ok": False, "missing": [FORM_MODEL], "invalid": []}
    data = _load(path)
    invalid = validate_artifact_execution(data, "ACOS-16")
    if data.get("production_glb_exported") is True:
        invalid.append(f"{FORM_MODEL}: production GLB is forbidden before Product Form Gate")
    if data.get("beauty_lookdev_done") is True:
        invalid.append(f"{FORM_MODEL}: beauty lookdev is forbidden before Product Form Gate")
    if not str(data.get("spec_ref") or ""):
        invalid.append(f"{FORM_MODEL}: spec_ref missing")
    if _list_len(data.get("clay_views")) < 6:
        invalid.append(f"{FORM_MODEL}: clay_views must list the required stems")
    if not invalid:
        write_execution_receipt(project_dir, "ACOS-16", FORM_MODEL)
    return {"ok": not invalid, "missing": [], "invalid": invalid}


def clay_images(project_dir: Path) -> list[Path]:
    root = project_dir / CLAY_DIR
    if not root.is_dir():
        return []
    found: list[Path] = []
    for path in root.rglob("*"):
        if path.is_file() and path.suffix.lower() in {".png", ".webp"} and path.stat().st_size > 4_000:
            found.append(path)
    return sorted(found)


def validate_clay_evidence(project_dir: Path, spec: dict[str, Any] | None = None) -> dict[str, Any]:
    issues: list[str] = []
    shots = clay_images(project_dir)
    stems = {p.stem.lower() for p in shots}
    for required in REQUIRED_CLAY_STEMS:
        if required not in stems:
            issues.append(f"{CLAY_DIR}/{required}.png missing — clay multi-view incomplete")
    mechanics = str((spec or {}).get("mechanics") or "").strip().lower()
    if mechanics and mechanics not in {"none", "n/a", "na"} and "joint" not in stems:
        issues.append(f"{CLAY_DIR}/joint.png missing — spec requires mechanics")
    if len(shots) < 6:
        issues.append(f"{CLAY_DIR}/ needs the required clay set, not lookdev")
    readable = 0
    for shot in shots:
        stats = png_stats(shot)
        if not stats:
            issues.append(f"{shot.name}: unreadable clay PNG")
            continue
        if stats["mean_luma"] < 0.08 and stats["contrast"] < 0.04:
            issues.append(f"{shot.name}: crushed/dark — beauty studio is not clay")
        if stats["mean_luma"] > 0.82 and stats["contrast"] < 0.03:
            issues.append(f"{shot.name}: flat white dump — not a clay read")
        readable += 1
    if lookdev_images(project_dir) and not shots:
        issues.append("lookdev exists but form-clay does not — lookdev cannot replace clay")
    return {"ok": not issues and readable >= 6, "issues": issues}


def validate_form_critic(project_dir: Path, *, pass_id: str | None, roles: dict[str, Any] | None) -> dict[str, Any]:
    path = project_dir / ID_CRITIC
    if not path.is_file() or path.stat().st_size < 40:
        return {"ok": False, "missing": [ID_CRITIC], "invalid": []}
    data = _load(path)
    invalid = validate_artifact_execution(data, "ACOS-17")
    if data.get("inspected_rendered_output") is not True:
        invalid.append(f"{ID_CRITIC}: inspected_rendered_output must be true")
    findings = data.get("findings")
    if not isinstance(findings, list) or not findings:
        invalid.append(f"{ID_CRITIC}: findings[] required from clay views")
    refs = data.get("evidence_refs") or []
    ref_text = " ".join(str(r) for r in refs).replace("\\", "/")
    if "lookdev" in ref_text or "viewports" in ref_text:
        invalid.append(f"{ID_CRITIC}: must cite {CLAY_DIR}/ only — lookdev/viewports are not form evidence")
    if CLAY_DIR not in ref_text:
        invalid.append(f"{ID_CRITIC}: evidence_refs must include {CLAY_DIR}/")
    if str(data.get("independence") or "") == SAME_SESSION:
        invalid.append(f"{ID_CRITIC}: independence is {SAME_SESSION}")
    if pass_id and str(data.get("form_critic_pass_id") or "") != pass_id:
        invalid.append(f"{ID_CRITIC}: form_critic_pass_id does not match the open form critic pass")
    if not data.get("form_critic_pass_id"):
        invalid.append(f"{ID_CRITIC}: missing form_critic_pass_id")
    verdict = str(data.get("verdict") or "").lower()
    if verdict not in {"pass", "fail", "blocked_insufficient_evidence"}:
        invalid.append(f"{ID_CRITIC}: verdict must be pass|fail|blocked_insufficient_evidence")
    roles = roles or {}
    context = classify_host_context(roles.get("producer_host_context_id"), roles.get("form_critic_host_context_id"))
    if context != "DISTINCT":
        invalid.append(
            f"form independent_host_context is {context} — form critic pass needs a distinct ACOS_HOST_CONTEXT_ID"
        )
        if verdict == "pass":
            invalid.append(f"{ID_CRITIC}: verdict pass is illegal without DISTINCT form critic context")
    majors = [
        f
        for f in findings or []
        if isinstance(f, dict) and str(f.get("severity") or "").lower() in {"critical", "major"}
    ]
    if verdict == "pass" and majors:
        invalid.append(f"{ID_CRITIC}: verdict pass with unresolved critical/major findings")
    if not invalid:
        write_execution_receipt(project_dir, "ACOS-17", ID_CRITIC)
    return {"ok": not invalid, "missing": [], "invalid": invalid, "verdict": verdict, "context": context}


def evaluate_product_form_gate(
    project_dir: Path,
    *,
    signals: dict[str, Any] | None,
    request: str = "",
    pass_id: str | None,
    roles: dict[str, Any] | None,
) -> dict[str, Any]:
    if not requires_industrial_form(signals, request):
        return {
            "status": "NOT_APPLICABLE",
            "form_gate": {"status": "NOT_APPLICABLE"},
        }
    design = validate_product_design(project_dir)
    model = validate_form_model(project_dir)
    spec = _load(project_dir / FORM_SPEC)
    clay = validate_clay_evidence(project_dir, spec)
    critic = validate_form_critic(project_dir, pass_id=pass_id, roles=roles)
    primitive = validate_hero_primitives(project_dir)
    issues: list[str] = []
    issues.extend([f"missing {m}" for m in design["missing"] + model["missing"] + critic.get("missing", [])])
    issues.extend(design["invalid"])
    issues.extend(model["invalid"])
    issues.extend(clay["issues"])
    issues.extend(critic.get("invalid") or [])
    issues.extend(primitive)
    for asset in (project_dir / "implementation").rglob("*") if (project_dir / "implementation").is_dir() else []:
        if asset.suffix.lower() in {".glb", ".gltf"} and asset.stat().st_size > 32:
            issues.extend(inspect_hero_asset(asset)["issues"])

    if issues:
        status = "BLOCKED_INSUFFICIENT_EVIDENCE"
        if critic.get("verdict") == "fail" or any("primitive" in i.lower() or "sphere" in i.lower() for i in issues):
            status = "REJECTED"
        if any(x.startswith("missing ") for x in issues) and critic.get("verdict") != "fail":
            status = "BLOCKED_INSUFFICIENT_EVIDENCE"
        report = {
            "status": status,
            "form_gate": {
                "status": status,
                "issues": issues,
                "critic_verdict": critic.get("verdict"),
            },
        }
        return report

    if critic.get("verdict") != "pass":
        return {
            "status": "REJECTED" if critic.get("verdict") == "fail" else "BLOCKED_INSUFFICIENT_EVIDENCE",
            "form_gate": {"status": "REJECTED" if critic.get("verdict") == "fail" else "BLOCKED_INSUFFICIENT_EVIDENCE", "issues": ["critic verdict is not pass"], "critic_verdict": critic.get("verdict")},
        }

    return {
        "status": "APPROVED",
        "form_gate": {"status": "APPROVED", "issues": [], "critic_verdict": "pass"},
    }
