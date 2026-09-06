"""Checked-in form plan: envelope in → named parts + clay cameras out.

Re-run this plan. Do not write _clay_iterN.py novels.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

CLAY_CAMERAS = ("front", "profile", "rear", "front34", "rear34", "proportion")


def load_spec(project_dir: Path) -> dict[str, Any]:
    path = project_dir / "direction" / "form_specification.yaml"
    if not path.is_file():
        return {}
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}


def _num(data: dict[str, Any], *keys: str, default: float = 0.0) -> float:
    for key in keys:
        if key in data and data[key] is not None:
            try:
                return float(data[key])
            except (TypeError, ValueError):
                return default
    return default


def _case_mm(spec: dict[str, Any]) -> tuple[float, float, float]:
    env = spec.get("envelope") or {}
    case = env.get("case_closed") if isinstance(env.get("case_closed"), dict) else env
    if not isinstance(case, dict):
        return (54.0, 26.0, 28.0)
    width = _num(case, "width_mm", "width", default=54.0)
    depth = _num(case, "depth_mm", "depth", default=26.0)
    height = _num(case, "height_mm", "height", default=28.0)
    return (width or 54.0, depth or 26.0, height or 28.0)


def _part_names(spec: dict[str, Any]) -> list[str]:
    parts = spec.get("part_architecture") or spec.get("parts") or []
    names: list[str] = []
    for part in parts:
        if isinstance(part, dict):
            names.append(str(part.get("name") or part.get("id") or "").strip())
        else:
            names.append(str(part).strip())
    return [name for name in names if name]


def is_tws(spec: dict[str, Any]) -> bool:
    names = " ".join(_part_names(spec)).lower()
    blob = f"{names} {spec.get('archetype') or ''}"
    return any(token in blob for token in ("case_", "earbud", "tws", "in-ear", "charging"))


def plan_parts(spec: dict[str, Any]) -> list[dict[str, Any]]:
    width, depth, height = _case_mm(spec)
    names = _part_names(spec)
    if is_tws(spec) or {"Case_Base", "Case_Lid"} <= set(names):
        seam = height * 0.38
        well_r = min(width, depth) * 0.16
        well_z = 2.0
        bud_w = _num((spec.get("envelope") or {}).get("earbud") or {}, "acoustic_width_mm", "width_mm", default=18.0)
        return [
            {
                "name": "Case_Base",
                "kind": "enclosure_base",
                "size_mm": [width, depth, seam],
                "location_mm": [0.0, 0.0, seam / 2],
                "bbox_mm": {"min": [-width / 2, -depth / 2, 0.0], "max": [width / 2, depth / 2, seam]},
            },
            {
                "name": "Case_Lid",
                "kind": "enclosure_lid",
                "size_mm": [width, depth, height - seam],
                "location_mm": [0.0, 0.0, seam + (height - seam) / 2],
                "bbox_mm": {
                    "min": [-width / 2, -depth / 2, seam],
                    "max": [width / 2, depth / 2, height],
                },
            },
            {
                "name": "Earbud_Left",
                "kind": "in_ear_three_volume",
                "size_mm": [bud_w * 0.7, bud_w, bud_w * 0.55],
                "location_mm": [-width * 0.22, 0.0, well_z + bud_w * 0.28],
                "bbox_mm": {
                    "min": [-width * 0.22 - well_r, -well_r, well_z],
                    "max": [-width * 0.22 + well_r, well_r, well_z + bud_w * 0.55],
                },
            },
            {
                "name": "Earbud_Right",
                "kind": "in_ear_three_volume",
                "size_mm": [bud_w * 0.7, bud_w, bud_w * 0.55],
                "location_mm": [width * 0.22, 0.0, well_z + bud_w * 0.28],
                "bbox_mm": {
                    "min": [width * 0.22 - well_r, -well_r, well_z],
                    "max": [width * 0.22 + well_r, well_r, well_z + bud_w * 0.55],
                },
            },
        ]
    planned: list[dict[str, Any]] = []
    count = max(len(names), 1)
    for index, name in enumerate(names or ["Hero_Body"]):
        z0 = height * (index / count)
        z1 = height * ((index + 1) / count)
        planned.append(
            {
                "name": name,
                "kind": "named_volume",
                "size_mm": [width * 0.7, depth * 0.55, max(z1 - z0, 8.0)],
                "location_mm": [0.0, 0.0, (z0 + z1) / 2],
                "bbox_mm": {
                    "min": [-width * 0.35, -depth * 0.28, z0],
                    "max": [width * 0.35, depth * 0.28, z1],
                },
            }
        )
    return planned


def plan_cameras(spec: dict[str, Any]) -> list[dict[str, Any]]:
    width, depth, height = _case_mm(spec)
    span = max(width, depth, height)
    dist = span * 2.35
    target = [0.0, 0.0, height * 0.42]
    return [
        {"name": "front", "location_mm": [0.0, -dist, height * 0.45], "target_mm": target},
        {"name": "profile", "location_mm": [dist, 0.0, height * 0.45], "target_mm": target},
        {"name": "rear", "location_mm": [0.0, dist, height * 0.45], "target_mm": target},
        {"name": "front34", "location_mm": [dist * 0.72, -dist * 0.72, height * 0.7], "target_mm": target},
        {"name": "rear34", "location_mm": [dist * 0.72, dist * 0.72, height * 0.7], "target_mm": target},
        {"name": "proportion", "location_mm": [0.0, -span * 1.35, height * 0.55], "target_mm": target},
    ]


def build_plan(project_dir: Path) -> dict[str, Any]:
    spec = load_spec(project_dir)
    return {
        "builder": "tools/form/build_form.py",
        "envelope_mm": list(_case_mm(spec)),
        "parts": plan_parts(spec),
        "cameras": plan_cameras(spec),
    }


def write_plan(project_dir: Path, plan: dict[str, Any] | None = None) -> Path:
    plan = plan or build_plan(project_dir)
    direction = project_dir / "direction"
    direction.mkdir(parents=True, exist_ok=True)
    path = direction / "form_plan.yaml"
    path.write_text(yaml.dump(plan, sort_keys=False), encoding="utf-8")
    scene = {
        "parts": [
            {"name": part["name"], "bbox_mm": part["bbox_mm"]}
            for part in plan.get("parts") or []
            if isinstance(part, dict)
        ]
    }
    (direction / "form_scene.yaml").write_text(yaml.dump(scene, sort_keys=False), encoding="utf-8")
    return path
