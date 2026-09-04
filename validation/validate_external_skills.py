#!/usr/bin/env python3
"""ACOS v1.2 Phase B external skills validator."""

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
PHASE = "B"

EXPECTED_COUNTS = {
    "frontend_design_accessibility": 4,
    "threejs_selected": 10,
    "r3f_reference": 1,
    "gsap_selected": 5,
    "blender_selected": 15,
    "img2threejs": 1,
    "total": 36,
}

UNAPPROVED_THREEJS = {
    "threejs-audio",
    "threejs-geometry",
    "threejs-physics",
    "threejs-xr",
}
UNAPPROVED_GSAP = {"gsap-frameworks", "gsap-plugins", "gsap-utils"}
UNAPPROVED_BLENDER_EXAMPLE = {"character-artist", "sculpting", "rigging", "voxel-style"}


def fail(errors: list[str], msg: str) -> None:
    errors.append(msg)


def load_yaml(path: Path, errors: list[str]) -> dict | None:
    if yaml is None:
        fail(errors, "PyYAML required")
        return None
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        fail(errors, f"Failed to parse {path.relative_to(REPO)}: {exc}")
        return None
    return data


def check_frontmatter(skill_md: Path, errors: list[str], entry_id: str) -> None:
    text = skill_md.read_text(encoding="utf-8")
    if not text.startswith("---"):
        fail(errors, f"{entry_id}: SKILL.md missing YAML frontmatter")
        return
    if "name:" not in text.split("---", 2)[1]:
        fail(errors, f"{entry_id}: SKILL.md frontmatter missing name:")


def check_local_refs(skill_dir: Path, errors: list[str], entry_id: str) -> None:
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        return
    text = skill_md.read_text(encoding="utf-8")
    skip_patterns = ("<", "--", '"', "|", "python3 ", "node ", "npm ", " ")
    runtime_generated_prefixes = (".img2threejs/",)
    for match in re.findall(r"`([^`]+)`", text):
        if match.startswith(("http://", "https://")):
            continue
        if any(p in match for p in skip_patterns):
            continue
        if not re.search(r"\.(?:md|json|yaml|yml|py|sh|mjs|ts|js)$", match):
            continue
        if any(match.startswith(prefix) for prefix in runtime_generated_prefixes):
            continue
        if match.startswith("forge/") or match.startswith("grimoire/") or match.startswith("docs/"):
            resolved = (skill_dir / match).resolve()
        elif match.startswith("../"):
            resolved = (skill_dir / match).resolve()
        elif match.startswith("./"):
            resolved = (skill_dir / match[2:]).resolve()
        else:
            # bare filename references are often examples, not repo paths
            if "/" not in match:
                continue
            resolved = (skill_dir / match).resolve()
        try:
            resolved.relative_to(REPO)
        except ValueError:
            continue
        if not resolved.exists():
            fail(errors, f"{entry_id}: referenced local file missing: {match}")


