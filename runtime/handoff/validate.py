"""Handoff construction and validation."""

from __future__ import annotations

import uuid
from typing import Any


REQUIRED = (
    "handoff_id",
    "task_id",
    "from_stage",
    "to_stage",
    "producer_skill_id",
    "consumer_skill_ids",
    "artifact_refs",
    "evidence_refs",
    "constraints_preserved",
    "status",
)


def build_handoff(
    *,
    task_id: str,
    from_stage: str,
    to_stage: str,
    producer_skill_id: str,
    consumer_skill_ids: list[str],
    artifact_refs: list[str],
    evidence_refs: list[str],
    constraints_preserved: list[str],
    decisions: dict[str, Any] | None = None,
    open_questions: list[str] | None = None,
    known_defects: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "handoff_id": f"handoff-{uuid.uuid4().hex[:12]}",
        "task_id": task_id,
        "from_stage": from_stage,
        "to_stage": to_stage,
        "producer_skill_id": producer_skill_id,
        "consumer_skill_ids": consumer_skill_ids,
        "artifact_refs": artifact_refs,
        "evidence_refs": evidence_refs,
        "decisions": decisions or {},
        "open_questions": open_questions or [],
        "known_defects": known_defects or [],
        "constraints_preserved": constraints_preserved,
        "status": "PENDING",
    }


def validate_handoff(handoff: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for field in REQUIRED:
        if field not in handoff or handoff[field] is None:
            errors.append(f"Missing handoff field: {field}")
    for ref in handoff.get("evidence_refs", []):
        if isinstance(ref, str) and ref.lower().strip() in ("looks good", "tested", "passed"):
            errors.append(f"Claim-only evidence forbidden in handoff: {ref}")
    return errors
