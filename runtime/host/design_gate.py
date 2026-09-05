"""Substantive Design Gate — file presence is never enough to APPROVE."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from runtime.host.artifact_contract import load_yaml, required_creative_files, validate_creative_artifacts


def _text(value: Any) -> str:
    return str(value or "").strip()


def evaluate_host_design_gate(project_dir: Path, planned_ids: list[str], routing_id: str | None = None) -> dict[str, Any]:
    files = validate_creative_artifacts(project_dir, planned_ids)
    if files["missing"]:
        return {
            "status": "BLOCKED_INSUFFICIENT_EVIDENCE",
            "routing_id": routing_id,
            "substantive_review_performed": True,
            "missing_artifacts": files["missing"],
            "failures": files["invalid"],
            "required_before_production": True,
        }
    if files["invalid"]:
        return {
            "status": "REJECTED",
            "routing_id": routing_id,
            "substantive_review_performed": True,
            "failures": files["invalid"],
            "required_before_production": True,
            "route_correction_upstream": True,
        }

    failures: list[str] = []
    creative = load_yaml(project_dir / "direction" / "creative_direction.yaml") if (project_dir / "direction" / "creative_direction.yaml").is_file() else {}
    thesis = _text(
        creative.get("central_creative_thesis")
        or (creative.get("product") or {}).get("concept_thesis")
        or creative.get("concept_thesis")
    )
    if len(thesis) < 40:
        failures.append("creative_direction: central thesis missing or too thin")
    specificity = creative.get("project_specificity") or {}
    if str(specificity.get("name_swap_test", "")).lower() == "fail":
        failures.append("creative_direction: name-swap test failed — thesis is not project-specific")
    if "ACOS-01" in planned_ids and not specificity.get("justification") and len(thesis) < 80:
        failures.append("creative_direction: project specificity justification missing")

    if "ACOS-03" in planned_ids:
        anti = load_yaml(project_dir / "direction" / "anti_generic_review.yaml")
        verdict = str(anti.get("verdict") or anti.get("status") or "").upper()
        if verdict not in {"PASS", "APPROVED"}:
            failures.append("anti_generic_review: verdict is not PASS")

    if "ACOS-04" in planned_ids:
        art = load_yaml(project_dir / "direction" / "art_direction.yaml")
        if not (_text(art.get("typography") or (art.get("visual_system") or {}).get("typography"))):
            failures.append("art_direction: typography system missing")
        if not (_text(art.get("composition") or art.get("hierarchy"))):
            failures.append("art_direction: composition/hierarchy missing")

    if "ACOS-05" in planned_ids:
        exp = load_yaml(project_dir / "direction" / "experience_direction.yaml")
        journey = exp.get("information_architecture") or exp.get("journey") or exp.get("sections")
        if not journey:
            failures.append("experience_direction: journey / IA missing")
        if not _text(exp.get("responsive_strategy") or (exp.get("responsive") or "")):
            failures.append("experience_direction: responsive strategy missing")

    three_d = (creative.get("specialized_direction_flags") or {}).get("three_d") or (
        (creative.get("three_d_decision") or {}).get("meaningful_3d_used")
    )
    if three_d in ("required", True) and not _text(
        (creative.get("specialized_direction_flags") or {}).get("three_d_rationale")
        or (creative.get("three_d_decision") or {}).get("rationale")
    ):
        failures.append("3D is claimed required without a communicative rationale")

    if failures:
        return {
            "status": "REJECTED",
            "routing_id": routing_id,
            "substantive_review_performed": True,
            "failures": failures,
            "required_before_production": True,
            "route_correction_upstream": True,
            "checked_files": required_creative_files(planned_ids),
        }

    return {
        "status": "APPROVED",
        "routing_id": routing_id,
        "substantive_review_performed": True,
        "required_before_production": True,
        "checked_files": required_creative_files(planned_ids),
        "note": "Direction artifacts passed structural Design Gate checks. This is not visual QA.",
    }