def main() -> int:
    errors: list[str] = []
    print(f"ACOS v1.2 Phase {PHASE} External Skills Validator")
    print(f"Repository: {REPO}")
    print("-" * 60)

    lock_path = REPO / "registry" / "EXTERNAL_SKILLS_LOCK.yaml"
    lock = load_yaml(lock_path, errors)
    if not isinstance(lock, dict):
        return 1

    entries = lock.get("entries")
    if not isinstance(entries, list):
        fail(errors, "Lock file missing entries list")
        return 1

    if len(entries) != EXPECTED_COUNTS["total"]:
        fail(errors, f"Expected {EXPECTED_COUNTS['total']} lock entries, found {len(entries)}")

    counts = lock.get("counts", {})
    for key, expected in EXPECTED_COUNTS.items():
        if key == "total":
            continue
        if counts.get(key) != expected:
            fail(errors, f"Lock counts.{key} expected {expected}, got {counts.get(key)}")

    categories: dict[str, int] = {}
    for entry in entries:
        if not isinstance(entry, dict):
            fail(errors, "Lock entry is not a mapping")
            continue
        for req in (
            "id",
            "name",
            "category",
            "decision",
            "operational_status",
            "repo",
            "upstream_path",
            "commit_sha",
            "license",
            "local_path",
        ):
            if req not in entry:
                fail(errors, f"Lock entry missing {req}: {entry.get('id', '?')}")

        eid = entry["id"]
        local = REPO / entry["local_path"]
        categories[entry["category"]] = categories.get(entry["category"], 0) + 1

        sha = entry.get("commit_sha", "")
        if not re.fullmatch(r"[0-9a-f]{40}", sha):
            fail(errors, f"{eid}: invalid commit SHA: {sha}")
        if sha in {"main", "latest", "master"}:
            fail(errors, f"{eid}: floating ref forbidden")

        status = entry.get("operational_status")
        if status not in {"operational", "reference", "restricted", "blocked"}:
            fail(errors, f"{eid}: invalid operational_status: {status}")

        if not local.exists():
            fail(errors, f"{eid}: local path missing: {entry['local_path']}")
            continue

        skill_md = local / "SKILL.md"
        if not skill_md.is_file():
            fail(errors, f"{eid}: missing SKILL.md at {entry['local_path']}")
        else:
            check_frontmatter(skill_md, errors, eid)
            if status in {"operational", "restricted"}:
                check_local_refs(local, errors, eid)

        if local.name != entry["name"] and entry["category"] != "threejs":
            # R3F reference folder name differs by design
            if entry["id"] != "EXT-R3F-01":
                if local.name != entry["name"]:
                    fail(errors, f"{eid}: directory name {local.name} != {entry['name']}")

    if categories.get("frontend") != 4:
        fail(errors, f"Expected 4 frontend entries, found {categories.get('frontend', 0)}")
    if categories.get("threejs") != 10:
        fail(errors, f"Expected 10 threejs runtime entries, found {categories.get('threejs', 0)}")
    if categories.get("r3f_reference") != 1:
        fail(errors, f"Expected 1 r3f reference entry, found {categories.get('r3f_reference', 0)}")
    if categories.get("gsap") != 5:
        fail(errors, f"Expected 5 gsap entries, found {categories.get('gsap', 0)}")
    if categories.get("blender") != 15:
        fail(errors, f"Expected 15 blender entries, found {categories.get('blender', 0)}")
    if categories.get("img2threejs") != 1:
        fail(errors, f"Expected 1 img2threejs entry, found {categories.get('img2threejs', 0)}")

    # Unapproved imports
    threejs_dir = REPO / "skills" / "external" / "threejs"
    for name in UNAPPROVED_THREEJS:
        if (threejs_dir / name).exists():
            fail(errors, f"Unapproved Three.js skill imported: {name}")
    gsap_dir = REPO / "skills" / "external" / "gsap"
    for name in UNAPPROVED_GSAP:
        if (gsap_dir / name).exists():
            fail(errors, f"Unapproved GSAP skill imported: {name}")
    blender_dir = REPO / "skills" / "external" / "blender"
    for item in blender_dir.iterdir():
        if item.is_dir() and item.name not in {"references"}:
            if item.name not in {e["name"] for e in entries if e.get("category") == "blender"}:
                fail(errors, f"Unapproved Blender skill directory: {item.name}")

    # Proprietary skills must not exist
    acos_skills = list((REPO / "skills" / "acos").rglob("SKILL.md"))
    if acos_skills:
        fail(errors, f"Proprietary SKILL.md must not exist in Phase B: {acos_skills}")

    # Benchmarks/projects empty
    for name in ("benchmarks", "projects"):
        base = REPO / name
        for item in base.rglob("*"):
            if item.name == ".gitkeep":
                continue
            if item.is_file():
                fail(errors, f"{name}/ must remain empty: {item.relative_to(REPO)}")

    # Phase A validator
    phase_a = REPO / "validation" / "validate_foundation.py"
    if phase_a.exists():
        result = subprocess.run(
            [sys.executable, str(phase_a)],
            capture_output=True,
            text=True,
            cwd=REPO,
        )
        if result.returncode != 0:
            fail(errors, "Phase A foundation validator failed after Phase B imports")
            if result.stdout:
                print(result.stdout)
            if result.stderr:
                print(result.stderr)
    else:
        fail(errors, "Phase A validator missing")

    if errors:
        print("VALIDATION: FAILED")
        for i, err in enumerate(errors, 1):
            print(f"  {i}. {err}")
        return 1

    print("VALIDATION: PASSED")
    print(f"Verified {len(entries)} locked external skill entries.")
    print("Phase C (proprietary skills): NOT VALIDATED (not started)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
