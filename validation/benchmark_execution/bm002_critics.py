"""Independent critic evaluation for BM-002 cinematic 3D benchmark."""

from __future__ import annotations

from validation.benchmark_execution.critic_integrity import (
    cap_score_for_review_basis,
    independent_rendered_review_complete,
    review_is_producer_derived,
    scene_log_is_self_reported,
    validate_premium_score_requires_substance,
)


def _cinematic_critic(
    *,
    evidence_bundle: dict[str, Any],
    analysis: dict[str, Any],
    viewport_manifest: dict[str, Any] | None,
) -> dict[str, Any]:
    e012 = evidence_bundle.get("E-012") or {}
    e013 = evidence_bundle.get("E-013") or {}
    scene_log = evidence_bundle.get("scene_log") or {}
    findings: list[dict[str, Any]] = []
    hard_failures: list[str] = []
    score = 8.0

    if scene_log_is_self_reported(scene_log):
        findings.append(
            {
                "check": "scene_telemetry_independence",
                "severity": "major",
                "detail": "Scene/camera progression self-reported by implementation; not independently verified",
                "evidence_refs": ["evidence/E-007/scene_progression.json"],
            }
        )
        score -= 2.0

    if not independent_rendered_review_complete(viewport_manifest):
        findings.append(
            {
                "check": "rendered_cinematic_review",
                "severity": "major",
                "detail": "No independent rendered-output review of cinematic composition",
                "evidence_refs": ["evidence/E-001/manifest.yaml"],
            }
        )
        score -= 2.0

    if not e012.get("sufficient"):
        findings.append({"check": "scene_states", "severity": "major", "detail": f"Missing scene states: {e012.get('missing_states')}", "evidence_refs": ["evidence/E-012/scene_state_captures.json"]})
        score -= 3.0
    keyframes = e013.get("camera_keyframes") or []
    if len(keyframes) < 3:
        findings.append({"check": "camera_progression", "severity": "major", "detail": "Insufficient camera keyframes logged", "evidence_refs": ["evidence/E-013/camera_scene_progression_log.json"]})
        score -= 2.0
    if not analysis.get("scroll_camera_choreography"):
        hard_failures.append("no_intentional_cinematic_camera_work")
        score -= 4.0

    score = max(0.0, min(10.0, score))
    score, _ = cap_score_for_review_basis(
        domain="cinematic_direction",
        score=score,
        producer_derived=scene_log_is_self_reported(scene_log),
        rendered_review_complete=independent_rendered_review_complete(viewport_manifest),
    )
    integrity_notes = validate_premium_score_requires_substance(domain="cinematic_direction", score=score, findings=findings)
    for note in integrity_notes:
        findings.append({"check": "premium_score_substance", "severity": "major", "detail": note, "evidence_refs": ["evidence/E-012/scene_state_captures.json"]})
        score = min(score, 8.9)

    verdict = "FAIL" if score < 7.0 or hard_failures else "PASS"
    return {
        "critic_capability": "ACOS-06",
        "domain": "cinematic_direction",
        "verdict": verdict,
        "dimension_score": round(score, 2),
        "evidence_refs": ["evidence/E-012/scene_state_captures.json", "evidence/E-013/camera_scene_progression_log.json"],
        "findings": findings,
        "hard_failures": sorted(set(hard_failures)),
        "summary": f"Cinematic direction score {score}/10 — requires independent rendered review; self-reported telemetry capped.",
    }


def _3d_critic(
    *,
    evidence_bundle: dict[str, Any],
    analysis: dict[str, Any],
    viewport_manifest: dict[str, Any] | None,
) -> dict[str, Any]:
    review = evidence_bundle.get("E-011") or {}
    findings = list(review.get("findings") or [])
    hard_failures = list(review.get("hard_failures") or [])
    score = float(review.get("dimension_score", 0))

    if review_is_producer_derived(review):
        findings.append(
            {
                "check": "3d_review_independence",
                "severity": "critical",
                "detail": "E-011 produced by producer static analysis; ACOS-12 requires rendered/runtime 3D evidence",
                "evidence_refs": ["evidence/E-011/3d_quality_review.json"],
            }
        )
    if not independent_rendered_review_complete(viewport_manifest):
        findings.append(
            {
                "check": "rendered_3d_review",
                "severity": "critical",
                "detail": "No independent rendered 3D critique of geometry/materials/lighting",
                "evidence_refs": ["evidence/E-001/manifest.yaml"],
            }
        )

    score, _ = cap_score_for_review_basis(
        domain="three_d_quality",
        score=score,
        producer_derived=review_is_producer_derived(review),
        rendered_review_complete=independent_rendered_review_complete(viewport_manifest),
    )
    for note in validate_premium_score_requires_substance(domain="three_d_quality", score=score, findings=findings):
        findings.append({"check": "premium_score_substance", "severity": "major", "detail": note, "evidence_refs": ["evidence/E-011/3d_quality_review.json"]})
        score = min(score, 8.9)

    verdict = "FAIL" if score < 7.0 or hard_failures else "PASS"
    if review_is_producer_derived(review) and not independent_rendered_review_complete(viewport_manifest):
        verdict = "BLOCKED_INSUFFICIENT_EVIDENCE"
    return {
        "critic_capability": "ACOS-12",
        "domain": "three_d_quality",
        "verdict": verdict,
        "dimension_score": round(score, 2),
        "evidence_refs": ["evidence/E-011/3d_quality_review.json", "evidence/E-001/manifest.yaml"],
        "findings": findings,
        "hard_failures": hard_failures,
        "summary": f"3D quality score {score}/10 — capped without independent rendered 3D review.",
    }


