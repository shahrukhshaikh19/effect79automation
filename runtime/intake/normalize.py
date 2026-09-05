"""Intake normalization — preserves provenance labels."""

from __future__ import annotations

from copy import deepcopy
from typing import Any


def normalize_intake(intake: dict[str, Any]) -> dict[str, Any]:
    normalized = deepcopy(intake)
    inputs = normalized.setdefault("available_inputs", {})
    for key in ("user_stated_facts", "runtime_observed_facts", "inferred_assumptions", "unknowns"):
        inputs.setdefault(key, [])
    signals = normalized.setdefault("task_signals", {})
    for flag in (
        "requires_creative_direction",
        "requires_visual_output",
        "requires_3d",
        "requires_motion",
        "requires_responsive",
        "requires_accessibility",
        "requires_frontend",
        "requires_reference_analysis",
        "requires_physical_product",
    ):
        signals.setdefault(flag, False)
    signals.setdefault("reconstruction_path", "none")
    signals.setdefault("quality_bar", "standard")
    signals.setdefault("license_review_acknowledged", False)
    normalized.setdefault("runtime_capabilities", {})
    normalized.setdefault("prohibited_assumptions", [])
    normalized.setdefault("risk_flags", [])
    normalized.setdefault("prior_evidence_refs", [])
    normalized.setdefault("prior_memory_refs", [])
    return normalized
