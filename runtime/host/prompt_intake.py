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
_REF = re.compile(r"\b(reference image|reconstruct|img2three|match this image)\b", re.I)
_A11Y = re.compile(r"\b(a11y|accessibility|wcag|screen reader)\b", re.I)
_FLAGSHIP = re.compile(
    r"\b(premium|cinematic|flagship|physical (tech(?:nology)?|product|instrument)|"
    r"launch (site|website)|hero product|scroll[- ]driven|hydrographic|"
    r"meaningful real-time|webgl/three\.js)\b",
    re.I,
)


def classify_signals(prompt: str) -> dict[str, Any]:
    text = prompt.strip()
    wants_3d = bool(_3D.search(text))
    wants_ref = bool(_REF.search(text))
    wants_visual = bool(_VISUAL.search(text)) or wants_3d
    wants_motion = bool(_MOTION.search(text))
    if wants_ref and wants_3d:
        profile = "reference_reconstruction"
        reconstruction = "procedural_browser"
    elif wants_3d:
        profile = "interactive_3d"
        reconstruction = "none"
        if _FLAGSHIP.search(text):
            reconstruction = "blender_authoring"
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
        "reconstruction_path": reconstruction,
        "quality_bar": "flagship" if wants_3d and reconstruction == "blender_authoring" else "standard",
    }


def intake_from_prompt(prompt: str, *, task_id: str | None = None) -> dict[str, Any]:
    if not prompt.strip():
        raise ValueError("Project prompt is empty")
    signals = classify_signals(prompt)
    goal = prompt.strip().splitlines()[0][:240]
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