def _visual_critic(
    *,
    analysis: dict[str, Any],
    visual_review: dict[str, Any],
    evidence_refs: list[str],
    viewport_manifest: dict[str, Any] | None,
) -> dict[str, Any]:
    score = float(visual_review.get("dimension_score", 0))
    findings = list(visual_review.get("findings") or [])
    hard_failures: list[str] = []

    if review_is_producer_derived(visual_review):
        findings.append(
            {
                "check": "visual_review_independence",
                "severity": "critical",
                "detail": "E-003 produced by producer static analysis; ACOS-10 requires rendered/browser evidence review",
                "evidence_refs": evidence_refs + ["evidence/E-003/visual_consistency_review.json"],
            }
        )
    if viewport_manifest and viewport_manifest.get("visual_quality_approved") is False:
        findings.append(
            {
                "check": "visual_quality_not_approved",
                "severity": "major",
                "detail": "Browser manifest visual_quality_approved=false — rendered output not independently approved",
                "evidence_refs": evidence_refs,
            }
        )
    if not independent_rendered_review_complete(viewport_manifest):
        findings.append(
            {
                "check": "rendered_visual_review",
                "severity": "critical",
                "detail": "Screenshots captured but no independent rendered visual critique performed",
                "evidence_refs": evidence_refs,
            }
        )

    score, _ = cap_score_for_review_basis(
        domain="visual",
        score=score,
        producer_derived=review_is_producer_derived(visual_review),
        rendered_review_complete=independent_rendered_review_complete(viewport_manifest),
    )
    for note in validate_premium_score_requires_substance(domain="visual", score=score, findings=findings):
        findings.append({"check": "premium_score_substance", "severity": "major", "detail": note, "evidence_refs": evidence_refs})
        score = min(score, 8.9)

    if score < 7.0:
        findings.append({"check": "visual_quality_bar", "severity": "major", "detail": f"Visual score {score} below premium bar", "evidence_refs": evidence_refs})

    if review_is_producer_derived(visual_review) and not independent_rendered_review_complete(viewport_manifest):
        verdict = "BLOCKED_INSUFFICIENT_EVIDENCE"
    else:
        verdict = "FAIL" if score < 7.0 else "PASS"
    return {
        "critic_capability": "ACOS-10",
        "domain": "visual",
        "verdict": verdict,
        "dimension_score": round(score, 2),
        "evidence_refs": evidence_refs,
        "findings": findings,
        "hard_failures": hard_failures,
        "summary": f"Visual review {score}/10 — capped without independent rendered-output inspection.",
    }


def _creative_critic(*, analysis: dict[str, Any], direction: dict[str, Any] | None, evidence_refs: list[str]) -> dict[str, Any]:
    score = 8.0
    hard_failures: list[str] = []
    findings: list[dict[str, Any]] = []
    if not analysis.get("fictional_brand_present"):
        hard_failures.append("no_intentional_creative_concept")
        score -= 3.0
    if analysis.get("sections", 0) < 5:
        score -= 2.0
        findings.append({"check": "experience_depth", "severity": "major", "detail": "Insufficient sections", "evidence_refs": evidence_refs})
    if direction and (direction.get("creative") or {}).get("product", {}).get("name"):
        score += 0.5
    score = max(0.0, min(10.0, score))
    verdict = "FAIL" if hard_failures or score < 7.0 else "PASS"
    return {
        "critic_capability": "ACOS-11",
        "domain": "creative",
        "verdict": verdict,
        "dimension_score": round(score, 2),
        "evidence_refs": evidence_refs + ["execution/direction/creative_direction.yaml"],
        "findings": findings,
        "hard_failures": sorted(set(hard_failures)),
        "summary": f"Creative review {score}/10 — Solstice Arc concept and section depth.",
    }


