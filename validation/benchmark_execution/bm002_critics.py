"""Independent critic evaluation for BM-002 cinematic 3D benchmark."""

from __future__ import annotations

from typing import Any


def _cinematic_critic(*, evidence_bundle: dict[str, Any], analysis: dict[str, Any]) -> dict[str, Any]:
    e012 = evidence_bundle.get("E-012") or {}
    e013 = evidence_bundle.get("E-013") or {}
    findings: list[dict[str, Any]] = []
    hard_failures: list[str] = []
    score = 8.0

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
    verdict = "FAIL" if score < 7.0 or hard_failures else "PASS"
    return {
        "critic_capability": "ACOS-06",
        "domain": "cinematic_direction",
        "verdict": verdict,
        "dimension_score": round(score, 2),
        "evidence_refs": ["evidence/E-012/scene_state_captures.json", "evidence/E-013/camera_scene_progression_log.json"],
        "findings": findings,
        "hard_failures": sorted(set(hard_failures)),
        "summary": f"Cinematic direction score {score}/10 — camera/scene progression from E-012/E-013.",
    }


def _3d_critic(*, evidence_bundle: dict[str, Any], analysis: dict[str, Any]) -> dict[str, Any]:
    review = evidence_bundle.get("E-011") or {}
    score = float(review.get("dimension_score", 0))
    hard_failures = list(review.get("hard_failures") or [])
    verdict = "FAIL" if score < 7.0 or hard_failures else "PASS"
    return {
        "critic_capability": "ACOS-12",
        "domain": "three_d_quality",
        "verdict": verdict,
        "dimension_score": score,
        "evidence_refs": ["evidence/E-011/3d_quality_review.json"],
        "findings": review.get("findings") or [],
        "hard_failures": hard_failures,
        "summary": f"3D quality score {score}/10 — geometry/materials/lighting from implementation + E-011.",
    }


def _visual_critic(*, analysis: dict[str, Any], visual_review: dict[str, Any], evidence_refs: list[str]) -> dict[str, Any]:
    score = float(visual_review.get("dimension_score", 0))
    findings = list(visual_review.get("findings") or [])
    hard_failures: list[str] = []
    if score < 7.0:
        findings.append({"check": "visual_quality_bar", "severity": "major", "detail": f"Visual score {score} below premium bar", "evidence_refs": evidence_refs})
    verdict = "FAIL" if score < 7.0 else "PASS"
    return {
        "critic_capability": "ACOS-10",
        "domain": "visual",
        "verdict": verdict,
        "dimension_score": score,
        "evidence_refs": evidence_refs,
        "findings": findings,
        "hard_failures": hard_failures,
        "summary": f"Visual review {score}/10 — 3D/DOM integration assessed from E-003 + viewports.",
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

    if "E-003" not in evidence_bundle:
        findings.append({"critic_capability": "ACOS-10", "domain": "visual", "verdict": "BLOCKED_INSUFFICIENT_EVIDENCE", "summary": "E-003 missing", "evidence_refs": []})
    elif "ACOS-10" in skills:
        findings.append(_visual_critic(analysis=analysis, visual_review=evidence_bundle["E-003"], evidence_refs=e001_refs + ["evidence/E-003/visual_consistency_review.json"]))

    if "ACOS-11" in skills:
        findings.append(_creative_critic(analysis=analysis, direction=direction, evidence_refs=e001_refs))

    if "ACOS-06" in skills or meaningful_3d_used:
        if "E-012" not in evidence_bundle or "E-013" not in evidence_bundle:
            findings.append({"critic_capability": "ACOS-06", "domain": "cinematic_direction", "verdict": "BLOCKED_INSUFFICIENT_EVIDENCE", "summary": "E-012/E-013 missing", "evidence_refs": []})
        else:
            findings.append(_cinematic_critic(evidence_bundle=evidence_bundle, analysis=analysis))

    if meaningful_3d_used and "ACOS-12" in skills:
        if "E-011" not in evidence_bundle:
            findings.append({"critic_capability": "ACOS-12", "domain": "three_d_quality", "verdict": "BLOCKED_INSUFFICIENT_EVIDENCE", "summary": "E-011 missing", "evidence_refs": []})
        else:
            findings.append(_3d_critic(evidence_bundle=evidence_bundle, analysis=analysis))

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
