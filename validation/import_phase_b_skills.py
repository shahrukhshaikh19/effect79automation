#!/usr/bin/env python3
"""One-shot Phase B importer — run from repo root. Not part of runtime validation."""

from __future__ import annotations

import re
import shutil
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
TMP = REPO / ".tmp-import"
SKILLS = REPO / "skills" / "external"
RETRIEVAL_DATE = "2026-09-04"

PINS = {
    "openai/plugins": "1e285826e604f66f7208f7ac4dba0fe8341d1f57",
    "anthropics/knowledge-work-plugins": "9e2bcbc55b70d5c3cdc04a9789cb00c030bf7fc1",
    "magnus919/agent-skills": "de968dfdfb5ac92336a4915dad4bb56a27fe0207",
    "alton47/threejs-skills": "7b8e25638cff83a6be4926d8f05001022cc80ac3",
    "shreyam1008/shre-skills": "412c49746b8bbbb59b7e823b0d5126f866050314",
    "greensock/gsap-skills": "aed9cfd3277740755f6bfc1155c7aa645403b760",
    "arjun988/blender-skills": "8f778d2405a214b508d4c7d80742be8e43acdd52",
    "img2threejs/img2threejs": "d6815db757c1eb435ae55f91fb375a7a98ddf28b",
}


def copytree(src: Path, dst: Path) -> None:
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)


def copy_skill_dir(src: Path, dst: Path) -> None:
    copytree(src, dst)


def remove_gitkeep(parent: Path) -> None:
    keep = parent / ".gitkeep"
    if keep.exists():
        keep.unlink()


def main() -> None:
    if not TMP.exists():
        raise SystemExit("Missing .tmp-import — clone upstream repos first.")

    # --- Frontend ---
    fe = SKILLS / "frontend"
    remove_gitkeep(fe)

    copy_skill_dir(
        TMP / "openai-plugins/plugins/build-web-apps/skills/frontend-app-builder",
        fe / "openai-frontend-app-builder",
    )
    copy_skill_dir(
        TMP / "openai-plugins/plugins/build-web-apps/skills/frontend-testing-debugging",
        fe / "openai-frontend-testing-debugging",
    )
    copy_skill_dir(
        TMP / "anthropic-kwp/design/skills/design-critique",
        fe / "anthropic-design-critique",
    )
    shutil.copy2(
        TMP / "anthropic-kwp/design/CONNECTORS.md",
        SKILLS / "CONNECTORS.md",
    )
    copy_skill_dir(
        TMP / "magnus919-agent-skills/web-accessibility",
        fe / "web-accessibility",
    )
    shutil.copy2(
        TMP / "magnus919-agent-skills/LICENSE.md",
        fe / "web-accessibility" / "UPSTREAM_LICENSE.md",
    )

    # --- Three.js ---
    tj = SKILLS / "threejs"
    remove_gitkeep(tj)
    selected_threejs = [
        "threejs-core",
        "threejs-materials",
        "threejs-lighting",
        "threejs-camera",
        "threejs-animation",
        "threejs-loaders",
        "threejs-react",
        "threejs-performance",
        "threejs-shaders",
        "threejs-postprocessing",
    ]
    for name in selected_threejs:
        copy_skill_dir(TMP / "threejs-skills/skills" / name, tj / name)
    shutil.copy2(TMP / "threejs-skills/LICENSE", tj / "UPSTREAM_LICENSE")

    # R3F merge reference (not a competing authority)
    r3f_dst = tj / "references" / "react-three-fiber-production-rules"
    copy_skill_dir(TMP / "shre-skills/skills/react-three-fiber", r3f_dst)
    shutil.copy2(TMP / "shre-skills/LICENSE", r3f_dst / "UPSTREAM_LICENSE")

    # --- GSAP ---
    gs = SKILLS / "gsap"
    remove_gitkeep(gs)
    for name in [
        "gsap-core",
        "gsap-timeline",
        "gsap-scrolltrigger",
        "gsap-react",
        "gsap-performance",
    ]:
        copy_skill_dir(TMP / "gsap-skills/skills" / name, gs / name)
    shutil.copy2(TMP / "gsap-skills/LICENSE", gs / "UPSTREAM_LICENSE")

    # --- Blender ---
    bl = SKILLS / "blender"
    remove_gitkeep(bl)
    blender_selected = [
        "blender-director",
        "blender-modeler",
        "prop-artist",
        "uv-workflow",
        "materials",
        "lookdev",
        "camera-cinematography",
        "lighting",
        "rendering",
        "qa-review",
        "asset-optimization",
        "export-pipeline",
        "hard-surface",
        "geometry-nodes",
        "compositing",
    ]
    copytree(
        TMP / "blender-skills/.claude/skills/references",
        bl / "references",
    )
    for name in blender_selected:
        src = TMP / "blender-skills/.claude/skills" / name
        copy_skill_dir(src, bl / name)
    shutil.copy2(TMP / "blender-skills/LICENSE", bl / "UPSTREAM_LICENSE")

    # --- img2threejs minimum operational subset ---
    i2t = SKILLS / "img2threejs"
    remove_gitkeep(i2t)
    if i2t.exists():
        shutil.rmtree(i2t)
    i2t.mkdir(parents=True)
    upstream = TMP / "img2threejs"
    for item in ["SKILL.md", "steps.json", "LICENSE"]:
        shutil.copy2(upstream / item, i2t / item)
    for folder in ["forge", "grimoire", "docs", "scripts"]:
        copytree(upstream / folder, i2t / folder)

    print("Phase B import complete.")


if __name__ == "__main__":
    main()
