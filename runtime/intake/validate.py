"""Intake validation — distinguishes facts, assumptions, and unknowns."""

from __future__ import annotations

from typing import Any


class IntakeValidationError(ValueError):
    pass


REQUIRED_FIELDS = ("task_id", "request", "normalized_goal", "task_signals")


def validate_intake(intake: dict[str, Any]) -> None:
    missing = [f for f in REQUIRED_FIELDS if not intake.get(f)]
    if missing:
        raise IntakeValidationError(f"Missing required intake fields: {missing}")

    signals = intake.get("task_signals")
    if not isinstance(signals, dict):
        raise IntakeValidationError("task_signals must be an object")

    profile = signals.get("deliverable_profile")
    valid_profiles = {
        "standard_application",
        "visual_experience",
        "interactive_3d",
        "reference_reconstruction",
        "authored_3d_asset",
    }
    if profile and profile not in valid_profiles:
        raise IntakeValidationError(f"Invalid deliverable_profile: {profile}")

    inputs = intake.get("available_inputs") or {}
    if inputs:
        for key in ("user_stated_facts", "runtime_observed_facts", "inferred_assumptions", "unknowns"):
            val = inputs.get(key)
            if val is not None and not isinstance(val, list):
                raise IntakeValidationError(f"available_inputs.{key} must be a list")

    caps = intake.get("runtime_capabilities") or {}
    if caps and not isinstance(caps, dict):
        raise IntakeValidationError("runtime_capabilities must be an object")


def has_sufficient_routing_input(intake: dict[str, Any]) -> bool:
    goal = (intake.get("normalized_goal") or "").strip()
    signals = intake.get("task_signals") or {}
    profile = signals.get("deliverable_profile")
    return bool(goal and profile)
