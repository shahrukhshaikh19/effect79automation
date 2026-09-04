"""Quality Gate terminal-state evaluation with HR/EB precedence."""

from __future__ import annotations

from typing import Any

from runtime.common.constants import (
    EVIDENCE_BLOCKER_IDS,
    FORBIDDEN_GATE_IDS,
    GATE_TERMINAL_STATUSES,
    HARD_REJECT_IDS,
)


class QualityGateError(ValueError):
    pass


def evaluate_gate(gate_report: dict[str, Any]) -> dict[str, Any]:
    report = gate_report.get("gate_report", gate_report)
    status = report.get("status")
    if status not in GATE_TERMINAL_STATUSES:
        raise QualityGateError(f"Invalid terminal status: {status}")

    decisions = report.get("decisions", {}) or {}
    hard_ids = decisions.get("hard_reject_ids") or []
    eb_ids = decisions.get("evidence_blocker_ids") or []

    for forbidden in FORBIDDEN_GATE_IDS:
        if forbidden in hard_ids or forbidden in eb_ids:
            raise QualityGateError(f"Forbidden gate id present: {forbidden}")

    triggered_hr = [
        hr["id"]
        for hr in report.get("hard_rejects", [])
        if isinstance(hr, dict) and hr.get("triggered") and hr.get("id") in HARD_REJECT_IDS
    ]
    triggered_eb = [
        eb["id"]
        for eb in report.get("evidence_blockers", [])
        if isinstance(eb, dict) and eb.get("triggered") and eb.get("id") in EVIDENCE_BLOCKER_IDS
    ]

    if decisions.get("evidence_blocker_triggered") or triggered_eb:
        return {"status": "BLOCKED_INSUFFICIENT_EVIDENCE", "triggered": triggered_eb or eb_ids}

    evidence = report.get("evidence") or report.get("inputs_used", {}).get("qa_evidence")
    if status == "APPROVED" and not evidence:
        return {"status": "BLOCKED_INSUFFICIENT_EVIDENCE", "reason": "missing_evidence_for_approval"}

    if status == "REJECTED" and not (triggered_hr or decisions.get("hard_reject_triggered")):
        if not evidence:
            return {"status": "BLOCKED_INSUFFICIENT_EVIDENCE", "reason": "reject_without_demonstrated_defect"}

    if triggered_hr or decisions.get("hard_reject_triggered"):
        return {"status": "REJECTED", "triggered": triggered_hr or hard_ids}

    scores = report.get("scores") or {}
    if status == "APPROVED" and scores:
        pass  # scores cannot override — status already APPROVED with evidence

    return {"status": status}


def validate_producer_independence(
    *,
    producer_skill_id: str,
    critic_skill_id: str,
    gate_evaluator_skill_id: str = "ACOS-13",
) -> list[str]:
    errors: list[str] = []
    if producer_skill_id == critic_skill_id:
        errors.append("Producer cannot act as independent critic")
    if producer_skill_id == gate_evaluator_skill_id:
        errors.append("Producer cannot self-approve Quality Gate")
    return errors
