"""Build runtime intake from frozen BM-001 registration — no manual skill prescription."""

from __future__ import annotations

import uuid
from typing import Any

from runtime.intake.normalize import normalize_intake


def build_intake_from_registration(registration: dict[str, Any]) -> dict[str, Any]:
    brief = registration.get("normalized_brief") or {}
    caps = registration.get("capability_expectations") or {}
    task_id = f"bm001-{uuid.uuid4().hex[:12]}"
    return normalize_intake(
        {
            "task_id": task_id,
            "request": brief.get("objective", ""),
            "normalized_goal": brief.get("primary_goal", brief.get("objective", "")),
            "deliverables": [brief.get("deliverable_type", "functional_interactive_web_experience")],
            "constraints": [
                "benchmark_independence",
                "evidence_required",
                "frozen_acceptance_contract",
                "normal_acos_routing_only",
            ],
            "task_signals": {
                "deliverable_profile": "visual_experience",
                "requires_visual_output": True,
                "requires_creative_direction": True,
                "requires_responsive": True,
                "requires_accessibility": True,
                "requires_motion": bool(caps.get("motion_expected", True)),
                "requires_3d": False,
                "requires_frontend": True,
            },
            "runtime_capabilities": {
                "browser": "AVAILABLE",
                "blender": "RESTRICTED",
                "git": "AVAILABLE",
                "shell": "AVAILABLE",
                "filesystem": "AVAILABLE",
            },
            "benchmark_ref": {
                "benchmark_id": registration.get("benchmark_id", "BM-001"),
                "contract_version": registration.get("contract_version", "1.1"),
                "contract_hash": registration.get("benchmark_contract_sha256"),
            },
        }
    )
