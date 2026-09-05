#!/usr/bin/env python3
"""Expose canonical ACOS skills to Cursor, Claude Code, and Codex discovery paths.

Canonical bodies stay in skills/. Platform directories only receive directory
links (symlink, or Windows junction). Never copy SKILL.md bodies.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import stat
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
CANONICAL_ROOT = REPO / "skills"
MANIFEST_PATH = Path(__file__).resolve().parent / "exposure-manifest.yaml"

PLATFORMS = {
    "cursor": Path(".cursor") / "skills",
    "claude": Path(".claude") / "skills",
    "codex": Path(".agents") / "skills",
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def discover_skills() -> list[tuple[str, Path]]:
    found: dict[str, Path] = {}
    for skill_md in sorted(CANONICAL_ROOT.rglob("SKILL.md")):
        skill_dir = skill_md.parent
        name = skill_dir.name
        if name in found:
            raise SystemExit(
                f"Duplicate skill folder name '{name}':\n  {found[name]}\n  {skill_dir}"
            )
        found[name] = skill_dir
    if not found:
        raise SystemExit(f"No SKILL.md files under {CANONICAL_ROOT}")
    return [(name, path) for name, path in sorted(found.items())]


def is_link(path: Path) -> bool:
    if path.is_symlink():
        return True
    if os.name != "nt" or not path.exists():
        return False
    try:
        return bool(path.stat().st_file_attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT)  # type: ignore[attr-defined]
    except AttributeError:
        return False


def remove_link(path: Path) -> None:
    if not path.exists() and not path.is_symlink():
        return
    if path.is_symlink():
        path.unlink()
        return
    if is_link(path) and path.is_dir():
        path.rmdir()
        return
    raise SystemExit(f"Refusing to replace non-link path: {path}")


def create_link(canonical: Path, dest: Path) -> str:
    dest.parent.mkdir(parents=True, exist_ok=True)
    remove_link(dest)
    relative = os.path.relpath(canonical, dest.parent)
    try:
        os.symlink(relative, dest, target_is_directory=True)
        return "symlink"
    except OSError:
        if os.name != "nt":
            raise
        completed = subprocess.run(
            ["cmd", "/c", "mklink", "/J", str(dest), str(canonical.resolve())],
            capture_output=True,
            text=True,
        )
        if completed.returncode != 0:
            raise SystemExit(
                "Failed to create symlink or junction for "
                f"{dest} -> {canonical}\n{completed.stderr or completed.stdout}"
            )
        return "junction"


def resolve_skill_md(link_dir: Path) -> Path:
    return (link_dir / "SKILL.md").resolve()


def sync_root(root: Path, skills: list[tuple[str, Path]]) -> list[dict]:
    records: list[dict] = []
    for platform, rel in PLATFORMS.items():
        platform_root = root / rel
        platform_root.mkdir(parents=True, exist_ok=True)
        for name, canonical in skills:
            dest = platform_root / name
            method = create_link(canonical, dest)
            skill_md = canonical / "SKILL.md"
            exposed_md = resolve_skill_md(dest)
            if exposed_md != skill_md.resolve():
                raise SystemExit(
                    f"{platform} link does not resolve to canonical SKILL.md:\n"
                    f"  {dest}\n  resolved={exposed_md}\n  canonical={skill_md.resolve()}"
                )
            records.append(
                {
                    "name": name,
                    "platform": platform,
                    "root": str(root),
                    "canonical": str(canonical.relative_to(REPO) if root == REPO else canonical),
                    "exposed": str(dest.relative_to(root)),
                    "method": method,
                    "skill_md_sha256": sha256_file(skill_md),
                }
            )
    return records


def write_manifest(records: list[dict], skills: list[tuple[str, Path]]) -> None:
    lines = [
        "generated_by: tools/skill_exposure/sync_native_skills.py",
        "canonical_root: skills/",
        "copy_policy: links_only_never_copy_bodies",
        f"skill_count: {len(skills)}",
        "platforms:",
        "  cursor: .cursor/skills/",
        "  claude: .claude/skills/",
        "  codex: .agents/skills/",
        "skills:",
    ]
    seen: set[str] = set()
    for name, canonical in skills:
        if name in seen:
            continue
        seen.add(name)
        sample = next(r for r in records if r["name"] == name)
        lines.append(f"  - name: {name}")
        lines.append(f"    canonical: {canonical.relative_to(REPO).as_posix()}")
        lines.append(f"    skill_md_sha256: {sample['skill_md_sha256']}")
    MANIFEST_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--extra-root",
        action="append",
        default=[],
        help="Additional workspace root that should also receive native skill links",
    )
    args = parser.parse_args()

    skills = discover_skills()
    records = sync_root(REPO, skills)
    extra_roots = [Path(raw).resolve() for raw in args.extra_root]
    for extra in extra_roots:
        if extra == REPO:
            continue
        records.extend(sync_root(extra, skills))
    write_manifest(records, skills)

    print(f"Exposed {len(skills)} canonical skills")
    print(f"  Cursor : {REPO / PLATFORMS['cursor']}")
    print(f"  Claude : {REPO / PLATFORMS['claude']}")
    print(f"  Codex  : {REPO / PLATFORMS['codex']}")
    for extra in extra_roots:
        print(f"  extra  : {extra}")
    print(f"Manifest : {MANIFEST_PATH.relative_to(REPO)}")
    print(json.dumps({"skill_count": len(skills), "link_records": len(records)}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
