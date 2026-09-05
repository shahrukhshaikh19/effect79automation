"""Bind routed skills to canonical SKILL.md hashes and procedure evidence.

A boolean or producer name is not execution proof.
"""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from runtime.common.registry_loader import skill_name_map, skill_path_for_id

REPO = Path(__file__).resolve().parents[2]
MIN_EVIDENCE = 24

# Host-checked procedure keys mapped to SKILL.md Exact procedure / required outputs.
# Validator recomputes the live SKILL.md hash; these keys must have unique prose evidence.
SKILL_CONTRACTS: dict[str, dict[str, Any]] = {
    "ACOS-01": {
        "artifact": "direction/creative_direction.yaml",
        "procedure": [
            "confirm_activation",
            "ingest_inputs",
            "central_thesis",
            "specificity_test",
            "principles",
            "handoff",
        ],
    },
    "ACOS-02": {
        "artifact": "direction/reference_analysis.yaml",
        "procedure": ["extract_principles", "no_literal_copy", "handoff"],
    },
    "ACOS-03": {
        "artifact": "direction/anti_generic_review.yaml",
        "procedure": ["challenge_pass", "generic_tropes", "verdict"],
    },
    "ACOS-04": {
        "artifact": "direction/art_direction.yaml",
        "procedure": ["typography", "composition", "surfaces"],
    },
    "ACOS-05": {
        "artifact": "direction/experience_direction.yaml",
        "procedure": ["journey", "hierarchy", "responsive"],
    },
    "ACOS-10": {
        "artifact": "critics/visual_critic.yaml",
        "procedure": ["inspect_pixels", "viewport_findings", "hierarchy"],
    },
    "ACOS-11": {
        "artifact": "critics/creative_critic.yaml",
        "procedure": ["inspect_pixels", "concept_findings", "genericness"],
    },
    "ACOS-12": {
        "artifact": "critics/3d_critic.yaml",
        "procedure": ["inspect_pixels", "silhouette_materials", "lighting_camera"],
    },
    "ACOS-15": {
        "artifact": "direction/product_design.yaml",
        "procedure": [
            "confirm_activation",
            "archetype_and_architecture",
            "scale_and_envelope",
            "form_directions",
            "form_hierarchy",
            "parts_and_mechanics",
            "cmf_intent",
            "multi_view_spec",
            "handoff",
        ],
    },
    "ACOS-16": {
        "artifact": "direction/form_model.yaml",
        "procedure": [
            "ingest_spec",
            "dimensioned_blockout",
            "primary_forms",
            "clay_capture",
            "proportion_correct",
            "joints_and_seams",
            "handoff_clay",
        ],
    },
    "ACOS-17": {
        "artifact": "critics/industrial_design.yaml",
        "procedure": [
            "independence",
            "inspect_clay",
            "silhouette_proportion",
            "primitive_derived",
            "mechanics_and_identity",
            "detail_hiding_form",
            "handoff",
        ],
    },
    "EXT-3DWEB-02": {
        "artifact": "direction/threejs_materials.yaml",
        "procedure": ["material_system", "not_default_mesh"],
    },
    "EXT-3DWEB-03": {
        "artifact": "direction/threejs_lighting.yaml",
        "procedure": ["lighting_rig", "not_dim_default"],
    },
    "EXT-3DWEB-04": {
        "artifact": "direction/threejs_camera.yaml",
        "procedure": ["authored_framing", "lens_intent"],
    },
    "EXT-BLD-01": {
        "artifact": "direction/blender_production.yaml",
        "procedure": ["analyze", "plan", "brief"],
    },
    "EXT-BLD-02": {
        "artifact": "direction/blender_modeler.yaml",
        "procedure": ["blockout", "authored_forms", "cleanup"],
    },
    "EXT-BLD-03": {
        "artifact": "direction/prop_artist.yaml",
        "procedure": ["primary_volumes", "product_parts", "not_primitive_hero"],
    },
    "EXT-BLD-05": {
        "artifact": "direction/blender_materials.yaml",
        "procedure": ["material_masters", "assigned_to_parts"],
    },
    "EXT-BLD-06": {
        "artifact": "direction/blender_lookdev.yaml",
        "procedure": ["lit_read", "full_object_shot"],
    },
    "EXT-BLD-12": {
        "artifact": "direction/blender_export.yaml",
        "procedure": ["blender_modeled", "glb_exported", "loader_handoff"],
    },
    "EXT-BLD-13": {
        "artifact": "direction/hard_surface.yaml",
        "procedure": ["primary_forms", "boolean_bevel", "manufacturing_seams"],
    },
}


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_skill_md(skill_id: str) -> Path | None:
    rel = skill_path_for_id(skill_id)
    if not rel:
        return None
    path = REPO / rel
    return path if path.is_file() else None


