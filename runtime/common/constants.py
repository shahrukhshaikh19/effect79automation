"""Shared constants for Phase F runtime."""

from __future__ import annotations

GATE_TERMINAL_STATUSES = frozenset(
    {"APPROVED", "REJECTED", "BLOCKED_INSUFFICIENT_EVIDENCE"}
)

HARD_REJECT_IDS = tuple(f"HR-{i:02d}" for i in range(1, 11))
EVIDENCE_BLOCKER_IDS = ("EB-01",)
FORBIDDEN_GATE_IDS = ("HR-11",)

ROUTING_STATUSES = frozenset(
    {
        "ROUTED",
        "ROUTING_BLOCKED_INSUFFICIENT_INPUT",
        "ROUTING_BLOCKED_CAPABILITY",
        "ROUTING_REQUIRES_HUMAN_DECISION",
    }
)

TOOL_STATES = frozenset(
    {"AVAILABLE", "RESTRICTED", "BLOCKED", "UNAVAILABLE", "UNKNOWN"}
)

DESIGN_GATE_STATES = frozenset(
    {
        "NOT_APPLICABLE",
        "PENDING",
        "APPROVED",
        "REJECTED",
        "BLOCKED_INSUFFICIENT_EVIDENCE",
    }
)

PROMOTION_LEVELS = (
    "observation",
    "project-rule",
    "candidate-global",
    "validated-global",
    "deprecated",
)

MEMORY_CATEGORIES = (
    "knowledge",
    "taste",
    "projects",
    "failures",
    "successes",
    "model_compatibility",
)

LICENSE_RESTRICTED_SKILLS = frozenset({"EXT-FE-01", "EXT-FE-02"})
OPERATIONAL_RESTRICTED_SKILLS = frozenset({"EXT-IMG3D-01"})

FORBIDDEN_EVIDENCE_CLAIMS = frozenset(
    {"looks good", "tested", "passed", "compiles", "build succeeded"}
)

EXECUTION_EVENT_TYPES = (
    "TASK_NORMALIZED",
    "ROUTING_CREATED",
    "SKILL_ACTIVATED",
    "HANDOFF_CREATED",
    "EVIDENCE_REGISTERED",
    "CRITIC_COMPLETED",
    "GATE_BLOCKED",
    "GATE_REJECTED",
    "CORRECTION_REQUESTED",
    "CORRECTION_COMPLETED",
    "GATE_APPROVED",
    "MEMORY_CANDIDATE_CREATED",
    "EXECUTION_RESUMED",
    "DESIGN_GATE_APPROVED",
    "EXECUTABLE_SKILLS_REFRESHED",
)

DEFAULT_RETRY_BUDGET = 2
CORRECTION_EXhaustED_STATUS = "HUMAN_REVIEW_REQUIRED"

CANONICAL_AUTHORITY_PREFIXES = (
    "core/CONSTITUTION.md",
    "core/QUALITY_GATES.md",
    "core/ROUTING.md",
    "registry/SKILLS.yaml",
    "registry/TOOLS.yaml",
)
