#!/usr/bin/env python3
"""ACOS v1.2 Phase B external skills validator (hardened)."""

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

SCRIPT_EXT = {".py", ".sh", ".ps1", ".js", ".ts", ".mjs", ".bat", ".cmd"}

# Shared/non-skill paths allowed within category roots (not runtime skill directories)
CATEGORY_SHARED_ALLOWLIST: dict[str, set[str]] = {
    "frontend": set(),
    "threejs": {"references", "UPSTREAM_LICENSE"},
    "gsap": {"UPSTREAM_LICENSE"},
    "blender": {"references", "UPSTREAM_LICENSE"},
    "img2threejs": set(),  # entire root is one skill import
}

SECURITY_REQUIRED_FIELDS = (
    "path",
    "language",
    "runtime_role",
    "filesystem_access",
    "network_access",
    "subprocess_execution",
    "shell_execution",
    "package_install_behavior",
    "environment_variable_access",
    "destructive_write_delete_behavior",
    "external_binary_requirements",
    "review_status",
    "risk_classification",
    "notes",
)

TRI_VALUES = {"yes", "no", "unknown"}


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
        if match.startswith(("forge/", "grimoire/", "docs/")):
            resolved = (skill_dir / match).resolve()
        elif match.startswith("../"):
            resolved = (skill_dir / match).resolve()
        elif match.startswith("./"):
            resolved = (skill_dir / match[2:]).resolve()
        else:
            if "/" not in match:
                continue
            resolved = (skill_dir / match).resolve()
        try:
            resolved.relative_to(REPO)
        except ValueError:
            continue
        if not resolved.exists():
            fail(errors, f"{entry_id}: referenced local file missing: {match}")


def category_roots() -> dict[str, Path]:
    base = REPO / "skills" / "external"
    return {
        "frontend": base / "frontend",
        "threejs": base / "threejs",
        "gsap": base / "gsap",
        "blender": base / "blender",
        "img2threejs": base / "img2threejs",
    }


def approved_skill_dirs(entries: list[dict]) -> dict[str, set[str]]:
    approved: dict[str, set[str]] = {
        "frontend": set(),
        "threejs": set(),
        "gsap": set(),
        "blender": set(),
        "img2threejs": set(),
    }
    for entry in entries:
        cat = entry["category"]
        local = Path(entry["local_path"])
        if cat == "r3f_reference":
            approved["threejs"].add(f"references/{local.name}")
            continue
        if cat == "img2threejs":
            approved["img2threejs"].add(".")
            continue
        approved[cat].add(local.name)
    return approved


def list_runtime_dirs(category: str, root: Path) -> set[str]:
    if not root.exists():
        return set()
    if category == "img2threejs":
        return {"."} if (root / "SKILL.md").is_file() else set()

    shared = CATEGORY_SHARED_ALLOWLIST.get(category, set())
    found: set[str] = set()
    for item in root.iterdir():
        if item.is_file():
            continue
        if not item.is_dir():
            continue
        if category == "threejs" and item.name == "references":
            for sub in item.iterdir():
                if sub.is_dir():
                    found.add(f"references/{sub.name}")
            continue
        if item.name in shared:
            continue
        found.add(item.name)
    return found


def validate_directory_allowlists(entries: list[dict], errors: list[str]) -> None:
    approved = approved_skill_dirs(entries)
    roots = category_roots()

    for category, root in roots.items():
        expected = approved[category]
        actual = list_runtime_dirs(category, root)
        missing = expected - actual
        unexpected = actual - expected
        if missing:
            fail(
                errors,
                f"{category}: missing approved skill directories: {sorted(missing)}",
            )
        if unexpected:
            fail(
                errors,
                f"{category}: unexpected skill directories: {sorted(unexpected)}",
            )

        # Shared allowlist entries must exist when declared
        for shared in CATEGORY_SHARED_ALLOWLIST.get(category, set()):
            shared_path = root / shared
            if shared.endswith("_LICENSE") or shared == "UPSTREAM_LICENSE":
                if not shared_path.is_file():
                    fail(errors, f"{category}: missing shared file {shared_path.relative_to(REPO)}")
            elif not shared_path.exists():
                fail(errors, f"{category}: missing shared directory {shared_path.relative_to(REPO)}")


def validate_lock_uniqueness(entries: list[dict], errors: list[str]) -> None:
    ids: list[str] = []
    paths: list[str] = []
    for entry in entries:
        ids.append(entry["id"])
        paths.append(entry["local_path"])
    if len(ids) != len(set(ids)):
        dupes = sorted({x for x in ids if ids.count(x) > 1})
        fail(errors, f"Duplicate lock IDs: {dupes}")
    if len(paths) != len(set(paths)):
        dupes = sorted({x for x in paths if paths.count(x) > 1})
        fail(errors, f"Duplicate lock local paths: {dupes}")


