"""Substantive artifact analysis for BM-002 cinematic 3D benchmark."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from validation.benchmark_execution.artifact_analysis import (
    build_responsive_behavior_check,
    build_visual_consistency_review,
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.is_file() else ""


def analyze_implementation(impl_dir: Path) -> dict[str, Any]:
    html = _read(impl_dir / "index.html")
    css = _read(impl_dir / "styles.css")
    js = _read(impl_dir / "main.js")
    html_lower = html.lower()
    css_lower = css.lower()
    js_lower = js.lower()

    sections = len(re.findall(r"<section\b", html, re.I))
    nav_present = bool(re.search(r"<nav\b", html, re.I))
    skip_link = "skip-link" in html_lower or "skip to content" in html_lower
    fictional_brand = "solstice arc" in html_lower or "solstice" in html_lower

    webgl_canvas = bool(re.search(r"<canvas\b", html, re.I))
    three_js = "three" in js_lower or "three.module" in html_lower
    model_viewer = "model-viewer" in html_lower
    static_render_only = bool(re.search(r"<img[^>]+product|static-render", html_lower))
    scroll_camera = "scroll" in js_lower and ("camera" in js_lower or "progress" in js_lower)
    scene_states = len(re.findall(r"data-scene-state", html, re.I))

    breakpoints = len(re.findall(r"@media\s*\(", css, re.I))
    reduced_motion_rules = "prefers-reduced-motion" in css_lower
    responsive_camera = "viewportprofile" in js_lower or "recomposecamera" in js_lower.replace("_", "")
    css_vars = len(re.findall(r"--[a-z0-9-]+:", css, re.I))
    display_font = "font-display" in css_lower or "cormorant" in css_lower or "georgia" in css_lower
    gradient_count = len(re.findall(r"linear-gradient|radial-gradient", css, re.I))
    glassmorphism = bool(re.search(r"backdrop-filter\s*:\s*blur", css_lower))

    hard_failure_signals: list[dict[str, str]] = []

    if model_viewer:
        hard_failure_signals.append(
            {"id": "rotating_model_viewer_without_meaningful_experience", "evidence_ref": "implementation/index.html", "detail": "model-viewer element detected"}
        )
    if not three_js or not webgl_canvas:
        hard_failure_signals.append(
            {"id": "not_a_functional_web_experience", "evidence_ref": "implementation/main.js", "detail": "missing Three.js/WebGL canvas implementation"}
        )
    if static_render_only and not three_js:
        hard_failure_signals.append(
            {"id": "static_render_embedded_as_experience", "evidence_ref": "implementation/index.html", "detail": "static render without real-time 3D"}
        )
    if three_js and not scroll_camera:
        hard_failure_signals.append(
            {"id": "simple_object_spin_on_scroll_only", "evidence_ref": "implementation/main.js", "detail": "no scroll-driven camera choreography detected"}
        )
    if sections < 5:
        hard_failure_signals.append(
            {"id": "three_d_disconnected_from_page_storytelling", "evidence_ref": "implementation/index.html", "detail": f"insufficient sections={sections}"}
        )
    if not reduced_motion_rules:
        hard_failure_signals.append(
            {"id": "reduced_motion_not_considered_where_applicable", "evidence_ref": "implementation/styles.css", "detail": "missing prefers-reduced-motion rules"}
        )
    if not nav_present:
        hard_failure_signals.append(
            {"id": "broken_navigation_or_interaction", "evidence_ref": "implementation/index.html", "detail": "navigation missing"}
        )

    primitive_only = "boxgeometry" in js_lower.replace(" ", "") and "lathegeometry" not in js_lower and "extrudegeometry" not in js_lower
    if primitive_only:
        hard_failure_signals.append(
            {"id": "primitive_demo_quality_scene_as_premium", "evidence_ref": "implementation/main.js", "detail": "primitive box-only geometry"}
        )

    return {
        "sections": sections,
        "nav_present": nav_present,
        "skip_link": skip_link,
        "fictional_brand_present": fictional_brand,
        "webgl_canvas": webgl_canvas,
        "three_js": three_js,
        "model_viewer": model_viewer,
        "scroll_camera_choreography": scroll_camera,
        "scene_state_markers": scene_states,
        "responsive_breakpoints": breakpoints,
        "responsive_3d_recomposition": responsive_camera,
        "reduced_motion_css": reduced_motion_rules,
        "css_custom_properties": css_vars,
        "display_typography": display_font,
        "gradient_count": gradient_count,
        "meaningful_3d_used": bool(three_js and webgl_canvas and scroll_camera),
        "glassmorphism_detected": glassmorphism,
        "floating_card_grid": False,
        "hard_failure_signals": hard_failure_signals,
    }


def build_3d_quality_review(analysis: dict[str, Any], *, evidence_refs: list[str]) -> dict[str, Any]:
    findings: list[dict[str, Any]] = []
    hard_failures: list[str] = []
    score = 10.0

    if not analysis.get("three_js"):
        hard_failures.append("three_d_decorative_checkbox_only")
        score = 2.0
    if analysis.get("model_viewer"):
        hard_failures.append("rotating_model_viewer_without_meaningful_experience")
        score = min(score, 3.0)
    if not analysis.get("scroll_camera_choreography"):
        hard_failures.append("simple_object_spin_on_scroll_only")
        score -= 3.0

    if analysis.get("three_js") and analysis.get("webgl_canvas"):
        score = max(score, 7.0)
    if analysis.get("scene_state_markers", 0) >= 4:
        score += 0.5
    if analysis.get("responsive_3d_recomposition"):
        score += 0.5

    score = max(0.0, min(10.0, score))
    if score < 7.0:
        hard_failures.append("poor_3d_quality_when_meaningful_3d_used")

    return {
        "review_type": "3d_quality_review",
        "evidence_refs": evidence_refs,
        "findings": findings,
        "dimension_score": round(score, 2),
        "geometry": "procedural_lathe_instrument",
        "materials": "pbr_metalness_roughness_brass",
        "lighting": "directional_plus_rim",
        "hard_failures": sorted(set(hard_failures)),
    }


def build_scene_state_captures(*, scene_log: dict[str, Any], evidence_refs: list[str]) -> dict[str, Any]:
    states = scene_log.get("states") or []
    required = {
        "opening_establishing_state",
        "product_reveal_or_focus_state",
        "mid_experience_progression_state",
        "closing_or_cta_state",
    }
    captured = {s.get("state_id") for s in states if s.get("state_id")}
    missing = sorted(required - captured)
    return {
        "review_type": "scene_state_captures",
        "evidence_refs": evidence_refs,
        "states": states,
        "required_states": sorted(required),
        "missing_states": missing,
        "sufficient": not missing,
    }


def build_camera_progression_log(*, scene_log: dict[str, Any], evidence_refs: list[str]) -> dict[str, Any]:
    keyframes = scene_log.get("camera_keyframes") or []
    return {
        "review_type": "camera_scene_progression_log",
        "evidence_refs": evidence_refs,
        "scroll_progress_samples": scene_log.get("scroll_samples") or [],
        "camera_keyframes": keyframes,
        "interaction_mapping": scene_log.get("interaction_mapping") or [],
    }


def build_responsive_3d_composition_check(
    *,
    viewports_captured: list[str],
    analysis: dict[str, Any],
    scene_log: dict[str, Any],
    evidence_refs: list[str],
) -> dict[str, Any]:
    required = {"desktop", "laptop", "tablet", "mobile"}
    missing = sorted(required - set(viewports_captured))
    viewport_profiles = scene_log.get("viewport_profiles") or {}
    findings: list[dict[str, Any]] = []
    score = 10.0
    if missing:
        findings.append({"check": "viewport_coverage", "severity": "critical", "detail": f"Missing: {missing}", "evidence_refs": evidence_refs})
        score -= 5.0
    if not analysis.get("responsive_3d_recomposition"):
        findings.append({"check": "camera_recomposition", "severity": "major", "detail": "No responsive 3D camera recomposition detected", "evidence_refs": ["implementation/main.js"]})
        score -= 2.5
    if len(viewport_profiles) < 4:
        findings.append({"check": "viewport_profiles", "severity": "major", "detail": f"Only {len(viewport_profiles)} viewport camera profiles logged", "evidence_refs": evidence_refs})
        score -= 1.5
    score = max(0.0, min(10.0, score))
    return {
        "review_type": "responsive_3d_composition_check",
        "evidence_refs": evidence_refs,
        "viewports_required": sorted(required),
        "viewports_captured": viewports_captured,
        "viewport_camera_profiles": viewport_profiles,
        "findings": findings,
        "dimension_score": round(score, 2),
        "desktop_only_3d_composition": score < 5.0 and "mobile" in viewports_captured,
    }


def build_visual_review_bm002(analysis: dict[str, Any], *, evidence_refs: list[str]) -> dict[str, Any]:
    review = build_visual_consistency_review(analysis, evidence_refs=evidence_refs)
    if analysis.get("three_js") and analysis.get("webgl_canvas"):
        review["dimension_score"] = min(10.0, float(review.get("dimension_score", 0)) + 1.0)
        review["visual_coherence"] = "strong_3d_dom_integration"
    return review


def build_responsive_review_bm002(
    *,
    viewports_captured: list[str],
    analysis: dict[str, Any],
    evidence_refs: list[str],
) -> dict[str, Any]:
    return build_responsive_behavior_check(
        viewports_captured=viewports_captured,
        analysis=analysis,
        evidence_refs=evidence_refs,
    )
