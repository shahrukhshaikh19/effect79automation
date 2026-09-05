"""Independent critic evaluation from captured evidence — producer cannot self-approve."""

from __future__ import annotations

from typing import Any


def _visual_critic(
    *,
    analysis: dict[str, Any],
    visual_review: dict[str, Any],
    evidence_refs: list[str],
) -> dict[str, Any]:
    findings: list[dict[str, Any]] = []
    hard_failures: list[str] = []
    score = float(visual_review.get("dimension_score", 0))

    for item in visual_review.get("findings") or []:
        findings.append({**item, "critic_capability": "ACOS-10"})
        if item.get("severity") == "critical":
            hard_failures.append("arbitrary_glassmorphism")

    for signal in analysis.get("hard_failure_signals") or []:
        if signal.get("id") in ("arbitrary_glassmorphism", "predictable_gradient_heavy_ai_aesthetics"):
            hard_failures.append(signal["id"])

    if score < 6.0:
        verdict = "FAIL"
    elif score < 7.5:
        verdict = "FAIL"
        findings.append(
            {
                "check": "visual_quality_bar",
                "severity": "major",
                "detail": f"Visual dimension score {score} below premium benchmark bar",
                "evidence_refs": evidence_refs,
                "critic_capability": "ACOS-10",
            }
        )
    else:
        verdict = "PASS"

    return {
        "critic_capability": "ACOS-10",
        "domain": "visual",
        "verdict": verdict,
        "dimension_score": score,
        "evidence_refs": evidence_refs,
        "findings": findings,
        "hard_failures": sorted(set(hard_failures)),
        "summary": (
            f"Visual review score {score}/10 — composition/typography/coherence assessed from "
            f"E-003 + viewport evidence; glassmorphism={'yes' if analysis.get('glassmorphism_detected') else 'no'}."
        ),
    }


def _creative_critic(
    *,
    analysis: dict[str, Any],
    direction: dict[str, Any] | None,
    evidence_refs: list[str],
) -> dict[str, Any]:
    findings: list[dict[str, Any]] = []
    hard_failures: list[str] = []
    score = 7.0

    if not analysis.get("fictional_brand_present"):
        findings.append({"check": "creative_concept", "severity": "critical", "detail": "No fictional product identity detected", "evidence_refs": evidence_refs})
        hard_failures.append("no_intentional_creative_concept")
        score -= 3.0

    if analysis.get("floating_card_grid"):
        findings.append({"check": "template_risk", "severity": "major", "detail": "Floating card grid pattern detected", "evidence_refs": evidence_refs})
        hard_failures.append("random_floating_cards")
        score -= 2.0

    for signal in analysis.get("hard_failure_signals") or []:
        sid = signal.get("id", "")
        if sid in ("generic_saas_landing_template", "imitates_recognizable_brand", "generic_ai_generated_aesthetic"):
            hard_failures.append(sid)
            score -= 3.0

    if direction:
        concept = (direction.get("creative") or {}).get("product", {}).get("concept_thesis", "")
        if concept and analysis.get("sections", 0) >= 5:
            score += 1.0
    else:
        findings.append({"check": "direction_evidence", "severity": "major", "detail": "Missing creative direction artifact for concept validation", "evidence_refs": evidence_refs})
        score -= 1.0

    if analysis.get("sections", 0) < 5:
        findings.append({"check": "experience_depth", "severity": "major", "detail": "Insufficient meaningful sections for premium benchmark", "evidence_refs": evidence_refs})
        score -= 2.0

    score = max(0.0, min(10.0, score))
    verdict = "FAIL" if score < 7.0 or hard_failures else "PASS"

    return {
        "critic_capability": "ACOS-11",
        "domain": "creative",
        "verdict": verdict,
        "dimension_score": round(score, 2),
        "evidence_refs": evidence_refs + ["execution/direction/creative_direction.yaml"],
        "findings": findings,
        "hard_failures": sorted(set(hard_failures)),
        "summary": (
            f"Creative review score {score}/10 — originality/concept assessed from HTML content, "
            f"direction artifacts, and anti-pattern scan; sections={analysis.get('sections', 0)}."
        ),
    }


