"""Evidence-derived benchmark scoring against frozen BM-001 v1.1 contract."""

from __future__ import annotations

from typing import Any


def select_weight_profile(meaningful_3d_used: bool, acceptance: dict[str, Any]) -> str:
    if meaningful_3d_used:
        return "meaningful_3d_used"
    return "no_meaningful_3d"


def score_benchmark(
    *,
    acceptance: dict[str, Any],
    evidence_manifest: dict[str, Any],
    critic_report: dict[str, Any],
    gate_status: str,
    meaningful_3d_used: bool,
) -> dict[str, Any]:
    profiles = (acceptance.get("weight_normalization") or {}).get("profiles") or {}
    profile_name = select_weight_profile(meaningful_3d_used, acceptance)
    profile = profiles.get(profile_name, {})
    weights = profile.get("dimensions") or {}

    if gate_status == "BLOCKED_INSUFFICIENT_EVIDENCE":
        return {
            "benchmark_result": "BLOCKED",
            "benchmark_score": None,
            "profile": profile_name,
            "reason": "insufficient_evidence_for_scoring",
        }

    if gate_status == "REJECTED":
        return {
            "benchmark_result": "FAIL",
            "benchmark_score": None,
            "profile": profile_name,
            "reason": "quality_gate_rejected",
        }

    hard_fails = critic_report.get("hard_critic_failures") or []
    if hard_fails:
        return {
            "benchmark_result": "FAIL",
            "benchmark_score": None,
            "profile": profile_name,
            "reason": "critic_hard_failures",
        }

    dim_scores: dict[str, float] = {}
    runtime_ok = evidence_manifest.get("runtime_healthy", False)
    dim_scores["functional"] = 9.0 if runtime_ok else 3.0
    dim_scores["visual"] = 8.5 if evidence_manifest.get("viewports_captured") else 4.0
    dim_scores["creative"] = 8.5 if evidence_manifest.get("sections_present", 0) >= 5 else 4.0
    dim_scores["responsive"] = 8.5 if len(evidence_manifest.get("viewports_captured", [])) >= 4 else 3.0
    dim_scores["performance"] = 8.0 if evidence_manifest.get("performance_ok", True) else 4.0
    dim_scores["accessibility"] = 8.5 if evidence_manifest.get("reduced_motion_verified") else 4.0
    dim_scores["engineering"] = 9.0 if gate_status == "APPROVED" else 5.0
    dim_scores["motion_quality"] = 8.0 if evidence_manifest.get("interaction_verified") else 4.0

    total = 0.0
    for dim, weight in weights.items():
        if dim == "three_d_quality":
            continue
        score = dim_scores.get(dim, 5.0)
        total += (score / 10.0) * float(weight)

    result = "PASS" if gate_status == "APPROVED" and total >= 70.0 else "FAIL"
    if gate_status != "APPROVED":
        result = "FAIL"

    return {
        "benchmark_result": result,
        "benchmark_score": round(total, 2),
        "profile": profile_name,
        "dimension_scores": dim_scores,
        "weights_applied": weights,
    }
