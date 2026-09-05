"""Required host artifacts per workflow stage. Presence is not quality."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

PIXEL_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".webm", ".mp4"}
SAME_SESSION_INDEPENDENCE = "same_host_session_as_producer"

CREATIVE_FILES = {
    "ACOS-01": "direction/creative_direction.yaml",
    "ACOS-03": "direction/anti_generic_review.yaml",
    "ACOS-04": "direction/art_direction.yaml",
    "ACOS-05": "direction/experience_direction.yaml",
    "ACOS-02": "direction/reference_analysis.yaml",
}
PRODUCTION_MARKERS = (
    "implementation/index.html",
    "implementation/src/main.tsx",
    "implementation/src/main.js",
    "implementation/main.js",
)
CRITIC_FILES = {
    "ACOS-10": "critics/visual_critic.yaml",
    "ACOS-11": "critics/creative_critic.yaml",
    "ACOS-12": "critics/3d_critic.yaml",
}
HERO_ASSET_SUFFIXES = {".glb", ".gltf"}
FLAGSHIP_PRODUCTION_FILES = {
    "EXT-3DWEB-02": "direction/threejs_materials.yaml",
    "EXT-3DWEB-03": "direction/threejs_lighting.yaml",
    "EXT-3DWEB-04": "direction/threejs_camera.yaml",
    "EXT-BLD-12": "direction/blender_export.yaml",
}


def load_yaml(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}


def required_creative_files(planned_ids: list[str]) -> list[str]:
    return [CREATIVE_FILES[sid] for sid in planned_ids if sid in CREATIVE_FILES]


def _has_procedure_mark(data: dict[str, Any]) -> bool:
    if data.get("skill_procedure_executed") is True:
        return True
    producer = str(data.get("producer") or data.get("skill") or "")
    return producer.startswith("acos-") or producer.startswith("ACOS-")


def validate_creative_artifacts(project_dir: Path, planned_ids: list[str]) -> dict[str, Any]:
    missing: list[str] = []
    invalid: list[str] = []
    for rel in required_creative_files(planned_ids):
        path = project_dir / rel
        if not path.is_file() or path.stat().st_size < 40:
            missing.append(rel)
            continue
        data = load_yaml(path)
        if not _has_procedure_mark(data):
            invalid.append(f"{rel}: missing skill_procedure_executed or producer skill")
        if "bm002_direction" in str(data.get("producer", "")) or data.get("decision_provenance") == "hardcoded":
            invalid.append(f"{rel}: runner-authored placeholder, not a skill output")
    return {"missing": missing, "invalid": invalid, "ok": not missing and not invalid}


def has_implementation(project_dir: Path) -> bool:
    return any((project_dir / rel).is_file() for rel in PRODUCTION_MARKERS)


def is_flagship(signals: dict[str, Any] | None) -> bool:
    return str((signals or {}).get("quality_bar") or "") == "flagship"


def hero_assets(project_dir: Path) -> list[str]:
    found: list[str] = []
    for root in (project_dir / "implementation", project_dir / "assets"):
        if not root.is_dir():
            continue
        for path in root.rglob("*"):
            if path.is_file() and path.suffix.lower() in HERO_ASSET_SUFFIXES and path.stat().st_size > 32:
                found.append(str(path.relative_to(project_dir)).replace("\\", "/"))
    return sorted(found)


def validate_flagship_production(project_dir: Path, planned_ids: list[str], signals: dict[str, Any] | None) -> dict[str, Any]:
    if not is_flagship(signals):
        return {"ok": True, "missing": [], "invalid": []}
    missing: list[str] = []
    invalid: list[str] = []
    assets = hero_assets(project_dir)
    if not assets:
        missing.append("implementation/ hero GLB/GLTF from Blender — lathe/primitive is not a flagship hero")
    for sid, rel in FLAGSHIP_PRODUCTION_FILES.items():
        if sid not in planned_ids:
            continue
        path = project_dir / rel
        if not path.is_file() or path.stat().st_size < 40:
            missing.append(rel)
            continue
        data = load_yaml(path)
        if not data.get("skill_procedure_executed"):
            invalid.append(f"{rel}: missing skill_procedure_executed")
        if sid == "EXT-BLD-12" and data.get("blender_used") is not True:
            invalid.append("direction/blender_export.yaml: blender_used must be true")
    notes = project_dir / "direction" / "production_notes.yaml"
    if notes.is_file():
        data = load_yaml(notes)
        if data.get("blender_used") is False:
            invalid.append("production_notes: flagship cannot skip Blender for convenience")
    return {"missing": missing, "invalid": invalid, "ok": not missing and not invalid}


def evidence_files(project_dir: Path) -> list[str]:
    """Rendered pixel/video evidence only. Capture scripts and YAML are not evidence."""
    return pixel_evidence(project_dir)


def pixel_evidence(project_dir: Path) -> list[str]:
    root = project_dir / "evidence"
    if not root.is_dir():
        return []
    found: list[str] = []
    for path in root.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in PIXEL_SUFFIXES:
            continue
        if path.stat().st_size < 32:
            continue
        found.append(str(path.relative_to(project_dir)).replace("\\", "/"))
    return sorted(found)


def viewport_manifest(project_dir: Path) -> dict[str, Any] | None:
    path = project_dir / "evidence" / "viewports" / "manifest.yaml"
    if not path.is_file():
        return None
    data = load_yaml(path)
    return data or None


def validate_critic_independence(
    project_dir: Path,
    planned_ids: list[str],
    *,
    critic_pass_id: str | None,
    attested: bool,
) -> dict[str, Any]:
    issues: list[str] = []
    if not attested:
        issues.append("independent critic pass is not attested — run critic-pass in a new chat")
    if not critic_pass_id:
        issues.append("no critic_pass_id on session")
    for sid, rel in CRITIC_FILES.items():
        if sid not in planned_ids:
            continue
        path = project_dir / rel
        if not path.is_file():
            continue
        data = load_yaml(path)
        independence = str(data.get("independence") or "")
        if independence == SAME_SESSION_INDEPENDENCE:
            issues.append(f"{rel}: independence is {SAME_SESSION_INDEPENDENCE}")
        stamped = data.get("critic_pass_id")
        if critic_pass_id and stamped != critic_pass_id:
            issues.append(f"{rel}: critic_pass_id does not match the open critic pass")
        if not stamped:
            issues.append(f"{rel}: missing critic_pass_id")
    return {"ok": not issues, "issues": issues}


def validate_critic_artifacts(project_dir: Path, planned_ids: list[str]) -> dict[str, Any]:
    missing: list[str] = []
    invalid: list[str] = []
    for sid, rel in CRITIC_FILES.items():
        if sid not in planned_ids:
            continue
        path = project_dir / rel
        if not path.is_file():
            missing.append(rel)
            continue
        data = load_yaml(path)
        findings = data.get("findings")
        if not isinstance(findings, list) or not findings:
            invalid.append(f"{rel}: critic must include findings[] from rendered evidence")
        if data.get("inspected_rendered_output") is not True:
            invalid.append(f"{rel}: inspected_rendered_output must be true")
    return {"missing": missing, "invalid": invalid, "ok": not missing and not invalid}
