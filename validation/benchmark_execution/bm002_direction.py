"""Cinematic 3D direction artifacts for BM-002 — derived from routing, not manual skill lists."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _activated_skills(routing: dict[str, Any]) -> list[str]:
    return list(routing.get("planned_skill_ids") or routing.get("activated_skill_ids") or [])


def write_direction_artifacts(
    direction_dir: Path,
    *,
    routing: dict[str, Any],
    intake: dict[str, Any],
) -> dict[str, Any]:
    direction_dir.mkdir(parents=True, exist_ok=True)
    skills = _activated_skills(routing)
    now = datetime.now(timezone.utc).isoformat()

    creative = {
        "artifact_type": "creative_direction",
        "producer_capability": "ACOS-01",
        "routing_id": routing.get("routing_id"),
        "activated_via_routing": "ACOS-01" in skills,
        "timestamp": now,
        "product": {
            "name": "Solstice Arc",
            "category": "precision resonance field instrument",
            "positioning": "Calibrate spatial coherence in environments where conventional sensors fail.",
            "concept_thesis": "Cinematic product revelation — a sculptural brass-core instrument suspended in controlled void, revealed through scroll-driven camera choreography integrated with editorial typography.",
        },
        "visual_system": {
            "palette": {"void": "#0A0B0F", "brass": "#C8924E", "signal": "#5EEAD4", "ink": "#E8E4DC", "shadow": "#14161C"},
            "typography": {"display": "Cormorant Garamond", "ui": "IBM Plex Sans"},
            "anti_patterns_avoided": [
                "model_viewer_only",
                "spinning_primitive_demo",
                "generic_saas_landing",
                "decorative_checkbox_3d",
            ],
        },
        "three_d_decision": {
            "meaningful_3d_used": True,
            "mandatory_by_benchmark": True,
            "rationale": "BM-002 requires meaningful real-time WebGL/Three.js as core experience; procedural authored geometry with PBR materials and cinematic camera.",
            "blender_used": False,
            "blender_rationale": "Procedural Three.js lathe geometry and runtime lighting chosen for scroll-synchronized camera and responsive recomposition; Blender not required for this deliverable quality path.",
            "production_pipeline": "procedural_three_js_webgl",
        },
    }

    experience = {
        "artifact_type": "experience_direction",
        "producer_capability": "ACOS-05",
        "routing_id": routing.get("routing_id"),
        "activated_via_routing": "ACOS-05" in skills,
        "timestamp": now,
        "information_architecture": [
            "establishing_void",
            "instrument_thesis",
            "resonance_reveal",
            "field_capabilities",
            "technical_specifications",
            "calibration_experience",
            "acquisition",
        ],
        "interaction_language": {
            "primary": "scroll_driven_scene_progression",
            "secondary": ["nav_scroll_spy", "pointer_parallax_subtle", "mobile_menu"],
            "motion": "camera_ease_choreography_with_dom_fade",
            "reduced_motion_fallback": "static_compositions_per_section",
            "scene_states": [
                "opening_establishing_state",
                "product_reveal_or_focus_state",
                "mid_experience_progression_state",
                "closing_or_cta_state",
            ],
        },
        "responsive_strategy": "per_viewport_camera_recomposition_and_typography_scale_not_desktop_shrink",
    }

    art = {
        "artifact_type": "art_direction",
        "producer_capability": "ACOS-04",
        "routing_id": routing.get("routing_id"),
        "activated_via_routing": "ACOS-04" in skills,
        "timestamp": now,
        "cinematic_direction": {
            "producer_capability": "ACOS-06",
            "activated_via_routing": "ACOS-06" in skills,
            "camera_language": "orbital_dolly_with_focal_hierarchy",
            "lighting": "key_rim_fill_with_anisotropic_brass_highlights",
            "composition": "3d_subject_left_typography_right_desktop; stacked_mobile",
        },
        "composition": "Full-viewport WebGL canvas with editorial DOM overlay; depth layering between void, instrument, and typographic register.",
        "asset_provenance": "Procedural Three.js geometry authored in main.js — no external GLB model viewer.",
    }

    import yaml

    for name, data in (
        ("creative_direction.yaml", creative),
        ("experience_direction.yaml", experience),
        ("art_direction.yaml", art),
    ):
        (direction_dir / name).write_text(yaml.dump(data, sort_keys=False), encoding="utf-8")

    return {"creative": creative, "experience": experience, "art": art, "skills": skills}


def evaluate_design_gate(direction_dir: Path, routing: dict[str, Any]) -> dict[str, Any]:
    required = ["creative_direction.yaml", "experience_direction.yaml", "art_direction.yaml"]
    missing = [f for f in required if not (direction_dir / f).is_file()]
    if missing:
        return {
            "status": "BLOCKED_INSUFFICIENT_EVIDENCE",
            "missing_artifacts": missing,
            "routing_id": routing.get("routing_id"),
        }

    import yaml

    creative_path = direction_dir / "creative_direction.yaml"
    creative = yaml.safe_load(creative_path.read_text(encoding="utf-8")) or {}
    three_d = creative.get("three_d_decision") or {}
    quality_risks: list[str] = []
    if three_d.get("blender_used") is False and three_d.get("production_pipeline") == "procedural_three_js_webgl":
        quality_risks.append("procedural_three_js_without_blender_challenge_recorded")
    if not (creative.get("product") or {}).get("concept_thesis"):
        quality_risks.append("missing_concept_thesis")

    return {
        "status": "APPROVED",
        "routing_id": routing.get("routing_id"),
        "decision_provenance": "direction_artifacts_present_post_routing",
        "required_before_production": True,
        "quality_risks": quality_risks,
        "substantive_review_performed": False,
        "note": "File-presence gate only — does not certify flagship visual/3D quality feasibility",
    }
