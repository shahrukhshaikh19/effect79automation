"""Critic independence and rendered-evidence integrity checks for benchmark execution."""

from __future__ import annotations

from typing import Any

# Domains that require independent rendered-output review for flagship benchmarks.
RENDERED_REVIEW_DOMAINS = frozenset({"visual", "three_d_quality", "cinematic_direction"})

# Maximum scores when only producer/static analysis exists (no rendered critique).
MAX_SCORE_WITHOUT_INDEPENDENT_RENDERED_REVIEW: dict[str, float] = {
    "visual": 6.0,
    "three_d_quality": 7.0,
    "cinematic_direction": 7.0,
}

PREMIUM_SCORE_THRESHOLD = 9.0
PASS_THRESHOLD = 7.0


def review_is_producer_derived(review: dict[str, Any] | None) -> bool:
    if not review:
        return True
    if review.get("independent_critic_review") is True:
        return False
    if review.get("producer_authored") is True:
        return True
    basis = str(review.get("review_basis") or "")
    return basis in ("static_source_analysis", "producer_pipeline_derived")


def manifest_has_render_captures(manifest: dict[str, Any] | None, *, min_viewports: int = 4) -> bool:
    if not manifest:
        return False
    captures = manifest.get("captures") or []
    viewports = {
        c.get("viewport", {}).get("name")
        for c in captures
        if c.get("screenshot_path") or c.get("capture_type") in ("viewport", "full_page")
    }
    viewports.discard(None)
    return len(viewports) >= min_viewports


def independent_rendered_review_complete(manifest: dict[str, Any] | None) -> bool:
    """True only when rendered evidence was independently reviewed (not merely captured)."""
    if not manifest:
        return False
    if manifest.get("independent_rendered_review_complete") is True:
        return True
    if manifest.get("visual_quality_approved") is True:
        return True
    return False


def scene_log_is_self_reported(scene_log: dict[str, Any] | None) -> bool:
    """Scene telemetry authored by implementation (e.g. window.__SCENE__) is not independent."""
    if not scene_log:
        return True
    if scene_log.get("independent_capture_verified") is True:
        return False
    return bool(scene_log.get("self_reported") or scene_log.get("source") == "implementation_global")


def validate_premium_score_requires_substance(
    *,
    domain: str,
    score: float,
    findings: list[Any],
    positive_evidence: list[Any] | None = None,
) -> list[str]:
    violations: list[str] = []
    if score >= PREMIUM_SCORE_THRESHOLD and not findings and not positive_evidence:
        violations.append(
            f"{domain}: score {score}>={PREMIUM_SCORE_THRESHOLD} without substantive findings or positive_evidence"
        )
    return violations


def cap_score_for_review_basis(
    *,
    domain: str,
    score: float,
    producer_derived: bool,
    rendered_review_complete: bool,
) -> tuple[float, list[str]]:
    """Cap inflated scores when critics did not inspect rendered output."""
    notes: list[str] = []
    capped = score
    if domain in RENDERED_REVIEW_DOMAINS and not rendered_review_complete:
        ceiling = MAX_SCORE_WITHOUT_INDEPENDENT_RENDERED_REVIEW.get(domain, PASS_THRESHOLD)
        if producer_derived and capped > ceiling:
            notes.append(
                f"{domain}: capped {capped}->{ceiling} (producer/static review; no independent rendered critique)"
            )
            capped = ceiling
    return capped, notes


def assess_critic_integrity(
    *,
    critic_report: dict[str, Any],
    evidence_bundle: dict[str, Any],
    viewport_manifest: dict[str, Any] | None,
    benchmark_id: str = "BM-002",
) -> dict[str, Any]:
    """
    Detect false-pass patterns: producer-derived reviews, unrated screenshots,
    self-reported scene logs, and premium scores without substance.
    """
    violations: list[str] = []
    mechanisms: list[str] = []
    rendered_complete = independent_rendered_review_complete(viewport_manifest)
    has_captures = manifest_has_render_captures(viewport_manifest)

    e003 = evidence_bundle.get("E-003") or {}
    e011 = evidence_bundle.get("E-011") or {}
    scene_log = evidence_bundle.get("scene_log") or {}

    if review_is_producer_derived(e003):
        mechanisms.append("producer_derived_visual_review")
        violations.append("E-003 visual_consistency_review is producer/static-derived, not independent critic output")
    if review_is_producer_derived(e011):
        mechanisms.append("producer_derived_3d_review")
        violations.append("E-011 3d_quality_review is producer/static-derived, not independent critic output")
    if scene_log_is_self_reported(scene_log):
        mechanisms.append("self_reported_scene_telemetry")
        violations.append("E-012/E-013 scene progression sourced from implementation self-report, not verified capture")

    if has_captures and not rendered_complete:
        mechanisms.append("screenshots_not_interpreted")
        violations.append(
            "Browser screenshots captured but independent_rendered_review_complete=false "
            "and visual_quality_approved=false — renders were not visually critiqued"
        )

    manifest_vqa = viewport_manifest.get("visual_quality_approved") if viewport_manifest else None
    for finding in critic_report.get("findings") or []:
        domain = finding.get("domain", "")
        score = float(finding.get("dimension_score") or 0)
        findings_list = finding.get("findings") or []

        violations.extend(
            validate_premium_score_requires_substance(
                domain=domain,
                score=score,
                findings=findings_list,
                positive_evidence=finding.get("positive_evidence"),
            )
        )

        if domain == "visual" and score >= PASS_THRESHOLD and manifest_vqa is False:
            mechanisms.append("visual_quality_approved_contradiction")
            violations.append(
                f"visual critic PASS/score {score} while E-001 manifest visual_quality_approved=false"
            )

        if domain in RENDERED_REVIEW_DOMAINS and score >= PASS_THRESHOLD and not rendered_complete:
            producer = review_is_producer_derived(e003 if domain == "visual" else e011 if domain == "three_d_quality" else None)
            if producer or domain == "cinematic_direction":
                mechanisms.append(f"{domain}_pass_without_rendered_review")
                violations.append(f"{domain} score {score}>=pass without independent rendered-output review")

    integrity_ok = not violations
    return {
        "benchmark_id": benchmark_id,
        "integrity_ok": integrity_ok,
        "rendered_captures_present": has_captures,
        "independent_rendered_review_complete": rendered_complete,
        "producer_derived_visual_review": review_is_producer_derived(e003),
        "producer_derived_3d_review": review_is_producer_derived(e011),
        "self_reported_scene_telemetry": scene_log_is_self_reported(scene_log),
        "false_pass_mechanisms": sorted(set(mechanisms)),
        "violations": violations,
    }
