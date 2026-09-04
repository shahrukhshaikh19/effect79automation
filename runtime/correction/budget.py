"""Correction routing and bounded retry budget."""

from __future__ import annotations

import uuid
from typing import Any

from runtime.common.registry_loader import default_retry_budget
from runtime.correction.route import route_defect_to_skill

__all__ = ["create_correction_request", "route_defect_to_skill"]


def create_correction_request(
    *,
    task_id: str,
    source_gate_or_critic: str,
    defect_ids: list[str],
    severity: str,
    responsible_skill_ids: list[str],
    retry_number: int,
    evidence_refs: list[str] | None = None,
    required_changes: list[str] | None = None,
    preserve_constraints: list[str] | None = None,
    retry_budget: int | None = None,
) -> dict[str, Any]:
    budget = retry_budget if retry_budget is not None else default_retry_budget()
    status = "REQUESTED"
    if retry_number > budget:
        status = "HUMAN_REVIEW_REQUIRED"
    return {
        "correction_id": f"corr-{uuid.uuid4().hex[:12]}",
        "task_id": task_id,
        "source_gate_or_critic": source_gate_or_critic,
        "defect_ids": defect_ids,
        "severity": severity,
        "responsible_skill_ids": responsible_skill_ids,
        "artifact_refs": [],
        "evidence_refs": evidence_refs or [],
        "required_changes": required_changes or [],
        "preserve_constraints": preserve_constraints or [],
        "retry_number": retry_number,
        "retry_budget": budget,
        "status": status,
    }

