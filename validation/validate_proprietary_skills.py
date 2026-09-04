#!/usr/bin/env python3
"""ACOS v1.2 Phase C proprietary skills validator."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore[assignment]

REPO = Path(__file__).resolve().parent.parent
PHASE = "C"
ACOS_DIR = REPO / "skills" / "acos"

SECTION_PATTERNS = [
    re.compile(r"^##\s*(?:\d+\.\s*)?Purpose\b", re.I | re.M),
    re.compile(r"^##\s*(?:\d+\.\s*)?Activation\s*/?\s*trigger", re.I | re.M),
    re.compile(r"^##\s*(?:\d+\.\s*)?Do-not-activate", re.I | re.M),
    re.compile(r"^##\s*(?:\d+\.\s*)?Responsibility boundary", re.I | re.M),
    re.compile(r"^##\s*(?:\d+\.\s*)?Required inputs", re.I | re.M),
    re.compile(r"^##\s*(?:\d+\.\s*)?Exact procedure", re.I | re.M),
    re.compile(r"^##\s*(?:\d+\.\s*)?Required outputs", re.I | re.M),
    re.compile(r"^##\s*(?:\d+\.\s*)?Rejection\s*/?\s*failure", re.I | re.M),
    re.compile(r"^##\s*(?:\d+\.\s*)?Handoff contract", re.I | re.M),
    re.compile(r"^##\s*(?:\d+\.\s*)?QA\s*/?\s*evaluation", re.I | re.M),
    re.compile(r"^##\s*(?:\d+\.\s*)?Evidence requirements", re.I | re.M),
    re.compile(r"^##\s*(?:\d+\.\s*)?Memory interaction", re.I | re.M),
    re.compile(
        r"^##\s*(?:\d+\.\s*)?Relationship to neighboring ACOS skills", re.I | re.M
    ),
    re.compile(r"^##\s*(?:\d+\.\s*)?Non-goals", re.I | re.M),
]

PLACEHOLDER_PATTERNS = [
    re.compile(r"\bTODO\b", re.I),
    re.compile(r"\bTBD\b", re.I),
    re.compile(r"\bcoming soon\b", re.I),
    re.compile(r"\bfill later\b", re.I),
    re.compile(r"\bplaceholder section\b", re.I),
    re.compile(r"\blorem ipsum\b", re.I),
]

FORBIDDEN_DOMAIN = re.compile(r"\bcoffee\b", re.I)

HANDOFF_FIELDS = (
    "status",
    "inputs_used",
    "decisions",
    "constraints",
    "open_risks",
    "evidence",
    "deliverables",
    "next_owner",
    "rejection_route",
)


def fail(errors: list[str], msg: str) -> None:
    errors.append(msg)


def load_registry_proprietary(errors: list[str]) -> list[str]:
    path = REPO / "registry" / "SKILLS.yaml"
    if yaml is None:
        fail(errors, "PyYAML required")
        return []
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    items = data.get("proprietary", [])
    names = [item["name"] for item in items if isinstance(item, dict) and "name" in item]
    if len(names) != 14:
        fail(errors, f"Expected 14 proprietary names in SKILLS.yaml, found {len(names)}")
    return names


def parse_frontmatter(text: str) -> dict | None:
    if not text.startswith("---"):
        return None
    parts = text.split("---", 2)
    if len(parts) < 3:
        return None
    try:
        data = yaml.safe_load(parts[1])
    except yaml.YAMLError:
        return None
    return data if isinstance(data, dict) else None


def validate_skill(name: str, errors: list[str]) -> None:
    skill_dir = ACOS_DIR / name
    skill_md = skill_dir / "SKILL.md"
    if skill_dir.name != name:
        fail(errors, f"{name}: folder name mismatch")
    if not skill_md.is_file():
        fail(errors, f"{name}: missing SKILL.md")
        return
    text = skill_md.read_text(encoding="utf-8")
    if len(text.strip()) < 800:
        fail(errors, f"{name}: SKILL.md too small to be operational")
    fm = parse_frontmatter(text)
    if fm is None:
        fail(errors, f"{name}: invalid or missing YAML frontmatter")
    else:
        if fm.get("name") != name:
            fail(errors, f"{name}: frontmatter name '{fm.get('name')}' != folder")
        desc = fm.get("description", "")
        if not isinstance(desc, str) or len(desc.strip()) < 40:
            fail(errors, f"{name}: description missing or too short")
        if re.search(r"world-class|you are a\b", desc, re.I):
            fail(errors, f"{name}: persona-style description forbidden")

    for i, pattern in enumerate(SECTION_PATTERNS, 1):
        if not pattern.search(text):
            fail(errors, f"{name}: missing mandatory section #{i}")

    for pattern in PLACEHOLDER_PATTERNS:
        if pattern.search(text):
            fail(errors, f"{name}: placeholder marker detected: {pattern.pattern}")

    if FORBIDDEN_DOMAIN.search(text):
        fail(errors, f"{name}: forbidden domain keyword 'coffee' detected")

    missing_handoff = [f for f in HANDOFF_FIELDS if f not in text]
    if missing_handoff:
        fail(errors, f"{name}: handoff contract missing fields: {missing_handoff}")


def run_validator(script: str, errors: list[str], label: str) -> None:
    path = REPO / "validation" / script
    result = subprocess.run(
        [sys.executable, str(path)],
        capture_output=True,
        text=True,
        cwd=REPO,
    )
    if result.returncode != 0:
        fail(errors, f"{label} failed")
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr)


def main() -> int:
    errors: list[str] = []
    print(f"ACOS v1.2 Phase {PHASE} Proprietary Skills Validator")
    print(f"Repository: {REPO}")
    print("-" * 60)

    expected = load_registry_proprietary(errors)
    if not ACOS_DIR.is_dir():
        fail(errors, "skills/acos/ missing")
        return 1

    actual_dirs = sorted(
        p.name for p in ACOS_DIR.iterdir() if p.is_dir() and not p.name.startswith("_")
    )
    if sorted(expected) != sorted(actual_dirs):
        missing = sorted(set(expected) - set(actual_dirs))
        extra = sorted(set(actual_dirs) - set(expected))
        if missing:
            fail(errors, f"Missing proprietary skill directories: {missing}")
        if extra:
            fail(errors, f"Unexpected proprietary skill directories: {extra}")

    for name in expected:
        if name in actual_dirs:
            validate_skill(name, errors)

    from benchmark_scope import scan_benchmarks_and_projects

    scan_benchmarks_and_projects(errors, fail)

    run_validator("validate_foundation.py", errors, "Phase A foundation validator")
    run_validator("validate_external_skills.py", errors, "Phase B external skills validator")

    if errors:
        print("VALIDATION: FAILED")
        for i, err in enumerate(errors, 1):
            print(f"  {i}. {err}")
        return 1

    print("VALIDATION: PASSED")
    print(f"Verified {len(expected)} proprietary ACOS skills.")
    print("Phase C proprietary skill checks complete.")
    print("Later phases are outside this validator's scope.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