def discover_scripts_for_entry(entry: dict) -> list[Path]:
    local = REPO / entry["local_path"]
    if not local.exists():
        return []
    return sorted(
        p
        for p in local.rglob("*")
        if p.is_file() and p.suffix.lower() in SCRIPT_EXT
    )


def validate_script_security(entries: list[dict], errors: list[str]) -> None:
    sec_path = REPO / "registry" / "EXTERNAL_SCRIPT_SECURITY.yaml"
    security = load_yaml(sec_path, errors)
    if not isinstance(security, dict):
        return

    records = security.get("scripts")
    if not isinstance(records, list):
        fail(errors, "EXTERNAL_SCRIPT_SECURITY.yaml missing scripts list")
        return

    inventory_paths: list[str] = []
    for rec in records:
        if not isinstance(rec, dict):
            fail(errors, "Security inventory record is not a mapping")
            continue
        for field in SECURITY_REQUIRED_FIELDS:
            if field not in rec:
                fail(errors, f"Security record missing field {field}: {rec.get('path', '?')}")
        for tri_field in (
            "filesystem_access",
            "network_access",
            "subprocess_execution",
            "shell_execution",
            "package_install_behavior",
            "environment_variable_access",
            "destructive_write_delete_behavior",
        ):
            val = rec.get(tri_field)
            if val not in TRI_VALUES:
                fail(
                    errors,
                    f"Security record {rec.get('path')}: {tri_field} must be yes/no/unknown",
                )
        inventory_paths.append(rec["path"])

    if len(inventory_paths) != len(set(inventory_paths)):
        dupes = sorted({x for x in inventory_paths if inventory_paths.count(x) > 1})
        fail(errors, f"Duplicate security inventory paths: {dupes}")

    inventory_set = set(inventory_paths)
    for inv_path in inventory_set:
        full = REPO / "skills" / "external" / "img2threejs" / inv_path
        if not full.is_file():
            fail(errors, f"Security inventory path missing on disk: {inv_path}")

    for entry in entries:
        if not entry.get("scripts_present"):
            continue
        eid = entry["id"]
        discovered = discover_scripts_for_entry(entry)
        rel_paths = {p.relative_to(REPO / entry["local_path"]).as_posix() for p in discovered}
        missing_inv = sorted(rel_paths - inventory_set)
        extra_inv = sorted(inventory_set - rel_paths)
        if missing_inv:
            fail(
                errors,
                f"{eid}: discovered scripts missing security inventory: {missing_inv[:5]}"
                + (f" (+{len(missing_inv)-5} more)" if len(missing_inv) > 5 else ""),
            )
        if extra_inv:
            fail(
                errors,
                f"{eid}: security inventory paths not present in import: {extra_inv[:5]}"
                + (f" (+{len(extra_inv)-5} more)" if len(extra_inv) > 5 else ""),
            )


def check_proprietary_skills_phase(errors: list[str]) -> None:
    """Allow zero proprietary skills (Phase B) or exactly 14 registry skills (Phase C+)."""
    skill_files = sorted((REPO / "skills" / "acos").rglob("SKILL.md"))
    if not skill_files:
        return
    registry = load_yaml(REPO / "registry" / "SKILLS.yaml", errors)
    if not isinstance(registry, dict):
        return
    expected = {
        item["name"]
        for item in registry.get("proprietary", [])
        if isinstance(item, dict) and "name" in item
    }
    actual = {p.parent.name for p in skill_files}
    if actual == expected and len(actual) == 14:
        return
    fail(
        errors,
        f"Proprietary skills must be absent (Phase B) or complete set of 14 (Phase C+): {actual}",
    )


def main() -> int:
    errors: list[str] = []
    print(f"ACOS v1.2 Phase {PHASE} External Skills Validator (hardened)")
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

    validate_lock_uniqueness(entries, errors)

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

        if entry["id"] != "EXT-R3F-01" and entry["category"] != "img2threejs":
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

    validate_directory_allowlists(entries, errors)
    validate_script_security(entries, errors)
    check_proprietary_skills_phase(errors)

    from benchmark_scope import scan_benchmarks_and_projects

    scan_benchmarks_and_projects(errors, fail)

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
    print("Directory allowlists derived from lockfile: OK")
    print("Script security inventory: OK")
    print("Phase B external skill checks complete.")
    print("Later phases are outside this validator's scope.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
