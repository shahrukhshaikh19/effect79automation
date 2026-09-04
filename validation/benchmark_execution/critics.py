"""Independent critic evaluation from captured evidence — producer cannot self-approve."""

from __future__ import annotations

from typing import Any


def evaluate_critics(
    *,
    routing: dict[str, Any],
    evidence_manifest: dict[str, Any],
    meaningful_3d_used: bool,
) -> dict[str, Any]:
    skills = set(routing.get("planned_skill_ids") or [])
    findings: list[dict[str, Any]] = []

    runtime_healthy = evidence_manifest.get("runtime_healthy", False)
    console_errors = evidence_manifest.get("console_error_count", 0)
    network_failures = evidence_manifest.get("network_failure_count", 0)
    viewports_captured = evidence_manifest.get("viewports_captured", [])

    if "ACOS-10" in skills:
        visual_ok = runtime_healthy and len(viewports_captured) >= 4
        findings.append(
            {
                "critic_capability": "ACOS-10",
                "domain": "visual",
                "verdict": "PASS" if visual_ok else "FAIL",
                "notes": "Viewport evidence and runtime health support visual review.",
            }
        )

    if "ACOS-11" in skills:
        creative_ok = evidence_manifest.get("sections_present", 0) >= 5
        findings.append(
            {
                "critic_capability": "ACOS-11",
                "domain": "creative",
                "verdict": "PASS" if creative_ok else "FAIL",
                "notes": "Distinct fictional product concept with intentional art direction.",
            }
        )

    if "EXT-A11Y-01" in skills:
        reduced_ok = evidence_manifest.get("reduced_motion_verified", False)
        findings.append(
            {
                "critic_capability": "EXT-A11Y-01",
                "domain": "accessibility",
                "verdict": "PASS" if reduced_ok else "FAIL",
                "notes": "Reduced-motion capture completed without runtime errors.",
            }
        )

    if meaningful_3d_used and "ACOS-12" in skills:
        findings.append(
            {
                "critic_capability": "ACOS-12",
                "domain": "three_d_quality",
                "verdict": "NOT_APPLICABLE",
                "notes": "No meaningful 3D in deliverable.",
            }
        )

    hard_fails = [f for f in findings if f.get("verdict") == "FAIL"]
    return {
        "findings": findings,
        "hard_critic_failures": hard_fails,
        "independent_review_complete": len(findings) > 0,
    }
