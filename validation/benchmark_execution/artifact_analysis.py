"""Substantive artifact analysis for BM-001 critic and evidence generation."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any


GENERIC_SAAS_MARKERS = (
    "trusted by",
    "get started free",
    "join thousands",
    "all-in-one platform",
    "supercharge your",
)

BRAND_MARKERS = (
    "apple",
    "stripe",
    "linear",
    "tesla",
    "nothing phone",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.is_file() else ""


def analyze_implementation(impl_dir: Path) -> dict[str, Any]:
    html = _read(impl_dir / "index.html")
    css = _read(impl_dir / "styles.css")
    js = _read(impl_dir / "main.js")
    html_lower = html.lower()
    css_lower = css.lower()

    sections = len(re.findall(r"<section\b", html, re.I))
    h1_count = len(re.findall(r"<h1\b", html, re.I))
    nav_present = bool(re.search(r"<nav\b", html, re.I))
    skip_link = "skip-link" in html_lower or "skip to content" in html_lower
    aria_labels = len(re.findall(r"aria-", html, re.I))
    fictional_brand = "helix meridian" in html_lower or "helix" in html_lower

    css_vars = len(re.findall(r"--[a-z0-9-]+:", css, re.I))
    display_font = "font-display" in css_lower or "georgia" in css_lower
    breakpoints = len(re.findall(r"@media\s*\(", css, re.I))
    reduced_motion_rules = "prefers-reduced-motion" in css_lower
    glassmorphism = "backdrop-filter" in css_lower or re.search(r"backdrop-filter\s*:\s*blur", css_lower)
    gradient_count = len(re.findall(r"linear-gradient|radial-gradient", css, re.I))
    glow_heavy = len(re.findall(r"box-shadow:[^;]{0,80}(0\s+0\s+\d+px|rgba?\([^)]*,\s*0\.[5-9])", css, re.I))
    floating_card_grid = bool(re.search(r"card.*grid|grid.*card", css_lower)) and sections <= 4

    js_interactions = sum(
        1 for token in ("addEventListener", "IntersectionObserver", "classList", "aria-expanded") if token in js
    )
    reduced_motion_js = "prefers-reduced-motion" in js or "matchMedia" in js

    generic_markers_found = [m for m in GENERIC_SAAS_MARKERS if m in html_lower]
    brand_imitation_found = [m for m in BRAND_MARKERS if m in html_lower]

    hard_failure_signals: list[dict[str, str]] = []
    if glassmorphism:
        hard_failure_signals.append(
            {"id": "arbitrary_glassmorphism", "evidence_ref": "implementation/styles.css", "detail": "backdrop-filter blur on header"}
        )
    if gradient_count >= 4:
        hard_failure_signals.append(
            {"id": "predictable_gradient_heavy_ai_aesthetics", "evidence_ref": "implementation/styles.css", "detail": f"{gradient_count} gradient declarations"}
        )
    if generic_markers_found:
        hard_failure_signals.append(
            {"id": "generic_saas_landing_template", "evidence_ref": "implementation/index.html", "detail": ", ".join(generic_markers_found)}
        )
    if brand_imitation_found:
        hard_failure_signals.append(
            {"id": "imitates_recognizable_brand", "evidence_ref": "implementation/index.html", "detail": ", ".join(brand_imitation_found)}
        )
    if not nav_present or sections < 5:
        hard_failure_signals.append(
            {"id": "broken_navigation_or_interaction", "evidence_ref": "implementation/index.html", "detail": f"nav={nav_present}, sections={sections}"}
        )
    if not reduced_motion_rules:
        hard_failure_signals.append(
            {"id": "reduced_motion_not_considered_where_applicable", "evidence_ref": "implementation/styles.css", "detail": "missing prefers-reduced-motion rules"}
        )

    return {
        "sections": sections,
        "h1_count": h1_count,
        "nav_present": nav_present,
        "skip_link": skip_link,
        "aria_labels": aria_labels,
        "fictional_brand_present": fictional_brand,
        "css_custom_properties": css_vars,
        "display_typography": display_font,
        "responsive_breakpoints": breakpoints,
        "reduced_motion_css": reduced_motion_rules,
        "reduced_motion_js": reduced_motion_js,
        "interaction_handlers": js_interactions,
        "glassmorphism_detected": bool(glassmorphism),
        "gradient_count": gradient_count,
        "glow_heavy_count": glow_heavy,
        "floating_card_grid": floating_card_grid,
        "hard_failure_signals": hard_failure_signals,
    }


def build_visual_consistency_review(analysis: dict[str, Any], *, evidence_refs: list[str]) -> dict[str, Any]:
    findings: list[dict[str, Any]] = []
    score = 10.0

    if analysis.get("css_custom_properties", 0) < 4:
        findings.append({"check": "visual_system", "severity": "major", "detail": "Limited CSS custom property system", "evidence_refs": evidence_refs})
        score -= 2.0
    if not analysis.get("display_typography"):
        findings.append({"check": "typography", "severity": "major", "detail": "No deliberate display typography detected", "evidence_refs": evidence_refs})
        score -= 2.5
    if analysis.get("glassmorphism_detected"):
        findings.append({"check": "art_direction", "severity": "critical", "detail": "Glassmorphism/backdrop blur detected", "evidence_refs": evidence_refs + ["implementation/styles.css"]})
        score -= 4.0
    if analysis.get("gradient_count", 0) >= 4:
        findings.append({"check": "visual_coherence", "severity": "major", "detail": "Gradient-heavy aesthetic risk", "evidence_refs": evidence_refs})
        score -= 1.5

    score = max(0.0, min(10.0, score))
    return {
        "review_type": "visual_consistency_review",
        "evidence_refs": evidence_refs,
        "findings": findings,
        "dimension_score": round(score, 2),
        "composition": "sectioned editorial layout with typographic hero",
        "typography": "display serif + system UI sans",
        "visual_coherence": "moderate" if score >= 6 else "weak",
    }


def build_responsive_behavior_check(
    *,
    viewports_captured: list[str],
    analysis: dict[str, Any],
    evidence_refs: list[str],
) -> dict[str, Any]:
    required = {"desktop", "laptop", "tablet", "mobile"}
    missing = sorted(required - set(viewports_captured))
    findings: list[dict[str, Any]] = []
    score = 10.0

    if missing:
        findings.append({"check": "viewport_coverage", "severity": "critical", "detail": f"Missing viewports: {missing}", "evidence_refs": evidence_refs})
        score -= 5.0
    if analysis.get("responsive_breakpoints", 0) < 2:
        findings.append({"check": "responsive_css", "severity": "major", "detail": "Insufficient responsive breakpoints in CSS", "evidence_refs": ["implementation/styles.css"]})
        score -= 2.0

    score = max(0.0, min(10.0, score))
    return {
        "review_type": "responsive_behavior_check",
        "evidence_refs": evidence_refs,
        "viewports_required": sorted(required),
        "viewports_captured": viewports_captured,
        "missing_viewports": missing,
        "findings": findings,
        "dimension_score": round(score, 2),
        "catastrophic_breakage_detected": bool(missing),
    }