def _accessibility_critic(*, analysis: dict[str, Any], reduced_meta: dict[str, Any] | None, evidence_refs: list[str]) -> dict[str, Any]:
    score = 8.0
    hard_failures: list[str] = []
    findings: list[dict[str, Any]] = []
    if not analysis.get("reduced_motion_css"):
        hard_failures.append("reduced_motion_not_considered_where_applicable")
        score -= 4.0
    if reduced_meta and reduced_meta.get("console_errors_during_capture", 0) > 0:
        score -= 2.0
    score = max(0.0, min(10.0, score))
    verdict = "FAIL" if hard_failures else "PASS"
    return {
        "critic_capability": "EXT-A11Y-01",
        "domain": "accessibility",
        "verdict": verdict,
        "dimension_score": round(score, 2),
        "evidence_refs": evidence_refs,
        "findings": findings,
        "hard_failures": hard_failures,
        "summary": f"Accessibility {score}/10 — reduced-motion for 3D/DOM.",
    }


def evaluate_critics(
    *,
    routing: dict[str, Any],
    analysis: dict[str, Any],
    evidence_bundle: dict[str, Any],
    direction: dict[str, Any] | None,
    meaningful_3d_used: bool,
) -> dict[str, Any]:
    skills = set(routing.get("planned_skill_ids") or [])
    findings: list[dict[str, Any]] = []
    e001_refs = ["evidence/E-001/manifest.yaml"]
    viewport_manifest = evidence_bundle.get("E-001_manifest") or {}

    if "E-003" not in evidence_bundle:
        findings.append({"critic_capability": "ACOS-10", "domain": "visual", "verdict": "BLOCKED_INSUFFICIENT_EVIDENCE", "summary": "E-003 missing", "evidence_refs": []})
    elif "ACOS-10" in skills:
        findings.append(
            _visual_critic(
                analysis=analysis,
                visual_review=evidence_bundle["E-003"],
                evidence_refs=e001_refs + ["evidence/E-003/visual_consistency_review.json"],
                viewport_manifest=viewport_manifest,
            )
        )

    if "ACOS-11" in skills:
        findings.append(_creative_critic(analysis=analysis, direction=direction, evidence_refs=e001_refs))

    if "ACOS-06" in skills or meaningful_3d_used:
        if "E-012" not in evidence_bundle or "E-013" not in evidence_bundle:
            findings.append({"critic_capability": "ACOS-06", "domain": "cinematic_direction", "verdict": "BLOCKED_INSUFFICIENT_EVIDENCE", "summary": "E-012/E-013 missing", "evidence_refs": []})
        else:
            findings.append(_cinematic_critic(evidence_bundle=evidence_bundle, analysis=analysis, viewport_manifest=viewport_manifest))

    if meaningful_3d_used and "ACOS-12" in skills:
        if "E-011" not in evidence_bundle:
            findings.append({"critic_capability": "ACOS-12", "domain": "three_d_quality", "verdict": "BLOCKED_INSUFFICIENT_EVIDENCE", "summary": "E-011 missing", "evidence_refs": []})
        else:
            findings.append(_3d_critic(evidence_bundle=evidence_bundle, analysis=analysis, viewport_manifest=viewport_manifest))

    if "EXT-A11Y-01" in skills or meaningful_3d_used:
        findings.append(_accessibility_critic(analysis=analysis, reduced_meta=evidence_bundle.get("E-008_meta"), evidence_refs=["evidence/E-008/manifest.yaml"]))

    hard_fails = [f for f in findings if f.get("verdict") in ("FAIL", "REJECTED")]
    blocked = [f for f in findings if f.get("verdict") == "BLOCKED_INSUFFICIENT_EVIDENCE"]

    dimension_scores: dict[str, float] = {
        f["domain"]: float(f["dimension_score"])
        for f in findings
        if f.get("dimension_score") is not None
    }

    e004 = evidence_bundle.get("E-004") or {}
    if e004.get("dimension_score") is not None:
        dimension_scores["responsive"] = float(e004["dimension_score"])
    e014 = evidence_bundle.get("E-014") or {}
    if e014.get("dimension_score") is not None:
        dimension_scores["responsive"] = max(dimension_scores.get("responsive", 0), float(e014["dimension_score"]))

    e002 = evidence_bundle.get("E-002") or {}
    functional_score = 9.0 if e002.get("functional") and e002.get("real_time_webgl_three_d_scene_present") else 3.0
    dimension_scores["functional"] = functional_score

    perf = evidence_bundle.get("E-009") or {}
    dcl = perf.get("dom_content_loaded_ms", 99999)
    dimension_scores["performance"] = 9.0 if dcl < 4000 else (6.0 if dcl < 8000 else 3.0)

    eng_score = 9.0 if evidence_bundle.get("runtime_healthy") and evidence_bundle.get("network_failure_count", 0) == 0 else 4.0
    dimension_scores["engineering"] = eng_score

    interactions = (evidence_bundle.get("E-007") or {}).get("interactions") or []
    scroll_ix = sum(1 for i in interactions if i.get("type") in ("scroll_progress", "scroll_settle"))
    dimension_scores["motion_quality"] = 9.0 if scroll_ix >= 3 else 5.0

    return {
        "findings": findings,
        "hard_critic_failures": hard_fails,
        "blocked_critics": blocked,
        "independent_review_complete": len(findings) > 0 and not blocked,
        "dimension_scores": dimension_scores,
    }
