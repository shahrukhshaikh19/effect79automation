"""Evidence-derived benchmark scoring — downstream of gate only."""

from __future__ import annotations

from typing import Any


def select_weight_profile(meaningful_3d_used: bool) -> str:
    return "meaningful_3d_used" if meaningful_3d_used else "no_meaningful_3d"


def score_benchmark(
    *,
    acceptance: dict[str, Any],
    gate_status: str,
    critic_report: dict[str, Any],
    evidence_completeness: dict[str, Any],
    meaningful_3d_used: bool,
) -> dict[str, Any]:
    profiles = (acceptance.get("weight_normalization") or {}).get("profiles") or {}
    profile_name = select_weight_profile(meaningful_3d_used)
    profile = profiles.get(profile_name, {})
    weights = profile.get("dimensions") or {}

    if gate_status == "REJECTED":
        return {
            "benchmark_result": "FAIL",
            "benchmark_score": None,
            "profile": profile_name,
            "reason": "quality_gate_rejected",
            "dimension_scores": {},
            "provenance": {},
        }

    if gate_status == "BLOCKED_INSUFFICIENT_EVIDENCE" or not evidence_completeness.get("sufficient"):
        return {
            "benchmark_result": "BLOCKED",
            "benchmark_score": None,
            "profile": profile_name,
            "reason": "insufficient_evidence_for_scoring",
            "dimension_scores": {},
            "provenance": {},
        }

    if gate_status != "APPROVED":
        return {
            "benchmark_result": "FAIL",
            "benchmark_score": None,
            "profile": profile_name,
            "reason": f"gate_status_{gate_status}",
            "dimension_scores": {},
            "provenance": {},
        }

    critic_dims = critic_report.get("dimension_scores") or {}
    domain_map = {
        "functional": "functional",
        "visual": "visual",
        "creative": "creative",
        "responsive": "responsive",
        "accessibility": "accessibility",
        "motion_quality": "motion_quality",
        "performance": "performance",
        "engineering": "engineering",
    }

    dim_scores: dict[str, float] = {}
    provenance: dict[str, str] = {}

    for dim, weight in weights.items():
        if dim == "three_d_quality":
            continue
        source_domain = domain_map.get(dim, dim)
        score = critic_dims.get(source_domain)
        if score is None:
            score = critic_dims.get(dim)
        if score is None:
            return {
                "benchmark_result": "BLOCKED",
                "benchmark_score": None,
                "profile": profile_name,
                "reason": f"missing_critic_score_for_{dim}",
                "dimension_scores": dim_scores,
                "provenance": provenance,
            }
        dim_scores[dim] = float(score)
        provenance[dim] = f"critic:{source_domain}"

    total = 0.0
    for dim, weight in weights.items():
        if dim == "three_d_quality":
            continue
        total += (dim_scores[dim] / 10.0) * float(weight)

    result = "PASS" if total >= 70.0 else "FAIL"
    return {
        "benchmark_result": result,
        "benchmark_score": round(total, 2),
        "profile": profile_name,
        "dimension_scores": dim_scores,
        "provenance": provenance,
        "reason": "gate_approved_evidence_backed_scoring",
    }
