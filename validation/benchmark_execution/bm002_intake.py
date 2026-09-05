"""Build runtime intake from frozen BM-002 registration — requires_3d via task semantics."""

from __future__ import annotations

import uuid
from typing import Any

from runtime.intake.normalize import normalize_intake


def build_intake_from_registration(registration: dict[str, Any]) -> dict[str, Any]:
    brief = registration.get("normalized_brief") or {}
    signals = brief.get("routing_task_signals") or {}
    caps = registration.get("capability_expectations") or {}
    bid = registration.get("benchmark_id", "BM-002")
    slug = bid.lower().replace("-", "")
    task_id = f"{slug}-{uuid.uuid4().hex[:12]}"
    return normalize_intake(
        {
            "task_id": task_id,
            "request": brief.get("objective", ""),
            "normalized_goal": brief.get("primary_goal", brief.get("objective", "")),
            "deliverables": [brief.get("deliverable_type", "cinematic_interactive_3d_web_experience")],
            "constraints": [
                "benchmark_independence",
                "evidence_required",
                "frozen_acceptance_contract",
                "normal_acos_routing_only",
                "mandatory_meaningful_real_time_3d",
            ],
            "task_signals": {
                "deliverable_profile": signals.get("deliverable_profile", "interactive_3d"),
                "requires_visual_output": bool(signals.get("requires_visual_output", True)),
                "requires_creative_direction": bool(signals.get("requires_creative_direction", True)),
                "requires_responsive": bool(signals.get("requires_responsive", True)),
                "requires_accessibility": bool(signals.get("requires_accessibility", True)),
                "requires_motion": bool(signals.get("requires_motion", caps.get("motion_expected", True))),
                "requires_3d": bool(signals.get("requires_3d", caps.get("three_d_mandatory", True))),
                "requires_frontend": bool(signals.get("requires_frontend", True)),
                "requires_cinematic_3d_direction": bool(signals.get("requires_cinematic_3d_direction", True)),
                "requires_spatial_interaction": bool(signals.get("requires_spatial_interaction", True)),
            },
            "runtime_capabilities": {
                "browser": "AVAILABLE",
                "blender": "RESTRICTED",
                "git": "AVAILABLE",
                "shell": "AVAILABLE",
                "filesystem": "AVAILABLE",
            },
            "benchmark_ref": {
                "benchmark_id": bid,
                "contract_version": registration.get("contract_version", "1.0"),
                "contract_hash": registration.get("benchmark_contract_sha256"),
            },
        }
    )