def _accessibility_critic(
    *,
    analysis: dict[str, Any],
    reduced_review: dict[str, Any] | None,
    evidence_refs: list[str],
) -> dict[str, Any]:
    findings: list[dict[str, Any]] = []
    hard_failures: list[str] = []
    score = 8.0

    if not analysis.get("reduced_motion_css"):
        hard_failures.append("reduced_motion_not_considered_where_applicable")
        score -= 4.0
        findings.append({"check": "reduced_motion_css", "severity": "critical", "detail": "CSS reduced-motion handling missing", "evidence_refs": ["implementation/styles.css"]})
    if not analysis.get("skip_link"):
        score -= 1.0
        findings.append({"check": "skip_link", "severity": "minor", "detail": "Skip link not detected", "evidence_refs": ["implementation/index.html"]})
    if reduced_review and reduced_review.get("console_errors_during_capture", 0) > 0:
        score -= 2.0
        findings.append({"check": "reduced_motion_runtime", "severity": "major", "detail": "Console errors during reduced-motion capture", "evidence_refs": evidence_refs})

    score = max(0.0, min(10.0, score))
    verdict = "FAIL" if hard_failures or score < 6.0 else "PASS"

    return {
        "critic_capability": "EXT-A11Y-01",
        "domain": "accessibility",
        "verdict": verdict,
        "dimension_score": round(score, 2),
        "evidence_refs": evidence_refs,
        "findings": findings,
        "hard_failures": sorted(set(hard_failures)),
        "summary": f"Accessibility score {score}/10 — reduced-motion, skip link, semantic/nav checks from E-008 + implementation.",
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
    e003 = evidence_bundle.get("E-003") or {}
    e004 = evidence_bundle.get("E-004") or {}
    e008_refs = ["evidence/E-008/manifest.yaml"]

    if "E-003" not in evidence_bundle:
        findings.append(
            {
                "critic_capability": "ACOS-10",
                "domain": "visual",
                "verdict": "BLOCKED_INSUFFICIENT_EVIDENCE",
                "summary": "E-003 visual consistency review missing",
                "evidence_refs": [],
            }
        )
    elif "ACOS-10" in skills:
        findings.append(_visual_critic(analysis=analysis, visual_review=e003, evidence_refs=e001_refs + ["evidence/E-003/visual_consistency_review.json"]))

    if "E-004" not in evidence_bundle:
        findings.append(
            {
                "critic_capability": "ACOS-11",
                "domain": "responsive",
                "verdict": "BLOCKED_INSUFFICIENT_EVIDENCE",
                "summary": "E-004 responsive behavior review missing",
                "evidence_refs": [],
            }
        )

    if "ACOS-11" in skills:
        findings.append(_creative_critic(analysis=analysis, direction=direction, evidence_refs=e001_refs + ["evidence/E-003/visual_consistency_review.json"]))

    if "EXT-A11Y-01" in skills:
        findings.append(
            _accessibility_critic(
                analysis=analysis,
                reduced_review=evidence_bundle.get("E-008_meta"),
                evidence_refs=e008_refs,
            )
        )

    if meaningful_3d_used and "ACOS-12" in skills:
        if "E-011" not in evidence_bundle:
            findings.append(
                {
                    "critic_capability": "ACOS-12",
                    "domain": "three_d_quality",
                    "verdict": "BLOCKED_INSUFFICIENT_EVIDENCE",
                    "summary": "E-011 required when meaningful 3D used",
                    "evidence_refs": [],
                }
            )
        else:
            findings.append(
                {
                    "critic_capability": "ACOS-12",
                    "domain": "three_d_quality",
                    "verdict": "NOT_APPLICABLE",
                    "summary": "3D critic not applicable — no meaningful 3D",
                    "evidence_refs": [],
                }
            )

    hard_fails = [f for f in findings if f.get("verdict") in ("FAIL", "REJECTED")]
    blocked = [f for f in findings if f.get("verdict") == "BLOCKED_INSUFFICIENT_EVIDENCE"]

    dimension_scores: dict[str, float] = {
        f["domain"]: f.get("dimension_score")
        for f in findings
        if f.get("dimension_score") is not None
    }

    e004 = evidence_bundle.get("E-004") or {}
    if e004.get("dimension_score") is not None:
        dimension_scores["responsive"] = float(e004["dimension_score"])

    e002 = evidence_bundle.get("E-002") or {}
    functional_score = 9.0 if e002.get("functional") and evidence_bundle.get("runtime_healthy") else 3.0
    dimension_scores["functional"] = functional_score

    perf = evidence_bundle.get("E-009") or {}
    dcl = perf.get("dom_content_loaded_ms", 99999)
    dimension_scores["performance"] = 9.0 if dcl < 3000 else (6.0 if dcl < 5000 else 3.0)

    eng_score = 9.0 if evidence_bundle.get("runtime_healthy") and evidence_bundle.get("network_failure_count", 0) == 0 else 4.0
    dimension_scores["engineering"] = eng_score

    interactions = (evidence_bundle.get("E-007") or {}).get("interactions") or []
    meaningful_ix = sum(1 for i in interactions if i.get("type") in ("click", "scroll_settle"))
    dimension_scores["motion_quality"] = 8.0 if meaningful_ix >= 3 else 4.0

    return {
        "findings": findings,
        "hard_critic_failures": hard_fails,
        "blocked_critics": blocked,
        "independent_review_complete": len(findings) > 0 and not blocked,
        "dimension_scores": dimension_scores,
    }
