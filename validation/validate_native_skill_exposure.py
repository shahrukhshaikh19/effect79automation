#!/usr/bin/env python3
"""Validate native skill exposure links for Cursor, Claude Code, and Codex."""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CANONICAL_ROOT = REPO / "skills"
MANIFEST = REPO / "tools" / "skill_exposure" / "exposure-manifest.yaml"

PLATFORMS = {
    "cursor": REPO / ".cursor" / "skills",
    "claude": REPO / ".claude" / "skills",
    "codex": REPO / ".agents" / "skills",
}


def fail(errors: list[str], msg: str) -> None:
    errors.append(msg)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def discover_canonical() -> dict[str, Path]:
    found: dict[str, Path] = {}
    for skill_md in CANONICAL_ROOT.rglob("SKILL.md"):
        found[skill_md.parent.name] = skill_md.parent
    return found


def main() -> int:
    errors: list[str] = []
    canonical = discover_canonical()
    if not canonical:
        fail(errors, "No canonical SKILL.md files found under skills/")
    if not MANIFEST.is_file():
        fail(errors, "Missing tools/skill_exposure/exposure-manifest.yaml — run sync_native_skills.py")

    for platform, root in PLATFORMS.items():
        if not root.is_dir():
            fail(errors, f"{platform}: missing native root {root.relative_to(REPO)}")
            continue
        for name, skill_dir in sorted(canonical.items()):
            exposed = root / name
            if not exposed.exists() and not exposed.is_symlink():
                fail(errors, f"{platform}: missing exposure for {name}")
                continue
            exposed_md = (exposed / "SKILL.md").resolve()
            canonical_md = (skill_dir / "SKILL.md").resolve()
            if exposed_md != canonical_md:
                fail(
                    errors,
                    f"{platform}: {name} does not resolve to canonical SKILL.md "
                    f"({exposed_md} != {canonical_md})",
                )
                continue
            if sha256_file(exposed_md) != sha256_file(canonical_md):
                fail(errors, f"{platform}: {name} SKILL.md hash drift")

        extra = sorted(
            child.name
            for child in root.iterdir()
            if child.name not in canonical and (child / "SKILL.md").exists()
        )
        for name in extra:
            fail(errors, f"{platform}: unexpected extra skill {name}")

    if errors:
        print("Native skill exposure validation FAILED")
        for item in errors:
            print(f"  - {item}")
        return 1

    print(
        "Native skill exposure validation passed: "
        f"{len(canonical)} skills x {len(PLATFORMS)} platforms"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
