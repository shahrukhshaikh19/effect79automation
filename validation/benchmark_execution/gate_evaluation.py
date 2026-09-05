"""ACOS Quality Gate evaluation for BM-001 — no hard-coded HR success."""

from __future__ import annotations

from typing import Any

from runtime.common.constants import EVIDENCE_BLOCKER_IDS, HARD_REJECT_IDS
from runtime.quality.gate import evaluate_gate

# Benchmark hard-failure → canonical HR mapping (ACOS-13 semantics)
BENCHMARK_HR_MAP: dict[str, str] = {
    "broken_navigation_or_interaction": "HR-01",
    "obvious_console_runtime_errors": "HR-02",
    "catastrophic_breakage_at_required_viewports": "HR-03",
    "desktop_only_designed_experience": "HR-03",
    "reduced_motion_not_considered_where_applicable": "HR-04",
    "unjustified_severe_performance_degradation": "HR-05",
    "missing_critical_fallback": "HR-06",
    "generic_saas_landing_template": "HR-10",
    "predictable_gradient_heavy_ai_aesthetics": "HR-10",
    "arbitrary_glassmorphism": "HR-10",
    "excessive_glow_without_purpose": "HR-10",
    "generic_ai_generated_aesthetic": "HR-10",
    "imitates_recognizable_brand": "HR-10",
    "meaningless_decorative_animation": "HR-10",
    "not_a_functional_web_experience": "HR-01",
    "obvious_layout_breakage": "HR-03",
    "placeholder_quality_visual_assets": "HR-10",
    "poor_3d_quality_when_meaningful_3d_used": "HR-08",
}


def _hard_rejects_from_findings(
    critic_report: dict[str, Any],
    artifact_analysis: dict[str, Any],
) -> list[dict[str, Any]]:
    triggered: dict[str, dict[str, Any]] = {}

    for finding in critic_report.get("findings") or []:
        if finding.get("verdict") not in ("FAIL", "REJECTED"):
            continue
        for hf in finding.get("hard_failures") or []:
            hid = str(hf.get("id", hf) if isinstance(hf, dict) else hf)
            hr = BENCHMARK_HR_MAP.get(hid)
            if hr:
                triggered[hr] = {
                    "id": hr,
                    "triggered": True,
                    "source": finding.get("critic_capability"),
                    "benchmark_hard_failure": hid,
                    "evidence_refs": finding.get("evidence_refs") or [],
                    "detail": finding.get("summary") or finding.get("notes") or hid,
                }

    for signal in artifact_analysis.get("hard_failure_signals") or []:
        hid = signal.get("id", "")
        hr = BENCHMARK_HR_MAP.get(hid)
        if hr:
            triggered[hr] = {
                "id": hr,
                "triggered": True,
                "source": "artifact_analysis",
                "benchmark_hard_failure": hid,
                "evidence_refs": [signal.get("evidence_ref", "")],
                "detail": signal.get("detail", hid),
            }

    rejects = [{"id": hr, "triggered": False} for hr in HARD_REJECT_IDS]
    for item in rejects:
        if item["id"] in triggered:
            item.update(triggered[item["id"]])
    return rejects


def determine_gate_status(
    *,
    evidence_completeness: dict[str, Any],
    critic_report: dict[str, Any],
    artifact_analysis: dict[str, Any],
    runtime_healthy: bool,
    console_error_count: int,
) -> tuple[str, list[dict[str, Any]], dict[str, Any]]:
    """Precedence: evidence → HR → critic failures → approve."""
    decisions: dict[str, Any] = {
        "hard_reject_triggered": False,
        "evidence_blocker_triggered": False,
        "hard_reject_ids": [],
        "evidence_blocker_ids": [],
    }

    if not evidence_completeness.get("sufficient"):
        decisions["evidence_blocker_triggered"] = True
        decisions["evidence_blocker_ids"] = list(EVIDENCE_BLOCKER_IDS)
        hard_rejects = [{"id": hr, "triggered": False} for hr in HARD_REJECT_IDS]
        return "BLOCKED_INSUFFICIENT_EVIDENCE", hard_rejects, decisions

    if console_error_count > 0 or not runtime_healthy:
        artifact_analysis.setdefault("hard_failure_signals", []).append(
            {
                "id": "obvious_console_runtime_errors",
                "evidence_ref": "evidence/E-005/console_log.json",
                "detail": f"console_errors={console_error_count}, runtime_healthy={runtime_healthy}",
            }
        )

    hard_rejects = _hard_rejects_from_findings(critic_report, artifact_analysis)
    triggered_hr = [hr["id"] for hr in hard_rejects if hr.get("triggered")]

    if triggered_hr:
        decisions["hard_reject_triggered"] = True
        decisions["hard_reject_ids"] = triggered_hr
        return "REJECTED", hard_rejects, decisions

    critic_blocked = any(f.get("verdict") == "BLOCKED_INSUFFICIENT_EVIDENCE" for f in critic_report.get("findings") or [])
    critic_fail = any(f.get("verdict") == "FAIL" for f in critic_report.get("findings") or [])

    if critic_blocked:
        decisions["evidence_blocker_triggered"] = True
        decisions["evidence_blocker_ids"] = list(EVIDENCE_BLOCKER_IDS)
        return "BLOCKED_INSUFFICIENT_EVIDENCE", hard_rejects, decisions

    if critic_fail:
        decisions["hard_reject_triggered"] = True
        decisions["hard_reject_ids"] = ["HR-10"]
        for hr in hard_rejects:
            if hr["id"] == "HR-10":
                hr["triggered"] = True
                hr["source"] = "critic_dimension_fail"
        return "REJECTED", hard_rejects, decisions

    return "APPROVED", hard_rejects, decisions


def build_gate_report(
    *,
    gate_status: str,
    hard_rejects: list[dict[str, Any]],
    decisions: dict[str, Any],
    evidence_records: list[dict[str, Any]],
    critic_report: dict[str, Any],
    dimension_scores: dict[str, Any] | None = None,
) -> dict[str, Any]:
    eb_triggered = gate_status == "BLOCKED_INSUFFICIENT_EVIDENCE"
    return {
        "gate_report": {
            "status": gate_status,
            "benchmark_id": "BM-001",
            "contract_version": "1.1",
            "decisions": decisions,
            "hard_rejects": hard_rejects,
            "evidence_blockers": [{"id": "EB-01", "triggered": eb_triggered}],
            "evidence": evidence_records,
            "critic_summary": critic_report,
            "scores": dimension_scores or {},
        }
    }


def evaluate_quality_gate(gate_report: dict[str, Any]) -> dict[str, Any]:
    return evaluate_gate(gate_report)