def skill_md_sha256(skill_id: str) -> str:
    path = canonical_skill_md(skill_id)
    if path is None:
        return ""
    return sha256_file(path)


def binding_for(skill_id: str) -> dict[str, Any]:
    contract = SKILL_CONTRACTS.get(skill_id) or {}
    path = skill_path_for_id(skill_id)
    name = skill_name_map().get(skill_id, "")
    return {
        "skill_id": skill_id,
        "native_skill_name": name,
        "invoke": f"/{name}" if name else "",
        "skill_path": path,
        "skill_md_sha256": skill_md_sha256(skill_id),
        "required_procedure": list(contract.get("procedure") or []),
        "artifact": contract.get("artifact") or "",
    }


def _evidence_map(data: dict[str, Any]) -> dict[str, str]:
    raw = data.get("procedure_evidence")
    if not isinstance(raw, dict):
        return {}
    out: dict[str, str] = {}
    for key, value in raw.items():
        if isinstance(value, dict):
            text = str(value.get("evidence") or value.get("note") or "").strip()
        else:
            text = str(value or "").strip()
        out[str(key)] = text
    return out


def validate_artifact_execution(data: dict[str, Any], skill_id: str) -> list[str]:
    """Return invalid reasons. Booleans and producer names never pass this."""
    issues: list[str] = []
    contract = SKILL_CONTRACTS.get(skill_id)
    if not contract:
        return issues
    live = skill_md_sha256(skill_id)
    if not live:
        issues.append(f"{skill_id}: canonical SKILL.md missing — cannot bind execution")
        return issues
    claimed = str(data.get("skill_md_sha256") or "").strip().lower()
    if claimed != live:
        issues.append(
            f"{skill_id}: artifact skill_md_sha256 does not match live SKILL.md "
            f"(claimed={claimed or 'missing'}, live={live[:12]}…)"
        )
    claimed_id = str(data.get("skill_id") or "").strip()
    if claimed_id and claimed_id != skill_id:
        issues.append(f"{skill_id}: artifact skill_id does not match routed skill")
    evidence = _evidence_map(data)
    required = list(contract["procedure"])
    missing_steps = [step for step in required if step not in evidence]
    if missing_steps:
        issues.append(f"{skill_id}: procedure_evidence missing {missing_steps}")
    seen: set[str] = set()
    for step in required:
        text = evidence.get(step, "")
        if len(text) < MIN_EVIDENCE:
            issues.append(f"{skill_id}: procedure_evidence.{step} is too thin to count as execution")
            continue
        if text.lower() in {"true", "done", "yes", "ok", "executed", "followed"}:
            issues.append(f"{skill_id}: procedure_evidence.{step} is a token, not evidence")
        if text in seen:
            issues.append(f"{skill_id}: procedure_evidence values are duplicated — not step evidence")
        seen.add(text)
    if data.get("skill_procedure_executed") is True and not evidence:
        issues.append(f"{skill_id}: skill_procedure_executed is not proof without procedure_evidence")
    return issues


def write_execution_receipt(project_dir: Path, skill_id: str, artifact_rel: str) -> Path:
    binding = binding_for(skill_id)
    payload = {
        "skill_id": skill_id,
        "skill_path": binding["skill_path"],
        "skill_md_sha256": binding["skill_md_sha256"],
        "artifact": artifact_rel,
        "required_procedure": binding["required_procedure"],
        "verified_against_canonical": True,
        "verified_at": datetime.now(timezone.utc).isoformat(),
        "producer_name_is_not_proof": True,
        "boolean_flag_is_not_proof": True,
    }
    directory = project_dir / "receipts"
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{skill_id}.yaml"
    path.write_text(yaml.dump(payload, sort_keys=False), encoding="utf-8")
    return path


def validate_contracted_artifacts(project_dir: Path, skill_ids: list[str], *, write_receipts: bool = False) -> dict[str, Any]:
    missing: list[str] = []
    invalid: list[str] = []
    for skill_id in skill_ids:
        contract = SKILL_CONTRACTS.get(skill_id)
        if not contract:
            continue
        rel = str(contract["artifact"])
        path = project_dir / rel
        if not path.is_file() or path.stat().st_size < 40:
            missing.append(rel)
            continue
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            invalid.append(f"{rel}: not a mapping")
            continue
        issues = validate_artifact_execution(data, skill_id)
        if issues:
            invalid.extend(issues)
            continue
        if write_receipts:
            write_execution_receipt(project_dir, skill_id, rel)
    return {"missing": missing, "invalid": invalid, "ok": not missing and not invalid}
