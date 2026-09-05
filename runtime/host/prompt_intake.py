"""Build a domain-neutral intake from a freeform project request."""

from __future__ import annotations

import re
import uuid
from typing import Any

from runtime.host.capabilities import host_capabilities
from runtime.intake.normalize import normalize_intake

_3D = re.compile(
    r"\b(3d|three\.?js|webgl|webgpu|blender|glb|gltf|r3f|react-three|webxr|cinematic 3d)\b",
    re.I,
)
_MOTION = re.compile(
    r"\b(scroll[- ]driven|scroll drives|gsap|timeline|parallax|choreograph|animation-heavy|motion)\b",
    re.I,
)
_VISUAL = re.compile(
    r"\b(website|landing|launch site|brand|visual|cinematic|hero|typography|art direction|experience)\b",
    re.I,
)
_REF_MOOD = re.compile(
    r"\b(reference image|reference still|mood reference|composition only)\b",
    re.I,
)
_RECONSTRUCT = re.compile(
    r"\b(img2three|match this image|reconstruct this|rebuild this image)\b",
    re.I,
)
_NO_RECONSTRUCT = re.compile(r"\b(do not reconstruct|don't reconstruct|not reconstruct)\b", re.I)
_A11Y = re.compile(r"\b(a11y|accessibility|wcag|screen reader)\b", re.I)
_FLAGSHIP = re.compile(
    r"\b(premium|cinematic|flagship|physical (tech(?:nology)?|product|instrument)|"
    r"launch (site|website)|hero product|scroll[- ]driven|hydrographic|"
    r"meaningful real-time|webgl/three\.js)\b",
    re.I,
)
_BLENDER_REQUIRED = re.compile(
    r"\b("
    r"blender must|must model|export glb|export gltf|hero glb|"
    r"if blender mcp|do not skip blender|"
    r"blender to model|model this .{0,80}export"
    r")\b",
    re.I,
)
_SCROLL_STORY = re.compile(r"\b(scroll is|scroll equals|scroll =|scroll states|this order only)\b", re.I)
_LIVE_SCENE = re.compile(r"\b(ripple|foliage|wind is blowing|hover and drag|live 3d)\b", re.I)
_PHYSICAL_PRODUCT = re.compile(
    r"\b("
    r"headphone|headset|earcup|over-ear|in-ear|yoke|"
    r"physical (product|instrument|device|object)|"
    r"hero product|anodized|watch|camera body|keyboard"
    r")\b",
    re.I,
)


def classify_signals(prompt: str) -> dict[str, Any]:
    text = prompt.strip()
    wants_3d = bool(_3D.search(text))
    wants_reconstruct = bool(_RECONSTRUCT.search(text)) and not _NO_RECONSTRUCT.search(text)
    wants_ref = wants_reconstruct or bool(_REF_MOOD.search(text))
    wants_visual = bool(_VISUAL.search(text)) or wants_3d
    wants_motion = bool(_MOTION.search(text)) or bool(_SCROLL_STORY.search(text)) or bool(_LIVE_SCENE.search(text))
    authored = bool(_FLAGSHIP.search(text) or _BLENDER_REQUIRED.search(text))
    if wants_3d and authored:
        profile = "interactive_3d"
        reconstruction = "blender_authoring"
    elif wants_reconstruct and wants_3d:
        profile = "reference_reconstruction"
        reconstruction = "procedural_browser"
    elif wants_3d:
        profile = "interactive_3d"
        reconstruction = "blender_authoring" if authored else "none"
    elif wants_visual:
        profile = "visual_experience"
        reconstruction = "none"
    else:
        profile = "standard_application"
        reconstruction = "none"
    return {
        "deliverable_profile": profile,
        "requires_3d": wants_3d,
        "requires_visual_output": wants_visual,
        "requires_creative_direction": wants_visual,
        "requires_motion": wants_motion,
        "requires_responsive": wants_visual or wants_3d,
        "requires_accessibility": bool(_A11Y.search(text)) or wants_visual,
        "requires_frontend": True,
        "requires_reference_analysis": wants_ref,
        "requires_physical_product": bool(_PHYSICAL_PRODUCT.search(text)),
        "reconstruction_path": reconstruction,
        "quality_bar": "flagship" if wants_3d and reconstruction == "blender_authoring" else "standard",
    }


def intake_from_prompt(prompt: str, *, task_id: str | None = None) -> dict[str, Any]:
    if not prompt.strip():
        raise ValueError("Project prompt is empty")
    signals = classify_signals(prompt)
    goal = _normalized_goal(prompt)
    return normalize_intake(
        {
            "task_id": task_id or f"host-{uuid.uuid4().hex[:12]}",
            "request": prompt.strip(),
            "normalized_goal": goal,
            "task_signals": signals,
            "deliverables": ["host_project"],
            "available_inputs": {
                "user_stated_facts": [prompt.strip()],
                "runtime_observed_facts": [],
                "inferred_assumptions": [
                    f"deliverable_profile inferred as {signals['deliverable_profile']} from prompt language"
                ],
                "unknowns": [],
            },
            "runtime_capabilities": host_capabilities(),
        }
    )


def _normalized_goal(prompt: str) -> str:
    for line in prompt.strip().splitlines():
        text = line.strip()
        if not text:
            continue
        if text.lower().startswith("this is a product request"):
            continue
        return text[:240]
    return prompt.strip().splitlines()[0][:240]
