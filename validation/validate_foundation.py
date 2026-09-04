#!/usr/bin/env python3
"""ACOS v1.2 Phase A foundation validator.

Validates canonical repository structure and required documents for Phase A.
Does NOT validate external skill import (Phase B) or proprietary skills (Phase C).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore[assignment]


PHASE = "A"
REPO_ROOT = Path(__file__).resolve().parent.parent

REQUIRED_DIRS = [
    "core",
    "registry",
    "skills/external/frontend",
    "skills/external/threejs",
    "skills/external/img2threejs",
    "skills/external/gsap",
    "skills/external/blender",
    "skills/acos",
    "tools/blender-mcp",
    "tools/browser",
    "tools/validation",
    "memory/knowledge",
    "memory/taste",
    "memory/projects",
    "memory/failures",
    "memory/successes",
    "memory/model-compatibility",
    "benchmarks",
    "projects",
    "adapters/claude",
    "adapters/cursor",
    "adapters/codex",
    "adapters/local",
    "model-profiles",
    "templates",
    "validation",
    "docs",
]

REQUIRED_FILES = [
    "ACOS_FINAL_CANONICAL_v1.2.md",
    "AGENTS.md",
    "README.md",
    "core/CONSTITUTION.md",
    "core/WORKFLOW.md",
    "core/ROUTING.md",
    "core/QUALITY_GATES.md",
    "core/MEMORY_POLICY.md",
    "core/MODEL_COMPATIBILITY.md",
    "registry/SKILLS.yaml",
    "registry/MODELS.yaml",
    "adapters/local/LOCAL_LLM_BOOTSTRAP.md",
    "templates/MODEL_PROFILE_TEMPLATE.md",
    "IMPLEMENTATION_CHECKLIST.md",
    "PACK_INVENTORY.md",
    "docs/PROGRESS_LEDGER.md",
]

MIN_POLICY_BYTES = 200
CANONICAL_MASTER = "ACOS_FINAL_CANONICAL_v1.2.md"

FORBIDDEN_DUPLICATE_MASTER_PATTERNS = [
    "ACOS_FINAL_CANONICAL_v1.0.md",
    "ACOS_FINAL_CANONICAL_v1.1.md",
    "ACOS_CANONICAL.md",
]


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def parse_yaml(path: Path, errors: list[str]) -> dict | list | None:
    if yaml is None:
        fail(errors, "PyYAML not installed; cannot parse YAML registries")
        return None
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        fail(errors, f"Failed to parse {path.relative_to(REPO_ROOT)}: {exc}")
        return None
    if data is None:
        fail(errors, f"YAML file is empty: {path.relative_to(REPO_ROOT)}")
    return data


def check_proprietary_skills_phase(errors: list[str]) -> None:
    """Allow zero proprietary skills (Phase A/B) or exactly 14 registry skills (Phase C+)."""
    acos_dir = REPO_ROOT / "skills" / "acos"
    skill_files = sorted(acos_dir.rglob("SKILL.md")) if acos_dir.is_dir() else []
    if not skill_files:
        return

    registry = REPO_ROOT / "registry" / "SKILLS.yaml"
    if yaml is None or not registry.is_file():
        rel = [str(p.relative_to(REPO_ROOT)) for p in skill_files]
        fail(errors, f"Unexpected proprietary SKILL.md before registry check: {rel}")
        return

    data = yaml.safe_load(registry.read_text(encoding="utf-8"))
    expected = {
        item["name"]
        for item in data.get("proprietary", [])
        if isinstance(item, dict) and "name" in item
    }
    actual = {p.parent.name for p in skill_files}
    if actual == expected and len(actual) == 14:
        return
    rel = [str(p.relative_to(REPO_ROOT)) for p in skill_files]
    fail(
        errors,
        f"Proprietary skills must be absent (Phase A/B) or exactly 14 registry skills (Phase C+): {rel}",
    )


def check_benchmarks_projects_empty(errors: list[str]) -> None:
    for name in ("benchmarks", "projects"):
        base = REPO_ROOT / name
        for item in base.rglob("*"):
            if item.name == ".gitkeep":
                continue
            if item.is_file():
                rel = item.relative_to(REPO_ROOT)
                if item.stat().st_size > 0 and item.name not in (".gitkeep",):
                    fail(errors, f"Phase A: {rel} should remain empty of project content")


def check_no_duplicate_masters(errors: list[str]) -> None:
    for pattern in FORBIDDEN_DUPLICATE_MASTER_PATTERNS:
        if (REPO_ROOT / pattern).exists():
            fail(errors, f"Forbidden duplicate/superseded master found: {pattern}")

    masters = [
        p
        for p in REPO_ROOT.rglob("ACOS_FINAL_CANONICAL*.md")
        if p.is_file() and p.name != CANONICAL_MASTER
    ]
    if masters:
        rel = [str(p.relative_to(REPO_ROOT)) for p in masters]
        fail(errors, f"Unexpected additional canonical master files: {rel}")


def validate_skills_registry(errors: list[str]) -> None:
    path = REPO_ROOT / "registry" / "SKILLS.yaml"
    data = parse_yaml(path, errors)
    if not isinstance(data, dict):
        return
    for key in ("version", "authority", "external", "proprietary"):
        if key not in data:
            fail(errors, f"SKILLS.yaml missing required key: {key}")
    if data.get("authority") != CANONICAL_MASTER:
        fail(
            errors,
            f"SKILLS.yaml authority must reference {CANONICAL_MASTER}",
        )


def validate_models_registry(errors: list[str]) -> None:
    path = REPO_ROOT / "registry" / "MODELS.yaml"
    data = parse_yaml(path, errors)
    if not isinstance(data, dict):
        return
    for key in ("version", "authority", "models"):
        if key not in data:
            fail(errors, f"MODELS.yaml missing required key: {key}")
    if not isinstance(data.get("models"), list):
        fail(errors, "MODELS.yaml 'models' must be a list")


def main() -> int:
    errors: list[str] = []

    print(f"ACOS v1.2 Phase {PHASE} Foundation Validator")
    print(f"Repository: {REPO_ROOT}")
    print("-" * 60)

    for rel in REQUIRED_DIRS:
        if not (REPO_ROOT / rel).is_dir():
            fail(errors, f"Missing directory: {rel}")

    for rel in REQUIRED_FILES:
        path = REPO_ROOT / rel
        if not path.is_file():
            fail(errors, f"Missing file: {rel}")
        elif rel.startswith("core/") and path.stat().st_size < MIN_POLICY_BYTES:
            fail(errors, f"Policy document too small (likely empty): {rel}")

    master = REPO_ROOT / CANONICAL_MASTER
    if not master.is_file():
        fail(errors, f"Canonical master missing: {CANONICAL_MASTER}")
    elif master.stat().st_size < 1000:
        fail(errors, f"Canonical master appears truncated: {CANONICAL_MASTER}")

    check_no_duplicate_masters(errors)
    validate_skills_registry(errors)
    validate_models_registry(errors)
    check_proprietary_skills_phase(errors)
    check_benchmarks_projects_empty(errors)

    if errors:
        print("VALIDATION: FAILED")
        for i, err in enumerate(errors, 1):
            print(f"  {i}. {err}")
        return 1

    print("VALIDATION: PASSED")
    print(f"Phase {PHASE} checks complete.")
    print("Later phases are outside this validator's scope.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
