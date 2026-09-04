"""Creative / experience direction artifacts derived from routing activation — not manual skill lists."""

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
    """Record direction outputs for skills activated by routing (ACOS creative chain)."""
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
            "name": "Helix Meridian",
            "category": "spatial field instrument",
            "positioning": "Precision measurement for environments that resist calibration.",
            "concept_thesis": "Editorial instrument catalog — warm mineral surfaces, copper register accents, typographic hierarchy as primary visual system.",
        },
        "visual_system": {
            "palette": {"ground": "#E6E2D8", "ink": "#141210", "accent": "#9A4E2A", "muted": "#5C574F"},
            "typography": {"display": "Instrument Serif / Libre Baskerville", "ui": "DM Sans"},
            "anti_patterns_avoided": [
                "generic_saas_gradient",
                "glassmorphism",
                "floating_card_grid",
                "excessive_glow",
            ],
        },
        "three_d_decision": {
            "meaningful_3d_used": False,
            "rationale": "Routing selected visual_creative_route without requires_3d; dimensional storytelling achieved via typographic composition and SVG schematic.",
        },
    }

    experience = {
        "artifact_type": "experience_direction",
        "producer_capability": "ACOS-05",
        "routing_id": routing.get("routing_id"),
        "activated_via_routing": "ACOS-05" in skills,
        "timestamp": now,
        "information_architecture": [
            "hero_register",
            "thesis",
            "instrument_schematic",
            "capabilities",
            "specifications",
            "field_experience",
            "contact",
        ],
        "interaction_language": {
            "primary": "scroll_reveal",
            "secondary": ["nav_scroll_spy", "capability_accordion", "mobile_menu"],
            "motion": "restrained_ease_out_reveals",
            "reduced_motion_fallback": "instant_visibility_no_transforms",
        },
        "responsive_strategy": "mobile_first_typography_scale_with_collapsing_nav",
    }

    art = {
        "artifact_type": "art_direction",
        "producer_capability": "ACOS-04",
        "routing_id": routing.get("routing_id"),
        "activated_via_routing": "ACOS-04" in skills,
        "timestamp": now,
        "composition": "Asymmetric hero with vertical rhythm grid; copper rule lines anchor section breaks.",
        "asset_provenance": "SVG schematic and CSS-only surfaces — no external stock imagery.",
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
    """Design Gate — requires direction evidence before production unlock."""
    required = ["creative_direction.yaml", "experience_direction.yaml", "art_direction.yaml"]
    missing = [f for f in required if not (direction_dir / f).is_file()]
    if missing:
        return {
            "status": "BLOCKED_INSUFFICIENT_EVIDENCE",
            "missing_artifacts": missing,
            "routing_id": routing.get("routing_id"),
        }
    if routing.get("design_gate_state") == "NOT_APPLICABLE":
        return {"status": "NOT_APPLICABLE", "routing_id": routing.get("routing_id")}
    return {
        "status": "APPROVED",
        "routing_id": routing.get("routing_id"),
        "decision_provenance": "direction_artifacts_present_post_routing",
        "required_before_production": True,
    }
